"""
business_report.py - Dynamic Business Report Architecture & Microsoft Word (.docx) Exporter
Implements the 6-part standardized Dynamic Business Report for Minh An Company:
  Phần 1: Tóm tắt điều hành (Executive Summary)
  Phần 2: Dashboard KPI (Kỳ gần nhất vs Kỳ liền trước)
  Phần 3: Phân tích chuyên đề (Theo từng cột số học)
  Phần 4: Kết luận (Tự động sinh từ dữ liệu thực tế)
  Phần 5: Đề xuất hành động (Kèm mức độ ưu tiên & chỉ số đo lường)
  Phần 6: Chi tiết Bộ dữ liệu & Thống kê kỹ thuật
"""

import re
import io
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls


def clean_num_series(series: pd.Series) -> pd.Series:
    """Chuyển đổi một Series sang kiểu float an toàn."""
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


class DynamicBusinessReportGenerator:
    """Tự động phân tích động mọi bộ dữ liệu nạp vào theo chuẩn cấu trúc 6 phần."""

    @classmethod
    def generate_report_data(
        cls, 
        df: pd.DataFrame, 
        file_name: str = "Du_Lieu_Minh_An", 
        audit_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Trích xuất và tổng hợp cấu trúc báo cáo 6 phần hoàn toàn động từ DataFrame."""
        if df is None or df.empty:
            return cls._empty_report_data(file_name)

        work_df = df.copy()
        total_rows = len(work_df)
        total_cols = len(work_df.columns)

        # Xác định các cột số học
        num_cols = work_df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Nếu chưa nhận diện cột số do lưu dạng text tiền tệ, tự động dò quét
        if not num_cols:
            for c in work_df.columns:
                cleaned_s = clean_num_series(work_df[c])
                if cleaned_s.abs().sum() > 0:
                    work_df[c] = cleaned_s
                    num_cols.append(c)

        # --------------------------------------------------------------------------------------------
        # PHẦN 1: TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)
        # --------------------------------------------------------------------------------------------
        quant_summary = []
        for nc in num_cols:
            s = work_df[nc].dropna()
            non_null = int(s.count())
            coverage_pct = round((non_null / total_rows * 100), 1) if total_rows > 0 else 0.0
            quant_summary.append({
                "column_name": str(nc),
                "sum": float(s.sum()),
                "mean": float(s.mean()) if non_null > 0 else 0.0,
                "coverage_count": non_null,
                "coverage_pct": coverage_pct,
                "coverage_text": f"{non_null}/{total_rows} dòng ({coverage_pct:.1f}%)"
            })

        # Bối cảnh dữ liệu
        col_names_lower = " ".join([str(c).lower() for c in work_df.columns])
        if any(k in col_names_lower for k in ["gia", "price", "revenue", "doanh_thu", "khach", "customer"]):
            data_context = "Giao dịch kinh doanh B2B, đơn đặt hàng & thanh toán thiết bị công nghệ"
        elif any(k in col_names_lower for k in ["ton_kho", "stock", "sku", "hang_hoa"]):
            data_context = "Danh mục thiết bị công nghệ, định mức bảng giá niêm yết & tồn kho khả dụng"
        elif any(k in col_names_lower for k in ["nvkd", "staff", "nhan_vien"]):
            data_context = "Phân bổ nhân sự kinh doanh và hiệu suất xử lý yêu cầu khách hàng"
        else:
            data_context = "Dữ liệu vận hành & quản trị tổng hợp doanh nghiệp"

        # --------------------------------------------------------------------------------------------
        # PHẦN 2: DASHBOARD KPI (SO SÁNH KỲ GẦN NHẤT VS KỲ LIỀN TRƯỚC)
        # --------------------------------------------------------------------------------------------
        # Tự động chia 2 kỳ: Kỳ gần nhất vs Kỳ liền trước
        date_candidates = [c for c in work_df.columns if any(k in str(c).lower() for k in ["date", "ngay", "time", "created"])]
        has_time_dim = False
        
        if date_candidates:
            try:
                date_col = date_candidates[0]
                work_df["_dt_parsed"] = pd.to_datetime(work_df[date_col], errors="coerce")
                if work_df["_dt_parsed"].notna().sum() >= 2:
                    work_df = work_df.sort_values(by="_dt_parsed")
                    has_time_dim = True
            except Exception:
                has_time_dim = False

        half_idx = max(1, total_rows // 2)
        curr_period_df = work_df.iloc[half_idx:] if total_rows > 1 else work_df
        prev_period_df = work_df.iloc[:half_idx] if total_rows > 1 else work_df

        # Tìm các chỉ số tiêu chuẩn
        def find_col_by_keywords(keywords: List[str]) -> Optional[str]:
            for kw in keywords:
                for c in work_df.columns:
                    if kw in str(c).lower():
                        return c
            return None

        rev_col = find_col_by_keywords(["doanh_thu", "revenue", "total_price", "finaltotal", "thanh_tien", "gia_tri", "tong_tien"])
        qty_col = find_col_by_keywords(["so_luong", "quantity", "qty", "sl"])
        profit_col = find_col_by_keywords(["loi_nhuan", "profit", "margin", "lai"])
        cost_col = find_col_by_keywords(["chi_phi", "cost", "cogs", "gia_von"])

        kpi_rows = []

        # 1. Doanh thu / Giá trị chính
        if rev_col and rev_col in num_cols:
            c_val = float(clean_num_series(curr_period_df[rev_col]).sum())
            p_val = float(clean_num_series(prev_period_df[rev_col]).sum())
            chg = ((c_val - p_val) / p_val * 100) if p_val > 0 else (100.0 if c_val > 0 else 0.0)
            kpi_rows.append({
                "metric": f"Tổng Giá trị / Doanh thu ({rev_col})",
                "current": f"{c_val:,.0f} đ",
                "previous": f"{p_val:,.0f} đ",
                "change": f"{chg:+.1f}%",
                "is_present": True
            })
        else:
            kpi_rows.append({
                "metric": "Tổng Doanh thu / Giá trị giao dịch",
                "current": "—",
                "previous": "—",
                "change": "—",
                "is_present": False
            })

        # 2. Số lượng giao dịch / Bản ghi
        c_cnt = len(curr_period_df)
        p_cnt = len(prev_period_df)
        cnt_chg = ((c_cnt - p_cnt) / p_cnt * 100) if p_cnt > 0 else 0.0
        kpi_rows.append({
            "metric": "Số lượng Giao dịch / Đơn hàng",
            "current": f"{c_cnt} dòng",
            "previous": f"{p_cnt} dòng",
            "change": f"{cnt_chg:+.1f}%",
            "is_present": True
        })

        # 3. Sản lượng thiết bị (nếu có cột số lượng)
        if qty_col and qty_col in num_cols:
            c_q = float(clean_num_series(curr_period_df[qty_col]).sum())
            p_q = float(clean_num_series(prev_period_df[qty_col]).sum())
            q_chg = ((c_q - p_q) / p_q * 100) if p_q > 0 else (100.0 if c_q > 0 else 0.0)
            kpi_rows.append({
                "metric": f"Tổng Sản lượng Thiết bị ({qty_col})",
                "current": f"{c_q:,.0f}",
                "previous": f"{p_q:,.0f}",
                "change": f"{q_chg:+.1f}%",
                "is_present": True
            })
        else:
            kpi_rows.append({
                "metric": "Tổng Sản lượng Thiết bị",
                "current": "—",
                "previous": "—",
                "change": "—",
                "is_present": False
            })

        # 4. Lợi nhuận (Nếu không có cột trong file -> Tự động hiển thị "—")
        if profit_col and profit_col in num_cols:
            c_pf = float(clean_num_series(curr_period_df[profit_col]).sum())
            p_pf = float(clean_num_series(prev_period_df[profit_col]).sum())
            pf_chg = ((c_pf - p_pf) / p_pf * 100) if p_pf > 0 else (100.0 if c_pf > 0 else 0.0)
            kpi_rows.append({
                "metric": f"Lợi nhuận ({profit_col})",
                "current": f"{c_pf:,.0f} đ",
                "previous": f"{p_pf:,.0f} đ",
                "change": f"{pf_chg:+.1f}%",
                "is_present": True
            })
        else:
            kpi_rows.append({
                "metric": "Lợi nhuận ròng",
                "current": "—",
                "previous": "—",
                "change": "—",
                "is_present": False
            })

        # 5. Chi phí vận hành (Nếu không có trong file -> Tự động hiển thị "—")
        if cost_col and cost_col in num_cols:
            c_cs = float(clean_num_series(curr_period_df[cost_col]).sum())
            p_cs = float(clean_num_series(prev_period_df[cost_col]).sum())
            cs_chg = ((c_cs - p_cs) / p_cs * 100) if p_cs > 0 else (100.0 if c_cs > 0 else 0.0)
            kpi_rows.append({
                "metric": f"Chi phí ({cost_col})",
                "current": f"{c_cs:,.0f} đ",
                "previous": f"{p_cs:,.0f} đ",
                "change": f"{cs_chg:+.1f}%",
                "is_present": True
            })
        else:
            kpi_rows.append({
                "metric": "Chi phí vận hành",
                "current": "—",
                "previous": "—",
                "change": "—",
                "is_present": False
            })

        # --------------------------------------------------------------------------------------------
        # PHẦN 3: PHÂN TÍCH CHUYÊN ĐỀ (CHI TIẾT TỪNG CỘT SỐ HỌC)
        # --------------------------------------------------------------------------------------------
        thematic_analysis = []
        for nc in num_cols:
            clean_s = clean_num_series(work_df[nc]).dropna()
            if len(clean_s) == 0:
                continue
            cnt = int(clean_s.count())
            tot = float(clean_s.sum())
            avg = float(clean_s.mean())
            med = float(clean_s.median())
            std_v = float(clean_s.std()) if cnt > 1 else 0.0
            min_v = float(clean_s.min())
            max_v = float(clean_s.max())
            q25 = float(clean_s.quantile(0.25))
            q75 = float(clean_s.quantile(0.75))
            iqr = float(q75 - q25)
            cv = round((std_v / avg), 2) if avg != 0 else 0.0

            # Nhận xét phân phối
            if cv > 0.8:
                dist_note = f"Độ biến thiên cao (CV = {cv}), dữ liệu có sự chênh lệch lớn giữa các bản ghi nhỏ và lớn."
            elif cv > 0.3:
                dist_note = f"Độ biến thiên vừa phải (CV = {cv}), phản ánh cấu trúc danh mục đa dạng."
            else:
                dist_note = f"Độ phân tán thấp (CV = {cv}), các giá trị phân bổ đồng đều xung quanh mức trung bình."

            thematic_analysis.append({
                "column": str(nc),
                "count": cnt,
                "sum": tot,
                "mean": avg,
                "median": med,
                "std": std_v,
                "min": min_v,
                "max": max_v,
                "q25": q25,
                "q75": q75,
                "iqr": iqr,
                "cv": cv,
                "dist_note": dist_note
            })

        # --------------------------------------------------------------------------------------------
        # PHẦN 4: KẾT LUẬN (SINH TỪ DỮ LIỆU THỰC TẾ)
        # --------------------------------------------------------------------------------------------
        conclusions = []
        # Nhận định về biến động 2 kỳ
        if rev_col and rev_col in num_cols:
            c_val = float(clean_num_series(curr_period_df[rev_col]).sum())
            p_val = float(clean_num_series(prev_period_df[rev_col]).sum())
            diff = c_val - p_val
            pct = ((diff) / p_val * 100) if p_val > 0 else 0.0
            trend = "tăng trưởng" if diff >= 0 else "suy giảm"
            conclusions.append(
                f"Chỉ số chính '{rev_col}' ghi nhận xu hướng {trend} {abs(pct):.1f}% giữa hai kỳ quan sát (từ {p_val:,.0f} đ lên {c_val:,.0f} đ, chênh lệch {diff:+,.0f} đ)."
            )
        else:
            conclusions.append(
                f"Khối lượng giao dịch ghi nhận ổn định qua 2 kỳ với tổng số {total_rows} bản ghi được xử lý."
            )

        # Nhận định về phân nhóm đứng đầu
        cat_col = find_col_by_keywords(["product", "san_pham", "category", "danh_muc", "nhom", "khach", "customer"])
        if not cat_col:
            cat_candidates = work_df.select_dtypes(exclude=[np.number]).columns.tolist()
            if cat_candidates:
                cat_col = cat_candidates[0]

        top_leader_name = "N/A"
        top_leader_val = 0.0
        top_leader_share = 0.0

        if cat_col and cat_col in work_df.columns:
            metric_target = rev_col if (rev_col and rev_col in num_cols) else (num_cols[0] if num_cols else None)
            if metric_target:
                grouped_agg = work_df.groupby(cat_col)[metric_target].sum().sort_values(ascending=False).reset_index()
                if not grouped_agg.empty:
                    top_leader_name = str(grouped_agg.iloc[0][cat_col])
                    top_leader_val = float(grouped_agg.iloc[0][metric_target])
                    tot_m = float(grouped_agg[metric_target].sum())
                    top_leader_share = round((top_leader_val / tot_m * 100), 1) if tot_m > 0 else 0.0
                    conclusions.append(
                        f"Phân loại '{cat_col}' có mức tập trung cao nhất tại nhóm '{top_leader_name}' đạt {top_leader_val:,.0f} (chiếm {top_leader_share:.1f}% tổng quy mô)."
                    )

        # Nhận định về độ sạch dữ liệu
        empty_cells = int(work_df.isna().sum().sum())
        conclusions.append(
            f"Độ hoàn chỉnh dữ liệu đạt {((1 - empty_cells / (total_rows * total_cols)) * 100):.1f}% với {total_rows} dòng và {total_cols} cột sẵn sàng phục vụ ra quyết định."
        )

        # --------------------------------------------------------------------------------------------
        # PHẦN 5: ĐỀ XUẤT HÀNH ĐỘNG (KÈM ƯU TIÊN VÀ CHỈ SỐ ĐO LƯỜNG)
        # --------------------------------------------------------------------------------------------
        recommendations = [
            {
                "stt": 1,
                "action": f"Tập trung nguồn lực và chính sách ưu đãi vào nhóm chủ lực '{top_leader_name}' để duy trì đà tăng trưởng doanh số.",
                "priority": "Cao (High)",
                "metric": f"Duy trì tỷ trọng đóng góp >= {top_leader_share:.0f}% và biên an toàn kho",
                "timeline": "30 ngày tới"
            },
            {
                "stt": 2,
                "action": "Thiết lập cơ chế kiểm soát giá sàn niêm yết hiện hành và thẩm định SLA tồn kho trước khi gửi đề xuất thương mại.",
                "priority": "Cao (High)",
                "metric": "100% đề xuất khớp bảng giá 2026 và 0% cam kết vượt SLA khả dụng",
                "timeline": "Áp dụng ngay"
            },
            {
                "stt": 3,
                "action": "Tự động hóa đối soát trường thông tin ngân sách và gán rõ NVKD + Cán bộ theo dõi cho từng cơ hội kinh doanh.",
                "priority": "Trung bình (Medium)",
                "metric": "0 hồ sơ bị thả nổi và thời gian phản hồi khách hàng < 4 giờ",
                "timeline": "Trong quý này"
            }
        ]

        # --------------------------------------------------------------------------------------------
        # PHẦN 6: CHI TIẾT BỘ DỮ LIỆU & THỐNG KÊ KỸ THUẬT
        # --------------------------------------------------------------------------------------------
        # 6.1 Thông tin làm sạch dữ liệu
        audit = audit_info or {}
        cleaning_info = {
            "initial_rows": total_rows,
            "cleaned_rows": total_rows,
            "cleaned_cols": total_cols,
            "empty_cells_count": empty_cells,
            "duplicate_rows_removed": audit.get("duplicate_count", 0),
            "outliers_detected": len(audit.get("outliers", {})),
            "quality_score": audit.get("quality_score", 100)
        }

        # 6.2 Nhận xét thống kê tự động
        primary_metric_name = rev_col or (num_cols[0] if num_cols else "Giá trị")
        primary_series = clean_num_series(work_df[primary_metric_name]) if primary_metric_name in work_df.columns else pd.Series([0])
        stat_observations = {
            "primary_metric": primary_metric_name,
            "min_val": float(primary_series.min()) if not primary_series.empty else 0.0,
            "max_val": float(primary_series.max()) if not primary_series.empty else 0.0,
            "mean_val": float(primary_series.mean()) if not primary_series.empty else 0.0,
            "top_group": top_leader_name,
            "top_group_share": top_leader_share
        }

        # 6.3 Bảng Tổng hợp theo nhóm (Group-by: Nhóm | Giá trị | Số dòng được tính | Tỷ trọng %)
        groupby_rows = []
        if cat_col and cat_col in work_df.columns:
            m_col = primary_metric_name if primary_metric_name in work_df.columns else work_df.columns[0]
            work_df["_m_clean"] = clean_num_series(work_df[m_col]) if m_col in num_cols else 1.0
            grp = work_df.groupby(cat_col).agg(
                TotalVal=('_m_clean', 'sum'),
                RowCount=('_m_clean', 'count')
            ).reset_index().sort_values(by="TotalVal", ascending=False)
            
            tot_g = grp["TotalVal"].sum()
            for _, r in grp.head(10).iterrows():
                val_g = float(r["TotalVal"])
                sh_g = round((val_g / tot_g * 100), 1) if tot_g > 0 else 0.0
                groupby_rows.append({
                    "group_name": str(r[cat_col]),
                    "value": f"{val_g:,.0f} đ" if m_col in num_cols else f"{val_g:,.0f}",
                    "row_count": int(r["RowCount"]),
                    "share_pct": f"{sh_g:.1f}%"
                })

        # 6.4 Bảng Thống kê theo từng cột (Cột | Ô trống | Giá trị khác nhau | Trung bình | Nhỏ nhất | Lớn nhất)
        col_stats_rows = []
        for c in work_df.columns:
            if c.startswith("_"):
                continue
            s = work_df[c]
            missing_count = int(s.isna().sum())
            unique_count = int(s.nunique(dropna=True))
            if c in num_cols:
                s_num = clean_num_series(s).dropna()
                mean_str = f"{s_num.mean():,.1f}" if len(s_num) > 0 else "—"
                min_str = f"{s_num.min():,.0f}" if len(s_num) > 0 else "—"
                max_str = f"{s_num.max():,.0f}" if len(s_num) > 0 else "—"
            else:
                mean_str = "—"
                min_str = "—"
                max_str = "—"
                
            col_stats_rows.append({
                "column": str(c),
                "missing": missing_count,
                "unique": unique_count,
                "mean": mean_str,
                "min": min_str,
                "max": max_str
            })

        return {
            "section_1": {
                "dataset_name": file_name,
                "total_rows": total_rows,
                "total_cols": total_cols,
                "context_description": data_context,
                "quantitative_summary": quant_summary
            },
            "section_2": {
                "kpi_table": kpi_rows
            },
            "section_3": {
                "thematic_analysis": thematic_analysis
            },
            "section_4": {
                "conclusions": conclusions
            },
            "section_5": {
                "recommendations": recommendations
            },
            "section_6": {
                "cleaning_info": cleaning_info,
                "stat_observations": stat_observations,
                "groupby_table": groupby_rows,
                "col_stats_table": col_stats_rows
            }
        }

    @classmethod
    def _empty_report_data(cls, file_name: str) -> Dict[str, Any]:
        return {
            "section_1": {"dataset_name": file_name, "total_rows": 0, "total_cols": 0, "context_description": "Trống", "quantitative_summary": []},
            "section_2": {"kpi_table": []},
            "section_3": {"thematic_analysis": []},
            "section_4": {"conclusions": ["Không có dữ liệu"]},
            "section_5": {"recommendations": []},
            "section_6": {"cleaning_info": {}, "stat_observations": {}, "groupby_table": [], "col_stats_table": []}
        }


# ====================================================================================================
# BỘ XUẤT BÁO CÁO MICROSOFT WORD (.DOCX) ĐỒNG BỘ 100% CẤU TRÚC 6 PHẦN
# ====================================================================================================

def _set_cell_background(cell, fill_hex: str):
    """Đặt màu nền cho ô trong bảng Word."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex.replace("#", "")}"/>')
    tcPr.append(shd)

def _set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Đặt lề trong cho ô bảng Word."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)


def export_report_to_word(report_data: Dict[str, Any]) -> io.BytesIO:
    """
    Sinh tài liệu Microsoft Word (.docx) chuyên nghiệp, chuẩn hóa phân cấp Heading 1, 2, 3
    và cấu trúc bảng biểu đúng 6 phần của Báo cáo Kinh doanh Động.
    """
    doc = docx.Document()
    
    # Cấu hình lề trang 1 inch
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # ------------------------------------------------------------------------------------------------
    # TIÊU ĐỀ CHÍNH & THÔNG TIN BAN ĐẦU
    # ------------------------------------------------------------------------------------------------
    p_title = doc.add_paragraph()
    run_title = p_title.add_run("BÁO CÁO KINH DOANH & PHÂN TÍCH DỮ LIỆU ĐỘNG")
    run_title.bold = True
    run_title.font.size = Pt(20)
    run_title.font.color.rgb = RGBColor(30, 58, 138)  # Navy Blue #1E3A8A
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_sub = doc.add_paragraph()
    run_sub = p_sub.add_run(f"Công ty Cổ phần Công nghệ Minh An • Xuất ngày: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    run_sub.font.size = Pt(10.5)
    run_sub.font.color.rgb = RGBColor(100, 116, 139)
    run_sub.italic = True
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()

    # ------------------------------------------------------------------------------------------------
    # PHẦN 1: TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)
    # ------------------------------------------------------------------------------------------------
    s1 = report_data.get("section_1", {})
    h1 = doc.add_heading("1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)", level=1)
    h1.style.font.color.rgb = RGBColor(30, 58, 138)

    p1 = doc.add_paragraph()
    p1.add_run(f"• Tên bộ dữ liệu phân tích: ").bold = True
    p1.add_run(f"{s1.get('dataset_name')}\n")
    p1.add_run(f"• Quy mô tập dữ liệu: ").bold = True
    p1.add_run(f"{s1.get('total_rows')} dòng dữ liệu, {s1.get('total_cols')} trường thông tin.\n")
    p1.add_run(f"• Bối cảnh & Loại hình dữ liệu: ").bold = True
    p1.add_run(f"{s1.get('context_description')}\n")

    p1_metrics = doc.add_paragraph()
    p1_metrics.add_run("• Tổng giá trị và Độ phủ dữ liệu định lượng chính:\n").bold = True
    for qs in s1.get("quantitative_summary", []):
        p1_metrics.add_run(f"   - Chỉ số '{qs['column_name']}': Tổng cộng = {qs['sum']:,.0f} | Trung bình = {qs['mean']:,.1f} | Độ phủ dữ liệu: {qs['coverage_text']}\n")

    # ------------------------------------------------------------------------------------------------
    # PHẦN 2: DASHBOARD KPI (SO SÁNH KỲ GẦN NHẤT VS KỲ LIỀN TRƯỚC)
    # ------------------------------------------------------------------------------------------------
    s2 = report_data.get("section_2", {})
    h2 = doc.add_heading("2. DASHBOARD KPI (SO SÁNH KỲ GẦN NHẤT VS KỲ LIỀN TRƯỚC)", level=1)
    h2.style.font.color.rgb = RGBColor(30, 58, 138)
    
    doc.add_paragraph("Bảng đối chiếu các chỉ số kinh doanh giữa kỳ gần nhất và kỳ liền trước (các chỉ số không có trong bộ dữ liệu được thể hiện bằng dấu '—' nhằm đảm bảo tính trung thực dữ liệu):")

    kpi_table_data = s2.get("kpi_table", [])
    if kpi_table_data:
        t2 = doc.add_table(rows=1, cols=4)
        t2.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr_cells = t2.rows[0].cells
        hdr_titles = ["Chỉ số", "Giá trị (Kỳ gần nhất)", "Kỳ trước", "Thay đổi %"]
        for idx, title in enumerate(hdr_titles):
            hdr_cells[idx].text = title
            hdr_cells[idx].paragraphs[0].runs[0].bold = True
            hdr_cells[idx].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            _set_cell_background(hdr_cells[idx], "4F46E5")
            _set_cell_margins(hdr_cells[idx], 120, 120, 160, 160)

        for r_idx, row in enumerate(kpi_table_data):
            row_cells = t2.add_row().cells
            row_cells[0].text = str(row["metric"])
            row_cells[1].text = str(row["current"])
            row_cells[2].text = str(row["previous"])
            row_cells[3].text = str(row["change"])
            
            fill = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
            for c in row_cells:
                _set_cell_background(c, fill)
                _set_cell_margins(c, 100, 100, 140, 140)
    doc.add_paragraph()

    # ------------------------------------------------------------------------------------------------
    # PHẦN 3: PHÂN TÍCH CHUYÊN ĐỀ THEO CHỈ SỐ ĐỊNH LƯỢNG
    # ------------------------------------------------------------------------------------------------
    s3 = report_data.get("section_3", {})
    h3 = doc.add_heading("3. PHÂN TÍCH CHUYÊN ĐỀ THEO TỪNG CHỈ SỐ ĐỊNH LƯỢNG", level=1)
    h3.style.font.color.rgb = RGBColor(30, 58, 138)

    thematic = s3.get("thematic_analysis", [])
    if thematic:
        for th in thematic:
            h_sub = doc.add_heading(f"3.{thematic.index(th) + 1}. Phân tích chuyên sâu chỉ số '{th['column']}'", level=2)
            h_sub.style.font.color.rgb = RGBColor(67, 56, 202)
            
            p_th = doc.add_paragraph()
            p_th.add_run(f"• Thống kê mẫu số liệu: ").bold = True
            p_th.add_run(f"Số lượng = {th['count']:,} dòng | Tổng cộng = {th['sum']:,.0f} | Trung bình = {th['mean']:,.1f} | Trung vị = {th['median']:,.1f}\n")
            p_th.add_run(f"• Độ phân tán & Biên độ: ").bold = True
            p_th.add_run(f"Độ lệch chuẩn = {th['std']:,.1f} | Giá trị nhỏ nhất = {th['min']:,.0f} | Giá trị lớn nhất = {th['max']:,.0f} | Khoảng tứ phân vị (IQR) = {th['iqr']:,.1f}\n")
            p_th.add_run(f"• Nhận xét phân phối: ").bold = True
            p_th.add_run(f"{th['dist_note']}\n")
    else:
        doc.add_paragraph("Tập dữ liệu không chứa cột số học định lượng để phân tích chuyên đề sâu.")
    doc.add_paragraph()

    # ------------------------------------------------------------------------------------------------
    # PHẦN 4: KẾT LUẬN TỪ DỮ LIỆU THỰC TẾ
    # ------------------------------------------------------------------------------------------------
    s4 = report_data.get("section_4", {})
    h4 = doc.add_heading("4. KẾT LUẬN TỪ DỮ LIỆU THỰC TẾ", level=1)
    h4.style.font.color.rgb = RGBColor(30, 58, 138)

    for c_item in s4.get("conclusions", []):
        p_c = doc.add_paragraph(style='List Bullet')
        p_c.add_run(str(c_item))
    doc.add_paragraph()

    # ------------------------------------------------------------------------------------------------
    # PHẦN 5: ĐỀ XUẤT HÀNH ĐỘNG & QUẢN TRỊ
    # ------------------------------------------------------------------------------------------------
    s5 = report_data.get("section_5", {})
    h5 = doc.add_heading("5. ĐỀ XUẤT HÀNH ĐỘNG & CHỈ SỐ ĐO LƯỜNG QUẢN TRỊ", level=1)
    h5.style.font.color.rgb = RGBColor(30, 58, 138)

    recs = s5.get("recommendations", [])
    if recs:
        t5 = doc.add_table(rows=1, cols=4)
        t5.alignment = WD_TABLE_ALIGNMENT.CENTER
        h5_cells = t5.rows[0].cells
        h5_titles = ["STT", "Khuyến nghị quản trị", "Mức độ ưu tiên", "Chỉ số đo lường (KPI)"]
        for idx, title in enumerate(h5_titles):
            h5_cells[idx].text = title
            h5_cells[idx].paragraphs[0].runs[0].bold = True
            h5_cells[idx].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            _set_cell_background(h5_cells[idx], "10B981")  # Emerald #10B981
            _set_cell_margins(h5_cells[idx], 120, 120, 140, 140)

        for r_idx, r in enumerate(recs):
            row_cells = t5.add_row().cells
            row_cells[0].text = str(r["stt"])
            row_cells[1].text = str(r["action"])
            row_cells[2].text = str(r["priority"])
            row_cells[3].text = str(r["metric"]) + f" (Thời hạn: {r.get('timeline', 'Q1')})"
            
            fill = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
            for c in row_cells:
                _set_cell_background(c, fill)
                _set_cell_margins(c, 100, 100, 140, 140)
    doc.add_paragraph()

    # ------------------------------------------------------------------------------------------------
    # PHẦN 6: CHI TIẾT BỘ DỮ LIỆU & THỐNG KÊ KỸ THUẬT
    # ------------------------------------------------------------------------------------------------
    s6 = report_data.get("section_6", {})
    h6 = doc.add_heading("6. CHI TIẾT BỘ DỮ LIỆU & THỐNG KÊ KỸ THUẬT", level=1)
    h6.style.font.color.rgb = RGBColor(30, 58, 138)

    # 6.1 Thông tin làm sạch
    clean_info = s6.get("cleaning_info", {})
    h6_1 = doc.add_heading("6.1. Thông tin làm sạch & Kiểm tra chất lượng dữ liệu", level=2)
    h6_1.style.font.color.rgb = RGBColor(67, 56, 202)
    p6_1 = doc.add_paragraph()
    p6_1.add_run(f"• Số dòng dữ liệu sau làm sạch: ").bold = True
    p6_1.add_run(f"{clean_info.get('cleaned_rows', 0)} dòng • ")
    p6_1.add_run(f"Số cột: ").bold = True
    p6_1.add_run(f"{clean_info.get('cleaned_cols', 0)} cột\n")
    p6_1.add_run(f"• Số ô trống / thiếu dữ liệu đã kiểm tra: ").bold = True
    p6_1.add_run(f"{clean_info.get('empty_cells_count', 0)} ô\n")
    p6_1.add_run(f"• Số dòng trùng lặp đã loại bỏ: ").bold = True
    p6_1.add_run(f"{clean_info.get('duplicate_rows_removed', 0)} dòng\n")
    p6_1.add_run(f"• Điểm chất lượng dữ liệu (Data Quality Score): ").bold = True
    p6_1.add_run(f"{clean_info.get('quality_score', 100)} / 100 điểm\n")

    # 6.2 Nhận xét thống kê tự động
    stat_obs = s6.get("stat_observations", {})
    h6_2 = doc.add_heading("6.2. Nhận xét thống kê tự động", level=2)
    h6_2.style.font.color.rgb = RGBColor(67, 56, 202)
    p6_2 = doc.add_paragraph()
    p6_2.add_run(f"• Chỉ số trọng tâm khảo sát: ").bold = True
    p6_2.add_run(f"'{stat_obs.get('primary_metric')}'\n")
    p6_2.add_run(f"• Giá trị nhỏ nhất: ").bold = True
    p6_2.add_run(f"{stat_obs.get('min_val', 0):,.0f} | ")
    p6_2.add_run(f"Giá trị lớn nhất: ").bold = True
    p6_2.add_run(f"{stat_obs.get('max_val', 0):,.0f} | ")
    p6_2.add_run(f"Giá trị trung bình: ").bold = True
    p6_2.add_run(f"{stat_obs.get('mean_val', 0):,.1f}\n")
    p6_2.add_run(f"• Nhóm chiếm ưu thế dẫn đầu: ").bold = True
    p6_2.add_run(f"'{stat_obs.get('top_group')}' chiếm {stat_obs.get('top_group_share', 0):.1f}% tổng giá trị.\n")

    # 6.3 Bảng Tổng hợp theo nhóm
    h6_3 = doc.add_heading("6.3. Bảng Tổng hợp theo nhóm (Group-by)", level=2)
    h6_3.style.font.color.rgb = RGBColor(67, 56, 202)
    grp_rows = s6.get("groupby_table", [])
    if grp_rows:
        t6_3 = doc.add_table(rows=1, cols=4)
        t6_3.alignment = WD_TABLE_ALIGNMENT.CENTER
        h6_3_cells = t6_3.rows[0].cells
        h6_3_titles = ["Nhóm", "Giá trị", "Số dòng được tính", "Tỷ trọng (%)"]
        for idx, title in enumerate(h6_3_titles):
            h6_3_cells[idx].text = title
            h6_3_cells[idx].paragraphs[0].runs[0].bold = True
            h6_3_cells[idx].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            _set_cell_background(h6_3_cells[idx], "0284C7")  # Cyan/Blue #0284C7
            _set_cell_margins(h6_3_cells[idx], 100, 100, 140, 140)

        for r_idx, r in enumerate(grp_rows):
            row_cells = t6_3.add_row().cells
            row_cells[0].text = str(r["group_name"])
            row_cells[1].text = str(r["value"])
            row_cells[2].text = str(r["row_count"])
            row_cells[3].text = str(r["share_pct"])
            fill = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
            for c in row_cells:
                _set_cell_background(c, fill)
                _set_cell_margins(c, 80, 80, 120, 120)
    doc.add_paragraph()

    # 6.4 Bảng Thống kê theo từng cột
    h6_4 = doc.add_heading("6.4. Bảng Thống kê chi tiết theo từng cột dữ liệu", level=2)
    h6_4.style.font.color.rgb = RGBColor(67, 56, 202)
    col_rows = s6.get("col_stats_table", [])
    if col_rows:
        t6_4 = doc.add_table(rows=1, cols=6)
        t6_4.alignment = WD_TABLE_ALIGNMENT.CENTER
        h6_4_cells = t6_4.rows[0].cells
        h6_4_titles = ["Cột", "Ô trống", "Giá trị khác nhau", "Trung bình", "Nhỏ nhất", "Lớn nhất"]
        for idx, title in enumerate(h6_4_titles):
            h6_4_cells[idx].text = title
            h6_4_cells[idx].paragraphs[0].runs[0].bold = True
            h6_4_cells[idx].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            _set_cell_background(h6_4_cells[idx], "475569")  # Slate #475569
            _set_cell_margins(h6_4_cells[idx], 100, 100, 120, 120)

        for r_idx, r in enumerate(col_rows):
            row_cells = t6_4.add_row().cells
            row_cells[0].text = str(r["column"])
            row_cells[1].text = str(r["missing"])
            row_cells[2].text = str(r["unique"])
            row_cells[3].text = str(r["mean"])
            row_cells[4].text = str(r["min"])
            row_cells[5].text = str(r["max"])
            fill = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
            for c in row_cells:
                _set_cell_background(c, fill)
                _set_cell_margins(c, 80, 80, 120, 120)

    # Xuất ra bộ đệm byte
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream
