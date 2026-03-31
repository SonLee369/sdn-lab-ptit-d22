# Module 6 — Ke Hoach (Chua Thuc Hien)

> **Trang thai**: Chua bat dau — luu lai de thuc hien sau.

---

## Cac Lua Chon Module 6

### Option A — Static FDB / Unicast VXLAN ★★☆

**Muc tieu**: Thay the co che ARP flooding mac dinh bang **static MAC entries** trong FDB cua OVS. Moi VTEP biet truoc MAC cua tat ca host → khong can broadcast ARP qua tunnel.

**Ly do quan trong**:
- Trong datacenter lon, ARP flooding qua VXLAN gay ton bang thong underlay
- Production VXLAN (EVPN, SDN) deu dung unicast thay flooding
- Day la buoc tien gan voi thuc te nhat

**Topology** (ke thua Module 4):
```
  h1 (10.0.0.1)                    h2 (10.0.0.2)
       |                                 |
     [s1] ====== VXLAN VNI 100 ====== [s2]
  VTEP: 192.168.1.1              VTEP: 192.168.1.2
```

**Cac buoc thuc hien**:

1. Tat ARP flooding tren bridge (dung `arpcache` hoac flow rules)
2. Them static FDB entry tren s1: "MAC cua h2 nam o VTEP 192.168.1.2"
3. Them static FDB entry tren s2: "MAC cua h1 nam o VTEP 192.168.1.1"
4. Kiem tra: ping h1 → h2 **khong can ARP broadcast**

**Cau hinh chinh**:
```bash
# Tren s1: chi h2 MAC tren VTEP s2
bridge fdb add 00:00:00:00:00:02 dev vxlan1 dst 192.168.1.2 vni 100

# Tren s2: chi h1 MAC tren VTEP s1
bridge fdb add 00:00:00:00:00:01 dev vxlan2 dst 192.168.1.1 vni 100
```

**Kiem tra**:
```bash
# Xoa ARP cache, ping (khong duoc co ARP broadcast qua tunnel)
h1.cmd('ip neigh flush all')
h1.cmd('ping -c 3 10.0.0.2')

# Xac nhan: tcpdump tren underlay KHONG thay ARP broadcast
# Chi thay ICMP duoc dong goi trong VXLAN
```

---

### Option B — VXLAN Traffic Analysis (tcpdump deep-dive) ★☆☆

**Muc tieu**: Bat va phan tich chi tiet tung byte cua goi tin VXLAN, giai thich tung tang header.

**Topology**: Ke thua Module 4 (h1 ↔ h2 qua VXLAN VNI 100).

**Cac buoc thuc hien**:

1. Chay Module 4 topo
2. Bat `tcpdump -i any -XX -v udp port 4789` trong khi h1 ping h2
3. Giai thich tung truong trong output:
   - Outer Ethernet header
   - Outer IP header (src=192.168.1.1, dst=192.168.1.2)
   - UDP header (src port random, dst port 4789)
   - VXLAN header (flag=0x08, VNI=100)
   - Inner Ethernet header (src=h1 MAC, dst=h2 MAC)
   - Inner IP header (src=10.0.0.1, dst=10.0.0.2)
   - ICMP payload

**Mau tcpdump can phan tich**:
```
IP 192.168.1.1.PORT > 192.168.1.2.4789: VXLAN, flags [I] (0x08), vni 100
IP 10.0.0.1 > 10.0.0.2: ICMP echo request
```

**So sanh overhead**:
```
Goi tin goc (ICMP):    14 + 20 + 8 = 42 bytes header
Goi tin VXLAN:         14 + 20 + 8 + 8 + 14 = 64 bytes header (+50 bytes)
Ty le overhead:        ~119% voi goi 84 bytes payload
```

---

### Option C — VXLAN + Inter-VNI Routing (VXLAN Gateway) ★★★

**Muc tieu**: Them mot **router node** lam cau noi co kiem soat giua VNI 100 va VNI 200. Mo phong khai niem **Integrated Routing & Bridging (IRB)** / **VXLAN Gateway**.

**Topology**:
```
  [VNI 100]                                    [VNI 200]
  h1 (10.0.0.1) --- s1a === VXLAN 100 === s2a --- h2 (10.0.0.2)
                     |                     |
                    [GW] router node       |
                     |                     |
  h3 (10.1.0.1) --- s1b === VXLAN 200 === s2b --- h4 (10.1.0.2)
  [VNI 200]
```

**Nguyen ly**:
- Trong cung VNI: giao tiep L2 (khong qua router)
- Khac VNI: phai qua Gateway (router) → co the ap dung ACL/policy

**Cac buoc thuc hien**:
1. Ke thua Module 5 topo (4 bridges, 2 VNI)
2. Them host `gw` lam router (ip_forward=1)
3. `gw` co 2 interface: mot trong VNI 100, mot trong VNI 200
4. Them static route tren h1, h3 qua gw
5. Kiem tra: h1 (VNI 100) ping h3 (VNI 200) phai di qua gw

**Kiem tra**:
```bash
# Ping inter-VNI (qua gateway)
h1 ping 10.1.0.1   # phai PASS (qua gw)

# Xac nhan di qua gw
h1 traceroute 10.1.0.1  # phai thay gw IP
```

---

### Option D — EVPN Control Plane (FRRouting) ★★★★

**Muc tieu**: Dung **BGP EVPN** (RFC 7432) de phan phoi MAC/IP thay vi ARP flood. VTEP quang ba MAC cua host qua BGP → cac VTEP khac cap nhat FDB tu dong.

**Yeu cau them**:
- FRRouting (frr) phai duoc cai tren he thong
- Kien thuc BGP co ban

**Topology**:
```
  h1 --- [VTEP1/frr] --- BGP EVPN --- [VTEP2/frr] --- h2
                              |
                         [Route Reflector]
```

**Khai niem chinh**:
- **Type-2 Route (MAC/IP Advertisement)**: VTEP quang ba MAC+IP cua host local
- **Type-3 Route (Inclusive Multicast)**: Dang ky nhan BUM traffic
- **RD/RT (Route Distinguisher/Target)**: Phan biet VNI trong BGP

**Cau hinh FRRouting (vi du)**:
```
router bgp 65000
  neighbor 192.168.1.2 remote-as 65000
  address-family l2vpn evpn
    neighbor 192.168.1.2 activate
    advertise-all-vni
```

---

## Uu Tien De Xuat

```
Do kho:  A < B < C < D
Gia tri: B < A < C < D
Sat thuc te: B < A < C = D
```

| Option | Thoi gian uoc tinh | Phu hop neu... |
|--------|------------------|---------------|
| A — Static FDB | 1 buoi | Muon hieu production VXLAN |
| B — Traffic Analysis | 0.5 buoi | Muon hieu goi tin chi tiet |
| C — Inter-VNI Routing | 2 buoi | Muon lam VXLAN Gateway |
| D — EVPN | 3+ buoi | Da co FRRouting, muon lam full |

---

## Ghi Chu Ky Thuat De Nho

- **Mininet same-namespace**: VXLAN dung local delivery, can `options:local_ip`
- **Port name unique**: Moi VXLAN port phai co ten khac nhau trong toan bo OVS instance
- **del-port underlay**: Phai xoa `s1-eth2` khoi bridge truoc khi cau hinh VXLAN
- **Script chuan bi**: Chay `sudo mn -c` truoc moi lan chay script moi

---

*Ke hoach tao ngay: 30/03/2026 — Thuc hien sau*
