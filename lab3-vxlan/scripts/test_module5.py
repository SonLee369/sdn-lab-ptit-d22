#!/usr/bin/env python3
"""
test_module5.py — Kiểm tra tự động Module 5: Traffic Testing
Xây dựng topology VXLAN rồi chạy toàn bộ bài kiểm tra, in kết quả PASS/FAIL.

Cách chạy:
    sudo python3 test_module5.py
    sudo python3 test_module5.py --no-cli   # chạy test xong thoát luôn (không mở CLI)
"""

import sys
import re
import argparse
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info

# ─────────────────────────────────────────────
#  Thông số mạng
# ─────────────────────────────────────────────
UNDERLAY_S1   = '10.0.0.1'
UNDERLAY_S2   = '10.0.0.2'
UNDERLAY_MASK = '24'
OVERLAY_H1    = '192.168.100.1'
OVERLAY_H2    = '192.168.100.2'
OVERLAY_MASK  = '24'
VNI           = '100'
VXLAN_PORT    = '4789'

# ─────────────────────────────────────────────
#  Màu terminal
# ─────────────────────────────────────────────
GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
BOLD   = '\033[1m'
RESET  = '\033[0m'

def ok(msg):   print(f'  {GREEN}[PASS]{RESET} {msg}')
def fail(msg): print(f'  {RED}[FAIL]{RESET} {msg}')
def warn(msg): print(f'  {YELLOW}[WARN]{RESET} {msg}')
def hdr(msg):  print(f'\n{CYAN}{BOLD}{"─"*55}\n  {msg}\n{"─"*55}{RESET}')
def detail(text):
    for line in text.strip().splitlines():
        print(f'         {line}')

# ─────────────────────────────────────────────
#  Kết quả tổng hợp
# ─────────────────────────────────────────────
results = []   # list of (test_name, passed: bool, note)

def record(name, passed, note=''):
    results.append((name, passed, note))
    if passed:
        ok(f'{name}  {YELLOW}{note}{RESET}' if note else name)
    else:
        fail(f'{name}  {YELLOW}{note}{RESET}' if note else name)

# ─────────────────────────────────────────────
#  Helper: build topology (giống topology.py)
# ─────────────────────────────────────────────
def add_vxlan_port(switch, port_name, local_ip, remote_ip, vni):
    switch.cmd(
        f'ovs-vsctl add-port {switch.name} {port_name}'
        f' -- set interface {port_name} type=vxlan'
        f' options:local_ip={local_ip}'
        f' options:remote_ip={remote_ip}'
        f' options:key={vni}'
        f' options:dst_port={VXLAN_PORT}'
    )

def build_network():
    net = Mininet(controller=None)
    h1 = net.addHost('h1', ip=f'{OVERLAY_H1}/{OVERLAY_MASK}')
    h2 = net.addHost('h2', ip=f'{OVERLAY_H2}/{OVERLAY_MASK}')
    s1 = net.addSwitch('s1', cls=OVSBridge, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSBridge, failMode='standalone')
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(s1, s2)
    net.start()

    # Fix L2 loop: rút underlay veth ra khỏi OVS bridge
    s1.cmd('ovs-vsctl del-port s1 s1-eth2')
    s2.cmd('ovs-vsctl del-port s2 s2-eth2')

    # Gán VTEP IP cho raw veth
    s1.cmd(f'ip addr add {UNDERLAY_S1}/{UNDERLAY_MASK} dev s1-eth2')
    s2.cmd(f'ip addr add {UNDERLAY_S2}/{UNDERLAY_MASK} dev s2-eth2')
    s1.cmd('ip link set s1-eth2 up')
    s2.cmd('ip link set s2-eth2 up')

    # Thêm VXLAN tunnel ports
    add_vxlan_port(s1, 'vxlan0', UNDERLAY_S1, UNDERLAY_S2, VNI)
    add_vxlan_port(s2, 'vxlan1', UNDERLAY_S2, UNDERLAY_S1, VNI)

    # Xóa default route trên host
    h1.cmd('ip route del default 2>/dev/null; true')
    h2.cmd('ip route del default 2>/dev/null; true')

    return net

# ═══════════════════════════════════════════════════════════
#  CÁC BÀI KIỂM TRA
# ═══════════════════════════════════════════════════════════

# ── T1: Kiểm tra IP underlay trên veth ─────────────────────
def test_underlay_ip(net):
    hdr('T1: Kiểm tra VTEP IP trên underlay veth')
    s1 = net.get('s1')
    s2 = net.get('s2')

    out1 = s1.cmd('ip addr show s1-eth2')
    has_ip1 = UNDERLAY_S1 in out1
    record('s1-eth2 có IP 10.0.0.1/24', has_ip1)
    if not has_ip1:
        detail(out1)

    out2 = s2.cmd('ip addr show s2-eth2')
    has_ip2 = UNDERLAY_S2 in out2
    record('s2-eth2 có IP 10.0.0.2/24', has_ip2)
    if not has_ip2:
        detail(out2)

    # Kiểm tra s1-eth2 KHÔNG nằm trong OVS bridge s1
    ports_s1 = s1.cmd('ovs-vsctl list-ports s1')
    no_loop = 's1-eth2' not in ports_s1
    record('s1-eth2 không còn trong OVS bridge s1 (không loop)', no_loop,
           '← critical' if not no_loop else '')
    if not no_loop:
        warn('s1-eth2 vẫn trong bridge → nguy cơ broadcast storm!')

    ports_s2 = s2.cmd('ovs-vsctl list-ports s2')
    no_loop2 = 's2-eth2' not in ports_s2
    record('s2-eth2 không còn trong OVS bridge s2 (không loop)', no_loop2,
           '← critical' if not no_loop2 else '')

# ── T2: Kiểm tra kết nối underlay ─────────────────────────
def test_underlay_ping(net):
    hdr('T2: Kiểm tra kết nối underlay (VTEP-to-VTEP)')
    s1 = net.get('s1')

    out = s1.cmd(f'ping -c 4 -W 2 {UNDERLAY_S2}')
    received = re.search(r'(\d+) received', out)
    cnt = int(received.group(1)) if received else 0
    passed = cnt >= 3
    record(f'Underlay ping 10.0.0.1 → 10.0.0.2 ({cnt}/4 received)', passed)
    detail(out.strip().splitlines()[-2] if out.strip() else 'Không có output')

# ── T3: Kiểm tra cấu hình VXLAN trên OVS ─────────────────
def test_vxlan_config(net):
    hdr('T3: Kiểm tra cấu hình VXLAN tunnel trên OVS')
    s1 = net.get('s1')
    s2 = net.get('s2')

    # vxlan0 trên s1
    # 'ovs-vsctl list interface' dùng định dạng "field                : value"
    # với số lượng khoảng trắng bất kỳ trước dấu ':' → dùng regex thay vì str check
    out = s1.cmd('ovs-vsctl list interface vxlan0 2>/dev/null')
    has_vxlan0      = bool(re.search(r'type\s*:\s*vxlan', out))
    has_local_ip_s1 = UNDERLAY_S1 in out
    has_remote_s1   = UNDERLAY_S2 in out
    has_vni_s1      = bool(re.search(r'key.*' + VNI, out))
    has_port_s1     = VXLAN_PORT in out

    record('vxlan0 tồn tại trên s1 (type=vxlan)', has_vxlan0)
    record(f'vxlan0: local_ip={UNDERLAY_S1}', has_local_ip_s1)
    record(f'vxlan0: remote_ip={UNDERLAY_S2}', has_remote_s1)
    record(f'vxlan0: VNI key={VNI}', has_vni_s1)
    record(f'vxlan0: dst_port={VXLAN_PORT}', has_port_s1)

    # vxlan1 trên s2
    out2 = s2.cmd('ovs-vsctl list interface vxlan1 2>/dev/null')
    has_vxlan1      = bool(re.search(r'type\s*:\s*vxlan', out2))
    has_local_ip_s2 = UNDERLAY_S2 in out2
    has_remote_s2   = UNDERLAY_S1 in out2

    record('vxlan1 tồn tại trên s2 (type=vxlan)', has_vxlan1)
    record(f'vxlan1: local_ip={UNDERLAY_S2}', has_local_ip_s2)
    record(f'vxlan1: remote_ip={UNDERLAY_S1}', has_remote_s2)

    # link_state
    link0 = s1.cmd('ovs-vsctl get interface vxlan0 link_state 2>/dev/null').strip().strip('"')
    link1 = s2.cmd('ovs-vsctl get interface vxlan1 link_state 2>/dev/null').strip().strip('"')
    record(f'vxlan0 link_state=up', link0 == 'up', f'(got: {link0})')
    record(f'vxlan1 link_state=up', link1 == 'up', f'(got: {link1})')

# ── T4: Kiểm tra IP overlay của host ──────────────────────
def test_host_ip(net):
    hdr('T4: Kiểm tra địa chỉ IP overlay của h1 và h2')
    h1 = net.get('h1')
    h2 = net.get('h2')

    out1 = h1.cmd('ip addr show h1-eth0')
    record(f'h1 có IP {OVERLAY_H1}/24', OVERLAY_H1 in out1)

    out2 = h2.cmd('ip addr show h2-eth0')
    record(f'h2 có IP {OVERLAY_H2}/24', OVERLAY_H2 in out2)

# ── T5: Overlay ping h1 → h2 ──────────────────────────────
def test_overlay_ping_h1_h2(net):
    hdr('T5: Overlay ping h1 → h2 (qua VXLAN tunnel)')
    h1 = net.get('h1')

    out = h1.cmd(f'ping -c 5 -W 2 {OVERLAY_H2}')
    received = re.search(r'(\d+) received', out)
    cnt = int(received.group(1)) if received else 0
    passed = cnt >= 4   # cho phép mất 1 gói ARP đầu tiên
    record(f'h1 → h2 overlay ping ({cnt}/5 received)', passed,
           '' if passed else '← VXLAN tunnel không hoạt động')
    detail(out.strip().splitlines()[-2] if out.strip() else 'Không có output')

# ── T6: Overlay ping h2 → h1 ──────────────────────────────
def test_overlay_ping_h2_h1(net):
    hdr('T6: Overlay ping h2 → h1 (chiều ngược lại)')
    h2 = net.get('h2')

    out = h2.cmd(f'ping -c 3 -W 2 {OVERLAY_H1}')
    received = re.search(r'(\d+) received', out)
    cnt = int(received.group(1)) if received else 0
    passed = cnt >= 2
    record(f'h2 → h1 overlay ping ({cnt}/3 received)', passed)
    detail(out.strip().splitlines()[-2] if out.strip() else 'Không có output')

# ── T7: ARP table trên h1 ─────────────────────────────────
def test_arp_table(net):
    hdr('T7: Kiểm tra ARP table (h1 đã học MAC của h2)')
    h1 = net.get('h1')
    h2 = net.get('h2')

    # Lấy MAC của h2
    mac_out = h2.cmd('cat /sys/class/net/h2-eth0/address').strip()
    arp_out  = h1.cmd('arp -n')
    has_arp  = OVERLAY_H2 in arp_out and mac_out.lower() in arp_out.lower()

    record(f'h1 ARP table có entry cho {OVERLAY_H2}', OVERLAY_H2 in arp_out)
    record(f'ARP entry đúng MAC của h2 ({mac_out})', has_arp)
    detail(arp_out.strip())

# ── T8: MAC learning trên OVS FDB ─────────────────────────
def test_fdb(net):
    hdr('T8: Kiểm tra MAC learning — FDB của s1')
    s1 = net.get('s1')
    h1 = net.get('h1')
    h2 = net.get('h2')

    mac_h1 = h1.cmd('cat /sys/class/net/h1-eth0/address').strip()
    mac_h2 = h2.cmd('cat /sys/class/net/h2-eth0/address').strip()
    fdb    = s1.cmd('ovs-appctl fdb/show s1')

    # h1 MAC phải học trên port LOCAL (không phải vxlan0 — nếu trên vxlan0 là dấu hiệu loop)
    vxlan0_port = s1.cmd('ovs-vsctl get interface vxlan0 ofport 2>/dev/null').strip()

    h1_in_fdb = mac_h1.lower() in fdb.lower()
    h2_in_fdb = mac_h2.lower() in fdb.lower()

    record(f'FDB s1 chứa MAC của h1 ({mac_h1})', h1_in_fdb)
    record(f'FDB s1 chứa MAC của h2 ({mac_h2})', h2_in_fdb)

    # Phát hiện loop: nếu MAC của h1 nằm trên ofport của vxlan0 → có loop
    if h1_in_fdb and vxlan0_port:
        for line in fdb.splitlines():
            if mac_h1.lower() in line.lower():
                port_in_fdb = line.strip().split()[0]
                loop_detected = (port_in_fdb == vxlan0_port.strip())
                record('MAC h1 học đúng port (không phải vxlan0)',
                       not loop_detected,
                       f'port={port_in_fdb}, vxlan0_port={vxlan0_port.strip()}')
                break

    detail(fdb.strip())

# ── T9: Flow table ─────────────────────────────────────────
def test_flow_table(net):
    hdr('T9: Kiểm tra flow table trên s1')
    s1 = net.get('s1')

    flows = s1.cmd('ovs-ofctl dump-flows s1')
    has_flows  = bool(flows.strip())
    has_normal = 'actions=NORMAL' in flows

    record('Flow table s1 có entry', has_flows)
    record('Flow table dùng actions=NORMAL (standalone mode)', has_normal)
    detail(flows.strip())

# ── T10: Broadcast storm detection ────────────────────────
def test_no_storm(net):
    hdr('T10: Kiểm tra không có broadcast storm')
    h1 = net.get('h1')
    h2 = net.get('h2')

    # Lấy RX trước
    def get_rx(host, iface):
        out = host.cmd(f'cat /sys/class/net/{iface}/statistics/rx_packets')
        return int(out.strip()) if out.strip().isdigit() else 0

    rx_h1_before = get_rx(h1, 'h1-eth0')
    rx_h2_before = get_rx(h2, 'h2-eth0')

    # Gửi 3 gói ping
    h1.cmd(f'ping -c 3 -W 1 {OVERLAY_H2}')

    import time
    time.sleep(0.5)

    rx_h1_after = get_rx(h1, 'h1-eth0')
    rx_h2_after = get_rx(h2, 'h2-eth0')

    delta_h1 = rx_h1_after - rx_h1_before
    delta_h2 = rx_h2_after - rx_h2_before

    # Nếu có loop: h1 sẽ nhận hàng nghìn gói trong 3 giây
    no_storm_h1 = delta_h1 < 1000
    no_storm_h2 = delta_h2 < 1000

    record(f'Không có storm trên h1 (RX delta={delta_h1} gói trong 3s ping)',
           no_storm_h1, '← LOOP!' if not no_storm_h1 else '')
    record(f'Không có storm trên h2 (RX delta={delta_h2} gói trong 3s ping)',
           no_storm_h2, '← LOOP!' if not no_storm_h2 else '')

# ═══════════════════════════════════════════════════════════
#  Bảng kết quả tổng hợp
# ═══════════════════════════════════════════════════════════
def print_summary():
    total  = len(results)
    passed = sum(1 for _, p, _ in results if p)
    failed = total - passed

    print(f'\n{BOLD}{"═"*55}')
    print(f'  KẾT QUẢ KIỂM TRA MODULE 5')
    print(f'{"═"*55}{RESET}')
    print(f'  {"Bài kiểm tra":<40} {"Kết quả"}')
    print(f'  {"─"*40} {"─"*10}')
    for name, p, note in results:
        status = f'{GREEN}PASS{RESET}' if p else f'{RED}FAIL{RESET}'
        label  = f'{name[:38]:<38}'
        print(f'  {label}  {status}  {YELLOW}{note}{RESET}' if note else
              f'  {label}  {status}')
    print(f'\n  {BOLD}Tổng: {passed}/{total} PASS  |  {failed} FAIL{RESET}')
    if failed == 0:
        print(f'  {GREEN}{BOLD}✓ Tất cả bài kiểm tra PASS — VXLAN hoạt động bình thường{RESET}')
    else:
        print(f'  {RED}{BOLD}✗ Có {failed} bài kiểm tra FAIL — xem chi tiết ở trên{RESET}')
    print(f'{BOLD}{"═"*55}{RESET}\n')

# ═══════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description='Test Module 5 — VXLAN Traffic Testing')
    parser.add_argument('--no-cli', action='store_true',
                        help='Không mở Mininet CLI sau khi test, thoát luôn')
    args = parser.parse_args()

    setLogLevel('warning')   # tắt bớt log Mininet khi test

    print(f'\n{BOLD}{"═"*55}')
    print(f'  Lab 3 — Test Module 5: VXLAN Traffic Testing')
    print(f'{"═"*55}{RESET}')
    print('  Đang khởi động topology...\n')

    net = build_network()

    try:
        # Chạy tất cả bài kiểm tra
        test_underlay_ip(net)
        test_underlay_ping(net)
        test_vxlan_config(net)
        test_host_ip(net)
        test_overlay_ping_h1_h2(net)
        test_overlay_ping_h2_h1(net)
        test_arp_table(net)
        test_fdb(net)
        test_flow_table(net)
        test_no_storm(net)

        # Tổng kết
        print_summary()

        # Mở CLI nếu cần
        if not args.no_cli:
            print('  Mở Mininet CLI để kiểm tra thêm (gõ exit để thoát)...\n')
            setLogLevel('info')
            CLI(net)

    finally:
        net.stop()

if __name__ == '__main__':
    main()
