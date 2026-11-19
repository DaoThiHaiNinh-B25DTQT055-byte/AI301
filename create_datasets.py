import pandas as pd
import json

# 1. Products and Pricing
products = [
    {
        "SKU": "SRV-DELL-R750",
        "ProductName": "Máy chủ Dell PowerEdge R750 (Intel Xeon Silver 4314, 32GB RAM, 2x 480GB SSD, 2x 2TB HDD, H755)",
        "Category": "Máy chủ & Lưu trữ",
        "UnitPrice": 92500000,
        "Unit": "Bộ",
        "WarrantyMonths": 36,
        "AvailableStock": 4,
        "LeadTimeInStockDays": 2,
        "LeadTimeOutOfStockDays": 14,
        "Description": "Máy chủ 2U dành cho doanh nghiệp vừa và lớn, tải cơ sở dữ liệu và ảo hóa."
    },
    {
        "SKU": "SRV-HPE-DL380",
        "ProductName": "Máy chủ HPE ProLiant DL380 Gen10 (Xeon 4210R, 32GB RAM, P408i-a, 8SFF, 800W)",
        "Category": "Máy chủ & Lưu trữ",
        "UnitPrice": 86000000,
        "Unit": "Bộ",
        "WarrantyMonths": 36,
        "AvailableStock": 2,
        "LeadTimeInStockDays": 2,
        "LeadTimeOutOfStockDays": 15,
        "Description": "Máy chủ đa năng hiệu năng cao cho hệ thống ERP và kế toán."
    },
    {
        "SKU": "SW-CISCO-C9200L-24P",
        "ProductName": "Thiết bị chuyển mạch Cisco Catalyst C9200L-24P-4G-E (24 Port PoE+, 4x 1G SFP)",
        "Category": "Thiết bị mạng",
        "UnitPrice": 38500000,
        "Unit": "Chiếc",
        "WarrantyMonths": 24,
        "AvailableStock": 8,
        "LeadTimeInStockDays": 1,
        "LeadTimeOutOfStockDays": 21,
        "Description": "Switch quản lý Layer 3 doanh nghiệp, cấp nguồn PoE+ cho camera và Access Point."
    },
    {
        "SKU": "SW-ARUBA-1930-48G",
        "ProductName": "Switch Aruba Instant On 1930 48G 4SFP/SFP+ (JL685A)",
        "Category": "Thiết bị mạng",
        "UnitPrice": 19800000,
        "Unit": "Chiếc",
        "WarrantyMonths": 24,
        "AvailableStock": 15,
        "LeadTimeInStockDays": 1,
        "LeadTimeOutOfStockDays": 10,
        "Description": "Switch 48 cổng Gigabit, 4 cổng quang 10G, quản lý đám mây hoặc web cục bộ."
    },
    {
        "SKU": "AP-ARUBA-AP22",
        "ProductName": "Bộ phát WiFi Aruba Instant On AP22 (Wi-Fi 6, 2x2 MU-MIMO)",
        "Category": "Thiết bị mạng",
        "UnitPrice": 3600000,
        "Unit": "Chiếc",
        "WarrantyMonths": 24,
        "AvailableStock": 25,
        "LeadTimeInStockDays": 1,
        "LeadTimeOutOfStockDays": 7,
        "Description": "Access Point chuẩn Wifi 6 chịu tải đến 75 thiết bị đồng thời cho văn phòng."
    },
    {
        "SKU": "NB-DELL-LAT5540",
        "ProductName": "Laptop Dell Latitude 5540 (Core i7-1365U, 16GB RAM, 512GB SSD, 15.6 Inch FHD, Win 11 Pro)",
        "Category": "Máy tính & Thiết bị đầu cuối",
        "UnitPrice": 26500000,
        "Unit": "Chiếc",
        "WarrantyMonths": 24,
        "AvailableStock": 12,
        "LeadTimeInStockDays": 1,
        "LeadTimeOutOfStockDays": 10,
        "Description": "Laptop doanh nhân bảo mật cao cấp, độ bền chuẩn quân đội."
    },
    {
        "SKU": "NB-LENOVO-T14G4",
        "ProductName": "Laptop Lenovo ThinkPad T14 Gen 4 (Core i5-1335U, 16GB RAM, 512GB SSD, 14 Inch WUXGA)",
        "Category": "Máy tính & Thiết bị đầu cuối",
        "UnitPrice": 23900000,
        "Unit": "Chiếc",
        "WarrantyMonths": 36,
        "AvailableStock": 10,
        "LeadTimeInStockDays": 1,
        "LeadTimeOutOfStockDays": 12,
        "Description": "Bàn phím ThinkPad trứ danh, bền bỉ cho nhân viên văn phòng và quản lý."
    },
    {
        "SKU": "MON-DELL-U2724D",
        "ProductName": "Màn hình đồ họa Dell UltraSharp U2724D (27 Inch, 2K QHD, 120Hz, IPS Black, Type-C)",
        "Category": "Màn hình & Phụ kiện",
        "UnitPrice": 9900000,
        "Unit": "Chiếc",
        "WarrantyMonths": 36,
        "AvailableStock": 18,
        "LeadTimeInStockDays": 1,
        "LeadTimeOutOfStockDays": 7,
        "Description": "Màn hình cao cấp chuẩn màu 98% DCI-P3 cho thiết kế đồ họa và lập trình."
    },
    {
        "SKU": "UPS-APC-SMT2200",
        "ProductName": "Bộ lưu điện APC Smart-UPS 2200VA LCD 230V (SMT2200I)",
        "Category": "Thiết bị nguồn & Phụ trợ",
        "UnitPrice": 24500000,
        "Unit": "Chiếc",
        "WarrantyMonths": 24,
        "AvailableStock": 3,
        "LeadTimeInStockDays": 2,
        "LeadTimeOutOfStockDays": 14,
        "Description": "Bộ lưu điện chuẩn Sine wave cho tủ Rack máy chủ và phòng Server."
    },
    {
        "SKU": "SVC-INSTALL-SRV",
        "ProductName": "Dịch vụ Triển khai & Cấu hình Máy chủ, Hệ điều hành Windows Server / Linux, Hyper-V",
        "Category": "Dịch vụ công nghệ",
        "UnitPrice": 8000000,
        "Unit": "Gói",
        "WarrantyMonths": 12,
        "AvailableStock": 999,
        "LeadTimeInStockDays": 1,
        "LeadTimeOutOfStockDays": 2,
        "Description": "Bao gồm lắp đặt phần cứng, cấu hình RAID, OS, Active Directory và phân quyền."
    },
    {
        "SKU": "SVC-NETWORK-SETUP",
        "ProductName": "Dịch vụ Khảo sát, Lắp đặt và Cấu hình Mạng LAN / VLAN / VPN Doanh nghiệp",
        "Category": "Dịch vụ công nghệ",
        "UnitPrice": 6500000,
        "Unit": "Gói",
        "WarrantyMonths": 12,
        "AvailableStock": 999,
        "LeadTimeInStockDays": 1,
        "LeadTimeOutOfStockDays": 2,
        "Description": "Cấu hình chia VLAN phòng ban, định tuyến, firewall bảo mật và VPN kết nối từ xa."
    },
    {
        "SKU": "LIC-M365-BUS-STD",
        "ProductName": "Bản quyền Microsoft 365 Business Standard (Thuê bao 1 năm / User)",
        "Category": "Phần mềm & Bản quyền",
        "UnitPrice": 3450000,
        "Unit": "User/Năm",
        "WarrantyMonths": 12,
        "AvailableStock": 999,
        "LeadTimeInStockDays": 1,
        "LeadTimeOutOfStockDays": 1,
        "Description": "Ứng dụng Office cài đặt trên 5 thiết bị, Exchange Online 50GB, Teams, OneDrive 1TB."
    },
    {
        "SKU": "LIC-WIN-SRV-2022",
        "ProductName": "Bản quyền Windows Server 2022 Standard 16 Core (Vĩnh viễn)",
        "Category": "Phần mềm & Bản quyền",
        "UnitPrice": 21500000,
        "Unit": "License",
        "WarrantyMonths": 12,
        "AvailableStock": 999,
        "LeadTimeInStockDays": 1,
        "LeadTimeOutOfStockDays": 1,
        "Description": "Bản quyền hợp lệ cho máy chủ vật lý hỗ trợ tối đa 2 máy ảo ảo hóa."
    }
]

# 2. Sales Team (6 Sales reps as stated in the prompt)
sales_team = [
    {
        "StaffID": "NV01",
        "FullName": "Nguyễn Văn An",
        "Role": "Nhân viên Kinh doanh",
        "Specialty": "Máy chủ, Lưu trữ & Hạ tầng CNTT",
        "Email": "an.nguyen@minhan.vn",
        "Phone": "0912.345.001",
        "ActiveDeals": 12
    },
    {
        "StaffID": "NV02",
        "FullName": "Trần Thị Bích",
        "Role": "Nhân viên Kinh doanh",
        "Specialty": "Phần mềm, Bản quyền & Cloud",
        "Email": "bich.tran@minhan.vn",
        "Phone": "0912.345.002",
        "ActiveDeals": 9
    },
    {
        "StaffID": "NV03",
        "FullName": "Lê Hoàng Cường",
        "Role": "Nhân viên Kinh doanh",
        "Specialty": "Thiết bị mạng & Bảo mật",
        "Email": "cuong.le@minhan.vn",
        "Phone": "0912.345.003",
        "ActiveDeals": 15
    },
    {
        "StaffID": "NV04",
        "FullName": "Phạm Thu Dung",
        "Role": "Nhân viên Kinh doanh",
        "Specialty": "Laptop, Máy tính để bàn & Màn hình",
        "Email": "dung.pham@minhan.vn",
        "Phone": "0912.345.004",
        "ActiveDeals": 8
    },
    {
        "StaffID": "NV05",
        "FullName": "Vũ Đức Giang",
        "Role": "Nhân viên Kinh doanh",
        "Specialty": "Dịch vụ Triển khai & Tích hợp hệ thống",
        "Email": "giang.vu@minhan.vn",
        "Phone": "0912.345.005",
        "ActiveDeals": 11
    },
    {
        "StaffID": "NV06",
        "FullName": "Hoàng Mai Hương",
        "Role": "Nhân viên Kinh doanh",
        "Specialty": "Khách hàng Doanh nghiệp Tổng hợp (SMB)",
        "Email": "huong.hoang@minhan.vn",
        "Phone": "0912.345.006",
        "ActiveDeals": 7
    }
]

# 3. Discount and Approval Policy
policies = [
    {
        "ApprovalLevel": "Cấp 1 - Nhân viên Kinh doanh (NVKD)",
        "MaxDiscountPercent": 5.0,
        "MaxOrderValueVND": 100000000,
        "LeadTimePolicy": "Tuân thủ SLA tiêu chuẩn của kho/vận hành",
        "DecisionType": "Tự động phê duyệt",
        "Note": "NVKD được chủ động báo giá và chiết khấu tối đa 5% với các đơn hàng dưới 100 triệu."
    },
    {
        "ApprovalLevel": "Cấp 2 - Trưởng phòng Kinh doanh",
        "MaxDiscountPercent": 12.0,
        "MaxOrderValueVND": 500000000,
        "LeadTimePolicy": "Chấp nhận phê duyệt rút ngắn SLA sau khi xác nhận với Vận hành",
        "DecisionType": "Cần Trưởng phòng duyệt",
        "Note": "Áp dụng khi chiết khấu từ trên 5% đến 12%, đơn hàng từ 100tr - 500tr, hoặc cam kết giao gấp ngoài SLA."
    },
    {
        "ApprovalLevel": "Cấp 3 - Ban Giám đốc",
        "MaxDiscountPercent": 25.0,
        "MaxOrderValueVND": 9999999999,
        "LeadTimePolicy": "Dự án chiến lược đặc thù",
        "DecisionType": "Cần Ban Giám đốc duyệt",
        "Note": "Áp dụng cho các dự án lớn trên 500 triệu hoặc chiết khấu trên 12%."
    }
]

# Write to Excel
excel_path = "data/minhan_catalog.xlsx"
with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    pd.DataFrame(products).to_excel(writer, sheet_name="Bang_Gia_Ton_Kho", index=False)
    pd.DataFrame(sales_team).to_excel(writer, sheet_name="Nhan_Vien_Kinh_Doanh", index=False)
    pd.DataFrame(policies).to_excel(writer, sheet_name="Chinh_Sach_Duyet", index=False)

# Export individual CSVs for users who prefer CSV upload
pd.DataFrame(products).to_csv("data/bang_gia_ton_kho.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(sales_team).to_csv("data/nhan_vien_kinh_doanh.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(policies).to_csv("data/chinh_sach_duyet.csv", index=False, encoding="utf-8-sig")

# 4. Realistic sample customer requests for testing and demo
sample_requests = [
    {
        "id": "REQ-001",
        "title": "Mẫu 1: Yêu cầu chuẩn - Đầy đủ thông tin, trong thẩm quyền NVKD",
        "type": "Standard",
        "customer_name": "Công ty Cổ phần Công nghệ DigiTech",
        "contact_person": "Anh Trần Minh Tuấn (Trưởng phòng IT)",
        "email": "tuan.tm@digitech.vn",
        "phone": "0988.123.456",
        "raw_text": """Kính gửi Bộ phận Kinh doanh Công ty Minh An,

Công ty chúng tôi (DigiTech JSC) đang cần mở rộng văn phòng và cần báo giá gấp các hạng mục thiết bị sau:
1. 05 chiếc Laptop Lenovo ThinkPad T14 Gen 4 cho nhân viên lập trình.
2. 05 chiếc Màn hình Dell UltraSharp U2724D 27 Inch.
3. 01 bộ Switch Cisco Catalyst C9200L-24P-4G-E.
4. Gói dịch vụ khảo sát và cấu hình mạng LAN / VLAN văn phòng.

Ngân sách dự kiến của chúng tôi cho đợt này là khoảng 220.000.000 VNĐ.
Thời hạn triển khai mong muốn: Trong vòng 7 ngày làm việc kể từ ngày ký hợp đồng.
Chúng tôi đề nghị mức chiết khấu 4% cho đơn hàng này vì là khách hàng thân thiết.

Nhờ Minh An gửi sớm báo giá chi tiết và dự thảo hợp đồng.
Trân trọng,
Trần Minh Tuấn - Trưởng phòng IT DigiTech
SĐT: 0988.123.456""",
        "expected_flow": "Đầy đủ thông tin -> Trong thẩm quyền NVKD -> Đề xuất báo giá"
    },
    {
        "id": "REQ-002",
        "title": "Mẫu 2: Thiếu thông tin nghiêm trọng (Thiếu số lượng & Ngân sách) -> Cần hỏi lại KH",
        "type": "Missing_Info",
        "customer_name": "Công ty TNHH May Mặc Hưng Phát",
        "contact_person": "Chị Lê Thu Hằng (Phòng Mua hàng)",
        "email": "hang.lt@hungphattextile.com",
        "phone": "0903.555.789",
        "raw_text": """Chào Minh An,

Bên mình cần mua một số máy chủ Dell PowerEdge R750 và một vài bộ máy tính cho phòng kế toán dùng phần mềm MISA. Ngoài ra cần gói cài đặt máy chủ luôn.
Giao hàng tại kho Hưng Yên trước ngày 25 tháng này nhé.
Cho mình xin báo giá và chiết khấu tốt nhất nhé!

Cảm ơn,
Hằng - May Mặc Hưng Phát""",
        "expected_flow": "Thiếu thông tin -> Nhánh 'Yêu cầu KH làm rõ/bổ sung' -> Tự động soạn email hỏi lại"
    },
    {
        "id": "REQ-003",
        "title": "Mẫu 3: Chiết khấu vượt quyền (12%) & Giao hàng gấp (2 ngày) -> Trưởng phòng duyệt",
        "type": "Exceed_Authority",
        "customer_name": "Tập đoàn Xây dựng Nam Long",
        "contact_person": "Ông Nguyễn Hoàng Quân (Giám đốc Dự án)",
        "email": "quan.nh@namlonggroup.vn",
        "phone": "0918.777.888",
        "raw_text": """Gửi Công ty Minh An,

Chúng tôi đang triển khai dự án Site Office tại Quận 7 và cần trang bị ngay thiết bị mạng:
1. 02 chiếc Switch Aruba Instant On 1930 48G.
2. 06 bộ WiFi Aruba Instant On AP22.
3. 02 bộ Lưu điện APC Smart-UPS 2200VA.
4. Gói cấu hình hệ thống mạng LAN / VPN.

Thời hạn hoàn thành: Cần bàn giao và lắp đặt trong vòng 2 ngày làm việc (yêu cầu tiến độ cực kỳ khẩn cấp).
Đề xuất mức chiết khấu thương mại: 10% trên tổng giá niêm yết.
Ngân sách đã được phê duyệt tối đa: 110.000.000 VNĐ.

Nếu Minh An cam kết được thời gian giao hàng trong 2 ngày và đồng ý mức chiết khấu trên, chúng tôi sẽ tiến hành ký ngay trong ngày mai.
Trân trọng,
Nguyễn Hoàng Quân - Nam Long Group""",
        "expected_flow": "Đủ thông tin -> Vượt thẩm quyền (Chiết khấu 10% & Giao khẩn cấp) -> Trình Trưởng phòng duyệt"
    },
    {
        "id": "REQ-004",
        "title": "Mẫu 4: Yêu cầu số lượng vượt Tồn khả dụng -> Cảnh báo Lead time & Vận hành",
        "type": "Out_Of_Stock_Warning",
        "customer_name": "Trường Quốc tế Song ngữ Wellspring",
        "contact_person": "Thầy Đỗ Quang Minh (Phụ trách Hạ tầng)",
        "email": "minh.dq@wellspring-edu.vn",
        "phone": "0977.889.900",
        "raw_text": """Kính gửi Minh An,

Nhà trường cần chuẩn bị phòng thực hành tin học mới cho năm học tới với danh mục:
1. 08 chiếc Máy chủ Dell PowerEdge R750 (cần cài đặt Hyper-V).
2. 08 Gói Dịch vụ Triển khai Máy chủ.
3. 10 chiếc Màn hình đồ họa Dell UltraSharp U2724D.

Thời gian nhà trường yêu cầu hoàn thành nghiệm thu: trong 5 ngày tới.
Ngân sách dự kiến: 800.000.000 VNĐ.
Đề nghị mức chiết khấu: 6%.

Mong nhận được phản hồi sớm từ quý công ty.
Đỗ Quang Minh - Ban CNTT Trường Wellspring""",
        "expected_flow": "Đủ thông tin -> Cảnh báo Tồn kho chỉ có 4 máy (thiếu 4 máy), Lead-time nhập mới 14 ngày (vi phạm 5 ngày) -> Cần phối hợp Vận hành & Trưởng phòng duyệt"
    }
]

with open("data/sample_requests.json", "w", encoding="utf-8") as f:
    json.dump(sample_requests, f, ensure_ascii=False, indent=2)

print("Generated sample Excel, CSVs, and sample customer requests successfully!")
