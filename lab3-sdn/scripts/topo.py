#!/usr/bin/env python3
"""
Module 1: Star Topology cho mạng SDN
=====================================
Topology: 1 OVS Switch (s1) + 4 Hosts (h1-h4)
Controller: Ryu (RemoteController, TCP 6633)
Link: Bandwidth 10 Mbps, Delay 5ms

Cách chạy:
    Terminal 1 (Ryu): ryu-manager controller.py
    Terminal 2 (Mininet): sudo python3 topo.py
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI


# ──────────────────────────────────────────────
# Định nghĩa Topology
# ──────────────────────────────────────────────
class StarTopo(Topo):
    """
    Star Topology:
        h1 ─┐
        h2 ─┤─── s1 ──── RemoteController (Ryu)
        h3 ─┤
        h4 ─┘
    """

    def build(self, n_hosts=4, bw=10, delay='5ms'):
        """
        Tạo topology Star với n_hosts hosts kết nối vào 1 switch.

        Args:
            n_hosts (int): Số lượng host (mặc định 4)
            bw      (int): Băng thông mỗi link (Mbps, mặc định 10)
            delay   (str): Độ trễ mỗi link (mặc định '5ms')
        """
        # Thông số link
        link_opts = dict(bw=bw, delay=delay, loss=0, use_htb=True)

        # Tạo switch trung tâm
        switch = self.addSwitch('s1', protocols='OpenFlow13')

        # Tạo hosts và kết nối vào switch
        for i in range(1, n_hosts + 1):
            host = self.addHost(
                f'h{i}',
                ip=f'10.0.0.{i}/24',
                mac=f'00:00:00:00:00:0{i}'
            )
            self.addLink(host, switch, **link_opts)


# ──────────────────────────────────────────────
# Hàm chạy mạng
# ──────────────────────────────────────────────
def run():
    setLogLevel('info')

    info('*** Khởi tạo topology Star (1 switch, 4 hosts)\n')
    topo = StarTopo(n_hosts=4, bw=10, delay='5ms')

    info('*** Kết nối Ryu RemoteController tại 127.0.0.1:6633\n')
    net = Mininet(
        topo=topo,
        switch=OVSSwitch,
        controller=None,       # Không dùng controller mặc định
        link=TCLink,
        autoSetMacs=False,     # Đã gán MAC thủ công trong topo
        autoStaticArp=False    # Để SDN tự xử lý ARP
    )

    # Thêm Ryu RemoteController
    ryu = net.addController(
        'ryu',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6633
    )

    info('*** Khởi động mạng\n')
    net.start()

    # Cấu hình OVS switch dùng OpenFlow 1.3
    info('*** Cấu hình OVS switch: OpenFlow 1.3\n')
    for sw in net.switches:
        sw.cmd(f'ovs-vsctl set bridge {sw.name} protocols=OpenFlow13')

    # In thông tin topology
    info('\n=== THÔNG TIN TOPOLOGY ===\n')
    info(f'Switch : s1\n')
    for host in net.hosts:
        info(f'Host   : {host.name}  IP={host.IP()}  MAC={host.MAC()}\n')
    info('==========================\n\n')

    info('*** Mở Mininet CLI (gõ "exit" để thoát)\n')
    CLI(net)

    info('*** Dừng mạng\n')
    net.stop()


# ──────────────────────────────────────────────
# Entrypoint
# ──────────────────────────────────────────────
if __name__ == '__main__':
    run()
