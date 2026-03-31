#!/usr/bin/env python3
"""
=============================================================
  VXLAN Lab - Module 2: Underlay L3 Network
=============================================================
Topology:

  h1 (10.0.0.1/24)            h2 (10.0.0.2/24)
        |                            |
      [s1]                         [s2]
  VTEP: 192.168.1.1/30 ---- VTEP: 192.168.1.2/30
        |____________________________|
               Underlay Link
               (s1-eth2 <-> s2-eth2)

Muc tieu:
  - Xay dung ket noi L3 giua 2 OVS switch (underlay)
  - Xac nhan ping duoc giua 2 VTEP: 192.168.1.1 <-> 192.168.1.2
=============================================================
"""

import os
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.clean import cleanup


def build_topology():
    # -------------------------
    # 1. Don dep topo cu truoc khi tao moi
    # -------------------------
    info('*** [M2] Don dep topo cu (mn -c)\n')
    cleanup()
    os.system('ip link delete s1-eth2 2>/dev/null; ip link delete s2-eth2 2>/dev/null')

    # -------------------------
    # 2. Khoi tao mang Mininet
    # -------------------------
    net = Mininet(controller=None)

    # -------------------------
    # 2. Them hosts
    # -------------------------
    info('*** [M2] Them hosts\n')
    h1 = net.addHost('h1',
                     ip='10.0.0.1/24',
                     mac='00:00:00:00:00:01')
    h2 = net.addHost('h2',
                     ip='10.0.0.2/24',
                     mac='00:00:00:00:00:02')

    # -------------------------
    # 3. Them OVS switches
    #    failMode='standalone' -> OVS dung che do NORMAL (hoc MAC, forward)
    #    khi khong co controller
    # -------------------------
    info('*** [M2] Them OVS switches\n')
    s1 = net.addSwitch('s1', cls=OVSBridge, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSBridge, failMode='standalone')

    # -------------------------
    # 4. Them links
    #    h1 -- s1 : h1-eth0 <-> s1-eth1
    #    h2 -- s2 : h2-eth0 <-> s2-eth1
    #    s1 -- s2 : s1-eth2 <-> s2-eth2  (underlay link)
    # -------------------------
    info('*** [M2] Them links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(s1, s2)

    # -------------------------
    # 5. Khoi dong mang
    # -------------------------
    info('*** [M2] Khoi dong mang\n')
    net.start()

    # -------------------------
    # 6. Gan IP cho bridge interface (VTEP IP)
    #    Muc dich: 2 switch co the ping nhau qua underlay
    # -------------------------
    info('*** [M2] Cau hinh VTEP IP tren underlay\n')
    s1.cmd('ip addr add 192.168.1.1/30 dev s1')
    s2.cmd('ip addr add 192.168.1.2/30 dev s2')

    # Kich hoat bridge interface
    s1.cmd('ip link set s1 up')
    s2.cmd('ip link set s2 up')

    # -------------------------
    # 7. Kiem tra ket noi underlay
    # -------------------------
    info('\n*** [M2] Kiem tra ket noi underlay (ping VTEP)\n')
    info('--- s1 (192.168.1.1) ping s2 (192.168.1.2) ---\n')
    result = s1.cmd('ping -c 4 -W 2 192.168.1.2')
    info(result)

    if '0% packet loss' in result:
        info('>>> KET QUA: UNDERLAY OK - 2 VTEP ket noi thanh cong!\n\n')
    else:
        info('>>> KET QUA: UNDERLAY FAILED - Kiem tra lai cau hinh!\n\n')

    # -------------------------
    # 8. In thong tin topo
    # -------------------------
    info('=== THONG TIN TOPO ===\n')
    info('s1 interfaces:\n')
    info(s1.cmd('ip addr show'))
    info('s2 interfaces:\n')
    info(s2.cmd('ip addr show'))

    # -------------------------
    # 9. Mo Mininet CLI
    # -------------------------
    info('*** Mo Mininet CLI. Go "exit" de thoat.\n')
    CLI(net)

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    build_topology()
