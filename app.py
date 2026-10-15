#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STREAMLIT WEB DASHBOARD - GIAO DIỆN TRỰC QUAN ĐẦU TƯ CHỨNG KHOÁN
Dành cho người dùng thích thao tác click chuột trên trình duyệt, không cần gõ lệnh Terminal.
"""

import os
import sys
import json
from datetime import datetime
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'tools'))
from screener import scan_all_stocks, analyze_stock, WATCHLIST
from daily_morning_report import generate_morning_report

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Trợ Lý Chứng Khoán VN",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tùy biến CSS giao diện hiện đại Dark Mode
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 BẢNG ĐIỀU KHIỂN ĐẦU TƯ CHỨNG KHOÁN (NAV 100M)")
st.caption("Chiến lược Cân bằng Chủ động Săn sóng Ngành • Quản trị rủi ro Max Drawdown < 6%")

# Sidebar điều hướng
menu = st.sidebar.radio(
    "📌 CHỌN TÍNH NĂNG TRỰC QUAN:",
    ["💼 Danh Mục & Tài Khoản", "📊 Bản Tin Sáng & Báo Cáo", "🔍 Bộ Lọc Cổ Phiếu Săn Sóng", "🎯 Soi Chi Tiết 1 Mã CP"]
)

# 1. TAB: DANH MỤC & TÀI KHOẢN
if menu == "💼 Danh Mục & Tài Khoản":
    st.subheader("💰 TỔNG QUAN TÀI SẢN THỰC CHIẾN")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Vốn ban đầu (NAV 0)", value="100,000,000 đ", delta="Mục tiêu: +10-15%")
    with col2:
        st.metric(label="Tiền mặt khả dụng", value="43,984,000 đ", delta="43.98% NAV (An toàn)")
    with col3:
        st.metric(label="Giá trị Cổ phiếu (TCB + DCM)", value="56,016,000 đ", delta="56.02% NAV")
    with col4:
        st.metric(label="Khoản lẻ TD6 (TC6 cũ)", value="~1,905,000 đ", delta="+3.59% (Lãi nhẹ)")

    st.markdown("---")
    st.subheader("📦 CHI TIẾT CÁC MÃ ĐANG NẮM GIỮ")

    # Dữ liệu bảng danh mục
    portfolio_data = [
        {"Mã CP": "TCB", "Ngành": "Ngân hàng", "Khối lượng": 900, "Giá vốn": "32.64k", "Thị giá": "33.20k", "Tổng giá trị": "29,880,000 đ", "Lãi/Lỗ (%)": "+1.72%", "Hàng về": "Chiều 17/10 (T+2.5)", "Khuyến nghị": "NẮM GIỮ (Cắt lỗ 31.00 | Chốt lời 35.9 - 38.0)"},
        {"Mã CP": "DCM", "Ngành": "Hóa chất/Phân bón", "Khối lượng": 800, "Giá vốn": "33.30k", "Thị giá": "34.10k", "Tổng giá trị": "27,280,000 đ", "Lãi/Lỗ (%)": "+2.40%", "Hàng về": "Chiều 17/10 (T+2.5)", "Khuyến nghị": "NẮM GIỮ (Cắt lỗ 31.65 | Chốt lời 36.6 - 38.2)"},
        {"Mã CP": "TD6", "Ngành": "Than", "Khối lượng": 300, "Giá vốn": "6.13k", "Thị giá": "6.35k", "Tổng giá trị": "1,905,000 đ", "Lãi/Lỗ (%)": "+3.59%", "Hàng về": "Khả dụng ngay", "Khuyến nghị": "CANH BÁN 6.4 - 6.5 (Dọn gọn danh mục)"}
    ]
    st.dataframe(portfolio_data, use_container_width=True)

    st.info("💡 **Kỷ luật bảo vệ vốn:** Nếu bất kỳ mã nào vi phạm ngưỡng cắt lỗ **-5.0%**, hệ thống khuyến nghị bán ngay 1/2 vị thế. Thủng **-7%** bán toàn bộ 100% không gồng lỗ.")

# 2. TAB: BẢN TIN SÁNG & BÁO CÁO
elif menu == "📊 Bản Tin Sáng & Báo Cáo":
    st.subheader("🚀 BẢN TIN CHIẾN LƯỢC ĐẦU NGÀY (8H30 SÁNG)")
    
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        if st.button("🔄 BẤM VÀO ĐÂY ĐỂ TẠO BÁO CÁO MỚI NHẤT"):
            with st.spinner("Đang quét 60+ cổ phiếu và tạo báo cáo trực tiếp..."):
                rep_file, web_url = generate_morning_report()
                st.success("Đã tạo báo cáo thành công!")
                if web_url:
                    st.markdown(f"👉 **[Bấm vào đây để mở Bản tin trên Web Rentry]({web_url})**")
    
    # Đọc bản tin mới nhất từ thư mục reports
    reports_dir = os.path.join(BASE_DIR, "reports")
    if os.path.exists(reports_dir):
        files = sorted([f for f in os.listdir(reports_dir) if f.startswith("ban_tin_sang_")], reverse=True)
        if files:
            latest_file = os.path.join(reports_dir, files[0])
            with open(latest_file, "r", encoding="utf-8") as f:
                content = f.read()
            st.markdown(content)

# 3. TAB: BỘ LỌC CỔ PHIẾU
elif menu == "🔍 Bộ Lọc Cổ Phiếu Săn Sóng":
    st.subheader("🏆 SÀNG LỌC TOP CỔ PHIẾU THEO TIÊU CHÍ KỸ THUẬT & DÒNG TIỀN")
    
    sector_filter = st.selectbox("Chọn nhóm ngành lọc (hoặc để Tất cả):", ["Tất cả"] + list(WATCHLIST.keys()))
    sec_arg = None if sector_filter == "Tất cả" else sector_filter
    
    if st.button("🔎 BẮT ĐẦU QUÉT THỊ TRƯỜNG"):
        with st.spinner("Đang tính toán điểm số VSA, RSI, MA20 cho 60+ mã..."):
            results = scan_all_stocks(sector_filter=sec_arg)
            table_data = []
            for i, s in enumerate(results[:15], 1):
                table_data.append({
                    "Hạng": f"#{i}",
                    "Mã CP": s['symbol'],
                    "Ngành": s['sector'],
                    "Điểm số": f"{s['score']}/100",
                    "Thị giá": f"{s['close']:.2f}k",
                    "Thay đổi": f"{s['pct_change']:+.2f}%",
                    "GTGD 20p": f"{s['val20_bil']:.1f} Tỷ",
                    "RSI": round(s['rsi'], 1),
                    "Tỷ lệ R:R": f"{s['rr_ratio']:.1f} : 1",
                    "Khuyến nghị": s['action']
                })
            st.dataframe(table_data, use_container_width=True)

# 4. TAB: SOI CHI TIẾT 1 MÃ
elif menu == "🎯 Soi Chi Tiết 1 Mã CP":
    st.subheader("🎯 TRA CỨU ĐIỂM SỐ & KẾ HOẠCH GIAO DỊCH TỪNG CỔ PHIẾU")
    symbol_input = st.text_input("Nhập mã cổ phiếu cần soi (ví dụ: DCM, TCB, KBC, HPG, MWG):", "DCM").upper()
    
    if st.button(f"🔍 SOI MÃ {symbol_input}"):
        found_sector = "Khác"
        for sec, syms in WATCHLIST.items():
            if symbol_input in syms:
                found_sector = sec
                break
        res = analyze_stock(symbol_input, found_sector)
        if res:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(label="Điểm tổng hợp", value=f"{res['score']}/100", delta=res['action'])
            with c2:
                st.metric(label="Thị giá hiện tại", value=f"{res['close']:.2f}k", delta=f"{res['pct_change']:+.2f}%")
            with c3:
                st.metric(label="Tỷ lệ Lời/Lỗ (R:R)", value=f"{res['rr_ratio']:.1f} : 1", delta="Chuẩn >= 2.0")

            st.markdown("### 📋 Kịch bản thực chiến:")
            st.write(f"- **Vùng giá canh mua:** `{res['buy_min']:.2f} - {res['buy_max']:.2f}k`")
            st.write(f"- **Giá cắt lỗ nghiêm ngặt (-5%):** `{res['stop_loss']:.2f}k` (Thủng là bán, không gồng lỗ)")
            st.write(f"- **Giá chốt lời mục tiêu:** `{res['target_price']:.2f}k` (+{res['potential_upside']:.1f}%)")
            
            st.markdown("### 🏷️ Đặc điểm nhận diện:")
            for tag in res['tags']:
                st.markdown(f"- ✅ **{tag}**")
        else:
            st.error(f"Không tìm thấy dữ liệu cho mã {symbol_input}")
