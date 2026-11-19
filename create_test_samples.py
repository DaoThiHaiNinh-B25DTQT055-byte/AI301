import os
import json
import pandas as pd
from docx import Document

os.makedirs('data/test_samples', exist_ok=True)

# 1. Multi-sheet Excel
orders_data = {
    'Mã_Đơn': ['ORD-001', 'ORD-002', 'ORD-003', 'ORD-004', 'ORD-005'],
    'Khách_Hàng': ['FPT IS', 'VNG Corp', 'Viettel Post', 'CMC Telecom', 'Tiki Tech'],
    'Sản_Phẩm': ['Cisco C9200L-24P-4G-E', 'FortiGate-60F', 'Aruba AP-505', 'Cisco C9300-24T-A', 'FortiGate-100F'],
    'Số_Lượng': [4, 10, 25, 2, 3],
    'Đơn_Giá': [38500000, 16800000, 8900000, 89000000, 48000000],
    'Chiết_Khấu_%': [5.0, 7.5, 4.0, 3.0, 8.0],
    'Doanh_Thu': [146300000, 155400000, 213600000, 172660000, 132480000],
    'Lợi_Nhuận': [23408000, 31080000, 42720000, 34532000, 23846400],
    'Ngày_Tạo': ['2026-11-01', '2026-11-05', '2026-11-10', '2026-11-12', '2026-11-15']
}
inv_data = {
    'Mã_SP': ['C9200L-24P', 'FG-60F', 'AP-505', 'C9300-24T', 'FG-100F'],
    'Tồn_Kho_Hà_Nội': [15, 28, 50, 6, 12],
    'Tồn_Kho_TP_HCM': [10, 14, 30, 4, 8]
}

with pd.ExcelWriter('data/test_samples/sample_orders.xlsx', engine='openpyxl') as writer:
    pd.DataFrame(orders_data).to_excel(writer, sheet_name='Danh_Sách_Đơn_Hàng', index=False)
    pd.DataFrame(inv_data).to_excel(writer, sheet_name='Tồn_Kho_Kha_Dung', index=False)

# 2. Vietnamese CSV with dot thousands and comma decimals
vn_csv_content = """Mã Khách Hàng;Tên Khách Hàng;Mặt Hàng;Số Lượng;Đơn Giá (VNĐ);Chiết Khấu (%);Doanh Số;Ngày Đặt
KH001;Công ty CP Công nghệ Dược phẩm;Cisco C9200L-24P-4G-E;5;38.500.000,00;4,5;183.837.500,00;01/11/2026
KH002;Ngân hàng TMCP Việt Nam Thịnh Vượng;FortiGate-60F;12;16.800.000,00;6,0;189.504.000,00;04/11/2026
KH003;Tập đoàn Bưu chính Viễn thông;Aruba AP-505;30;8.900.000,00;5,0;253.650.000,00;08/11/2026
KH004;Công ty TNHH Phần mềm FPT;Cisco C9300-24T-A;3;89.000.000,00;3,5;257.655.000,00;12/11/2026
KH005;Chuỗi Bán lẻ WinCommerce;FortiGate-100F;4;48.000.000,00;7,0;178.560.000,00;15/11/2026
"""
with open('data/test_samples/sample_orders_vn.csv', 'w', encoding='utf-8-sig') as f:
    f.write(vn_csv_content)

# 3. JSON Orders
json_data = [
    {'customer': 'Techcombank Data Center', 'product': 'Cisco C9300-24T-A', 'quantity': 4, 'unit_price': 89000000, 'discount_pct': 4.0, 'revenue': 341760000, 'profit': 68352000, 'date': '2026-11-02'},
    {'customer': 'Momo Payment Gateway', 'product': 'FortiGate-100F', 'quantity': 6, 'unit_price': 48000000, 'discount_pct': 5.5, 'revenue': 272160000, 'profit': 48988800, 'date': '2026-11-06'},
    {'customer': 'VNG Games Studio', 'product': 'Aruba AP-505', 'quantity': 40, 'unit_price': 8900000, 'discount_pct': 6.0, 'revenue': 334640000, 'profit': 66928000, 'date': '2026-11-14'}
]
with open('data/test_samples/sample_inquiry.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

# 4. XML Orders
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Orders>
    <Order>
        <CustomerID>MB-001</CustomerID>
        <CustomerName>Ngân hàng Quân Đội MB</CustomerName>
        <ProductName>Cisco C9200L-24P-4G-E</ProductName>
        <Quantity>8</Quantity>
        <UnitPrice>38500000</UnitPrice>
        <DiscountPct>5.0</DiscountPct>
        <TotalAmount>292600000</TotalAmount>
        <Date>2026-11-03</Date>
    </Order>
    <Order>
        <CustomerID>TCB-002</CustomerID>
        <CustomerName>Tập đoàn Vingroup</CustomerName>
        <ProductName>FortiGate-60F</ProductName>
        <Quantity>15</Quantity>
        <UnitPrice>16800000</UnitPrice>
        <DiscountPct>7.0</DiscountPct>
        <TotalAmount>234360000</TotalAmount>
        <Date>2026-11-07</Date>
    </Order>
</Orders>"""
with open('data/test_samples/sample_inquiry.xml', 'w', encoding='utf-8') as f:
    f.write(xml_content)

# 5. Word Document (.docx)
doc = Document()
doc.add_heading('YÊU CẦU BÁO GIÁ THIẾT BỊ MẠNG & BẢO MẬT', 0)
doc.add_paragraph('Kính gửi: Công ty TNHH Công nghệ Minh An\nĐơn vị yêu cầu: Tập đoàn Dầu khí Quốc gia Việt Nam\nNgày yêu cầu: 16/11/2026')
table = doc.add_table(rows=1, cols=5)
hdr_cells = table.rows[0].cells
hdr_cells[0].text = 'STT'
hdr_cells[1].text = 'Tên Thiết Bị'
hdr_cells[2].text = 'Số Lượng'
hdr_cells[3].text = 'Địa Điểm Giao Hàng'
hdr_cells[4].text = 'Yêu Cầu Chiết Khấu'

items = [
    ('1', 'Switch Cisco C9200L-24P-4G-E', '6 chiếc', 'Kho Hà Nội', '4.5%'),
    ('2', 'Firewall FortiGate-60F', '4 chiếc', 'Kho TP.HCM', '5.0%'),
    ('3', 'Wifi Aruba AP-505', '20 bộ', 'Kho Hà Nội', '6.0%')
]
for item in items:
    row_cells = table.add_row().cells
    for i in range(5):
        row_cells[i].text = item[i]
doc.save('data/test_samples/sample_rfp.docx')

# 6. Email (.eml)
eml_content = """From: Nguyen Van Hai <hai.nv@vietcombank.com.vn>
To: sales@minhancomputer.vn
Date: Mon, 17 Nov 2026 09:15:30 +0700
Subject: Yêu cầu báo giá khẩn cấp dự án nâng cấp hạ tầng mạng Chi nhánh Sài Gòn
Content-Type: text/plain; charset="utf-8"

Chào Ban Giám đốc và Phòng Kinh doanh Công nghệ Minh An,

Chúng tôi đang triển khai gói thầu mở rộng mạng LAN và Wifi cho tòa nhà chi nhánh Vietcombank tại Quận 1, TP. Hồ Chí Minh.
Rất mong nhận được báo giá tốt nhất cho các mã thiết bị sau:

1. Thiết bị chuyển mạch Cisco C9200L-24P-4G-E: Số lượng 5 chiếc.
2. Thiết bị tường lửa FortiGate-60F: Số lượng 2 chiếc.
3. Bộ phát Wifi Aruba AP-505 (Indoor AP): Số lượng 15 bộ.

Tiến độ bàn giao: Trước ngày 25/11/2026 tại Chi nhánh TP.HCM.
Đề nghị mức chiết khấu thương mại tối thiểu 5% cho dự án khối tài chính ngân hàng.

Trân trọng,
Nguyễn Văn Hải - Trưởng phòng CNTT Vietcombank
"""
with open('data/test_samples/sample_email.eml', 'w', encoding='utf-8') as f:
    f.write(eml_content)

# 7. Text RFQ
txt_content = """PHIẾU YÊU CẦU BÁO GIÁ THIẾT BỊ IT (RFQ-2026-992)
Khách hàng: Công ty Cổ phần Giao Hàng Nhanh (GHN)
Người liên hệ: Trần Tuấn Linh (linh.tt@ghn.vn) - 0912345678
Địa chỉ giao hàng: Tổng kho Tân Bình, TP. Hồ Chí Minh

Nội dung yêu cầu:
Cần cấp gấp 8 con Firewall FortiGate-60F để triển khai bảo mật các bưu cục vệ tinh.
Yêu cầu hàng mới 100%, chính hãng, bảo hành 36 tháng.
Mong muốn chiết khấu 6% do mua số lượng lớn.
Thanh toán: Tạm ứng 30%, 70% sau khi nghiệm thu giao nhận.
"""
with open('data/test_samples/sample_quote.txt', 'w', encoding='utf-8') as f:
    f.write(txt_content)

print('Successfully generated 7 sample test files in data/test_samples/')
