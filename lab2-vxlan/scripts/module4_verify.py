#!/usr/bin/env python3
"""
=============================================================
  VXLAN Lab - Module 4: L2 Overlay Verification
=============================================================
Topology:

  h1 (10.0.0.1/24)              h2 (10.0.0.2/24)
        |                              |
      [s1]  <==== VXLAN VNI 100 ====> [s2]
  VTEP: 192.168.1.1/30 ---------- VTEP: 192.168.1.2/30
        |______________________________|
               s1-eth2 <-> s2-eth2
                 (Underlay Link)

Muc tieu:
  1. Kiem tra ARP va ping giua h1 <-> h2 qua VXLAN overlay
  2. Bat goi tin tren underlay bang tcpdump de xac nhan
     goi tin duoc dong goi VXLAN (UDP port 4789)
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
    info('*** [M4] Don dep topo cu\n')
    cleanup()
    os.system('ip link delete s1-eth2 2>/dev/null')
    os.system('ip link delete s2-eth2 2>/dev/null')
    os.system('rm -f /tmp/vxlan_capture.txt')

    # ----------------------------------------
    # 2. Khoi tao Mininet
    # ----------------------------------------
    net = Mininet(controller=None)

    # ----------------------------------------
    # 3. Them hosts
    # ----------------------------------------
    info('*** [M4] Them hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')

    # ----------------------------------------
    # 4. Them OVS switches
    # ----------------------------------------
    info('*** [M4] Them OVS switches\n')
    s1 = net.addSwitch('s1', cls=OVSBridge, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSBridge, failMode='standalone')

    # ----------------------------------------
    # 5. Them links
    # ----------------------------------------
    info('*** [M4] Them links\n')
    net.addLink(h1, s1)   # h1-eth0 <-> s1-eth1
    net.addLink(h2, s2)   # h2-eth0 <-> s2-eth1
    net.addLink(s1, s2)   # s1-eth2 <-> s2-eth2 (underlay)

    # ----------------------------------------
    # 6. Khoi dong mang
    # ----------------------------------------
    info('*** [M4] Khoi dong mang\n')
    net.start()

    # ----------------------------------------
    # 7. Cau hinh VTEP IP (underlay)
    #    FIX: Xoa s1-eth2/s2-eth2 khoi bridge va gan IP truc tiep
    #    vao interface underlay. Neu de s1-eth2/s2-eth2 trong bridge
    #    se tao switching loop: VXLAN packet bi flood qua ca physical
    #    port lan vxlan port -> broadcast storm.
    # ----------------------------------------
    info('*** [M4] Cau hinh VTEP IP (xoa underlay port khoi bridge)\n')
    # Xoa s1-eth2/s2-eth2 khoi bridge de pha vo switching loop.
    # Trong Mininet, tat ca OVS bridge chung 1 namespace (root).
    # Neu s1-eth2 con trong bridge, VXLAN packet bi flood qua ca
    # physical port lan tunnel port -> broadcast storm.
    s1.cmd('ovs-vsctl del-port s1 s1-eth2')
    s2.cmd('ovs-vsctl del-port s2 s2-eth2')
    # Gan VTEP IP vao bridge interface (dev s1, dev s2).
    # Luu y: khong dung dev s1-eth2/s2-eth2 vi ca 2 IP
    # (192.168.1.1 va 192.168.1.2) deu o cung 1 namespace ->
    # kernel se chon sai source IP khi gui VXLAN (bug local-delivery).
    s1.cmd('ip addr add 192.168.1.1/30 dev s1')
    s2.cmd('ip addr add 192.168.1.2/30 dev s2')
    s1.cmd('ip link set s1 up')
    s2.cmd('ip link set s2 up')

    # ----------------------------------------
    # 8. Cau hinh VXLAN tunnel
    # ----------------------------------------
    info('*** [M4] Cau hinh VXLAN tunnel (VNI=100)\n')
    # Bat buoc phai co options:local_ip.
    # Khong co local_ip, OVS hoi kernel "source IP cho 192.168.1.2 la gi?"
    # Kernel tra loi 192.168.1.2 (vi day la local address trong cung namespace)
    # -> VXLAN packet gui voi src=192.168.1.2, dst=192.168.1.2
    # -> vxlan2 tu choi vi remote_ip=192.168.1.1 khong khop -> ARP that bai.
    s1.cmd(
        'ovs-vsctl add-port s1 vxlan1 '
        '-- set interface vxlan1 '
        'type=vxlan '
        'options:local_ip=192.168.1.1 '
        'options:remote_ip=192.168.1.2 '
        'options:key=100 '
        'options:dst_port=4789'
    )
    s2.cmd(
        'ovs-vsctl add-port s2 vxlan2 '
        '-- set interface vxlan2 '
        'type=vxlan '
        'options:local_ip=192.168.1.2 '
        'options:remote_ip=192.168.1.1 '
        'options:key=100 '
        'options:dst_port=4789'
    )

    # Cho OVS ap dung cau hinh
    time.sleep(1)

    # ----------------------------------------
    # 9. BAT TCPDUMP TREN UNDERLAY (BACKGROUND)
    #    Bat goi tin tren s1-eth2 (underlay link)
    #    Chi loc UDP port 4789 (VXLAN)
    #    -n: khong resolve hostname
    #    -v: verbose (hien thi chi tiet)
    #    -c 20: bat toi da 20 goi
    # ----------------------------------------
    # Trong Mininet same-namespace, VXLAN di qua local-delivery (loopback),
    # khong di qua s1-eth2 vat ly. Dung -i any de bat duoc.
    info('\n*** [M4] Bat tcpdump tren tat ca interface (UDP 4789)\n')
    os.system(
        'tcpdump -i any -n -v udp port 4789 -c 20 '
        '> /tmp/vxlan_capture.txt 2>&1 &'
    )
    time.sleep(1)

    # ----------------------------------------
    # 10. KIEM TRA ARP
    #     Xoa ARP cache truoc de dam bao ARP request duoc tao ra
    # ----------------------------------------
    info('\n*** [M4] Xoa ARP cache tren h1 va h2\n')
    h1.cmd('ip neigh flush all')
    h2.cmd('ip neigh flush all')

    info('*** [M4] Kiem tra ARP: h1 -> h2\n')
    arp_result = h1.cmd('arping -c 3 -I h1-eth0 10.0.0.2')
    info(arp_result)

    # ----------------------------------------
    # 11. KIEM TRA PING (L2 Overlay)
    # ----------------------------------------
    info('\n*** [M4] Kiem tra ping: h1 (10.0.0.1) -> h2 (10.0.0.2)\n')
    ping_result = h1.cmd('ping -c 5 -W 2 10.0.0.2')
    info(ping_result)

    if '0% packet loss' in ping_result:
        info('>>> KET QUA: L2 OVERLAY OK - h1 va h2 thong nhau qua VXLAN!\n')
    else:
        info('>>> KET QUA: OVERLAY FAILED - Kiem tra lai cau hinh!\n')

    # ----------------------------------------
    # 12. CHO TCPDUMP HOAN TAT VA IN KET QUA
    # ----------------------------------------
    info('\n*** [M4] Cho tcpdump hoan tat...\n')
    time.sleep(3)
    os.system('kill %1 2>/dev/null')  # Dung tcpdump neu van con chay

    info('\n*** [M4] Ket qua bat goi tin VXLAN (tcpdump):\n')
    info('=' * 60 + '\n')
    capture = os.popen('cat /tmp/vxlan_capture.txt').read()
    info(capture)
    info('=' * 60 + '\n')

    # ----------------------------------------
    # 13. KIEM TRA ARP TABLE
    # ----------------------------------------
    info('\n*** [M4] ARP table sau khi ping:\n')
    info('h1 ARP table:\n')
    info(h1.cmd('arp -n'))
    info('h2 ARP table:\n')
    info(h2.cmd('arp -n'))

    # ----------------------------------------
    # 14. KIEM TRA MAC TABLE TREN OVS
    # ----------------------------------------
    info('\n*** [M4] MAC table cua OVS (da hoc qua VXLAN):\n')
    info('s1 MAC table:\n')
    info(s1.cmd('ovs-appctl fdb/show s1'))
    info('s2 MAC table:\n')
    info(s2.cmd('ovs-appctl fdb/show s2'))

    # ----------------------------------------
    # 15. Mo CLI de kiem tra them
    # ----------------------------------------
    info('\n*** Mo Mininet CLI. Go "exit" de thoat.\n')
    info('Goi y lenh:\n')
    info('  mininet> h1 ping -c 3 10.0.0.2\n')
    info('  mininet> h2 ping -c 3 10.0.0.1\n')
    info('  mininet> h1 arp -n\n')
    info('  mininet> sh ovs-appctl fdb/show s1\n')
    info('  mininet> sh tcpdump -i s1-eth2 -n udp port 4789 -c 5\n')
    CLI(net)

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    build_topology()
