\*\*\_ [M2] Them hosts

\_\*\* [M2] Them OVS switches

\*\*\* [M2] Them links

Traceback (most recent call last):

File "/home/son/lab2-vxlan/vxlan.py", line 117, in <module>

build_topology()

File "/home/son/lab2-vxlan/vxlan.py", line 64, in build_topology

net.addLink(s1, s2)

File "/usr/lib/python3/dist-packages/mininet/net.py", line 406, in addLink
link = cls( node1, node2, \*\*options )

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/usr/lib/python3/dist-packages/mininet/link.py", line 568, in **init**
Link.**init**( self, \*args, \*\*kwargs)
File "/usr/lib/python3/dist-packages/mininet/link.py", line 456, in **init**
self.makeIntfPair( intfName1, intfName2, addr1, addr2,
File "/usr/lib/python3/dist-packages/mininet/link.py", line 501, in makeIntfPair
return makeIntfPair( intfname1, intfname2, addr1, addr2, node1, node2,
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/usr/lib/python3/dist-packages/mininet/util.py", line 270, in makeIntfPair
raise Exception( "Error creating interface pair (%s,%s): %s " %
Exception: Error creating interface pair (s1-eth2,s2-eth2): RTNETLINK answers: File exists
