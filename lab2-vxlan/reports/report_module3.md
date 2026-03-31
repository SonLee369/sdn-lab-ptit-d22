# Bao Cao Lab VXLAN — Module 3: VXLAN Tunnel Setup

---

## 1. Muc Tieu

Thiet lap VXLAN tunnel giua 2 OVS switch (s1 va s2) su dung VNI 100, chuan bi nen tang overlay L2 cho Module 4.

---

## 2. Mo Hinh Topo

```
  h1 (10.0.0.1/24)              h2 (10.0.0.2/24)
        |                              |
      [s1]  <==== VXLAN VNI 100 ====> [s2]
  VTEP: 192.168.1.1/30 ---------- VTEP: 192.168.1.2/30
        |______________________________|
                  Underlay Link
               (s1-eth2 <-> s2-eth2)
```

| Thanh phan | Chi tiet |
|-----------|---------|
| VXLAN VNI | 100 |
| UDP Port | 4789 (chuan IANA) |
| VTEP s1 | 192.168.1.1 — port `vxlan1` |
| VTEP s2 | 192.168.1.2 — port `vxlan2` |

---

## 3. Nguyen Ly VXLAN

```
 Goi tin truoc khi dong goi (overlay):
 +------------------+
 |  Ethernet Frame  |  <- L2 giua h1 va h2
 +------------------+

 Goi tin sau khi dong goi (underlay):
 +------------+--------+--------+------------------+
 | Outer IP   | UDP    | VXLAN  |  Ethernet Frame  |
 | src:1.1    | 4789   | VNI=100|  (payload goc)   |
 | dst:1.2    |        |        |                  |
 +------------+--------+--------+------------------+
  ^--- Underlay header (192.168.1.0/30) ---^
```

- **Encapsulation**: s1 nhan frame tu h1, dong goi vao VXLAN/UDP/IP roi gui qua underlay
- **Decapsulation**: s2 nhan goi tu underlay, go bo VXLAN header, chuyen frame goc toi h2

---

## 4. Cac Buoc Thuc Hien

### Buoc 1 — Don dep va chay script

```bash
sudo mn -c
sudo python3 module3_vxlan.py
```

### Buoc 2 — Cau hinh VXLAN tren s1

```bash
ovs-vsctl add-port s1 vxlan1 \
  -- set interface vxlan1 \
     type=vxlan \
     options:remote_ip=192.168.1.2 \
     options:key=100 \
     options:dst_port=4789
```

### Buoc 3 — Cau hinh VXLAN tren s2

```bash
ovs-vsctl add-port s2 vxlan2 \
  -- set interface vxlan2 \
     type=vxlan \
     options:remote_ip=192.168.1.1 \
     options:key=100 \
     options:dst_port=4789
```

> **Luu y quan trong**: Ten port phai khac nhau (`vxlan1` va `vxlan2`) vi ca 2 switch dung chung 1 OVS instance (cung ovsdb). Ten interface phai la duy nhat trong toan bo he thong OVS.

### Buoc 4 — Xac nhan cau hinh trong CLI

```bash
mininet> sh ovs-vsctl show
mininet> sh ovs-vsctl list interface vxlan1
mininet> sh ovs-vsctl list interface vxlan2
```

---

## 5. Ket Qua Thuc Te

### 5.1 Cau truc OVS sau khi cau hinh

```
Bridge s1
    fail_mode: standalone
    Port vxlan1
        Interface vxlan1
            type: vxlan
            options: {dst_port="4789", key="100", remote_ip="192.168.1.2"}
    Port s1-eth1
    Port s1-eth2
    Port s1
        type: internal

Bridge s2
    fail_mode: standalone
    Port vxlan2
        Interface vxlan2
            type: vxlan
            options: {dst_port="4789", key="100", remote_ip="192.168.1.1"}
    Port s2-eth1
    Port s2-eth2
    Port s2
        type: internal

ovs_version: "3.3.4"
```

### 5.2 Chi tiet vxlan1 (s1)

```
name              : vxlan1
type              : vxlan
admin_state       : up
link_state        : up
options           : {dst_port="4789", key="100", remote_ip="192.168.1.2"}
status            : {tunnel_egress_iface=s2, tunnel_egress_iface_carrier=up}
statistics        : {rx_bytes=612849511, rx_packets=4313821,
                     tx_bytes=612875786, tx_packets=4314020}
```

### 5.3 Chi tiet vxlan2 (s2)

```
name              : vxlan2
type              : vxlan
admin_state       : up
link_state        : up
options           : {dst_port="4789", key="100", remote_ip="192.168.1.1"}
status            : {tunnel_egress_iface=s1, tunnel_egress_iface_carrier=up}
statistics        : {rx_bytes=825750150, rx_packets=5863226,
                     tx_bytes=825691157, tx_packets=5862834}
```

---

## 6. Phan Tich

| Tieu chi | Ket qua | Y nghia |
|---------|---------|---------|
| vxlan1 admin_state | up | Port duoc kich hoat |
| vxlan1 link_state | up | Tunnel dang hoat dong |
| tunnel_egress_iface=s2 | OK | Traffic tu s1 di ra dung interface underlay |
| vxlan2 admin_state | up | Port duoc kich hoat |
| vxlan2 link_state | up | Tunnel dang hoat dong |
| tunnel_egress_iface=s1 | OK | Traffic tu s2 di ra dung interface underlay |
| Statistics co gia tri | OK | Ca 2 chieu deu co traffic thuc su |

---

## 7. Loi Gap Va Cach Xu Ly

| Loi | Nguyen nhan | Cach xu ly |
|-----|------------|-----------|
| s2 khong co vxlan port | Ca s1 va s2 dung chung ovsdb, ten interface `vxlan1` bi trung | Dat ten khac nhau: `vxlan1` cho s1, `vxlan2` cho s2 |

---

## 8. Ket Luan

Module 3 hoan thanh thanh cong. VXLAN tunnel da duoc thiet lap:
- **vxlan1** tren s1: tunnel toi 192.168.1.2 (s2), VNI=100
- **vxlan2** tren s2: tunnel toi 192.168.1.1 (s1), VNI=100
- Ca 2 tunnel deu co trang thai `up`, `carrier=up`, va co traffic thuc su

**San sang cho Module 4: Kiem tra L2 Overlay va bat goi tin VXLAN.**

---

*Ngay thuc hien: 30/03/2026*
