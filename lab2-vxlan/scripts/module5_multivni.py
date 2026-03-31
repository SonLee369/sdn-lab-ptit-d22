#!/usr/bin/env python3
"""
=============================================================
  VXLAN Lab - Module 5: Multi-VNI / Tenant Isolation
=============================================================
Topology:

  [Tenant A - VNI 100]              [Tenant B - VNI 200]
  h1 (10.0.0.1)  h2 (10.0.0.2)    h3 (10.0.0.1)  h4 (10.0.0.2)
       |               |                 |               |
     [s1a]           [s2a]            [s1b]           [s2b]
  VTEP:192.168.1.1   VTEP:192.168.1.2  VTEP:192.168.1.1  VTEP:192.168.1.2
       |=====VXLAN VNI 100 tunnel========|
                    |=====VXLAN VNI 200 tunnel========|

Muc tieu:
  1. h1 <-> h2 thong (VNI 100)
  2. h3 <-> h4 thong (VNI 200)
  3. h1 KHONG thong voi h3/h4 (khac VNI)
  4. ARP cache cua h1 va h3 cho cung IP (10.0.0.2)
     se co 2 MAC khac nhau -> chung minh isolation
=============================================================
"""

import os
import time
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.clean import cleanup


def build_topology():
    # ----------------------------------------
    # 1. Don dep topo cu
    # ----------------------------------------
    info('*** [M5] Don dep topo cu\n')
    cleanup()

    # ----------------------------------------
    # 2. Khoi tao Mininet
    # ----------------------------------------
    net = Mininet(controller=None)

    # ----------------------------------------
    # 3. Them hosts
    #    VNI 100 — Tenant A: h1, h2
    #    VNI 200 — Tenant B: h3, h4
    #    Luu y: h1 va h3 cung IP 10.0.0.1
    #            h2 va h4 cung IP 10.0.0.2
    #    Day la diem chinh de chung minh isolation!
    # ----------------------------------------
    info('*** [M5] Them hosts (VNI 100: h1,h2 | VNI 200: h3,h4)\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:01:01')
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:01:02')
    h3 = net.addHost('h3', ip='10.0.0.1/24', mac='00:00:00:00:02:01')
    h4 = net.addHost('h4', ip='10.0.0.2/24', mac='00:00:00:00:02:02')

    # ----------------------------------------
    # 4. Them OVS bridges (4 bridge, 2 moi ben)
    #    s1a/s2a -> VNI 100 (Tenant A)
    #    s1b/s2b -> VNI 200 (Tenant B)
    # ----------------------------------------
    info('*** [M5] Them OVS bridges\n')
    s1a = net.addSwitch('s1a', cls=OVSBridge, failMode='standalone')
    s2a = net.addSwitch('s2a', cls=OVSBridge, failMode='standalone')
    s1b = net.addSwitch('s1b', cls=OVSBridge, failMode='standalone')
    s2b = net.addSwitch('s2b', cls=OVSBridge, failMode='standalone')

    # ----------------------------------------
    # 5. Them links (chi host <-> bridge)
    #    Khong can link vat ly giua s1x va s2x
    #    vi VXLAN dung local-delivery (cung namespace)
    # ----------------------------------------
    info('*** [M5] Them links\n')
    net.addLink(h1, s1a)   # h1-eth0 <-> s1a-eth1
    net.addLink(h2, s2a)   # h2-eth0 <-> s2a-eth1
    net.addLink(h3, s1b)   # h3-eth0 <-> s1b-eth1
    net.addLink(h4, s2b)   # h4-eth0 <-> s2b-eth1

    # ----------------------------------------
    # 6. Khoi dong mang
    # ----------------------------------------
    info('*** [M5] Khoi dong mang\n')
    net.start()

    # ----------------------------------------
    # 7. Gan VTEP IP len bridge interface
    #    192.168.1.1 dung chung cho s1a va s1b (ben trai)
    #    192.168.1.2 dung chung cho s2a va s2b (ben phai)
    #    OVS phan biet tunnel bang (local_ip, remote_ip, VNI key)
    # ----------------------------------------
    info('*** [M5] Cau hinh VTEP IP\n')
    s1a.cmd('ip addr add 192.168.1.1/30 dev s1a')
    s2a.cmd('ip addr add 192.168.1.2/30 dev s2a')
    s1a.cmd('ip link set s1a up')
    s2a.cmd('ip link set s2a up')

    # ----------------------------------------
    # 8. Cau hinh VXLAN tunnels
    #    VNI 100: s1a <-> s2a  (Tenant A)
    #    VNI 200: s1b <-> s2b  (Tenant B)
    #    Ten port phai unique trong toan bo OVS instance:
    #      v100s1, v100s2, v200s1, v200s2
    # ----------------------------------------
    info('*** [M5] Cau hinh VXLAN tunnel VNI 100 (Tenant A)\n')
    s1a.cmd(
        'ovs-vsctl add-port s1a v100s1 '
        '-- set interface v100s1 '
        'type=vxlan '
        'options:local_ip=192.168.1.1 '
        'options:remote_ip=192.168.1.2 '
        'options:key=100 '
        'options:dst_port=4789'
    )
    s2a.cmd(
        'ovs-vsctl add-port s2a v100s2 '
        '-- set interface v100s2 '
        'type=vxlan '
        'options:local_ip=192.168.1.2 '
        'options:remote_ip=192.168.1.1 '
        'options:key=100 '
        'options:dst_port=4789'
    )

    info('*** [M5] Cau hinh VXLAN tunnel VNI 200 (Tenant B)\n')
    s1b.cmd(
        'ovs-vsctl add-port s1b v200s1 '
        '-- set interface v200s1 '
        'type=vxlan '
        'options:local_ip=192.168.1.1 '
        'options:remote_ip=192.168.1.2 '
        'options:key=200 '
        'options:dst_port=4789'
    )
    s2b.cmd(
        'ovs-vsctl add-port s2b v200s2 '
        '-- set interface v200s2 '
        'type=vxlan '
        'options:local_ip=192.168.1.2 '
        'options:remote_ip=192.168.1.1 '
        'options:key=200 '
        'options:dst_port=4789'
    )

    time.sleep(1)

    # ----------------------------------------
    # 9. KIEM TRA INTRA-VNI (cung tenant)
    # ----------------------------------------
    info('\n' + '=' * 60 + '\n')
    info('*** [M5] TEST 1: Intra-VNI — h1 -> h2 (VNI 100)\n')
    r1 = h1.cmd('ping -c 3 -W 2 10.0.0.2')
    info(r1)
    if '0% packet loss' in r1:
        info('>>> PASS: VNI 100 thong (h1 <-> h2)\n')
    else:
        info('>>> FAIL: VNI 100 khong thong!\n')

    info('*** [M5] TEST 2: Intra-VNI — h3 -> h4 (VNI 200)\n')
    r2 = h3.cmd('ping -c 3 -W 2 10.0.0.2')
    info(r2)
    if '0% packet loss' in r2:
        info('>>> PASS: VNI 200 thong (h3 <-> h4)\n')
    else:
        info('>>> FAIL: VNI 200 khong thong!\n')

    # ----------------------------------------
    # 10. KIEM TRA ISOLATION (khac tenant)
    #     Dung arping de thu ARP cross-VNI:
    #     h1 tim MAC cua 10.0.0.2 -> chi thay h2 (VNI 100)
    #     h3 tim MAC cua 10.0.0.2 -> chi thay h4 (VNI 200)
    # ----------------------------------------
    info('\n' + '=' * 60 + '\n')
    info('*** [M5] TEST 3: Isolation — Kiem tra ARP cache\n')
    info('h1 ARP cache (phai thay MAC cua h2: 00:00:00:00:01:02):\n')
    info(h1.cmd('arp -n'))

    info('h3 ARP cache (phai thay MAC cua h4: 00:00:00:00:02:02):\n')
    info(h3.cmd('arp -n'))

    # ----------------------------------------
    # 11. HIEN THI FDB TABLE
    # ----------------------------------------
    info('\n' + '=' * 60 + '\n')
    info('*** [M5] FDB Tables\n')
    info('--- s1a (VNI 100, ben trai) ---\n')
    info(s1a.cmd('ovs-appctl fdb/show s1a'))
    info('--- s2a (VNI 100, ben phai) ---\n')
    info(s2a.cmd('ovs-appctl fdb/show s2a'))
    info('--- s1b (VNI 200, ben trai) ---\n')
    info(s1b.cmd('ovs-appctl fdb/show s1b'))
    info('--- s2b (VNI 200, ben phai) ---\n')
    info(s2b.cmd('ovs-appctl fdb/show s2b'))

    # ----------------------------------------
    # 12. HIEN THI OVS CAU HINH
    # ----------------------------------------
    info('\n*** [M5] OVS config tong quat:\n')
    info(s1a.cmd('ovs-vsctl show'))

    # ----------------------------------------
    # 13. Mo CLI
    # ----------------------------------------
    info('\n*** Mo Mininet CLI. Go "exit" de thoat.\n')
    info('Goi y lenh kiem tra isolation:\n')
    info('  mininet> h1 ping -c 3 10.0.0.2    <- VNI 100, OK\n')
    info('  mininet> h3 ping -c 3 10.0.0.2    <- VNI 200, OK\n')
    info('  mininet> h1 arp -n                <- MAC = h2 (01:02)\n')
    info('  mininet> h3 arp -n                <- MAC = h4 (02:02)\n')
    info('  mininet> sh ovs-appctl fdb/show s1a\n')
    info('  mininet> sh ovs-appctl fdb/show s1b\n')
    CLI(net)

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    build_topology()
