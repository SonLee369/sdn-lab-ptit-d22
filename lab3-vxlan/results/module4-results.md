mininet> sh bash vxlan_setup.sh

============================================================
Lab 3 — Cấu hình VXLAN thủ công trên OVS
============================================================

> > > BƯỚC 1: Kiểm tra điều kiện tiên quyết
> > > [OK] ovs-vsctl tìm thấy: ovs-vsctl (Open vSwitch) 3.3.4
> > > [OK] OVS daemon đang hoạt động
> > > [OK] Bridge 's1' tồn tại
> > > [OK] Bridge 's2' tồn tại

> > > BƯỚC 2: Gán địa chỉ IP underlay cho VTEP
> > > [OK] s1 VTEP IP: 10.0.0.1/24
> > > [OK] s2 VTEP IP: 10.0.0.2/24

> > > BƯỚC 3: Kiểm tra kết nối underlay (s1 ping s2)
> > > [WARN] Ping underlay thất bại — kiểm tra lại IP bridge và liên kết s1-s2
> > > PING 10.0.0.2 (10.0.0.2) from 10.0.0.1 s1: 56(84) bytes of data.

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss, time 2035ms
pipe 3

> > > BƯỚC 4: Dọn dẹp VXLAN port cũ (nếu có)
> > > [WARN] Đã xóa port 'vxlan0' cũ trên s1
> > > [OK] Không có port 'vxlan0' cũ trên s2

> > > BƯỚC 5: Thêm VXLAN tunnel port vào s1
> > > [OK] VXLAN port 'vxlan0' đã thêm vào s1

          local_ip  = 10.0.0.1
          remote_ip = 10.0.0.2
          VNI (key) = 100
          dst_port  = 4789

> > > BƯỚC 6: Thêm VXLAN tunnel port vào s2
> > > ovs-vsctl: cannot create a port named vxlan0 because a port named vxlan0 already exists on bridge s1
> > > [ERROR] Thêm VXLAN port vào s2 thất bại
> > > mininet>
