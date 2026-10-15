#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VISUAL DASHBOARD GENERATOR - BẢNG ĐIỀU KHIỂN & ĐÁNH GIÁ CỔ PHIẾU TRỰC QUAN
Tạo trang Dashboard đồ họa tương tác cao, tích hợp CÔNG CỤ ĐÁNH GIÁ CỔ PHIẾU TỰ ĐỘNG (60+ mã),
biểu đồ Radar Chart tương tác, theo dõi danh mục thực tế (TCB, DCM), và phân tích Head-to-Head.
"""

import os
import sys
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(BASE_DIR) == "tools":
    BASE_DIR = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'tools'))
from screener import scan_all_stocks

def generate_visual_dashboard(output_file=None):
    if output_file is None:
        output_file = os.path.join(BASE_DIR, "reports", "dashboard.html")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    today_str = datetime.now().strftime("%d/%m/%Y")
    
    print("\n📊 Đang thu thập dữ liệu và tính toán chỉ số so sánh đa chiều...")
    results = scan_all_stocks()
    
    top_stocks = results[:12]
    top_buys = [s for s in results if s['score'] >= 70][:6]
    top_avoids = [s for s in results if s['score'] < 52 and s['val20_bil'] >= 50][:4]

    radar_labels = ["Thanh khoản", "Xu hướng MA", "Dòng tiền lớn", "Độ siết nền", "Tỷ lệ R:R"]
    
    # 4 mã so sánh tổng quan
    comparison_symbols = ["TCB", "DCM", "KBC", "HPG"]
    comparison_data = {}
    
    # Xây dựng Database đánh giá cho toàn bộ 60+ mã để tra cứu tương tác
    stocks_db = {}
    for s in results:
        liq_score = min(100, (s['val20_bil'] / 200) * 100)
        tr_score = 95 if s['dist_ma20'] >= 0 and s['dist_ma20'] <= 3 else (70 if s['dist_ma20'] > 3 else 40)
        mf_score = min(100, s['vol_ratio'] * 70)
        b_score = max(20, min(100, 100 - s['spread_5d'] * 10))
        rr_sc = min(100, (s['rr_ratio'] / 2.5) * 100)
        
        radar_values = [round(liq_score), round(tr_score), round(mf_score), round(b_score), round(rr_sc)]
        
        stocks_db[s['symbol']] = {
            'symbol': s['symbol'],
            'sector': s['sector'],
            'close': round(s['close'], 2),
            'pct_change': round(s['pct_change'], 2),
            'score': s['score'],
            'action': s['action'],
            'status': s['status'],
            'rsi': round(s['rsi'], 1),
            'dist_ma20': round(s['dist_ma20'], 2),
            'vol_ratio': round(s['vol_ratio'], 2),
            'val20_bil': round(s['val20_bil'], 1),
            'spread_5d': round(s['spread_5d'], 2),
            'rr_ratio': round(s['rr_ratio'], 1),
            'entry_zone': s.get('entry_zone', 'N/A'),
            'stop_loss': round(s.get('cutloss_price', 0), 2),
            'target_price': round(s.get('target_price', 0), 2),
            'potential_upside': round(s.get('potential_upside', 0), 1),
            'tags': s['tags'],
            'radar': radar_values
        }

    for sym in comparison_symbols:
        if sym in stocks_db:
            comparison_data[sym] = {
                'data': stocks_db[sym]['radar'],
                'score': stocks_db[sym]['score']
            }

    stocks_json_str = json.dumps(stocks_db, ensure_ascii=False)
    sorted_symbols = [s['symbol'] for s in sorted(results, key=lambda x: x['score'], reverse=True)]

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bảng Điều Khiển & Đánh Giá Cổ Phiếu - {today_str}</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .badge-buy {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.4); }}
        .badge-watch {{ background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); }}
        .badge-avoid {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); }}
        .pill-active {{ background: #06b6d4 !important; color: #0f172a !important; font-weight: bold; }}
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
                        BẢNG ĐIỀU KHIỂN & ĐÁNH GIÁ CỔ PHIẾU
                        <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Live System</span>
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
                    <span class="text-xs text-slate-400">Tiền mặt / CP:</span>
                    <span class="text-sm font-bold text-cyan-400">44tr (44%) / 56tr (56%)</span>
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
                        <h3 class="text-lg font-bold text-amber-300 mt-1">Kiểm định mốc 1.700</h3>
                    </div>
                    <span class="p-2 rounded-lg bg-amber-500/10 text-amber-400"><i class="fa-solid fa-compass"></i></span>
                </div>
                <p class="text-xs text-slate-400 mt-3">Phân hóa mạnh mẽ. Dòng tiền gom mạnh ở nhóm Ngân hàng và Hóa chất.</p>
            </div>
            <!-- Card 2 -->
            <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 shadow-lg hover:border-slate-600 transition">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-slate-400">Danh Mục Đang Nắm Giữ</p>
                        <h3 class="text-lg font-bold text-emerald-400 mt-1">TCB (900) & DCM (800)</h3>
                    </div>
                    <span class="p-2 rounded-lg bg-emerald-500/10 text-emerald-400"><i class="fa-solid fa-bullseye"></i></span>
                </div>
                <p class="text-xs text-slate-400 mt-3">Khớp giá đỏ tối ưu (TCB 32.64, DCM 33.30). Hàng về chiều 17/10.</p>
            </div>
            <!-- Card 3 -->
            <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 shadow-lg hover:border-slate-600 transition">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-slate-400">Cảnh Báo Kỷ Luật</p>
                        <h3 class="text-lg font-bold text-rose-400 mt-1">Cắt lỗ -5% / -8%</h3>
                    </div>
                    <span class="p-2 rounded-lg bg-rose-500/10 text-rose-400"><i class="fa-solid fa-shield-halved"></i></span>
                </div>
                <p class="text-xs text-slate-400 mt-3">TCB cắt lỗ 31.00; DCM cắt lỗ 31.65. Chạm -5% bán 1/2 không gồng lỗ.</p>
            </div>
            <!-- Card 4 -->
            <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 shadow-lg hover:border-slate-600 transition">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-slate-400">Sức Mua Tiền Mặt</p>
                        <h3 class="text-lg font-bold text-cyan-400 mt-1">43.984.000 VNĐ</h3>
                    </div>
                    <span class="p-2 rounded-lg bg-cyan-500/10 text-cyan-400"><i class="fa-solid fa-wallet"></i></span>
                </div>
                <p class="text-xs text-slate-400 mt-3">Chiếm 43.98% NAV. Tạm dừng mua mới, giữ vị thế chủ động phòng thủ.</p>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- 🎯 CÔNG CỤ TRA CỨU & ĐÁNH GIÁ CỔ PHIẾU TỰ ĐỘNG (INTERACTIVE EVALUATOR) -->
        <!-- ======================================================== -->
        <div class="bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950/40 border border-indigo-500/30 rounded-2xl p-6 shadow-2xl">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5 pb-4 border-b border-slate-700/60">
                <div>
                    <h2 class="text-lg font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-magnifying-glass-chart text-cyan-400"></i>
                        CÔNG CỤ ĐÁNH GIÁ CỔ PHIẾU TỰ ĐỘNG (CHẤM ĐIỂM 0 - 100)
                    </h2>
                    <p class="text-xs text-slate-400 mt-1">Chọn hoặc gõ mã cổ phiếu bất kỳ để xem điểm kỹ thuật, biểu đồ radar 5 trục, vùng gom, điểm cắt lỗ và chốt lời</p>
                </div>
                <!-- Dropdown selector -->
                <div class="flex items-center gap-2">
                    <span class="text-xs text-slate-400">Chọn cổ phiếu:</span>
                    <select id="stockSelect" onchange="selectStock(this.value)" class="bg-slate-900 border border-cyan-500/50 rounded-xl px-4 py-2 text-sm text-cyan-300 font-bold focus:outline-none focus:ring-2 focus:ring-cyan-400 cursor-pointer shadow-lg">
                        <!-- Populated dynamically -->
                    </select>
                </div>
            </div>

            <!-- Quick pick pill buttons -->
            <div class="flex items-center gap-2 flex-wrap mb-5 text-xs">
                <span class="text-slate-400 font-medium mr-1">Xem nhanh:</span>
                <button onclick="selectStock('DCM')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-emerald-500/40 text-emerald-300 font-semibold transition">🔥 DCM (80đ)</button>
                <button onclick="selectStock('TCB')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-indigo-500/40 text-indigo-300 font-semibold transition">🔥 TCB (75đ)</button>
                <button onclick="selectStock('KBC')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-amber-500/40 text-amber-300 font-semibold transition">⭐ KBC (76đ)</button>
                <button onclick="selectStock('HPG')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-cyan-500/40 text-cyan-300 font-semibold transition">⭐ HPG (75đ)</button>
                <button onclick="selectStock('SSI')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-300 transition">SSI</button>
                <button onclick="selectStock('FPT')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-300 transition">FPT</button>
                <button onclick="selectStock('MWG')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-300 transition">MWG</button>
                <button onclick="selectStock('VHM')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-rose-500/40 text-rose-400 transition">⛔ VHM (Gãy)</button>
                <button onclick="selectStock('DGC')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-rose-500/40 text-rose-400 transition">⛔ DGC (Gãy)</button>
            </div>

            <!-- Dynamic Evaluator Card -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 bg-slate-950/60 p-5 rounded-xl border border-slate-800" id="evalCard">
                <!-- Left: Evaluation Details -->
                <div class="lg:col-span-7 space-y-4">
                    <div class="flex items-center justify-between">
                        <div>
                            <span class="text-xs uppercase tracking-wider text-slate-400" id="evalSector">Ngành: Hóa chất</span>
                            <div class="flex items-center gap-3 mt-1">
                                <h3 class="text-2xl font-black text-white" id="evalSymbol">DCM</h3>
                                <span class="text-lg font-bold text-emerald-400" id="evalPrice">34.10k (+3.18%)</span>
                            </div>
                        </div>
                        <div class="text-right">
                            <span class="text-xs text-slate-400 block">ĐIỂM KỸ THUẬT</span>
                            <span class="text-3xl font-black text-emerald-400" id="evalScore">80<span class="text-sm text-slate-500">/100</span></span>
                        </div>
                    </div>

                    <!-- Progress bar -->
                    <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                        <div id="evalScoreBar" class="bg-emerald-500 h-2.5 rounded-full transition-all duration-500" style="width: 80%;"></div>
                    </div>

                    <!-- Action Badge -->
                    <div class="p-3 rounded-lg border font-bold text-sm flex items-center justify-between" id="evalActionBox">
                        <span id="evalActionText">🔥 MUA ƯU TIÊN (TOP 1 TOÀN THỊ TRƯỜNG)</span>
                        <span class="text-xs px-2 py-0.5 rounded bg-black/30 font-semibold" id="evalStatus">SIÊU PHẨM SĂN SÓNG</span>
                    </div>

                    <!-- 4 Trading Key Levels -->
                    <div class="grid grid-cols-4 gap-2 text-center pt-2">
                        <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-700/60">
                            <span class="text-[10px] text-slate-400 block">Vùng gom mua</span>
                            <span class="text-xs font-bold text-cyan-300" id="evalBuyZone">33.84 - 34.10k</span>
                        </div>
                        <div class="bg-slate-900/80 p-2.5 rounded-lg border border-rose-500/30">
                            <span class="text-[10px] text-rose-400 block">Cắt lỗ (-5%)</span>
                            <span class="text-xs font-bold text-rose-400" id="evalStopLoss">32.40k</span>
                        </div>
                        <div class="bg-slate-900/80 p-2.5 rounded-lg border border-emerald-500/30">
                            <span class="text-[10px] text-emerald-400 block">Chốt lời</span>
                            <span class="text-xs font-bold text-emerald-400" id="evalTarget">38.19k (+12%)</span>
                        </div>
                        <div class="bg-slate-900/80 p-2.5 rounded-lg border border-indigo-500/30">
                            <span class="text-[10px] text-indigo-400 block">Tỷ lệ R:R</span>
                            <span class="text-xs font-bold text-indigo-300" id="evalRR">2.4 : 1</span>
                        </div>
                    </div>

                    <!-- Tags list -->
                    <div class="flex items-center gap-1.5 flex-wrap pt-1 text-xs" id="evalTags">
                        <!-- Populated by JS -->
                    </div>
                </div>

                <!-- Right: Dedicated Stock Radar Chart & Quantitative Metrics -->
                <div class="lg:col-span-5 bg-slate-900/70 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <div>
                        <span class="text-xs font-bold text-slate-300 block mb-2 flex items-center gap-2">
                            <i class="fa-solid fa-chart-pie text-cyan-400"></i>
                            BIỂU ĐỒ SỨC MẠNH 5 TRỤC CỦA MÃ NÀY
                        </span>
                        <div class="h-44 relative">
                            <canvas id="stockRadarChart"></canvas>
                        </div>
                    </div>

                    <div class="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-800 text-center text-xs">
                        <div class="bg-slate-800/60 p-1.5 rounded">
                            <span class="text-[10px] text-slate-400 block">Vị thế vs MA20</span>
                            <span class="font-bold text-white" id="evalMa20">+0.76%</span>
                        </div>
                        <div class="bg-slate-800/60 p-1.5 rounded">
                            <span class="text-[10px] text-slate-400 block">Xung lực RSI</span>
                            <span class="font-bold text-white" id="evalRsi">54.1</span>
                        </div>
                        <div class="bg-slate-800/60 p-1.5 rounded">
                            <span class="text-[10px] text-slate-400 block">GTGD Bình quân</span>
                            <span class="font-bold text-white" id="evalVal">95.6 Tỷ</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 3. SO SÁNH ĐA CHIỀU (RADAR CHART TỔNG THỂ & HEAD-TO-HEAD BATTLE) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <!-- Radar Chart: So sánh sức mạnh 4 ứng viên -->
            <div class="lg:col-span-5 bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5 shadow-xl">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <h2 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-diagram-project text-indigo-400"></i>
                            SO SÁNH TƯƠNG QUAN 4 TRỤ CỘT
                        </h2>
                        <p class="text-xs text-slate-400">TCB (Bank) • DCM (Hóa chất) • KBC (KCN) • HPG (Thép)</p>
                    </div>
                    <span class="text-xs text-slate-400 bg-slate-700/50 px-2 py-1 rounded">Thang 100</span>
                </div>
                <div class="h-64 relative">
                    <canvas id="radarChart"></canvas>
                </div>
                <div class="grid grid-cols-4 gap-2 mt-4 text-center">
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-indigo-500/30">
                        <span class="text-xs font-semibold text-indigo-400 block">TCB</span>
                        <span class="text-sm font-bold text-white">75 đ</span>
                    </div>
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-emerald-500/30">
                        <span class="text-xs font-semibold text-emerald-400 block">DCM</span>
                        <span class="text-sm font-bold text-white">80 đ</span>
                    </div>
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-amber-500/30">
                        <span class="text-xs font-semibold text-amber-400 block">KBC</span>
                        <span class="text-sm font-bold text-white">76 đ</span>
                    </div>
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-cyan-500/30">
                        <span class="text-xs font-semibold text-cyan-400 block">HPG</span>
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
                                <span class="font-bold text-emerald-300">✅ KBC:</span> Đã vượt lấy lại MA20 thành công, phiên test cung cạn vol chỉ 0.52x, R:R hấp dẫn 2.5 : 1.
                            </div>
                            <div class="bg-slate-800/40 border border-slate-700/50 p-2 rounded text-slate-400">
                                <span class="font-bold text-slate-300">⚠️ IDC:</span> Vẫn nằm dưới MA20 (-0.4%), áp lực cung bán vùng 34k còn lớn, biên độ lợi nhuận ngắn hạn hẹp hơn.
                            </div>
                        </div>
                    </div>

                    <!-- Battle 3: DCM vs DGC -->
                    <div class="bg-slate-900/80 rounded-xl p-3 border border-slate-700/60 hover:border-slate-600 transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">NHÓM HÓA CHẤT / PHÂN BÓN</span>
                            <span class="text-xs text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Chọn DCM (80đ) > DGC (48đ)</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3 mt-2 text-xs">
                            <div class="bg-emerald-950/30 border border-emerald-800/40 p-2 rounded">
                                <span class="font-bold text-emerald-300">✅ DCM (Top 1):</span> Giá > MA20 > MA50 chuẩn uptrend, tăng +3.18%, test cung hoàn hảo sát MA20, R:R 2.4:1.
                            </div>
                            <div class="bg-slate-800/40 border border-slate-700/50 p-2 rounded text-slate-400">
                                <span class="font-bold text-rose-400">⛔ DGC:</span> Gãy MA50 (-6.2%), RSI yếu 41.5, tổ chức xả hàng, tuyệt đối né xa không bắt đáy.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <!-- FOOTER -->
    <footer class="text-center text-xs text-slate-500 pt-8 border-t border-slate-800 mt-12">
        Hệ thống Tự động hóa Phân tích & Đánh giá Cổ phiếu • Đồng hành kế hoạch NAV 100tr • Cập nhật: {today_str}
    </footer>

    <!-- INTERACTIVE JAVASCRIPT & CHARTS -->
    <script>
        const STOCKS_DB = {stocks_json_str};
        const SORTED_SYMBOLS = {json.dumps(sorted_symbols)};
        let stockRadarChartInstance = null;

        // Initialize Stock Selector Dropdown
        const selector = document.getElementById('stockSelect');
        SORTED_SYMBOLS.forEach(sym => {{
            const s = STOCKS_DB[sym];
            const opt = document.createElement('option');
            opt.value = sym;
            opt.textContent = `${{s.symbol}} (${{s.score}}đ) - ${{s.sector}}`;
            selector.appendChild(opt);
        }});

        function selectStock(symbol) {{
            if (!STOCKS_DB[symbol]) return;
            const s = STOCKS_DB[symbol];
            selector.value = symbol;

            // Update Left Details
            document.getElementById('evalSector').textContent = `Ngành: ${{s.sector}}`;
            document.getElementById('evalSymbol').textContent = s.symbol;
            
            const pctSign = s.pct_change >= 0 ? '+' : '';
            const priceEl = document.getElementById('evalPrice');
            priceEl.textContent = `${{s.close.toFixed(2)}}k (${{pctSign}}${{s.pct_change.toFixed(2)}}%)`;
            priceEl.className = s.pct_change >= 0 ? "text-lg font-bold text-emerald-400" : "text-lg font-bold text-rose-400";

            // Score & Bar
            const scoreEl = document.getElementById('evalScore');
            scoreEl.innerHTML = `${{s.score}}<span class="text-sm text-slate-500">/100</span>`;
            
            const barEl = document.getElementById('evalScoreBar');
            barEl.style.width = `${{s.score}}%`;
            if (s.score >= 80) {{
                scoreEl.className = "text-3xl font-black text-emerald-400";
                barEl.className = "bg-emerald-500 h-2.5 rounded-full transition-all duration-500";
            }} else if (s.score >= 70) {{
                scoreEl.className = "text-3xl font-black text-cyan-400";
                barEl.className = "bg-cyan-500 h-2.5 rounded-full transition-all duration-500";
            }} else if (s.score >= 55) {{
                scoreEl.className = "text-3xl font-black text-amber-400";
                barEl.className = "bg-amber-500 h-2.5 rounded-full transition-all duration-500";
            }} else {{
                scoreEl.className = "text-3xl font-black text-rose-400";
                barEl.className = "bg-rose-500 h-2.5 rounded-full transition-all duration-500";
            }}

            // Action Box
            const actionBox = document.getElementById('evalActionBox');
            const actionText = document.getElementById('evalActionText');
            const statusText = document.getElementById('evalStatus');
            actionText.textContent = s.action;
            statusText.textContent = s.status;

            if (s.score >= 80) {{
                actionBox.className = "p-3 rounded-lg border font-bold text-sm flex items-center justify-between bg-emerald-950/40 border-emerald-500/50 text-emerald-300";
            }} else if (s.score >= 70) {{
                actionBox.className = "p-3 rounded-lg border font-bold text-sm flex items-center justify-between bg-cyan-950/40 border-cyan-500/50 text-cyan-300";
            }} else if (s.score >= 55) {{
                actionBox.className = "p-3 rounded-lg border font-bold text-sm flex items-center justify-between bg-amber-950/40 border-amber-500/50 text-amber-300";
            }} else {{
                actionBox.className = "p-3 rounded-lg border font-bold text-sm flex items-center justify-between bg-rose-950/40 border-rose-500/50 text-rose-300";
            }}

            // Key Levels
            document.getElementById('evalBuyZone').textContent = s.entry_zone;
            document.getElementById('evalStopLoss').textContent = `${{s.stop_loss.toFixed(2)}}k`;
            document.getElementById('evalTarget').textContent = `${{s.target_price.toFixed(2)}}k (+${{s.potential_upside}}%)`;
            document.getElementById('evalRR').textContent = `${{s.rr_ratio.toFixed(1)}} : 1`;

            // Metrics
            const distSign = s.dist_ma20 >= 0 ? '+' : '';
            document.getElementById('evalMa20').textContent = `${{distSign}}${{s.dist_ma20}}%`;
            document.getElementById('evalRsi').textContent = s.rsi;
            document.getElementById('evalVal').textContent = `${{s.val20_bil}} Tỷ`;

            // Tags
            const tagsContainer = document.getElementById('evalTags');
            tagsContainer.innerHTML = '';
            s.tags.forEach(t => {{
                const span = document.createElement('span');
                span.className = "px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300";
                span.textContent = `✓ ${{t}}`;
                tagsContainer.appendChild(span);
            }});

            // Update Dedicated Radar Chart
            updateStockRadar(s);
        }}

        function updateStockRadar(s) {{
            const ctxStock = document.getElementById('stockRadarChart').getContext('2d');
            if (stockRadarChartInstance) {{
                stockRadarChartInstance.destroy();
            }}

            const chartColor = s.score >= 80 ? '#10b981' : (s.score >= 70 ? '#06b6d4' : (s.score >= 55 ? '#f59e0b' : '#ef4444'));
            const chartBg = s.score >= 80 ? 'rgba(16, 185, 129, 0.3)' : (s.score >= 70 ? 'rgba(6, 182, 212, 0.3)' : (s.score >= 55 ? 'rgba(245, 158, 11, 0.3)' : 'rgba(239, 68, 68, 0.3)'));

            stockRadarChartInstance = new Chart(ctxStock, {{
                type: 'radar',
                data: {{
                    labels: {json.dumps(radar_labels, ensure_ascii=False)},
                    datasets: [{{
                        label: `${{s.symbol}} (${{s.score}}đ)`,
                        data: s.radar,
                        backgroundColor: chartBg,
                        borderColor: chartColor,
                        borderWidth: 2,
                        pointBackgroundColor: chartColor
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        r: {{
                            angleLines: {{ color: 'rgba(148, 163, 184, 0.15)' }},
                            grid: {{ color: 'rgba(148, 163, 184, 0.15)' }},
                            pointLabels: {{ color: '#94a3b8', font: {{ size: 9, weight: '600' }} }},
                            ticks: {{ display: false, min: 0, max: 100 }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#cbd5e1', font: {{ size: 10, weight: 'bold' }}, boxWidth: 10 }}
                        }}
                    }}
                }}
            }});
        }}

        // Overall 4-stock comparison radar
        const ctxOverview = document.getElementById('radarChart').getContext('2d');
        new Chart(ctxOverview, {{
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
                        pointLabels: {{ color: '#94a3b8', font: {{ size: 10, weight: '600' }} }},
                        ticks: {{ display: false, min: 0, max: 100 }}
                    }}
                }},
                plugins: {{
                    legend: {{ labels: {{ color: '#cbd5e1', font: {{ size: 11, weight: 'bold' }}, boxWidth: 12 }} }}
                }}
            }}
        }});

        // Default to DCM on load
        selectStock('DCM');
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
