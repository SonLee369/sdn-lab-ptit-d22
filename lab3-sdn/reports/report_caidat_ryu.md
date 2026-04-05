# Báo Cáo: Cài Đặt và Sửa Lỗi Ryu Controller

## 1. Thông Tin Môi Trường

| Thành phần | Phiên bản |
|---|---|
| Hệ điều hành | Ubuntu 24.04 (VM) |
| Python | 3.12.3 |
| Ryu | 4.34 |
| eventlet (ban đầu) | 0.31.1 |
| eventlet (sau sửa lỗi) | 0.35.2 |

---

## 2. Quá Trình Cài Đặt

### Bước 1 — Cài các thư viện phụ thuộc

```bash
sudo apt install -y python3 python3-pip python3-dev \
    libffi-dev libssl-dev gcc
```

**Kết quả:** Tất cả các gói đã được cài sẵn, không cần cài mới.

```
python3 is already the newest version (3.12.3-0ubuntu2.1)
python3-pip is already the newest version (24.0+dfsg-1ubuntu1.3)
...
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
```

### Bước 2 — Cài Ryu qua pip3

```bash
pip3 install ryu
```

**Kết quả:** Ryu 4.34 được cài thành công vào `~/.local/lib/python3.12/site-packages/`

```
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: ryu in ./.local/lib/python3.12/site-packages (4.34)
Requirement already satisfied: eventlet==0.31.1 ...
```

> **Lưu ý:** Pip cài vào thư mục người dùng (`~/.local/`) thay vì thư mục hệ thống vì không chạy với `sudo`.

---

## 3. Lỗi Phát Sinh và Cách Xử Lý

### Lỗi 1 — `ryu-manager: command not found`

#### Mô tả
Sau khi cài Ryu thành công, lệnh `ryu-manager --version` trả về lỗi:
```
ryu-manager: command not found
```

#### Nguyên nhân
Script `ryu-manager` được cài vào `~/.local/bin/` nhưng thư mục này **chưa có trong biến `PATH`** của hệ thống. Đây là hành vi mặc định khi `pip3` chạy ở chế độ **user installation**.

```
~/.local/bin/ryu-manager   ← File tồn tại
PATH = /usr/bin:/usr/local/bin/...  ← Thiếu ~/.local/bin
```

#### Cách sửa
```bash
export PATH=$PATH:~/.local/bin
```

Để lưu vĩnh viễn:
```bash
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

---

### Lỗi 2 — `TypeError: cannot set 'is_timeout' attribute of immutable type 'TimeoutError'`

#### Mô tả
Sau khi thêm PATH, chạy `ryu-manager --version` vẫn lỗi:

```
Traceback (most recent call last):
  File "/home/son/.local/bin/ryu-manager", line 5, in <module>
    from ryu.cmd.manager import main
  File ".../ryu/lib/hub.py", line 30, in <module>
    import eventlet
  File ".../eventlet/__init__.py", line 17, in <module>
    from eventlet import convenience
  ...
  File ".../eventlet/greenio/base.py", line 32, in <module>
    socket_timeout = eventlet.timeout.wrap_is_timeout(socket.timeout)
TypeError: cannot set 'is_timeout' attribute of immutable type 'TimeoutError'
```

#### Phân Tích Nguyên Nhân

Đây là lỗi **xung đột phiên bản** giữa Python 3.12 và eventlet 0.31.1:

```
Python 3.12
  └─ TimeoutError trở thành IMMUTABLE
       (không cho phép gán thuộc tính từ bên ngoài)

eventlet 0.31.1
  └─ wrap_is_timeout() cố gán:
       base.is_timeout = property(lambda _: True)
       vào TimeoutError  →  TypeError !!!
```

**Luồng lỗi chi tiết:**

```
ryu-manager
  → import ryu.cmd.manager
    → import ryu.lib.hub
      → import eventlet
        → import eventlet.convenience
          → import eventlet.green.socket
            → import eventlet.greenio
              → import eventlet.greenio.base
                → wrap_is_timeout(socket.timeout)
                  → TypeError  ← CRASH tại đây
```

#### Cách Sửa

Nâng cấp eventlet lên phiên bản đã vá lỗi tương thích với Python 3.12:

```bash
pip3 install --force-reinstall 'eventlet==0.35.2'
```

**Giải thích tham số:**
- `--force-reinstall`: Gỡ eventlet 0.31.1 và cài đè eventlet 0.35.2, bỏ qua ràng buộc phiên bản của Ryu

**Xác nhận phiên bản mới:**
```bash
pip3 show eventlet | grep Version
# Version: 0.35.2
```

---

## 4. Xác Nhận Cài Đặt Thành Công

### Kiểm tra phiên bản
```bash
ryu-manager --version
# ryu-manager 4.34
```

### Chạy thử với app mẫu
```bash
ryu-manager ryu.app.simple_switch_13
```

**Kết quả mong đợi:**
```
loading app ryu.app.simple_switch_13
loading app ryu.controller.ofp_handler
instantiating app ryu.app.simple_switch_13 of SimpleSwitch13
creating context wsgi
...
```
> Ryu lắng nghe tại **TCP port 6633** — sẵn sàng nhận kết nối từ Mininet.

---

## 5. Tổng Hợp Quá Trình

```
Bước 1: pip3 install ryu
         └─ Ryu 4.34 cài thành công
         └─ eventlet 0.31.1 được cài theo (phụ thuộc)

Bước 2: ryu-manager --version
         └─ LỖI 1: command not found
         └─ Nguyên nhân: ~/.local/bin chưa trong PATH
         └─ Sửa: export PATH=$PATH:~/.local/bin

Bước 3: ryu-manager --version (lần 2)
         └─ LỖI 2: TypeError immutable TimeoutError
         └─ Nguyên nhân: eventlet 0.31.1 không tương thích Python 3.12
         └─ Sửa: pip3 install --force-reinstall eventlet==0.35.2

Bước 4: ryu-manager --version (lần 3)
         └─ THÀNH CÔNG: ryu-manager 4.34
```

---

## 6. Bảng Tóm Tắt Lỗi

| # | Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|---|
| 1 | `command not found` | `~/.local/bin` chưa trong PATH | `export PATH=$PATH:~/.local/bin` |
| 2 | `TypeError: immutable type 'TimeoutError'` | eventlet 0.31.1 không tương thích Python 3.12 | `pip3 install --force-reinstall eventlet==0.35.2` |

---

## 7. Lưu Ý Cho Lần Cài Đặt Sau

1. **Thêm PATH ngay khi cài xong:** Thêm `~/.local/bin` vào `.bashrc` để tránh lỗi 1
2. **Python 3.12+ cần eventlet >= 0.33.3:** Luôn nâng cấp eventlet sau khi cài Ryu
3. **Không cần cài lại Ryu:** Chỉ cần thay eventlet, Ryu 4.34 vẫn hoạt động tốt với eventlet 0.35.2

```bash
# Script cài đặt hoàn chỉnh (tránh cả 2 lỗi)
pip3 install ryu
pip3 install --force-reinstall 'eventlet==0.35.2'
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
ryu-manager --version
```

---

*Báo cáo cài đặt Ryu Controller — Dự án "Tạo mạng SDN trên Mininet"*
