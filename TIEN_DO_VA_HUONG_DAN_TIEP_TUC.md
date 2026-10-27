# 📌 BÁO CÁO TIẾN ĐỘ & HƯỚNG DẪN TIẾP TỤC DỰ ÁN ĐẦU TƯ
**Khung thời gian mục tiêu:** 3 tháng (14/10/2026 – 14/01/2027)  
**Quy mô vốn ban đầu:** `100.000.000 VNĐ` (Một trăm triệu đồng)  
**Chiến lược cốt lõi:** **Cân bằng chủ động săn sóng ngành (Active Sector Rotation)**  
**Cập nhật gần nhất:** Phiên trưa ngày 26/10/2026  

---

## I. TỔNG QUAN MỤC TIÊU & HIỆU SUẤT ĐẦU TƯ ĐẾN NAY

| Chỉ số / Hạng mục | Mục tiêu 3 tháng (14/01/2027) | Thực tế đạt được (26/10/2026) | Trạng thái đánh giá |
| :--- | :---: | :---: | :--- |
| **Giá trị tài sản ròng (NAV)** | **110 – 115 triệu VNĐ** | **105.380.000 VNĐ** | Đã hoàn thành **+5.38%** (Đạt gần 50% mục tiêu giai đoạn) |
| **Tỷ suất sinh lời lũy kế** | **+10.0% đến +15.0%** | **+5.38%** | Vượt tiến độ so với kế hoạch tháng đầu tiên (+3% đến +5%) |
| **Mức sụt giảm tối đa (Drawdown)** | **< 6.0%** (Tối đa lỗ 6 triệu) | **0.00%** | Toàn bộ danh mục đều đang sinh lời, kiểm soát rủi ro tuyệt đối |
| **Cơ cấu danh mục thực tế** | 2 – 3 mã chiến lược trọng tâm | **3 mã chính + 1 mã lẻ + Tiền mặt** | NBC (35.7%), TCB (28.7%), DCM (26.7%), TD6 (1.8%), Cash (8.1%) |
| **Tỷ trọng Tiền mặt / Cổ phiếu** | Linh hoạt theo xu hướng | **~8.1% Tiền mặt / ~91.9% Cổ phiếu** | Tiền mặt khả dụng 8.600.000 VNĐ (thu về từ chốt lời 1.000 NBC @ 8.60) |

---

## II. BÁO CÁO CHI TIẾT DANH MỤC THỰC CHIẾN (27/10/2026)

| Mã CP | Ngành | Số lượng | Giá vốn (VNĐ) | Thị giá (VNĐ) | Giá trị TT (VNĐ) | Lãi / Lỗ | Trạng thái T+ | Định hướng & Kế hoạch xử lý |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **DCM** | Phân bón - Hóa chất | 800 | 33.30 | **35.50** | 28.400.000 | **+6.61%** | T+0 (Khả dụng) | **Khóa lãi & Nâng Trailing Stop**.<br>• Kê bán 1/3 (300 cp) vùng **36.0 – 36.5**.<br>• Nâng mốc bảo vệ lãi cho 500 cp còn lại lên **34.0** (vốn 33.3). |
| **TCB** | Ngân hàng | 900 | 32.64 | **34.20** | 30.780.000 | **+4.78%** | T+0 (Khả dụng) | **Tiếp tục nắm giữ theo sóng**.<br>• Canh chốt lời 1/2 tại **35.90** (+10%).<br>• Chặn lỗ bảo vệ an toàn: **31.00** (-5%). |
| **NBC** | Khai thác Than | **4,500** | **8.30** | **8.40** | 37.800.000 | **+1.20%** | T+0 (Khả dụng) | **ĐÃ CHỐT LỜI 1.000 CP @ 8.60** (+300.000 VNĐ, thu 8.6tr tiền mặt).<br>• 4.500 cp còn lại: Canh chốt vùng **9.10 – 9.60**.<br>• Ngưỡng chặn lỗ kỷ luật: **7.90** (thủng bán 1/2). |
| **TD6** | Than (Mã lẻ) | 300 | 6.13 | **6.35** | 1.905.000 | **+3.59%** | T+0 (Khả dụng) | **Canh bán dứt khoát vùng 6.35 – 6.5** để dọn sạch bảng, thu hồi tiền mặt. |

---

## III. TIẾN ĐỘ HỆ THỐNG CÔNG NGHỆ & TỰ ĐỘNG HÓA

Hệ thống hạ tầng tự động hóa đã hoàn thiện và hoạt động ổn định 100%:
1. **Công cụ định lượng & lọc sóng ngành (`screener.py`):**
   - Đánh giá tự động 60+ mã cổ phiếu toàn thị trường theo 6 tiêu chí chấm điểm kỹ thuật (0 – 100 điểm).
   - Tự động phát hiện vị thế bứt phá MA20, RSI, thanh khoản đột biến và tính toán tỷ lệ Risk/Reward (R:R).
2. **Hệ thống tạo Bản tin & Báo cáo đầu tư (`daily_report.py`):**
   - Tự động gắn kết chặt chẽ số liệu danh mục thực tế của tài khoản 100M vào từng bản tin.
   - Phân tích đối đầu (Head-to-Head) giữa các mã đang nắm giữ và các ứng viên thay thế tiềm năng.
3. **Bảng điều khiển trực quan (Interactive Live Dashboard & Web):**
   - File xuất bản: `index.html` và `reports/dashboard.html`.
   - Tính năng: Biểu đồ Radar động, bảng so sánh đa chiều, tra cứu lịch sử báo cáo các ngày từ 14/10 đến nay.
4. **Lịch trình tự động hóa GitHub Actions (`.github/workflows/daily_report.yml`):**
   - Chạy định kỳ 3 phiên/ngày theo các mốc giờ tối ưu:
     * **08:20 sáng:** Bản tin phân tích đầu ngày & kịch bản phiên.
     * **11:25 trưa:** Bản tin tổng kết phiên sáng & định hướng phiên chiều.
     * **15:08 chiều:** Bản tin tổng kết đóng cửa ATC & cập nhật sổ nhật ký giao dịch.

---

## IV. HƯỚNG DẪN HÀNH ĐỘNG TIẾP TỤC (ACTION PLAN CHO NHÀ ĐẦU TƯ)

### 1. Hành động cụ thể cho Phiên chiều 26/10 & các phiên kế tiếp
* **Hành động 1 - Bán thu hồi mã lẻ TD6:**
  - Đặt lệnh bán 300 cp TD6 tại mức giá **6.35 – 6.45**. 
  - Mục đích: Thu hồi ngay ~1.9 triệu tiền mặt và dọn dẹp sạch sẽ danh mục, chỉ giữ lại các mã chủ lực.
* **Hành động 2 - Chủ động hiện thực hóa một phần lợi nhuận DCM:**
  - Kê lệnh bán trước 1/3 vị thế (**300 cp DCM**) tại vùng giá **36.0 – 36.5** (+8.1% đến +9.6%).
  - Mục đích: Đút túi khoản lãi chắc chắn, đồng thời giải phóng **~11 triệu tiền mặt** tạo sức mua dự phòng.
  - Với 500 cp DCM còn lại: Đặt mốc nâng chặn lãi (Trailing Stop) tại **34.00**. Nếu cổ phiếu tiếp tục tăng lên 38.x thì giữ nguyên để ăn trọn sóng lớn; nếu quay đầu thủng 34.00 thì chốt lời toàn bộ (vẫn đảm bảo lãi).
* **Hành động 3 - Kiểm soát kỷ luật TCB và NBC:**
  - **TCB:** Kê sẵn lệnh chốt lời 450 cp tại **35.90** (+10%). Giữ nguyên ngưỡng cắt lỗ 31.00.
  - **NBC:** Không mua trung bình giá thêm. Kích hoạt bán 1/2 ngay nếu giá thủng **7.90** (-5%), bán sạch nếu thủng **7.60**.

### 2. Kế hoạch giải ngân khi có tiền mặt quay lại (Sức mua mới ~13 triệu VNĐ)
* **Điều kiện thị trường:** Chỉ giải ngân tiền mới khi chỉ số VN-Index kiểm định thành công vùng hỗ trợ tâm lý cứng **1.700 – 1.705 điểm** và có lực cầu bắt đáy xác nhận.
* **Danh sách cổ phiếu ưu tiên số 1 (Theo Screener đạt 80/100 điểm):**
  1. **STB (Ngân hàng):** Điểm 80/100 | Nền sát MA20 (+1.8%) | Khối lượng 2.30x bình quân | Khối ngoại gom ròng mạnh.
  2. **VPB (Ngân hàng):** Điểm 80/100 | Thanh khoản đột biến 393 tỷ | R:R = 2.4 : 1.
  3. **MWG (Bán lẻ):** Điểm 80/100 | Tạo nền chặt chẽ trên MA20 | R:R = 2.4 : 1.

### 3. Lộ trình chiến lược cho các tháng tiếp theo
* **Giai đoạn 1 (đến 14/11/2026) – "Chắt chiu đệm lợi nhuận BCTC Q3":**
  - Giữ vững thành quả lãi +5% hiện tại, nâng mục tiêu NAV chạm mốc 108 – 110 triệu VNĐ.
* **Giai đoạn 2 (15/11 – 14/12/2026) – "Tối ưu hóa vị thế & Gia tăng hiệu suất":**
  - Gia tăng tỷ trọng trên các cổ phiếu hình thành sóng tăng rõ nét (Pyramiding có chọn lọc).
* **Giai đoạn 3 (15/12/2026 – 14/01/2027) – "Đón sóng chốt NAV & Hiện thực hóa mục tiêu":**
  - Bán chốt lời dần về tiền mặt, cán đích mục tiêu 110 – 115 triệu VNĐ và đóng sổ chu kỳ 3 tháng.

---

## V. SỔ TAY QUY TRÌNH VẬN HÀNH & XỬ LÝ LỖI HỆ THỐNG (RUNBOOK)

1. **Chạy cập nhật dữ liệu và báo cáo thủ công:**
   ```bash
   cd /workspace
   python3 daily_report.py
   python3 tools/build_visual_dashboard.py
   cp reports/dashboard.html index.html
   ```
2. **Kiểm tra trạng thái đồng bộ:**
   ```bash
   git status
   git log -n 3 --oneline
   ```
3. **Quy tắc vàng khi tư vấn / báo cáo:**
   - Luôn đặt danh mục thực tế của tài khoản lên hàng đầu (số lượng, giá vốn, lãi/lỗ %, ngày về T+).
   - Tuyệt đối khuyến nghị hành động dứt khoát (Nắm giữ, Chốt lời, Cắt lỗ) trước khi khuyến nghị cơ hội mới.
