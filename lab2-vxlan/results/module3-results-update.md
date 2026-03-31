mininet> sh ovs-vsctl show
68aa1f77-4cfe-4e4f-b81b-5d4e2d367764
Bridge s1
fail_mode: standalone
Port vxlan1
Interface vxlan1
type: vxlan
options: {dst_port="4789", key="100", remote_ip="192.168.1.2"}
Port s1
Interface s1
type: internal
Port s1-eth2
Interface s1-eth2
Port s1-eth1
Interface s1-eth1
Bridge s2
fail_mode: standalone
Port vxlan2
Interface vxlan2
type: vxlan
options: {dst_port="4789", key="100", remote_ip="192.168.1.1"}
Port s2
Interface s2
type: internal
Port s2-eth1
Interface s2-eth1
Port s2-eth2
Interface s2-eth2
ovs_version: "3.3.4"

mininet> sh ovs-vsctl list interface vxlan1
\_uuid : 2ab382e6-3663-4dd5-bb93-01d02bff4d4b
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
ifindex : 68
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
mac_in_use : "06:e8:4e:ce:e2:75"
mtu : []
mtu_request : []
name : vxlan1
ofport : 3
ofport_request : []
options : {dst_port="4789", key="100", remote_ip="192.168.1.2"}
other_config : {}
statistics : {rx_bytes=612849511, rx_packets=4313821, tx_bytes=612875786, tx_packets=4314020}
status : {tunnel_egress_iface=s2, tunnel_egress_iface_carrier=up}
type : vxlan

mininet> sh ovs-vsctl list interface vxlan2
\_uuid : d52783f3-a816-4a12-bc90-307a310f5175
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
ifindex : 68
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
mac_in_use : "ce:9d:cf:ac:b6:5c"
mtu : []
mtu_request : []
name : vxlan2
ofport : 3
ofport_request : []
options : {dst_port="4789", key="100", remote_ip="192.168.1.1"}
other_config : {}
statistics : {rx_bytes=825750150, rx_packets=5863226, tx_bytes=825691157, tx_packets=5862834}
status : {tunnel_egress_iface=s1, tunnel_egress_iface_carrier=up}
type : vxlan
mininet>
