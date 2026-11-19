"""
Minh An Company B2B Sales Platform - High-End SaaS Design System (Edition 2026)
Inspired by Linear, Vercel, Stripe, and Notion Calendar.
Multi-layered ambient glow, animated mesh gradients, glassmorphism, and WCAG AA contrast.
"""

import re

def get_app_styles(is_dark: bool = False) -> str:
    """Generates zero-indent clean CSS with CSS variables for Light or Dark theme."""
    
    if is_dark:
        # Dark Theme Tokens (Deep Space Tech Navy & Ambient Glow)
        bg_canvas = "#070b18"
        bg_canvas_gradient = """
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.22) 0px, transparent 48%),
            radial-gradient(at 100% 0%, rgba(34, 211, 238, 0.16) 0px, transparent 45%),
            radial-gradient(at 50% 50%, rgba(15, 23, 42, 0.85) 0px, transparent 100%),
            radial-gradient(at 85% 90%, rgba(236, 72, 153, 0.15) 0px, transparent 45%),
            radial-gradient(at 15% 95%, rgba(245, 158, 11, 0.12) 0px, transparent 45%)
        """
        bg_surface = "rgba(21, 28, 54, 0.72)"
        bg_surface_elevated = "#17203d"
        bg_surface_subtle = "rgba(255, 255, 255, 0.04)"
        bg_navbar = "rgba(11, 16, 35, 0.86)"
        
        border_subtle = "rgba(255, 255, 255, 0.08)"
        border_card = "rgba(255, 255, 255, 0.10)"
        border_glow = "rgba(99, 102, 241, 0.4)"
        border_focus = "#6366f1"
        
        text_primary = "#f8fafc"
        text_secondary = "#94a3b8"
        text_muted = "#64748b"
        text_code = "#a5b4fc"
        
        shadow_card = "0 8px 32px 0 rgba(0, 0, 0, 0.45), 0 1px 3px 0 rgba(0, 0, 0, 0.3)"
        shadow_hover = "0 18px 48px -4px rgba(99, 102, 241, 0.25), 0 8px 24px -2px rgba(0, 0, 0, 0.5)"
        shadow_glow = "0 0 24px rgba(99, 102, 241, 0.35)"
        
        chip_bg = "rgba(99, 102, 241, 0.18)"
        chip_border = "rgba(99, 102, 241, 0.38)"
        chip_text = "#c7d2fe"
        
        tab_bg = "rgba(244, 114, 182, 0.18)"
        tab_active_bg = "linear-gradient(135deg, #F43F5E 0%, #EC4899 50%, #DB2777 100%)"
        tab_active_text = "#ffffff"
        
        input_bg = "rgba(11, 16, 35, 0.85)"
        grid_dot_color = "rgba(255, 255, 255, 0.05)"
    else:
        # Light Theme Tokens (Pure Crisp Canvas & Soft Prismatic Glow)
        bg_canvas = "#f5f7ff"
        bg_canvas_gradient = """
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 45%),
            radial-gradient(at 100% 0%, rgba(34, 211, 238, 0.10) 0px, transparent 40%),
            radial-gradient(at 50% 50%, rgba(245, 247, 255, 0.6) 0px, transparent 100%),
            radial-gradient(at 90% 90%, rgba(236, 72, 153, 0.09) 0px, transparent 42%),
            radial-gradient(at 10% 95%, rgba(245, 158, 11, 0.08) 0px, transparent 40%)
        """
        bg_surface = "rgba(255, 255, 255, 0.85)"
        bg_surface_elevated = "#ffffff"
        bg_surface_subtle = "#f1f5f9"
        bg_navbar = "rgba(255, 255, 255, 0.88)"
        
        border_subtle = "rgba(226, 232, 240, 0.9)"
        border_card = "rgba(226, 232, 240, 0.85)"
        border_glow = "rgba(99, 102, 241, 0.3)"
        border_focus = "#6366f1"
        
        text_primary = "#0f172a"
        text_secondary = "#334155"
        text_muted = "#64748b"
        text_code = "#4338ca"
        
        shadow_card = "0 8px 30px -4px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.03)"
        shadow_hover = "0 20px 45px -6px rgba(99, 102, 241, 0.15), 0 6px 16px -2px rgba(15, 23, 42, 0.06)"
        shadow_glow = "0 0 20px rgba(99, 102, 241, 0.2)"
        
        chip_bg = "rgba(99, 102, 241, 0.08)"
        chip_border = "rgba(99, 102, 241, 0.24)"
        chip_text = "#4338ca"
        
        tab_bg = "#FCE7F3"
        tab_active_bg = "linear-gradient(135deg, #F43F5E 0%, #EC4899 50%, #DB2777 100%)"
        tab_active_text = "#ffffff"
        
        input_bg = "rgba(255, 255, 255, 0.95)"
        grid_dot_color = "rgba(15, 23, 42, 0.04)"

    css = f"""
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {{
    --bg-canvas: {bg_canvas};
    --bg-surface: {bg_surface};
    --bg-surface-elevated: {bg_surface_elevated};
    --bg-surface-subtle: {bg_surface_subtle};
    --bg-navbar: {bg_navbar};
    --border-subtle: {border_subtle};
    --border-card: {border_card};
    --border-glow: {border_glow};
    --border-focus: {border_focus};
    
    --text-primary: {text_primary};
    --text-secondary: {text_secondary};
    --text-muted: {text_muted};
    --text-code: {text_code};
    
    --tab-bg: {tab_bg};
    --tab-active-bg: {tab_active_bg};
    --tab-active-text: {tab_active_text};
    
    --accent-indigo: #6366f1;
    --accent-cyan: #22d3ee;
    --accent-pink: #ec4899;
    --accent-amber: #f59e0b;
    --accent-emerald: #10b981;
    
    --accent-gradient: linear-gradient(135deg, #6366f1 0%, #22d3ee 100%);
    --accent-cta-gradient: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    --shimmer-gradient: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0) 100%);
    
    --status-success: #059669;
    --status-success-bg: {'rgba(5, 150, 105, 0.18)' if is_dark else '#ecfdf5'};
    --status-success-border: {'rgba(5, 150, 105, 0.4)' if is_dark else '#a7f3d0'};
    
    --status-warning: #d97706;
    --status-warning-bg: {'rgba(217, 119, 6, 0.18)' if is_dark else '#fffbeb'};
    --status-warning-border: {'rgba(217, 119, 6, 0.4)' if is_dark else '#fde68a'};
    
    --status-danger: #e11d48;
    --status-danger-bg: {'rgba(225, 29, 72, 0.18)' if is_dark else '#fff1f2'};
    --status-danger-border: {'rgba(225, 29, 72, 0.4)' if is_dark else '#fecdd3'};
    
    --shadow-card: {shadow_card};
    --shadow-hover: {shadow_hover};
    --shadow-glow: {shadow_glow};
    
    --radius-sm: 10px;
    --radius-md: 16px;
    --radius-lg: 22px;
    --radius-xl: 28px;
    --radius-pill: 9999px;
    --transition-smooth: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}}

/* -------------------------------------------------------------
   0. RESET & VIEWPORT (NO HORIZONTAL SCROLLBAR, FULL RESPONSIVE)
   ------------------------------------------------------------- */
* {{
    box-sizing: border-box !important;
}}

html, body {{
    overflow-x: hidden !important;
    max-width: 100vw !important;
    margin: 0 !important;
    padding: 0 !important;
    font-family: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.012em;
    background-color: var(--bg-canvas) !important;
}}

/* Ambient Background Aurora & Dot Pattern */
.stApp {{
    background-color: var(--bg-canvas) !important;
    background-image: 
        radial-gradient({grid_dot_color} 1px, transparent 1px),
        {bg_canvas_gradient} !important;
    background-size: 24px 24px, 100% 100% !important;
    background-attachment: fixed !important;
    overflow-x: hidden !important;
    max-width: 100vw !important;
    transition: background-color 0.25s ease;
}}

[data-testid="stAppViewContainer"] {{
    overflow-x: hidden !important;
    max-width: 100vw !important;
}}

/* Hide Default Streamlit Chrome */
#MainMenu, header[data-testid="stHeader"], footer, .stDeployButton,
div[data-testid="stToolbar"], div[data-testid="stDecoration"], div[data-testid="stStatusWidget"] {{
    display: none !important;
    visibility: hidden !important;
}}

.block-container {{
    padding-top: 1rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1320px !important;
    margin: 0 auto !important;
}}

/* Chống lỗi React DOM insertBefore do Google Translate */
.notranslate, [translate="no"] {{
    translate: no !important;
}}

/* -------------------------------------------------------------
   1. STICKY TOP NAVBAR (GLASSMORPHISM, 72PX HEIGHT, INTEGRATED)
   ------------------------------------------------------------- */
div[class*="st-key-minhan_header"] {{
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
    width: 100% !important;
    min-height: 72px !important;
    padding: 12px 26px !important;
    background: var(--bg-navbar) !important;
    backdrop-filter: blur(20px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(160%) !important;
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border-subtle) !important;
    box-shadow: 0 4px 24px -2px rgba(0, 0, 0, 0.08) !important;
    margin-bottom: 20px !important;
}}

div[class*="st-key-minhan_header"] [data-testid="stHorizontalBlock"] {{
    align-items: center !important;
    display: flex !important;
    gap: 16px !important;
}}

div[class*="st-key-minhan_header"] [data-testid="stColumn"] {{
    display: flex !important;
    align-items: center !important;
}}

/* Brand Section */
.brand-wrapper {{
    display: flex;
    align-items: center;
    gap: 14px;
    white-space: nowrap !important;
}}

.brand-icon-box {{
    width: 44px;
    height: 44px;
    border-radius: 14px;
    background: linear-gradient(135deg, #6366f1 0%, #22d3ee 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.45);
    flex-shrink: 0;
}}

.brand-title-text {{
    font-size: 21px;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    line-height: 1.15;
    white-space: nowrap !important;
}}

.brand-caption-text {{
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
    letter-spacing: 0.02em;
    line-height: 1.25;
    white-space: nowrap !important;
}}

/* Live Model Capsule Chip */
.model-status-chip {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: var(--radius-pill);
    background: {chip_bg};
    border: 1px solid {chip_border};
    color: {chip_text};
    font-size: 13px;
    font-weight: 700;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}}

.pulsing-emerald-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10b981;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6);
    animation: livePulse 2s infinite;
}}

@keyframes livePulse {{
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
    70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
}}

/* Segmented Control & Theme Button in Header */
div[class*="st-key-minhan_header"] [data-testid="stSegmentedControl"] {{
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
}}

div[class*="st-key-minhan_header"] div.stButton > button {{
    border-radius: var(--radius-pill) !important;
    min-height: 40px !important;
    height: 40px !important;
    padding: 0 16px !important;
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-card) !important;
    color: var(--text-primary) !important;
    box-shadow: var(--shadow-card) !important;
    transition: var(--transition-smooth) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

div[class*="st-key-minhan_header"] div.stButton > button:hover {{
    transform: scale(1.05) !important;
    border-color: var(--accent-indigo) !important;
    box-shadow: var(--shadow-glow) !important;
}}

/* -------------------------------------------------------------
   2. STICKY TABS (CÁC KHỐI HÌNH CHỮ NHẬT BO GÓC MÀU HỒNG PASTEL NỔI BẬT)
   ------------------------------------------------------------- */
div[data-testid="stTabs"] {{
    margin-top: 10px !important;
}}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    position: sticky !important;
    top: 76px !important;
    z-index: 990 !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 12px !important;
    background: transparent !important;
    padding: 8px 2px !important;
    border: none !important;
    margin-bottom: 24px !important;
    width: fit-content !important;
    max-width: 100% !important;
    overflow-x: auto !important;
    scrollbar-width: none !important;
    box-shadow: none !important;
}}

div[data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar {{
    display: none !important;
}}

/* Hide default ugly underline borders and orange highlights */
div[data-testid="stTabs"] [data-baseweb="tab-border"] {{
    display: none !important;
    height: 0px !important;
    width: 0px !important;
    visibility: hidden !important;
    background: transparent !important;
}}

div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
    display: none !important;
    height: 0px !important;
    width: 0px !important;
    visibility: hidden !important;
    background: transparent !important;
}}

/* Khối hình chữ nhật bo góc màu hồng pastel cho từng tab */
div[data-testid="stTabs"] [data-baseweb="tab"],
div[data-testid="stTabs"] button[role="tab"],
div[data-testid="stTabs"] [role="tab"] {{
    background: {'#FCE7F3' if not is_dark else 'rgba(244, 114, 182, 0.18)'} !important;
    border: 1.5px solid {'#F472B6' if not is_dark else 'rgba(244, 114, 182, 0.45)'} !important;
    border-radius: 12px !important;
    padding: 10px 22px !important;
    font-size: 14.5px !important;
    font-weight: 700 !important;
    color: {'#9D174D' if not is_dark else '#FBCFE8'} !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    white-space: nowrap !important;
    cursor: pointer !important;
    letter-spacing: -0.2px !important;
    box-shadow: 0 2px 8px {'rgba(244, 114, 182, 0.2)' if not is_dark else 'rgba(0, 0, 0, 0.3)'} !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}}

div[data-testid="stTabs"] [data-baseweb="tab"] p,
div[data-testid="stTabs"] [data-baseweb="tab"] span,
div[data-testid="stTabs"] button[role="tab"] p,
div[data-testid="stTabs"] button[role="tab"] span,
div[data-testid="stTabs"] [role="tab"] p,
div[data-testid="stTabs"] [role="tab"] span {{
    color: {'#9D174D' if not is_dark else '#FBCFE8'} !important;
    font-size: 14.5px !important;
    font-weight: 700 !important;
}}

/* Hiệu ứng Hover: Nổi khối và sáng viền hồng */
div[data-testid="stTabs"] [data-baseweb="tab"]:hover,
div[data-testid="stTabs"] button[role="tab"]:hover,
div[data-testid="stTabs"] [role="tab"]:hover {{
    background: {'#FBCFE8' if not is_dark else 'rgba(244, 114, 182, 0.28)'} !important;
    border-color: {'#EC4899' if not is_dark else '#F472B6'} !important;
    color: {'#831843' if not is_dark else '#FFFFFF'} !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px {'rgba(236, 72, 153, 0.3)' if not is_dark else 'rgba(244, 114, 182, 0.35)'} !important;
}}

div[data-testid="stTabs"] [data-baseweb="tab"]:hover p,
div[data-testid="stTabs"] [data-baseweb="tab"]:hover span,
div[data-testid="stTabs"] button[role="tab"]:hover p,
div[data-testid="stTabs"] button[role="tab"]:hover span,
div[data-testid="stTabs"] [role="tab"]:hover p,
div[data-testid="stTabs"] [role="tab"]:hover span {{
    color: {'#831843' if not is_dark else '#FFFFFF'} !important;
}}

/* Tab đang kích hoạt: Khối hình chữ nhật màu hồng đậm / hồng đào nổi bật rực rỡ */
div[data-testid="stTabs"] [aria-selected="true"],
div[data-testid="stTabs"] button[aria-selected="true"],
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    background: linear-gradient(135deg, #F43F5E 0%, #EC4899 50%, #DB2777 100%) !important;
    color: #FFFFFF !important;
    border: 1.5px solid #FDA4AF !important;
    border-radius: 12px !important;
    box-shadow: 0 6px 20px rgba(244, 63, 94, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    font-weight: 800 !important;
    transform: translateY(-1px) scale(1.02) !important;
}}

div[data-testid="stTabs"] [aria-selected="true"] p,
div[data-testid="stTabs"] [aria-selected="true"] span,
div[data-testid="stTabs"] button[aria-selected="true"] p,
div[data-testid="stTabs"] button[aria-selected="true"] span,
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] p,
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] span {{
    color: #FFFFFF !important;
    font-weight: 800 !important;
}}

/* -------------------------------------------------------------
   2.1 WORKFLOW STEP NAVIGATION DOCK (MODERN TABS/PILLS IN TAB 1)
   ------------------------------------------------------------- */
.step-nav-dock {{
    background: var(--bg-surface);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border-card);
    border-radius: 18px;
    padding: 8px 10px;
    margin-bottom: 22px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
}}

.step-nav-dock div[data-testid="stHorizontalBlock"] {{
    gap: 8px !important;
}}

.step-nav-dock div.stButton > button {{
    min-height: 44px !important;
    height: 44px !important;
    padding: 0 12px !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    border: 1px solid transparent !important;
    letter-spacing: -0.2px !important;
    white-space: nowrap !important;
}}

.step-nav-dock div.stButton > button[kind="secondary"],
.step-nav-dock div.stButton > button[data-testid="baseButton-secondary"] {{
    background: var(--bg-surface-subtle) !important;
    color: var(--text-secondary) !important;
    border-color: var(--border-subtle) !important;
    box-shadow: none !important;
}}

.step-nav-dock div.stButton > button[kind="secondary"]:hover,
.step-nav-dock div.stButton > button[data-testid="baseButton-secondary"]:hover {{
    background: rgba(99, 102, 241, 0.08) !important;
    color: var(--text-primary) !important;
    border-color: rgba(99, 102, 241, 0.25) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.15) !important;
}}

.step-nav-dock div.stButton > button[kind="primary"],
.step-nav-dock div.stButton > button[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, #4f46e5 0%, #2563eb 50%, #06b6d4 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    box-shadow: 0 4px 16px rgba(79, 70, 229, 0.45) !important;
    transform: translateY(-1px) scale(1.02) !important;
}}

/* Secondary Buttons General Styling */
div.stButton > button[kind="secondary"],
div.stButton > button[data-testid="baseButton-secondary"] {{
    background: var(--bg-surface) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: var(--radius-pill) !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
    transition: var(--transition-smooth) !important;
}}

div.stButton > button[kind="secondary"]:hover,
div.stButton > button[data-testid="baseButton-secondary"]:hover {{
    background: var(--bg-surface-elevated) !important;
    color: var(--text-primary) !important;
    border-color: var(--accent-indigo) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.18) !important;
}}

/* -------------------------------------------------------------
   3. HERO SHOWCASE BENTO CARD (LINEAR / STRIPE STYLE)
   ------------------------------------------------------------- */
.hero-saas-card {{
    background: {'linear-gradient(135deg, rgba(21, 28, 54, 0.95) 0%, rgba(30, 41, 75, 0.85) 100%)' if is_dark else 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%)'};
    border-radius: var(--radius-xl);
    padding: 38px 42px;
    border: 1px solid var(--border-card);
    box-shadow: var(--shadow-card);
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(20px);
}}

.hero-saas-card::before {{
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 75% 20%, rgba(99, 102, 241, 0.12) 0%, transparent 40%);
    pointer-events: none;
}}

.hero-top-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 5px 16px;
    border-radius: var(--radius-pill);
    background: {'rgba(99, 102, 241, 0.22)' if is_dark else '#eef2ff'};
    color: {'#c7d2fe' if is_dark else '#4338ca'};
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 14px;
    border: 1px solid {'rgba(99, 102, 241, 0.35)' if is_dark else '#e0e7ff'};
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15);
}}

.hero-main-title {{
    font-size: clamp(32px, 4vw, 52px);
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text-primary);
    line-height: 1.25;
    margin-bottom: 12px;
}}

.gradient-shimmer-text {{
    background: linear-gradient(135deg, #6366f1 0%, #22d3ee 35%, #ec4899 70%, #6366f1 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 8s ease infinite;
    display: inline-block;
    white-space: nowrap;
    font-weight: 800;
}}

@keyframes gradientShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

.hero-desc-text {{
    font-size: 16px;
    color: var(--text-secondary);
    max-width: 860px;
    line-height: 1.65;
    margin-bottom: 24px;
}}

/* Hero Micro KPI Grid Row */
.hero-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-top: 22px;
}}

@media (max-width: 1024px) {{
    .hero-kpi-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 560px) {{
    .hero-kpi-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }}
    .hero-kpi-tile {{
        padding: 10px 12px;
        gap: 10px;
    }}
    .hero-kpi-num {{
        font-size: 16px;
    }}
    .hero-kpi-lbl {{
        font-size: 11px;
    }}
}}

.hero-kpi-tile {{
    background: var(--bg-surface-subtle);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 14px;
    backdrop-filter: blur(12px);
    transition: var(--transition-smooth);
    min-width: 0;
}}

.hero-kpi-tile:hover {{
    transform: translateY(-2px);
    border-color: var(--border-glow);
    background: var(--bg-surface);
    box-shadow: var(--shadow-hover);
}}

.hero-kpi-num {{
    font-size: 20px;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.1;
}}

.hero-kpi-lbl {{
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}

/* -------------------------------------------------------------
   4. STEPPER INDICATOR (3-STEP VISUAL PROGRESSION)
   ------------------------------------------------------------- */
.stepper-container {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-surface);
    border: 1px solid var(--border-card);
    border-radius: var(--radius-lg);
    padding: 16px 24px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-card);
}}

.step-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
}}

.step-circle {{
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 700;
    flex-shrink: 0;
}}

.step-circle.active {{
    background: var(--accent-gradient);
    color: #ffffff;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}}

.step-circle.completed {{
    background: var(--status-success);
    color: #ffffff;
}}

.step-circle.warning {{
    background: var(--status-warning);
    color: #ffffff;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}}

.step-circle.dimmed {{
    background: var(--bg-surface-subtle);
    color: var(--text-muted);
    opacity: 0.45;
    border: 1px dashed var(--border-subtle);
}}

.step-circle.idle {{
    background: var(--bg-surface-subtle);
    color: var(--text-muted);
    border: 1px solid var(--border-subtle);
}}

.step-label {{
    font-size: 14px;
    font-weight: 700;
    color: var(--text-primary);
}}

.step-sublabel {{
    font-size: 11px;
    color: var(--text-muted);
    white-space: nowrap;
}}

.step-divider {{
    height: 2px;
    flex: 0.3;
    background: var(--border-subtle);
    margin: 0 10px;
}}

/* Audit Trail & Data Quality Cards */
.audit-step-card {{
    background: var(--bg-surface-subtle);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    margin-bottom: 10px;
    border-left: 4px solid var(--accent-indigo);
    transition: var(--transition-smooth);
}}

.audit-step-card:hover {{
    background: var(--bg-surface);
    border-color: var(--border-glow);
}}

.quality-score-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 18px;
    border-radius: var(--radius-pill);
    font-size: 15px;
    font-weight: 800;
}}

/* -------------------------------------------------------------
   5. BENTO SURFACES & SECTION HEADERS
   ------------------------------------------------------------- */
.bento-surface {{
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    border: 1px solid var(--border-card);
    box-shadow: var(--shadow-card);
    margin-bottom: 20px;
    transition: var(--transition-smooth);
    backdrop-filter: blur(16px);
}}

.bento-surface:hover {{
    box-shadow: var(--shadow-hover);
    border-color: var(--border-glow);
    transform: translateY(-2px);
}}

/* -------------------------------------------------------------
   5.1. DEDICATED PLOTLY CHART CARDS & INSIGHT CHIPS (SAAS 2026)
   ------------------------------------------------------------- */
div[class*="st-key-chart_box_"] {{
    background: {'rgba(21, 28, 54, 0.72)' if is_dark else 'rgba(255, 255, 255, 0.90)'} !important;
    border: 1px solid {'rgba(255, 255, 255, 0.10)' if is_dark else 'rgba(0, 0, 0, 0.08)'} !important;
    border-radius: 22px !important;
    padding: 22px 24px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05), 0 12px 32px rgba(99, 102, 241, 0.14) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    overflow: hidden !important;
    margin-bottom: 22px !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
}}

div[class*="st-key-chart_box_"]:hover {{
    transform: translateY(-2px) !important;
    border-color: var(--border-glow) !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 18px 40px rgba(99, 102, 241, 0.20) !important;
}}

/* Plotly clipping & transparent canvas */
div[data-testid="stPlotlyChart"] {{
    border-radius: 16px !important;
    overflow: hidden !important;
    background: transparent !important;
}}

div[data-testid="stPlotlyChart"] .plot-container {{
    border-radius: 16px !important;
    overflow: hidden !important;
    background: transparent !important;
}}

div[data-testid="stPlotlyChart"] svg.main-svg {{
    border-radius: 16px !important;
    background: transparent !important;
}}

/* Automated Real-Data Insight Chip with Lightbulb */
.chart-insight-chip {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    background: {'linear-gradient(135deg, rgba(99, 102, 241, 0.16) 0%, rgba(30, 27, 75, 0.35) 100%)' if is_dark else 'linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(248, 250, 252, 0.9) 100%)'};
    border: 1px solid {'rgba(99, 102, 241, 0.30)' if is_dark else 'rgba(99, 102, 241, 0.22)'};
    border-left: 4px solid #6366F1;
    border-radius: 14px;
    padding: 12px 16px;
    margin-top: 14px;
    font-size: 13.5px;
    line-height: 1.55;
    color: var(--text-primary);
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.08);
}}

.legendtext {{
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: 12.5px !important;
}}

.chart-insight-icon {{
    font-size: 16px;
    flex-shrink: 0;
    margin-top: 1px;
}}

.chart-card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}}

.chart-card-title {{
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}}

/* Primary Action Download Button (Quotation Excel) */
div[data-testid="stDownloadButton"] > button[kind="primary"] {{
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9999px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 14.5px !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    letter-spacing: 0.01em !important;
}}

div[data-testid="stDownloadButton"] > button[kind="primary"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
}}

/* Compact Empty State Container */
.chart-empty-state {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 18px 22px;
    background: {'rgba(99, 102, 241, 0.06)' if is_dark else 'rgba(99, 102, 241, 0.04)'};
    border: 1px dashed {'rgba(99, 102, 241, 0.28)' if is_dark else 'rgba(99, 102, 241, 0.20)'};
    border-radius: 14px;
    color: var(--text-muted);
    font-size: 13.5px;
    margin-top: 8px;
}}

.chart-empty-icon {{
    font-size: 20px;
    flex-shrink: 0;
}}

/* 40x40 Gradient Icon Header Tile */
.section-header-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 18px;
}}

.icon-tile-gradient {{
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    flex-shrink: 0;
}}

.icon-tile-indigo {{
    background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
}}

.icon-tile-cyan {{
    background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
    box-shadow: 0 4px 14px rgba(6, 182, 212, 0.35);
}}

.icon-tile-pink {{
    background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);
    box-shadow: 0 4px 14px rgba(236, 72, 153, 0.35);
}}

.icon-tile-amber {{
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
}}

.icon-tile-emerald {{
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
}}

.section-header-title {{
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}}

/* -------------------------------------------------------------
   6. OPERATIONAL RULES CHIPS (COLOR ACCENTED SUB-CARDS)
   ------------------------------------------------------------- */
.rule-subcard {{
    background: var(--bg-surface-subtle);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    border: 1px solid var(--border-subtle);
    transition: var(--transition-smooth);
}}

.rule-subcard:hover {{
    transform: translateX(4px);
    background: var(--bg-surface);
}}

.rule-subcard.sku-accent {{
    border-left: 4px solid #6366f1 !important;
}}

.rule-subcard.sla-accent {{
    border-left: 4px solid #06b6d4 !important;
}}

.rule-subcard.matrix-accent {{
    border-left: 4px solid #f59e0b !important;
}}

/* -------------------------------------------------------------
   7. STAT KPI BLOCKS (HIGH CONTRAST & ACCENT STRIP)
   ------------------------------------------------------------- */
.stat-kpi-card {{
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 22px 24px;
    border: 1px solid var(--border-card);
    box-shadow: var(--shadow-card);
    position: relative;
    overflow: hidden;
    transition: var(--transition-smooth);
    backdrop-filter: blur(16px);
}}

.stat-kpi-card:hover {{
    transform: translateY(-4px);
    box-shadow: var(--shadow-hover);
    border-color: var(--border-glow);
}}

.stat-kpi-card::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--accent-gradient);
}}

.stat-kpi-value {{
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    line-height: 1.15;
    margin-bottom: 4px;
    font-family: 'Be Vietnam Pro', sans-serif;
}}

.stat-kpi-label {{
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
}}

/* -------------------------------------------------------------
   8. LINE ITEMS (PRODUCT CATALOG ROW TILES)
   ------------------------------------------------------------- */
.item-showcase-tile {{
    background: var(--bg-surface);
    border: 1px solid var(--border-card);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: var(--transition-smooth);
}}

.item-showcase-tile:hover {{
    border-color: var(--border-glow);
    background: var(--bg-surface-elevated);
    transform: translateX(4px);
    box-shadow: var(--shadow-card);
}}

.sku-mono-pill {{
    display: inline-block;
    padding: 3px 9px;
    border-radius: 6px;
    background: var(--bg-surface-subtle);
    color: var(--text-code);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
}}

/* -------------------------------------------------------------
   9. BADGES & PILLS (WCAG AA CONTRAST)
   ------------------------------------------------------------- */
.badge-capsule {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: var(--radius-pill);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.01em;
}}

.badge-green {{
    background: var(--status-success-bg);
    color: var(--status-success);
    border: 1px solid var(--status-success-border);
}}

.badge-amber {{
    background: var(--status-warning-bg);
    color: var(--status-warning);
    border: 1px solid var(--status-warning-border);
}}

.badge-red {{
    background: var(--status-danger-bg);
    color: var(--status-danger);
    border: 1px solid var(--status-danger-border);
}}

/* -------------------------------------------------------------
   10. BUTTONS & FORM INPUTS (FIXED CLIPPING, FULL WIDTH)
   ------------------------------------------------------------- */
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {{
    background: var(--accent-cta-gradient) !important;
    color: #ffffff !important;
    border-radius: var(--radius-pill) !important;
    padding: 12px 26px !important;
    min-height: 46px !important;
    font-weight: 700 !important;
    font-size: 14.5px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    box-shadow: 0 8px 24px -4px rgba(99, 102, 241, 0.45) !important;
    transition: var(--transition-smooth) !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    text-overflow: clip !important;
    line-height: 1.4 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="baseButton-primary"]:hover {{
    box-shadow: 0 12px 32px -4px rgba(99, 102, 241, 0.6) !important;
    transform: translateY(-2px) scale(1.01) !important;
}}

div.stButton > button[kind="primary"]:active,
div.stButton > button[data-testid="baseButton-primary"]:active {{
    transform: translateY(1px) scale(0.99) !important;
}}

div.stDownloadButton > button {{
    border-radius: var(--radius-pill) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 24px !important;
    min-height: 46px !important;
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-card) !important;
    color: var(--text-primary) !important;
    box-shadow: var(--shadow-card) !important;
    transition: var(--transition-smooth) !important;
    white-space: normal !important;
    word-wrap: break-word !important;
}}

div.stDownloadButton > button:hover {{
    background: var(--bg-surface-elevated) !important;
    border-color: var(--accent-indigo) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-glow) !important;
}}

/* Textarea & Inputs - Increased Height, No Top Cut */
.stTextArea textarea {{
    border-radius: 14px !important;
    border: 1px solid var(--border-card) !important;
    background: {input_bg} !important;
    color: var(--text-primary) !important;
    padding: 16px 18px !important;
    font-size: 15px !important;
    line-height: 1.65 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    min-height: 200px !important;
}}

.stTextArea textarea:focus {{
    border-color: var(--accent-indigo) !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2) !important;
    outline: none !important;
}}

.stTextInput input {{
    border-radius: 12px !important;
    border: 1px solid var(--border-card) !important;
    background: {input_bg} !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}

.stTextInput input:focus {{
    border-color: var(--accent-indigo) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
}}

/* -------------------------------------------------------------
   11. INTERACTIVE COPILOT CHAT & TELEGRAM CARD
   ------------------------------------------------------------- */
.telegram-approval-card {{
    background: {'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)' if is_dark else 'linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%)'};
    border: 1px solid {'rgba(99, 102, 241, 0.35)' if is_dark else '#c7d2fe'};
    border-radius: var(--radius-lg);
    padding: 22px 24px;
    margin: 16px 0;
    box-shadow: var(--shadow-card);
}}

.copilot-container {{
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-card);
    padding: 22px 26px;
    margin-top: 20px;
    box-shadow: var(--shadow-card);
}}

.copilot-msg-box {{
    background: var(--bg-surface-subtle);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    margin-top: 14px;
    border-left: 4px solid var(--accent-cyan);
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-primary);
}}

/* Quick Prompt Pills */
.quick-prompt-pill {{
    display: inline-block;
    padding: 6px 14px;
    border-radius: var(--radius-pill);
    background: var(--bg-surface-subtle);
    border: 1px solid var(--border-subtle);
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    cursor: pointer;
    margin: 4px;
    transition: var(--transition-smooth);
}}

.quick-prompt-pill:hover {{
    background: var(--accent-indigo);
    color: #ffffff;
    border-color: var(--accent-indigo);
    transform: translateY(-1px);
}}

/* Footer */
.footer-bar-modern {{
    text-align: center;
    padding: 34px 0 14px 0;
    color: var(--text-muted);
    font-size: 13px;
    font-weight: 500;
    border-top: 1px solid var(--border-card);
    margin-top: 50px;
}}

/* -------------------------------------------------------------
   12. RESPONSIVE BREAKPOINTS
   ------------------------------------------------------------- */
@media (max-width: 768px) {{
    div[class*="st-key-minhan_header"] {{
        padding: 12px 16px !important;
    }}
    .hero-saas-card {{
        padding: 24px 20px;
    }}
    .hero-main-title {{
        font-size: 26px;
    }}
    .stepper-container {{
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }}
    .step-divider {{
        display: none;
    }}
    .item-showcase-tile {{
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }}
}}

@media (prefers-reduced-motion: reduce) {{
    * {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }}
}}
"""
    return css


def clean_html(raw_html: str) -> str:
    """Strips leading/trailing whitespace per line, eliminates blank lines, and converts markdown bold to HTML strong tags."""
    cleaned_lines = []
    for line in raw_html.strip().splitlines():
        stripped = line.strip()
        if stripped:
            converted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', stripped)
            cleaned_lines.append(converted)
    return "\n".join(cleaned_lines)

