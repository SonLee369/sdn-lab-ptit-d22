mininet> sh ovs-vsctl show

68aa1f77-4cfe-4e4f-b81b-5d4e2d367764
Bridge s1
fail_mode: standalone
Port s1-eth1
Interface s1-eth1
Port vxlan1
Interface vxlan1
type: vxlan
options: {dst_port="4789", key="100", remote_ip="192.168.1.2"}
Port s1-eth2
Interface s1-eth2
Port s1
Interface s1
type: internal
Bridge s2
fail_mode: standalone
Port s2-eth1
Interface s2-eth1
Port s2-eth2
Interface s2-eth2
Port s2
Interface s2
type: internal
ovs_version: "3.3.4"

mininet> sh ovs-vsctl list interface vxlan1

\_uuid : 9f7a2138-5384-4f7d-b4e1-a37dc4730806
admin_state : up
bfd : {}
bfd_status : {}
cfm_fault : []
cfm_fault_status : []
cfm_flap_count : []
cfm_health : []
cfm_mpid : []
cfm_remote_mpids : []
cfm_remote_opstate : []
duplex : []
error : []
external_ids : {}
ifindex : 60
ingress_policing_burst: 0
ingress_policing_kpkts_burst: 0
ingress_policing_kpkts_rate: 0
ingress_policing_rate: 0
lacp_current : []
link_resets : 0
link_speed : []
link_state : up
lldp : {}
mac : []
mac_in_use : "b6:bf:8d:d7:a9:fe"
mtu : []
mtu_request : []
name : vxlan1
ofport : 3
ofport_request : []
options : {dst_port="4789", key="100", remote_ip="192.168.1.2"}
other_config : {}
statistics : {rx_bytes=10668, rx_packets=81, tx_bytes=10848, tx_packets=83}
status : {tunnel_egress_iface=s2, tunnel_egress_iface_carrier=up}
type : vxlan
mininet>
