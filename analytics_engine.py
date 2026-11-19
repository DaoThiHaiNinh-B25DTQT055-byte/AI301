"""
Minh An Statistical & AI Analytics Engine (Edition 2026)
Executes the standard 8-step analytical framework, descriptive statistics, financial metrics,
flexible customer RFM segmentation, confidence estimation, and Plotly interactive chart generation.
"""

import re
import unicodedata
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from config import CUSTOMER_TIERS, CONFIDENCE_THRESHOLD_MEDIUM


def strip_accents(text: str) -> str:
    """Chuyển đổi chuỗi tiếng Việt có dấu thành không dấu chuẩn xác để so khớp synonym."""
    text = str(text).replace('Đ', 'D').replace('đ', 'd')
    nfkd = unicodedata.normalize('NFKD', text)
    cleaned = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9_]', '', cleaned.lower().replace(' ', '_'))


def clean_vn_series(series: pd.Series) -> pd.Series:
    """Chuyển đổi một Series dữ liệu số/tiền tệ Việt Nam sang dạng float an toàn tuyệt đối."""
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors='coerce').fillna(0.0)
    def _parse(val):
        if pd.isna(val) or val is None:
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip()
        s = re.sub(r'[^\d.,-]', '', s)
        if not s:
            return 0.0
        if '.' in s and ',' in s:
            s = s.replace('.', '').replace(',', '.')
        elif s.count('.') > 1:
            s = s.replace('.', '')
        elif re.match(r'^-?\d{1,3}(\.\d{3})+$', s):
            s = s.replace('.', '')
        elif ',' in s and re.match(r'^-?\d+,\d+$', s):
            s = s.replace(',', '.')
        try:
            return float(s)
        except Exception:
            return 0.0
    return series.apply(_parse)


class StatisticalAnalyticsEngine:
    """Enterprise analytics engine delivering standard 8-step data workflow and financial intelligence."""

    @classmethod
    def resolve_revenue_column(cls, df: pd.DataFrame) -> Optional[str]:
        """Tự động tìm kiếm và xác định cột doanh thu/thành tiền từ DataFrame bất kỳ."""
        if df.empty:
            return None
        # 1. Khớp chính xác
        if "total_price" in df.columns:
            return "total_price"
        if "FinalTotal" in df.columns:
            return "FinalTotal"
            
        # 2. Khớp từ đồng nghĩa với bóc tách dấu tiếng Việt
        synonyms = [
            "thanh_tien", "doanh_thu", "doanh_so", "revenue", "sales", 
            "total", "total_price", "total_amount", "tong_tien", "gia_tri", 
            "tong_gia_tri", "net_amount", "amount", "finaltotal", "listtotal",
            "tien_thanh_toan", "tien", "thanh_toan", "tri_gia"
        ]
        col_norm = {c: strip_accents(c) for c in df.columns}
        for orig, norm in col_norm.items():
            if norm in synonyms:
                return orig
        for orig, norm in col_norm.items():
            for syn in synonyms:
                if syn in norm or norm in syn:
                    return orig
                    
        # 3. Nếu có cả đơn giá và số lượng, tự tạo cột total_price
        p_col = next((c for c, n in col_norm.items() if any(k in n for k in ["price", "gia", "don_gia", "unit_price"])), None)
        q_col = next((c for c, n in col_norm.items() if any(k in n for k in ["qty", "luong", "sl", "quantity"])), None)
        if p_col and q_col and p_col != q_col:
            try:
                p_num = clean_vn_series(df[p_col])
                q_num = clean_vn_series(df[q_col]).replace(0, 1)
                df["total_price"] = p_num * q_num
                return "total_price"
            except Exception:
                pass
                
        # 4. Dự phòng cột số có tổng lớn nhất
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            return max(num_cols, key=lambda c: df[c].sum() if pd.notna(df[c].sum()) else 0)
            
        return None

    @classmethod
    def resolve_customer_column(cls, df: pd.DataFrame) -> str:
        """Tự động tìm kiếm và xác định cột khách hàng/doanh nghiệp từ DataFrame bất kỳ."""
        if df.empty:
            return ""
        if "customer_name" in df.columns:
            return "customer_name"
            
        synonyms = ["khach_hang", "customer", "customer_name", "company", "ten_khach_hang", "don_vi", "cong_ty", "client", "buyer", "organization", "nguoi_mua", "doanh_nghiep", "doi_tac"]
        col_norm = {c: strip_accents(c) for c in df.columns}
        for orig, norm in col_norm.items():
            if norm in synonyms or any(s in norm for s in synonyms):
                return orig
                
        non_num = df.select_dtypes(exclude=[np.number]).columns.tolist()
        if non_num:
            return non_num[0]
        return df.columns[0]

    @classmethod
    def resolve_category_column(cls, df: pd.DataFrame) -> Optional[str]:
        """Tự động tìm kiếm cột sản phẩm/danh mục từ DataFrame bất kỳ."""
        if df.empty:
            return None
        for cand in ["product_name", "ProductName", "Category", "danh_muc", "nhom"]:
            if cand in df.columns:
                return cand
                
        synonyms = ["san_pham", "product", "ten_hang", "hang_hoa", "thiet_bi", "category", "danh_muc", "nhom", "item", "sku"]
        col_norm = {c: strip_accents(c) for c in df.columns}
        for orig, norm in col_norm.items():
            if any(s in norm for s in synonyms):
                return orig
                
        non_num = df.select_dtypes(exclude=[np.number]).columns.tolist()
        cust_col = cls.resolve_customer_column(df)
        other_non_num = [c for c in non_num if c != cust_col]
        if other_non_num:
            return other_non_num[0]
        return df.columns[0] if not df.empty else None

    @classmethod
    def compute_descriptive_statistics(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates central tendency, dispersion, percentiles, and counts across numerical columns."""
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        stats_summary = {}
        
        for col in num_cols:
            series = df[col].dropna()
            if len(series) == 0:
                continue
            q25 = float(series.quantile(0.25))
            q75 = float(series.quantile(0.75))
            stats_summary[str(col)] = {
                "count": int(series.count()),
                "sum": float(series.sum()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std()) if len(series) > 1 else 0.0,
                "min": float(series.min()),
                "max": float(series.max()),
                "q25": q25,
                "q75": q75,
                "iqr": float(q75 - q25)
            }
            
        return stats_summary

    @classmethod
    def compute_financial_kpis(cls, df: pd.DataFrame, revenue_col: Optional[str] = None, cost_rate: float = 0.78) -> Dict[str, Any]:
        """
        Calculates key B2B financial metrics:
        Total Revenue, Estimated Cost of Goods Sold (COGS), Gross Profit, Gross Margin %, Average Order Value (AOV).
        Tự động xác định cột doanh thu và không bao giờ crash KeyError.
        """
        if df.empty:
            return {
                "total_revenue": 0.0,
                "total_cogs": 0.0,
                "gross_profit": 0.0,
                "gross_margin_pct": 0.0,
                "aov": 0.0,
                "total_orders": 0
            }
            
        rev_col = revenue_col if (revenue_col and revenue_col in df.columns) else cls.resolve_revenue_column(df)
        if not rev_col or rev_col not in df.columns or df[rev_col].dropna().empty:
            return {
                "total_revenue": 0.0,
                "total_cogs": 0.0,
                "gross_profit": 0.0,
                "gross_margin_pct": 0.0,
                "aov": 0.0,
                "total_orders": len(df)
            }
            
        rev_series = clean_vn_series(df[rev_col])
        total_rev = float(rev_series.sum())
        total_cogs = float(total_rev * cost_rate)
        gross_profit = float(total_rev - total_cogs)
        margin_pct = round((gross_profit / total_rev * 100), 2) if total_rev > 0 else 0.0
        aov = round(total_rev / len(df), 0) if len(df) > 0 else 0.0
        
        return {
            "total_revenue": total_rev,
            "total_cogs": total_cogs,
            "gross_profit": gross_profit,
            "gross_margin_pct": margin_pct,
            "aov": aov,
            "total_orders": len(df)
        }

    @classmethod
    def segment_customers_rfm(cls, df: pd.DataFrame, 
                              customer_col: Optional[str] = None, 
                              revenue_col: Optional[str] = None,
                              date_col: Optional[str] = "order_date") -> pd.DataFrame:
        """
        Performs customer prioritization & segmentation based on order values, frequency, and recency.
        Assigns Tiers: VIP, PRIORITY, STANDARD with confidence score (%) and explanatory reason.
        Tự động dò tìm cột khách hàng và doanh thu, không bao giờ phát sinh KeyError.
        """
        if df.empty:
            return pd.DataFrame()
            
        cust_col = customer_col if (customer_col and customer_col in df.columns) else cls.resolve_customer_column(df)
        rev_col = revenue_col if (revenue_col and revenue_col in df.columns) else cls.resolve_revenue_column(df)
        
        if not cust_col or cust_col not in df.columns:
            return pd.DataFrame()
            
        work_df = df.copy()
        if rev_col and rev_col in work_df.columns:
            work_df["_rev_clean"] = clean_vn_series(work_df[rev_col])
        else:
            work_df["_rev_clean"] = 1.0
            
        grouped = work_df.groupby(cust_col).agg(
            total_spend=('_rev_clean', 'sum'),
            order_count=('_rev_clean', 'count'),
            avg_order_value=('_rev_clean', 'mean')
        ).reset_index()
        
        segments = []
        for _, row in grouped.iterrows():
            spend = float(row['total_spend'])
            count = int(row['order_count'])
            aov = round(float(row['avg_order_value']), 0)
            
            # Rule-based Tier Assignment
            if spend >= CUSTOMER_TIERS["VIP"]["min_revenue"] or count >= 5:
                tier = "VIP"
                confidence = 95.0 if spend >= 400_000_000 else 88.0
                reason = f"Doanh số lớn ({spend:,.0f} đ) hoặc tần suất đặt hàng cao ({count} đơn)."
            elif spend >= CUSTOMER_TIERS["PRIORITY"]["min_revenue"] or count >= 2:
                tier = "PRIORITY"
                confidence = 85.0
                reason = f"Đơn hàng quy mô vừa ({spend:,.0f} đ), khách hàng tiềm năng tăng trưởng."
            else:
                tier = "STANDARD"
                confidence = 80.0
                reason = f"Đơn hàng giá trị tiêu chuẩn ({spend:,.0f} đ)."
                
            needs_review = confidence < CONFIDENCE_THRESHOLD_MEDIUM
            
            segments.append({
                "Customer": str(row[cust_col]),
                "TotalSpend": spend,
                "OrderCount": count,
                "AOV": aov,
                "AssignedTier": tier,
                "ConfidencePct": confidence,
                "Reason": reason,
                "NeedsReview": needs_review
            })
            
        return pd.DataFrame(segments).sort_values(by="TotalSpend", ascending=False)

    @classmethod
    def flexible_segmentation(cls, df: pd.DataFrame, criteria_col: str, value_col: Optional[str] = None) -> pd.DataFrame:
        """
        Dynamically groups data by any selected attribute (Category, Region, Sales Rep, Priority).
        Calculates group share %, order volume, and value.
        """
        if criteria_col not in df.columns or df.empty:
            return pd.DataFrame()
            
        val_col = value_col if (value_col and value_col in df.columns) else cls.resolve_revenue_column(df)
        
        if val_col and val_col in df.columns:
            work_df = df.copy()
            work_df["_v_clean"] = clean_vn_series(work_df[val_col])
            grouped = work_df.groupby(criteria_col).agg(
                Count=('_v_clean', 'count'),
                TotalValue=('_v_clean', 'sum')
            ).reset_index()
            total_sum = grouped['TotalValue'].sum()
            grouped['SharePct'] = round((grouped['TotalValue'] / total_sum * 100), 1) if total_sum > 0 else 0.0
        else:
            grouped = df.groupby(criteria_col).size().reset_index(name='Count')
            grouped['SharePct'] = round((grouped['Count'] / len(df) * 100), 1)
            
        return grouped.sort_values(by="Count", ascending=False)

    @classmethod
    def build_financial_charts(cls, df: pd.DataFrame, is_dark: bool = False) -> Dict[str, go.Figure]:
        """Generates interactive Plotly charts adhering to the 2026 SaaS aesthetic with vibrant colors and side legends."""
        charts = {}
        if df.empty:
            return charts
            
        template = "plotly_dark" if is_dark else "plotly_white"
        text_color = "#F8FAFC" if is_dark else "#0F172A"
        muted_color = "#94A3B8" if is_dark else "#64748B"
        border_stroke = "#0f172a" if is_dark else "#ffffff"
        primary_color = "#818CF8" if is_dark else "#4F46E5"
        color_palette = ["#6366F1", "#06B6D4", "#10B981", "#EC4899", "#F59E0B", "#8B5CF6", "#3B82F6", "#14B8A6"]
        
        # Resolve columns dynamically
        cat_col = cls.resolve_category_column(df)
        val_col = cls.resolve_revenue_column(df)
        cust_col = cls.resolve_customer_column(df)
        
        # 1. Product / Category Breakdown Donut Chart
        if cat_col and val_col and val_col in df.columns:
            plot_df = df.copy()
            plot_df[val_col] = clean_vn_series(plot_df[val_col])
            agg = plot_df.groupby(cat_col)[val_col].sum().reset_index().sort_values(by=val_col, ascending=False).head(8)
            total_rev = agg[val_col].sum()
            rev_label = f"{total_rev/1e6:,.1f} Tr.₫" if total_rev >= 1e6 else f"{total_rev:,.0f} ₫"
            
            fig_donut = px.pie(
                agg, 
                names=cat_col, 
                values=val_col, 
                hole=0.68,
                color_discrete_sequence=color_palette,
                template=template
            )
            fig_donut.update_traces(
                textposition='inside', 
                textinfo='percent', 
                hovertemplate="<b>%{label}</b><br>Doanh thu: %{value:,.0f} ₫<br>Tỷ trọng: %{percent:.1%}<extra></extra>",
                marker=dict(line=dict(color=border_stroke, width=2.5))
            )
            fig_donut.update_layout(
                margin=dict(t=40, b=25, l=25, r=160),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.02,
                    bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Be Vietnam Pro, sans-serif", size=12.5, color=text_color)
                ),
                annotations=[
                    dict(
                        text=f"<span style='font-size:11px;font-weight:700;letter-spacing:1px;color:{muted_color};text-transform:uppercase;'>TỔNG DOANH THU</span><br><span style='font-size:20px;font-weight:800;color:{primary_color};'>{rev_label}</span>",
                        x=0.5, y=0.5,
                        font_family="Be Vietnam Pro, sans-serif",
                        showarrow=False
                    )
                ],
                font=dict(family="Be Vietnam Pro, sans-serif", size=13),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            charts["donut_revenue"] = fig_donut

        # 2. Revenue by Customer / Horizontal Bar Chart with Rounded Corners & Side Value Callouts
        if cust_col and val_col and val_col in df.columns:
            plot_df = df.copy()
            plot_df[val_col] = clean_vn_series(plot_df[val_col])
            cust_agg = plot_df.groupby(cust_col)[val_col].sum().reset_index().sort_values(by=val_col, ascending=True).tail(8)
            cust_agg["display_text"] = cust_agg[val_col].apply(lambda v: f" {v/1e6:,.1f} Tr.₫" if v >= 1e6 else f" {v:,.0f} ₫")
            
            fig_bar = px.bar(
                cust_agg,
                x=val_col,
                y=cust_col,
                orientation='h',
                template=template,
                text="display_text",
                color=val_col,
                color_continuous_scale=[[0, "#A5B4FC"], [0.5, "#6366F1"], [1, "#4338CA"]]
            )
            fig_bar.update_traces(
                textposition='outside',
                texttemplate="<b>%{text}</b>",
                hovertemplate="<b>%{y}</b><br>Doanh thu: %{x:,.0f} ₫<extra></extra>",
                marker=dict(cornerradius=8, line=dict(width=0))
            )
            fig_bar.update_layout(
                coloraxis_showscale=False,
                xaxis_title="Tổng Doanh Thu (VNĐ)",
                yaxis_title="",
                margin=dict(t=35, b=30, l=120, r=110),
                font=dict(family="Be Vietnam Pro, sans-serif", size=12.5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            charts["bar_customer"] = fig_bar

        # 3. Value Distribution Histogram / Boxplot with Median Callout & Modern Translucent Fill
        if val_col and val_col in df.columns:
            plot_df = df.copy()
            plot_df[val_col] = pd.to_numeric(plot_df[val_col], errors='coerce').dropna()
            if len(plot_df) >= 3:
                fig_box = px.box(
                    plot_df,
                    y=val_col,
                    points="all",
                    template=template,
                    color_discrete_sequence=["#F43F5E"]
                )
                fig_box.update_traces(
                    fillcolor="rgba(244, 63, 94, 0.14)",
                    line=dict(color="#F43F5E", width=2),
                    marker=dict(color="#FB7185", size=7, opacity=0.85),
                    jitter=0.25,
                    pointpos=-1.8,
                    hovertemplate="Giá trị: %{y:,.0f} ₫<extra></extra>"
                )
                med_val = plot_df[val_col].median()
                med_fmt = f"{med_val/1e6:,.1f} Tr.₫" if med_val >= 1e6 else f"{med_val:,.0f} ₫"
                fig_box.add_annotation(
                    y=med_val,
                    x=0.35,
                    text=f"<b>Trung vị: {med_fmt}</b>",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="#F43F5E",
                    arrowwidth=1.5,
                    ax=65,
                    ay=-22,
                    font=dict(size=12, color=text_color, family="Be Vietnam Pro, sans-serif"),
                    bgcolor="rgba(244, 63, 94, 0.16)",
                    bordercolor="#F43F5E",
                    borderwidth=1.5,
                    borderpad=5
                )
                fig_box.update_layout(
                    yaxis_title="Giá Trị Đơn Hàng (VNĐ)",
                    margin=dict(t=35, b=25, l=60, r=40),
                    font=dict(family="Be Vietnam Pro, sans-serif", size=12.5),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                charts["box_distribution"] = fig_box

        return charts

    @classmethod
    def generate_executive_insights(cls, df: pd.DataFrame, financial_kpis: Dict[str, Any], segments_df: Optional[pd.DataFrame] = None) -> List[str]:
        """Synthesizes key analytical insights, operational risk factors, and recommended next actions."""
        insights = []
        rev = financial_kpis.get("total_revenue", 0)
        aov = financial_kpis.get("aov", 0)
        margin = financial_kpis.get("gross_margin_pct", 0)
        
        # 1. Main Findings
        insights.append(f"🎯 **Quy mô Doanh thu & Biên lợi nhuận:** Tổng doanh thu ghi nhận **{rev:,.0f} đ** qua {len(df)} dòng dữ liệu, biên lợi nhuận gộp ước đạt **{margin:.1f}%**, giá trị đơn bình quân (AOV) đạt **{aov:,.0f} đ**.")
        
        # 2. Customer Concentration
        if segments_df is not None and not segments_df.empty:
            vip_count = len(segments_df[segments_df["AssignedTier"] == "VIP"])
            vip_spend = segments_df[segments_df["AssignedTier"] == "VIP"]["TotalSpend"].sum()
            vip_share = (vip_spend / rev * 100) if rev > 0 else 0
            insights.append(f"👥 **Tập trung Khách hàng Trọng điểm:** Phân khúc VIP gồm **{vip_count} đối tác**, đóng góp **{vip_share:.1f}%** tổng giá trị danh mục. Cần ưu tiên kênh hỗ trợ chuyên biệt và SLA giao hàng 24h.")
            
        # 3. Operational Risks & Actions
        insights.append("⚠️ **Cảnh báo Rủi ro & Khuyến nghị:** Đề xuất kiểm tra công nợ đối với các đơn hàng trên 100 triệu VNĐ, đồng thời kiểm tra tồn kho tại các kho vệ tinh đối với sản phẩm máy chủ cấu hình cao trước khi chốt cam kết giao hàng.")
        
        return insights


# Re-export Dynamic Business Report Generator & Microsoft Word (.docx) Exporter
from business_report import DynamicBusinessReportGenerator, export_report_to_word

