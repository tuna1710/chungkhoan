# 📈 HỆ THỐNG TRỢ LÝ ĐẦU TƯ CHỨNG KHOÁN VIỆT NAM (VIETNAM STOCK ASSISTANT)

> **Mục tiêu chiến lược:** Cân bằng chủ động săn sóng ngành (Active Sector Rotation)  
> **Quy mô vốn thử nghiệm:** 100.000.000 VNĐ | **Kỳ vọng 3 tháng:** +10% đến +15% (NAV: 110 - 115 triệu VNĐ)  
> **Kỷ luật bảo vệ vốn:** Tuyệt đối không để sụt giảm quá 6% tổng NAV (Max Drawdown < 6%)

---

## 📑 MỤC LỤC
1. [Giới thiệu Hệ thống](#-giới-thiệu-hệ-thống)
2. [Cấu trúc Thư mục Dự án](#-cấu-trúc-thư-mục-dự-án)
3. [Hướng dẫn Cài đặt & Môi trường](#-hướng-dẫn-cài-đặt--môi-trường)
4. [Hướng dẫn Sử dụng Chi tiết Các Công cụ](#-hướng-dẫn-sử-dụng-chi-tiết-các-công-cụ)
   - [4.1. Bản tin Chiến lược Đầu ngày & Theo dõi Danh mục](#41-bản-tin-chiến-lược-đầu-ngày--theo-dõi-danh-mục-daily_reportpy)
   - [4.2. Bộ lọc Cổ phiếu Dẫn sóng](#42-bộ-lọc-cổ-phiếu-dẫn-sóng-screenerpy)
   - [4.3. Bảng điều khiển Trực quan](#43-bảng-điều-khiển-trực-quan-dashboardhtml)
   - [4.4. Nhật ký Giao dịch & Quản trị Vị thế](#44-nhật-ký-giao-dịch--quản-trị-vị-thế-journalnhat_ky_giao_dichmd)
5. [Tự động hóa với GitHub Actions](#-tự-động-hóa-với-github-actions)
6. [Kỷ luật Thép & Quản trị Rủi ro](#-kỷ-luật-thép--quản-trị-rủi-ro)

---

## 🌟 GIỚI THIỆU HỆ THỐNG

Hệ thống được thiết kế dành riêng cho Nhà đầu tư cá nhân trên thị trường chứng khoán Việt Nam (HOSE, HNX), giải quyết 3 bài toán lớn:
1. **Loại bỏ cảm xúc khi giao dịch:** Chấm điểm kỹ thuật khách quan từ 0 đến 100 điểm dựa trên VSA, Price Action, RSI và vị thế MA.
2. **Theo dõi danh mục sát sao hàng ngày:** Mọi báo cáo luôn ưu tiên theo dõi các mã đang nắm giữ thực tế (như DCM, TD6), cập nhật lãi/lỗ %, tình trạng T+ và cảnh báo điểm chặn lãi / cắt lỗ.
3. **Tự động hóa toàn diện:** Không cần mở máy tính, hệ thống tự động chạy lúc **08h30 sáng mỗi ngày giao dịch**, tạo báo cáo Markdown và đẩy trực tiếp lên nền tảng Web công khai (Rentry) để xem trên điện thoại.

---

## 📂 CẤU TRÚC THƯ MỤC DỰ ÁN

```bash
chungkhoan/
├── .github/
│   └── workflows/
│       └── daily_report.yml       # Cấu hình tự động hóa GitHub Actions chạy 8h30 sáng
├── data/
│   └── danh_muc_theo_doi.md       # Watchlist các nhóm ngành tiềm năng
├── journal/
│   └── nhat_ky_giao_dich.md       # Nhật ký lệnh thực tế, cân bằng NAV & tỷ lệ Cash/Stock
├── reports/
│   ├── ban_tin_sang_15_10_2026.md # Các bản tin chiến lược hàng ngày
│   ├── ket_qua_loc_co_phieu.md    # Kết quả xuất từ bộ lọc
│   └── dashboard.html             # Trang giao diện Dashboard phân tích đồ họa
├── tools/
│   ├── build_visual_dashboard.py  # Script tạo dashboard trực quan
│   ├── daily_morning_report.py    # Script phân tích và xuất bản báo cáo sáng
│   ├── publish_rentry.py          # Module PUSH báo cáo lên Web Rentry (không bị chặn 403)
│   └── screener.py                # Thuật toán quét dữ liệu và chấm điểm cổ phiếu
├── daily_report.py                # Lệnh chạy báo cáo sáng tại thư mục gốc
├── screener.py                    # Lệnh chạy bộ lọc cổ phiếu tại thư mục gốc
├── muctieu.md                     # Bản kế hoạch mục tiêu chi tiết 3 tháng
├── requirements.txt               # Thư viện phụ thuộc (requests)
├── .gitignore
└── README.md
```

---

## 💻 HƯỚNG DẪN CÀI ĐẶT & MÔI TRƯỜNG

### Yêu cầu:
* **Python:** Phiên bản 3.10 trở lên.
* **Hệ điều hành:** Linux, macOS, Windows đều được hỗ trợ.

### Các bước cài đặt:
1. Clone repo về máy:
   ```bash
   git clone https://github.com/tuna1710/chungkhoan.git
   cd chungkhoan
   ```
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ HƯỚNG DẪN SỬ DỤNG CHI TIẾT CÁC CÔNG CỤ

### 4.1. Bản tin Chiến lược Đầu ngày & Theo dõi Danh mục (`daily_report.py`)

Đây là công cụ quan trọng nhất được sử dụng vào **08h30 sáng mỗi ngày** trước khi phiên giao dịch mở cửa.

* **Cách chạy:**
  ```bash
  python3 daily_report.py
  ```
* **Nội dung công cụ thực hiện:**
  1. Quét dữ liệu 60+ cổ phiếu và đọc trạng thái tài khoản thực tế.
  2. **Theo dõi danh mục thực tế (Ưu tiên số 1):** Cập nhật giá vốn, thị giá hiện tại, lãi/lỗ %, tình trạng T+ và đưa ra khuyến nghị cụ thể cho từng mã (DCM, TD6, lệnh chờ TCB).
  3. Đánh giá vĩ mô đêm qua & nhận định kịch bản VN-Index.
  4. Lập bảng so sánh đối đầu trực diện giữa các mã cùng ngành (TCB vs MBB, DCM vs DGC, KBC vs IDC).
  5. **Tự động lưu báo cáo** tại `reports/ban_tin_sang_DD_MM_YYYY.md` và **in ra đường link Web Rentry.co** để click vào xem ngay trên điện thoại hoặc trình duyệt.

---

### 4.2. Bộ lọc Cổ phiếu Dẫn sóng (`screener.py`)

Công cụ sàng lọc cổ phiếu săn sóng ngành, chấm điểm sức mạnh giá và dòng tiền từ 0 - 100 điểm.

* **Lệnh 1: Quét toàn bộ thị trường & hiển thị Top 10 cổ phiếu xuất sắc nhất:**
  ```bash
  python3 screener.py
  ```
* **Lệnh 2: Quét Top 5 cổ phiếu và xuất báo cáo markdown:**
  ```bash
  python3 screener.py --top 5 --export
  ```
  *(Báo cáo chi tiết sẽ được tự động lưu tại `reports/ket_qua_loc_co_phieu.md`)*

* **Lệnh 3: Lọc riêng theo từng ngành trọng điểm:**
  ```bash
  python3 screener.py --sector "Ngân hàng"
  python3 screener.py --sector "BĐS Khu công nghiệp"
  python3 screener.py --sector "Hóa chất - Phân bón"
  python3 screener.py --sector "Thép - Kim loại"
  python3 screener.py --sector "Bán lẻ - Tiêu dùng"
  ```

* **Lệnh 4: Phân tích chuyên sâu 1 cổ phiếu cụ thể (Vùng mua, Cắt lỗ, Chốt lời, R:R):**
  ```bash
  python3 screener.py --symbol DCM
  python3 screener.py --symbol TCB
  python3 screener.py --symbol KBC
  ```
  *Bảng phân tích sẽ trả về đầy đủ:*
  * Điểm tổng hợp (0-100) & Khuyến nghị hành động.
  * Vùng giá gom mua an toàn sát nền hỗ trợ.
  * Mốc cắt lỗ nghiêm ngặt (-5%).
  * Giá chốt lời mục tiêu (+10% đến +15%).
  * Tỷ lệ Risk:Reward (chỉ chọn mã có R:R >= 2:1).

---

### 4.3. Bảng điều khiển Trực quan (`dashboard.html`)

Tạo giao diện đồ họa đẹp mắt hiển thị tổng thể thị trường:
```bash
python3 tools/build_visual_dashboard.py
```
Mở file `reports/dashboard.html` trên trình duyệt Chrome / Edge / Safari để xem:
* Biểu đồ Radar Chart 5 trục (Thanh khoản, Xu hướng MA, Dòng tiền lớn, Độ siết nền, Tỷ lệ R:R).
* Thẻ mua khuyến nghị Top 1 và Kế hoạch đi tiền chi tiết.

---

### 4.4. Nhật ký Giao dịch & Quản trị Vị thế (`journal/nhat_ky_giao_dich.md`)

File này lưu trữ tình trạng tài khoản và lịch sử giao dịch thực tế:
* **Thông số tài khoản:** Vốn ban đầu 100 triệu, NAV hiện tại, tỷ lệ Tiền mặt / Cổ phiếu (hiện tại: 73.36% Cash / 26.64% Stock).
* **Danh mục đang nắm giữ:** Khối lượng, giá vốn, giá thị trường, tỷ lệ lãi/lỗ %, ngày hàng về (T+2.5).
* **Nhật ký lệnh chi tiết:** Lưu đầy đủ lý do mua, giá cắt lỗ, giá chốt lời cho từng lệnh.
* **Đánh giá tuần:** Đánh giá hiệu suất và rà soát kỷ luật vào cuối mỗi tuần giao dịch.

---

## ⚡ TỰ ĐỘNG HÓA VỚI GITHUB ACTIONS

Dự án đã tích hợp sẵn workflow tại `.github/workflows/daily_report.yml`.

### 1. Lịch chạy tự động 3 lần mỗi ngày (Thứ 2 đến Thứ 6):
* **Lần 1 - 08h30 sáng:** Bản tin chiến lược đầu ngày & chuẩn bị kế hoạch trước giờ mở cửa.
* **Lần 2 - 11h35 trưa:** Cập nhật biến động giá, khối lượng và lãi/lỗ khi kết thúc phiên sáng.
* **Lần 3 - 15h05 chiều:** Tổng kết toàn diện sau giờ đóng cửa phiên, rà soát kỷ luật cắt lỗ/chốt lời.
* **Hành động tự động:**
  1. Tự động khởi chạy trên server đám mây GitHub Actions (hoàn toàn miễn phí).
  2. Quét dữ liệu 60+ cổ phiếu và cập nhật danh mục thực tế (TCB, DCM, TD6).
  3. Tạo file báo cáo mới vào thư mục `reports/` và đẩy link lên Web Rentry.
  4. Tự động vẽ lại trang web `index.html` và cập nhật trực tiếp lên **GitHub Pages**: `https://tuna1710.github.io/chungkhoan/`.

### 2. Cách chạy thủ công bất kỳ lúc nào trên GitHub:
1. Vào repo trên GitHub: `https://github.com/tuna1710/chungkhoan`.
2. Bấm vào tab **Actions**.
3. Chọn workflow **Daily Morning Report & Portfolio Tracker** ở cột bên trái.
4. Bấm nút **Run workflow** -> Chọn branch `main` -> Bấm nút xanh **Run workflow**.
5. Đợi khoảng 30 giây, báo cáo mới sẽ được sinh ra và lưu thẳng vào repo!

---

## 🛡️ KỶ LUẬT THÉP & QUẢN TRỊ RỦI RO

Mọi khuyến nghị của hệ thống đều tuân thủ nguyên tắc sống còn trên thị trường chứng khoán Việt Nam:

1. **Nguyên tắc Cắt lỗ (-5% và -7%):**
   * Lỗ **-5.0%**: Bán ngay **1/2 vị thế** không chần chừ.
   * Lỗ **-7.0% đến -8.0%**: Bán **toàn bộ 100% vị thế**, tuyệt đối **không gồng lỗ** và **không trung bình giá xuống**.
2. **Tỷ lệ Risk : Reward:**
   * Chỉ mở vị thế khi tỷ lệ Lợi nhuận kỳ vọng / Rủi ro đạt tối thiểu **2 : 1** (kỳ vọng lãi từ 10-15% trong khi rủi ro cắt lỗ chỉ trong khoảng 4-5%).
3. **Phân bổ vốn:**
   * Danh mục tối đa chỉ từ 2 đến 3 mã cổ phiếu để đảm bảo khả năng phản ứng nhanh khi thị trường rung lắc mạnh.
   * Luôn duy trì tỷ trọng tiền mặt hợp lý (như hiện tại còn > 73 triệu VNĐ tiền mặt) để chủ động ứng phó.

---

*Hệ thống được vận hành tự động và liên tục cải tiến phục vụ kế hoạch đầu tư 3 tháng.*
