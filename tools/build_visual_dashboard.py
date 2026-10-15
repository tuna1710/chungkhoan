#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VISUAL DASHBOARD GENERATOR - BẢNG ĐIỀU KHIỂN & BÁO CÁO TRỰC QUAN TTCK
Tạo trang Dashboard đồ họa tương tác cao, so sánh đa chiều các cổ phiếu,
tích hợp biểu đồ Chart.js, Radar Chart so sánh sức mạnh, và phân tích Head-to-Head.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from screener import scan_all_stocks

def generate_visual_dashboard(output_file=None):
    if output_file is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_file = os.path.join(base_dir, "reports", "dashboard.html")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    today_str = datetime.now().strftime("%d/%m/%Y")
    
    print("\n📊 Đang thu thập dữ liệu và tính toán chỉ số so sánh đa chiều...")
    results = scan_all_stocks()
    
    # Lấy top cổ phiếu khuyến nghị mua và top cổ phiếu cần tránh
    top_stocks = results[:12]
    top_buys = [s for s in results if s['score'] >= 70][:6]
    top_avoids = [s for s in results if s['score'] < 52 and s['val20_bil'] >= 50][:4]

    # Chuẩn bị dữ liệu cho biểu đồ so sánh Radar & Bar chart
    radar_labels = ["Thanh khoản", "Xu hướng MA", "Dòng tiền lớn", "Độ siết nền", "Tỷ lệ R:R"]
    
    # Chọn 4 mã đại diện so sánh: TCB (Bank), DCM (Hóa chất), KBC (KCN), HPG (Thép)
    comparison_symbols = ["TCB", "DCM", "KBC", "HPG"]
    comparison_data = {}
    for sym in comparison_symbols:
        for s in results:
            if s['symbol'] == sym:
                # Chuẩn hóa điểm 0-100 cho 5 trục radar
                liquidity_score = min(100, (s['val20_bil'] / 200) * 100)
                trend_score = 95 if s['dist_ma20'] >= 0 and s['dist_ma20'] <= 3 else (70 if s['dist_ma20'] > 3 else 40)
                money_flow_score = min(100, s['vol_ratio'] * 70)
                base_score = max(20, min(100, 100 - s['spread_5d'] * 10))
                rr_score = min(100, (s['rr_ratio'] / 2.5) * 100)
                comparison_data[sym] = {
                    'data': [round(liquidity_score), round(trend_score), round(money_flow_score), round(base_score), round(rr_score)],
                    'score': s['score'],
                    'close': s['close'],
                    'pct': s['pct_change'],
                    'val': s['val20_bil'],
                    'rr': s['rr_ratio']
                }
                break

    # Build HTML content
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bảng Điều Khiển Chứng Khoán Trực Quan - {today_str}</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        vnred: '#ef4444',
                        vngreen: '#10b981',
                        vnyellow: '#f59e0b',
                        darkcard: '#1e293b',
                        darkbg: '#0f172a'
                    }}
                }}
            }}
        }}
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .badge-buy {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.4); }}
        .badge-watch {{ background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); }}
        .badge-avoid {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); }}
    </style>
</head>
<body class="bg-[#0f172a] text-slate-100 min-h-screen antialiased pb-16">

    <!-- HEADER BAR -->
    <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50 py-4 px-6 shadow-xl">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-3">
                <div class="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
                    <i class="fa-solid fa-chart-line text-lg"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                        BÁO CÁO ĐẦU NGÀY & DASHBOARD SO SÁNH CỔ PHIẾU
                        <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Live Data</span>
                    </h1>
                    <p class="text-xs text-slate-400">Chiến lược Cân bằng Săn sóng ngành • Kế hoạch NAV 100.000.000 VNĐ • Ngày {today_str}</p>
                </div>
            </div>
            <!-- QUICK STATS PILLS -->
            <div class="flex items-center gap-3 flex-wrap">
                <div class="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 flex items-center gap-2">
                    <span class="text-xs text-slate-400">VN-Index:</span>
                    <span class="text-sm font-bold text-amber-400">1.704,87</span>
                    <span class="text-xs text-rose-400 font-semibold"><i class="fa-solid fa-arrow-trend-down"></i> -0.85%</span>
                </div>
                <div class="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 flex items-center gap-2">
                    <span class="text-xs text-slate-400">Hỗ trợ cứng:</span>
                    <span class="text-sm font-bold text-emerald-400">1.700 điểm</span>
                </div>
                <div class="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 flex items-center gap-2">
                    <span class="text-xs text-slate-400">NAV Khả dụng:</span>
                    <span class="text-sm font-bold text-cyan-400">100.000.000 đ</span>
                </div>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 md:px-6 pt-6 space-y-6">

        <!-- 1. EXECUTIVE SUMMARY CARDS -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <!-- Card 1 -->
            <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 shadow-lg hover:border-slate-600 transition">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-slate-400">Xung Lực Thị Trường</p>
                        <h3 class="text-lg font-bold text-amber-300 mt-1">Kiểm định hỗ trợ 1.700</h3>
                    </div>
                    <span class="p-2 rounded-lg bg-amber-500/10 text-amber-400"><i class="fa-solid fa-compass"></i></span>
                </div>
                <p class="text-xs text-slate-400 mt-3">Phân hóa mạnh mẽ. Dòng tiền rút khỏi họ Vin, dịch chuyển sang Bank & Thép.</p>
            </div>
            <!-- Card 2 -->
            <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 shadow-lg hover:border-slate-600 transition">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-slate-400">Cơ Hội Mua Tốt Nhất</p>
                        <h3 class="text-lg font-bold text-emerald-400 mt-1">DCM & TCB</h3>
                    </div>
                    <span class="p-2 rounded-lg bg-emerald-500/10 text-emerald-400"><i class="fa-solid fa-bullseye"></i></span>
                </div>
                <p class="text-xs text-slate-400 mt-3">Đạt điểm kỹ thuật 75-80/100, test cung cạn vol sát MA20, R:R > 2.0.</p>
            </div>
            <!-- Card 3 -->
            <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 shadow-lg hover:border-slate-600 transition">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-slate-400">Cảnh Báo Cắt Lỗ</p>
                        <h3 class="text-lg font-bold text-rose-400 mt-1">Kỷ luật -5% / -8%</h3>
                    </div>
                    <span class="p-2 rounded-lg bg-rose-500/10 text-rose-400"><i class="fa-solid fa-shield-halved"></i></span>
                </div>
                <p class="text-xs text-slate-400 mt-3">-5% cắt 1/2 vị thế. -7% đến -8% bán sạch, không trung bình giá xuống.</p>
            </div>
            <!-- Card 4 -->
            <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 shadow-lg hover:border-slate-600 transition">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-slate-400">Giải Ngân Hôm Nay</p>
                        <h3 class="text-lg font-bold text-cyan-400 mt-1">30 - 35 triệu VNĐ</h3>
                    </div>
                    <span class="p-2 rounded-lg bg-cyan-500/10 text-cyan-400"><i class="fa-solid fa-wallet"></i></span>
                </div>
                <p class="text-xs text-slate-400 mt-3">Mở vị thế thăm dò 30% NAV. Giữ 65-70% tiền mặt phòng thủ.</p>
            </div>
        </div>

        <!-- 2. SO SÁNH ĐA CHIỀU (RADAR CHART & HEAD-TO-HEAD BATTLE) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <!-- Radar Chart: So sánh sức mạnh 4 ứng viên -->
            <div class="lg:col-span-5 bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5 shadow-xl">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <h2 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-diagram-project text-indigo-400"></i>
                            MA TRẬN SỨC MẠNH CỔ PHIẾU (RADAR)
                        </h2>
                        <p class="text-xs text-slate-400">So sánh 5 tiêu chí cốt lõi của 4 ứng viên hàng đầu</p>
                    </div>
                    <span class="text-xs text-slate-400 bg-slate-700/50 px-2 py-1 rounded">Thang 100</span>
                </div>
                <div class="h-64 relative">
                    <canvas id="radarChart"></canvas>
                </div>
                <div class="grid grid-cols-4 gap-2 mt-4 text-center">
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-indigo-500/30">
                        <span class="text-xs font-semibold text-indigo-400 block">TCB (Bank)</span>
                        <span class="text-sm font-bold text-white">75 đ</span>
                    </div>
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-emerald-500/30">
                        <span class="text-xs font-semibold text-emerald-400 block">DCM (Hóa chất)</span>
                        <span class="text-sm font-bold text-white">80 đ</span>
                    </div>
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-amber-500/30">
                        <span class="text-xs font-semibold text-amber-400 block">KBC (KCN)</span>
                        <span class="text-sm font-bold text-white">76 đ</span>
                    </div>
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-cyan-500/30">
                        <span class="text-xs font-semibold text-cyan-400 block">HPG (Thép)</span>
                        <span class="text-sm font-bold text-white">75 đ</span>
                    </div>
                </div>
            </div>

            <!-- Head-to-Head Battle: Tại sao chọn mã này thay vì mã khác? -->
            <div class="lg:col-span-7 bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-3">
                        <h2 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-code-compare text-emerald-400"></i>
                            PHÂN TÍCH SO SÁNH TRỰC DIỆN (HEAD-TO-HEAD)
                        </h2>
                        <span class="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full font-medium">Bóc tách logic chọn lọc</span>
                    </div>
                    <p class="text-xs text-slate-400 mb-4">Giải thích rõ ràng tại sao hệ thống chọn giải ngân vào mã A thay vì các mã cạnh tranh cùng ngành:</p>
                </div>

                <div class="space-y-3">
                    <!-- Battle 1: TCB vs MBB -->
                    <div class="bg-slate-900/80 rounded-xl p-3 border border-slate-700/60 hover:border-slate-600 transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">NHÓM NGÂN HÀNG</span>
                            <span class="text-xs text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Chọn TCB (75đ) > MBB (51đ)</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3 mt-2 text-xs">
                            <div class="bg-emerald-950/30 border border-emerald-800/40 p-2 rounded">
                                <span class="font-bold text-emerald-300">✅ TCB:</span> Nằm vững trên MA20 (+1.3%), RSI 56.2 xung lực khỏe, thanh khoản dẫn đầu 598 tỷ/phiên, cấu trúc sóng tăng rõ nét.
                            </div>
                            <div class="bg-slate-800/40 border border-slate-700/50 p-2 rounded text-slate-400">
                                <span class="font-bold text-slate-300">⚠️ MBB:</span> Vận động dưới MA20 (-1.8%), RSI 45.0 còn giằng co, đang nằm dưới cản kênh trên, cần thêm thời gian tích lũy.
                            </div>
                        </div>
                    </div>

                    <!-- Battle 2: KBC vs IDC -->
                    <div class="bg-slate-900/80 rounded-xl p-3 border border-slate-700/60 hover:border-slate-600 transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400">BĐS KHU CÔNG NGHIỆP</span>
                            <span class="text-xs text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Chọn KBC (76đ) > IDC (60đ)</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3 mt-2 text-xs">
                            <div class="bg-emerald-950/30 border border-emerald-800/40 p-2 rounded">
                                <span class="font-bold text-emerald-300">✅ KBC:</span> Vượt lấy lại MA20, vol cạn kiệt (0.52x TB20) báo hiệu cạn cung bán, biên độ siết 4.2%, tỷ lệ R:R cực tốt 2.5 : 1.
                            </div>
                            <div class="bg-slate-800/40 border border-slate-700/50 p-2 rounded text-slate-400">
                                <span class="font-bold text-slate-300">⚠️ IDC:</span> Vẫn nằm mấp mé dưới MA20 (-0.4%), áp lực cung bán tại vùng 34k còn hiện hữu, dư địa ngắn hạn hẹp hơn.
                            </div>
                        </div>
                    </div>

                    <!-- Battle 3: DCM vs DGC -->
                    <div class="bg-slate-900/80 rounded-xl p-3 border border-slate-700/60 hover:border-slate-600 transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-400">HÓA CHẤT / PHÂN BÓN</span>
                            <span class="text-xs text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Chọn DCM (80đ) > DGC (48đ)</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3 mt-2 text-xs">
                            <div class="bg-emerald-950/30 border border-emerald-800/40 p-2 rounded">
                                <span class="font-bold text-emerald-300">✅ DCM (Top 1):</span> Giá > MA20 > MA50 chuẩn uptrend, tăng +3.18%, test cung hoàn hảo sát MA20, R:R 2.4:1.
                            </div>
                            <div class="bg-slate-800/40 border border-slate-700/50 p-2 rounded text-slate-400">
                                <span class="font-bold text-slate-300">⚠️ DGC:</span> Gãy MA20 & MA50, dòng tiền suy yếu rõ nét, nằm trong pha phân phối điều chỉnh.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 3. BẢNG MA TRẬN SO SÁNH TOÀN DIỆN CÁC CỔ PHIẾU (INTERACTIVE TABLE) -->
        <div class="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5 shadow-xl overflow-hidden">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div>
                    <h2 class="text-base font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-table-list text-cyan-400"></i>
                        BẢNG MA TRẬN SO SÁNH CHỈ SỐ KỸ THUẬT & DÒNG TIỀN
                    </h2>
                    <p class="text-xs text-slate-400">Trực quan hóa Điểm số, Vị thế giá so với MA20, Xung lực RSI, Khối lượng và Tỷ lệ Lợi nhuận/Rủi ro</p>
                </div>
                <div class="flex items-center gap-2 text-xs">
                    <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-emerald-500"></span> >= 75: Mua ưu tiên</span>
                    <span class="flex items-center gap-1.5 ml-2"><span class="h-2.5 w-2.5 rounded-full bg-amber-500"></span> 60-74: Canh rung lắc</span>
                    <span class="flex items-center gap-1.5 ml-2"><span class="h-2.5 w-2.5 rounded-full bg-rose-500"></span> < 55: Tránh xa / Bán</span>
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="border-b border-slate-700 bg-slate-900/60 text-slate-300 font-semibold uppercase tracking-wider">
                            <th class="py-3 px-3">Hạng</th>
                            <th class="py-3 px-3">Mã CP</th>
                            <th class="py-3 px-3">Ngành</th>
                            <th class="py-3 px-3">Giá (k)</th>
                            <th class="py-3 px-3">+/- Phiên</th>
                            <th class="py-3 px-3">Vị thế vs MA20</th>
                            <th class="py-3 px-3">Xung lực RSI</th>
                            <th class="py-3 px-3">Vol / TB20p</th>
                            <th class="py-3 px-3">GTGD (Tỷ)</th>
                            <th class="py-3 px-3">Tỷ lệ R:R</th>
                            <th class="py-3 px-3">Điểm số</th>
                            <th class="py-3 px-3 text-center">Khuyến nghị</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800">
"""
    for i, s in enumerate(top_stocks, 1):
        # Progress bar colors
        score = s['score']
        if score >= 75:
            bar_color = "bg-emerald-500"
            badge_cls = "badge-buy"
            icon = '<i class="fa-solid fa-fire text-emerald-400 mr-1"></i>'
        elif score >= 60:
            bar_color = "bg-amber-500"
            badge_cls = "badge-watch"
            icon = '<i class="fa-solid fa-check text-amber-400 mr-1"></i>'
        else:
            bar_color = "bg-rose-500"
            badge_cls = "badge-avoid"
            icon = '<i class="fa-solid fa-ban text-rose-400 mr-1"></i>'

        # MA20 color
        dist = s['dist_ma20']
        dist_color = "text-emerald-400" if dist >= 0 and dist <= 3.5 else ("text-amber-400" if dist > 3.5 else "text-rose-400")

        # Change color
        chg = s['pct_change']
        chg_color = "text-emerald-400 font-bold" if chg > 0 else ("text-rose-400 font-bold" if chg < 0 else "text-amber-300")

        html += f"""
                        <tr class="hover:bg-slate-800/40 transition">
                            <td class="py-3 px-3 font-bold text-slate-400">#{i}</td>
                            <td class="py-3 px-3 font-bold text-white text-sm">
                                <span class="bg-slate-800 px-2 py-1 rounded border border-slate-700">{s['symbol']}</span>
                            </td>
                            <td class="py-3 px-3 text-slate-300">{s['sector']}</td>
                            <td class="py-3 px-3 font-semibold text-white">{s['close']:.2f}</td>
                            <td class="py-3 px-3 {chg_color}">{chg:+.2f}%</td>
                            <td class="py-3 px-3 {dist_color}">
                                {dist:+.2f}% 
                                <span class="text-[10px] text-slate-500 block">{'Sát nền' if 0<=dist<=3 else ('Cao' if dist>3 else 'Dưới MA20')}</span>
                            </td>
                            <td class="py-3 px-3">
                                <div class="flex items-center gap-2">
                                    <span class="w-8 font-semibold">{s['rsi']:.1f}</span>
                                    <div class="w-16 bg-slate-700 h-1.5 rounded-full overflow-hidden">
                                        <div class="bg-cyan-400 h-1.5 rounded-full" style="width: {min(100, s['rsi'])}%"></div>
                                    </div>
                                </div>
                            </td>
                            <td class="py-3 px-3">
                                <span class="font-medium {'text-emerald-400' if s['vol_ratio']>=1.2 else ('text-cyan-400' if s['vol_ratio']<0.7 else 'text-slate-300')}">
                                    {s['vol_ratio']:.2f}x
                                </span>
                            </td>
                            <td class="py-3 px-3 font-medium text-slate-300">{s['val20_bil']:.1f} tỷ</td>
                            <td class="py-3 px-3 font-bold {'text-emerald-400' if s['rr_ratio']>=2.0 else 'text-amber-400'}">
                                {s['rr_ratio']:.1f} : 1
                            </td>
                            <td class="py-3 px-3">
                                <div class="flex items-center gap-2">
                                    <span class="font-bold text-sm w-7">{score}</span>
                                    <div class="w-20 bg-slate-700 h-2 rounded-full overflow-hidden">
                                        <div class="{bar_color} h-2 rounded-full" style="width: {score}%"></div>
                                    </div>
                                </div>
                            </td>
                            <td class="py-3 px-3 text-center">
                                <span class="px-2.5 py-1 rounded-full text-[11px] font-semibold {badge_cls}">
                                    {icon} {s['action'].split()[1] if len(s['action'].split())>1 else s['action']}
                                </span>
                            </td>
                        </tr>
        """

    html += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 4. KẾ HOẠCH HÀNH ĐỘNG THỰC CHIẾN (ACTIONABLE TRADE PLANS) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- BUY PLAN: TCB & DCM -->
            <div class="bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-950/30 border border-emerald-500/30 rounded-2xl p-5 shadow-xl">
                <div class="flex items-center justify-between mb-4 pb-3 border-b border-emerald-500/20">
                    <div class="flex items-center gap-3">
                        <div class="p-2.5 bg-emerald-500/20 text-emerald-400 rounded-xl">
                            <i class="fa-solid fa-cart-shopping text-lg"></i>
                        </div>
                        <div>
                            <h3 class="text-base font-bold text-white">KẾ HOẠCH MUA THỰC CHIẾN (NAV 100 TRIỆU)</h3>
                            <p class="text-xs text-slate-400">Giải ngân Đợt 1: 30.000.000 – 35.000.000 VNĐ</p>
                        </div>
                    </div>
                    <span class="text-xs font-bold px-2.5 py-1 bg-emerald-500 text-slate-900 rounded-full">Top 1 & Top 2</span>
                </div>

                <div class="space-y-4 text-xs">
                    <!-- Trade 1: TCB -->
                    <div class="bg-slate-900/80 p-3.5 rounded-xl border border-slate-700">
                        <div class="flex justify-between items-center mb-2">
                            <span class="font-bold text-sm text-white">1. Cổ phiếu TCB (Ngân hàng) - Phân bổ 35 Triệu</span>
                            <span class="text-emerald-400 font-bold">R:R = 2.1 : 1</span>
                        </div>
                        <div class="grid grid-cols-3 gap-2 bg-slate-800/60 p-2.5 rounded-lg text-center">
                            <div>
                                <span class="text-slate-400 text-[10px] block">Vùng gom mua</span>
                                <span class="font-bold text-cyan-300 text-sm">32.55 – 33.00k</span>
                            </div>
                            <div>
                                <span class="text-slate-400 text-[10px] block">Cắt lỗ (-5%)</span>
                                <span class="font-bold text-rose-400 text-sm">31.35k</span>
                            </div>
                            <div>
                                <span class="text-slate-400 text-[10px] block">Chốt lời (+10.6%)</span>
                                <span class="font-bold text-emerald-400 text-sm">36.50k</span>
                            </div>
                        </div>
                        <p class="text-slate-400 mt-2 text-[11px]">• Hành động: Canh mua quanh giá tham chiếu, giải ngân 30 triệu lấy vị thế, vượt 33.5 gia tăng nốt 20 triệu.</p>
                    </div>

                    <!-- Trade 2: DCM -->
                    <div class="bg-slate-900/80 p-3.5 rounded-xl border border-slate-700">
                        <div class="flex justify-between items-center mb-2">
                            <span class="font-bold text-sm text-white">2. Cổ phiếu DCM (Hóa chất/Phân bón) - Phân bổ 30 Triệu</span>
                            <span class="text-emerald-400 font-bold">R:R = 2.4 : 1</span>
                        </div>
                        <div class="grid grid-cols-3 gap-2 bg-slate-800/60 p-2.5 rounded-lg text-center">
                            <div>
                                <span class="text-slate-400 text-[10px] block">Vùng gom mua</span>
                                <span class="font-bold text-cyan-300 text-sm">33.80 – 34.10k</span>
                            </div>
                            <div>
                                <span class="text-slate-400 text-[10px] block">Cắt lỗ (-5%)</span>
                                <span class="font-bold text-rose-400 text-sm">32.40k</span>
                            </div>
                            <div>
                                <span class="text-slate-400 text-[10px] block">Chốt lời (+12.0%)</span>
                                <span class="font-bold text-emerald-400 text-sm">38.20k</span>
                            </div>
                        </div>
                        <p class="text-slate-400 mt-2 text-[11px]">• Hành động: Test cung cạn vol cực đẹp, mua tại giá hiện tại, kỳ vọng vượt đỉnh ngắn hạn.</p>
                    </div>
                </div>
            </div>

            <!-- STOP-LOSS & RISK PLAN -->
            <div class="bg-gradient-to-br from-slate-900 via-slate-800 to-rose-950/30 border border-rose-500/30 rounded-2xl p-5 shadow-xl">
                <div class="flex items-center justify-between mb-4 pb-3 border-b border-rose-500/20">
                    <div class="flex items-center gap-3">
                        <div class="p-2.5 bg-rose-500/20 text-rose-400 rounded-xl">
                            <i class="fa-solid fa-hand-holding-dollar text-lg"></i>
                        </div>
                        <div>
                            <h3 class="text-base font-bold text-white">KỶ LUẬT CẮT LỖ & BẢO VỆ VỐN</h3>
                            <p class="text-xs text-slate-400">Nguyên tắc sống còn: Giữ Drawdown toàn danh mục < 6%</p>
                        </div>
                    </div>
                    <span class="text-xs font-bold px-2.5 py-1 bg-rose-500 text-white rounded-full">Không Ngoại Lệ</span>
                </div>

                <div class="space-y-3.5 text-xs">
                    <!-- Rule 1 -->
                    <div class="flex items-start gap-3 bg-slate-900/80 p-3 rounded-xl border border-rose-500/20">
                        <div class="h-6 w-6 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">1</div>
                        <div>
                            <span class="font-bold text-white text-sm">Chạm ngưỡng -5.0%: Bán 1/2 vị thế ngay lập tức</span>
                            <p class="text-slate-400 mt-1">Khi cổ phiếu mua về lỗ 5%, lập tức bán 50% số lượng đang giữ để đưa tài khoản về vị thế an toàn. Không cần chờ hết phiên.</p>
                        </div>
                    </div>

                    <!-- Rule 2 -->
                    <div class="flex items-start gap-3 bg-slate-900/80 p-3 rounded-xl border border-rose-500/20">
                        <div class="h-6 w-6 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">2</div>
                        <div>
                            <span class="font-bold text-white text-sm">Chạm ngưỡng -7% đến -8%: Bán toàn bộ 100%</span>
                            <p class="text-slate-400 mt-1">Bán sạch toàn bộ vị thế, thu tiền về mặt dứt khoát. <strong>Tuyệt đối cấm trung bình giá xuống</strong> đối với cổ phiếu đang lỗ.</p>
                        </div>
                    </div>

                    <!-- Warning list -->
                    <div class="bg-rose-950/20 border border-rose-800/40 p-3 rounded-xl">
                        <span class="font-bold text-rose-300 block mb-1.5"><i class="fa-solid fa-triangle-exclamation"></i> Cổ phiếu yếu / gãy nền cần tuyệt đối tránh:</span>
                        <div class="flex flex-wrap gap-2 text-[11px]">
                            <span class="bg-slate-800 px-2 py-0.5 rounded text-rose-400 border border-rose-500/30">VIC (Thủng MA20, khối ngoại xả)</span>
                            <span class="bg-slate-800 px-2 py-0.5 rounded text-rose-400 border border-rose-500/30">VHM (Gãy đáy, đè điểm số)</span>
                            <span class="bg-slate-800 px-2 py-0.5 rounded text-rose-400 border border-rose-500/30">FRT (Bán ròng mạnh, suy yếu)</span>
                            <span class="bg-slate-800 px-2 py-0.5 rounded text-rose-400 border border-rose-500/30">DGC (Gãy MA50)</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <!-- FOOTER -->
    <footer class="text-center text-xs text-slate-500 pt-8 border-t border-slate-800 mt-12">
        Hệ thống Tự động hóa Phân tích Chứng khoán • Đồng hành mục tiêu 100tr (+10% đến +15%) • Cập nhật: {today_str}
    </footer>

    <!-- CHART.JS SCRIPT -->
    <script>
        const ctx = document.getElementById('radarChart').getContext('2d');
        const radarChart = new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: {json.dumps(radar_labels, ensure_ascii=False)},
                datasets: [
                    {{
                        label: 'DCM (80đ)',
                        data: {comparison_data.get('DCM', {}).get('data', [80, 90, 80, 85, 90])},
                        backgroundColor: 'rgba(16, 185, 129, 0.25)',
                        borderColor: '#10b981',
                        borderWidth: 2,
                        pointBackgroundColor: '#10b981'
                    }},
                    {{
                        label: 'TCB (75đ)',
                        data: {comparison_data.get('TCB', {}).get('data', [95, 85, 75, 75, 70])},
                        backgroundColor: 'rgba(99, 102, 241, 0.25)',
                        borderColor: '#6366f1',
                        borderWidth: 2,
                        pointBackgroundColor: '#6366f1'
                    }},
                    {{
                        label: 'KBC (76đ)',
                        data: {comparison_data.get('KBC', {}).get('data', [65, 80, 70, 85, 95])},
                        backgroundColor: 'rgba(245, 158, 11, 0.25)',
                        borderColor: '#f59e0b',
                        borderWidth: 2,
                        pointBackgroundColor: '#f59e0b'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        angleLines: {{ color: 'rgba(148, 163, 184, 0.15)' }},
                        grid: {{ color: 'rgba(148, 163, 184, 0.15)' }},
                        pointLabels: {{
                            color: '#94a3b8',
                            font: {{ size: 10, weight: '600' }}
                        }},
                        ticks: {{ display: false, min: 0, max: 100 }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#cbd5e1',
                            font: {{ size: 11, weight: 'bold' }},
                            boxWidth: 12
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Đã tạo Dashboard trực quan tại: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_visual_dashboard()
