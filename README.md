# 📈 TRỢ LÝ ĐẦU TƯ CHỨNG KHOÁN VIỆT NAM (VIETNAM STOCK ASSISTANT)

Hệ thống tự động hóa phân tích kỹ thuật, sàng lọc cổ phiếu săn sóng ngành, quản trị kỷ luật tài khoản (NAV 100M) và tự động phát hành Bản tin chiến lược đầu ngày lúc 08h30 sáng lên Web.

---

## 🌟 TÍNH NĂNG CHÍNH

1. **Quản trị Danh mục Thực chiến (Portfolio Tracker):**
   - Theo dõi trạng thái từng mã đang nắm giữ (DCM, TD6...), lệnh chờ (TCB).
   - Kiểm soát kỷ luật cắt lỗ (-5% bán 1/2, -7% bán hết) và chốt lời theo kế hoạch.
   - Quản trị tỷ lệ Tiền mặt / Cổ phiếu và giới hạn sụt giảm vốn (Max Drawdown < 6%).

2. **Bộ lọc Săn Sóng Ngành (Stock Screener):**
   - Chấm điểm kỹ thuật 0 - 100 điểm cho 60+ cổ phiếu đầu ngành.
   - Đo lường VSA, RSI, khoảng cách MA20/MA50, độ siết nền, tỷ lệ Risk:Reward >= 2.0.

3. **Bản tin Chiến lược Đầu ngày (Daily Morning Report):**
   - Chạy tự động lúc 08h30 sáng mỗi ngày giao dịch qua GitHub Actions.
   - Tự động xuất bản lên Web qua Rentry.co để xem nhanh trên điện thoại không bị chặn.

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & CHẠY THỦ CÔNG

### 1. Cài đặt môi trường
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
```

### 2. Chạy Báo cáo Chiến lược Đầu ngày & Theo dõi Danh mục
```bash
python3 daily_report.py
```

### 3. Sử dụng Bộ lọc Cổ phiếu
```bash
# Quét toàn thị trường
python3 screener.py

# Quét Top 5 và xuất báo cáo markdown
python3 screener.py --top 5 --export

# Lọc theo nhóm ngành
python3 screener.py --sector "Ngân hàng"
python3 screener.py --sector "Hóa chất - Phân bón"

# Phân tích chuyên sâu 1 mã
python3 screener.py --symbol DCM
```

---

## ⚙️ TỰ ĐỘNG HÓA VỚI GITHUB ACTIONS

Workflow tại `.github/workflows/daily_report.yml` đã được cấu hình sẵn:
- **Lịch chạy:** 08h30 sáng (01h30 UTC) từ Thứ 2 đến Thứ 6.
- **Hành động:** Chạy phân tích, cập nhật danh mục, xuất bản link web và tự động commit báo cáo mới vào repo.
