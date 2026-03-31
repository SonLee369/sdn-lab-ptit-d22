#!/usr/bin/env python3
"""
Lab 3: VXLAN over SDN with Mininet + OVS
Topology:
    h1 (192.168.100.1) --- s1 (VTEP: 10.0.0.1)
                               ||  VXLAN VNI 100 (UDP 4789)
    h2 (192.168.100.2) --- s2 (VTEP: 10.0.0.2)
"""

from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


# ─────────────────────────────────────────────
#  Constants
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
#  Helper: configure VXLAN on one OVS bridge
# ─────────────────────────────────────────────
def add_vxlan_port(switch, port_name, local_ip, remote_ip, vni):
    """Add a VXLAN tunnel port to an OVS bridge."""
    switch.cmd(
        f'ovs-vsctl add-port {switch.name} {port_name}'
        f' -- set interface {port_name} type=vxlan'
        f' options:local_ip={local_ip}'
        f' options:remote_ip={remote_ip}'
        f' options:key={vni}'
        f' options:dst_port={VXLAN_PORT}'
    )


# ─────────────────────────────────────────────
#  Main topology builder
# ─────────────────────────────────────────────
def build_topology():

    # --- Create network (no external controller needed) ---
    net = Mininet(controller=None, link=TCLink)

    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip=f'{OVERLAY_H1}/{OVERLAY_MASK}')
    h2 = net.addHost('h2', ip=f'{OVERLAY_H2}/{OVERLAY_MASK}')

    info('*** Adding OVS bridges (VTEPs)\n')
    # failMode=standalone → OVS acts as a self-learning L2 switch
    s1 = net.addSwitch('s1', cls=OVSBridge, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSBridge, failMode='standalone')

    info('*** Adding links\n')
    # Overlay links: hosts ↔ switches
    net.addLink(h1, s1)   # h1-eth0 ↔ s1-eth1
    net.addLink(h2, s2)   # h2-eth0 ↔ s2-eth1

    # Underlay link: switch ↔ switch (simulates L3 network)
    net.addLink(s1, s2)   # s1-eth2 ↔ s2-eth2

    # --- Start network ---
    info('*** Starting network\n')
    net.start()

    # ── Step 1: Remove underlay veth from OVS bridges ─────────────────────
    # ROOT CAUSE FIX: s1-eth2/s2-eth2 inside OVS bridges + VXLAN tunnel
    # = TWO L2 paths between s1 and s2 → OVS floods both → broadcast storm.
    # Fix: pull the underlay veth OUT of OVS, make it a plain kernel interface.
    # s1 bridge will only have: s1-eth1 (h1) + vxlan0 (tunnel). No loop.
    info('*** Removing underlay veth from OVS bridges (prevent L2 loop)\n')
    s1.cmd('ovs-vsctl del-port s1 s1-eth2')
    s2.cmd('ovs-vsctl del-port s2 s2-eth2')

    # ── Step 2: Assign VTEP IPs to raw underlay veth interfaces ───────────
    # These veth interfaces are now plain kernel interfaces — NOT in any bridge.
    # The kernel uses these IPs as VTEP source/dest for VXLAN encapsulation.
    info(f'*** Assigning underlay IPs: s1-eth2={UNDERLAY_S1}, s2-eth2={UNDERLAY_S2}\n')
    s1.cmd(f'ip addr add {UNDERLAY_S1}/{UNDERLAY_MASK} dev s1-eth2')
    s2.cmd(f'ip addr add {UNDERLAY_S2}/{UNDERLAY_MASK} dev s2-eth2')
    s1.cmd('ip link set s1-eth2 up')
    s2.cmd('ip link set s2-eth2 up')

    # ── Step 3: Verify underlay reachability ──────────────────────────────
    info('*** Testing underlay connectivity (s1 → s2)\n')
    result = s1.cmd(f'ping -c 2 -W 2 {UNDERLAY_S2}')
    if '2 received' in result or '1 received' in result:
        info('    [OK] Underlay reachable\n')
    else:
        info('    [WARN] Underlay ping failed — check veth IPs\n')

    # ── Step 4: Add VXLAN tunnel ports ────────────────────────────────────
    # OVS requires globally unique interface names across all bridges on the
    # same instance => s1 uses 'vxlan0', s2 uses 'vxlan1'
    info(f'*** Adding VXLAN tunnel ports (VNI={VNI})\n')
    add_vxlan_port(s1, 'vxlan0', UNDERLAY_S1, UNDERLAY_S2, VNI)
    add_vxlan_port(s2, 'vxlan1', UNDERLAY_S2, UNDERLAY_S1, VNI)

    # ── Step 5: Remove default gateway from hosts (not needed here) ───────
    h1.cmd('ip route del default 2>/dev/null; true')
    h2.cmd('ip route del default 2>/dev/null; true')

    # ── Print summary ──────────────────────────────────────────────────────
    info('\n' + '='*55 + '\n')
    info('  Topology ready!\n')
    info(f'  Underlay : s1={UNDERLAY_S1}  s2={UNDERLAY_S2}\n')
    info(f'  Overlay  : h1={OVERLAY_H1}  h2={OVERLAY_H2}\n')
    info(f'  VXLAN    : VNI={VNI}  UDP={VXLAN_PORT}\n')
    info('='*55 + '\n\n')
    info('  Try: h1 ping h2  →  pingall  →  h1 ping 192.168.100.2\n\n')

    # --- Open Mininet CLI ---
    CLI(net)

    # --- Cleanup ---
    info('*** Stopping network\n')
    net.stop()


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == '__main__':
    setLogLevel('info')
    build_topology()
