#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VISUAL DASHBOARD GENERATOR - BẢNG ĐIỀU KHIỂN & MA TRẬN SO SÁNH CỔ PHIẾU TRỰC QUAN
Tạo trang Dashboard đồ họa tương tác cao với BẢNG MA TRẬN SO SÁNH TOÀN DIỆN hiển thị trực tiếp,
kèm Bảng theo dõi danh mục thực tế (TCB, DCM), biểu đồ Radar đa chiều, Kế hoạch kỷ luật vốn,
và TÍCH HỢP TÍNH NĂNG CHỌN XEM LẠI BÁO CÁO CŨ THEO TỪNG NGÀY (ARCHIVE VIEWER).
"""

import os
import sys
import json
import re
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
    top_stocks = results[:20]

    s_dict = {s['symbol']: s for s in results}
    radar_labels = ["Thanh khoản", "Xu hướng MA", "Dòng tiền lớn", "Độ siết nền", "Tỷ lệ R:R"]
    comparison_symbols = ["TCB", "DCM", "KBC", "HPG"]
    comparison_data = {}
    
    for sym in comparison_symbols:
        s = s_dict.get(sym)
        if s:
            liq_score = min(100, (s['val20_bil'] / 200) * 100)
            tr_score = 95 if s['dist_ma20'] >= 0 and s['dist_ma20'] <= 3 else (70 if s['dist_ma20'] > 3 else 40)
            mf_score = min(100, s['vol_ratio'] * 70)
            b_score = max(20, min(100, 100 - s['spread_5d'] * 10))
            rr_sc = min(100, (s['rr_ratio'] / 2.5) * 100)
            comparison_data[sym] = {
                'data': [round(liq_score), round(tr_score), round(mf_score), round(b_score), round(rr_sc)],
                'score': s['score']
            }
        else:
            comparison_data[sym] = {
                'data': [75, 75, 75, 75, 75],
                'score': 75
            }

    tcb_score = comparison_data['TCB']['score']
    dcm_score = comparison_data['DCM']['score']
    kbc_score = comparison_data['KBC']['score']
    hpg_score = comparison_data['HPG']['score']

    # Dữ liệu động cho Head-to-Head
    tcb_s = s_dict.get('TCB', {'score': 80, 'dist_ma20': 1.64, 'rsi': 58.5, 'val20_bil': 612.2, 'vol_ratio': 1.07})
    mbb_s = s_dict.get('MBB', {'score': 55, 'dist_ma20': -1.2, 'rsi': 46.5, 'val20_bil': 250.0, 'vol_ratio': 0.85})
    
    kbc_s = s_dict.get('KBC', {'score': 80, 'dist_ma20': 1.58, 'rsi': 52.9, 'val20_bil': 28.6, 'vol_ratio': 0.62, 'rr_ratio': 2.3})
    idc_s = s_dict.get('IDC', {'score': 60, 'dist_ma20': -0.4, 'rsi': 48.0, 'val20_bil': 35.0, 'vol_ratio': 0.75, 'rr_ratio': 1.8})
    
    dcm_s = s_dict.get('DCM', {'score': 80, 'dist_ma20': 2.1, 'rsi': 60.5, 'val20_bil': 120.0, 'vol_ratio': 1.15, 'rr_ratio': 2.4})
    dgc_s = s_dict.get('DGC', {'score': 48, 'dist_ma20': -6.2, 'rsi': 41.5, 'val20_bil': 95.0, 'vol_ratio': 0.70, 'rr_ratio': 1.2})

    def get_report_sort_key(filename):
        m = re.search(r"ban_tin_(sang|trua|chieu)_(\d{1,2})_(\d{1,2})_(\d{4})", filename)
        if m:
            sess, d, mth, y = m.groups()
            sess_order = {"chieu": 3, "trua": 2, "sang": 1}.get(sess, 0)
            return (datetime(int(y), int(mth), int(d)), sess_order)
        if "kich_ban" in filename:
            return (datetime(2026, 10, 14), 0.5)
        if "ket_qua" in filename:
            return (datetime(2026, 10, 14), 0.0)
        return (datetime(2020, 1, 1), 0)

    # Đọc kho báo cáo lịch sử theo ngày (sắp xếp từ gần nhất đến xa hơn)
    reports_dir = os.path.join(BASE_DIR, "reports")
    past_reports = {}
    if os.path.exists(reports_dir):
        md_files = [f for f in os.listdir(reports_dir) if f.endswith(".md")]
        for fname in sorted(md_files, key=get_report_sort_key, reverse=True):
            filepath = os.path.join(reports_dir, fname)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    md_text = f.read()
                if fname.startswith("ban_tin_sang_"):
                    parts = fname.replace("ban_tin_sang_", "").replace(".md", "").split("_")
                    date_label = f"{parts[0]}/{parts[1]}/{parts[2]}" if len(parts) == 3 else fname
                    display_name = f"Bản tin sáng {date_label}"
                elif fname.startswith("ban_tin_trua_"):
                    parts = fname.replace("ban_tin_trua_", "").replace(".md", "").split("_")
                    date_label = f"{parts[0]}/{parts[1]}/{parts[2]}" if len(parts) == 3 else fname
                    display_name = f"Bản tin trưa {date_label}"
                elif fname.startswith("ban_tin_chieu_"):
                    parts = fname.replace("ban_tin_chieu_", "").replace(".md", "").split("_")
                    date_label = f"{parts[0]}/{parts[1]}/{parts[2]}" if len(parts) == 3 else fname
                    display_name = f"Bản tin chiều {date_label}"
                elif "kich_ban" in fname:
                    display_name = "Kịch bản chiến lược 14/10"
                elif "ket_qua_loc" in fname:
                    display_name = "Kết quả bộ lọc cổ phiếu"
                else:
                    display_name = fname.replace(".md", "")
                
                past_reports[fname] = {
                    "name": display_name,
                    "content": md_text
                }
            except Exception:
                pass

    past_reports_json = json.dumps(past_reports, ensure_ascii=False)

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
    <!-- Marked.js (Markdown renderer) -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <!-- Auto-refresh every 5 minutes (300s) on browser -->
    <meta http-equiv="refresh" content="300">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .badge-buy {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.4); }}
        .badge-watch {{ background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); }}
        .badge-avoid {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); }}
        
        /* Markdown reader styles */
        #reportViewerContent table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 12px; }}
        #reportViewerContent th {{ background: #1e293b; padding: 10px 12px; border: 1px solid #334155; text-align: left; color: #94a3b8; font-weight: 700; }}
        #reportViewerContent td {{ padding: 10px 12px; border: 1px solid #334155; color: #e2e8f0; }}
        #reportViewerContent h1 {{ font-size: 20px; font-weight: 800; color: #fff; margin-bottom: 12px; }}
        #reportViewerContent h2 {{ font-size: 16px; font-weight: 700; color: #38bdf8; margin: 20px 0 10px 0; border-bottom: 1px solid #334155; padding-bottom: 6px; }}
        #reportViewerContent h3 {{ font-size: 14px; font-weight: 700; color: #6ee7b7; margin: 14px 0 6px 0; }}
        #reportViewerContent p, #reportViewerContent li {{ font-size: 13px; color: #cbd5e1; line-height: 1.6; margin: 6px 0; }}
        #reportViewerContent blockquote {{ border-left: 3px solid #10b981; background: rgba(16, 185, 129, 0.1); padding: 10px 14px; border-radius: 6px; margin: 12px 0; }}
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
                        BÁO CÁO ĐẦU NGÀY & BẢNG MA TRẬN SO SÁNH CỔ PHIẾU
                        <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Live Data</span>
                    </h1>
                    <p class="text-xs text-slate-400">Chiến lược Cân bằng Săn sóng ngành • Kế hoạch NAV 100.000.000 VNĐ • Cập nhật: {today_str}</p>
                </div>
            </div>

            <!-- CONTROLS & STATS PILLS -->
            <div class="flex items-center gap-3 flex-wrap">
                <!-- DROPDOWN CHỌN XEM LẠI NGÀY CŨ -->
                <div class="flex items-center gap-2 bg-indigo-950/60 border border-indigo-500/40 rounded-xl px-3 py-1.5 shadow-lg">
                    <i class="fa-solid fa-calendar-days text-indigo-400 text-xs"></i>
                    <select id="reportHistorySelect" onchange="openReportModal(this.value)" class="bg-transparent text-xs text-indigo-200 font-bold focus:outline-none cursor-pointer">
                        <option value="" class="bg-slate-900 text-slate-300">📅 Chọn ngày xem báo cáo cũ...</option>
                    </select>
                </div>

                <div class="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 flex items-center gap-2">
                    <span class="text-xs text-slate-400">VN-Index:</span>
                    <span class="text-sm font-bold text-amber-400">1.704,87</span>
                    <span class="text-xs text-rose-400 font-semibold"><i class="fa-solid fa-arrow-trend-down"></i> -0.85%</span>
                </div>
                <div class="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 flex items-center gap-2">
                    <span class="text-xs text-slate-400">Tiền mặt / CP:</span>
                    <span class="text-sm font-bold text-cyan-400">0tr (0%) / 102tr (100%)</span>
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
                <p class="text-xs text-slate-400 mt-3">Phân hóa mạnh mẽ. Dòng tiền gom mạnh ở nhóm Ngân hàng và Hóa chất.</p>
            </div>
            <!-- Card 2 -->
            <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 shadow-lg hover:border-slate-600 transition">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-slate-400">Danh Mục Đang Nắm Giữ</p>
                        <h3 class="text-lg font-bold text-emerald-400 mt-1">NBC, TCB, DCM</h3>
                    </div>
                    <span class="p-2 rounded-lg bg-emerald-500/10 text-emerald-400"><i class="fa-solid fa-bullseye"></i></span>
                </div>
                <p class="text-xs text-slate-400 mt-3">Khớp NBC 5.5k @ 8.30; TCB 900 @ 32.64; DCM 800 @ 33.30.</p>
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
                <p class="text-xs text-slate-400 mt-3">NBC cắt lỗ 7.90; TCB cắt lỗ 31.00; DCM cắt lỗ 31.65. Chạm -5% bán 1/2.</p>
            </div>
            <!-- Card 4 -->
            <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 shadow-lg hover:border-slate-600 transition">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-slate-400">Sức Mua Tiền Mặt</p>
                        <h3 class="text-lg font-bold text-cyan-400 mt-1">0 VNĐ (Full Cổ)</h3>
                    </div>
                    <span class="p-2 rounded-lg bg-cyan-500/10 text-cyan-400"><i class="fa-solid fa-wallet"></i></span>
                </div>
                <p class="text-xs text-slate-400 mt-3">Chiếm 0% NAV. Đã giải ngân đủ vị thế, tuyệt đối dừng mua mới.</p>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- 💼 2. BẢNG THEO DÕI DANH MỤC THỰC CHIẾN (ƯU TIÊN SỐ 1) -->
        <!-- ======================================================== -->
        <div class="bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-950/30 border border-emerald-500/30 rounded-2xl p-5 shadow-xl overflow-hidden">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4 pb-3 border-b border-emerald-500/20">
                <div>
                    <h2 class="text-base font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-wallet text-emerald-400"></i>
                        THEO DÕI VỊ THẾ DANH MỤC THỰC CHIẾN & KHUYẾN NGHỊ HÀNH ĐỘNG
                    </h2>
                    <p class="text-xs text-slate-400">Tổng tài sản NAV: 100.000.000 VNĐ • Đã giải ngân hoàn tất 100% NAV vào 3 mã chiến lược</p>
                </div>
                <div class="flex items-center gap-2 text-xs">
                    <span class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full font-bold">100% Cổ phiếu / 0% Tiền mặt</span>
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="border-b border-slate-700 bg-slate-900/80 text-slate-300 font-semibold uppercase tracking-wider">
                            <th class="py-3 px-3">Mã CP</th>
                            <th class="py-3 px-3">Khối lượng</th>
                            <th class="py-3 px-3">Giá vốn (k)</th>
                            <th class="py-3 px-3">Thị giá (k)</th>
                            <th class="py-3 px-3">Giá trị TT (VNĐ)</th>
                            <th class="py-3 px-3">Tỷ trọng NAV</th>
                            <th class="py-3 px-3">Lãi / Lỗ</th>
                            <th class="py-3 px-3">Tình trạng T+</th>
                            <th class="py-3 px-3 text-center">Khuyến nghị hành động dứt khoát</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800">
                        <!-- Row 1: NBC -->
                        <tr class="hover:bg-slate-800/40 transition">
                            <td class="py-3 px-3 font-bold text-white text-sm">
                                <span class="bg-amber-950/60 text-amber-300 px-2.5 py-1 rounded border border-amber-500/40 font-black">NBC</span>
                                <span class="text-[10px] text-slate-400 block mt-0.5">Than Núi Béo (HNX)</span>
                            </td>
                            <td class="py-3 px-3 font-bold text-white">5.500 cp</td>
                            <td class="py-3 px-3 font-semibold text-slate-300">8.30</td>
                            <td class="py-3 px-3 font-bold text-emerald-400">8.35</td>
                            <td class="py-3 px-3 font-bold text-white">45.925.000 đ</td>
                            <td class="py-3 px-3 font-semibold text-cyan-400">45.65%</td>
                            <td class="py-3 px-3 font-bold text-emerald-400">+0.60% (+275k)</td>
                            <td class="py-3 px-3 text-amber-300 font-medium">Khớp 16/10 (Chiều 20/10 về TK)</td>
                            <td class="py-3 px-3 text-center">
                                <span class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-3 py-1 rounded-full font-bold">
                                    <i class="fa-solid fa-lock mr-1"></i> TIẾP TỤC NẮM GIỮ
                                </span>
                                <span class="text-[10px] text-slate-400 block mt-1">Cắt lỗ: 7.90 (-5%) | Chốt lời: 9.10 - 9.60</span>
                            </td>
                        </tr>

                        <!-- Row 2: TCB -->
                        <tr class="hover:bg-slate-800/40 transition">
                            <td class="py-3 px-3 font-bold text-white text-sm">
                                <span class="bg-indigo-950/60 text-indigo-300 px-2.5 py-1 rounded border border-indigo-500/40 font-black">TCB</span>
                                <span class="text-[10px] text-slate-400 block mt-0.5">Ngân hàng</span>
                            </td>
                            <td class="py-3 px-3 font-bold text-white">900 cp</td>
                            <td class="py-3 px-3 font-semibold text-slate-300">32.64</td>
                            <td class="py-3 px-3 font-bold text-emerald-400">32.90</td>
                            <td class="py-3 px-3 font-bold text-white">29.610.000 đ</td>
                            <td class="py-3 px-3 font-semibold text-cyan-400">29.38%</td>
                            <td class="py-3 px-3 font-bold text-emerald-400">+0.80% (+234k)</td>
                            <td class="py-3 px-3 text-emerald-400 font-medium">Khớp 15/10 (Đã về TK - Sẵn sàng GD)</td>
                            <td class="py-3 px-3 text-center">
                                <span class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-3 py-1 rounded-full font-bold">
                                    <i class="fa-solid fa-lock mr-1"></i> TIẾP TỤC NẮM GIỮ
                                </span>
                                <span class="text-[10px] text-slate-400 block mt-1">Cắt lỗ: 31.00 (-5%) | Chốt lời: 35.9 - 38.0</span>
                            </td>
                        </tr>

                        <!-- Row 3: DCM -->
                        <tr class="hover:bg-slate-800/40 transition">
                            <td class="py-3 px-3 font-bold text-white text-sm">
                                <span class="bg-emerald-950/60 text-emerald-300 px-2.5 py-1 rounded border border-emerald-500/40 font-black">DCM</span>
                                <span class="text-[10px] text-slate-400 block mt-0.5">Hóa chất - Phân bón</span>
                            </td>
                            <td class="py-3 px-3 font-bold text-white">800 cp</td>
                            <td class="py-3 px-3 font-semibold text-slate-300">33.30</td>
                            <td class="py-3 px-3 font-bold text-emerald-400">33.60</td>
                            <td class="py-3 px-3 font-bold text-white">26.880.000 đ</td>
                            <td class="py-3 px-3 font-semibold text-cyan-400">26.64%</td>
                            <td class="py-3 px-3 font-bold text-emerald-400">+0.90% (+240k)</td>
                            <td class="py-3 px-3 text-emerald-400 font-medium">Khớp 15/10 (Đã về TK - Sẵn sàng GD)</td>
                            <td class="py-3 px-3 text-center">
                                <span class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-3 py-1 rounded-full font-bold">
                                    <i class="fa-solid fa-lock mr-1"></i> TIẾP TỤC NẮM GIỮ
                                </span>
                                <span class="text-[10px] text-slate-400 block mt-1">Cắt lỗ: 31.65 (-5%) | Chốt lời: 36.6 - 38.2</span>
                            </td>
                        </tr>

                        <!-- Row 4: TD6 -->
                        <tr class="hover:bg-slate-800/40 transition">
                            <td class="py-3 px-3 font-bold text-white text-sm">
                                <span class="bg-slate-800 text-slate-300 px-2.5 py-1 rounded border border-slate-700 font-bold">TD6</span>
                                <span class="text-[10px] text-slate-500 block mt-0.5">TC6 sáp nhập</span>
                            </td>
                            <td class="py-3 px-3 font-medium text-slate-400">300 cp</td>
                            <td class="py-3 px-3 font-semibold text-slate-300">6.13</td>
                            <td class="py-3 px-3 font-bold text-emerald-400">6.35</td>
                            <td class="py-3 px-3 font-bold text-white">1.905.000 đ</td>
                            <td class="py-3 px-3 font-semibold text-slate-400">~1.9%</td>
                            <td class="py-3 px-3 font-bold text-emerald-400">+3.59% (+66k)</td>
                            <td class="py-3 px-3 text-emerald-400 font-medium">Khả dụng ngay</td>
                            <td class="py-3 px-3 text-center">
                                <span class="bg-amber-500/20 text-amber-400 border border-amber-500/40 px-3 py-1 rounded-full font-bold">
                                    <i class="fa-solid fa-arrow-right-from-bracket mr-1"></i> CANH BÁN 6.4 - 6.5
                                </span>
                                <span class="text-[10px] text-slate-400 block mt-1">Chốt lời dọn gọn danh mục</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- 🏆 3. BẢNG MA TRẬN SO SÁNH TOÀN DIỆN CÁC CỔ PHIẾU (HIỂN THỊ TRỰC TIẾP) -->
        <!-- ======================================================== -->
        <div class="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5 shadow-xl overflow-hidden">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div>
                    <h2 class="text-base font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-table-list text-cyan-400"></i>
                        BẢNG MA TRẬN SO SÁNH CHỈ SỐ KỸ THUẬT & DÒNG TIỀN (TOP CỔ PHIẾU)
                    </h2>
                    <p class="text-xs text-slate-400">Trực quan hóa Điểm số, Vị thế giá vs MA20, Xung lực RSI, Khối lượng và Tỷ lệ Lợi nhuận/Rủi ro</p>
                </div>
                <!-- Search filter box -->
                <div class="flex items-center gap-3">
                    <div class="relative">
                        <i class="fa-solid fa-search absolute left-3 top-2.5 text-xs text-slate-400"></i>
                        <input type="text" id="filterInput" onkeyup="filterStockTable()" placeholder="Lọc nhanh mã CP..." class="bg-slate-900 border border-slate-600 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400 w-44">
                    </div>
                    <div class="flex items-center gap-2 text-xs">
                        <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-emerald-500"></span> >=75: Mua</span>
                        <span class="flex items-center gap-1 ml-1"><span class="h-2 w-2 rounded-full bg-amber-500"></span> 60-74: Canh</span>
                        <span class="flex items-center gap-1 ml-1"><span class="h-2 w-2 rounded-full bg-rose-500"></span> &lt;55: Né</span>
                    </div>
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse" id="matrixTable">
                    <thead>
                        <tr class="border-b border-slate-700 bg-slate-900/80 text-slate-300 font-semibold uppercase tracking-wider">
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

        dist = s['dist_ma20']
        dist_color = "text-emerald-400" if dist >= 0 and dist <= 3.5 else ("text-amber-400" if dist > 3.5 else "text-rose-400")

        chg = s['pct_change']
        chg_color = "text-emerald-400 font-bold" if chg > 0 else ("text-rose-400 font-bold" if chg < 0 else "text-amber-300")

        html += f"""
                        <tr class="hover:bg-slate-800/40 transition stock-row">
                            <td class="py-3 px-3 font-bold text-slate-400">#{i}</td>
                            <td class="py-3 px-3 font-bold text-white text-sm stock-sym">
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

        <!-- 4. SO SÁNH ĐA CHIỀU (RADAR CHART TỔNG THỂ & HEAD-TO-HEAD BATTLE) -->
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
                        <span class="text-xs font-semibold text-indigo-400 block">TCB</span>
                        <span class="text-sm font-bold text-white">{tcb_score} đ</span>
                    </div>
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-emerald-500/30">
                        <span class="text-xs font-semibold text-emerald-400 block">DCM</span>
                        <span class="text-sm font-bold text-white">{dcm_score} đ</span>
                    </div>
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-amber-500/30">
                        <span class="text-xs font-semibold text-amber-400 block">KBC</span>
                        <span class="text-sm font-bold text-white">{kbc_score} đ</span>
                    </div>
                    <div class="bg-slate-900/60 p-2 rounded-lg border border-cyan-500/30">
                        <span class="text-xs font-semibold text-cyan-400 block">HPG</span>
                        <span class="text-sm font-bold text-white">{hpg_score} đ</span>
                    </div>
                </div>
            </div>

            <!-- Head-to-Head Battle -->
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
                            <span class="text-xs text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Chọn TCB ({tcb_s['score']}đ) > MBB ({mbb_s['score']}đ)</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3 mt-2 text-xs">
                            <div class="bg-emerald-950/30 border border-emerald-800/40 p-2 rounded">
                                <span class="font-bold text-emerald-300">✅ TCB (Đã khớp 900 cp):</span> Vị thế {f"+{tcb_s['dist_ma20']:.2f}% vs MA20" if tcb_s['dist_ma20'] >= 0 else f"{tcb_s['dist_ma20']:.2f}% vs MA20"}, RSI {tcb_s['rsi']:.1f} ({'xung lực khỏe' if tcb_s['rsi'] >= 50 else 'xung lực yếu'}), thanh khoản dẫn đầu {tcb_s['val20_bil']:.0f} tỷ/phiên.
                            </div>
                            <div class="bg-slate-800/40 border border-slate-700/50 p-2 rounded text-slate-400">
                                <span class="font-bold text-slate-300">⚠️ MBB:</span> Vị thế {f"+{mbb_s['dist_ma20']:.2f}% vs MA20" if mbb_s['dist_ma20'] >= 0 else f"{mbb_s['dist_ma20']:.2f}% vs MA20"}, RSI {mbb_s['rsi']:.1f}, thanh khoản {mbb_s['val20_bil']:.0f} tỷ/phiên, cần tích lũy thêm.
                            </div>
                        </div>
                    </div>

                    <!-- Battle 2: KBC vs IDC -->
                    <div class="bg-slate-900/80 rounded-xl p-3 border border-slate-700/60 hover:border-slate-600 transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400">BĐS KHU CÔNG NGHIỆP</span>
                            <span class="text-xs text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Chọn KBC ({kbc_s['score']}đ) > IDC ({idc_s['score']}đ)</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3 mt-2 text-xs">
                            <div class="bg-emerald-950/30 border border-emerald-800/40 p-2 rounded">
                                <span class="font-bold text-emerald-300">✅ KBC:</span> Vị thế {f"+{kbc_s['dist_ma20']:.2f}% vs MA20" if kbc_s['dist_ma20'] >= 0 else f"{kbc_s['dist_ma20']:.2f}% vs MA20"}, RSI {kbc_s['rsi']:.1f}, Vol {kbc_s['vol_ratio']:.2f}x, R:R hấp dẫn {kbc_s.get('rr_ratio', 2.3):.1f}:1.
                            </div>
                            <div class="bg-slate-800/40 border border-slate-700/50 p-2 rounded text-slate-400">
                                <span class="font-bold text-slate-300">⚠️ IDC:</span> Vị thế {f"+{idc_s['dist_ma20']:.2f}% vs MA20" if idc_s['dist_ma20'] >= 0 else f"{idc_s['dist_ma20']:.2f}% vs MA20"}, RSI {idc_s['rsi']:.1f}, áp lực cung bán cần hấp thụ thêm.
                            </div>
                        </div>
                    </div>

                    <!-- Battle 3: DCM vs DGC -->
                    <div class="bg-slate-900/80 rounded-xl p-3 border border-slate-700/60 hover:border-slate-600 transition">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">NHÓM HÓA CHẤT / PHÂN BÓN</span>
                            <span class="text-xs text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Chọn DCM ({dcm_s['score']}đ) > DGC ({dgc_s['score']}đ)</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3 mt-2 text-xs">
                            <div class="bg-emerald-950/30 border border-emerald-800/40 p-2 rounded">
                                <span class="font-bold text-emerald-300">✅ DCM (Đã khớp 800 cp):</span> Vị thế {f"+{dcm_s['dist_ma20']:.2f}% vs MA20" if dcm_s['dist_ma20'] >= 0 else f"{dcm_s['dist_ma20']:.2f}% vs MA20"}, RSI {dcm_s['rsi']:.1f}, R:R {dcm_s.get('rr_ratio', 2.4):.1f}:1, giữ vững kênh uptrend.
                            </div>
                            <div class="bg-slate-800/40 border border-slate-700/50 p-2 rounded text-slate-400">
                                <span class="font-bold text-rose-400">⛔ DGC:</span> Vị thế {f"+{dgc_s['dist_ma20']:.2f}% vs MA20" if dgc_s['dist_ma20'] >= 0 else f"{dgc_s['dist_ma20']:.2f}% vs MA20"}, RSI {dgc_s['rsi']:.1f}, dòng tiền tổ chức còn thận trọng.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 5. KỶ LUẬT CẮT LỖ & BẢO VỆ VỐN -->
        <div class="bg-gradient-to-br from-slate-900 via-slate-800 to-rose-950/30 border border-rose-500/30 rounded-2xl p-5 shadow-xl">
            <div class="flex items-center justify-between mb-4 pb-3 border-b border-rose-500/20">
                <div class="flex items-center gap-3">
                    <div class="p-2.5 bg-rose-500/20 text-rose-400 rounded-xl">
                        <i class="fa-solid fa-hand-holding-dollar text-lg"></i>
                    </div>
                    <div>
                        <h3 class="text-base font-bold text-white">KỶ LUẬT CẮT LỖ & BẢO VỆ VỐN (QUY TẮC BẤT BIẾN)</h3>
                        <p class="text-xs text-slate-400">Nguyên tắc sống còn: Luôn giữ sụt giảm vốn Max Drawdown &lt; 6% toàn danh mục</p>
                    </div>
                </div>
                <span class="text-xs font-bold px-2.5 py-1 bg-rose-500 text-white rounded-full">Không Ngoại Lệ</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <!-- Rule 1 -->
                <div class="flex items-start gap-3 bg-slate-900/80 p-3 rounded-xl border border-rose-500/20">
                    <div class="h-6 w-6 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">1</div>
                    <div>
                        <span class="font-bold text-white text-sm">Chạm ngưỡng -5.0%: Bán ngay 1/2 vị thế</span>
                        <p class="text-slate-400 mt-1">Khi cổ phiếu mua về lỗ 5%, lập tức bán 50% số lượng đang giữ để đưa tài khoản về vị thế an toàn. Không chờ hết phiên.</p>
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
            </div>
        </div>

    </main>

    <!-- REPORT VIEWER MODAL (POPUP XEM BÁO CÁO CŨ) -->
    <div id="reportModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
            <div class="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/80">
                <div class="flex items-center gap-2">
                    <i class="fa-solid fa-book-open text-indigo-400"></i>
                    <h3 class="font-bold text-white text-sm" id="modalReportTitle">Báo cáo lịch sử</h3>
                </div>
                <button onclick="closeReportModal()" class="text-slate-400 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-bold transition">
                    <i class="fa-solid fa-xmark mr-1"></i> Đóng lại
                </button>
            </div>
            <div class="p-6 overflow-y-auto space-y-4" id="reportViewerContent">
                <!-- Nội dung Markdown sẽ được render tại đây -->
            </div>
        </div>
    </div>

    <!-- FOOTER -->
    <footer class="text-center text-xs text-slate-500 pt-8 border-t border-slate-800 mt-12">
        Hệ thống Tự động hóa Phân tích & Đánh giá Cổ phiếu • Đồng hành kế hoạch NAV 100tr • Cập nhật: {today_str}
    </footer>

    <!-- JAVASCRIPT LOGIC -->
    <script>
        const PAST_REPORTS = {past_reports_json};

        // Khởi tạo danh sách ngày vào Dropdown
        const reportSelect = document.getElementById("reportHistorySelect");
        for (const [fname, rdata] of Object.entries(PAST_REPORTS)) {{
            const opt = document.createElement("option");
            opt.value = fname;
            opt.textContent = `📅 ${{rdata.name}}`;
            opt.className = "bg-slate-900 text-slate-100";
            reportSelect.appendChild(opt);
        }}

        // Hàm mở Popup xem báo cáo cũ
        function openReportModal(fname) {{
            if (!fname || !PAST_REPORTS[fname]) return;
            const rdata = PAST_REPORTS[fname];
            document.getElementById("modalReportTitle").textContent = rdata.name;
            document.getElementById("reportViewerContent").innerHTML = marked.parse(rdata.content);
            document.getElementById("reportModal").classList.remove("hidden");
            reportSelect.value = ""; // reset dropdown
        }}

        // Đóng Popup
        function closeReportModal() {{
            document.getElementById("reportModal").classList.add("hidden");
        }}

        // Đóng khi bấm ra ngoài hoặc phím ESC
        window.addEventListener("keydown", (e) => {{
            if (e.key === "Escape") closeReportModal();
        }});
        document.getElementById("reportModal").addEventListener("click", (e) => {{
            if (e.target.id === "reportModal") closeReportModal();
        }});

        // Bộ lọc nhanh trên Bảng ma trận
        function filterStockTable() {{
            const input = document.getElementById("filterInput");
            const filter = input.value.toUpperCase();
            const rows = document.querySelectorAll("#matrixTable tbody tr.stock-row");

            rows.forEach(row => {{
                const sym = row.querySelector(".stock-sym").textContent.trim();
                const sector = row.children[2].textContent.trim();
                if (sym.toUpperCase().indexOf(filter) > -1 || sector.toUpperCase().indexOf(filter) > -1) {{
                    row.style.display = "";
                }} else {{
                    row.style.display = "none";
                }}
            }});
        }}

        // Biểu đồ Radar 4 trụ cột
        const ctx = document.getElementById('radarChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: {json.dumps(radar_labels, ensure_ascii=False)},
                datasets: [
                    {{
                        label: 'DCM ({dcm_score}đ)',
                        data: {comparison_data.get('DCM', {}).get('data', [80, 90, 80, 85, 90])},
                        backgroundColor: 'rgba(16, 185, 129, 0.25)',
                        borderColor: '#10b981',
                        borderWidth: 2,
                        pointBackgroundColor: '#10b981'
                    }},
                    {{
                        label: 'TCB ({tcb_score}đ)',
                        data: {comparison_data.get('TCB', {}).get('data', [95, 85, 75, 75, 70])},
                        backgroundColor: 'rgba(99, 102, 241, 0.25)',
                        borderColor: '#6366f1',
                        borderWidth: 2,
                        pointBackgroundColor: '#6366f1'
                    }},
                    {{
                        label: 'KBC ({kbc_score}đ)',
                        data: {comparison_data.get('KBC', {}).get('data', [65, 80, 70, 85, 95])},
                        backgroundColor: 'rgba(245, 158, 11, 0.25)',
                        borderColor: '#f59e0b',
                        borderWidth: 2,
                        pointBackgroundColor: '#f59e0b'
                    }},
                    {{
                        label: 'HPG ({hpg_score}đ)',
                        data: {comparison_data.get('HPG', {}).get('data', [85, 70, 75, 80, 80])},
                        backgroundColor: 'rgba(6, 182, 212, 0.25)',
                        borderColor: '#06b6d4',
                        borderWidth: 2,
                        pointBackgroundColor: '#06b6d4'
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
