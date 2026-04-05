son@son-SDN-VM:~/lab3-sdn$ ryu-manager controller.py
2 RLock(s) were not greened, to fix this error make sure you run eventlet.monkey_patch() before importing any other modules.
loading app controller.py
loading app ryu.controller.ofp_handler
instantiating app controller.py of L2LearningSwitch
instantiating app ryu.controller.ofp_handler of OFPHandler
[CONNECT] Switch dpid=0x0000000000000001 đã kết nối
[FLOW] priority=0 | match=OFPMatch(oxm_fields={}) | idle_timeout=30s
[FLOW] Switch dpid=0x0000000000000001 — Đã cài table-miss rule
[LEARN] dpid=0x0000000000000001 | MAC 00:00:00:00:00:04 → port 4
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 33:33:ff:00:00:04 (unknown dst, flooding)
[LEARN] dpid=0x0000000000000001 | MAC 00:00:00:00:00:02 → port 2
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 33:33:00:00:00:16 (unknown dst, flooding)
[LEARN] dpid=0x0000000000000001 | MAC 00:00:00:00:00:03 → port 3
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 33:33:00:00:00:16 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 33:33:ff:00:00:03 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 33:33:00:00:00:16 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 33:33:ff:00:00:02 (unknown dst, flooding)
[LEARN] dpid=0x0000000000000001 | MAC 00:00:00:00:00:01 → port 1
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 33:33:ff:00:00:01 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 33:33:00:00:00:16 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 33:33:00:00:00:16 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 33:33:00:00:00:16 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 33:33:00:00:00:16 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 33:33:00:00:00:16 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 33:33:00:00:00:16 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 33:33:00:00:00:16 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 33:33:00:00:00:16 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 33:33:00:00:00:02 (unknown dst, flooding)
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → ff:ff:ff:ff:ff:ff (unknown dst, flooding)
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 00:00:00:00:00:01 via port 1
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 2, 'eth_dst': '00:00:00:00:00:01', 'eth_src': '00:00:00:00:00:02'}) | idle_timeout=30s
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 00:00:00:00:00:02 via port 2
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 1, 'eth_dst': '00:00:00:00:00:02', 'eth_src': '00:00:00:00:00:01'}) | idle_timeout=30s
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → ff:ff:ff:ff:ff:ff (unknown dst, flooding)
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 00:00:00:00:00:01 via port 1
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 3, 'eth_dst': '00:00:00:00:00:01', 'eth_src': '00:00:00:00:00:03'}) | idle_timeout=30s
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 00:00:00:00:00:03 via port 3
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 1, 'eth_dst': '00:00:00:00:00:03', 'eth_src': '00:00:00:00:00:01'}) | idle_timeout=30s
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:01 → ff:ff:ff:ff:ff:ff (unknown dst, flooding)
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 00:00:00:00:00:01 via port 1
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 4, 'eth_dst': '00:00:00:00:00:01', 'eth_src': '00:00:00:00:00:04'}) | idle_timeout=30s
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:01 → 00:00:00:00:00:04 via port 4
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 1, 'eth_dst': '00:00:00:00:00:04', 'eth_src': '00:00:00:00:00:01'}) | idle_timeout=30s
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → ff:ff:ff:ff:ff:ff (unknown dst, flooding)
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 00:00:00:00:00:02 via port 2
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 3, 'eth_dst': '00:00:00:00:00:02', 'eth_src': '00:00:00:00:00:03'}) | idle_timeout=30s
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 00:00:00:00:00:03 via port 3
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 2, 'eth_dst': '00:00:00:00:00:03', 'eth_src': '00:00:00:00:00:02'}) | idle_timeout=30s
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:02 → ff:ff:ff:ff:ff:ff (unknown dst, flooding)
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 00:00:00:00:00:02 via port 2
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 4, 'eth_dst': '00:00:00:00:00:02', 'eth_src': '00:00:00:00:00:04'}) | idle_timeout=30s
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:02 → 00:00:00:00:00:04 via port 4
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 2, 'eth_dst': '00:00:00:00:00:04', 'eth_src': '00:00:00:00:00:02'}) | idle_timeout=30s
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:03 → ff:ff:ff:ff:ff:ff (unknown dst, flooding)
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:04 → 00:00:00:00:00:03 via port 3
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 4, 'eth_dst': '00:00:00:00:00:03', 'eth_src': '00:00:00:00:00:04'}) | idle_timeout=30s
[MATCH] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 00:00:00:00:00:04 via port 4
[FLOW] priority=1 | match=OFPMatch(oxm_fields={'in_port': 3, 'eth_dst': '00:00:00:00:00:04', 'eth_src': '00:00:00:00:00:03'}) | idle_timeout=30s
[FLOOD] dpid=0x0000000000000001 | 00:00:00:00:00:03 → 33:33:00:00:00:02 (unknown dst, flooding)
