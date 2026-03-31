# Bao Cao Lab VXLAN — Module 2: Underlay L3 Network

---

## 1. Muc Tieu

Xay dung mang underlay L3 giua 2 OVS switch trong Mininet, dam bao 2 VTEP co the ping duoc nhau truoc khi trien khai VXLAN tunnel o Module 3.

---

## 2. Mo Hinh Topo

```
  h1 (10.0.0.1/24)              h2 (10.0.0.2/24)
        |                              |
      [s1]                           [s2]
  VTEP: 192.168.1.1/30 -------- VTEP: 192.168.1.2/30
        |____________________________|
                 Underlay Link
              (s1-eth2 <-> s2-eth2)
```

| Thanh phan        | Ten                 | Dia chi IP     |
| ----------------- | ------------------- | -------------- |
| Host 1            | h1                  | 10.0.0.1/24    |
| Host 2            | h2                  | 10.0.0.2/24    |
| Switch 1 (VTEP 1) | s1                  | 192.168.1.1/30 |
| Switch 2 (VTEP 2) | s2                  | 192.168.1.2/30 |
| Underlay link     | s1-eth2 <-> s2-eth2 | 192.168.1.0/30 |

---

## 3. Moi Truong Lab

| Thanh phan         | Phien ban |
| ------------------ | --------- |
| Mininet            | 2.x       |
| Open vSwitch (OVS) | 3.3.4     |
| He dieu hanh       | Ubuntu    |
| Python             | 3.x       |

---

## 4. Cac Buoc Thuc Hien

### Buoc 1 — Cai dat moi truong

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install mininet openvswitch-switch python3 -y
sudo systemctl start openvswitch-switch
```

### Buoc 2 — Tao file script

Tao file `module2_underlay.py` voi noi dung:

```python
#!/usr/bin/env python3
import os
from mininet.net import Mininet
from mininet.node import OVSBCheridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.clean import cleanup

def build_topology():
    # Don dep topo cu
    info('*** [M2] Don dep topo cu (mn -c)\n')
    cleanup()
    os.system('ip link delete s1-eth2 2>/dev/null; ip link delete s2-eth2 2>/dev/null')

    # Khoi tao mang
    net = Mininet(controller=None)

    # Them hosts
    info('*** [M2] Them hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')

    # Them OVS switches (failMode=standalone: khong can controller)
    info('*** [M2] Them OVS switches\n')
    s1 = net.addSwitch('s1', cls=OVSBridge, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSBridge, failMode='standalone')

    # Them links
    info('*** [M2] Them links\n')
    net.addLink(h1, s1)   # h1-eth0 <-> s1-eth1
    net.addLink(h2, s2)   # h2-eth0 <-> s2-eth1
    net.addLink(s1, s2)   # s1-eth2 <-> s2-eth2 (underlay)

    # Khoi dong mang
    net.start()

    # Gan VTEP IP cho bridge interface
    info('*** [M2] Cau hinh VTEP IP\n')
    s1.cmd('ip addr add 192.168.1.1/30 dev s1')
    s2.cmd('ip addr add 192.168.1.2/30 dev s2')
    s1.cmd('ip link set s1 up')
    s2.cmd('ip link set s2 up')

    # Kiem tra ket noi
    info('\n*** [M2] Kiem tra ket noi underlay\n')
    result = s1.cmd('ping -c 4 -W 2 192.168.1.2')
    info(result)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    build_topology()
```

### Buoc 3 — Don dep va chay script

```bash
# Don dep topo cu (neu co)
sudo mn -c

# Chay script
sudo python3 module2_underlay.py
```

### Buoc 4 — Kiem tra trong Mininet CLI

```bash
# Kiem tra IP cua s1
mininet> sh ip addr show dev s1

# Kiem tra IP cua s2
mininet> sh ip addr show dev s2

# Ping giua 2 VTEP (quan trong nhat)
mininet> sh ping -c 3 192.168.1.2

# Xem cau hinh OVS
mininet> sh ovs-vsctl show
```

---

## 5. Ket Qua Thuc Te

### 5.1 Cau hinh s1

```
51: s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    link/ether c2:09:07:68:94:46 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.1/30 scope global s1
```

### 5.2 Cau hinh s2

```
52: s2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    link/ether 12:69:16:e0:1a:45 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.2/30 scope global s2
```

### 5.3 Ping giua 2 VTEP

```
PING 192.168.1.2 (192.168.1.2) 56(84) bytes of data.
64 bytes from 192.168.1.2: icmp_seq=1 ttl=64 time=0.073 ms
64 bytes from 192.168.1.2: icmp_seq=2 ttl=64 time=0.571 ms
64 bytes from 192.168.1.2: icmp_seq=3 ttl=64 time=0.084 ms

--- 192.168.1.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2034ms
rtt min/avg/max/mdev = 0.073/0.242/0.571/0.232 ms
```

### 5.4 Cau truc OVS

```
Bridge s1
    fail_mode: standalone
    Port s1-eth2      <- ket noi toi s2 (underlay)
    Port s1-eth1      <- ket noi toi h1
    Port s1           <- bridge interface (VTEP IP)
        type: internal

Bridge s2
    fail_mode: standalone
    Port s2-eth1      <- ket noi toi h2
    Port s2-eth2      <- ket noi toi s1 (underlay)
    Port s2           <- bridge interface (VTEP IP)
        type: internal

ovs_version: "3.3.4"
```

---

## 6. Phan Tich

| Tieu chi       | Ket qua    | Ghi chu                                            |
| -------------- | ---------- | -------------------------------------------------- |
| s1 co VTEP IP  | OK         | 192.168.1.1/30                                     |
| s2 co VTEP IP  | OK         | 192.168.1.2/30                                     |
| Ping s1 -> s2  | OK         | 0% packet loss                                     |
| RTT trung binh | 0.242 ms   | Rat thap, phu hop moi truong Mininet               |
| OVS failMode   | standalone | Khong can SDN controller                           |
| Port mapping   | Dung       | s1-eth1/s2-eth1 (host), s1-eth2/s2-eth2 (underlay) |

---

## 7. Loi Gap Va Cach Xu Ly

| Loi                                                   | Nguyen nhan                             | Cach xu ly                                  |
| ----------------------------------------------------- | --------------------------------------- | ------------------------------------------- |
| `RTNETLINK answers: File exists`                      | Interface con ton tai tu lan chay truoc | Chay `sudo mn -c` truoc khi chay lai script |
| Script dung `link=TCLink` bi loi voi switch-to-switch | TCLink khong tuong thich                | Xoa `link=TCLink`, dung Link mac dinh       |

---

## 8. Ket Luan

Module 2 hoan thanh thanh cong. Mang underlay L3 da duoc thiet lap voi:

- 2 OVS switch hoat dong o che do `standalone`
- 2 VTEP co dia chi IP trong subnet `192.168.1.0/30`
- Ket noi L3 thong suot giua 2 VTEP (0% packet loss)

**San sang cho Module 3: Cau hinh VXLAN Tunnel.**

---

_Ngay thuc hien: 30/03/2026_
