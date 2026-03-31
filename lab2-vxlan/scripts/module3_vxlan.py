#!/usr/bin/env python3
"""
=============================================================
  VXLAN Lab - Module 3: VXLAN Tunnel Setup
=============================================================
Topology:

  h1 (10.0.0.1/24)              h2 (10.0.0.2/24)
        |                              |
      [s1]  <=== VXLAN VNI 100 ===>  [s2]
  VTEP: 192.168.1.1/30 -------- VTEP: 192.168.1.2/30
        |____________________________|
              Underlay Link
           (s1-eth2 <-> s2-eth2)

Muc tieu:
  - Tao VXLAN tunnel (VNI=100) giua s1 va s2
  - Kiem tra tunnel da duoc cau hinh dung
  - Chuan bi cho Module 4: kiem tra L2 overlay
=============================================================
"""

import os
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.clean import cleanup


def build_topology():
    # ----------------------------------------
    # 1. Don dep topo cu
    # ----------------------------------------
    info('*** [M3] Don dep topo cu\n')
    cleanup()
    os.system('ip link delete s1-eth2 2>/dev/null')
    os.system('ip link delete s2-eth2 2>/dev/null')

    # ----------------------------------------
    # 2. Khoi tao Mininet
    # ----------------------------------------
    net = Mininet(controller=None)

    # ----------------------------------------
    # 3. Them hosts
    # ----------------------------------------
    info('*** [M3] Them hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')

    # ----------------------------------------
    # 4. Them OVS switches
    # ----------------------------------------
    info('*** [M3] Them OVS switches\n')
    s1 = net.addSwitch('s1', cls=OVSBridge, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSBridge, failMode='standalone')

    # ----------------------------------------
    # 5. Them links (underlay)
    #    h1-eth0 <-> s1-eth1
    #    h2-eth0 <-> s2-eth1
    #    s1-eth2 <-> s2-eth2  (underlay link)
    # ----------------------------------------
    info('*** [M3] Them links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(s1, s2)

    # ----------------------------------------
    # 6. Khoi dong mang
    # ----------------------------------------
    info('*** [M3] Khoi dong mang\n')
    net.start()

    # ----------------------------------------
    # 7. Cau hinh VTEP IP (underlay) - Module 2
    # ----------------------------------------
    info('*** [M3] Cau hinh VTEP IP (underlay)\n')
    s1.cmd('ip addr add 192.168.1.1/30 dev s1')
    s2.cmd('ip addr add 192.168.1.2/30 dev s2')
    s1.cmd('ip link set s1 up')
    s2.cmd('ip link set s2 up')

    # Kiem tra nhanh underlay
    result = s1.cmd('ping -c 2 -W 2 192.168.1.2')
    if '0% packet loss' in result:
        info('*** [M3] Underlay OK\n')
    else:
        info('*** [M3] CANH BAO: Underlay FAILED! Kiem tra lai.\n')
        info(result)

    # ----------------------------------------
    # 8. Cau hinh VXLAN Tunnel - Module 3
    #
    #  s1: tao port vxlan1, tro toi VTEP cua s2 (192.168.1.2)
    #  s2: tao port vxlan2, tro toi VTEP cua s1 (192.168.1.1)
    #  Ten port phai KHAC NHAU vi ca 2 switch dung chung 1 OVS instance
    #  VNI = 100 (VXLAN Network Identifier)
    #  UDP port = 4789 (chuan IANA cho VXLAN)
    # ----------------------------------------
    info('\n*** [M3] Cau hinh VXLAN Tunnel (VNI=100)\n')

    # Tao VXLAN port tren s1 (ten: vxlan1)
    info('--- Tao vxlan1 tren s1 (remote_ip=192.168.1.2)\n')
    s1.cmd(
        'ovs-vsctl add-port s1 vxlan1 '
        '-- set interface vxlan1 '
        'type=vxlan '
        'options:remote_ip=192.168.1.2 '
        'options:key=100 '
        'options:dst_port=4789'
    )

    # Tao VXLAN port tren s2 (ten: vxlan2 - khac ten de tranh xung dot)
    info('--- Tao vxlan2 tren s2 (remote_ip=192.168.1.1)\n')
    s2.cmd(
        'ovs-vsctl add-port s2 vxlan2 '
        '-- set interface vxlan2 '
        'type=vxlan '
        'options:remote_ip=192.168.1.1 '
        'options:key=100 '
        'options:dst_port=4789'
    )

    # ----------------------------------------
    # 9. Xac nhan cau hinh VXLAN
    # ----------------------------------------
    info('\n*** [M3] Xac nhan cau hinh OVS sau khi them VXLAN\n')
    info('=== ovs-vsctl show ===\n')
    info(s1.cmd('ovs-vsctl show'))

    info('\n=== Kiem tra VXLAN interface tren s1 (vxlan1) ===\n')
    info(s1.cmd('ovs-vsctl list interface vxlan1'))

    info('\n=== Kiem tra VXLAN interface tren s2 (vxlan2) ===\n')
    info(s2.cmd('ovs-vsctl list interface vxlan2'))

    # ----------------------------------------
    # 10. Mo CLI
    # ----------------------------------------
    info('\n*** Mo Mininet CLI. Go "exit" de thoat.\n')
    info('Goi y lenh kiem tra:\n')
    info('  mininet> sh ovs-vsctl show\n')
    info('  mininet> sh ovs-vsctl list interface vxlan1  (s1)\n')
    info('  mininet> sh ovs-vsctl list interface vxlan2  (s2)\n')
    info('  mininet> h1 ping -c 3 10.0.0.2\n')
    CLI(net)

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    build_topology()
