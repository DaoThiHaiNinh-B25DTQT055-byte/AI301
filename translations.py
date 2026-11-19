"""
Hệ thống Đa ngôn ngữ (i18n) cho Minh An AI Sales Operations Center
Hỗ trợ chuyển đổi mượt mà giữa Tiếng Việt và Tiếng Anh chuyên nghiệp.
Phiên bản 2026 mở rộng: Universal File Reader, Data Quality Audit, Schema Mapping,
Quy trình Thống kê 8 bước, Phân loại RFM, Telegram Approval & AI Sales Copilot.
"""

TRANSLATIONS = {
    "vi": {
        "app_brand": "MINH AN COMPANY",
        "app_subtitle": "Nền tảng AI Bán hàng B2B Doanh nghiệp",
        "live_ai_online": "gemini-3.1-flash-lite • Trực tuyến",
        "live_rules_online": "Hệ thống Quy tắc Sẵn sàng",
        "team_metric": "Đội ngũ: 6 NVKD • Khối lượng: ~180 Yêu cầu/Tuần",
        
        "tab_single": "🎯 Xử lý yêu cầu khách hàng",
        "tab_batch": "📊 Pipeline Xử lý hàng loạt",
        "tab_analytics": "📈 Trung tâm Thống kê & Phân tích",
        "tab_catalog": "📦 Bảng giá & Kho khả dụng",
        "tab_settings": "⚙️ Nguồn Dữ liệu & AI Engine",
        
        "hero_tag": "AI Sales Operations Hub • Enterprise Edition 2026",
        "hero_title_1": "Tự Động Hóa Xử Lý Cơ Hội Bán Hàng",
        "hero_title_2": "Doanh Nghiệp B2B",
        "hero_desc": "Đột phá tốc độ xử lý yêu cầu khách hàng: Tự động trích xuất hạng mục, đối soát giá niêm yết hiện hành, kiểm tra kho khả dụng & tiến độ giao hàng khả thi, tự động phân quyền duyệt và xuất ngay bản nháp báo giá chuyên nghiệp.",
        
        "hero_kpi_1_num": "6 NVKD",
        "hero_kpi_1_lbl": "Chuyên viên phụ trách",
        "hero_kpi_2_num": "~180 Req",
        "hero_kpi_2_lbl": "Khối lượng xử lý / tuần",
        "hero_kpi_3_num": "< 3 Phút",
        "hero_kpi_3_lbl": "Tốc độ phản hồi (Giảm 85%)",
        "hero_kpi_4_num": "100%",
        "hero_kpi_4_lbl": "Chuẩn hóa đối soát giá",
        
        "hero_btn_cta": "🚀 Bắt đầu Thẩm định Yêu cầu",
        "hero_btn_catalog": "📦 Khám phá Danh mục Bảng giá",
        
        # 5-Step Stepper (Legacy alias)
        "step_5_1_title": "1. Tiếp nhận",
        "step_5_1_sub": "Khách hàng & Intake",
        "step_5_2_title": "2. Phân loại & Kiểm tra",
        "step_5_2_sub": "Đủ thông tin?",
        "step_5_3_title": "3. Tạo Hồ sơ Cơ hội",
        "step_5_3_sub": "Gán NVKD",
        "step_5_4_title": "4. Thẩm định Kho & Giá",
        "step_5_4_sub": "NVKD & Vận hành",
        "step_5_5_title": "5. Báo giá & Kết thúc",
        "step_5_5_sub": "Hoàn tất đề xuất",
        
        # 6-Step Stepper (Chuẩn Sơ đồ Quy trình B2B Minh An)
        "wf_step_1_title": "1. Tiếp nhận",
        "wf_step_1_sub": "Khách hàng & Intake",
        "wf_step_2_title": "2. Phân loại & Kiểm tra",
        "wf_step_2_sub": "Đủ thông tin?",
        "wf_step_3_title": "3. Tạo Hồ sơ Cơ hội",
        "wf_step_3_sub": "CRM & Gán NVKD",
        "wf_step_4_title": "4. Thẩm định kho & giá",
        "wf_step_4_sub": "NVKD & Vận hành",
        "wf_step_5_title": "5. Lập Báo giá & Dự thảo",
        "wf_step_5_sub": "NVKD & AI Copilot",
        "wf_step_approval_title": "Trưởng phòng duyệt",
        "wf_step_approval_sub": "Khi vượt quyền",
        "wf_step_6_title": "6. Kết thúc",
        "wf_step_6_sub": "Cập nhật & Theo dõi",
        
        "gateway_1_title": "Điểm rẽ 1: Kiểm tra Đầy đủ Thông tin",
        "gateway_1_sufficient": "Đủ thông tin hợp lệ -> Tiếp tục bước 3",
        "gateway_1_insufficient": "Thiếu thông tin bắt buộc -> Yêu cầu KH làm rõ / bổ sung",
        "gateway_2_title": "Điểm rẽ 2: Kiểm tra Thẩm quyền & Ngưỡng duyệt",
        "gateway_2_escalate": "Vượt thẩm quyền NVKD -> Chuyển Trưởng phòng duyệt",
        "gateway_2_auto": "Trong thẩm quyền tự quyết -> Hoàn tất đề xuất & Báo giá",
        "clarification_box_title": "Yêu cầu Khách hàng Làm rõ / Bổ sung Thông tin",
        "clarification_paste_label": "Dán thông tin bổ sung từ khách hàng (để nhận lại B1 & chạy lại B2):",
        "btn_resubmit_clarification": "🔄 Cập nhật bổ sung & Chạy lại quy trình",
        
        "req_box_title": "Tiếp nhận Yêu cầu từ Email / Biểu mẫu Khách hàng",
        "sample_select_label": "Chọn yêu cầu mẫu:",
        "sample_select_default": "-- Chọn yêu cầu mẫu để thử nghiệm nhanh kịch bản nghiệp vụ --",
        "req_input_label": "Nội dung yêu cầu từ khách hàng doanh nghiệp:",
        "req_input_placeholder": "Dán nội dung email hoặc mẫu đơn đặt hàng của khách hàng vào đây...",
        "btn_process": "🚀 Thẩm định Yêu cầu & Lập Đề Xuất Báo Giá",
        "processing_spinner": "AI Agent đang trích xuất dữ liệu, kiểm tra kho và định tuyến phê duyệt...",
        
        "rules_card_title": "Nguyên tắc Vận hành Minh An",
        "rule_sku_title": "Đối soát SKU & Đơn giá",
        "rule_sku_desc": "Tự động map danh mục thiết bị, lấy giá niêm yết mới nhất và kiểm tra tồn kho khả dụng.",
        "rule_sla_title": "SLA Kho & Giao hàng",
        "rule_sla_desc": "Hàng sẵn kho cam kết giao 1-2 ngày; hàng thiếu kích hoạt SLA nhập bổ sung 10-14 ngày.",
        "rule_matrix_title": "Ngưỡng Phân quyền Duyệt",
        "rule_matrix_desc": "Chiết khấu <= 5% & đơn <= 100tr: NVKD tự quyết. Vượt ngưỡng: bắt buộc Trưởng phòng phê duyệt.",
        
        "insufficient_title": "YÊU CẦU THIẾU THÔNG TIN ĐỂ LẬP BÁO GIÁ",
        "insufficient_desc": "Khách hàng chưa cung cấp cấu hình rõ ràng, số lượng hoặc ngân sách. Hệ thống tự động kích hoạt luồng <b>Yêu cầu KH làm rõ / bổ sung</b> để tránh NVKD báo giá phỏng đoán sai sót.",
        "missing_items_title": "Danh mục các điểm thiếu sót cần làm rõ:",
        "clarification_email_title": "Bản nháp Email gửi Khách hàng yêu cầu bổ sung:",
        "btn_download_clarification": "📥 Tải Bản nháp Email (.txt)",
        
        "opp_title": "Hồ Sơ Cơ Hội:",
        "valid_info_badge": "✓ Thông tin hợp lệ",
        "kpi_total_amount": "Tổng Giá Trị Thanh Toán",
        "kpi_discount": "Chiết Khấu Đề Xuất",
        "kpi_lead_time": "Tiến Độ Khả Thi Thực Tế",
        "kpi_sales_rep": "NVKD Phụ Trách",
        
        "items_table_title": "Danh mục Hàng hóa & Thẩm định Kho khả dụng",
        "btn_download_quotation": "Tải bảng báo giá chi tiết (.xlsx)",
        
        "client_info_title": "Thông tin Khách hàng & Phân bổ NVKD",
        "risk_warnings_title": "Cảnh báo Rủi ro Vận hành & SLA",
        "approval_memo_title": "Phiếu Trình Duyệt Nội Bộ (Gửi Trưởng phòng / BGĐ)",
        "approval_memo_expander": "Nhấp để xem đầy đủ lý do giải trình & các điều kiện cần phê duyệt",
        "proposal_email_title": "Bản nháp Email Báo giá & Đề xuất Kinh doanh Gửi Khách hàng",
        "btn_save_pipeline": "💾 Lưu Cơ hội vào Quản lý Pipeline",
        "btn_download_proposal": "📥 Tải Bản nháp Email Đề xuất (.txt)",
        "toast_saved_pipeline": "Đã lưu hồ sơ cơ hội vào Pipeline theo dõi!",
        
        # Universal File Ingestion & Data Quality
        "universal_uploader_title": "📁 Tiếp Nhận Hồ Sơ / Đơn Đặt Hàng Đa Định Dạng",
        "universal_uploader_desc": "Hỗ trợ tải lên file Excel (.xlsx, .xls), CSV, TSV, JSON, XML, Word (.docx), PDF (text/scan), Email (.eml, .msg) và Ảnh (.png, .jpg).",
        "preview_data_title": "Bản Xem Trước Dữ Liệu Tải Lên (10 dòng đầu)",
        "data_quality_title": "Báo Cáo Chất Lượng Dữ Liệu (Data Quality Audit)",
        "quality_score_label": "Điểm Đánh Giá Chất Lượng",
        "schema_mapping_title": "Ánh Xạ Cột Chuẩn Hóa (Schema Mapping)",
        "schema_mapping_desc": "AI tự động đối chiếu các cột trong tệp của bạn với các trường dữ liệu chuẩn của hệ thống Minh An.",
        "btn_apply_mapping": "⚡ Xác Nhận Ánh Xạ & Tiến Hành Phân Tích",
        
        # Audit Logs
        "audit_trail_title": "📋 Nhật Ký Xử Lý Minh Bạch (Audit Trail Log)",
        
        # Telegram Bot
        "tg_card_title": "Kênh Phê Duyệt Tức Thì Qua Telegram / Teams Bot",
        "tg_bot_badge": "🤖 Minh An Approval Bot • Trực tuyến",
        "tg_desc": "Yêu cầu bán hàng vượt thẩm quyền (Chiết khấu > 5% hoặc Đơn > 100tr). Trưởng phòng có thể bấm phê duyệt ngay tức thì qua Bot bên dưới:",
        "tg_btn_approve": "✅ Phê Duyệt Ngay (Approve)",
        "tg_btn_reject": "❌ Từ Chối Yêu Cầu (Reject)",
        "tg_btn_adjust": "💬 Yêu Cầu Giảm Chiết Khấu",
        "tg_status_approved": "ĐÃ PHÊ DUYỆT BỞI TRƯỞNG PHÒNG (QUA TELEGRAM BOT)",
        "tg_status_rejected": "TRƯỞNG PHÒNG TỪ CHỐI DUYỆT (CẦN TÍNH TOÁN LẠI)",
        "tg_status_adjusted": "YÊU CẦU ĐIỀU CHỈNH: GIẢM CHIẾT KHẤU XUỐNG DƯỚI 5%",
        "tg_toast_approved": "Trưởng phòng Kinh doanh đã phê duyệt thành công qua Telegram Bot!",
        
        # AI Sales Copilot
        "copilot_card_title": "Trợ Lý Đàm Phán Báo Giá Đa Vòng (AI Sales Copilot)",
        "copilot_subtitle": "Chuyên gia AI hỗ trợ NVKD đàm phán trực tiếp về giá, bảo toàn biên lợi nhuận và phương án kho.",
        "copilot_pill_1": "Khách xin giảm thêm 2% nếu thanh toán 100% trước?",
        "copilot_pill_2": "Khách cần giao gấp trong 3 ngày, giải pháp kho thế nào?",
        "copilot_pill_3": "Có nên tặng thêm gói bảo hành 06 tháng thay vì giảm giá?",
        "copilot_prompt_placeholder": "Nhập tình huống hoặc câu hỏi đàm phán của khách hàng...",
        "copilot_btn_ask": "✨ Phân Tích & Tư Vấn Đàm Phán",
        
        # Batch Tab
        "batch_title": "Pipeline Xử lý Đồng thời Danh sách Yêu cầu (~180 yêu cầu/tuần)",
        "batch_radio_label": "Phương thức nạp danh sách yêu cầu hàng tuần:",
        "batch_radio_sample": "Bộ 4 Yêu cầu thực tế mẫu của Minh An",
        "batch_radio_upload": "Tải lên file danh sách (.csv, .xlsx, .json, .pdf)",
        "btn_run_batch": "⚡ Chạy Xử lý Toàn bộ Danh sách",
        "batch_kpi_total": "Tổng Yêu Cầu",
        "batch_kpi_sufficient": "Đủ Điều Kiện Báo Giá",
        "batch_kpi_escalated": "Cần Trưởng Phòng Duyệt",
        "batch_kpi_pipeline": "Tổng Doanh Thu Tiềm Năng",
        
        # Webhook Feature
        "webhook_title": "Cổng Tiếp Nhận Webhook Tự Động (Email & CRM Ingestion)",
        "webhook_endpoint_label": "Webhook Endpoint (Sẵn sàng kết nối Gmail / Hubspot / Salesforce):",
        "webhook_btn_simulate_email": "✉️ Mô phỏng Email gửi tới sales@minhan.com.vn",
        "webhook_btn_simulate_crm": "⚡ Mô phỏng Ingest Yêu cầu từ CRM Doanh nghiệp",
        "webhook_success_msg": "Đã tiếp nhận thành công Payload Webhook từ kênh đối tác và tự động đưa vào hàng đợi xử lý!",
        
        # Analytics Tab (Standard 8-Step Process)
        "analytics_main_title": "📈 Trung Tâm Thống Kê & Phân Tích Tài Chính Chuẩn 8 Bước",
        "analytics_sub_financial": "💰 Thống Kê Tài Chính & KPI Doanh Số",
        "analytics_sub_rfm": "👥 Phân Hạng Khách Hàng (RFM Prioritization)",
        "analytics_sub_segment": "📊 Phân Nhóm Linh Hoạt (Dynamic Segmentation)",
        "analytics_sub_charts": "📉 Trực Quan Hóa Tương Tác (Plotly Charts)",
        "analytics_sub_insights": "💡 Nhận Định Chiến Lược & Khuyến Nghị Hành Động",
        "btn_export_analytics": "📊 Tải Báo Cáo Thống Kê Toàn Diện (.xlsx)",
        "guardrail_max_cols": "Cảnh báo: Tệp dữ liệu vượt quá giới hạn 200 cột cho phép (hiện tại: {cols} cột). Vui lòng rút gọn cấu trúc bảng trước khi phân tích.",
        "guardrail_min_rows": "Cảnh báo: Tệp chỉ có {rows} dòng dữ liệu, không đủ mẫu tối thiểu (cần ít nhất 2 dòng) để thực hiện phân tích xu hướng và thống kê.",
        "guardrail_no_metrics": "Lỗi cấu trúc dữ liệu: Không tìm thấy cột số liệu định lượng nào hợp lệ để tính toán chỉ số KPI và vẽ biểu đồ.",

        
        # Catalog Tab
        "catalog_title": "Bảng Giá Niêm Yết, Kho Khả Dụng & Đội Ngũ Kinh Doanh",
        "cat_tab_products": "Danh mục Sản phẩm & Kho khả dụng",
        "cat_tab_sales": "Đội ngũ 6 Nhân viên Kinh doanh",
        "cat_tab_charts": "📊 Trực quan hóa Tồn kho & Định giá",
        
        # Settings Tab
        "settings_title": "Quản lý Nguồn Dữ liệu Tham chiếu (Excel, CSV, Google Sheets)",
        "upload_file_title": "1. Tải lên file Bảng giá & Kho khả dụng (.xlsx, .csv)",
        "upload_file_desc": "Cập nhật danh mục thiết bị, đơn giá niêm yết mới nhất và số lượng tồn khả dụng từ kho.",
        "gsheet_title": "2. Đồng bộ trực tuyến từ Google Sheets",
        "gsheet_desc": "Đọc trực tiếp dữ liệu theo thời gian thực từ bảng tính Google Sheets ở chế độ công khai.",
        "btn_sync_gsheet": "Kết nối & Tải Dữ liệu",
        "gemini_title": "Tích hợp Trí tuệ Nhân tạo Google Gemini API",
        "gemini_status_label": "Trạng thái Gemini API:",
        "gemini_active": "✓ Đang hoạt động",
        "gemini_inactive": "Chưa kích hoạt",
        "gemini_desc": "Khóa API đã được tích hợp an toàn qua tệp môi trường .env. Hệ thống sử dụng mô hình tiên tiến Gemini 3.1 Flash Lite để tối ưu hóa việc phân tích yêu cầu phức tạp và tự động sinh bản nháp email phản hồi B2B chuyên nghiệp.",
        "btn_save_key": "Lưu & Cập nhật Khóa",
        
        "footer_text": "CÔNG TY CỔ PHẦN CÔNG NGHỆ MINH AN • TRUNG TÂM VẬN HÀNH BÁN HÀNG AI • LOCALHOST ENTERPRISE EDITION v4.0",
        "theme_light": "☀️ Sáng",
        "theme_dark": "🌙 Tối",
        
        # Chart Sections
        "overview_kpi_pipeline": "Tổng doanh thu báo giá",
        "overview_kpi_processed": "Số yêu cầu đã xử lý",
        "overview_kpi_autorate": "Tỷ lệ tự quyết NVKD",
        "overview_kpi_sla": "SLA xử lý trung bình",
        "charts_single_title": "Phân tích kỹ thuật & tài chính yêu cầu",
        "chart_opp_governance": "Thẩm quyền chiết khấu & giá trị",
        "chart_opp_items": "Giá trị từng hạng mục trong yêu cầu",
        "chart_opp_category": "Cơ cấu giá trị theo nhóm sản phẩm",
        "chart_opp_inventory": "Đối chiếu số lượng yêu cầu vs tồn kho khả dụng",
        "chart_opp_leadtime": "Tiến độ bàn giao dự kiến theo từng hạng mục",
        "charts_batch_title": "Trực quan hóa hiệu suất pipeline hàng loạt",
        "charts_catalog_title": "Phân tích cơ cấu kho & danh mục bảng giá",
        "charts_dynamic_title": "Khám phá & tùy biến biểu đồ dữ liệu tải lên",
        "charts_empty_state": "Hãy tải file hoặc xử lý một yêu cầu để xem biểu đồ trực quan."
    },
    "en": {
        "app_brand": "MINH AN COMPANY",
        "app_subtitle": "Enterprise B2B Sales AI Platform",
        "live_ai_online": "gemini-3.1-flash-lite • Online",
        "live_rules_online": "Rule-based Engine Ready",
        "team_metric": "Team: 6 Sales Reps • Workload: ~180 Inquiries/Week",
        
        "tab_single": "🎯 Customer Request Intake",
        "tab_batch": "📊 Batch Processing Pipeline",
        "tab_analytics": "📈 Statistical & Analytics Hub",
        "tab_catalog": "📦 Price List & Available Stock",
        "tab_settings": "⚙️ Data Sources & AI Engine",
        
        "hero_tag": "AI Sales Operations Hub • Enterprise Edition 2026",
        "hero_title_1": "Automated Sales Opportunity Operations",
        "hero_title_2": "Enterprise B2B",
        "hero_desc": "Accelerate B2B turnaround: Automatic entity extraction, live price verification, available inventory & lead-time feasibility audit, escalation matrix routing, and client quotation proposal drafting.",
        
        "hero_kpi_1_num": "6 Reps",
        "hero_kpi_1_lbl": "Dedicated Account Executives",
        "hero_kpi_2_num": "~180 Req",
        "hero_kpi_2_lbl": "Weekly Intake Volume",
        "hero_kpi_3_num": "< 3 Mins",
        "hero_kpi_3_lbl": "Turnaround Speed (-85%)",
        "hero_kpi_4_num": "100%",
        "hero_kpi_4_lbl": "Catalog Price Standardization",
        
        "hero_btn_cta": "🚀 Launch Request Assessment",
        "hero_btn_catalog": "📦 Explore Product Catalog",
        
        # 5-Step Stepper (Legacy alias)
        "step_5_1_title": "1. Intake",
        "step_5_1_sub": "Customer & Intake",
        "step_5_2_title": "2. Classify & Verify",
        "step_5_2_sub": "Sufficient Data?",
        "step_5_3_title": "3. Opportunity Profile",
        "step_5_3_sub": "Assign Rep",
        "step_5_4_title": "4. Stock & Price Audit",
        "step_5_4_sub": "Rep & Ops",
        "step_5_5_title": "5. Proposal & Close",
        "step_5_5_sub": "Final Commercial Draft",
        
        # 6-Step Stepper (Minh An B2B Official Workflow)
        "wf_step_1_title": "1. Intake",
        "wf_step_1_sub": "Customer & Intake",
        "wf_step_2_title": "2. Classify & Verify",
        "wf_step_2_sub": "Sufficient Data?",
        "wf_step_3_title": "3. Opportunity Profile",
        "wf_step_3_sub": "CRM & Assign Rep",
        "wf_step_4_title": "4. Stock & Price Audit",
        "wf_step_4_sub": "Sales Rep & Ops",
        "wf_step_5_title": "5. Quote & Proposal",
        "wf_step_5_sub": "Rep & AI Copilot",
        "wf_step_approval_title": "Manager Approval",
        "wf_step_approval_sub": "Escalation Only",
        "wf_step_6_title": "6. Close",
        "wf_step_6_sub": "Update & Follow-up",
        
        "gateway_1_title": "Decision Gateway 1: Request Data Sufficiency",
        "gateway_1_sufficient": "Data complete & valid -> Proceed to Step 3",
        "gateway_1_insufficient": "Missing mandatory data -> Customer clarification required",
        "gateway_2_title": "Decision Gateway 2: Governance & Approval Matrix",
        "gateway_2_escalate": "Exceeds rep authority -> Escalated to Sales Manager",
        "gateway_2_auto": "Within rep authority -> Self-approved, proposal finalized",
        "clarification_box_title": "Customer Clarification & Data Completion Required",
        "clarification_paste_label": "Paste supplementary information from client (loops to B1 & re-evaluates B2):",
        "btn_resubmit_clarification": "🔄 Submit Supplementary Info & Re-run Workflow",
        
        "req_box_title": "Inbound Request Intake (Email / Web Form)",
        "sample_select_label": "Select sample scenario:",
        "sample_select_default": "-- Select a sample inquiry for quick workflow testing --",
        "req_input_label": "Client business inquiry text:",
        "req_input_placeholder": "Paste customer inquiry email or RFP text here...",
        "btn_process": "🚀 Assess Inquiry & Generate Commercial Quotation",
        "processing_spinner": "AI Agent is extracting line-items, auditing inventory, and routing approvals...",
        
        "rules_card_title": "Minh An Operational Guidelines",
        "rule_sku_title": "SKU Matching & Pricing",
        "rule_sku_desc": "Automatically maps line-items to catalog prices and verifies physical on-hand stock.",
        "rule_sla_title": "Warehouse SLA & Delivery",
        "rule_sla_desc": "In-stock items ship within 1-2 days; backordered items trigger a 10-14 day import SLA.",
        "rule_matrix_title": "Approval Escalation Matrix",
        "rule_matrix_desc": "Discount <= 5% & order <= 100M VND: Rep approved. Exceeded: Sales Manager approval required.",
        
        "insufficient_title": "INSUFFICIENT INFORMATION TO DRAFT PROPOSAL",
        "insufficient_desc": "The client inquiry lacks specific model configurations, quantities, or budget boundaries. The agent triggered <b>Request Client Clarification</b> to prevent guesswork errors.",
        "missing_items_title": "Missing items required for proposal:",
        "clarification_email_title": "Draft Clarification Email to Client:",
        "btn_download_clarification": "📥 Download Clarification Email (.txt)",
        
        "opp_title": "Opportunity File:",
        "valid_info_badge": "✓ Validated Inquiry",
        "kpi_total_amount": "Total Net Value",
        "kpi_discount": "Applied Discount",
        "kpi_lead_time": "Feasible Delivery SLA",
        "kpi_sales_rep": "Assigned Sales Rep",
        
        "items_table_title": "Line Items & Available Stock Assessment",
        "btn_download_quotation": "Download detailed quotation (.xlsx)",
        
        "client_info_title": "Client Profile & Rep Routing",
        "risk_warnings_title": "Operations & SLA Risk Alerts",
        "approval_memo_title": "Internal Approval Memo (For Sales Manager / Executive)",
        "approval_memo_expander": "Click to expand justification analysis and approval criteria",
        "proposal_email_title": "Draft Commercial Proposal & Quotation Email",
        "btn_save_pipeline": "💾 Save to Pipeline Tracker",
        "btn_download_proposal": "📥 Download Proposal Email (.txt)",
        "toast_saved_pipeline": "Successfully saved opportunity to pipeline tracker!",
        
        # Universal File Ingestion & Data Quality
        "universal_uploader_title": "📁 Multi-format Document & Dataset Ingestion",
        "universal_uploader_desc": "Supports Excel (.xlsx, .xls), CSV, TSV, JSON, XML, Word (.docx), PDF (text/scan), Email (.eml, .msg), and Images (.png, .jpg).",
        "preview_data_title": "Uploaded Dataset Preview (First 10 Rows)",
        "data_quality_title": "Data Quality Audit Report",
        "quality_score_label": "Data Quality Index",
        "schema_mapping_title": "Canonical Schema Mapping",
        "schema_mapping_desc": "AI automatically matches your file headers to Minh An official canonical data schema.",
        "btn_apply_mapping": "⚡ Confirm Mapping & Execute Analytics",
        
        # Audit Logs
        "audit_trail_title": "📋 Transparent Processing Audit Trail Log",
        
        # Telegram Bot
        "tg_card_title": "Instant Escalation Approval via Telegram / Teams Bot",
        "tg_bot_badge": "🤖 Minh An Approval Bot • Online",
        "tg_desc": "Opportunity requires managerial sign-off (Discount > 5% or Amount > 100M VND). Sales Manager can execute instant approval below:",
        "tg_btn_approve": "✅ Approve Opportunity",
        "tg_btn_reject": "❌ Reject Request",
        "tg_btn_adjust": "💬 Request Discount Reduction",
        "tg_status_approved": "APPROVED BY SALES MANAGER (VIA TELEGRAM BOT)",
        "tg_status_rejected": "REJECTED BY SALES MANAGER (RE-CALCULATION REQUIRED)",
        "tg_status_adjusted": "ADJUSTMENT REQUESTED: REDUCE DISCOUNT BELOW 5%",
        "tg_toast_approved": "Sales Manager successfully signed off via Telegram Bot!",
        
        # AI Sales Copilot
        "copilot_card_title": "Interactive Commercial Negotiation Copilot",
        "copilot_subtitle": "Real-time AI Copilot assisting sales reps with live margins, discount tradeoffs, and SLA scheduling.",
        "copilot_pill_1": "Can we offer extra 2% discount if client pays 100% upfront?",
        "copilot_pill_2": "Client demands urgent delivery in 3 days, what is the inventory solution?",
        "copilot_pill_3": "Should we offer 6 months free maintenance instead of cash discount?",
        "copilot_prompt_placeholder": "Ask the sales copilot about pricing, margins, or negotiation terms...",
        "copilot_btn_ask": "✨ Analyze & Advise Terms",
        
        # Batch Tab
        "batch_title": "Batch Inbound Processing Pipeline (~180 inquiries/week)",
        "batch_radio_label": "Batch data source input method:",
        "batch_radio_sample": "Minh An 4 Core Scenario Samples",
        "batch_radio_upload": "Upload batch inquiry file (.csv, .xlsx, .json, .pdf)",
        "btn_run_batch": "⚡ Execute Batch Processing Pipeline",
        "batch_kpi_total": "Total Inquiries",
        "batch_kpi_sufficient": "Ready for Quotation",
        "batch_kpi_escalated": "Manager Approval Required",
        "batch_kpi_pipeline": "Total Pipeline Value",
        
        # Webhook Feature
        "webhook_title": "Automated Webhook Gateway (Email & CRM Ingestion)",
        "webhook_endpoint_label": "Live Webhook Endpoint (Ready for Gmail / Hubspot / Salesforce):",
        "webhook_btn_simulate_email": "✉️ Simulate Incoming Email to sales@minhan.com.vn",
        "webhook_btn_simulate_crm": "⚡ Simulate Inbound Lead from Enterprise CRM",
        "webhook_success_msg": "Successfully received and ingested Webhook Payload into automated sales queue!",
        
        # Analytics Tab (Standard 8-Step Process)
        "analytics_main_title": "📈 8-Step Standard Statistical & Financial Analytics Hub",
        "analytics_sub_financial": "💰 Financial Metrics & Revenue KPIs",
        "analytics_sub_rfm": "👥 Customer RFM Prioritization",
        "analytics_sub_segment": "📊 Dynamic Segmentation & Group Share",
        "analytics_sub_charts": "📉 Interactive Plotly Visualizations",
        "analytics_sub_insights": "💡 Executive Strategic Insights & Actions",
        "btn_export_analytics": "📊 Export Comprehensive Analytics Report (.xlsx)",
        "guardrail_max_cols": "Warning: Data file exceeds the limit of 200 columns (current: {cols} columns). Please reduce table structure before analysis.",
        "guardrail_min_rows": "Warning: File only contains {rows} data rows, not meeting minimum sample size (at least 2 rows required) for statistical analysis.",
        "guardrail_no_metrics": "Data structure error: No valid quantitative metric column found to compute KPIs and charts.",

        
        # Catalog Tab
        "catalog_title": "Price List, Available Stock & Sales Team",
        "cat_tab_products": "Product Catalog & Stock",
        "cat_tab_sales": "6 Sales Representatives",
        "cat_tab_charts": "📊 Inventory & Pricing Analytics",
        
        # Settings Tab
        "settings_title": "Reference Data Sources & AI Configuration",
        "upload_file_title": "1. Upload Catalog & Inventory File (.xlsx, .csv)",
        "upload_file_desc": "Update equipment master list, list prices, and available inventory from warehouse.",
        "gsheet_title": "2. Live Sync from Google Sheets",
        "gsheet_desc": "Directly fetch real-time data from public Google Sheets spreadsheet.",
        "btn_sync_gsheet": "Connect & Synchronize Data",
        "gemini_title": "Google Gemini AI Engine Integration",
        "gemini_status_label": "Gemini API Status:",
        "gemini_active": "✓ Active & Connected",
        "gemini_inactive": "Inactive",
        "gemini_desc": "API Key is securely configured via .env. The system utilizes Gemini 3.1 Flash Lite for semantic inquiry reasoning and executive communication drafting.",
        "btn_save_key": "Save & Update Key",
        
        "footer_text": "MINH AN TECHNOLOGY JSC • AI SALES OPERATIONS CENTER • LOCALHOST ENTERPRISE EDITION v4.0",
        "theme_light": "☀️ Light",
        "theme_dark": "🌙 Dark",
        
        # Chart Sections
        "overview_kpi_pipeline": "Total quoted pipeline",
        "overview_kpi_processed": "Opportunities processed",
        "overview_kpi_autorate": "Sales Rep self-approval rate",
        "overview_kpi_sla": "Avg turnaround SLA",
        "charts_single_title": "Technical & financial opportunity analytics",
        "chart_opp_governance": "Discount authority & order value",
        "chart_opp_items": "Requested items value contribution",
        "chart_opp_category": "Value breakdown by product category",
        "chart_opp_inventory": "Demand vs warehouse stock check",
        "chart_opp_leadtime": "Delivery SLA commitment by item",
        "charts_batch_title": "Batch operations & pipeline analytics",
        "charts_catalog_title": "Warehouse inventory & price matrix analytics",
        "charts_dynamic_title": "Dynamic data explorer & interactive visualizer",
        "charts_empty_state": "Upload a file or process an opportunity to unlock visual charts."
    }
}

def t(key: str, lang: str = "vi") -> str:
    """Retrieves localized text for key; fallbacks gracefully to Vietnamese."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["vi"])
    return lang_dict.get(key, TRANSLATIONS["vi"].get(key, key))
