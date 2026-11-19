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
from agent_core import DataLoader, MinhAnSalesAgent
import styles
importlib.reload(styles)
from styles import get_app_styles, clean_html

import translations
importlib.reload(translations)
from translations import t
from icons import get_svg_icon, get_icon_tile
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
    chart_batch_order_value_distribution,
    chart_catalog_top_stock,
    chart_catalog_price_vs_stock_scatter,
    chart_catalog_category_breakdown,
    chart_catalog_low_stock_alerts,
    chart_data_quality_missing_bars,
    chart_dynamic_builder,
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


st.markdown('<div style="margin-top: 14px; margin-bottom: 8px;"></div>', unsafe_allow_html=True)
ov_col1, ov_col2, ov_col3, ov_col4 = st.columns(4)

with ov_col1:
    st.metric(t("overview_kpi_pipeline", lang), f"{pipeline_sum:,.0f} ₫", "+18.4%")
    st.plotly_chart(chart_mini_sparkline([45, 62, 78, 95, 120, 145, 185], color="#6366F1", is_dark=is_dark), use_container_width=True, config={"displayModeBar": False})

with ov_col2:
    st.metric(t("overview_kpi_processed", lang), f"{total_requests_count} Yêu cầu", "+3")
    st.plotly_chart(chart_mini_sparkline([8, 12, 15, 18, 22, 25, 29], color="#22D3EE", is_dark=is_dark), use_container_width=True, config={"displayModeBar": False})

with ov_col3:
    st.metric(t("overview_kpi_autorate", lang), f"{auto_rate:.1f}%", "+5.2%")
    st.plotly_chart(chart_mini_sparkline([55, 58, 62, 60, 65, 68, 71], color="#10B981", is_dark=is_dark), use_container_width=True, config={"displayModeBar": False})

with ov_col4:
    st.metric(t("overview_kpi_sla", lang), "1.6 giây", "-0.4s")
    st.plotly_chart(chart_mini_sparkline([3.2, 2.8, 2.5, 2.2, 2.0, 1.9, 1.6], color="#F59E0B", is_dark=is_dark), use_container_width=True, config={"displayModeBar": False})

# ====================================================================================================
# 6. TABS ĐIỀU HƯỚNG CHÍNH (5 TABS STICKY Ở ĐẦU TRANG)
# ====================================================================================================
tab_single, tab_batch, tab_analytics, tab_catalog, tab_settings = st.tabs([
    t("tab_single", lang),
    t("tab_batch", lang),
    t("tab_analytics", lang),
    t("tab_catalog", lang),
    t("tab_settings", lang)
])

# ====================================================================================================
# TAB 1: XỬ LÝ YÊU CẦU ĐƠN LẺ (5-STEP PROCESS THEO SƠ ĐỒ QUY TRÌNH)
# ====================================================================================================
with tab_single:
    with open("data/sample_requests.json", encoding="utf-8") as f:
        sample_requests = json.load(f)
        
    sample_options = [t("sample_select_default", lang)] + [
        f"{s['id']}: {s['title']}" for s in sample_requests
    ]
    
    # STEPPER TIẾN TRÌNH TRỰC QUAN THEO ĐÚNG SƠ ĐỒ B2B MINH AN (B1 -> B2 -> B3 -> B4 -> B5 -> [Duyệt] -> B6)
    cur_res = st.session_state.get("current_result")
    if not cur_res:
        c1, c2, c3, c4, c5, c_appr, c6 = "active", "idle", "idle", "idle", "idle", "idle", "idle"
        n1, n2, n3, n4, n5, n_appr, n6 = "1", "2", "3", "4", "5", "—", "6"
    elif not (cur_res.get("parsed_request") or {}).get("is_sufficient", False):
        c1, c2, c3, c4, c5, c_appr, c6 = "completed", "warning", "idle", "idle", "idle", "idle", "idle"
        n1, n2, n3, n4, n5, n_appr, n6 = "✓", "⚠", "3", "4", "5", "—", "6"
    else:
        needs_appr = (cur_res.get("evaluation") or {}).get("needs_manager_approval", False)

        c1, c2, c3, c4, c5 = "completed", "completed", "completed", "completed", "completed"
        n1, n2, n3, n4, n5 = "✓", "✓", "✓", "✓", "✓"
        if needs_appr:
            c_appr = "warning"
            n_appr = "⚠"
        else:
            c_appr = "dimmed"
            n_appr = "✓"
        c6 = "completed"
        n6 = "✓"
            
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
    
    col_input_left, col_input_right = st.columns([7, 3])
    
    with col_input_left:
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
            label_visibility="collapsed"
        )
        
        default_text = ""
        if selected_sample != t("sample_select_default", lang):
            sample_id = selected_sample.split(":")[0]
            for s in sample_requests:
                if s["id"] == sample_id:
                    default_text = s["raw_text"]
                    break
                    
        # Tự động đồng bộ kết quả khi đổi mẫu
        if "last_selected_sample" not in st.session_state:
            st.session_state.last_selected_sample = selected_sample
        elif selected_sample != st.session_state.last_selected_sample:
            st.session_state.last_selected_sample = selected_sample
            if default_text:
                st.session_state.current_result = st.session_state.agent.process_request(default_text)
                    
        req_input = st.text_area(
            t("req_input_label", lang),
            value=default_text,
            height=210,
            placeholder=t("req_input_placeholder", lang)
        )
        
        run_process = st.button(t("btn_process", lang), use_container_width=True)

    with col_input_right:
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

    # Đảm bảo kết quả luôn sẵn sàng hiển thị
    if "current_result" not in st.session_state or st.session_state.current_result is None:
        st.session_state.current_result = st.session_state.agent.process_request(default_text if default_text else sample_requests[0]["raw_text"])

    if run_process and req_input.strip():
        with st.spinner(t("processing_spinner", lang)):
            st.session_state.current_result = st.session_state.agent.process_request(req_input)
            
    result = st.session_state.get("current_result")
    if result:
        st.write("")
        is_sufficient = result["parsed_request"]["is_sufficient"]
        
        # ----------------------------------------------------------------------------------------
        # KỊCH BẢN 1: THIẾU THÔNG TIN (YÊU CẦU KH LÀM RÕ)
        # ----------------------------------------------------------------------------------------
        if not is_sufficient:
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="border-left: 4px solid var(--status-danger);">
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
                    ⚡ Điểm rẽ 1: KHÔNG ĐỦ THÔNG TIN BẮT BUỘC ➔ Rẽ nhánh "Yêu cầu KH làm rõ / bổ sung"
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            c_clar1, c_clar2 = st.columns([1, 1])
            with c_clar1:
                st.markdown(clean_html(f'<div class="section-header-title" style="margin-bottom: 12px;">{t("missing_items_title", lang)}</div>'), unsafe_allow_html=True)
                for r in result["parsed_request"]["missing_reasons"]:
                    st.markdown(clean_html(f"""
                    <div style="background: var(--status-danger-bg); border: 1px solid var(--status-danger-border); padding: 12px 16px; border-radius: 12px; margin-bottom: 8px; font-size: 14px; color: var(--status-danger); font-weight: 600;">
                        • {r}
                    </div>
                    """), unsafe_allow_html=True)
            with c_clar2:
                st.markdown(clean_html(f'<div class="section-header-title" style="margin-bottom: 12px;">{t("clarification_email_title", lang)}</div>'), unsafe_allow_html=True)
                st.text_area("Nội dung thư làm rõ:", value=result["clarification_draft"], height=160, label_visibility="collapsed")
                st.download_button(
                    t("btn_download_clarification", lang),
                    data=result["clarification_draft"],
                    file_name=f"Yeu_cau_bo_sung_{result['opportunity_id']}.txt",
                    mime="text/plain",
                    use_container_width=True
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
                    key="supp_info_input",
                    label_visibility="collapsed"
                )
                if st.button(t("btn_resubmit_clarification", lang), key="btn_submit_supp", use_container_width=True):
                    if supp_text.strip():
                        combined = req_input + "\n\n[Thông tin bổ sung tiếp nhận lại tại B1]:\n" + supp_text.strip()
                        st.session_state.current_result = st.session_state.agent.process_request(combined)
                        st.toast("Đã tiếp nhận thông tin bổ sung vào B1 và hoàn tất tái thẩm định B2!", icon="✅")
                        st.rerun()
                
        # ----------------------------------------------------------------------------------------
        # KỊCH BẢN 2: ĐẦY ĐỦ THÔNG TIN (XUẤT HỒ SƠ & BÁO GIÁ)
        # ----------------------------------------------------------------------------------------
        else:
            eval_data = result["evaluation"]
            rep = result["sales_rep"]
            parsed = result["parsed_request"]
            
            # Trạng thái phê duyệt Telegram
            approval_key = f"approval_status_{result['opportunity_id']}"
            current_appr_badge = st.session_state.get(approval_key, eval_data['decision_badge'])
            
            st.markdown(clean_html(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; margin-bottom: 22px; flex-wrap: wrap; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 24px; font-weight: 800; color: var(--text-primary);">{t("opp_title", lang)} {result['opportunity_id']}</span>
                    <span class="badge-capsule badge-green">{t("valid_info_badge", lang)}</span>
                </div>
                <div>
                    <span class="badge-capsule {'badge-green' if ('DUYỆT' in current_appr_badge and 'CẦN' not in current_appr_badge) else 'badge-amber'}">
                        {current_appr_badge}
                    </span>
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            # 4 Thẻ KPI chính
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
                    <div class="stat-kpi-label">{t("kpi_discount", lang)}</div>
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
                    <div class="stat-kpi-value" style="font-size: 20px; line-height: 33px;">{rep['FullName']}</div>
                    <div class="stat-kpi-label">{t("kpi_sales_rep", lang)} ({rep['StaffID']})</div>
                </div>
                """), unsafe_allow_html=True)
                
            st.write("")
            
            # Hai cột chi tiết
            col_detail_left, col_detail_right = st.columns([6, 4])
            
            with col_detail_left:
                icon_pkg = get_icon_tile("package", "cyan")
                st.markdown(clean_html(f"""
                <div class="section-header-row">
                    {icon_pkg}
                    <div class="section-header-title">{t("items_table_title", lang)}</div>
                </div>
                """), unsafe_allow_html=True)
                
                for it in eval_data["items_detail"]:
                    status_str = str(it.get("StockStatus", ""))
                    is_service = ("Dịch vụ" in status_str or it.get("Category") == "Dịch vụ" or it.get("AvailableStock", 0) >= 999 or "SVC-" in str(it.get("SKU", "")).upper())
                    is_in_stock = ("Đủ hàng" in status_str or (not is_service and it.get("AvailableStock", 0) >= it.get("Quantity", 1)))
                    
                    if is_service:
                        display_badge_text = "Dịch vụ · không giới hạn" if lang == "vi" else "Service · no stock limit"
                        stock_badge = f'<span class="badge-capsule badge-cyan">{display_badge_text}</span>'
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
                                <span>• Đơn giá: <b>{it['UnitPrice']:,.0f} đ</b></span>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 800; font-size: 16px; color: var(--text-primary);">{it['FinalTotal']:,.0f} đ</div>
                            <div style="margin-top: 6px;">{stock_badge}</div>
                        </div>
                    </div>
                    """), unsafe_allow_html=True)
                    
                # Download Báo giá Excel (Nút chính nổi bật)
                items_df = pd.DataFrame(eval_data["items_detail"])
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    items_df.to_excel(writer, sheet_name="Bao_Gia", index=False)
                excel_bytes = excel_buffer.getvalue()
                
                st.write("")
                st.download_button(
                    label=t("btn_download_quotation", lang),
                    data=excel_bytes,
                    file_name=f"Bao_gia_{result['opportunity_id']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary",
                    key=f"btn_dl_quote_{result['opportunity_id']}"
                )

            with col_detail_right:
                icon_user = get_icon_tile("user_check", "indigo")
                st.markdown(clean_html(f"""
                <div class="section-header-row">
                    {icon_user}
                    <div class="section-header-title">{t("client_info_title", lang)}</div>
                </div>
                """), unsafe_allow_html=True)
                
                st.markdown(clean_html(f"""
                <div class="bento-surface">
                    <div style="font-size: 18px; font-weight: 800; color: var(--text-primary); margin-bottom: 8px;">{parsed['company_name']}</div>
                    <div style="font-size: 14px; color: var(--text-secondary); line-height: 1.8;">
                        • <b>Người liên hệ:</b> {parsed['contact_person']}<br>
                        • <b>Liên lạc:</b> {parsed['email']} • {parsed['phone']}<br>
                        • <b>Tình trạng ngân sách:</b> <span style="font-weight: 700; color: var(--text-primary);">{eval_data['budget_status']}</span><br>
                        • <b>NVKD phụ trách:</b> {rep['FullName']} ({rep['Specialty']})<br>
                        • <b>Thẩm quyền duyệt:</b> <b>{eval_data['approval_level']}</b>
                    </div>
                </div>
                """), unsafe_allow_html=True)
                
                # Cảnh báo rủi ro (nếu có)
                if eval_data["stock_warnings"] or eval_data["leadtime_warnings"]:
                    st.markdown(clean_html(f'<div class="section-header-title" style="margin-bottom: 12px;">{t("risk_warnings_title", lang)}</div>'), unsafe_allow_html=True)
                    for w in eval_data["stock_warnings"]:
                        st.markdown(clean_html(f'<div style="background: var(--status-warning-bg); border: 1px solid var(--status-warning-border); color: var(--status-warning); padding: 12px 14px; border-radius: 12px; font-size: 13px; margin-bottom: 6px;">📦 <b>Kho:</b> {w}</div>'), unsafe_allow_html=True)
                    for lw in eval_data["leadtime_warnings"]:
                        st.markdown(clean_html(f'<div style="background: var(--status-danger-bg); border: 1px solid var(--status-danger-border); color: var(--status-danger); padding: 12px 14px; border-radius: 12px; font-size: 13px; margin-bottom: 6px;">⏱️ <b>Tiến độ:</b> {lw}</div>'), unsafe_allow_html=True)

            # ====================================================================================
            # PHÂN TÍCH KỸ THUẬT & TÀI CHÍNH YÊU CẦU (PLOTLY CHARTS)
            # ====================================================================================
            st.markdown(clean_html(f"""
            <div class="section-header-row" style="margin-top: 24px; margin-bottom: 12px;">
                {get_icon_tile("sparkles", "indigo")}
                <div class="section-header-title">{t("charts_single_title", lang)}</div>
            </div>
            """), unsafe_allow_html=True)
            
            # 1. Thẻ Thẩm quyền chiết khấu & Giá trị (Dual Gauge cùng baseline, 300px, chips & banner)
            try:
                render_governance_card(eval_data, is_dark=is_dark, lang=lang)
            except Exception as e:
                st.info(f"Thẩm quyền chiết khấu & giá trị: {e}")
                
            # 2. Lưới 2 cột đều nhau cho 4 biểu đồ kỹ thuật & tài chính
            items_list = eval_data.get("items_detail") or eval_data.get("matched_items") or []
            
            col_a, col_b = st.columns(2, gap="large")
            with col_a:
                # (a) Cột ngang giá trị từng hạng mục
                try:
                    fig_it, ins_it, df_it = chart_opportunity_item_values(items_list, is_dark=is_dark, lang=lang)
                    render_chart_card(fig_it, t("chart_opp_items", lang), ins_it, df_it, "opp_items", lang=lang)
                except Exception as e:
                    st.info(f"Biểu đồ giá trị: {e}")
                    
                # (c) So sánh số lượng yêu cầu với tồn kho
                try:
                    fig_inv, ins_inv, df_inv = chart_opportunity_inventory_comparison(items_list, is_dark=is_dark, lang=lang)
                    render_chart_card(fig_inv, t("chart_opp_inventory", lang), ins_inv, df_inv, "opp_inventory", lang=lang)
                except Exception as e:
                    st.info(f"Biểu đồ tồn kho: {e}")
                    
            with col_b:
                # (b) Donut tỷ trọng theo nhóm sản phẩm
                try:
                    fig_cat, ins_cat, df_cat = chart_opportunity_category_donut(items_list, is_dark=is_dark, lang=lang)
                    render_chart_card(fig_cat, t("chart_opp_category", lang), ins_cat, df_cat, "opp_category", lang=lang)
                except Exception as e:
                    st.info(f"Biểu đồ cơ cấu nhóm: {e}")
                    
                # (d) Timeline thời gian giao hàng dự kiến
                try:
                    fig_lt, ins_lt, df_lt = chart_leadtime_timeline(items_list, is_dark=is_dark, lang=lang)
                    render_chart_card(fig_lt, t("chart_opp_leadtime", lang), ins_lt, df_lt, "opp_leadtime", lang=lang)
                except Exception as e:
                    st.info(f"Biểu đồ tiến độ: {e}")

            # Kênh duyệt tức thì Telegram Bot
            if eval_data["needs_manager_approval"]:
                bot_icon = get_icon_tile("bot", "amber")
                st.markdown(clean_html(f"""
                <div class="section-header-row" style="margin-top: 14px;">
                    {bot_icon}
                    <div class="section-header-title">{t("tg_card_title", lang)}</div>
                </div>
                """), unsafe_allow_html=True)
                
                st.markdown(clean_html(f"""
                <div class="telegram-approval-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span class="badge-capsule badge-amber">{t("tg_bot_badge", lang)}</span>
                        <span style="font-size: 13px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">Recipient: Trưởng phòng Kinh doanh</span>
                    </div>
                    <div style="font-size: 14px; color: var(--text-primary); line-height: 1.6; margin-bottom: 16px;">
                        {t("tg_desc", lang)}<br>
                        • <b>Hồ sơ:</b> {result['opportunity_id']} • <b>Khách hàng:</b> {parsed['company_name']}<br>
                        • <b>Giá trị:</b> <span style="font-weight: 800; color: var(--text-primary);">{eval_data['total_final_amount']:,.0f} đ</span> (Chiết khấu: <b>{eval_data['discount_pct']:.1f}%</b>)
                    </div>
                </div>
                """), unsafe_allow_html=True)
                
                col_tg1, col_tg2, col_tg3 = st.columns([1, 1, 1])
                with col_tg1:
                    if st.button(t("tg_btn_approve", lang), key="btn_tg_approve", use_container_width=True):
                        st.session_state[approval_key] = t("tg_status_approved", lang)
                        st.toast(t("tg_toast_approved", lang), icon="✅")
                        st.rerun()
                with col_tg2:
                    if st.button(t("tg_btn_reject", lang), key="btn_tg_reject", use_container_width=True):
                        st.session_state[approval_key] = t("tg_status_rejected", lang)
                        st.toast("Đã gửi phản hồi Từ chối tới NVKD qua Telegram!", icon="❌")
                        st.rerun()
                with col_tg3:
                    if st.button(t("tg_btn_adjust", lang), key="btn_tg_adjust", use_container_width=True):
                        st.session_state[approval_key] = t("tg_status_adjusted", lang)
                        st.toast("Đã gửi yêu cầu NVKD đàm phán giảm chiết khấu!", icon="💬")
                        st.rerun()

            # Phiếu trình duyệt nội bộ
            if eval_data["needs_manager_approval"] and result["approval_note"]:
                st.markdown(clean_html(f'<div class="section-header-title" style="margin-top: 16px; margin-bottom: 10px;">{t("approval_memo_title", lang)}</div>'), unsafe_allow_html=True)
                with st.expander(t("approval_memo_expander", lang), expanded=True):
                    st.code(result["approval_note"], language="text")

            # Bản nháp email đề xuất gửi khách hàng
            icon_send = get_icon_tile("send", "indigo")
            st.markdown(clean_html(f"""
            <div class="section-header-row" style="margin-top: 20px;">
                {icon_send}
                <div class="section-header-title">{t("proposal_email_title", lang)}</div>
            </div>
            """), unsafe_allow_html=True)
            st.text_area("Nội dung bản nháp đề xuất:", value=result["client_proposal"], height=240, label_visibility="collapsed")
            
            c_save_prop, c_dl_prop = st.columns([1, 1])
            with c_save_prop:
                if st.button(t("btn_save_pipeline", lang), use_container_width=True):
                    st.session_state.pipeline_history.append({
                        "OpportunityID": result["opportunity_id"],
                        "CreatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Customer": parsed["company_name"],
                        "SalesRep": rep["FullName"],
                        "TotalAmount": eval_data["total_final_amount"],
                        "DiscountPct": eval_data["discount_pct"],
                        "Approval": eval_data["approval_level"]
                    })
                    st.toast(t("toast_saved_pipeline", lang), icon="✨")
            with c_dl_prop:
                st.download_button(
                    t("btn_download_proposal", lang),
                    data=result["client_proposal"],
                    file_name=f"De_xuat_kinh_doanh_{result['opportunity_id']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            # ====================================================================================
            # B6. KẾT THÚC: CẬP NHẬT & THEO DÕI HỒ SƠ
            # ====================================================================================
            opp_rec = result.get("opportunity_record") or {}
            wf_status_label = "Chờ Trưởng phòng phê duyệt" if eval_data['needs_manager_approval'] else "Đã xuất báo giá (Hoàn tất)"
            wf_badge_cls = "badge-amber" if eval_data['needs_manager_approval'] else "badge-green"
            st.markdown(clean_html(f"""
            <div class="bento-surface" style="margin-top: 24px; border-left: 4px solid {'var(--status-warning)' if eval_data['needs_manager_approval'] else 'var(--status-success)'};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-weight: 800; font-size: 16px; color: var(--text-primary);">
                        B6. Kết thúc: Cập nhật & Theo dõi Hồ sơ {result['opportunity_id']}
                    </div>
                    <span class="badge-capsule {wf_badge_cls}">{wf_status_label}</span>
                </div>
                <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6;">
                    • <b>Khách hàng:</b> {parsed['company_name']} ({parsed['contact_person']}) &nbsp;|&nbsp; 
                    • <b>NVKD phụ trách:</b> {rep['FullName']} ({rep['Role']} - {rep['Specialty']})<br>
                    • <b>Thời điểm tạo hồ sơ:</b> {opp_rec.get('created_at', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))} &nbsp;|&nbsp; 
                    • <b>Hành động tiếp theo:</b> {'Trình Trưởng phòng Kinh doanh xem xét và ký duyệt theo thẩm quyền.' if eval_data['needs_manager_approval'] else 'Gửi báo giá chính thức đến khách hàng, theo dõi phản hồi trong 48h và xúc tiến hợp đồng.'}
                </div>
            </div>
            """), unsafe_allow_html=True)

            # ====================================================================================
            # NHẬT KÝ XỬ LÝ MINH BẠCH (AUDIT TRAIL LOG)
            # ====================================================================================
            if "audit_logs" in result and result["audit_logs"]:
                st.markdown(clean_html(f"""
                <div class="section-header-row" style="margin-top: 24px;">
                    {get_icon_tile("clipboard_check", "emerald")}
                    <div class="section-header-title">{t("audit_trail_title", lang)}</div>
                </div>
                """), unsafe_allow_html=True)
                
                with st.expander("Xem toàn bộ các bước xử lý minh bạch & quy tắc đã áp dụng", expanded=False):
                    for log_entry in result["audit_logs"]:
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

            # Trợ lý đàm phán AI Sales Copilot
            icon_spark = get_icon_tile("sparkles", "pink")
            st.markdown(clean_html(f"""
            <div class="copilot-container">
                <div class="section-header-row" style="margin-bottom: 6px;">
                    {icon_spark}
                    <div>
                        <div class="section-header-title">{t("copilot_card_title", lang)}</div>
                        <div style="font-size: 13px; color: var(--text-muted);">{t("copilot_subtitle", lang)}</div>
                    </div>
                </div>
            """), unsafe_allow_html=True)
            
            col_p1, col_p2, col_p3 = st.columns(3)
            quick_selected = None
            with col_p1:
                if st.button(f"💡 {t('copilot_pill_1', lang)}", key="btn_pill_1", use_container_width=True):
                    quick_selected = t('copilot_pill_1', lang)
            with col_p2:
                if st.button(f"⏱️ {t('copilot_pill_2', lang)}", key="btn_pill_2", use_container_width=True):
                    quick_selected = t('copilot_pill_2', lang)
            with col_p3:
                if st.button(f"🛡️ {t('copilot_pill_3', lang)}", key="btn_pill_3", use_container_width=True):
                    quick_selected = t('copilot_pill_3', lang)
                    
            copilot_input = st.text_input(
                "Câu hỏi đàm phán:",
                value=quick_selected if quick_selected else "",
                placeholder=t("copilot_prompt_placeholder", lang),
                label_visibility="collapsed"
            )
            
            if st.button(t("copilot_btn_ask", lang), key="btn_run_copilot") or quick_selected:
                q_text = quick_selected if quick_selected else copilot_input
                if q_text:
                    with st.spinner("AI Sales Copilot đang phân tích biên lợi nhuận và lập phương án đàm phán..."):
                        copilot_ans = st.session_state.agent.negotiate_copilot(result, q_text)
                        st.session_state.copilot_history[result["opportunity_id"]] = copilot_ans
                        
            active_copilot_ans = st.session_state.copilot_history.get(result["opportunity_id"])
            if active_copilot_ans:
                st.markdown(clean_html(f"""
                <div class="copilot-msg-box">
                    {active_copilot_ans}
                </div>
                """), unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)

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
    if batch_source == t("batch_radio_sample", lang):
        with open("data/sample_requests.json", encoding="utf-8") as f:
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
            # 4. THỐNG KÊ TÀI CHÍNH & KPI DOANH SỐ
            fin_kpis = StatisticalAnalyticsEngine.compute_financial_kpis(curr_df)
            
            st.markdown(clean_html(f"""
            <div class="section-header-row">
                {get_icon_tile("dollar_sign", "emerald")}
                <div class="section-header-title">{t("analytics_sub_financial", lang)}</div>
            </div>
            """), unsafe_allow_html=True)
            
            fk1, fk2, fk3, fk4 = st.columns(4)
            with fk1:
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value">{fin_kpis["total_revenue"]:,.0f} đ</div><div class="stat-kpi-label">Tổng Doanh Thu Ghi Nhận</div></div>'), unsafe_allow_html=True)
            with fk2:
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value">{fin_kpis["gross_profit"]:,.0f} đ</div><div class="stat-kpi-label">Lợi Nhuận Gộp Ước Tính</div></div>'), unsafe_allow_html=True)
            with fk3:
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value">{fin_kpis["gross_margin_pct"]:.1f}%</div><div class="stat-kpi-label">Biên Lợi Nhuận Gộp (Margin)</div></div>'), unsafe_allow_html=True)
            with fk4:
                st.markdown(clean_html(f'<div class="stat-kpi-card"><div class="stat-kpi-value">{fin_kpis["aov"]:,.0f} đ</div><div class="stat-kpi-label">Giá Trị Đơn Bình Quân (AOV)</div></div>'), unsafe_allow_html=True)

            st.write("")
            
            # 5. TIỂU MỤC THỐNG KÊ CHUYÊN SÂU
            stat_sub1, stat_sub2, stat_sub3 = st.tabs([
                t("analytics_sub_rfm", lang),
                t("analytics_sub_segment", lang),
                t("analytics_sub_charts", lang)
            ])
            
            # SUB-TAB 1: PHÂN HẠNG KHÁCH HÀNG (RFM PRIORITIZATION)
            with stat_sub1:
                segments_df = StatisticalAnalyticsEngine.segment_customers_rfm(curr_df)
                if not segments_df.empty:
                    st.markdown(f"<div class='notranslate' translate='no' style='font-size: 13px; color: var(--text-muted); margin-bottom: 10px;'>Phân hạng dựa trên doanh số và tần suất đơn. Bạn có thể chỉnh sửa trực tiếp cột <b>AssignedTier</b> bên dưới:</div>", unsafe_allow_html=True)
                    try:
                        edited_segments = st.data_editor(
                            segments_df,
                            key="rfm_segments_editor",
                            column_config={
                                "TotalSpend": st.column_config.NumberColumn("Tổng Doanh Thu (VNĐ)", format="%d đ"),
                                "OrderCount": st.column_config.NumberColumn("Số Lượng Đơn"),
                                "AOV": st.column_config.NumberColumn("AOV (VNĐ)", format="%d đ"),
                                "AssignedTier": st.column_config.SelectboxColumn("Phân Hạng Khách Hàng", options=["VIP", "PRIORITY", "STANDARD"]),
                                "ConfidencePct": st.column_config.ProgressColumn("Độ Tin Cậy (%)", min_value=0, max_value=100, format="%d%%"),
                                "Reason": st.column_config.TextColumn("Lý Do Phân Loại", width="large")
                            },
                            width="stretch",
                            hide_index=True
                        )
                    except Exception:
                        st.dataframe(segments_df, width="stretch", hide_index=True)
                else:
                    st.info("Chưa tìm thấy cột khách hàng để phân hạng RFM.")
                    
            # SUB-TAB 2: PHÂN NHÓM LINH HOẠT (DYNAMIC SEGMENTATION)
            with stat_sub2:
                if len(curr_df.columns) > 200:
                    st.warning("⚠️ Đã ẩn danh sách checkbox/phân nhóm do tệp dữ liệu vượt quá 200 cột để tránh làm vỡ giao diện.")
                else:
                    groupable_cols = [c for c in curr_df.columns if curr_df[c].nunique() <= 30]
                    if groupable_cols:
                        chosen_crit = st.selectbox("Chọn tiêu chí phân nhóm linh hoạt:", groupable_cols, index=0)
                        seg_result = StatisticalAnalyticsEngine.flexible_segmentation(curr_df, criteria_col=chosen_crit)
                        render_safe_dataframe(
                            seg_result,
                            num_formats={"TotalValue": "%,.0f đ", "SharePct": "%.1f%%"},
                            width="stretch",
                            hide_index=True
                        )
                    else:
                        st.info("Dữ liệu không có cột phân nhóm phù hợp.")

            # SUB-TAB 3: TRỰC QUAN HÓA PLOTLY TƯƠNG TÁC
            with stat_sub3:
                plotly_charts = StatisticalAnalyticsEngine.build_financial_charts(curr_df, is_dark=is_dark)
                if plotly_charts:
                    pc1, pc2 = st.columns(2)
                    with pc1:
                        if "donut_revenue" in plotly_charts:
                            render_chart_card(
                                plotly_charts["donut_revenue"],
                                "Tỷ Trọng Doanh Thu Danh Mục",
                                "Cơ cấu doanh thu danh mục sản phẩm chủ lực với chú thích phân bổ đầy đủ bên phải.",
                                data_df=curr_df,
                                card_id="stat_donut_rev",
                                lang=lang
                            )
                    with pc2:
                        if "bar_customer" in plotly_charts:
                            render_chart_card(
                                plotly_charts["bar_customer"],
                                "Top Doanh Thu Khách Hàng",
                                "Phân bổ tổng doanh thu khách hàng trọng điểm với số tiền VNĐ hiển thị trực tiếp bên cạnh cột.",
                                data_df=curr_df,
                                card_id="stat_bar_cust",
                                lang=lang
                            )
                            
                    if "box_distribution" in plotly_charts:
                        render_chart_card(
                            plotly_charts["box_distribution"],
                            "Phân Phối Giá Trị Đơn Hàng & Phát Hiện Ngoại Lệ",
                            "Phân bố quy mô đơn hàng (Boxplot) định vị rõ mức trung vị và khoảng tứ phân vị.",
                            data_df=curr_df,
                            card_id="stat_box_dist",
                            lang=lang
                        )
                else:
                    st.info("Chưa đủ dữ liệu dạng số để vẽ biểu đồ phân tích.")

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

            # 6. NHẬN ĐỊNH CHIẾN LƯỢC & XUẤT BÁO CÁO TOÀN DIỆN
            st.write("")
            st.markdown(clean_html(f"""
            <div class="section-header-row notranslate" translate="no">
                {get_icon_tile("clipboard_check", "indigo")}
                <div class="section-header-title">{t("analytics_sub_insights", lang)}</div>
            </div>
            """), unsafe_allow_html=True)
            
            exec_insights = StatisticalAnalyticsEngine.generate_executive_insights(curr_df, fin_kpis, segments_df if 'segments_df' in locals() else None)
            
            formatted_insights = []
            for ins in exec_insights:
                safe_ins = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(ins))
                formatted_insights.append(f'<div style="margin-bottom: 12px; line-height: 1.65; font-size: 14px; color: var(--text-primary);">{safe_ins}</div>')
                
            st.markdown(clean_html(f"""
            <div class="bento-surface notranslate" translate="no">
                {''.join(formatted_insights)}
            </div>
            """), unsafe_allow_html=True)
            
            # Nút xuất Excel đa sheet đầy đủ
            analytics_buffer = io.BytesIO()
            with pd.ExcelWriter(analytics_buffer, engine="openpyxl") as writer:
                curr_df.to_excel(writer, sheet_name="Du_Lieu_Goc", index=False)
                if 'segments_df' in locals() and not segments_df.empty:
                    segments_df.to_excel(writer, sheet_name="Phan_Hang_Khach_Hang", index=False)
                pd.DataFrame([fin_kpis]).to_excel(writer, sheet_name="Chi_So_Tai_Chinh", index=False)
            analytics_bytes = analytics_buffer.getvalue()
            
            st.download_button(
                label=t("btn_export_analytics", lang),
                data=analytics_bytes,
                file_name=f"Bao_Cao_Thong_Ke_Minh_An_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )


# ====================================================================================================
# TAB 4: DANH MỤC BẢNG GIÁ & KHO KHẢ DỤNG
# ====================================================================================================
with tab_catalog:
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
                    st.session_state.catalog_df = sheets[first_sheet]
                    st.session_state.agent = MinhAnSalesAgent(st.session_state.catalog_df, st.session_state.sales_df, st.session_state.policy_df)
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
                with open(".env", "w", encoding="utf-8") as f:
                    f.write(f"GEMINI_API_KEY={new_key.strip()}\n")
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
