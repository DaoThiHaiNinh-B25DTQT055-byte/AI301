"""
====================================================================================================
MINH AN TECHNOLOGY JSC • ENTERPRISE B2B SALES AI & STATISTICAL OPERATIONS CENTER
HIGH-END SAAS EDITION 2026 (UNIVERSAL FILE READER • 8-STEP ANALYTICS • AUDIT TRAIL LOG)
====================================================================================================
"""

import os
import io
import re
import json
import importlib
from datetime import datetime
from textwrap import dedent
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import streamlit as st

# Cấu hình cho phép xử lý và hiển thị bảng dữ liệu cực lớn (hàng triệu ô)
pd.set_option("styler.render.max_elements", 10_000_000)

import config
from file_reader import UniversalFileReader
import data_cleaning
importlib.reload(data_cleaning)
from data_cleaning import DataQualityCleaner, DataValidationGuardrail
from analytics_engine import StatisticalAnalyticsEngine
import business_report
importlib.reload(business_report)
from business_report import DynamicBusinessReportGenerator, export_report_to_word
from agent_core import DataLoader, MinhAnSalesAgent
import styles
importlib.reload(styles)
from styles import get_app_styles, clean_html

import translations
importlib.reload(translations)
from translations import t
from icons import get_svg_icon, get_icon_tile
import charts
importlib.reload(charts)
from charts import (
    chart_mini_sparkline,
    chart_opportunity_item_values,
    chart_opportunity_category_donut,
    chart_opportunity_inventory_comparison,
    chart_governance_gauges,
    render_governance_card,
    chart_leadtime_timeline,
    chart_batch_outcome_donut,
    chart_batch_sales_rep_workload,
    chart_pipeline_funnel,
    chart_operational_risk_bottlenecks,
    chart_sales_team_performance,
    chart_batch_order_value_distribution,
    chart_catalog_top_stock,
    chart_catalog_price_vs_stock_scatter,
    chart_catalog_category_breakdown,
    chart_catalog_low_stock_alerts,
    chart_data_quality_missing_bars,
    chart_dynamic_builder,
    chart_report_kpi_comparison,
    chart_report_thematic_distribution,
    chart_report_group_breakdown,
    render_chart_card
)

# ====================================================================================================
# 1. CẤU HÌNH TRANG WEB
# ====================================================================================================
st.set_page_config(
    page_title="Minh An AI Agent • Enterprise B2B Sales & Analytics Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo trạng thái Session State
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "lang" not in st.session_state:
    st.session_state.lang = "vi"

is_dark = st.session_state.dark_mode
lang = st.session_state.lang

# ====================================================================================================
# 2. INJECT CSS TỪ STYLES.PY (CHUẨN SAAS CAO CẤP 2026) & CHỐNG LỖI REACT INSERTBEFORE DO GOOGLE TRANSLATE
# ====================================================================================================
import streamlit.components.v1 as components

clean_app_css = clean_html(get_app_styles(is_dark))
st.markdown(f"<style>{clean_app_css}\n.notranslate, [translate='no'] {{ translate: no !important; }}</style>", unsafe_allow_html=True)

# Khóa thuộc tính translate ở cấp HTML/Body gốc để ngăn Google Chrome Auto-Translate làm đột biến DOM cây React
components.html("""
<script>
    try {
        const doc = window.parent.document;
        doc.documentElement.setAttribute('lang', 'vi');
        doc.documentElement.setAttribute('translate', 'no');
        doc.documentElement.classList.add('notranslate');
        if (doc.body) {
            doc.body.setAttribute('translate', 'no');
            doc.body.classList.add('notranslate');
        }
        let meta = doc.querySelector('meta[name="google"]');
        if (!meta) {
            meta = doc.createElement('meta');
            meta.name = 'google';
            meta.content = 'notranslate';
            doc.head.appendChild(meta);
        }
    } catch(e) {}
</script>
""", height=0)

# ====================================================================================================
# 3. KHỞI TẠO DỮ LIỆU & SESSION STATE (CÓ BẢO VỆ CACHE AN TOÀN)
# ====================================================================================================
if (
    "catalog_df" not in st.session_state 
    or "agent" not in st.session_state 
    or not hasattr(st.session_state.agent, "get_api_status")
    or not hasattr(st.session_state.agent, "process_batch")
):
    p_df, s_df, pol_df = DataLoader.load_default_data()
    st.session_state.catalog_df = p_df
    st.session_state.sales_df = s_df
    st.session_state.policy_df = pol_df
    st.session_state.agent = MinhAnSalesAgent(p_df, s_df, pol_df)

if "pipeline_history" not in st.session_state:
    st.session_state.pipeline_history = []

if "copilot_history" not in st.session_state:
    st.session_state.copilot_history = {}

if "wf_active_step" not in st.session_state:
    st.session_state.wf_active_step = 1

if "wf_view_mode" not in st.session_state:
    st.session_state.wf_view_mode = "wizard"

if "assigned_rep_name" not in st.session_state:
    st.session_state.assigned_rep_name = None

if "assigned_follower_name" not in st.session_state:
    st.session_state.assigned_follower_name = "Nguyễn Thị Thảo (Trợ lý Ban Kinh doanh)"

if "manager_decision" not in st.session_state:
    st.session_state.manager_decision = None

if "manager_feedback_note" not in st.session_state:
    st.session_state.manager_feedback_note = ""

if "uploaded_analytics_df" not in st.session_state:
    st.session_state.uploaded_analytics_df = None

if "schema_mapping" not in st.session_state:
    st.session_state.schema_mapping = {}

if "data_quality_report" not in st.session_state:
    st.session_state.data_quality_report = None

if "uploaded_file_invalid" not in st.session_state:
    st.session_state.uploaded_file_invalid = False

if "has_quantitative_metrics" not in st.session_state:
    st.session_state.has_quantitative_metrics = True


def get_safe_api_status() -> Dict[str, Any]:
    """Lấy trạng thái Gemini API an toàn, tự động tái tạo agent nếu phiên làm việc cũ thiếu phương thức."""
    if (
        "agent" not in st.session_state 
        or not hasattr(st.session_state.agent, "get_api_status")
        or not hasattr(st.session_state.agent, "process_batch")
        or "catalog_df" not in st.session_state
    ):
        p_df, s_df, pol_df = DataLoader.load_default_data()
        st.session_state.catalog_df = p_df
        st.session_state.sales_df = s_df
        st.session_state.policy_df = pol_df
        st.session_state.agent = MinhAnSalesAgent(p_df, s_df, pol_df)
    
    try:
        return st.session_state.agent.get_api_status()
    except Exception:
        return {
            "active": False,
            "model": "Rule-based Engine (Offline Fallback)",
            "masked_key": "Chưa cấu hình",
            "description": "Đang chạy chế độ quy tắc nội bộ"
        }

def render_safe_dataframe(
    df: Optional[pd.DataFrame], 
    num_formats: Optional[Dict[str, str]] = None, 
    width: str = "stretch", 
    hide_index: bool = True
):
    """
    Hiển thị DataFrame an toàn tuyệt đối cho mọi kích thước dữ liệu (từ nhỏ đến hàng trăm nghìn / hàng triệu ô).
    Sử dụng trực tiếp st.column_config thay vì Pandas Styler để triệt tiêu vĩnh viễn lỗi styler.render.max_elements.
    Hỗ trợ ảo hóa cuộn siêu tốc và định dạng tiền tệ / số trực tiếp.
    """
    if df is None or df.empty:
        st.info("Không có dữ liệu để hiển thị.")
        return
        
    col_cfg = {}
    if num_formats:
        for col_name, fmt in num_formats.items():
            if col_name in df.columns:
                std_fmt = fmt.replace("{:", "%").replace("}", "") if "{:" in fmt else fmt
                col_cfg[col_name] = st.column_config.NumberColumn(format=std_fmt)
                
    try:
        st.dataframe(
            df,
            column_config=col_cfg if col_cfg else None,
            width=width,
            hide_index=hide_index
        )
    except Exception:
        st.dataframe(df, width=width, hide_index=hide_index)

# Kiểm tra trạng thái Gemini AI
api_info = get_safe_api_status()

# ====================================================================================================
# 4. TOP NAVBAR STICKY (72PX, GLASSMORPHISM, BRAND, MODEL CHIP, LANG & THEME PILL)
# ====================================================================================================
with st.container(key="minhan_header"):
    col_brand, col_status, col_lang, col_theme = st.columns([4.6, 2.8, 1.2, 1.4], vertical_alignment="center")
    
    with col_brand:
        zap_svg = get_svg_icon("zap", size=22, color="#ffffff")
        st.markdown(clean_html(f"""
        <div class="brand-wrapper">
            <div class="brand-icon-box">{zap_svg}</div>
            <div>
                <div class="brand-title-text">{t("app_brand", lang)}</div>
                <div class="brand-caption-text">{t("app_subtitle", lang)}</div>
            </div>
        </div>
        """), unsafe_allow_html=True)
        
    with col_status:
        st.markdown(clean_html(f"""
        <div class="model-status-chip">
            <div class="pulsing-emerald-dot"></div>
            <span>{t("live_ai_online", lang) if api_info.get("active") else t("live_rules_online", lang)}</span>
        </div>
        """), unsafe_allow_html=True)
        
    with col_lang:
        selected_lang = st.segmented_control(
            "Language",
            options=["VI", "EN"],
            default=st.session_state.lang.upper(),
            label_visibility="collapsed"
        )
        if selected_lang and selected_lang.lower() != st.session_state.lang:
            st.session_state.lang = selected_lang.lower()
            st.rerun()
            
    with col_theme:
        # Nút chuyển Sáng/Tối dạng 1 pill duy nhất, đổi icon ☀️ ↔ 🌙
        theme_label = "☀️ Sáng" if is_dark else "🌙 Tối"
        if st.button(theme_label, key="theme_toggle_btn", use_container_width=True):
            st.session_state.dark_mode = not is_dark
            st.rerun()

# ====================================================================================================
# 5. HERO SECTION CAO CẤP (BENTO MESH, GRADIENT SHIMMER & 4 MICRO KPI)
# ====================================================================================================
users_svg = get_svg_icon("users", size=18, color="#6366f1")
layers_svg = get_svg_icon("layers", size=18, color="#06b6d4")
clock_svg = get_svg_icon("clock", size=18, color="#ec4899")
check_svg = get_svg_icon("check_circle", size=18, color="#10b981")
spark_svg = get_svg_icon("sparkles", size=14, color="#6366f1")

st.markdown(clean_html(f"""
<div class="hero-saas-card">
    <div class="hero-top-badge">{spark_svg} {t("hero_tag", lang)}</div>
    <div class="hero-main-title">{t("hero_title_1", lang)} <span class="gradient-shimmer-text">{t("hero_title_2", lang)}</span></div>
    <div class="hero-desc-text">{t("hero_desc", lang)}</div>
    <div class="hero-kpi-grid">
        <div class="hero-kpi-tile">
            <div style="background: rgba(99, 102, 241, 0.12); padding: 10px; border-radius: 12px; display: flex;">{users_svg}</div>
            <div>
                <div class="hero-kpi-num">{t("hero_kpi_1_num", lang)}</div>
                <div class="hero-kpi-lbl">{t("hero_kpi_1_lbl", lang)}</div>
            </div>
        </div>
        <div class="hero-kpi-tile">
            <div style="background: rgba(6, 182, 212, 0.12); padding: 10px; border-radius: 12px; display: flex;">{layers_svg}</div>
            <div>
                <div class="hero-kpi-num">{t("hero_kpi_2_num", lang)}</div>
                <div class="hero-kpi-lbl">{t("hero_kpi_2_lbl", lang)}</div>
            </div>
        </div>
        <div class="hero-kpi-tile">
            <div style="background: rgba(236, 72, 153, 0.12); padding: 10px; border-radius: 12px; display: flex;">{clock_svg}</div>
            <div>
                <div class="hero-kpi-num">{t("hero_kpi_3_num", lang)}</div>
                <div class="hero-kpi-lbl">{t("hero_kpi_3_lbl", lang)}</div>
            </div>
        </div>
        <div class="hero-kpi-tile">
            <div style="background: rgba(16, 185, 129, 0.12); padding: 10px; border-radius: 12px; display: flex;">{check_svg}</div>
            <div>
                <div class="hero-kpi-num">{t("hero_kpi_4_num", lang)}</div>
                <div class="hero-kpi-lbl">{t("hero_kpi_4_lbl", lang)}</div>
            </div>
        </div>
    </div>
</div>
"""), unsafe_allow_html=True)

# ====================================================================================================
# 5.5. HÀNG THẺ TỔNG QUAN METRICS KÈM BIỂU ĐỒ SPARKLINE TƯƠNG TÁC
# (Ưu tiên: Kiểm soát quy trình E2E -> Độ chính xác đề xuất -> Điểm nghẽn vận hành -> Tiến độ tuần & Doanh thu)
# ====================================================================================================
pipeline_sum = sum(item.get("TotalAmount", 0) for item in st.session_state.pipeline_history)
if "current_result" in st.session_state and st.session_state.current_result:
    cur_eval = st.session_state.current_result.get("evaluation") or {}
    pipeline_sum += cur_eval.get("total_final_amount", 0)
if pipeline_sum == 0:
    pipeline_sum = 582_500_000

total_requests_count = len(st.session_state.pipeline_history) + (1 if ("current_result" in st.session_state and st.session_state.current_result) else 0)
if total_requests_count == 0:
    total_requests_count = 6

auto_approved_count = sum(1 for item in st.session_state.pipeline_history if "NVKD" in str(item.get("Approval", "")) or "Tự duyệt" in str(item.get("Approval", "")))
if "current_result" in st.session_state and st.session_state.current_result:
    cur_eval = st.session_state.current_result.get("evaluation") or {}
    if not cur_eval.get("needs_manager_approval", True):
        auto_approved_count += 1
auto_rate = (auto_approved_count / total_requests_count * 100) if total_requests_count > 0 else 66.7
escalated_count = max(0, total_requests_count - auto_approved_count)

st.markdown(clean_html(f"""
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 14px; margin-bottom: 20px;">
    <!-- Khối 1: Tỷ lệ Tạo Hồ sơ & Dự thảo Hoàn chỉnh -->
    <div style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 16px; padding: 18px 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: space-between;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-size: 13px; font-weight: 600; color: var(--text-muted, #64748b);">{t("overview_kpi_completion", lang)}</span>
            <div style="background: rgba(16, 185, 129, 0.12); width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">{get_svg_icon("check_circle", size=18, color="#10B981")}</div>
        </div>
        <div style="font-size: 28px; font-weight: 800; color: #10B981; letter-spacing: -0.5px; margin-bottom: 10px;">100%</div>
        <div style="background: rgba(16, 185, 129, 0.08); border-radius: 8px; padding: 6px 10px; font-size: 12px; font-weight: 600; color: #059669; display: flex; align-items: center; gap: 6px;">
            <span>↑</span> {t("overview_kpi_completion_sub", lang)}
        </div>
    </div>

    <!-- Khối 2: Tỷ lệ Đề xuất Đạt chuẩn Vận hành -->
    <div style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 16px; padding: 18px 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: space-between;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-size: 13px; font-weight: 600; color: var(--text-muted, #64748b);">{t("overview_kpi_quality", lang)}</span>
            <div style="background: rgba(99, 102, 241, 0.12); width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">{get_svg_icon("shield_check", size=18, color="#6366F1")}</div>
        </div>
        <div style="font-size: 28px; font-weight: 800; color: #6366F1; letter-spacing: -0.5px; margin-bottom: 10px;">100%</div>
        <div style="background: rgba(99, 102, 241, 0.08); border-radius: 8px; padding: 6px 10px; font-size: 12px; font-weight: 600; color: #4F46E5; display: flex; align-items: center; gap: 6px;">
            <span>✓</span> {t("overview_kpi_quality_sub", lang)}
        </div>
    </div>

    <!-- Khối 3: Cảnh báo Điểm nghẽn & Cần duyệt -->
    <div style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 16px; padding: 18px 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: space-between;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-size: 13px; font-weight: 600; color: var(--text-muted, #64748b);">{t("overview_kpi_bottlenecks", lang)}</span>
            <div style="background: rgba(245, 158, 11, 0.12); width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">{get_svg_icon("alert_triangle", size=18, color="#D97706")}</div>
        </div>
        <div style="font-size: 28px; font-weight: 800; color: #D97706; letter-spacing: -0.5px; margin-bottom: 10px;">{escalated_count} Ca Chờ Duyệt</div>
        <div style="background: rgba(245, 158, 11, 0.08); border-radius: 8px; padding: 6px 10px; font-size: 12px; font-weight: 600; color: #B45309; display: flex; align-items: center; gap: 6px;">
            <span>⚡</span> Tự quyết {auto_rate:.0f}% • {t("overview_kpi_bottlenecks_sub", lang)}
        </div>
    </div>

    <!-- Khối 4: Tiến độ Khối lượng Tuần (~180 Req) -->
    <div style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 16px; padding: 18px 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: space-between;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-size: 13px; font-weight: 600; color: var(--text-muted, #64748b);">{t("overview_kpi_weekly_target", lang)}</span>
            <div style="background: rgba(6, 182, 212, 0.12); width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">{get_svg_icon("layers", size=18, color="#0284C7")}</div>
        </div>
        <div style="font-size: 28px; font-weight: 800; color: #0284C7; letter-spacing: -0.5px; margin-bottom: 10px;">{total_requests_count} / 180 Req</div>
        <div style="background: rgba(6, 182, 212, 0.08); border-radius: 8px; padding: 6px 10px; font-size: 12px; font-weight: 600; color: #0369A1; display: flex; align-items: center; gap: 6px;">
            <span>📊</span> Pipeline: {pipeline_sum:,.0f} ₫
        </div>
    </div>
</div>
"""), unsafe_allow_html=True)

# ====================================================================================================
# 6. TABS ĐIỀU HƯỚNG CHÍNH (5 TABS STICKY Ở ĐẦU TRANG)
# ====================================================================================================
tab_analytics, tab_single, tab_batch, tab_catalog, tab_settings = st.tabs([
    t("tab_analytics", lang),
    t("tab_single", lang),
    t("tab_batch", lang),
    t("tab_catalog", lang),
    t("tab_settings", lang)
])

# ====================================================================================================
# TAB 1: XỬ LÝ YÊU CẦU ĐƠN LẺ — QUY TRÌNH 6 BƯỚC XUYÊN SUỐT CÔNG TY MINH AN
# ====================================================================================================
with tab_single:
    sample_requests_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_requests.json")
    with open(sample_requests_file, encoding="utf-8") as f:
        sample_requests = json.load(f)
        
    sample_options = [t("sample_select_default", lang)] + [
        f"{s['id']}: {s['title']}" for s in sample_requests
    ]
    
    # ------------------------------------------------------------------------------------------------
    # THANH ĐIỀU HƯỚNG CHẾ ĐỘ XEM & THÔNG TIN BỐI CẢNH VẬN HÀNH
    # ------------------------------------------------------------------------------------------------
    col_vm_info, col_vm_toggle = st.columns([6.2, 3.8], vertical_alignment="center")
    with col_vm_info:
        st.markdown(clean_html(f"""
        <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 8px;">
            🏢 <b>Minh An B2B Sales Workflow</b>: 6 NVKD tiếp nhận ~180 yêu cầu/tuần • Kiểm soát 4 điểm nghẽn: <i>Không bỏ sót hạng mục, Chặn dùng giá cũ, Thẩm định SLA kho khả dụng, Định danh NVKD & Người theo dõi</i>.
        </div>
        """), unsafe_allow_html=True)
    with col_vm_toggle:
        view_mode_opts = [t("wizard_mode_label", lang), t("overview_mode_label", lang)]
        curr_mode_idx = 0 if st.session_state.wf_view_mode == "wizard" else 1
        sel_view_mode = st.segmented_control(
            "Chế độ hiển thị quy trình",
            options=view_mode_opts,
            default=view_mode_opts[curr_mode_idx],
            label_visibility="collapsed",
            key="segmented_view_mode"
        )
        if sel_view_mode:
            new_vm = "wizard" if ("Wizard" in sel_view_mode or "Từng bước" in sel_view_mode) else "overview"
            if new_vm != st.session_state.wf_view_mode:
                st.session_state.wf_view_mode = new_vm
                st.rerun()

    # ------------------------------------------------------------------------------------------------
    # TÍNH TOÁN TRẠNG THÁI STEPPER THEO TIẾN TRÌNH THỰC TẾ
    # ------------------------------------------------------------------------------------------------
    active_step = st.session_state.get("wf_active_step", 1)
    cur_res = st.session_state.get("current_result")
    
    # Đảm bảo có kết quả mẫu mặc định nếu mở lần đầu
    if cur_res is None:
        default_sample_text = sample_requests[0]["raw_text"]
        st.session_state.current_result = st.session_state.agent.process_request(default_sample_text)
        cur_res = st.session_state.current_result
        if cur_res and cur_res.get("sales_rep"):
            st.session_state.assigned_rep_name = cur_res["sales_rep"]["FullName"]

    is_sufficient = (cur_res.get("parsed_request") or {}).get("is_sufficient", True) if cur_res else True
    needs_appr = (cur_res.get("evaluation") or {}).get("needs_manager_approval", False) if cur_res else False
    
    # Tính icon & class cho 6 bước + nhánh duyệt
    c_list = ["idle"] * 7  # 1, 2, 3, 4, 5, appr, 6
    n_list = ["1", "2", "3", "4", "5", "—", "6"]
    
    for s_i in range(1, 7):
        idx = s_i - 1 if s_i <= 5 else 6
        if s_i < active_step:
            c_list[idx] = "completed"
            n_list[idx] = "✓"
        elif s_i == active_step:
            c_list[idx] = "active"
            n_list[idx] = str(s_i)
        else:
            c_list[idx] = "idle"
            n_list[idx] = str(s_i)
            
    # Xử lý ngoại lệ Gateway 1 tại Bước 2 (Không đủ thông tin)
    if not is_sufficient:
        c_list[1] = "warning"
        n_list[1] = "⚠"
        
    # Xử lý Gateway 2 tại Bước 5 / Trưởng phòng duyệt
    if needs_appr:
        if st.session_state.get("manager_decision"):
            c_list[5] = "completed"
            n_list[5] = "✓"
        else:
            c_list[5] = "warning" if active_step >= 5 else "idle"
            n_list[5] = "⚠"
    else:
        c_list[5] = "dimmed"
        n_list[5] = "—"
        
    c1, c2, c3, c4, c5, c_appr, c6 = c_list[0], c_list[1], c_list[2], c_list[3], c_list[4], c_list[5], c_list[6]
    n1, n2, n3, n4, n5, n_appr, n6 = n_list[0], n_list[1], n_list[2], n_list[3], n_list[4], n_list[5], n_list[6]

    # STEPPER VISUAL CONTAINER
    st.markdown(clean_html(f"""
    <div class="stepper-container">
        <div class="step-item">
            <div class="step-circle {c1}">{n1}</div>
            <div>
                <div class="step-label">{t("wf_step_1_title", lang)}</div>
                <div class="step-sublabel">{t("wf_step_1_sub", lang)}</div>
            </div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item">
            <div class="step-circle {c2}">{n2}</div>
            <div>
                <div class="step-label">{t("wf_step_2_title", lang)}</div>
                <div class="step-sublabel">{t("wf_step_2_sub", lang)}</div>
            </div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item">
            <div class="step-circle {c3}">{n3}</div>
            <div>
                <div class="step-label">{t("wf_step_3_title", lang)}</div>
                <div class="step-sublabel">{t("wf_step_3_sub", lang)}</div>
            </div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item">
            <div class="step-circle {c4}">{n4}</div>
            <div>
                <div class="step-label">{t("wf_step_4_title", lang)}</div>
                <div class="step-sublabel">{t("wf_step_4_sub", lang)}</div>
            </div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item">
            <div class="step-circle {c5}">{n5}</div>
            <div>
                <div class="step-label">{t("wf_step_5_title", lang)}</div>
                <div class="step-sublabel">{t("wf_step_5_sub", lang)}</div>
            </div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item">
            <div class="step-circle {c_appr}">{n_appr}</div>
            <div>
                <div class="step-label">{t("wf_step_approval_title", lang)}</div>
                <div class="step-sublabel">{t("wf_step_approval_sub", lang)}</div>
            </div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item">
            <div class="step-circle {c6}">{n6}</div>
            <div>
                <div class="step-label">{t("wf_step_6_title", lang)}</div>
                <div class="step-sublabel">{t("wf_step_6_sub", lang)}</div>
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)
    
    # ------------------------------------------------------------------------------------------------
    # THANH NÚT CHỌN BƯỚC TƯƠNG TÁC (CHUYỂN TRỰC TIẾP GIỮA CÁC BƯỚC KHÔNG MẤT DỮ LIỆU)
    # ------------------------------------------------------------------------------------------------
    st.markdown('<div class="step-nav-dock">', unsafe_allow_html=True)
    step_btn_cols = st.columns(6)
    
    # Tạo nhãn hiện đại kèm trạng thái động
    def get_step_nav_label(step_num: int, title_key: str) -> str:
        short_title = t(title_key, lang).split('. ')[-1]
        if step_num == active_step:
            return f"⚡ B{step_num}: {short_title}"
        elif step_num < active_step:
            if step_num == 2 and not is_sufficient:
                return f"⚠ B2: Làm rõ"
            return f"✓ B{step_num}: {short_title}"
        else:
            return f"{step_num}. {short_title}"

    step_labels = [
        (1, get_step_nav_label(1, "wf_step_1_title")),
        (2, get_step_nav_label(2, "wf_step_2_title")),
        (3, get_step_nav_label(3, "wf_step_3_title")),
        (4, get_step_nav_label(4, "wf_step_4_title")),
        (5, get_step_nav_label(5, "wf_step_5_title")),
        (6, get_step_nav_label(6, "wf_step_6_title"))
    ]
    for col_b, (s_idx, s_txt) in zip(step_btn_cols, step_labels):
        is_cur_b = (active_step == s_idx)
        btn_variant = "primary" if is_cur_b else "secondary"
        if col_b.button(s_txt, key=f"nav_btn_step_{s_idx}", type=btn_variant, use_container_width=True):
            st.session_state.wf_active_step = s_idx
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # ================================================================================================
    # KHAI BÁO CÁC HÀM RENDER TỪNG BƯỚC CỦA QUY TRÌNH
    # ================================================================================================
    
    def render_step_1():
        """BƯỚC 1: TIẾP NHẬN YÊU CẦU (Khách hàng & Intake Gateway)"""
        col_in_l, col_in_r = st.columns([7, 3])
        with col_in_l:
            icon_file = get_icon_tile("file_text", "indigo")
            st.markdown(clean_html(f"""
            <div class="section-header-row">
                {icon_file}
                <div class="section-header-title">{t("req_box_title", lang)}</div>
            </div>
            """), unsafe_allow_html=True)
            
            selected_sample = st.selectbox(
                t("sample_select_label", lang),
                sample_options,
                index=1,
                label_visibility="collapsed",
                key="sample_select_box"
            )
            
            default_text = ""
            if selected_sample != t("sample_select_default", lang):
                s_id = selected_sample.split(":")[0]
                for s in sample_requests:
                    if s["id"] == s_id:
                        default_text = s["raw_text"]
                        break
                        
            # Tự động đồng bộ kết quả khi đổi mẫu
            if "last_selected_sample" not in st.session_state:
                st.session_state.last_selected_sample = selected_sample
            elif selected_sample != st.session_state.last_selected_sample:
                st.session_state.last_selected_sample = selected_sample
                if default_text:
                    st.session_state.current_result = st.session_state.agent.process_request(default_text)
                    if st.session_state.current_result.get("sales_rep"):
                        st.session_state.assigned_rep_name = st.session_state.current_result["sales_rep"]["FullName"]
                    st.session_state.manager_decision = None
                    st.session_state.wf_active_step = 1
                    st.rerun()
                        
            req_input = st.text_area(
                t("req_input_label", lang),
                value=default_text if default_text else (cur_res.get("raw_text", "") if cur_res else ""),
                height=210,
                placeholder=t("req_input_placeholder", lang),
                key="text_req_input"
            )
            
            col_act1, col_act2 = st.columns([1, 1])
            with col_act1:
                if st.button("🚀 Thẩm định & Khởi tạo Hồ sơ (Bước 1 ➔ 2)", use_container_width=True, type="primary", key="btn_run_b1"):
                    if req_input.strip():
                        with st.spinner(t("processing_spinner", lang)):
                            st.session_state.current_result = st.session_state.agent.process_request(req_input)
                            if st.session_state.current_result.get("sales_rep"):
                                st.session_state.assigned_rep_name = st.session_state.current_result["sales_rep"]["FullName"]
                            st.session_state.manager_decision = None
                            st.session_state.wf_active_step = 2
                            st.toast("Đã tiếp nhận yêu cầu và hoàn tất trích xuất dữ liệu B1!", icon="📥")
                            st.rerun()
            with col_act2:
                if st.button("Tiếp tục xem kết quả kiểm tra (Bước 2) ➔", use_container_width=True, key="btn_next_b1_b2"):
                    st.session_state.wf_active_step = 2
                    st.rerun()

        with col_in_r:
            icon_shield = get_icon_tile("shield_check", "amber")
            st.markdown(clean_html(f"""
            <div class="section-header-row">
                {icon_shield}
                <div class="section-header-title">{t("rules_card_title", lang)}</div>
            </div>
            """), unsafe_allow_html=True)
            
            sku_icon = get_svg_icon("package", size=18, color="#6366f1")
            sla_icon = get_svg_icon("clock", size=18, color="#06b6d4")
            matrix_icon = get_svg_icon("shield_check", size=18, color="#f59e0b")
            
            st.markdown(clean_html(f"""
            <div class="rule-subcard sku-accent">
                <div style="flex-shrink: 0; margin-top: 2px;">{sku_icon}</div>
                <div>
                    <div style="font-weight: 700; color: var(--text-primary); font-size: 14px;">{t("rule_sku_title", lang)}</div>
                    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">{t("rule_sku_desc", lang)}</div>
                </div>
            </div>
            <div class="rule-subcard sla-accent">
                <div style="flex-shrink: 0; margin-top: 2px;">{sla_icon}</div>
                <div>
                    <div style="font-weight: 700; color: var(--text-primary); font-size: 14px;">{t("rule_sla_title", lang)}</div>
                    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">{t("rule_sla_desc", lang)}</div>
                </div>
            </div>
            <div class="rule-subcard matrix-accent">
                <div style="flex-shrink: 0; margin-top: 2px;">{matrix_icon}</div>
                <div>
                    <div style="font-weight: 700; color: var(--text-primary); font-size: 14px;">{t("rule_matrix_title", lang)}</div>
                    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">{t("rule_matrix_desc", lang)}</div>
                </div>
            </div>
            """), unsafe_allow_html=True)

    def render_step_2():
        """BƯỚC 2: PHÂN LOẠI & KIỂM TRA THÔNG TIN (Đủ thông tin? - Gateway 1)"""
        if not cur_res:
            st.info("Chưa có dữ liệu yêu cầu. Vui lòng quay lại Bước 1.")
            return

        parsed = cur_res.get("parsed_request") or {}
        is_suff = parsed.get("is_sufficient", True)
        
        icon_check = get_icon_tile("clipboard_check", "cyan")
        st.markdown(clean_html(f"""
        <div class="section-header-row">
            {icon_check}
            <div class="section-header-title">Bước 2: Phân loại & Kiểm tra Thông tin (Gateway 1: Đủ thông tin?)</div>
        </div>
        """), unsafe_allow_html=True)

        # 1. Trạng thái Đầy đủ Thông tin
        if not is_suff:
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--status-danger); margin-bottom: 18px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 18px; font-weight: 800; color: var(--status-danger);">
                        {t("insufficient_title", lang)}
                    </div>
                    <span class="badge-capsule badge-red">Chờ khách bổ sung</span>
                </div>
                <div style="color: var(--text-secondary); font-size: 14px; margin-bottom: 8px;">
                    {t("insufficient_desc", lang)}
                </div>
                <div style="font-size: 13px; font-weight: 700; color: var(--status-danger);">
                    ⚡ Điểm rẽ 1: KHÔNG ĐỦ THÔNG TIN BẮT BUỘC ➔ Kích hoạt quy trình yêu cầu Khách hàng làm rõ / bổ sung.
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            c_clar1, c_clar2 = st.columns([1, 1])
            with c_clar1:
                st.markdown(clean_html(f'<div class="section-header-title" style="margin-bottom: 12px;">{t("missing_items_title", lang)}</div>'), unsafe_allow_html=True)
                for r in parsed.get("missing_reasons", []):
                    st.markdown(clean_html(f"""
                    <div style="background: var(--status-danger-bg); border: 1px solid var(--status-danger-border); padding: 12px 16px; border-radius: 12px; margin-bottom: 8px; font-size: 14px; color: var(--status-danger); font-weight: 600;">
                        • {r}
                    </div>
                    """), unsafe_allow_html=True)
            with c_clar2:
                st.markdown(clean_html(f'<div class="section-header-title" style="margin-bottom: 12px;">{t("clarification_email_title", lang)}</div>'), unsafe_allow_html=True)
                clar_draft = cur_res.get("clarification_draft", "")
                st.text_area("Nội dung thư làm rõ:", value=clar_draft, height=160, label_visibility="collapsed", key="area_clar_draft")
                st.download_button(
                    t("btn_download_clarification", lang),
                    data=clar_draft,
                    file_name=f"Yeu_cau_bo_sung_{cur_res.get('opportunity_id', 'REQ')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="btn_dl_clar_b2"
                )
                
            # Cổng tiếp nhận thông tin bổ sung quay lại B1 theo đúng sơ đồ
            st.markdown(clean_html(f"""
            <div style="margin-top: 14px; margin-bottom: 6px; font-size: 13px; font-weight: 700; color: var(--text-primary);">
                🔄 {t("clarification_paste_label", lang)}
            </div>
            """), unsafe_allow_html=True)
            supp_text = st.text_area(
                "Thông tin bổ sung từ khách:",
                placeholder="Ví dụ: Bổ sung số lượng: 10 máy chủ Dell R750 và 5 switch Cisco C9200L, ngân sách 1 tỷ 2...",
                height=85,
                key="supp_info_input_b2",
                label_visibility="collapsed"
            )
            if st.button(t("btn_resubmit_clarification", lang), key="btn_submit_supp_b2", use_container_width=True, type="primary"):
                if supp_text.strip():
                    orig_input = st.session_state.get("text_req_input", "") or sample_requests[1]["raw_text"]
                    combined = orig_input + "\n\n[Thông tin bổ sung tiếp nhận lại tại B1]:\n" + supp_text.strip()
                    st.session_state.current_result = st.session_state.agent.process_request(combined)
                    if st.session_state.current_result.get("sales_rep"):
                        st.session_state.assigned_rep_name = st.session_state.current_result["sales_rep"]["FullName"]
                    st.session_state.wf_active_step = 2
                    st.toast("Đã tiếp nhận thông tin bổ sung vào B1 và hoàn tất tái thẩm định B2!", icon="✅")
                    st.rerun()
        else:
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--status-success); margin-bottom: 18px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="font-size: 16px; font-weight: 800; color: var(--status-success);">
                        ✅ {t("gateway_1_sufficient", lang)}
                    </div>
                    <span class="badge-capsule badge-green">Đầy đủ thông tin</span>
                </div>
                <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6;">
                    Yêu cầu đã được kiểm tra: Doanh nghiệp rõ ràng, chủng loại thiết bị và dịch vụ định danh đầy đủ, sẵn sàng khởi tạo Hồ sơ Cơ hội CRM.
                </div>
            </div>
            """), unsafe_allow_html=True)

        # 2. Cảnh báo Thiếu ngân sách & Rủi ro Bỏ sót hạng mục
        col_chk1, col_chk2 = st.columns(2)
        with col_chk1:
            budget_val = parsed.get("budget")
            if budget_val is None or budget_val <= 0:
                st.markdown(clean_html(f"""
                <div style="background: var(--status-warning-bg); border: 1px solid var(--status-warning-border); padding: 14px 16px; border-radius: 14px; margin-bottom: 12px;">
                    <div style="font-weight: 800; color: var(--status-warning); font-size: 14px; margin-bottom: 4px;">
                        ⚠ {t("warning_missing_budget", lang)}
                    </div>
                    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">
                        Khách hàng chưa khai báo ngân sách tổng trần. Hệ thống đã kích hoạt kịch bản đề xuất ngân sách tham chiếu theo cấu hình tiêu chuẩn của Minh An để NVKD tư vấn.
                    </div>
                </div>
                """), unsafe_allow_html=True)
            else:
                st.markdown(clean_html(f"""
                <div style="background: var(--status-success-bg); border: 1px solid var(--status-success-border); padding: 14px 16px; border-radius: 14px; margin-bottom: 12px;">
                    <div style="font-weight: 800; color: var(--status-success); font-size: 14px; margin-bottom: 4px;">
                        💰 Ngân sách Tổng của Khách hàng: {budget_val:,.0f} đ
                    </div>
                    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">
                        Ngân sách đã được xác lập cụ thể, làm căn cứ thẩm định phương án tài chính và mức chiết khấu phù hợp.
                    </div>
                </div>
                """), unsafe_allow_html=True)

        with col_chk2:
            extracted_items = parsed.get("items", [])
            st.markdown(clean_html(f"""
            <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25); padding: 14px 16px; border-radius: 14px; margin-bottom: 12px;">
                <div style="font-weight: 800; color: var(--accent-indigo); font-size: 14px; margin-bottom: 4px;">
                    🛡️ {t("warning_omitted_items", lang)}: {len(extracted_items)} Hạng mục
                </div>
                <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">
                    100% yêu cầu về máy chủ, thiết bị mạng, linh kiện và dịch vụ kỹ thuật đã được bóc tách tự động, loại bỏ hoàn toàn nguy cơ NVKD bỏ sót hạng mục khi lập đề xuất.
                </div>
            </div>
            """), unsafe_allow_html=True)

        # 3. Bảng tóm tắt thông tin bóc tách
        st.markdown(clean_html(f"""
        <div class="bento-surface" style="margin-top: 8px;">
            <div style="font-weight: 800; font-size: 15px; color: var(--text-primary); margin-bottom: 8px;">
                📋 Dữ liệu Hồ sơ Khách hàng đã Bóc tách từ Văn bản:
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; font-size: 13px; color: var(--text-secondary);">
                <div>• <b>Doanh nghiệp:</b> <span style="color: var(--text-primary); font-weight: 700;">{parsed.get('company_name', 'Chưa rõ')}</span></div>
                <div>• <b>Người liên hệ:</b> <span style="color: var(--text-primary); font-weight: 700;">{parsed.get('contact_person', 'Chưa rõ')}</span></div>
                <div>• <b>Email:</b> {parsed.get('email', 'Chưa cung cấp')}</div>
                <div>• <b>Số điện thoại:</b> {parsed.get('phone', 'Chưa cung cấp')}</div>
                <div>• <b>Thời hạn mong muốn:</b> {parsed.get('desired_delivery_days', 'Chưa nêu')} ngày</div>
                <div>• <b>Chiết khấu đề xuất:</b> {parsed.get('requested_discount_pct', 0.0)}%</div>
            </div>
        </div>
        """), unsafe_allow_html=True)

        # Bottom navigation
        c_nav_l, c_nav_r = st.columns([1, 1])
        with c_nav_l:
            if st.button("◀ Quay lại Bước 1 (Tiếp nhận)", use_container_width=True, key="btn_b2_back"):
                st.session_state.wf_active_step = 1
                st.rerun()
        with c_nav_r:
            if st.button("Tiếp tục sang Bước 3: Tạo Hồ sơ Cơ hội (CRM) ➔", use_container_width=True, type="primary", disabled=not is_suff, key="btn_b2_next"):
                st.session_state.wf_active_step = 3
                st.rerun()

    def render_step_3():
        """BƯỚC 3: TẠO HỒ SƠ CƠ HỘI (CRM & Gán NVKD trong 6 NVKD)"""
        if not cur_res:
            st.info("Chưa có dữ liệu yêu cầu. Vui lòng quay lại Bước 1.")
            return

        parsed = cur_res.get("parsed_request") or {}
        opp_rec = cur_res.get("opportunity_record") or {}
        
        icon_crm = get_icon_tile("user_check", "indigo")
        st.markdown(clean_html(f"""
        <div class="section-header-row">
            {icon_crm}
            <div class="section-header-title">Bước 3: Tạo Hồ sơ Cơ hội & Phân bổ NVKD (CRM Minh An)</div>
        </div>
        """), unsafe_allow_html=True)

        c_opp_l, c_opp_r = st.columns([6, 4])
        with c_opp_l:
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--accent-indigo); margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div>
                        <div style="font-size: 12px; font-weight: 700; color: var(--accent-indigo); text-transform: uppercase; letter-spacing: 0.5px;">HỒ SƠ CƠ HỘI CHUẨN HÓA</div>
                        <div style="font-size: 22px; font-weight: 800; color: var(--text-primary);">{cur_res.get('opportunity_id')}</div>
                    </div>
                    <span class="badge-capsule badge-blue">Đã ghi nhận CRM</span>
                </div>
                <div style="font-size: 14px; color: var(--text-secondary); line-height: 1.8;">
                    • <b>Khách hàng Doanh nghiệp:</b> <span style="font-weight: 700; color: var(--text-primary);">{parsed.get('company_name')}</span><br>
                    • <b>Người đại diện liên hệ:</b> {parsed.get('contact_person')} ({parsed.get('email')} • {parsed.get('phone')})<br>
                    • <b>Thời điểm khởi tạo:</b> {opp_rec.get('created_at', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}<br>
                    • <b>Kênh tiếp nhận:</b> Inbound Email & Web Form Gateway (~180 yêu cầu/tuần)
                </div>
            </div>
            """), unsafe_allow_html=True)

            # CẢNH BÁO ĐỊNH DANH NGƯỜI THEO DÕI — TRIỆT TIÊU RỦI RO HỒ SƠ BỊ THẢ NỔI
            st.markdown(clean_html(f"""
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <span style="font-size: 16px;">👤</span>
                    <span style="font-weight: 800; color: var(--status-success); font-size: 14px;">KIỂM SOÁT NGƯỜI THEO DÕI (OWNER & FOLLOWER)</span>
                </div>
                <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">
                    {t("follower_established_note", lang)}. Hồ sơ bắt buộc có NVKD trực tiếp phụ trách và Cán bộ theo dõi giám sát tiến độ để đảm bảo phản hồi khách hàng trong cam kết 2-4 giờ.
                </div>
            </div>
            """), unsafe_allow_html=True)

        with c_opp_r:
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="margin-bottom: 16px;">
                <div style="font-weight: 800; font-size: 15px; color: var(--text-primary); margin-bottom: 12px;">
                    🎯 Phân bổ & Gán Trách nhiệm Xử lý:
                </div>
            """), unsafe_allow_html=True)

            # 1. Gán NVKD trong nhóm 6 NVKD của Minh An
            sales_df = st.session_state.sales_df
            rep_options = []
            for _, r in sales_df.iterrows():
                rep_options.append(f"{r['StaffID']} - {r['FullName']} ({r['Specialty']})")

            curr_rep = st.session_state.assigned_rep_name or (cur_res.get("sales_rep") or {}).get("FullName", "")
            def_idx = 0
            for idx_r, opt_r in enumerate(rep_options):
                if curr_rep and curr_rep in opt_r:
                    def_idx = idx_r
                    break

            selected_rep_str = st.selectbox(
                t("assign_sales_rep_label", lang),
                rep_options,
                index=def_idx,
                key="sb_sales_rep_b3"
            )
            if selected_rep_str:
                chosen_name = selected_rep_str.split(" - ")[1].split(" (")[0].strip()
                st.session_state.assigned_rep_name = chosen_name
                m_rep = sales_df[sales_df["FullName"] == chosen_name]
                if not m_rep.empty:
                    cur_res["sales_rep"] = m_rep.iloc[0].to_dict()

            # 2. Định danh Cán bộ theo dõi (Follower)
            follower_val = st.text_input(
                t("assign_follower_label", lang),
                value=st.session_state.assigned_follower_name,
                key="txt_follower_b3",
                help="Loại bỏ tình trạng hồ sơ bị thả nổi hoặc chuyển qua lại không người chịu trách nhiệm."
            )
            if follower_val:
                st.session_state.assigned_follower_name = follower_val

            st.markdown("</div>", unsafe_allow_html=True)

        # Bottom navigation
        c_nav_l, c_nav_r = st.columns([1, 1])
        with c_nav_l:
            if st.button("◀ Quay lại Bước 2 (Phân loại & Kiểm tra)", use_container_width=True, key="btn_b3_back"):
                st.session_state.wf_active_step = 2
                st.rerun()
        with c_nav_r:
            if st.button("Tiếp tục sang Bước 4: Thẩm định Kho & Giá ➔", use_container_width=True, type="primary", key="btn_b3_next"):
                st.session_state.wf_active_step = 4
                st.rerun()

    def render_step_4():
        """BƯỚC 4: THẨM ĐỊNH TỒN KHO & ĐƠN GIÁ (NVKD & Vận hành)"""
        if not cur_res:
            st.info("Chưa có dữ liệu yêu cầu. Vui lòng quay lại Bước 1.")
            return

        eval_data = cur_res.get("evaluation")
        if not eval_data:
            st.warning("Yêu cầu chưa đủ thông tin thẩm định. Vui lòng quay lại Bước 2.")
            return

        items_detail = eval_data.get("items_detail", [])
        
        icon_box = get_icon_tile("package", "teal")
        st.markdown(clean_html(f"""
        <div class="section-header-row">
            {icon_box}
            <div class="section-header-title">Bước 4: Thẩm định Kho & Đơn giá (NVKD & Bộ phận Vận hành)</div>
        </div>
        """), unsafe_allow_html=True)

        # 1. Chốt chặn 1: Khóa 100% theo Bảng giá niêm yết hiện hành 2026
        st.markdown(clean_html(f"""
        <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
            <div style="font-weight: 800; color: #0891b2; font-size: 14px; margin-bottom: 4px;">
                🔒 {t("warning_price_control", lang)} — CHẶN DÙNG BẢNG GIÁ CŨ
            </div>
            <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">
                100% đơn giá từng hạng mục được hệ thống khóa cứng và đối soát theo Danh mục Bảng giá hiện hành 2026 của Minh An. Nghiêm cấm dùng bảng giá cũ hoặc tự ý nhập giá ngoài biểu giá niêm yết.
            </div>
        </div>
        """), unsafe_allow_html=True)

        # 2. Chốt chặn 2 & 3: Thẩm định Tồn khả dụng & Cảnh báo SLA giao hàng
        stock_warns = eval_data.get("stock_warnings", [])
        lead_warns = eval_data.get("leadtime_warnings", [])
        
        if stock_warns or lead_warns:
            for w in stock_warns:
                st.markdown(clean_html(f"""
                <div style="background: var(--status-warning-bg); border: 1px solid var(--status-warning-border); color: var(--status-warning); padding: 12px 16px; border-radius: 12px; font-size: 13px; margin-bottom: 8px;">
                    📦 <b>Cảnh báo Tồn kho Khả dụng:</b> {w}
                </div>
                """), unsafe_allow_html=True)
            for lw in lead_warns:
                st.markdown(clean_html(f"""
                <div style="background: var(--status-danger-bg); border: 1px solid var(--status-danger-border); color: var(--status-danger); padding: 12px 16px; border-radius: 12px; font-size: 13px; margin-bottom: 8px;">
                    ⏱️ <b>{t("warning_leadtime_sla", lang)}:</b> {lw}
                </div>
                """), unsafe_allow_html=True)
        else:
            st.markdown(clean_html(f"""
            <div style="background: var(--status-success-bg); border: 1px solid var(--status-success-border); color: var(--status-success); padding: 12px 16px; border-radius: 12px; font-size: 13px; margin-bottom: 12px;">
                ✅ <b>SLA KHO & VẬN HÀNH ĐẠT CHUẨN:</b> Hàng sẵn kho 100%, thời gian điều phối cam kết 1-2 ngày, đáp ứng hoàn toàn thời hạn triển khai của khách hàng.
            </div>
            """), unsafe_allow_html=True)

        # 3. Bảng thẻ chi tiết từng hạng mục thiết bị & dịch vụ
        st.markdown(clean_html(f'<div style="font-weight: 800; font-size: 15px; color: var(--text-primary); margin-top: 14px; margin-bottom: 10px;">📦 Danh mục Hạng mục Thẩm định với Bộ phận Vận hành ({len(items_detail)} SKU):</div>'), unsafe_allow_html=True)
        for it in items_detail:
            status_str = str(it.get("StockStatus", ""))
            is_service = ("Dịch vụ" in status_str or it.get("Category") == "Dịch vụ" or it.get("AvailableStock", 0) >= 999 or "SVC-" in str(it.get("SKU", "")).upper())
            is_in_stock = ("Đủ hàng" in status_str or (not is_service and it.get("AvailableStock", 0) >= it.get("Quantity", 1)))
            
            if is_service:
                stock_badge = '<span class="badge-capsule badge-cyan">Dịch vụ · không giới hạn</span>'
            elif is_in_stock:
                stock_badge = f'<span class="badge-capsule badge-green">{status_str}</span>'
            else:
                stock_badge = f'<span class="badge-capsule badge-red">{status_str}</span>'
            
            st.markdown(clean_html(f"""
            <div class="item-showcase-tile">
                <div style="max-width: 65%;">
                    <div style="font-weight: 700; font-size: 15px; color: var(--text-primary); margin-bottom: 4px;">{it['ProductName']}</div>
                    <div style="display: flex; gap: 8px; align-items: center; font-size: 13px; color: var(--text-muted); flex-wrap: wrap;">
                        <span class="sku-mono-pill">{it['SKU']}</span>
                        <span>SL: <b>{it['Quantity']} {it['Unit']}</b></span>
                        <span>• Giá niêm yết 2026: <b>{it['UnitPrice']:,.0f} đ</b></span>
                        <span>• Tồn kho Vận hành: <b>{it.get('AvailableStock', 0)}</b></span>
                        <span>• SLA giao: <b>{it.get('DeliveryDays', 1)} ngày</b></span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight: 800; font-size: 16px; color: var(--text-primary);">{it['FinalTotal']:,.0f} đ</div>
                    <div style="margin-top: 6px;">{stock_badge}</div>
                </div>
            </div>
            """), unsafe_allow_html=True)

        # Bottom navigation
        c_nav_l, c_nav_r = st.columns([1, 1])
        with c_nav_l:
            if st.button("◀ Quay lại Bước 3 (Hồ sơ Cơ hội CRM)", use_container_width=True, key="btn_b4_back"):
                st.session_state.wf_active_step = 3
                st.rerun()
        with c_nav_r:
            if st.button("Tiếp tục sang Bước 5: Lập Báo giá & Dự thảo ➔", use_container_width=True, type="primary", key="btn_b4_next"):
                st.session_state.wf_active_step = 5
                st.rerun()

    def render_step_5():
        """BƯỚC 5: LẬP BÁO GIÁ & DỰ THẢO + NHÁNH TRƯỞNG PHÒNG DUYỆT (KHI VƯỢT QUYỀN)"""
        if not cur_res:
            st.info("Chưa có dữ liệu yêu cầu. Vui lòng quay lại Bước 1.")
            return

        eval_data = cur_res.get("evaluation")
        if not eval_data:
            st.warning("Yêu cầu chưa đủ thông tin lập báo giá. Vui lòng quay lại Bước 2.")
            return

        parsed = cur_res.get("parsed_request") or {}
        rep = cur_res.get("sales_rep") or {}
        approval_key = f"approval_status_{cur_res['opportunity_id']}"
        current_appr_badge = st.session_state.get(approval_key, st.session_state.manager_decision or eval_data['decision_badge'])

        icon_quote = get_icon_tile("sparkles", "indigo")
        st.markdown(clean_html(f"""
        <div class="section-header-row">
            {icon_quote}
            <div class="section-header-title">Bước 5: Lập Báo giá & Dự thảo Đề xuất (NVKD & AI Copilot)</div>
        </div>
        """), unsafe_allow_html=True)

        # 1. 4 Thẻ KPI Tài chính & Tiến độ Báo giá
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(clean_html(f"""
            <div class="stat-kpi-card">
                <div class="stat-kpi-value">{eval_data['total_final_amount']:,.0f} đ</div>
                <div class="stat-kpi-label">{t("kpi_total_amount", lang)}</div>
            </div>
            """), unsafe_allow_html=True)
        with k2:
            st.markdown(clean_html(f"""
            <div class="stat-kpi-card">
                <div class="stat-kpi-value">{eval_data['discount_pct']:.1f}%</div>
                <div class="stat-kpi-label">{t("kpi_discount", lang)} ({eval_data['total_discount_amount']:,.0f} đ)</div>
            </div>
            """), unsafe_allow_html=True)
        with k3:
            st.markdown(clean_html(f"""
            <div class="stat-kpi-card">
                <div class="stat-kpi-value">{eval_data['max_lead_time_days']} ngày</div>
                <div class="stat-kpi-label">{t("kpi_lead_time", lang)}</div>
            </div>
            """), unsafe_allow_html=True)
        with k4:
            st.markdown(clean_html(f"""
            <div class="stat-kpi-card">
                <div class="stat-kpi-value" style="font-size: 20px; line-height: 33px;">{eval_data['budget_status']}</div>
                <div class="stat-kpi-label">Ngân sách vs Báo giá</div>
            </div>
            """), unsafe_allow_html=True)

        st.write("")

        # 2. Điểm rẽ 2: Kiểm tra Thẩm quyền & Nhánh Trưởng phòng duyệt khi vượt quyền
        if eval_data["needs_manager_approval"]:
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--status-warning); margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-weight: 800; font-size: 16px; color: var(--status-warning);">
                        ⚡ ĐIỂM RẼ 2: VƯỢT THẨM QUYỀN NVKD ➔ CHUYỂN TRƯỞNG PHÒNG KINH DOANH DUYỆT
                    </div>
                    <span class="badge-capsule badge-amber">{current_appr_badge}</span>
                </div>
                <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 10px;">
                    • <b>Lý do chuyển duyệt:</b> Chiết khấu đề xuất <b>{eval_data['discount_pct']:.1f}%</b> (vượt hạn mức 5.0% của NVKD) hoặc Tổng giá trị <b>{eval_data['total_final_amount']:,.0f} đ</b> (vượt 100M đ).<br>
                    • <b>NVKD trình duyệt:</b> {rep.get('FullName')} ({rep.get('StaffID')}) &nbsp;|&nbsp; 
                    • <b>Cán bộ theo dõi tiến độ:</b> {st.session_state.assigned_follower_name}
                </div>
            </div>
            """), unsafe_allow_html=True)

            # Khối tương tác Phê duyệt của Trưởng phòng Kinh doanh
            st.markdown(clean_html(f"""
            <div class="telegram-approval-card" style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span class="badge-capsule badge-amber">Kênh Phê duyệt Cấp quản lý</span>
                    <span style="font-size: 13px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">Recipient: Trưởng phòng Kinh doanh Minh An</span>
                </div>
                <div style="font-size: 14px; color: var(--text-primary); line-height: 1.6; margin-bottom: 14px;">
                    Hồ sơ <b>{cur_res['opportunity_id']}</b> cho khách hàng <b>{parsed.get('company_name')}</b> cần quyết định phê duyệt chính sách thương mại đặc biệt.
                </div>
            </div>
            """), unsafe_allow_html=True)

            c_act_ap1, c_act_ap2, c_act_ap3 = st.columns(3)
            with c_act_ap1:
                if st.button("✅ Phê duyệt Đề xuất", key="btn_ap_mgr_ok", use_container_width=True, type="primary"):
                    st.session_state[approval_key] = "Trưởng phòng Kinh doanh: ĐÃ PHÊ DUYỆT"
                    st.session_state.manager_decision = "ĐÃ PHÊ DUYỆT"
                    st.toast("Trưởng phòng Kinh doanh đã phê duyệt đề xuất chiết khấu!", icon="✅")
                    st.rerun()
            with c_act_ap2:
                if st.button("💬 Yêu cầu Điều chỉnh", key="btn_ap_mgr_adj", use_container_width=True):
                    st.session_state[approval_key] = "Trưởng phòng yêu cầu NVKD đàm phán giảm chiết khấu"
                    st.session_state.manager_decision = "YÊU CẦU ĐIỀU CHỈNH"
                    st.toast("Đã chuyển yêu cầu đàm phán giảm chiết khấu đến NVKD!", icon="💬")
                    st.rerun()
            with c_act_ap3:
                if st.button("❌ Từ chối Phê duyệt", key="btn_ap_mgr_rej", use_container_width=True):
                    st.session_state[approval_key] = "Trưởng phòng Kinh doanh: TỪ CHỐI"
                    st.session_state.manager_decision = "TỪ CHỐI"
                    st.toast("Trưởng phòng Kinh doanh đã từ chối đề xuất chiết khấu!", icon="❌")
                    st.rerun()
        else:
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--status-success); margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="font-weight: 800; font-size: 16px; color: var(--status-success);">
                        🟢 NVKD TỰ QUYẾT ĐỊNH TRONG THẨM QUYỀN
                    </div>
                    <span class="badge-capsule badge-green">Tự quyết 100%</span>
                </div>
                <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6;">
                    Chiết khấu <b>{eval_data['discount_pct']:.1f}%</b> <= 5.0% và Giá trị hợp đồng nằm trong hạn mức phân quyền. NVKD {rep.get('FullName')} được quyền ký duyệt và gửi báo giá trực tiếp đến khách hàng.
                </div>
            </div>
            """), unsafe_allow_html=True)

        # 3. Bản nháp Phản hồi khách hàng & Tải Excel Báo giá
        c_prop1, c_prop2 = st.columns([6, 4])
        with c_prop1:
            st.markdown(clean_html(f'<div class="section-header-title" style="margin-bottom: 8px;">{t("proposal_email_title", lang)}:</div>'), unsafe_allow_html=True)
            prop_text = cur_res.get("client_proposal", "")
            st.text_area("Bản nháp gửi khách hàng:", value=prop_text, height=220, label_visibility="collapsed", key="area_client_prop_b5")
            st.download_button(
                t("btn_download_proposal", lang),
                data=prop_text,
                file_name=f"De_xuat_kinh_doanh_{cur_res['opportunity_id']}.txt",
                mime="text/plain",
                use_container_width=True,
                key="btn_dl_prop_b5"
            )

        with c_prop2:
            st.markdown(clean_html(f'<div class="section-header-title" style="margin-bottom: 8px;">Tải Báo giá Chính thức (.xlsx):</div>'), unsafe_allow_html=True)
            items_df = pd.DataFrame(eval_data["items_detail"])
            excel_buf = io.BytesIO()
            with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                items_df.to_excel(writer, sheet_name="Bao_Gia", index=False)
            excel_data_bytes = excel_buf.getvalue()
            
            st.markdown(clean_html(f"""
            <div style="background: var(--bg-surface); border: 1px solid var(--border-card); border-radius: 14px; padding: 18px; margin-bottom: 12px;">
                <div style="font-weight: 700; font-size: 14px; color: var(--text-primary); margin-bottom: 6px;">Bảng Báo giá Thương mại Minh An</div>
                <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 14px;">
                    Bao gồm {len(items_df)} hạng mục đã thẩm định kho, áp dụng đúng bảng giá hiện hành 2026 và chiết khấu thương mại.
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            st.download_button(
                label=t("btn_download_quotation", lang),
                data=excel_data_bytes,
                file_name=f"Bao_gia_{cur_res['opportunity_id']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
                key="btn_dl_quote_b5"
            )

        # Bottom navigation
        c_nav_l, c_nav_r = st.columns([1, 1])
        with c_nav_l:
            if st.button("◀ Quay lại Bước 4 (Thẩm định Kho & Giá)", use_container_width=True, key="btn_b5_back"):
                st.session_state.wf_active_step = 4
                st.rerun()
        with c_nav_r:
            if st.button("Tiếp tục sang Bước 6: Kết thúc & Theo dõi ➔", use_container_width=True, type="primary", key="btn_b5_next"):
                st.session_state.wf_active_step = 6
                st.rerun()

    def render_step_6():
        """BƯỚC 6: KẾT THÚC — CẬP NHẬT & THEO DÕI HỒ SƠ CƠ HỘI"""
        if not cur_res:
            st.info("Chưa có dữ liệu yêu cầu. Vui lòng quay lại Bước 1.")
            return

        eval_data = cur_res.get("evaluation") or {}
        parsed = cur_res.get("parsed_request") or {}
        rep = cur_res.get("sales_rep") or {}
        opp_rec = cur_res.get("opportunity_record") or {}
        
        icon_flag = get_icon_tile("clipboard_check", "emerald")
        st.markdown(clean_html(f"""
        <div class="section-header-row">
            {icon_flag}
            <div class="section-header-title">Bước 6: Kết thúc — Cập nhật & Theo dõi Hồ sơ Cơ hội (Hoàn tất)</div>
        </div>
        """), unsafe_allow_html=True)

        # 1. Thẻ Chốt trạng thái Hồ sơ Cơ hội
        wf_status_label = "Chờ Trưởng phòng phê duyệt" if (eval_data.get('needs_manager_approval') and not st.session_state.get('manager_decision')) else "Đã xuất báo giá (Hoàn tất)"
        wf_badge_cls = "badge-amber" if (eval_data.get('needs_manager_approval') and not st.session_state.get('manager_decision')) else "badge-green"
        
        st.markdown(clean_html(f"""
        <div class="bento-surface" style="border-left: 4px solid var(--status-success); margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="font-weight: 800; font-size: 18px; color: var(--text-primary);">
                    Hồ sơ Cơ hội: {cur_res['opportunity_id']}
                </div>
                <span class="badge-capsule {wf_badge_cls}">{wf_status_label}</span>
            </div>
            <div style="font-size: 14px; color: var(--text-secondary); line-height: 1.8;">
                • <b>Khách hàng:</b> <span style="font-weight: 700; color: var(--text-primary);">{parsed.get('company_name')}</span> (Đại diện: {parsed.get('contact_person')})<br>
                • <b>NVKD phụ trách:</b> {rep.get('FullName')} ({rep.get('StaffID')} - {rep.get('Specialty')})<br>
                • <b>Cán bộ theo dõi tiếp theo:</b> <span style="font-weight: 700; color: var(--accent-indigo);">{st.session_state.assigned_follower_name}</span><br>
                • <b>Giá trị đề xuất chốt:</b> <span style="font-weight: 800; color: var(--text-primary);">{eval_data.get('total_final_amount', 0):,.0f} đ</span> (Chiết khấu: <b>{eval_data.get('discount_pct', 0):.1f}%</b>)<br>
                • <b>Kế hoạch Hành động Tiếp theo:</b> Gửi email báo giá và bản nháp phản hồi đến khách hàng trong vòng 2 giờ; theo dõi phản hồi trong 48 giờ; phối hợp bộ phận Vận hành chuẩn bị sẵn hàng khi hợp đồng được xác nhận.
            </div>
        </div>
        """), unsafe_allow_html=True)

        # 2. Biểu đồ Phân tích Kỹ thuật & Tài chính (Plotly)
        st.markdown(clean_html(f"""
        <div class="section-header-row" style="margin-top: 18px; margin-bottom: 12px;">
            {get_icon_tile("sparkles", "indigo")}
            <div class="section-header-title">{t("charts_single_title", lang)}</div>
        </div>
        """), unsafe_allow_html=True)

        # Dual Gauge Card Thẩm quyền
        try:
            render_governance_card(eval_data, is_dark=is_dark, lang=lang)
        except Exception:
            pass

        items_list = eval_data.get("items_detail") or []
        col_c_a, col_c_b = st.columns(2, gap="large")
        with col_c_a:
            try:
                fig_it, ins_it, df_it = chart_opportunity_item_values(items_list, is_dark=is_dark, lang=lang)
                render_chart_card(fig_it, t("chart_opp_items", lang), ins_it, df_it, "opp_items_b6", lang=lang)
            except Exception:
                pass
            try:
                fig_inv, ins_inv, df_inv = chart_opportunity_inventory_comparison(items_list, is_dark=is_dark, lang=lang)
                render_chart_card(fig_inv, t("chart_opp_inventory", lang), ins_inv, df_inv, "opp_inv_b6", lang=lang)
            except Exception:
                pass

        with col_c_b:
            try:
                fig_cat, ins_cat, df_cat = chart_opportunity_category_donut(items_list, is_dark=is_dark, lang=lang)
                render_chart_card(fig_cat, t("chart_opp_category", lang), ins_cat, df_cat, "opp_cat_b6", lang=lang)
            except Exception:
                pass
            try:
                fig_lt, ins_lt, df_lt = chart_leadtime_timeline(items_list, is_dark=is_dark, lang=lang)
                render_chart_card(fig_lt, t("chart_opp_leadtime", lang), ins_lt, df_lt, "opp_lt_b6", lang=lang)
            except Exception:
                pass

        # 3. Nhật ký Xử lý Minh bạch (Audit Trail Log)
        if "audit_logs" in cur_res and cur_res["audit_logs"]:
            st.markdown(clean_html(f"""
            <div class="section-header-row" style="margin-top: 20px;">
                {get_icon_tile("clipboard_check", "emerald")}
                <div class="section-header-title">{t("audit_trail_title", lang)}</div>
            </div>
            """), unsafe_allow_html=True)
            with st.expander("Xem toàn bộ lịch sử các bước xử lý minh bạch & quy tắc đã áp dụng", expanded=True):
                for log_entry in cur_res["audit_logs"]:
                    actor_tag = log_entry.get("actor", "NVKD & Vận hành")
                    st.markdown(clean_html(f"""
                    <div class="audit-step-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-weight: 700; color: var(--text-primary); font-size: 14px;">{log_entry['step_name']}</span>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <span class="badge-capsule badge-blue" style="font-size: 11px;">Phụ trách: {actor_tag}</span>
                                <span class="sku-mono-pill">{log_entry['timestamp']}</span>
                            </div>
                        </div>
                        <div style="font-size: 13px; color: var(--accent-indigo); margin-bottom: 4px;">Quy tắc: <b>{log_entry['rule_applied']}</b></div>
                        <div style="font-size: 13px; color: var(--text-secondary);">{log_entry['details']}</div>
                    </div>
                    """), unsafe_allow_html=True)

        # 4. Trợ lý đàm phán AI Sales Copilot
        icon_spark = get_icon_tile("sparkles", "pink")
        st.markdown(clean_html(f"""
        <div class="copilot-container" style="margin-top: 20px;">
            <div class="section-header-row" style="margin-bottom: 6px;">
                {icon_spark}
                <div>
                    <div class="section-header-title">{t("copilot_card_title", lang)}</div>
                    <div style="font-size: 13px; color: var(--text-muted);">{t("copilot_subtitle", lang)}</div>
                </div>
            </div>
        """), unsafe_allow_html=True)
        
        col_p1, col_p2, col_p3 = st.columns(3)
        quick_sel = None
        with col_p1:
            if st.button(f"💡 {t('copilot_pill_1', lang)}", key="btn_pill_1_b6", use_container_width=True):
                quick_sel = t('copilot_pill_1', lang)
        with col_p2:
            if st.button(f"⏱️ {t('copilot_pill_2', lang)}", key="btn_pill_2_b6", use_container_width=True):
                quick_sel = t('copilot_pill_2', lang)
        with col_p3:
            if st.button(f"🛡️ {t('copilot_pill_3', lang)}", key="btn_pill_3_b6", use_container_width=True):
                quick_sel = t('copilot_pill_3', lang)
                
        copilot_input = st.text_input(
            "Câu hỏi đàm phán:",
            value=quick_sel if quick_sel else "",
            placeholder=t("copilot_prompt_placeholder", lang),
            label_visibility="collapsed",
            key="txt_copilot_b6"
        )
        
        if st.button(t("copilot_btn_ask", lang), key="btn_run_copilot_b6") or quick_sel:
            q_txt = quick_sel if quick_sel else copilot_input
            if q_txt:
                with st.spinner("AI Sales Copilot đang phân tích biên lợi nhuận và lập phương án đàm phán..."):
                    copilot_ans = st.session_state.agent.negotiate_copilot(cur_res, q_txt)
                    st.session_state.copilot_history[cur_res["opportunity_id"]] = copilot_ans
                    
        active_copilot_ans = st.session_state.copilot_history.get(cur_res["opportunity_id"])
        if active_copilot_ans:
            st.markdown(clean_html(f"""
            <div class="copilot-msg-box">
                {active_copilot_ans}
            </div>
            """), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 5. Các nút thao tác Kết thúc
        c_fin1, c_fin2, c_fin3 = st.columns([1, 1, 1])
        with c_fin1:
            if st.button("💾 Lưu vào Pipeline CRM", use_container_width=True, type="primary", key="btn_save_crm_b6"):
                st.session_state.pipeline_history.append({
                    "OpportunityID": cur_res["opportunity_id"],
                    "CreatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Customer": parsed.get("company_name", ""),
                    "SalesRep": rep.get("FullName", ""),
                    "TotalAmount": eval_data.get("total_final_amount", 0),
                    "DiscountPct": eval_data.get("discount_pct", 0),
                    "Approval": eval_data.get("approval_level", "")
                })
                st.toast(t("toast_saved_pipeline", lang), icon="✨")
        with c_fin2:
            if st.button("◀ Xem lại Bước 5 (Báo giá)", use_container_width=True, key="btn_b6_back_b5"):
                st.session_state.wf_active_step = 5
                st.rerun()
        with c_fin3:
            if st.button("↺ Xử lý Yêu cầu Mới (Về Bước 1)", use_container_width=True, key="btn_b6_restart"):
                st.session_state.wf_active_step = 1
                st.session_state.manager_decision = None
                st.rerun()

    # ================================================================================================
    # ĐIỀU HƯỚNG HIỂN THỊ THEO CHẾ ĐỘ (WIZARD VS OVERVIEW)
    # ================================================================================================
    if st.session_state.wf_view_mode == "wizard":
        if active_step == 1:
            render_step_1()
        elif active_step == 2:
            render_step_2()
        elif active_step == 3:
            render_step_3()
        elif active_step == 4:
            render_step_4()
        elif active_step == 5:
            render_step_5()
        elif active_step == 6:
            render_step_6()
    else:
        # CHẾ ĐỘ TOÀN CẢNH (OVERVIEW): HIỂN THỊ ĐẦY ĐỦ 6 BƯỚC TUẦN TỰ
        render_step_1()
        st.markdown("<hr style='margin: 32px 0; border: none; border-top: 1px dashed var(--border-color, #cbd5e1);'>", unsafe_allow_html=True)
        render_step_2()
        st.markdown("<hr style='margin: 32px 0; border: none; border-top: 1px dashed var(--border-color, #cbd5e1);'>", unsafe_allow_html=True)
        render_step_3()
        st.markdown("<hr style='margin: 32px 0; border: none; border-top: 1px dashed var(--border-color, #cbd5e1);'>", unsafe_allow_html=True)
        render_step_4()
        st.markdown("<hr style='margin: 32px 0; border: none; border-top: 1px dashed var(--border-color, #cbd5e1);'>", unsafe_allow_html=True)
        render_step_5()
        st.markdown("<hr style='margin: 32px 0; border: none; border-top: 1px dashed var(--border-color, #cbd5e1);'>", unsafe_allow_html=True)
        render_step_6()


# ====================================================================================================
# TAB 2: PIPELINE XỬ LÝ HÀNG LOẠT & WEBHOOK INGESTION GATEWAY
# ====================================================================================================
with tab_batch:
    icon_layers = get_icon_tile("layers", "indigo")
    st.markdown(clean_html(f"""
    <div class="section-header-row">
        {icon_layers}
        <div class="section-header-title">{t("batch_title", lang)}</div>
    </div>
    """), unsafe_allow_html=True)
    
    # CỔNG TIẾP NHẬN WEBHOOK TỰ ĐỘNG
    with st.expander(f"⚡ {t('webhook_title', lang)}", expanded=False):
        st.markdown(clean_html(f"""
        <div class="bento-surface" style="padding: 18px 22px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px; color: var(--text-primary);">{t('webhook_endpoint_label', lang)}</span>
                <span class="badge-capsule badge-green">● Webhook Listener Active (Port 8501)</span>
            </div>
            <code style="display: block; padding: 10px 14px; background: var(--bg-surface-subtle); border-radius: 8px; font-size: 13px; color: var(--accent-indigo);">
                https://api.minhan.com.vn/v1/webhook/sales-inbound?token=sec_ma_77a9b0c2
            </code>
        </div>
        """), unsafe_allow_html=True)
        
        c_wh1, c_wh2 = st.columns(2)
        with c_wh1:
            if st.button(t("webhook_btn_simulate_email", lang), key="btn_sim_email", use_container_width=True):
                sim_text = "Từ: procurement@hoanglong-group.vn\nTiêu đề: Đơn đặt hàng bổ sung máy chủ Dell R750\nKính gửi Minh An, chúng tôi cần gấp 2 máy chủ Dell PowerEdge R750 và 4 Switch Cisco C9200L-24P giao về KCN Quế Võ. Yêu cầu giao trong 7 ngày."
                st.session_state.current_result = st.session_state.agent.process_request(sim_text, custom_opp_id="OPP-WEBHOOK-EMAIL-01")
                st.toast(t("webhook_success_msg", lang), icon="✉️")
        with c_wh2:
            if st.button(t("webhook_btn_simulate_crm", lang), key="btn_sim_crm", use_container_width=True):
                sim_text = "Từ CRM Hubspot Lead: Công ty CP Dược Phẩm An Khang\nNhu cầu: Cần báo giá 30 laptop Lenovo ThinkPad T14 Gen 4 và 30 màn hình Dell U2724D cho phòng R&D. Ngân sách 1 tỷ 2. Tiến độ trước ngày 25."
                st.session_state.current_result = st.session_state.agent.process_request(sim_text, custom_opp_id="OPP-WEBHOOK-CRM-02")
                st.toast(t("webhook_success_msg", lang), icon="⚡")
    
    col_batch_src, _ = st.columns([6, 4])
    with col_batch_src:
        batch_source = st.radio(
            t("batch_radio_label", lang),
            [t("batch_radio_sample", lang), t("batch_radio_upload", lang)],
            horizontal=True
        )
    
    batch_list = []
    sample_requests_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_requests.json")
    if batch_source == t("batch_radio_sample", lang):
        with open(sample_requests_file, encoding="utf-8") as f:
            batch_list = json.load(f)
    else:
        uploaded_batch = st.file_uploader("Chọn file danh sách (.csv, .xlsx, .json):", type=["xlsx", "csv", "json"])
        if uploaded_batch:
            try:
                raw_bytes = uploaded_batch.read()
                parsed_res = UniversalFileReader.load_any_file(uploaded_batch.name, raw_bytes)
                if parsed_res.get("kind") == "tabular":
                    first_sheet = list(parsed_res["sheets"].keys())[0]
                    b_df = parsed_res["sheets"][first_sheet]
                    
                    # Data Validation Guardrail for Batch Ingestion
                    is_valid_b, b_errors = DataValidationGuardrail.validate_file_structure(b_df)
                    if not is_valid_b:
                        for err_msg in b_errors:
                            st.error(err_msg)
                    else:
                        col_c = next((c for c in b_df.columns if str(c).lower() in ["raw_text", "noi_dung_yeu_cau", "content", "request", "mo_ta"]), b_df.columns[0])
                        col_vals = b_df[col_c].astype(str).tolist()
                        batch_list = [
                            {"id": f"REQ-BATCH-{idx+1:05d}", "title": f"Yêu cầu #{idx+1}", "raw_text": val}
                            for idx, val in enumerate(col_vals)
                        ]
                        st.success(f"Đã nạp {len(batch_list)} yêu cầu từ file thành công!")

            except Exception as e:
                st.error(f"Lỗi đọc file: {e}")

    if batch_list:
        st.write("")
        if st.button(t("btn_run_batch", lang), use_container_width=True):
            if not hasattr(st.session_state.agent, "process_batch"):
                p_df, s_df, pol_df = DataLoader.load_default_data()
                st.session_state.agent = MinhAnSalesAgent(p_df, s_df, pol_df)
                
            p_bar = st.progress(0)
            status_box = st.empty()
            status_box.markdown(
                f'<div style="font-size:13px; color:var(--text-muted); margin-bottom:8px;">⚡ Đang thẩm định và phân tích tự động {len(batch_list):,} yêu cầu...</div>',
                unsafe_allow_html=True
            )
            def on_progress(p):
                p_bar.progress(p)
                
            res_df, meta = st.session_state.agent.process_batch(batch_list, progress_callback=on_progress)
            p_bar.progress(1.0)
            status_box.empty()
            
            st.success(f"⚡ Hoàn tất xử lý toàn bộ danh sách {meta['total_items']:,} yêu cầu trong {meta['elapsed_seconds']:.2f}s! Tốc độ đạt ~{meta['speed_req_per_sec']:,.0f} yêu cầu/giây.")
            
            # Thống kê nhanh kết quả xử lý
            bs1, bs2, bs3, bs4 = st.columns(4)
            with bs1:
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value">{len(res_df)}</div><div class="stat-kpi-label">{t("batch_kpi_total", lang)}</div></div>'), unsafe_allow_html=True)
            with bs2:
                suf_c = len(res_df[res_df["Đầy đủ TT"] == "Có"]) if ("Đầy đủ TT" in res_df.columns and not res_df.empty) else 0
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value">{suf_c} / {len(res_df)}</div><div class="stat-kpi-label">{t("batch_kpi_sufficient", lang)}</div></div>'), unsafe_allow_html=True)
            with bs3:
                mgr_c = len(res_df[res_df["Cấp duyệt"].str.contains("Trưởng phòng|Ban Giám đốc", na=False)]) if ("Cấp duyệt" in res_df.columns and not res_df.empty) else 0
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value">{mgr_c}</div><div class="stat-kpi-label">{t("batch_kpi_escalated", lang)}</div></div>'), unsafe_allow_html=True)
            with bs4:
                val_c = float(res_df["Giá trị đơn (VNĐ)"].sum()) if ("Giá trị đơn (VNĐ)" in res_df.columns and not res_df.empty) else 0.0
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value">{val_c:,.0f} đ</div><div class="stat-kpi-label">{t("batch_kpi_pipeline", lang)}</div></div>'), unsafe_allow_html=True)

                
            st.write("")
            render_safe_dataframe(res_df, num_formats={"Giá trị đơn (VNĐ)": "%,.0f đ"}, width="stretch", hide_index=True)
            st.session_state.batch_result_df = res_df
            
            # ====================================================================================
            # TRỰC QUAN HÓA PIPELINE HÀNG LOẠT (BATCH CHARTS)
            # ====================================================================================
            st.markdown(clean_html(f"""
            <div class="section-header-row" style="margin-top: 24px; margin-bottom: 8px;">
                {get_icon_tile("sparkles", "cyan")}
                <div class="section-header-title">{t("charts_batch_title", lang)}</div>
            </div>
            """), unsafe_allow_html=True)
            
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                try:
                    fig_b_out, ins_b_out, df_b_out = chart_batch_outcome_donut(res_df, is_dark=is_dark, lang=lang)
                    render_chart_card(fig_b_out, "Tỷ lệ phê duyệt hồ sơ", ins_b_out, df_b_out, "batch_outcomes", lang=lang)
                except Exception as e:
                    st.info(f"Biểu đồ phân loại: {e}")
                    
                try:
                    fig_b_funnel, ins_b_funnel, df_b_funnel = chart_pipeline_funnel(res_df, is_dark=is_dark, lang=lang)
                    render_chart_card(fig_b_funnel, "Phễu chuyển đổi quy trình 5 bước", ins_b_funnel, df_b_funnel, "batch_funnel", lang=lang)
                except Exception as e:
                    st.info(f"Biểu đồ phễu: {e}")
                    
            with b_col2:
                try:
                    fig_b_rep, ins_b_rep, df_b_rep = chart_batch_sales_rep_workload(res_df, is_dark=is_dark, lang=lang)
                    render_chart_card(fig_b_rep, "Phân bổ tải NVKD", ins_b_rep, df_b_rep, "batch_reps", lang=lang)
                except Exception as e:
                    st.info(f"Biểu đồ NVKD: {e}")
                    
                try:
                    fig_b_val, ins_b_val, df_b_val = chart_batch_order_value_distribution(res_df, is_dark=is_dark, lang=lang)
                    render_chart_card(fig_b_val, "Phân tán giá trị đơn hàng", ins_b_val, df_b_val, "batch_values", lang=lang)
                except Exception as e:
                    st.info(f"Biểu đồ giá trị đơn: {e}")

# ====================================================================================================
# TAB 3: TRUNG TÂM THỐNG KÊ & PHÂN TÍCH TÀI CHÍNH CHUẨN 8 BƯỚC
# ====================================================================================================
with tab_analytics:
    icon_chart = get_icon_tile("sparkles", "pink")
    st.markdown(clean_html(f"""
    <div class="section-header-row">
        {icon_chart}
        <div class="section-header-title">{t("analytics_main_title", lang)}</div>
    </div>
    """), unsafe_allow_html=True)
    
    # 1. KHU VỰC TIẾP NHẬN TẬP TIN ĐA ĐỊNH DẠNG (UNIVERSAL INGESTION)
    st.markdown(clean_html(f"""
    <div class="bento-surface">
        <div style="font-weight: 700; font-size: 16px; margin-bottom: 6px;">{t("universal_uploader_title", lang)}</div>
        <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">{t("universal_uploader_desc", lang)}</div>
    </div>
    """), unsafe_allow_html=True)
    
    multi_uploaded_files = st.file_uploader(
        "Tải lên một hoặc nhiều tệp dữ liệu:",
        type=["xlsx", "xls", "csv", "tsv", "json", "xml", "docx", "pdf", "txt", "md", "eml", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if multi_uploaded_files:
        for u_file in multi_uploaded_files:
            file_bytes = u_file.read()
            try:
                read_res = UniversalFileReader.load_any_file(u_file.name, file_bytes, gemini_client=st.session_state.agent.gemini_client)
                
                # Tabular files handling
                if read_res.get("kind") == "tabular":
                    sheets = read_res["sheets"]
                    selected_sheet = list(sheets.keys())[0]
                    if len(sheets) > 1:
                        selected_sheet = st.selectbox(f"Chọn sheet dữ liệu từ '{u_file.name}':", list(sheets.keys()))
                    raw_df = sheets[selected_sheet]
                    
                    # 1. BỘ KIỂM TRA TÍNH HỢP LỆ DỮ LIỆU ĐẦU VÀO (DATA VALIDATION GUARDRAIL)
                    is_valid_struct, struct_errors = DataValidationGuardrail.validate_file_structure(raw_df)
                    if not is_valid_struct:
                        for err_msg in struct_errors:
                            st.error(err_msg)
                        st.session_state.uploaded_file_invalid = True
                        st.session_state.uploaded_analytics_df = None
                        st.session_state.has_quantitative_metrics = False
                        continue
                    
                    st.session_state.uploaded_file_invalid = False
                    
                    # Clean and standardize
                    cleaned_df = DataQualityCleaner.clean_and_standardize(raw_df)
                    
                    # Smart Schema Mapping Suggestions
                    suggested_mapping = DataQualityCleaner.suggest_schema_mapping(cleaned_df.columns.tolist(), sample_df=cleaned_df)
                    mapping_dict = {k: v["mapped_column"] for k, v in suggested_mapping.items() if v.get("confidence", 0) >= 40}
                    st.session_state.schema_mapping = mapping_dict
                    
                    # 2. KIỂM TRA SỰ TỒN TẠI CỦA CHỈ SỐ ĐỊNH LƯỢNG (QUANTITATIVE METRICS GUARDRAIL)
                    has_metrics = DataValidationGuardrail.has_quantitative_metrics(cleaned_df, mapping_dict)
                    st.session_state.has_quantitative_metrics = has_metrics
                    
                    if not has_metrics:
                        # Đổi banner màu xanh thành banner cảnh báo màu đỏ
                        st.error("Lỗi cấu trúc dữ liệu: Không tìm thấy cột số liệu định lượng nào hợp lệ để tính toán chỉ số KPI và vẽ biểu đồ.")
                        st.session_state.uploaded_analytics_df = cleaned_df
                        st.session_state.data_quality_report = DataQualityCleaner.audit_dataframe(cleaned_df)
                    else:
                        # Tự động ánh xạ chuẩn hóa sang canonical columns
                        std_df = DataQualityCleaner.apply_schema_mapping(cleaned_df, mapping_dict)
                        
                        # Tự động đồng bộ cột doanh thu nếu chưa có total_price
                        rev_col = StatisticalAnalyticsEngine.resolve_revenue_column(std_df)
                        if rev_col and rev_col != "total_price" and "total_price" not in std_df.columns:
                            std_df["total_price"] = std_df[rev_col]
                        
                        st.session_state.uploaded_analytics_df = std_df
                        st.session_state.data_quality_report = DataQualityCleaner.audit_dataframe(std_df)
                        
                        st.success(f"✓ Đã đọc tệp bảng tính '{u_file.name}' thành công ({len(std_df)} dòng, {len(std_df.columns)} cột).")
                    
                # Document / Image files handling
                elif read_res.get("kind") in ["document", "image"]:
                    extracted_text = read_res.get("text", "")
                    st.success(f"✓ Đã đọc nội dung văn bản từ '{u_file.name}' ({len(extracted_text)} ký tự).")
                    with st.expander(f"Xem nội dung trích xuất từ '{u_file.name}':", expanded=True):
                        st.text_area("Nội dung trích xuất:", value=extracted_text, height=180, label_visibility="collapsed")
                        if st.button("🚀 Đưa vào Xử lý theo Sơ đồ Minh An", key=f"btn_proc_doc_{u_file.name}"):
                            st.session_state.current_result = st.session_state.agent.process_request(extracted_text)
                            st.toast("Đã chuyển yêu cầu vào Tab 1 để xử lý!", icon="✨")
            except Exception as read_err:
                st.error(f"Lỗi đọc tệp '{u_file.name}': {read_err}")
                
    # Hiển thị dữ liệu mẫu nếu chưa tải tệp nào và không bị chặn bởi tệp lỗi
    if st.session_state.uploaded_analytics_df is None and not st.session_state.get("uploaded_file_invalid", False):
        default_catalog = st.session_state.catalog_df.copy()
        default_catalog["total_price"] = default_catalog["UnitPrice"] * default_catalog["AvailableStock"]
        default_catalog["customer_name"] = "Khách hàng B2B Doanh nghiệp"
        default_catalog["order_date"] = datetime.now().strftime("%Y-%m-%d")
        st.session_state.uploaded_analytics_df = default_catalog
        st.session_state.data_quality_report = DataQualityCleaner.audit_dataframe(default_catalog)
        st.session_state.has_quantitative_metrics = True

    if st.session_state.get("uploaded_file_invalid", False):
        st.markdown(clean_html("""
        <div class="bento-surface" style="border: 1px solid #ef4444; background: rgba(239, 68, 68, 0.05); padding: 18px 22px; text-align: center; margin-top: 15px;">
            <div style="font-size: 15px; font-weight: 700; color: #ef4444; margin-bottom: 6px;">⛔ Tệp dữ liệu không hợp lệ</div>
            <div style="font-size: 13px; color: var(--text-secondary);">Hệ thống đã dừng xử lý do vi phạm quy tắc cấu trúc tệp dữ liệu. Vui lòng kiểm tra lại số cột (tối đa 200) và số dòng (tối thiểu 2 dòng) trước khi tải lại để tiếp tục phân tích.</div>
        </div>
        """), unsafe_allow_html=True)

    curr_df = st.session_state.uploaded_analytics_df
    
    if curr_df is not None and not curr_df.empty:
        # 2. XEM TRƯỚC DỮ LIỆU & BÁO CÁO CHẤT LƯỢNG (DATA QUALITY AUDIT)
        col_prev1, col_prev2 = st.columns([6, 4])
        with col_prev1:
            st.markdown(clean_html(f'<div class="section-header-title">{t("preview_data_title", lang)}</div>'), unsafe_allow_html=True)
            st.dataframe(curr_df.head(10), width="stretch", hide_index=True)
            
        with col_prev2:
            st.markdown(clean_html(f'<div class="section-header-title">{t("data_quality_title", lang)}</div>'), unsafe_allow_html=True)
            audit = st.session_state.data_quality_report
            score = audit.get("quality_score", 100) if audit else 100
            score_color = "badge-green" if score >= 85 else ("badge-amber" if score >= 70 else "badge-red")
            
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="padding: 16px 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; color: var(--text-primary);">{t('quality_score_label', lang)}</span>
                    <span class="badge-capsule {score_color}">{score} / 100 Điểm</span>
                </div>
                <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.7;">
                    • <b>Tổng bản ghi:</b> {len(curr_df)} dòng • <b>Số cột:</b> {len(curr_df.columns)}<br>
                    • <b>Dòng trùng lặp:</b> {audit.get('duplicate_count', 0)} dòng ({audit.get('duplicate_pct', 0)}%)<br>
                    • <b>Cột có ngoại lệ (Outliers):</b> {len(audit.get('outliers', {}))} cột phát hiện
                </div>
            </div>
            """), unsafe_allow_html=True)

        # 3. SCHEMA MAPPING INTERACTIVE INTERFACE
        is_metrics_valid = st.session_state.get("has_quantitative_metrics", True)
        
        with st.expander(f"🧩 {t('schema_mapping_title', lang)}", expanded=(not is_metrics_valid)):
            st.markdown(f"<div style='font-size: 13px; color: var(--text-muted); margin-bottom: 12px;'>{t('schema_mapping_desc', lang)}</div>", unsafe_allow_html=True)
            
            if not is_metrics_valid:
                st.error("Lỗi cấu trúc dữ liệu: Không tìm thấy cột số liệu định lượng nào hợp lệ để tính toán chỉ số KPI và vẽ biểu đồ.")
                
            available_cols = ["(Không có)"] + curr_df.columns.tolist()
            map_cols_ui = st.columns(3)
            temp_mapping = {}
            for idx, (canon_key, meta) in enumerate(config.CANONICAL_COLUMNS.items()):
                target_col = map_cols_ui[idx % 3]
                current_val = st.session_state.schema_mapping.get(canon_key)
                selected_idx = available_cols.index(current_val) if current_val in available_cols else 0
                with target_col:
                    lbl = meta["label_vi"] if lang == "vi" else meta["label_en"]
                    chosen = st.selectbox(lbl, available_cols, index=selected_idx, key=f"map_select_{canon_key}")
                    temp_mapping[canon_key] = chosen if (chosen and chosen not in ["(Không có)", "-- Không sử dụng --"]) else None
                    
            user_has_metrics = DataValidationGuardrail.has_quantitative_metrics(curr_df, temp_mapping)
            
            if not user_has_metrics:
                st.button(
                    "🔒 Tiếp tục sang bước Làm sạch / Phân tích (Đã khóa)",
                    key="btn_confirm_map_engine_disabled",
                    disabled=True,
                    use_container_width=True
                )
                st.caption("ℹ️ Nút tiếp tục đã bị khóa cho đến khi bạn ánh xạ ít nhất một cột số liệu định lượng hoặc nạp tệp dữ liệu hợp lệ khác.")
            else:
                if st.button(t("btn_apply_mapping", lang), key="btn_confirm_map_engine", use_container_width=True):
                    st.session_state.schema_mapping = temp_mapping
                    st.session_state.has_quantitative_metrics = True
                    std_mapped_df = DataQualityCleaner.apply_schema_mapping(curr_df, temp_mapping)
                    st.session_state.uploaded_analytics_df = std_mapped_df
                    st.toast("Đã áp dụng ánh xạ cột chuẩn hóa vào trung tâm thống kê!", icon="✨")
                    st.rerun()

        st.markdown("---")
        
        if not is_metrics_valid:
            st.markdown(clean_html("""
            <div class="bento-surface" style="border: 1px solid #ef4444; background: rgba(239, 68, 68, 0.05); padding: 20px 24px; text-align: center; margin-top: 15px;">
                <div style="font-size: 16px; font-weight: 700; color: #ef4444; margin-bottom: 8px;">⛔ Đã khóa bước Phân tích Thống kê & Vẽ biểu đồ</div>
                <div style="font-size: 13px; color: var(--text-secondary); max-width: 650px; margin: 0 auto; line-height: 1.6;">
                    Lỗi cấu trúc dữ liệu: Không tìm thấy cột số liệu định lượng nào hợp lệ để tính toán chỉ số KPI và vẽ biểu đồ.<br>
                    Vui lòng chọn cột số ở mục <b>Ánh xạ cột dữ liệu</b> ở trên hoặc nạp tệp dữ liệu hợp lệ khác.
                </div>
            </div>
            """), unsafe_allow_html=True)
        else:
            # 4. CHỈ SỐ VẬN HÀNH & KIỂM SOÁT QUY TRÌNH DOANH NGHIỆP MINH AN
            fin_kpis = StatisticalAnalyticsEngine.compute_financial_kpis(curr_df)
            
            st.markdown(clean_html(f"""
            <div class="section-header-row">
                {get_icon_tile("shield_check", "indigo")}
                <div class="section-header-title">Hệ thống Giám sát Quy trình & Chỉ số Vận hành B2B (Minh An)</div>
            </div>
            """), unsafe_allow_html=True)
            
            fk1, fk2, fk3, fk4 = st.columns(4)
            with fk1:
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value" style="color:#10B981;">100%</div><div class="stat-kpi-label">Tỷ lệ Tạo Hồ sơ & Dự thảo Báo giá</div></div>'), unsafe_allow_html=True)
            with fk2:
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value" style="color:#6366F1;">100% Chuẩn Hóa</div><div class="stat-kpi-label">Chất lượng Đề xuất (0% Sót SKU / Lệch Giá)</div></div>'), unsafe_allow_html=True)
            with fk3:
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value" style="color:#F59E0B;">Định Danh NVKD</div><div class="stat-kpi-label">Cảnh báo Điểm nghẽn (Chờ duyệt / Thiếu TT)</div></div>'), unsafe_allow_html=True)
            with fk4:
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value" style="color:#06B6D4;">~180 Req / Tuần</div><div class="stat-kpi-label">Khối lượng 6 NVKD (Pipeline: {fin_kpis["total_revenue"]:,.0f} đ)</div></div>'), unsafe_allow_html=True)

            st.write("")
            
            # 5. TIỂU MỤC THỐNG KÊ & BÁO CÁO CHUYÊN SÂU
            st.markdown('<div class="report-subtabs-wrap">', unsafe_allow_html=True)
            stat_sub1, stat_sub2, stat_sub3, stat_sub4 = st.tabs([
                t("analytics_sub_funnel", lang),
                t("analytics_sub_risks", lang),
                t("analytics_sub_team", lang),
                t("analytics_sub_business", lang)
            ])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # SUB-TAB 1: PHỄU CHUYỂN ĐỔI & TIẾN ĐỘ QUY TRÌNH (Yêu cầu -> Hồ sơ -> Bản nháp)
            with stat_sub1:
                st.markdown(f"<div style='font-size: 13px; color: var(--text-muted); margin-bottom: 12px;'>{t('analytics_sub_funnel_desc', lang)}</div>", unsafe_allow_html=True)
                fig_funnel, ins_funnel, df_funnel = chart_pipeline_funnel(curr_df, is_dark=is_dark, lang=lang)
                render_chart_card(
                    fig_funnel,
                    t("chart_title_pipeline_funnel", lang),
                    ins_funnel,
                    data_df=df_funnel,
                    card_id="funnel_deep_dive",
                    lang=lang
                )
                
            # SUB-TAB 2: ĐIỂM NGHẼN & CẢNH BÁO RỦI RO VẬN HÀNH (4 Vấn đề cốt lõi)
            with stat_sub2:
                st.markdown(f"<div style='font-size: 13px; color: var(--text-muted); margin-bottom: 12px;'>{t('analytics_sub_risks_desc', lang)}</div>", unsafe_allow_html=True)
                fig_risk, ins_risk, df_risk = chart_operational_risk_bottlenecks(curr_df, is_dark=is_dark, lang=lang)
                render_chart_card(
                    fig_risk,
                    t("chart_title_risk_matrix", lang),
                    ins_risk,
                    data_df=df_risk,
                    card_id="risk_deep_dive",
                    lang=lang
                )
                
            # SUB-TAB 3: HIỆU SUẤT & PHÂN BỔ KHỐI LƯỢNG 6 NVKD
            with stat_sub3:
                st.markdown(f"<div style='font-size: 13px; color: var(--text-muted); margin-bottom: 12px;'>{t('analytics_sub_team_desc', lang)}</div>", unsafe_allow_html=True)
                fig_team, ins_team, df_team = chart_sales_team_performance(curr_df, is_dark=is_dark, lang=lang)
                render_chart_card(
                    fig_team,
                    t("chart_title_team_perf", lang),
                    ins_team,
                    data_df=df_team,
                    card_id="team_perf_deep_dive",
                    lang=lang
                )

            # SUB-TAB 4: PHÂN TÍCH KINH DOANH & PHÂN KHÚC KHÁCH HÀNG B2B
            with stat_sub4:
                st.markdown(f"<div style='font-size: 13px; color: var(--text-muted); margin-bottom: 12px;'>{t('analytics_sub_business_desc', lang)}</div>", unsafe_allow_html=True)
                
                # 4 thẻ tài chính
                fsub1, fsub2, fsub3, fsub4 = st.columns(4)
                with fsub1:
                    st.metric("Tổng Doanh Thu Ghi Nhận", f"{fin_kpis['total_revenue']:,.0f} đ")
                with fsub2:
                    st.metric("Lợi Nhuận Gộp Ước Tính", f"{fin_kpis['gross_profit']:,.0f} đ")
                with fsub3:
                    st.metric("Biên Lợi Nhuận Gộp", f"{fin_kpis['gross_margin_pct']:.1f}%")
                with fsub4:
                    st.metric("Giá Trị Đơn Bình Quân (AOV)", f"{fin_kpis['aov']:,.0f} đ")
                    
                st.write("")
                # RFM & Phân nhóm
                segments_df = StatisticalAnalyticsEngine.segment_customers_rfm(curr_df)
                if not segments_df.empty:
                    st.markdown("<div style='font-size: 13px; color: var(--text-muted); margin-bottom: 8px;'><b>Phân hạng Khách hàng RFM:</b></div>", unsafe_allow_html=True)
                    render_safe_dataframe(segments_df, num_formats={"TotalSpend": "%,.0f đ", "AOV": "%,.0f đ"}, width="stretch", hide_index=True)
                    
                # Biểu đồ tài chính Plotly
                plotly_charts = StatisticalAnalyticsEngine.build_financial_charts(curr_df, is_dark=is_dark)
                if plotly_charts:
                    pc1, pc2 = st.columns(2)
                    with pc1:
                        if "donut_revenue" in plotly_charts:
                            render_chart_card(plotly_charts["donut_revenue"], "Tỷ Trọng Doanh Thu Danh Mục", "", data_df=curr_df, card_id="stat_donut_rev", lang=lang)
                    with pc2:
                        if "bar_customer" in plotly_charts:
                            render_chart_card(plotly_charts["bar_customer"], "Top Doanh Thu Khách Hàng", "", data_df=curr_df, card_id="stat_bar_cust", lang=lang)
                            
                    if "box_distribution" in plotly_charts:
                        render_chart_card(plotly_charts["box_distribution"], "Phân Phối Giá Trị Đơn Hàng & Ngoại Lệ", "", data_df=curr_df, card_id="stat_box_dist", lang=lang)

                # Trình Tùy biến Biểu đồ Tương tác Động
                st.markdown("---")
                st.markdown(clean_html(f"""
                <div class="section-header-row" style="margin-top: 14px; margin-bottom: 8px;">
                    {get_icon_tile("sparkles", "indigo")}
                    <div class="section-header-title">{t("charts_dynamic_title", lang)}</div>
                </div>
                """), unsafe_allow_html=True)
                
                c_d1, c_d2, c_d3, c_d4 = st.columns([1.5, 1.5, 1.5, 1.5])
                with c_d1:
                    sel_chart_type = st.selectbox(
                        "Loại biểu đồ:" if lang == "vi" else "Chart Type:",
                        ["Cột (Bar)", "Đường (Line)", "Tròn (Donut)", "Phân tán (Scatter)", "Hộp (Boxplot)", "Nhiệt tương quan (Heatmap)"],
                        key="stat_dyn_chart_type"
                    )
                with c_d2:
                    all_cols = curr_df.columns.tolist()
                    def_x = "product_name" if "product_name" in all_cols else (all_cols[0] if all_cols else "")
                    sel_x = st.selectbox("Trục X / Phân loại:" if lang == "vi" else "X-Axis / Category:", all_cols, index=all_cols.index(def_x) if def_x in all_cols else 0, key="stat_dyn_x_col")
                with c_d3:
                    num_cols = ["(Không chọn)"] + curr_df.select_dtypes(include=[np.number]).columns.tolist()
                    def_y = "total_price" if "total_price" in num_cols else ("revenue" if "revenue" in num_cols else (num_cols[1] if len(num_cols) > 1 else "(Không chọn)"))
                    sel_y = st.selectbox("Trục Y / Giá trị (Số):" if lang == "vi" else "Y-Axis / Metric:", num_cols, index=num_cols.index(def_y) if def_y in num_cols else 0, key="stat_dyn_y_col")
                with c_d4:
                    cat_cols = ["(Không chọn)"] + curr_df.select_dtypes(include=['object', 'category']).columns.tolist()
                    sel_group = st.selectbox("Nhóm theo (Màu):" if lang == "vi" else "Group by (Color):", cat_cols, key="stat_dyn_group_col")
                    
                y_param = sel_y if sel_y != "(Không chọn)" else None
                g_param = sel_group if sel_group != "(Không chọn)" else None
                
                try:
                    fig_dyn, ins_dyn = chart_dynamic_builder(curr_df, sel_chart_type, sel_x, y_param, g_param, is_dark=is_dark, lang=lang)
                    render_chart_card(fig_dyn, f"Biểu đồ tùy biến: {sel_x}" + (f" vs {y_param}" if y_param else ""), ins_dyn, curr_df[[sel_x] + ([y_param] if y_param else [])], "dynamic_explorer", lang=lang)
                except Exception as e:
                    st.info(f"Không thể dựng biểu đồ tùy biến: {e}")

            # ====================================================================================
            # 6. HỆ THỐNG BÁO CÁO KINH DOANH ĐỘNG (CHUẨN HÓA 6 PHẦN) & XUẤT FILE WORD (.DOCX)
            # ====================================================================================
            st.write("")
            st.markdown(clean_html(f"""
            <div class="section-header-row notranslate" translate="no" style="margin-top: 24px; margin-bottom: 12px;">
                {get_icon_tile("file_text", "indigo")}
                <div>
                    <div class="section-header-title">BÁO CÁO KINH DOANH & PHÂN TÍCH DỮ LIỆU ĐỘNG (DYNAMIC REPORT VIEW)</div>
                    <div style="font-size: 13px; color: var(--text-muted);">Cấu trúc chuẩn hóa 6 phần • Phân tích động 100% theo dữ liệu thực tế • Xuất file Word (.docx) hoàn chỉnh</div>
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            # Khởi tạo dữ liệu Báo cáo Động từ DataFrame hiện tại
            active_file_title = "Du_Lieu_Phan_Tich_Minh_An"
            if multi_uploaded_files and len(multi_uploaded_files) > 0:
                active_file_title = multi_uploaded_files[0].name
                
            report_pkg = DynamicBusinessReportGenerator.generate_report_data(
                curr_df,
                file_name=active_file_title,
                audit_info=st.session_state.data_quality_report
            )
            
            s1_d = report_pkg["section_1"]
            s2_d = report_pkg["section_2"]
            s3_d = report_pkg["section_3"]
            s4_d = report_pkg["section_4"]
            s5_d = report_pkg["section_5"]
            s6_d = report_pkg["section_6"]

            # ------------------------------------------------------------------------------------
            # PHẦN 1: TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY) - DẪN CHỨNG TỔNG QUAN & ĐỘ PHỦ DỮ LIỆU
            # ------------------------------------------------------------------------------------
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--accent-indigo); margin-bottom: 18px;">
                <div style="font-size: 16px; font-weight: 800; color: var(--accent-indigo); margin-bottom: 8px;">
                    1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)
                </div>
                <div style="font-size: 14px; color: var(--text-primary); line-height: 1.8; margin-bottom: 12px;">
                    {s1_d.get('executive_narrative', '')}
                </div>
                <div style="font-size: 13.5px; color: var(--text-secondary); line-height: 1.8; padding-top: 8px; border-top: 1px solid var(--border-card);">
                    • <b>Tên bộ dữ liệu phân tích:</b> <span style="font-weight: 700; color: var(--text-primary);">{s1_d['dataset_name']}</span><br>
                    • <b>Quy mô dữ liệu:</b> {s1_d['total_rows']:,} dòng dữ liệu • {s1_d['total_cols']} trường thông tin (Độ hoàn thiện: <b>{s1_d.get('data_completeness_pct', 100):.1f}%</b>)<br>
                    • <b>Bối cảnh & Loại hình:</b> {s1_d['context_description']}
                </div>
            </div>
            """), unsafe_allow_html=True)

            if s1_d.get("quantitative_summary"):
                st.markdown(clean_html('<div style="font-size: 13.5px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">📊 Tổng giá trị tích lũy và Diễn giải chỉ số định lượng kèm dẫn chứng cụ thể:</div>'), unsafe_allow_html=True)
                s1_cols_ui = st.columns(min(4, max(1, len(s1_d["quantitative_summary"]))))
                for idx_q, qs in enumerate(s1_d["quantitative_summary"]):
                    target_c = s1_cols_ui[idx_q % len(s1_cols_ui)]
                    with target_c:
                        st.markdown(clean_html(f"""
                        <div class="stat-kpi-card" style="padding: 14px 16px; margin-bottom: 12px;">
                            <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">{qs['column_name']}</div>
                            <div class="stat-kpi-value" style="font-size: 20px; line-height: 28px;">{qs['sum']:,.0f}</div>
                            <div style="font-size: 11.5px; color: var(--accent-indigo); margin-top: 4px;">Độ phủ: <b>{qs['coverage_text']}</b></div>
                            <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px; line-height: 1.4;">
                                Trung bình: <b>{qs['mean']:,.1f}</b> | Trung vị: <b>{qs['median']:,.1f}</b><br>
                                Cực trị: <b>{qs.get('min', 0):,.0f}</b> ➔ <b>{qs.get('max', 0):,.0f}</b>
                            </div>
                        </div>
                        """), unsafe_allow_html=True)

            # ------------------------------------------------------------------------------------
            # PHẦN 2: DASHBOARD KPI (SO SÁNH KỲ GẦN NHẤT VS KỲ LIỀN TRƯỚC) - KÈM DẪN CHỨNG DỮ LIỆU
            # ------------------------------------------------------------------------------------
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--accent-cyan); margin-bottom: 18px; margin-top: 10px;">
                <div style="font-size: 16px; font-weight: 800; color: #0284C7; margin-bottom: 6px;">
                    2. DASHBOARD KPI (SO SÁNH KỲ GẦN NHẤT VS KỲ LIỀN TRƯỚC)
                </div>
                <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">
                    Đối chiếu kỳ gần nhất với kỳ liền trước kèm dẫn chứng dữ liệu cụ thể cho từng chỉ số. Các chỉ số không có trong file dữ liệu được thể hiện bằng dấu "—" nhằm bảo đảm tính trung thực dữ liệu, tuyệt đối không tự ý suy đoán số liệu tài chính khi file nguồn không cung cấp.
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            kpi_df = pd.DataFrame(s2_d["kpi_table"])
            if not kpi_df.empty:
                kpi_df_display = kpi_df.rename(columns={
                    "metric": "Chỉ số",
                    "current": "Giá trị (Kỳ gần nhất)",
                    "previous": "Kỳ trước",
                    "change": "Thay đổi %",
                    "status": "Đánh giá & Xu hướng",
                    "evidence": "Dẫn chứng dữ liệu thực tế"
                })
                display_cols = [c for c in ["Chỉ số", "Giá trị (Kỳ gần nhất)", "Kỳ trước", "Thay đổi %", "Đánh giá & Xu hướng", "Dẫn chứng dữ liệu thực tế"] if c in kpi_df_display.columns]
                render_safe_dataframe(kpi_df_display[display_cols], width="stretch", hide_index=True)
                
            if s2_d.get("kpi_analysis_notes"):
                st.markdown(clean_html(f"""
                <div style="background: rgba(2, 132, 199, 0.08); border-left: 3px solid #0284C7; padding: 12px 16px; border-radius: 8px; font-size: 13px; color: var(--text-primary); margin-top: 10px; margin-bottom: 14px; line-height: 1.7;">
                    💡 <b>Phân tích xu hướng & Dẫn chứng 2 kỳ:</b> {s2_d['kpi_analysis_notes']}
                </div>
                """), unsafe_allow_html=True)

            # Biểu đồ trực quan hóa KPI so sánh 2 kỳ với màu sắc hiện đại 2026 SaaS
            try:
                fig_kpi, ins_kpi, df_kpi_plot = chart_report_kpi_comparison(s2_d.get("kpi_table", []), is_dark=is_dark, lang=lang)
                if fig_kpi is not None:
                    render_chart_card(fig_kpi, "Biểu Đồ Đối Chiếu KPI: Kỳ Gần Nhất vs Kỳ Liền Trước", ins_kpi, df_kpi_plot, "report_kpi_comp", lang=lang)
            except Exception:
                pass

            # ------------------------------------------------------------------------------------
            # PHẦN 3: PHÂN TÍCH CHUYÊN ĐỀ (CHI TIẾT TỪNG CỘT SỐ HỌC KÈM DẪN CHỨNG CỰC TRỊ)
            # ------------------------------------------------------------------------------------
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--accent-pink); margin-bottom: 18px; margin-top: 20px;">
                <div style="font-size: 16px; font-weight: 800; color: #D946EF; margin-bottom: 6px;">
                    3. PHÂN TÍCH CHUYÊN ĐỀ THEO TỪNG CHỈ SỐ ĐỊNH LƯỢNG
                </div>
                <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">
                    Tự động phân tích thống kê chi tiết và giải thích dễ hiểu từng chỉ số định lượng: Trung bình, Trung vị, Độ lệch chuẩn, Cực trị có dẫn chứng thực thể, Khoảng tứ phân vị (IQR) và Hệ số biến thiên (CV).
                </div>
            </div>
            """), unsafe_allow_html=True)

            thematic_list = s3_d.get("thematic_analysis", [])
            if thematic_list:
                try:
                    fig_th, ins_th, df_th_plot = chart_report_thematic_distribution(thematic_list, is_dark=is_dark, lang=lang)
                    if fig_th is not None:
                        render_chart_card(fig_th, "Đối Chiếu Phân Phối Mean vs Median Từng Chỉ Số", ins_th, df_th_plot, "report_thematic_dist", lang=lang)
                except Exception:
                    pass

                for th in thematic_list:
                    with st.expander(f"📈 Phân tích chuyên sâu chỉ số '{th['column']}' (Tổng quy mô: {th['sum']:,.0f})", expanded=True):
                        th_c1, th_c2, th_c3, th_c4 = st.columns(4)
                        with th_c1:
                            st.metric("Trung bình (Mean)", f"{th['mean']:,.1f}")
                        with th_c2:
                            st.metric("Trung vị (Median)", f"{th['median']:,.1f}")
                        with th_c3:
                            st.metric("Độ lệch chuẩn (Std)", f"{th['std']:,.1f}")
                        with th_c4:
                            min_disp = f"{th['min']:,.0f}" + (f" ({th.get('min_name', '')})" if th.get('min_name') else "")
                            max_disp = f"{th['max']:,.0f}" + (f" ({th.get('max_name', '')})" if th.get('max_name') else "")
                            st.metric("Biên độ (Min ➔ Max)", f"{th['min']:,.0f} ➔ {th['max']:,.0f}")
                            
                        st.markdown(clean_html(f"""
                        <div style="background: var(--bg-surface-subtle); padding: 14px 18px; border-radius: 10px; font-size: 13px; color: var(--text-secondary); margin-top: 10px; line-height: 1.8;">
                            • <b>Phân tích Trung bình vs Trung vị (Mean vs Median):</b> {th.get('mean_vs_median_insight', '')}<br>
                            • <b>Độ phân tán & Quản trị rủi ro:</b> {th.get('dist_note', '')}<br>
                            • <b>Phân khúc 50% giao dịch phổ biến:</b> {th.get('middle_range_note', '')}<br>
                            • <b>Dẫn chứng Cực trị thực tế:</b> Giá trị nhỏ nhất là <b>{th['min']:,.0f}</b> (tại '{th.get('min_name', 'Bản ghi')}'), giá trị lớn nhất đạt <b>{th['max']:,.0f}</b> (tại '{th.get('max_name', 'Bản ghi')}'). Chênh lệch biên độ cực đại: <b>{th.get('spread', 0):,.0f}</b>.
                        </div>
                        """), unsafe_allow_html=True)
            else:
                st.info("Tập dữ liệu không chứa cột số học định lượng để phân tích chuyên đề sâu.")

            # ------------------------------------------------------------------------------------
            # PHẦN 4: KẾT LUẬN QUẢN TRỊ (EXECUTIVE CONCLUSIONS) - CÓ DẪN CHỨNG SỐ LIỆU ĐANH THÉP
            # ------------------------------------------------------------------------------------
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--status-warning); margin-bottom: 18px; margin-top: 20px;">
                <div style="font-size: 16px; font-weight: 800; color: var(--status-warning); margin-bottom: 8px;">
                    4. KẾT LUẬN QUẢN TRỊ (EXECUTIVE CONCLUSIONS)
                </div>
                <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">
                    Các nhận định quản trị cốt lõi được hệ thống tự động tổng hợp trực tiếp từ dữ liệu thực tế kèm dẫn chứng số liệu cụ thể:
                </div>
            </div>
            """), unsafe_allow_html=True)

            structured_conclusions = s4_d.get("structured_conclusions", [])
            if structured_conclusions:
                for sc in structured_conclusions:
                    evidence_badge = f'<div style="background: rgba(245, 158, 11, 0.08); border-left: 3px solid #F59E0B; padding: 6px 12px; border-radius: 6px; font-size: 12.5px; color: #B45309; margin-top: 8px;">📊 <b>Dẫn chứng số liệu:</b> {sc["evidence"]}</div>' if sc.get("evidence") else ''
                    st.markdown(clean_html(f"""
                    <div style="background: var(--bg-surface); border: 1px solid var(--border-card); border-left: 3px solid #F59E0B; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px;">
                        <div style="font-weight: 700; font-size: 14px; color: var(--text-primary); margin-bottom: 6px;">{sc['title']}</div>
                        <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.7;">{sc['detail']}</div>
                        {evidence_badge}
                    </div>
                    """), unsafe_allow_html=True)
            elif s4_d.get("conclusions"):
                for c_txt in s4_d.get("conclusions", []):
                    st.markdown(clean_html(f'<div style="margin-bottom: 6px; font-size: 13px;">• {c_txt}</div>'), unsafe_allow_html=True)

            # ------------------------------------------------------------------------------------
            # PHẦN 5: ĐỀ XUẤT HÀNH ĐỘNG (MA TRẬN HÀNH ĐỘNG KÈM ƯU TIÊN, DẪN CHỨNG VÀ KPI)
            # ------------------------------------------------------------------------------------
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--status-success); margin-bottom: 18px; margin-top: 20px;">
                <div style="font-size: 16px; font-weight: 800; color: var(--status-success); margin-bottom: 6px;">
                    5. ĐỀ XUẤT HÀNH ĐỘNG & MA TRẬN QUẢN TRỊ THỰC THI
                </div>
                <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">
                    Ma trận các khuyến nghị quản trị cụ thể được lượng hóa kèm mức độ ưu tiên, căn cứ dữ liệu thực tế, chỉ số đo lường KPI, đơn vị chịu trách nhiệm và thời hạn thực thi.
                </div>
            </div>
            """), unsafe_allow_html=True)

            recs_df = pd.DataFrame(s5_d.get("recommendations", []))
            if not recs_df.empty:
                recs_display = recs_df.rename(columns={
                    "priority_badge": "Mức ưu tiên",
                    "action": "Khuyến nghị quản trị chi tiết",
                    "evidence": "Căn cứ & Dẫn chứng dữ liệu",
                    "metric": "Chỉ số đo lường (KPI Target)",
                    "owner": "Đơn vị phụ trách",
                    "timeline": "Thời hạn"
                })
                display_cols = [c for c in ["Mức ưu tiên", "Khuyến nghị quản trị chi tiết", "Căn cứ & Dẫn chứng dữ liệu", "Chỉ số đo lường (KPI Target)", "Đơn vị phụ trách", "Thời hạn"] if c in recs_display.columns]
                render_safe_dataframe(recs_display[display_cols], width="stretch", hide_index=True)

            # ------------------------------------------------------------------------------------
            # PHẦN 6: CHI TIẾT BỘ DỮ LIỆU & THỐNG KÊ KỸ THUẬT (CỰC TRỊ, GROUP-BY & CỘT CÓ DẪN CHỨNG)
            # ------------------------------------------------------------------------------------
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid #64748B; margin-bottom: 18px; margin-top: 20px;">
                <div style="font-size: 16px; font-weight: 800; color: #475569; margin-bottom: 6px;">
                    6. CHI TIẾT BỘ DỮ LIỆU & THỐNG KÊ KỸ THUẬT
                </div>
                <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">
                    Bao gồm thông tin làm sạch dữ liệu, nhận xét thống kê tự động các cực trị có dẫn chứng, bảng tổng hợp theo nhóm và bảng thống kê chi tiết theo từng cột.
                </div>
            </div>
            """), unsafe_allow_html=True)

            # 6.1 Thông tin làm sạch & 6.2 Nhận xét thống kê tự động
            col_tech1, col_tech2 = st.columns(2)
            with col_tech1:
                clean_info_ui = s6_d.get("cleaning_info", {})
                st.markdown(clean_html(f"""
                <div class="bento-surface" style="padding: 16px 18px; margin-bottom: 14px;">
                    <div style="font-weight: 700; font-size: 14px; color: var(--text-primary); margin-bottom: 8px;">6.1. Thông tin làm sạch dữ liệu:</div>
                    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.8;">
                        • <b>Số dòng sau làm sạch:</b> {clean_info_ui.get('cleaned_rows', 0):,} dòng • <b>Số cột:</b> {clean_info_ui.get('cleaned_cols', 0)} cột<br>
                        • <b>Số ô trống đã kiểm soát:</b> {clean_info_ui.get('empty_cells_count', 0):,} ô (Độ hoàn thiện: <b>{clean_info_ui.get('completeness_pct', 100):.1f}%</b>)<br>
                        • <b>Số dòng trùng lặp đã loại bỏ:</b> {clean_info_ui.get('duplicate_rows_removed', 0):,} dòng<br>
                        • <b>Điểm chất lượng dữ liệu:</b> <span class="badge-capsule badge-green">{clean_info_ui.get('quality_score', 100)} / 100 điểm</span>
                    </div>
                </div>
                """), unsafe_allow_html=True)

            with col_tech2:
                stat_obs_ui = s6_d.get("stat_observations", {})
                st.markdown(clean_html(f"""
                <div class="bento-surface" style="padding: 16px 18px; margin-bottom: 14px;">
                    <div style="font-weight: 700; font-size: 14px; color: var(--text-primary); margin-bottom: 8px;">6.2. Nhận xét thống kê tự động:</div>
                    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.8;">
                        • <b>Chỉ số trọng tâm:</b> '{stat_obs_ui.get('primary_metric')}'<br>
                        • <b>Giá trị nhỏ nhất (Min):</b> {stat_obs_ui.get('min_val', 0):,.0f}<br>
                        • <b>Giá trị lớn nhất (Max):</b> {stat_obs_ui.get('max_val', 0):,.0f}<br>
                        • <b>Giá trị trung bình:</b> {stat_obs_ui.get('mean_val', 0):,.1f}<br>
                        • <b>Nhóm dẫn đầu:</b> '{stat_obs_ui.get('top_group')}' ({stat_obs_ui.get('top_group_share', 0):.1f}% tổng giá trị)<br>
                        • <b>Dẫn chứng cực trị:</b> {stat_obs_ui.get('evidence_extreme', '')}
                    </div>
                </div>
                """), unsafe_allow_html=True)

            # 6.3 Bảng Tổng hợp theo nhóm (Group-by) có dẫn chứng & Biểu đồ Pareto
            grp_rows_ui = s6_d.get("groupby_table", [])
            if grp_rows_ui:
                st.markdown(clean_html('<div style="font-weight: 700; font-size: 14px; color: var(--text-primary); margin-top: 6px; margin-bottom: 8px;">6.3. Bảng Tổng hợp theo nhóm & Biểu đồ đóng góp (Group-by theo chiều phân loại chính):</div>'), unsafe_allow_html=True)
                try:
                    fig_grp, ins_grp, df_grp_plot = chart_report_group_breakdown(grp_rows_ui, is_dark=is_dark, lang=lang)
                    if fig_grp is not None:
                        render_chart_card(fig_grp, "Cơ Cấu Giá Trị Đóng Góp Theo Nhóm Phân Loại", ins_grp, df_grp_plot, "report_grp_breakdown", lang=lang)
                except Exception:
                    pass

                grp_df_display = pd.DataFrame(grp_rows_ui).rename(columns={
                    "group_name": "Nhóm phân loại",
                    "value": "Giá trị",
                    "row_count": "Số dòng được tính",
                    "share_pct": "Tỷ trọng (%)",
                    "evidence": "Dẫn chứng thực tế"
                })
                display_grp_cols = [c for c in ["Nhóm phân loại", "Giá trị", "Số dòng được tính", "Tỷ trọng (%)", "Dẫn chứng thực tế"] if c in grp_df_display.columns]
                render_safe_dataframe(grp_df_display[display_grp_cols], width="stretch", hide_index=True)

            # 6.4 Bảng Thống kê theo từng cột
            col_rows_ui = s6_d.get("col_stats_table", [])
            if col_rows_ui:
                st.markdown(clean_html('<div style="font-weight: 700; font-size: 14px; color: var(--text-primary); margin-top: 14px; margin-bottom: 8px;">6.4. Bảng Thống kê chi tiết theo từng cột dữ liệu:</div>'), unsafe_allow_html=True)
                col_df_display = pd.DataFrame(col_rows_ui).rename(columns={
                    "column_name": "Cột",
                    "null_count": "Ô trống",
                    "unique_count": "Giá trị khác nhau",
                    "mean": "Trung bình",
                    "min": "Nhỏ nhất",
                    "max": "Lớn nhất",
                    "evidence": "Ý nghĩa & Dẫn chứng"
                })
                display_stat_cols = [c for c in ["Cột", "Ô trống", "Giá trị khác nhau", "Trung bình", "Nhỏ nhất", "Lớn nhất", "Ý nghĩa & Dẫn chứng"] if c in col_df_display.columns]
                render_safe_dataframe(col_df_display[display_stat_cols], width="stretch", hide_index=True)

            # ------------------------------------------------------------------------------------
            # CÁC NÚT XUẤT FILE HOÀN CHỈNH: MICROSOFT WORD (.DOCX) & EXCEL (.XLSX)
            # ------------------------------------------------------------------------------------
            st.write("")
            st.markdown(clean_html("""
            <div style="font-size: 14px; font-weight: 800; color: var(--text-primary); margin-top: 16px; margin-bottom: 10px;">
                📥 Xuất Báo Cáo Doanh Nghiệp Hoàn Chỉnh:
            </div>
            """), unsafe_allow_html=True)

            c_exp_word, c_exp_excel = st.columns(2)
            
            with c_exp_word:
                # Sinh tệp Microsoft Word (.docx) chuẩn hóa 100% cấu trúc 6 phần có dẫn chứng
                word_file_stream = export_report_to_word(report_pkg)
                word_bytes = word_file_stream.getvalue()
                
                st.download_button(
                    label="📄 Tải Báo Cáo Microsoft Word (.docx)",
                    data=word_bytes,
                    file_name=f"Bao_Cao_Kinh_Doanh_Minh_An_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True,
                    key="btn_export_report_word_docx"
                )

            with c_exp_excel:
                # Nút xuất Excel đa sheet đầy đủ
                analytics_buffer = io.BytesIO()
                with pd.ExcelWriter(analytics_buffer, engine="openpyxl") as writer:
                    curr_df.to_excel(writer, sheet_name="Du_Lieu_Goc", index=False)
                    if 'segments_df' in locals() and not segments_df.empty:
                        segments_df.to_excel(writer, sheet_name="Phan_Hang_Khach_Hang", index=False)
                    pd.DataFrame([fin_kpis]).to_excel(writer, sheet_name="Chi_So_Tai_Chinh", index=False)
                    pd.DataFrame(s2_d["kpi_table"]).to_excel(writer, sheet_name="Dashboard_KPI", index=False)
                    pd.DataFrame(s6_d["col_stats_table"]).to_excel(writer, sheet_name="Thong_Ke_Tung_Cot", index=False)
                analytics_bytes = analytics_buffer.getvalue()
                
                st.download_button(
                    label="📊 Tải Dữ Liệu Excel Đa Sheet (.xlsx)",
                    data=analytics_bytes,
                    file_name=f"Bao_Cao_Thong_Ke_Minh_An_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="btn_export_analytics_excel"
                )



# ====================================================================================================
# TAB 4: DANH MỤC BẢNG GIÁ & KHO KHẢ DỤNG
# ====================================================================================================
with tab_catalog:
    # Tự động đồng bộ và bảo đảm catalog_df luôn đầy đủ dữ liệu khả dụng từ Minh An
    if (
        st.session_state.get("catalog_df") is None 
        or not isinstance(st.session_state.catalog_df, pd.DataFrame) 
        or st.session_state.catalog_df.empty
        or "AvailableStock" not in st.session_state.catalog_df.columns
    ):
        try:
            p_df, s_df, pol_df = DataLoader.load_default_data()
            st.session_state.catalog_df = p_df
            st.session_state.sales_df = s_df
            st.session_state.policy_df = pol_df
        except Exception:
            pass

    icon_pkg = get_icon_tile("package", "cyan")
    st.markdown(clean_html(f"""
    <div class="section-header-row">
        {icon_pkg}
        <div class="section-header-title">{t("catalog_title", lang)}</div>
    </div>
    """), unsafe_allow_html=True)
    
    sub_cat_tab1, sub_cat_tab2, sub_cat_tab3 = st.tabs([t("cat_tab_products", lang), t("cat_tab_sales", lang), t("cat_tab_charts", lang)])
    
    with sub_cat_tab1:
        render_safe_dataframe(
            st.session_state.catalog_df,
            num_formats={"UnitPrice": "%,.0f đ", "AvailableStock": "%,.0f"} if "UnitPrice" in st.session_state.catalog_df.columns else None,
            width="stretch",
            hide_index=True
        )
    with sub_cat_tab2:
        st.dataframe(st.session_state.sales_df, width="stretch", hide_index=True)
        
    with sub_cat_tab3:
        c_cat1, c_cat2 = st.columns(2)
        with c_cat1:
            try:
                fig_c_stock, ins_c_stock, df_c_stock = chart_catalog_top_stock(st.session_state.catalog_df, is_dark=is_dark, lang=lang)
                render_chart_card(fig_c_stock, "Top 10 SKU Tồn kho cao nhất", ins_c_stock, df_c_stock, "catalog_top_stock", lang=lang)
            except Exception as e:
                st.info(f"Biểu đồ top tồn kho: {e}")
                
            try:
                fig_c_cat, ins_c_cat, df_c_cat = chart_catalog_category_breakdown(st.session_state.catalog_df, is_dark=is_dark, lang=lang)
                render_chart_card(fig_c_cat, "Cơ cấu tồn kho theo danh mục", ins_c_cat, df_c_cat, "catalog_category", lang=lang)
            except Exception as e:
                st.info(f"Biểu đồ danh mục: {e}")
                
        with c_cat2:
            try:
                fig_c_scat, ins_c_scat, df_c_scat = chart_catalog_price_vs_stock_scatter(st.session_state.catalog_df, is_dark=is_dark, lang=lang)
                render_chart_card(fig_c_scat, "Ma trận Đơn giá vs Tồn kho (Vốn lưu động)", ins_c_scat, df_c_scat, "catalog_price_stock", lang=lang)
            except Exception as e:
                st.info(f"Biểu đồ tương quan giá - tồn: {e}")
                
            try:
                fig_c_low, ins_c_low, df_c_low = chart_catalog_low_stock_alerts(st.session_state.catalog_df, is_dark=is_dark, lang=lang)
                render_chart_card(fig_c_low, "Cảnh báo thiết bị sắp hết hàng", ins_c_low, df_c_low, "catalog_low_stock", lang=lang)
            except Exception as e:
                st.info(f"Biểu đồ cảnh báo hết hàng: {e}")

# ====================================================================================================
# TAB 5: NGUỒN DỮ LIỆU & ĐỒNG BỘ AI
# ====================================================================================================
with tab_settings:
    icon_set = get_icon_tile("settings", "indigo")
    st.markdown(clean_html(f"""
    <div class="section-header-row">
        {icon_set}
        <div class="section-header-title">{t("settings_title", lang)}</div>
    </div>
    """), unsafe_allow_html=True)
    
    col_set1, col_set2 = st.columns([1, 1])
    
    with col_set1:
        st.markdown(clean_html(f"""
        <div class="bento-surface">
            <div style="font-weight: 700; font-size: 15px; margin-bottom: 6px;">{t("upload_file_title", lang)}</div>
            <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">{t("upload_file_desc", lang)}</div>
        </div>
        """), unsafe_allow_html=True)
        up_file = st.file_uploader("Tải lên file Bảng giá & Kho:", type=["xlsx", "xls", "csv", "tsv", "json", "xml"], label_visibility="collapsed")
        if up_file:
            try:
                sheets = DataLoader.load_from_uploaded_files(up_file)
                if sheets:
                    st.success(f"Đã cập nhật dữ liệu từ file: {up_file.name}")
                    first_sheet = list(sheets.keys())[0]
                    new_agent = MinhAnSalesAgent(sheets[first_sheet], st.session_state.sales_df, st.session_state.policy_df)
                    st.session_state.catalog_df = new_agent.products_df
                    st.session_state.agent = new_agent
            except Exception as e:
                st.error(f"Lỗi: {e}")
                
    with col_set2:
        st.markdown(clean_html(f"""
        <div class="bento-surface">
            <div style="font-weight: 700; font-size: 15px; margin-bottom: 6px;">{t("gsheet_title", lang)}</div>
            <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">{t("gsheet_desc", lang)}</div>
        </div>
        """), unsafe_allow_html=True)
        gs_url = st.text_input("Dán đường link Google Sheets:", placeholder="https://docs.google.com/spreadsheets/d/.../edit#gid=0")
        if st.button(t("btn_sync_gsheet", lang)):
            if gs_url:
                try:
                    df_sheet = DataLoader.load_from_google_sheet(gs_url)
                    st.session_state.catalog_df = df_sheet
                    st.session_state.agent = MinhAnSalesAgent(st.session_state.catalog_df, st.session_state.sales_df, st.session_state.policy_df)
                    st.success(f"Đã kết nối thành công! Đã nạp {len(df_sheet)} bản ghi.")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Vui lòng cung cấp link Google Sheets.")

    # Báo cáo Kiểm toán Chất lượng Dữ liệu Danh mục Kho
    if st.session_state.catalog_df is not None and not st.session_state.catalog_df.empty:
        cat_audit = DataQualityCleaner.audit_dataframe(st.session_state.catalog_df)
        with st.expander("🛡️ Xem Báo cáo Kiểm toán Chất lượng Dữ liệu & Ô trống", expanded=False):
            try:
                fig_aud, ins_aud, df_aud = chart_data_quality_missing_bars(cat_audit, is_dark=is_dark, lang=lang)
                render_chart_card(fig_aud, "Kiểm toán Dữ liệu khuyết thiếu", ins_aud, df_aud, "settings_data_audit", lang=lang)
            except Exception as e:
                st.info(f"Biểu đồ kiểm toán: {e}")

    # 3. Cấu hình Gemini AI Engine
    st.markdown("---")
    icon_spark = get_icon_tile("sparkles", "pink")
    st.markdown(clean_html(f"""
    <div class="section-header-row">
        {icon_spark}
        <div class="section-header-title">{t("gemini_title", lang)}</div>
    </div>
    """), unsafe_allow_html=True)
    
    current_status = get_safe_api_status()
    st.markdown(clean_html(f"""
    <div class="bento-surface">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
            <div>
                <span style="font-weight: 700; font-size: 15px; color: var(--text-primary);">{t("gemini_status_label", lang)}</span>
                <span class="badge-capsule {'badge-green' if current_status['active'] else 'badge-amber'}" style="margin-left: 8px;">
                    {t("gemini_active", lang) if current_status['active'] else t("gemini_inactive", lang)}
                </span>
            </div>
            <span style="font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
                Model: <b>{current_status['model']}</b> • Khóa: <b>{current_status['masked_key']}</b>
            </span>
        </div>
        <div style="font-size: 14px; color: var(--text-secondary); line-height: 1.6;">
            {t("gemini_desc", lang)}
        </div>
    </div>
    """), unsafe_allow_html=True)

    col_key_in, col_key_btn = st.columns([7, 3])
    with col_key_in:
        new_key = st.text_input("Cập nhật Khóa Gemini API mới (nếu cần thay đổi):", type="password", placeholder="Nhập khóa API mới vào đây...")
    with col_key_btn:
        st.write("")
        st.write("")
        if st.button(t("btn_save_key", lang), use_container_width=True):
            if new_key.strip():
                os.environ["GEMINI_API_KEY"] = new_key.strip()
                try:
                    with open(".env", "w", encoding="utf-8") as f:
                        f.write(f"GEMINI_API_KEY={new_key.strip()}\n")
                except Exception:
                    pass
                st.session_state.agent = MinhAnSalesAgent(
                    st.session_state.catalog_df, 
                    st.session_state.sales_df, 
                    st.session_state.policy_df,
                    api_key=new_key.strip()
                )
                st.toast("Đã cập nhật và kích hoạt Khóa Gemini API mới thành công!", icon="✨")
                st.rerun()

# ====================================================================================================
# 7. FOOTER
# ====================================================================================================
st.markdown(clean_html(f"""
<div class="footer-bar-modern">
    {t("footer_text", lang)}
</div>
"""), unsafe_allow_html=True)

# ==============================================================================
# 8. VERCEL SERVERLESS RUNTIME ENTRYPOINT COMPATIBILITY
# ==============================================================================
# Prevents [PYTHON_ENTRYPOINT_NOT_FOUND] if Vercel inspects app.py directly.
def handler(request=None, *args, **kwargs):
    """Fallback handler for Vercel Python runtime discovery."""
    return {"status": 200, "message": "Minh An AI Sales Operations Center is active."}

app = handler
application = handler
