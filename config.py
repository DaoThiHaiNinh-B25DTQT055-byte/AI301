"""
Minh An Company - B2B AI Sales Operations Platform Configuration
Centralized configuration parameters for business rules, thresholds, SLAs, and schema mappings.
"""

import os
from typing import Dict, List, Any

# ==============================================================================
# 1. THẨM QUYỀN DUYỆT & NGƯỠNG CHIẾT KHẤU KINH DOANH (APPROVAL MATRIX)
# ==============================================================================
# Ngưỡng tự quyết của Nhân viên Kinh doanh (NVKD)
MAX_REP_DISCOUNT_PCT: float = 5.0          # Chiết khấu <= 5.0%
MAX_REP_ORDER_VALUE: float = 100_000_000.0   # Giá trị đơn hàng <= 100 triệu VNĐ

# Ngưỡng phê duyệt của Trưởng phòng Kinh doanh
MAX_MANAGER_DISCOUNT_PCT: float = 10.0     # Chiết khấu từ > 5.0% đến <= 10.0%
MAX_MANAGER_ORDER_VALUE: float = 500_000_000.0 # Giá trị đơn hàng từ > 100tr đến <= 500 triệu VNĐ

# Ngưỡng phê duyệt của Ban Giám đốc (BGĐ)
# Áp dụng khi Chiết khấu > 10.0% hoặc Giá trị đơn > 500 triệu VNĐ

# Biên lợi nhuận gộp tối thiểu bắt buộc
MIN_GROSS_MARGIN_PCT: float = 12.0

# ==============================================================================
# 2. SLA KHO & TIẾN ĐỘ GIAO HÀNG (WAREHOUSE SLA)
# ==============================================================================
IN_STOCK_LEAD_TIME_DAYS_MIN: int = 1
IN_STOCK_LEAD_TIME_DAYS_MAX: int = 2       # Hàng có sẵn kho: 1-2 ngày
BACKORDER_LEAD_TIME_DAYS_MIN: int = 10
BACKORDER_LEAD_TIME_DAYS_MAX: int = 14     # Hàng thiếu tồn kho: 10-14 ngày nhập bổ sung

# ==============================================================================
# 3. CẤU HÌNH AI & MÔ HÌNH NGÔN NGỮ
# ==============================================================================
DEFAULT_GEMINI_MODEL: str = "gemini-3.1-flash-lite"
CONFIDENCE_THRESHOLD_HIGH: float = 85.0
CONFIDENCE_THRESHOLD_MEDIUM: float = 70.0   # Dưới 70% gắn cờ "Cần người kiểm tra"

# ==============================================================================
# 4. CHUẨN HÓA ÁNH XẠ CỘT DỮ LIỆU (CANONICAL SCHEMA MAPPING)
# ==============================================================================
CANONICAL_COLUMNS: Dict[str, Dict[str, Any]] = {
    "product_name": {
        "label_vi": "Tên Sản Phẩm / Thiết Bị",
        "label_en": "Product Name / Description",
        "type": "string",
        "synonyms": ["ten_san_pham", "product_name", "product", "ten_hang", "thiet_bi", "ten_thiet_bi", "mo_ta", "description", "item_name", "san_pham", "hang_hoa", "device"]
    },
    "sku": {
        "label_vi": "Mã SKU / Mã Sản Phẩm",
        "label_en": "SKU / Item Code",
        "type": "string",
        "synonyms": ["sku", "ma_sku", "ma_hang", "ma_san_pham", "item_code", "product_code", "model", "ma_thiet_bi", "part_number"]
    },
    "quantity": {
        "label_vi": "Số Lượng",
        "label_en": "Quantity",
        "type": "numeric",
        "synonyms": ["so_luong", "quantity", "sl", "qty", "amount_units", "so_luong_mua", "so_luong_yeu_cau"]
    },
    "unit_price": {
        "label_vi": "Đơn Giá (VNĐ)",
        "label_en": "Unit Price (VND)",
        "type": "numeric",
        "synonyms": ["don_gia", "unit_price", "gia", "price", "don_gia_niem_yet", "list_price", "don_gia_vnd", "cost"]
    },
    "total_price": {
        "label_vi": "Thành Tiền / Doanh Thu (VNĐ)",
        "label_en": "Total Amount / Revenue (VND)",
        "type": "numeric",
        "synonyms": ["thanh_tien", "doanh_thu", "doanh_so", "revenue", "sales", "total", "total_price", "total_amount", "tong_tien", "gia_tri", "tong_gia_tri", "net_amount", "amount"]
    },
    "customer_name": {
        "label_vi": "Khách Hàng / Doanh Nghiệp",
        "label_en": "Customer / Company Name",
        "type": "string",
        "synonyms": ["khach_hang", "customer", "customer_name", "company", "ten_khach_hang", "don_vi", "cong_ty", "client", "buyer", "organization"]
    },
    "contact_person": {
        "label_vi": "Người Liên Hệ",
        "label_en": "Contact Person",
        "type": "string",
        "synonyms": ["nguoi_lien_he", "contact_person", "contact", "ho_ten", "nguoi_mua", "dai_dien", "representative"]
    },
    "contact_email": {
        "label_vi": "Email Khách Hàng",
        "label_en": "Contact Email",
        "type": "string",
        "synonyms": ["email", "contact_email", "mail", "thu_dien_tu", "email_lien_he"]
    },
    "contact_phone": {
        "label_vi": "Số Điện Thoại",
        "label_en": "Phone Number",
        "type": "string",
        "synonyms": ["phone", "so_dien_thoai", "sdt", "dien_thoai", "telephone", "mobile", "tel"]
    },
    "order_date": {
        "label_vi": "Ngày Đặt / Ngày Yêu Cầu",
        "label_en": "Request / Order Date",
        "type": "datetime",
        "synonyms": ["ngay_dat", "order_date", "date", "ngay_gui", "ngay_yeu_cau", "created_at", "ngay_tao", "ngay"]
    },
    "deadline": {
        "label_vi": "Hạn Giao Hàng Mong Muốn",
        "label_en": "Delivery Deadline",
        "type": "datetime",
        "synonyms": ["deadline", "han_giao", "ngay_giao_mong_muon", "delivery_date", "han_chot", "tien_do_yeu_cau"]
    },
    "assigned_rep": {
        "label_vi": "NVKD Phụ Trách",
        "label_en": "Assigned Sales Rep",
        "type": "string",
        "synonyms": ["nvkd", "sales_rep", "nguoi_phu_trach", "assigned_to", "nhan_vien", "staff", "account_executive"]
    }
}

# ==============================================================================
# 5. TIÊU CHÍ PHÂN HẠNG KHÁCH HÀNG (CUSTOMER TIER RULES)
# ==============================================================================
CUSTOMER_TIERS = {
    "VIP": {
        "min_revenue": 300_000_000.0,
        "discount_privilege": 8.0,
        "sla_priority": "Ưu tiên cấp 1 (Hỏa tốc 24h)"
    },
    "PRIORITY": {
        "min_revenue": 100_000_000.0,
        "discount_privilege": 5.0,
        "sla_priority": "Ưu tiên cấp 2 (48h)"
    },
    "STANDARD": {
        "min_revenue": 0.0,
        "discount_privilege": 3.0,
        "sla_priority": "Tiêu chuẩn (3-5 ngày)"
    }
}

# ==============================================================================
# 6. TIÊU CHÍ KIỂM TRA ĐẦY ĐỦ THÔNG TIN YÊU CẦU (B2B REQUEST SUFFICIENCY RULES)
# ==============================================================================
REQUIRED_REQUEST_FIELDS: Dict[str, Dict[str, Any]] = {
    "customer_identification": {
        "label_vi": "Tên khách hàng / Doanh nghiệp liên hệ",
        "label_en": "Customer / Company Name",
        "description_vi": "Tên đơn vị, doanh nghiệp hoặc người liên hệ cụ thể",
        "description_en": "Specific company, organization, or contact person",
        "is_mandatory": True
    },
    "quantified_items": {
        "label_vi": "Hạng mục sản phẩm & Số lượng cụ thể",
        "label_en": "Product Items & Definite Quantities",
        "description_vi": "Ít nhất 1 sản phẩm/dịch vụ nhận diện được SKU với số lượng hợp lệ (> 0)",
        "description_en": "At least 1 product/service mapped to SKU with valid quantity (> 0)",
        "is_mandatory": True
    },
    "budget_or_timeline": {
        "label_vi": "Ngân sách hoặc Tiến độ giao hàng",
        "label_en": "Estimated Budget or Delivery Timeline",
        "description_vi": "Thông tin về ngân sách dự kiến hoặc thời hạn cần hàng",
        "description_en": "Information regarding estimated budget or requested deadline",
        "is_mandatory": False
    }
}

