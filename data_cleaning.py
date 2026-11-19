"""
Minh An Data Quality, Standardization & Smart Schema Mapping Engine (Edition 2026)
Provides automated data cleaning, missing value handling, Vietnamese currency parsing,
outlier detection (IQR method), and intelligent column mapping with confidence scores.
"""

import re
import difflib
import unicodedata
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil import parser as date_parser

from config import CANONICAL_COLUMNS
from file_reader import UniversalFileReader


def strip_accents(text: str) -> str:
    """Chuyển đổi chuỗi tiếng Việt có dấu thành không dấu chuẩn xác để so khớp synonym."""
    text = str(text).replace('Đ', 'D').replace('đ', 'd')
    nfkd = unicodedata.normalize('NFKD', text)
    cleaned = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9_]', '', cleaned.lower().replace(' ', '_'))


class DataQualityCleaner:
    """Enterprise cleaner performing audit reports, type conversion, and outlier mitigation."""

    @classmethod
    def audit_dataframe(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Generates a comprehensive Data Quality Report."""
        total_rows = len(df)
        total_cols = len(df.columns)
        
        # Missing values analysis
        missing_stats = []
        for col in df.columns:
            null_count = int(df[col].isna().sum())
            null_pct = round((null_count / total_rows * 100), 1) if total_rows > 0 else 0
            missing_stats.append({
                "column": str(col),
                "null_count": null_count,
                "null_pct": null_pct,
                "dtype": str(df[col].dtype)
            })
            
        # Duplicate rows
        duplicate_count = int(df.duplicated().sum())
        duplicate_pct = round((duplicate_count / total_rows * 100), 1) if total_rows > 0 else 0
        
        # Outlier detection using IQR on numeric columns
        outliers_detected = {}
        for col in df.columns:
            # Try to test if column is numeric or can be parsed
            numeric_series = pd.to_numeric(df[col].apply(UniversalFileReader.parse_vietnamese_number), errors='coerce').dropna()
            if len(numeric_series) >= 5:
                q25 = numeric_series.quantile(0.25)
                q75 = numeric_series.quantile(0.75)
                iqr = q75 - q25
                lower_bound = q25 - 1.5 * iqr
                upper_bound = q75 + 1.5 * iqr
                outlier_rows = numeric_series[(numeric_series < lower_bound) | (numeric_series > upper_bound)]
                if len(outlier_rows) > 0:
                    outliers_detected[str(col)] = {
                        "count": len(outlier_rows),
                        "lower_bound": round(lower_bound, 2),
                        "upper_bound": round(upper_bound, 2),
                        "min_val": round(float(outlier_rows.min()), 2),
                        "max_val": round(float(outlier_rows.max()), 2)
                    }

        # Calculate overall quality score (0 to 100)
        overall_null_pct = (df.isna().sum().sum() / (total_rows * total_cols) * 100) if (total_rows * total_cols) > 0 else 0
        quality_score = max(0, min(100, int(100 - (overall_null_pct * 0.7) - (duplicate_pct * 0.3))))
        
        return {
            "total_rows": total_rows,
            "total_cols": total_cols,
            "quality_score": quality_score,
            "missing_stats": missing_stats,
            "duplicate_count": duplicate_count,
            "duplicate_pct": duplicate_pct,
            "outliers": outliers_detected
        }

    @classmethod
    def clean_and_standardize(cls, df: pd.DataFrame, drop_duplicates: bool = True) -> pd.DataFrame:
        """Cleans whitespaces, converts Vietnamese numbers, and standardizes column formats."""
        cleaned_df = df.copy()
        
        # 1. Clean column names
        cleaned_df.columns = [re.sub(r'\s+', ' ', str(c).strip()) for c in cleaned_df.columns]
        
        # 2. Drop 100% empty rows and columns
        cleaned_df = cleaned_df.dropna(how='all').dropna(axis=1, how='all')
        
        # 3. Strip whitespace from string cells
        for col in cleaned_df.select_dtypes(include=['object']).columns:
            cleaned_df[col] = cleaned_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            
        # 4. Auto-parse Vietnamese numeric strings (currencies, quantities, percentages)
        for col in cleaned_df.select_dtypes(include=['object']).columns:
            col_lower = str(col).lower()
            if any(skip in col_lower for skip in ['phone', 'dien_thoai', 'sdt', 'tel', 'ma_', 'id', 'code', 'ten_', 'name', 'address', 'dia_chi', 'email']):
                continue
            series = cleaned_df[col].dropna()
            if len(series) > 0:
                is_num = series.astype(str).str.contains(r'^[0-9\.\,\s\%\-\+đ₫VNDvnd]+$', regex=True).all()
                is_not_phone = not series.astype(str).str.match(r'^0[0-9]{8,10}$').any()
                if is_num and is_not_phone:
                    try:
                        parsed = series.apply(UniversalFileReader.parse_vietnamese_number)
                        if not parsed.isna().all():
                            cleaned_df[col] = cleaned_df[col].apply(lambda v: UniversalFileReader.parse_vietnamese_number(v) if pd.notna(v) else v)
                    except Exception:
                        pass

        # 5. Handle duplicates
        if drop_duplicates and cleaned_df.duplicated().sum() > 0:
            cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)
            
        return cleaned_df

    @classmethod
    def suggest_schema_mapping(cls, df_columns: List[str], sample_df: Optional[pd.DataFrame] = None) -> Dict[str, Dict[str, Any]]:
        """
        Intelligently maps file columns to system canonical fields.
        Returns a dict of canonical_field -> {"mapped_column": ..., "confidence": ...}
        """
        suggestions: Dict[str, Dict[str, Any]] = {}
        assigned_cols = set()
        
        # Prepare normalized column names with full Vietnamese unaccenting
        normalized_cols = {col: strip_accents(col) for col in df_columns}
        
        for canon_field, canon_meta in CANONICAL_COLUMNS.items():
            best_col = None
            best_score = 0.0
            synonyms = canon_meta["synonyms"]
            
            for orig_col, norm_col in normalized_cols.items():
                if orig_col in assigned_cols:
                    continue
                    
                # Exact synonym match
                if norm_col in synonyms:
                    best_col = orig_col
                    best_score = 100.0
                    break
                    
                # Partial / substring match
                for syn in synonyms:
                    if syn in norm_col or norm_col in syn:
                        score = 85.0
                        if score > best_score:
                            best_score = score
                            best_col = orig_col
                            
                # Fuzzy string similarity
                for syn in synonyms:
                    sim = difflib.SequenceMatcher(None, syn, norm_col).ratio() * 100.0
                    if sim > 75.0 and sim > best_score:
                        best_score = sim
                        best_col = orig_col
                        
            # Heuristic value checks if sample_df is provided and best_score is low
            if (best_score < 70.0 or best_col is None) and sample_df is not None:
                for orig_col in df_columns:
                    if orig_col in assigned_cols:
                        continue
                    series = sample_df[orig_col].dropna()
                    if len(series) == 0:
                        continue
                        
                    # Check for email format
                    if canon_field == "contact_email":
                        sample_emails = series.astype(str).str.contains(r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', regex=True)
                        if sample_emails.mean() > 0.6:
                            best_col = orig_col
                            best_score = 92.0
                            break
                            
                    # Check for phone numbers
                    elif canon_field == "contact_phone":
                        sample_phones = series.astype(str).str.contains(r'(?:\+84|0[35789])[0-9]{8}', regex=True)
                        if sample_phones.mean() > 0.6:
                            best_col = orig_col
                            best_score = 90.0
                            break
                            
                    # Check for large currency values (> 100,000)
                    elif canon_field in ["unit_price", "total_price"]:
                        parsed_nums = series.apply(UniversalFileReader.parse_vietnamese_number)
                        numeric_vals = pd.to_numeric(parsed_nums, errors='coerce').dropna()
                        if len(numeric_vals) > 0 and numeric_vals.mean() > 50000:
                            if canon_field == "total_price" and ("thanh_tien" in orig_col.lower() or "tong" in orig_col.lower()):
                                best_col = orig_col
                                best_score = 88.0
                                break
                            elif canon_field == "unit_price" and ("don_gia" in orig_col.lower() or "gia" in orig_col.lower()):
                                best_col = orig_col
                                best_score = 88.0
                                break
            
            if best_col and best_score >= 50.0:
                suggestions[canon_field] = {
                    "mapped_column": best_col,
                    "confidence": round(best_score, 1),
                    "needs_review": best_score < 70.0
                }
                assigned_cols.add(best_col)
            else:
                suggestions[canon_field] = {
                    "mapped_column": None,
                    "confidence": 0.0,
                    "needs_review": True
                }
                
        return suggestions

    @classmethod
    def apply_schema_mapping(cls, df: pd.DataFrame, mapping_dict: Dict[str, str]) -> pd.DataFrame:
        """
        Creates a standardized DataFrame preserving all original columns while adding/renaming canonical fields.
        Performs vectorized type conversions for extreme performance (handles 50,000+ rows instantly).
        """
        if df.empty:
            return df
            
        std_df = df.copy()
        for canon_key, orig_col in mapping_dict.items():
            if orig_col and orig_col in df.columns:
                if canon_key != orig_col:
                    std_df[canon_key] = std_df[orig_col]
                    
                # Vectorized type conversions
                if canon_key in ["quantity", "unit_price", "total_price"]:
                    # Xử lý số kiểu Việt Nam (dấu chấm hàng nghìn, phẩy thập phân)
                    cleaned_num = std_df[canon_key].astype(str).str.replace(r'[^\d.,-]', '', regex=True)
                    # Nếu có cả chấm và phẩy: 1.250.000,00 -> bỏ chấm, thay phẩy thành chấm
                    has_both = cleaned_num.str.contains(r'\.', na=False) & cleaned_num.str.contains(r',', na=False)
                    cleaned_num = cleaned_num.where(~has_both, cleaned_num.str.replace('.', '', regex=False).str.replace(',', '.', regex=False))
                    # Nếu chỉ có chấm dạng hàng nghìn: 1.250.000
                    has_dot_thousand = cleaned_num.str.contains(r'^\d{1,3}(?:\.\d{3})+$', regex=True, na=False)
                    cleaned_num = cleaned_num.where(~has_dot_thousand, cleaned_num.str.replace('.', '', regex=False))
                    # Nếu chỉ có phẩy dạng thập phân: 1250,5
                    has_comma_dec = cleaned_num.str.contains(r'^\d+,\d+$', na=False)
                    cleaned_num = cleaned_num.where(~has_comma_dec, cleaned_num.str.replace(',', '.', regex=False))
                    
                    std_df[canon_key] = pd.to_numeric(cleaned_num, errors='coerce').fillna(0)
                elif canon_key in ["order_date", "deadline"]:
                    std_df[canon_key] = pd.to_datetime(std_df[canon_key], errors='coerce', dayfirst=True).dt.strftime("%Y-%m-%d")
                    
        return std_df


class DataValidationGuardrail:
    """
    Enterprise Data Validation Guardrail for Minh An Sales AI.
    Intercepts structural anomalies (Max Columns, Insufficient Rows)
    and verifies quantitative metrics availability to prevent analytics failures.
    """
    MAX_COLUMNS: int = 200
    MIN_ROWS: int = 2
    QUANTITATIVE_KEYS: List[str] = ["total_price", "unit_price", "quantity"]

    @classmethod
    def validate_file_structure(cls, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validates column count <= 200 and row count >= 2.
        Returns (is_valid, list_of_error_messages).
        """
        errors = []
        num_cols = len(df.columns)
        num_rows = len(df)

        if num_cols > cls.MAX_COLUMNS:
            errors.append(
                f"Cảnh báo: Tệp dữ liệu vượt quá giới hạn {cls.MAX_COLUMNS} cột cho phép (hiện tại: {num_cols} cột). Vui lòng rút gọn cấu trúc bảng trước khi phân tích."
            )

        if num_rows < cls.MIN_ROWS:
            errors.append(
                f"Cảnh báo: Tệp chỉ có {num_rows} dòng dữ liệu, không đủ mẫu tối thiểu (cần ít nhất {cls.MIN_ROWS} dòng) để thực hiện phân tích xu hướng và thống kê."
            )

        return (len(errors) == 0, errors)

    @classmethod
    def has_quantitative_metrics(cls, df: pd.DataFrame, mapping_dict: Optional[Dict[str, Optional[str]]] = None) -> bool:
        """
        Checks whether the DataFrame contains at least one valid quantitative numerical metric
        (e.g., Doanh thu, Chi phí, Lợi nhuận, Số lượng, Đơn giá...) with actual numeric content
        rather than dummy text characters (like 'x').
        """
        if df.empty:
            return False

        # 1. If mapping_dict is provided, check if any mapped column contains valid numeric data
        if mapping_dict:
            for canon_key in cls.QUANTITATIVE_KEYS:
                col_name = mapping_dict.get(canon_key)
                if col_name and col_name in df.columns:
                    series = df[col_name].dropna()
                    if len(series) > 0:
                        parsed = pd.to_numeric(series.apply(UniversalFileReader.parse_vietnamese_number), errors='coerce').dropna()
                        if len(parsed) > 0:
                            return True

        # 2. Check if canonical columns already exist directly in df
        for canon_key in cls.QUANTITATIVE_KEYS:
            if canon_key in df.columns:
                series = df[canon_key].dropna()
                if len(series) > 0:
                    parsed = pd.to_numeric(series.apply(UniversalFileReader.parse_vietnamese_number), errors='coerce').dropna()
                    if len(parsed) > 0:
                        return True

        # 3. Check any column in df: does ANY column have actual numbers?
        for col in df.columns:
            col_str = str(col).lower()
            if any(skip in col_str for skip in ['phone', 'sdt', 'dien_thoai', 'tel', 'ma_', 'id', 'code', 'email']):
                continue
            series = df[col].dropna()
            if len(series) == 0:
                continue
            # Try to parse as numbers
            parsed = pd.to_numeric(series.apply(UniversalFileReader.parse_vietnamese_number), errors='coerce').dropna()
            if len(parsed) > 0:
                return True

        return False

