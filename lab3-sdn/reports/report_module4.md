# Báo Cáo Module 4: Đo Hiệu Năng Mạng SDN

## 1. Mục Tiêu

Module 4 đo lường và đánh giá hiệu năng thực tế của mạng SDN thông qua các chỉ số:

- **Băng thông** (Bandwidth) — TCP và UDP
- **Độ trễ** (Latency) — RTT min/avg/max
- **Jitter** — độ biến động trễ (UDP)
- **Packet loss** — tỷ lệ mất gói
- **Khả năng đa luồng** — TCP multi-stream

---

## 2. Môi Trường Thực Nghiệm

| Thành phần | Giá trị |
|---|---|
| Công cụ đo | iperf3, ping |
| Topology | Star — h1–h4 qua switch s1 |
| Băng thông link | 10 Mbps (giới hạn TCLink) |
| Độ trễ link | 5ms mỗi chiều |
| Giao thức điều khiển | OpenFlow 1.3 |
| Flow rules | Đã học sẵn sau `pingall` |

---

## 3. Kết Quả Thực Nghiệm

### 3.1 Thử Nghiệm 1 — Băng Thông TCP (h1 → h4)

**Lệnh:**
```
h4 iperf3 -s -D
h1 iperf3 -c 10.0.0.4 -t 10 -i 1
```

**Kết quả theo giây:**

| Giây | Transfer | Bitrate | Retr | Cwnd |
|---|---|---|---|---|
| 0–1 | 1.75 MB | 14.7 Mbps | 0 | 175 KB |
| 1–2 | 1.62 MB | 13.6 Mbps | 0 | 235 KB |
| 2–3 | 1.12 MB | 9.43 Mbps | 0 | 293 KB |
| 3–4 | 1.25 MB | 10.5 Mbps | 0 | 351 KB |
| 4–5 | 1.62 MB | 13.6 Mbps | 0 | 409 KB |
| 5–6 | 1.75 MB | 14.7 Mbps | 0 | 468 KB |
| 6–7 | 1.00 MB | 8.38 Mbps | 0 | 526 KB |
| 7–8 | 1.12 MB | 9.44 Mbps | 0 | 584 KB |
| 8–9 | 2.38 MB | 19.9 Mbps | 0 | 643 KB |
| 9–10 | 1.38 MB | 11.5 Mbps | 0 | 701 KB |

**Tổng kết:**
```
Sender   : 15.0 MB — 12.6 Mbits/sec — Retransmits: 0
Receiver : 12.0 MB —  9.49 Mbits/sec
```

**Phân tích:**
- **Receiver đạt 9.49 Mbps** — xấp xỉ giới hạn link 10 Mbps (hiệu suất ~95%)
- **Sender báo 12.6 Mbps** — do TCP congestion window tăng dần (175→701 KB), sender gửi nhanh hơn link có thể xử lý; phần dư được buffer tại switch
- **Retransmits = 0** — không có gói nào phải gửi lại, kết nối ổn định hoàn toàn
- **Cwnd tăng tuyến tính** — TCP Slow Start → Congestion Avoidance hoạt động bình thường

---

### 3.2 Thử Nghiệm 2 — Băng Thông UDP (h1 → h4)

**Lệnh:**
```
h4 iperf3 -s -D
h1 iperf3 -c 10.0.0.4 -u -b 9M -t 10 -i 1
```

**Kết quả theo giây:**

| Giây | Transfer | Bitrate | Datagrams |
|---|---|---|---|
| 0–1 | 1.07 MB | 9.00 Mbps | 777 |
| 1–2 | 1.07 MB | 9.00 Mbps | 777 |
| 2–3 | 1.07 MB | 9.00 Mbps | 777 |
| 3–4 | 1.07 MB | 9.00 Mbps | 777 |
| 4–5 | 1.07 MB | 9.00 Mbps | 777 |
| 5–6 | 1.07 MB | 9.00 Mbps | 777 |
| 6–7 | 1.07 MB | 9.00 Mbps | 777 |
| 7–8 | 1.07 MB | 8.99 Mbps | 776 |
| 8–9 | 1.07 MB | 9.00 Mbps | 777 |
| 9–10 | 1.07 MB | 8.99 Mbps | 777 |

**Tổng kết:**
```
Sender   : 10.7 MB — 9.00 Mbps — Jitter: 0.000ms — Lost: 0/7769 (0%)
Receiver : 10.7 MB — 8.98 Mbps — Jitter: 0.352ms — Lost: 0/7769 (0%)
```

**Phân tích:**
- **Bandwidth cực kỳ ổn định**: 9.00 Mbps đều tất cả 10 giây — không biến động
- **Jitter chỉ 0.352ms** — độ biến động trễ rất thấp, chấp nhận được cho VoIP (< 30ms)
- **Packet loss = 0%** — không mất gói nào trong 7769 datagram
- UDP không có cơ chế kiểm soát tắc nghẽn → băng thông ổn định hơn TCP
- Kết quả lý tưởng cho các ứng dụng real-time (VoIP, video streaming)

---

### 3.3 Thử Nghiệm 3 — TCP Đa Luồng / Multi-stream (h1 → h4, 4 luồng)

**Lệnh:**
```
h4 iperf3 -s -D
h1 iperf3 -c 10.0.0.4 -t 10 -P 4
```

> **Lưu ý:** `-p` (chữ thường) là port number, `-P` (chữ hoa) mới là số luồng song song.

**Kết quả từng luồng:**

| Stream | Sender | Receiver |
|---|---|---|
| [5] | 5.38 MB — 4.51 Mbps | 3.38 MB — 2.45 Mbps |
| [7] | 5.50 MB — 4.61 Mbps | 3.38 MB — 2.45 Mbps |
| [9] | 4.75 MB — 3.98 Mbps | 3.12 MB — 2.27 Mbps |
| [11] | 4.62 MB — 3.88 Mbps | 3.00 MB — 2.18 Mbps |

**Tổng kết [SUM]:**
```
Sender   : 20.2 MB — 17.0 Mbits/sec — Retransmits: 0
Receiver : 12.9 MB —  9.35 Mbits/sec
```

**Phân tích:**
- **Receiver [SUM] = 9.35 Mbps** — xấp xỉ đúng giới hạn link 10 Mbps dù có 4 luồng
- **Sender [SUM] = 17.0 Mbps** — tổng cửa sổ TCP của 4 luồng vượt link capacity; switch buffer gói dư
- **4 luồng chia sẻ công bằng**: mỗi luồng nhận ~2.3 Mbps (9.35/4) — TCP Fair Queuing hoạt động đúng
- **Retransmits = 0** — không mất gói dù 4 luồng cạnh tranh
- Kết quả chứng minh switch OVS xử lý đa luồng hiệu quả với flow rules SDN

**Băng thông theo giây [SUM]:**

| Giây | [SUM] Bitrate |
|---|---|
| 0–1 | 17.8 Mbps |
| 1–2 | 11.5 Mbps |
| 2–3 | 10.5 Mbps |
| 3–4 | 14.7 Mbps |
| 4–5 | 8.38 Mbps |
| 5–6 | 14.7 Mbps |
| 6–7 | 15.7 Mbps |
| 7–8 | 25.2 Mbps |
| 8–9 | 23.1 Mbps |
| 9–10 | 28.2 Mbps |

> Biến động cao do 4 luồng TCP cạnh tranh băng thông và điều chỉnh cửa sổ độc lập.

---

### 3.4 Thử Nghiệm 4 — Độ Trễ Chi Tiết (h1 → h4, 20 gói)

**Lệnh:**
```
h1 ping h4 -c 20 -i 0.5
```

**Kết quả từng gói (ms):**

| Seq | RTT (ms) | | Seq | RTT (ms) |
|---|---|---|---|---|
| 1 | 24.5 | | 11 | 22.7 |
| 2 | 22.3 | | 12 | 21.9 |
| 3 | 23.1 | | 13 | 22.0 |
| 4 | 22.8 | | 14 | 21.9 |
| 5 | 22.7 | | 15 | 22.6 |
| 6 | 21.9 | | 16 | 21.3 |
| 7 | 21.9 | | 17 | 21.7 |
| 8 | 22.8 | | 18 | 20.8 |
| 9 | 22.1 | | 19 | 21.7 |
| 10 | 22.3 | | 20 | 22.2 |

**Tổng kết:**
```
20 packets transmitted, 20 received, 0% packet loss, time 9529ms
rtt min/avg/max/mdev = 20.757/22.251/24.469/0.738 ms
```

**Phân tích:**
- **Packet loss = 0%** — kết nối hoàn toàn ổn định
- **RTT avg = 22.251ms** bao gồm: 2× link delay (10ms) + xử lý switch + overhead VM
- **mdev = 0.738ms** — jitter thấp, mạng ổn định
- Gói seq=1 có RTT cao nhất (24.5ms) — do ARP resolution lần đầu
- Từ seq=2 trở đi ổn định hơn — flow rule đã được cài sẵn

---

### 3.5 Thử Nghiệm 5 — Băng Thông TCP Ngược (h4 → h1)

**Lệnh:**
```
h1 iperf3 -s -D
h4 iperf3 -c 10.0.0.1 -t 10 -i 1
```

**Tổng kết:**
```
Sender   : 15.0 MB — 12.6 Mbits/sec — Retransmits: 0
Receiver : 12.0 MB —  9.49 Mbits/sec
```

**Phân tích:**
- Kết quả **hoàn toàn đối xứng** với thử nghiệm 1 (h1→h4)
- Chứng minh flow rules được cài **2 chiều** độc lập và cân bằng
- Switch s1 xử lý cả 2 chiều với hiệu năng như nhau — đúng thiết kế SDN

---

## 4. Lỗi Phát Sinh

### Lỗi — Gõ sai lệnh iperf

| Lệnh sai | Lỗi | Lệnh đúng |
|---|---|---|
| `h1 iperf4 -c 10.0.0.4` | `bash: iperf4: command not found` | `h1 iperf3 -c 10.0.0.4` |
| `h1 iperf3 -c 10.0.0.4 -t 10 -p 4` | `Connection refused` (kết nối sai port) | `h1 iperf3 -c 10.0.0.4 -t 10 -P 4` |

> **Lưu ý:** `-p` (thường) = chỉ định port number; `-P` (hoa) = số luồng song song.

---

## 5. Tổng Hợp Kết Quả

| Thử nghiệm | Chỉ số | Kết quả | Đánh giá |
|---|---|---|---|
| TCP h1→h4 | Bandwidth receiver | **9.49 Mbps** | Đạt 95% link capacity |
| TCP h1→h4 | Retransmits | **0** | Không mất gói |
| UDP h1→h4 | Bandwidth | **9.00 Mbps** | Ổn định hoàn toàn |
| UDP h1→h4 | Jitter | **0.352 ms** | Rất thấp |
| UDP h1→h4 | Packet loss | **0% (0/7769)** | Xuất sắc |
| TCP 4 luồng | Bandwidth [SUM] receiver | **9.35 Mbps** | Đúng giới hạn link |
| TCP 4 luồng | Fair share / luồng | **~2.34 Mbps** | Phân chia công bằng |
| Ping 20 gói | RTT avg | **22.251 ms** | Ổn định |
| Ping 20 gói | mdev (jitter) | **0.738 ms** | Rất thấp |
| Ping 20 gói | Packet loss | **0%** | Xuất sắc |
| TCP h4→h1 | Bandwidth receiver | **9.49 Mbps** | Đối xứng hoàn toàn |

---

## 6. Phân Tích Tổng Quan

### 6.1 Hiệu Suất Sử Dụng Băng Thông

```
Giới hạn link      : 10.00 Mbps (100%)
TCP đơn luồng      :  9.49 Mbps ( 95%)  ← Hiệu quả cao
UDP đơn luồng      :  9.00 Mbps ( 90%)  ← Ổn định tuyệt đối
TCP 4 luồng [SUM]  :  9.35 Mbps ( 94%)  ← Đa luồng chia sẻ tốt
```

### 6.2 So Sánh TCP vs UDP

| Tiêu chí | TCP | UDP |
|---|---|---|
| Băng thông thực tế | 9.49 Mbps | 9.00 Mbps |
| Tính ổn định | Có biến động | Rất ổn định |
| Jitter | N/A | 0.352 ms |
| Packet loss | 0% | 0% |
| Phù hợp cho | File transfer, web | VoIP, video stream |

### 6.3 Đánh Giá Chất Lượng Mạng SDN

```
Tiêu chí               Kết quả        Ngưỡng chấp nhận   Đánh giá
──────────────────────────────────────────────────────────────────
Băng thông TCP         9.49 Mbps      > 8 Mbps            ✓ Đạt
Jitter UDP             0.352 ms       < 30 ms (VoIP)      ✓ Xuất sắc
Packet loss            0%             < 1%                ✓ Xuất sắc
RTT avg                22.251 ms      < 100 ms            ✓ Tốt
RTT mdev               0.738 ms       < 5 ms              ✓ Xuất sắc
```

---

## 7. Kết Luận Module 4

Mạng SDN được xây dựng trong dự án đạt hiệu năng tốt:

- **Băng thông TCP** đạt **95% link capacity** với 0 retransmit — switch SDN chuyển tiếp gói tin hiệu quả theo flow rules
- **UDP** hoàn toàn ổn định, jitter cực thấp (0.352ms) — phù hợp ứng dụng real-time
- **Đa luồng** chia sẻ băng thông công bằng, tổng throughput không vượt giới hạn vật lý
- **Độ trễ** ổn định ở 22ms (bao gồm 2×5ms link delay theo thiết kế)
- **Tính đối xứng** — hiệu năng 2 chiều h1↔h4 hoàn toàn bằng nhau

> **Kết luận:** Controller Ryu với OpenFlow 1.3 điều khiển switch OVS hiệu quả, đảm bảo chuyển tiếp gói tin theo flow rules với hiệu suất gần tối đa của đường truyền.

---

*Module 4 hoàn thành — Tiếp theo: Module 5 — Báo cáo tổng hợp*
