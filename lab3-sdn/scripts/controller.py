#!/usr/bin/env python3
"""
Module 2: Ryu L2 Learning Switch Controller
=============================================
Giao thức : OpenFlow 1.3
Chức năng  : Học địa chỉ MAC động, cài flow rule xuống switch
Cổng lắng nghe: TCP 6633

Cách chạy:
    ryu-manager controller.py
    ryu-manager controller.py --observe-links   (nếu cần topology)
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
import logging


class L2LearningSwitch(app_manager.RyuApp):
    """
    Ryu Application: L2 Learning Switch (OpenFlow 1.3)

    Luồng xử lý:
        1. Switch kết nối → cài table-miss flow rule
        2. Gói tin đến switch, không khớp rule → PacketIn lên controller
        3. Controller học MAC nguồn → cập nhật mac_to_port
        4. Tra cứu MAC đích:
           - Biết cổng đích → cài flow rule + gửi gói
           - Chưa biết      → flood ra tất cả cổng
    """

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L2LearningSwitch, self).__init__(*args, **kwargs)
        # Bảng học MAC: {datapath_id: {mac_address: port}}
        self.mac_to_port = {}
        self.logger.setLevel(logging.INFO)

    # ──────────────────────────────────────────────────────
    # Sự kiện: Switch kết nối với Controller
    # ──────────────────────────────────────────────────────
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
        Khi switch kết nối lần đầu:
        Cài flow rule table-miss (priority=0):
            match: tất cả gói tin
            action: gửi lên controller (CONTROLLER port)
        """
        datapath = ev.msg.datapath
        ofproto  = datapath.ofproto
        parser   = datapath.ofproto_parser
        dpid     = datapath.id

        self.logger.info(f'[CONNECT] Switch dpid={dpid:#018x} đã kết nối')

        # Cài table-miss rule: gói không khớp bất kỳ rule nào → lên controller
        match  = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self._add_flow(datapath, priority=0, match=match, actions=actions)
        self.logger.info(f'[FLOW]    Switch dpid={dpid:#018x} — Đã cài table-miss rule')

    # ──────────────────────────────────────────────────────
    # Sự kiện: Nhận gói tin từ Switch (PacketIn)
    # ──────────────────────────────────────────────────────
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
        Xử lý PacketIn:
        1. Parse gói tin, lấy MAC src/dst
        2. Học MAC nguồn → cổng vào
        3. Tra cứu MAC đích → cổng ra
        4. Cài flow rule nếu biết cổng đích
        5. Gửi gói tin ra cổng phù hợp (hoặc flood)
        """
        msg      = ev.msg
        datapath = msg.datapath
        ofproto  = datapath.ofproto
        parser   = datapath.ofproto_parser
        dpid     = datapath.id
        in_port  = msg.match['in_port']

        # Parse gói tin
        pkt     = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        # Bỏ qua gói LLDP (link discovery)
        if eth_pkt.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        src_mac = eth_pkt.src
        dst_mac = eth_pkt.dst

        # Bỏ qua IPv6 multicast (33:33:xx:xx:xx:xx) — tránh flood storm
        if dst_mac.startswith('33:33'):
            return

        # ── Bước 1: Khởi tạo bảng MAC cho switch nếu chưa có ──
        self.mac_to_port.setdefault(dpid, {})

        # ── Bước 2: Học MAC nguồn → cổng vào ──
        if src_mac not in self.mac_to_port[dpid]:
            self.mac_to_port[dpid][src_mac] = in_port
            self.logger.info(
                f'[LEARN]   dpid={dpid:#018x} | '
                f'MAC {src_mac} → port {in_port}'
            )

        # ── Bước 3: Tra cứu cổng ra cho MAC đích ──
        if dst_mac in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst_mac]
            self.logger.info(
                f'[MATCH]   dpid={dpid:#018x} | '
                f'{src_mac} → {dst_mac} via port {out_port}'
            )
        else:
            # Chưa biết MAC đích → flood
            out_port = ofproto.OFPP_FLOOD
            self.logger.info(
                f'[FLOOD]   dpid={dpid:#018x} | '
                f'{src_mac} → {dst_mac} (unknown dst, flooding)'
            )

        actions = [parser.OFPActionOutput(out_port)]

        # ── Bước 4: Cài flow rule nếu biết cổng đích ──
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port,
                                    eth_src=src_mac,
                                    eth_dst=dst_mac)
            # Chỉ cài rule nếu gói còn trong buffer hoặc có data
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self._add_flow(datapath, priority=1, match=match,
                               actions=actions, buffer_id=msg.buffer_id)
                return  # Gói đã được switch gửi qua buffer, không cần gửi lại
            else:
                self._add_flow(datapath, priority=1, match=match,
                               actions=actions)

        # ── Bước 5: Gửi gói tin ra cổng (Packet Out) ──
        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
        out  = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data
        )
        datapath.send_msg(out)

    # ──────────────────────────────────────────────────────
    # Hàm tiện ích: Cài flow rule xuống switch
    # ──────────────────────────────────────────────────────
    def _add_flow(self, datapath, priority, match, actions,
                  buffer_id=None, idle_timeout=0, hard_timeout=0):
        """
        Gửi OFPFlowMod để cài flow rule vào switch.

        Args:
            datapath     : Switch cần cài rule
            priority     : Độ ưu tiên (0 = thấp nhất, cao hơn = ưu tiên hơn)
            match        : Điều kiện khớp gói tin
            actions      : Hành động thực hiện khi khớp
            buffer_id    : Buffer ID của gói (nếu có)
            idle_timeout : Xóa rule sau N giây không dùng (0 = không xóa)
            hard_timeout : Xóa rule sau N giây tuyệt đối (0 = không xóa)
        """
        ofproto = datapath.ofproto
        parser  = datapath.ofproto_parser

        # Đóng gói actions vào Instructions
        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions
        )]

        # Tạo FlowMod message
        if buffer_id and buffer_id != ofproto.OFP_NO_BUFFER:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                buffer_id=buffer_id,
                priority=priority,
                match=match,
                instructions=inst,
                idle_timeout=idle_timeout,
                hard_timeout=hard_timeout
            )
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=priority,
                match=match,
                instructions=inst,
                idle_timeout=idle_timeout,
                hard_timeout=hard_timeout
            )

        datapath.send_msg(mod)
        self.logger.info(
            f'[FLOW]    priority={priority} | '
            f'match={match} | idle_timeout={idle_timeout}s'
        )
