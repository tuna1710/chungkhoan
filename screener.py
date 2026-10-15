#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STOCK SCREENER - BỘ LỌC CỔ PHIẾU THEO CHIẾN LƯỢC SĂN SÓNG NGÀNH
Phục vụ mục tiêu đầu tư 3 tháng (14/10 - 14/01) - NAV 100 Triệu VNĐ
"""

import os
import sys
import time
import argparse
import requests
import numpy as np
import pandas as pd
from datetime import datetime

# Fix proxy issues for local requests if any
os.environ['no_proxy'] = 'localhost,127.0.0.1'
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

# DANH MỤC CÁC MÃ DẪN SÓNG THEO TỪNG NGÀNH TRỌNG TÂM
WATCHLIST = {
    "Ngân hàng": ["TCB", "MBB", "ACB", "CTG", "BID", "VPB", "HDB", "STB", "TPB", "LPB", "MSB", "VCB", "SHB"],
    "BĐS Khu công nghiệp": ["IDC", "KBC", "VGC", "SZC", "BCM"],
    "Bất động sản": ["NLG", "KDH", "PDR", "DIG", "DXG", "VHM", "VIC"],
    "Chứng khoán": ["SSI", "HCM", "VCI", "VND", "FTS", "BSI", "CTS", "MBS"],
    "Công nghệ - Viễn thông": ["FPT", "CMG", "CTR", "VGI"],
    "Bán lẻ - Tiêu dùng": ["MWG", "FRT", "DGW", "PNJ", "MSN", "VNM"],
    "Thép - Kim loại": ["HPG", "HSG", "NKG"],
    "Hóa chất - Phân bón": ["DGC", "DCM", "DPM"],
    "Dầu khí - Năng lượng": ["PVD", "PVS", "PVT", "BSR", "POW", "PC1"],
    "Xuất khẩu - Khác": ["VHC", "ANV", "TNG", "HAH", "GMD"]
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_stock_ohlcv(symbol, days=150):
    to_time = int(time.time())
    from_time = to_time - days * 86400
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock?from={from_time}&to={to_time}&symbol={symbol}&resolution=1D"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('c') and len(data['c']) >= 30:
                df = pd.DataFrame({
                    'time': pd.to_datetime(data['t'], unit='s'),
                    'open': data['o'],
                    'high': data['h'],
                    'low': data['l'],
                    'close': data['c'],
                    'volume': data['v']
                })
                return df
    except Exception:
        pass
    return None

def compute_indicators(df):
    """Tính toán các chỉ báo kỹ thuật cốt lõi"""
    close = df['close']
    volume = df['volume']
    high = df['high']
    low = df['low']
    
    # Moving averages
    ma10 = close.rolling(10).mean()
    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    vol20 = volume.rolling(20).mean()
    
    # RSI (Wilder's 14)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=13, adjust=False).mean()
    avg_loss = loss.ewm(com=13, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    rsi14 = 100 - (100 / (1 + rs))
    
    # 5-day volatility contraction (độ siết nền)
    high_5d = high.rolling(5).max()
    low_5d = low.rolling(5).min()
    base_spread_pct = ((high_5d - low_5d) / close) * 100
    
    # 60-day resistance / highest high
    high_60d = high.rolling(60).max()
    low_20d = low.rolling(20).min()
    
    return {
        'last_close': close.iloc[-1],
        'prev_close': close.iloc[-2] if len(close) > 1 else close.iloc[-1],
        'last_vol': volume.iloc[-1],
        'ma10': ma10.iloc[-1],
        'ma20': ma20.iloc[-1],
        'ma50': ma50.iloc[-1] if not pd.isna(ma50.iloc[-1]) else ma20.iloc[-1],
        'vol20': vol20.iloc[-1],
        'rsi': rsi14.iloc[-1],
        'spread_5d': base_spread_pct.iloc[-1],
        'high_60d': high_60d.iloc[-1],
        'low_20d': low_20d.iloc[-1]
    }

def analyze_stock(symbol, sector):
    df = fetch_stock_ohlcv(symbol)
    if df is None:
        return None
    
    ind = compute_indicators(df)
    c = ind['last_close']
    prev_c = ind['prev_close']
    v = ind['last_vol']
    ma20 = ind['ma20']
    ma50 = ind['ma50']
    vol20 = ind['vol20']
    rsi = ind['rsi']
    spread_5d = ind['spread_5d']
    high_60d = ind['high_60d']
    
    # 1. Thay đổi giá trong ngày
    pct_change = ((c - prev_c) / prev_c) * 100 if prev_c > 0 else 0
    
    # 2. Giá trị giao dịch trung bình 20 phiên (Tỷ VNĐ/phiên)
    val20_bil = (vol20 * c * 1000) / 1e9
    
    # 3. Đột biến khối lượng (Volume Spike)
    vol_ratio = v / vol20 if vol20 > 0 else 0
    
    # 4. Khoảng cách tới đường MA20
    dist_ma20_pct = ((c - ma20) / ma20) * 100 if ma20 > 0 else 0
    
    # 5. Dư địa tăng tới cản đỉnh cũ 60 phiên (Upside potential)
    potential_upside_pct = max(0.0, ((high_60d - c) / c) * 100) if c > 0 else 0
    
    # Nếu đang vượt đỉnh thì target tối thiểu 12% theo kế hoạch
    if potential_upside_pct < 5.0:
        potential_upside_pct = 12.0
        
    # Ngưỡng cắt lỗ chuẩn 5%
    stop_loss_pct = 5.0
    rr_ratio = potential_upside_pct / stop_loss_pct

    # ================= CHẤM ĐIỂM CỔ PHIẾU (MAX 100 ĐIỂM) =================
    score = 0
    tags = []
    
    # TIÊU CHÍ 1: THANH KHOẢN (Tối đa 15 điểm)
    # Kế hoạch yêu cầu GTGD > 20 - 30 tỷ/phiên
    if val20_bil >= 30:
        score += 15
        tags.append("Thanh khoản dồi dào")
    elif val20_bil >= 15:
        score += 10
    else:
        score += 3
        tags.append("Thanh khoản thấp")

    # TIÊU CHÍ 2: XU HƯỚNG KỸ THUẬT & ĐƯỜNG MA (Tối đa 30 điểm)
    if c >= ma20:
        score += 15
        if ma20 >= ma50:
            score += 10  # Chuẩn cấu trúc Uptrend hoàn hảo
            tags.append("Uptrend vững (Giá > MA20 > MA50)")
        else:
            score += 5
            tags.append("Vượt lại trên MA20")
    else:
        # Dưới MA20
        if c >= ma50:
            score += 8
            tags.append("Hỗ trợ MA50 đỡ")
        else:
            score += 0
            tags.append("Gãy MA20 & MA50 (Yếu)")

    # Phạt nếu tăng quá rướn xa nền MA20 (> 6% là mua đuổi rủi ro)
    if dist_ma20_pct > 6.0:
        score -= 10
        tags.append("Tăng dốc xa nền (Dễ chỉnh)")
    elif 0.0 <= dist_ma20_pct <= 3.0:
        score += 5
        tags.append("Sát nền hỗ trợ MA20")

    # TIÊU CHÍ 3: DÒNG TIỀN & KHỐI LƯỢNG (Tối đa 25 điểm)
    if vol_ratio >= 1.4:
        score += 20
        tags.append(f"Dòng tiền lớn vào mạnh ({vol_ratio:.1f}x vol)")
    elif vol_ratio >= 1.0:
        score += 15
        tags.append("Thanh khoản tích cực")
    elif vol_ratio < 0.7:
        if abs(dist_ma20_pct) <= 2.5:
            score += 15
            tags.append("Test cung cạn vol (Rất đẹp)")
        else:
            score += 8
            tags.append("Thanh khoản cạn kiệt")
    else:
        score += 10

    # TIÊU CHÍ 4: ĐỘ SIẾT NỀN GIÁ & RSI (Tối đa 20 điểm)
    # Nền siết chặt 5 phiên < 3.5%
    if spread_5d <= 3.5:
        score += 10
        tags.append("Nền giá siết chặt (Chờ bung)")
    elif spread_5d <= 5.5:
        score += 5

    # RSI tối ưu từ 48 - 65
    if 50 <= rsi <= 65:
        score += 10
        tags.append("RSI xung lực khỏe (50-65)")
    elif 40 <= rsi < 50:
        score += 6
        tags.append("RSI vùng gom giá rẻ")
    elif rsi > 70:
        score -= 5
        tags.append("RSI quá mua (>70)")
    elif rsi < 35:
        score += 5
        tags.append("RSI quá bán (Hồi phục)")

    # TIÊU CHÍ 5: TỶ LỆ R:R (Tối đa 10 điểm)
    if rr_ratio >= 2.0:
        score += 10
        tags.append(f"Tỷ lệ R:R chuẩn {rr_ratio:.1f}:1")
    elif rr_ratio >= 1.5:
        score += 5

    # Đánh giá hành động khuyến nghị
    if score >= 80:
        action = "🔥 MUA ƯU TIÊN (TOP 1)"
        status = "SIÊU PHẨM SĂN SÓNG"
    elif score >= 70:
        action = "✅ CANH MUA RUNG LẮC"
        status = "TIỀM NĂNG CAO"
    elif score >= 55:
        action = "👀 THEO DÕI NỀN GIÁ"
        status = "TÍCH LŨY CHỜ THÊM"
    else:
        action = "⛔ TẠM ĐỨNG NGOÀI"
        status = "CHƯA ĐẠT TIÊU CHÍ"

    # Mức giá tham vấn (nghìn đồng)
    entry_zone = f"{ma20:.2f} - {c:.2f}" if c >= ma20 else f"{c*0.99:.2f} - {c:.2f}"
    cutloss_price = c * (1 - stop_loss_pct / 100)
    target_price = c * (1 + potential_upside_pct / 100)

    return {
        'symbol': symbol,
        'sector': sector,
        'close': c,
        'pct_change': pct_change,
        'val20_bil': val20_bil,
        'vol_ratio': vol_ratio,
        'dist_ma20': dist_ma20_pct,
        'rsi': rsi,
        'spread_5d': spread_5d,
        'potential_upside': potential_upside_pct,
        'rr_ratio': rr_ratio,
        'score': max(0, min(100, score)),
        'action': action,
        'status': status,
        'tags': tags,
        'entry_zone': entry_zone,
        'cutloss_price': cutloss_price,
        'target_price': target_price
    }

def scan_all_stocks(sector_filter=None):
    results = []
    print("\n🔍 ĐANG QUÉT DỮ LIỆU THỊ TRƯỜNG THEO BỘ TIÊU CHÍ ĐẦU TƯ...")
    
    total_symbols = 0
    for sector, symbols in WATCHLIST.items():
        if sector_filter and sector_filter.lower() not in sector.lower():
            continue
        total_symbols += len(symbols)

    scanned_count = 0
    for sector, symbols in WATCHLIST.items():
        if sector_filter and sector_filter.lower() not in sector.lower():
            continue
        for sym in symbols:
            scanned_count += 1
            print(f" -> [{scanned_count}/{total_symbols}] Quét mã {sym} ({sector})...", end="\r", flush=True)
            res = analyze_stock(sym, sector)
            if res:
                results.append(res)
            time.sleep(0.08)  # Anti rate-limit

    print(f"\n✅ Đã quét xong {len(results)} cổ phiếu trên thị trường.\n")
    # Sắp xếp theo Điểm số giảm dần
    results.sort(key=lambda x: (x['score'], x['val20_bil']), reverse=True)
    return results

def print_top_table(results, top_n=10):
    top_stocks = results[:top_n]
    print("=" * 105)
    print(f"{'TOP':<4}{'MÃ':<6}{'NGÀNH':<20}{'GIÁ (k)':<9}{'+/- (%)':<9}{'GTGD (tỷ)':<11}{'RSI':<7}{'R:R':<7}{'ĐIỂM':<7}{'HÀNH ĐỘNG':<20}")
    print("=" * 105)
    for i, s in enumerate(top_stocks, 1):
        color_change = f"{s['pct_change']:+.2f}%"
        print(f"#{i:<3}{s['symbol']:<6}{s['sector'][:18]:<20}{s['close']:<9.2f}{color_change:<9}{s['val20_bil']:<11.1f}{s['rsi']:<7.1f}{s['rr_ratio']:<7.1f}{s['score']:<7}{s['action']:<20}")
    print("=" * 105)

def print_symbol_detail(s):
    print("\n" + "=" * 70)
    print(f"📊 PHÂN TÍCH CHI TIẾT CỔ PHIẾU: {s['symbol']} - NGÀNH: {s['sector'].upper()}")
    print("=" * 70)
    print(f"• Điểm tổng hợp:      {s['score']}/100 ➔ Trạng thái: {s['status']}")
    print(f"• Khuyến nghị:        {s['action']}")
    print(f"• Giá hiện tại:       {s['close']:.2f} nghìn VNĐ ({s['pct_change']:+.2f}%)")
    print(f"• GTGD bình quân 20p: {s['val20_bil']:.1f} Tỷ VNĐ/phiên (Thanh khoản)")
    print(f"• Khối lượng hôm nay: {s['vol_ratio']:.2f}x so với bình quân 20 phiên")
    print(f"• Vị trí so với MA20: {s['dist_ma20']:+.2f}% (Độ lệch chuẩn nền giá)")
    print(f"• Chỉ số RSI (14):    {s['rsi']:.1f} | Độ siết nền 5 phiên: {s['spread_5d']:.2f}%")
    print("-" * 70)
    print("🎯 KỊCH BẢN THỰC CHIẾN (DÀNH CHO TÀI KHOẢN 100 TRIỆU):")
    print(f"  - Vùng giá canh mua: {s['entry_zone']} nghìn VNĐ")
    print(f"  - Giá cắt lỗ (-5%):  {s['cutloss_price']:.2f} nghìn VNĐ (Thủng là bán, không gồng lỗ)")
    print(f"  - Giá chốt lời mục tiêu: {s['target_price']:.2f} nghìn VNĐ (+{s['potential_upside']:.1f}%)")
    print(f"  - Tỷ lệ Lời/Lỗ (R:R): {s['rr_ratio']:.1f} : 1.0 (Đạt tiêu chí > 2:1)")
    print("• Đặc điểm nhận diện:")
    for tag in s['tags']:
        print(f"   ✓ {tag}")
    print("=" * 70 + "\n")

def export_report_markdown(results, output_file=None):
    if output_file is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(base_dir) == "tools":
            base_dir = os.path.dirname(base_dir)
        output_file = os.path.join(base_dir, "reports", "ket_qua_loc_co_phieu.md")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    today_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    md = f"""# BÁO CÁO KẾT QUẢ SÀNG LỌC CỔ PHIẾU DẪN SÓNG
*Thời gian chạy quét: {today_str}*  
*Chiến lược áp dụng: Cân bằng chủ động săn sóng ngành (Mục tiêu 3 tháng - NAV 100tr)*  

---

## 🏆 TOP CỔ PHIẾU ĐIỂM CAO NHẤT THỊ TRƯỜNG HÔM NAY

| Hạng | Mã CP | Ngành | Giá hiện tại (k) | Thay đổi | GTGD 20p (Tỷ) | RSI | R:R | Điểm số | Hành động khuyến nghị |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
"""
    for i, s in enumerate(results[:15], 1):
        md += f"| **#{i}** | **{s['symbol']}** | {s['sector']} | {s['close']:.2f} | {s['pct_change']:+.2f}% | {s['val20_bil']:.1f} tỷ | {s['rsi']:.1f} | {s['rr_ratio']:.1f}:1 | **{s['score']}/100** | {s['action']} |\n"

    md += """
---

## 🎯 CHI TIẾT CÁC ỨNG VIÊN ĐẠT CHUẨN MUA HÀNG ĐẦU

"""
    for i, s in enumerate(results[:5], 1):
        md += f"""### #{i}. Cổ phiếu **{s['symbol']}** ({s['sector']}) - Điểm: {s['score']}/100
- **Trạng thái:** {s['status']} ({s['action']})
- **Giá tham chiếu/khớp:** `{s['close']:.2f}k` ({s['pct_change']:+.2f}%)
- **Thanh khoản 20 phiên:** `{s['val20_bil']:.1f} tỷ/phiên` (Vol hôm nay: `{s['vol_ratio']:.2f}x` TB20p)
- **Tín hiệu kỹ thuật:** RSI `{s['rsi']:.1f}`, Giá cách MA20 `{s['dist_ma20']:+.2f}%`, Độ siết nền `{s['spread_5d']:.2f}%`
- **Kế hoạch giải ngân (Quy mô 100tr):**
  * **Vùng gom mua:** `{s['entry_zone']}k`
  * **Cắt lỗ nghiêm ngặt (-5%):** `{s['cutloss_price']:.2f}k`
  * **Chốt lời mục tiêu:** `{s['target_price']:.2f}k` (Biên lợi nhuận kỳ vọng: `+{s['potential_upside']:.1f}%`)
  * **Tỷ lệ R:R:** `{s['rr_ratio']:.1f} : 1.0`
- **Đặc điểm nổi bật:**
"""
        for tag in s['tags']:
            md += f"  - {tag}\n"
        md += "\n"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"📁 Đã xuất báo cáo chi tiết ra file: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Bộ lọc cổ phiếu ngon cho thị trường chứng khoán Việt Nam")
    parser.add_argument("--top", type=int, default=10, help="Số lượng top cổ phiếu hiển thị (mặc định: 10)")
    parser.add_argument("--sector", type=str, default=None, help="Lọc riêng theo ngành (ví dụ: NganHang, BDS, ChungKhoan...)")
    parser.add_argument("--symbol", type=str, default=None, help="Xem chi tiết 1 mã cụ thể (ví dụ: TCB, IDC, MWG...)")
    parser.add_argument("--export", action="store_true", help="Xuất kết quả ra file markdown báo cáo")

    args = parser.parse_args()

    if args.symbol:
        sym = args.symbol.upper()
        # Find sector
        found_sector = "Khác"
        for sec, syms in WATCHLIST.items():
            if sym in syms:
                found_sector = sec
                break
        res = analyze_stock(sym, found_sector)
        if res:
            print_symbol_detail(res)
        else:
            print(f"❌ Không tìm thấy dữ liệu cho mã {sym}!")
        return

    results = scan_all_stocks(sector_filter=args.sector)
    if not results:
        print("❌ Không có kết quả nào phù hợp!")
        return

    print_top_table(results, top_n=args.top)

    # Hiển thị chi tiết top 2 ứng viên cao điểm nhất (phù hợp danh mục 2 mã theo muc_tieu.md)
    print("\n💡 GỢI Ý 2 CỔ PHIẾU XUẤT SẮC NHẤT CHO DANH MỤC 100 TRIỆU:")
    for top_sym in results[:2]:
        print_symbol_detail(top_sym)

    if args.export:
        export_report_markdown(results)

if __name__ == "__main__":
    main()
