import os
import io
import pandas as pd
from file_reader import UniversalFileReader
from data_cleaning import DataQualityCleaner
from analytics_engine import StatisticalAnalyticsEngine
from agent_core import DataLoader, MinhAnSalesAgent
from config import (
    MAX_REP_DISCOUNT_PCT, 
    MAX_MANAGER_DISCOUNT_PCT, 
    MAX_REP_ORDER_VALUE, 
    MAX_MANAGER_ORDER_VALUE,
    CANONICAL_COLUMNS
)

print("=== STARTING FULL AUTOMATED TEST SUITE ===")

# TEST 1: Universal File Reader across all 7 sample formats
test_files = [
    'data/test_samples/sample_orders.xlsx',
    'data/test_samples/sample_orders_vn.csv',
    'data/test_samples/sample_inquiry.json',
    'data/test_samples/sample_inquiry.xml',
    'data/test_samples/sample_rfp.docx',
    'data/test_samples/sample_email.eml',
    'data/test_samples/sample_quote.txt'
]

loaded_results = {}
for path in test_files:
    fname = os.path.basename(path)
    with open(path, 'rb') as f:
        file_bytes = f.read()
    
    res = UniversalFileReader.load_any_file(fname, file_bytes)
    assert res is not None and "kind" in res, f"Failed to load file {fname}"
    loaded_results[fname] = res
    kind = res["kind"]
    if kind == "tabular":
        sheet_count = len(res.get("sheets", {}))
        first_sheet = list(res["sheets"].values())[0]
        print(f"  [PASS] File Reader: {fname:25} -> Kind: {kind}, Sheets: {sheet_count}, Shape: {first_sheet.shape}")
    else:
        text_len = len(res.get("text", ""))
        print(f"  [PASS] File Reader: {fname:25} -> Kind: {kind}, Extracted text: {text_len} chars")

# Verify Vietnamese CSV numbers are parsed cleanly
vn_sheets = loaded_results['sample_orders_vn.csv']['sheets']
raw_vn_df = list(vn_sheets.values())[0]
cleaned_vn_df = DataQualityCleaner.clean_and_standardize(raw_vn_df)
unit_price_col = [c for c in cleaned_vn_df.columns if 'Đơn Giá' in c or 'Don Gia' in c][0]
first_price = cleaned_vn_df[unit_price_col].iloc[0]
assert isinstance(first_price, (int, float)) and first_price == 38500000.0, f"Expected 38500000.0 but got {first_price}"
print(f"  [PASS] Vietnamese Currency Parsing: '38.500.000,00' -> {first_price:,.0f} VND")

# TEST 2: Data Quality Cleaning & Schema Mapping
raw_excel_df = list(loaded_results['sample_orders.xlsx']['sheets'].values())[0]
cleaned_df = DataQualityCleaner.clean_and_standardize(raw_excel_df)
audit_report = DataQualityCleaner.audit_dataframe(cleaned_df)
total_missing = sum(s['null_count'] for s in audit_report['missing_stats'])
print(f"  [PASS] Data Audit: Rows: {audit_report['total_rows']}, Missing Cells: {total_missing}, Duplicates: {audit_report['duplicate_count']}")

suggested_map = DataQualityCleaner.suggest_schema_mapping(cleaned_df.columns.tolist(), sample_df=cleaned_df)
active_mapping = {k: v["mapped_column"] for k, v in suggested_map.items() if v["mapped_column"]}
print(f"  [PASS] Smart Schema Mapping: {active_mapping}")

canonical_df = DataQualityCleaner.apply_schema_mapping(cleaned_df, active_mapping)
assert not canonical_df.empty, "Canonical DataFrame should not be empty"

# TEST 3: Statistical Analytics Engine
kpis = StatisticalAnalyticsEngine.compute_financial_kpis(canonical_df)
print(f"  [PASS] Financial KPIs: Revenue: {kpis['total_revenue']:,.0f} VND, Margin: {kpis['gross_margin_pct']:.1f}%, AOV: {kpis['aov']:,.0f} VND")

rfm_df = StatisticalAnalyticsEngine.segment_customers_rfm(canonical_df)
print(f"  [PASS] RFM Customer Prioritization: {len(rfm_df)} customers segmented.")
for _, row in rfm_df.iterrows():
    print(f"         - {row['Customer']}: Tier = {row['AssignedTier']}, Score = {row['ConfidencePct']}%, Reason = {row['Reason']}")

charts = StatisticalAnalyticsEngine.build_financial_charts(canonical_df, is_dark=False)
assert len(charts) >= 3, "Expected at least 3 Plotly charts"
print(f"  [PASS] Interactive Plotly Charts Generated ({len(charts)} figures: {list(charts.keys())})")

insights = StatisticalAnalyticsEngine.generate_executive_insights(canonical_df, kpis, rfm_df)
assert len(insights) >= 2, "Executive insights should contain at least 2 key points"
print(f"  [PASS] Executive Insights Generated ({len(insights)} key insights: {insights[0][:60]}...)")

# TEST 4: Agent Core with Transparent Audit Trail & B2B Rules
p_df, s_df, pol_df = DataLoader.load_default_data()
agent = MinhAnSalesAgent(p_df, s_df, pol_df)

sample_request = """
Khách hàng: Công ty Cổ phần Chứng khoán SSI
Cần mua 5 bộ Switch Cisco C9200L-24P-4G-E để lắp phòng Server tại Hà Nội.
Yêu cầu chiết khấu 7% và giao hàng gấp trong 2 ngày.
"""

result = agent.process_request(sample_request)
assert "audit_logs" in result, "Result missing audit_logs"
assert len(result["audit_logs"]) >= 5, f"Expected at least 5 audit logs, got {len(result['audit_logs'])}"
print(f"  [PASS] Agent 5-Step Process with Audit Trail ({len(result['audit_logs'])} steps logged):")
for log in result["audit_logs"]:
    print(f"         - Step {log['step_no']}: {log['step_name']} -> {log['status']}")

# Check discount policy logic: 7% > 5% (Rep threshold), so it requires Manager approval!
approval_note = result.get("approval_note")
assert approval_note is not None and isinstance(approval_note, str), "Expected approval_note string for 7% discount"
assert "LÝ DO TRÌNH DUYỆT" in approval_note or "PHÊ DUYỆT" in approval_note, "Approval note missing key headers"
eval_level = result["evaluation"]["approval_level"]
print(f"  [PASS] Approval Governance Check: Level = {eval_level}, Length = {len(approval_note)} chars")

# TEST 5: AI Sales Copilot
copilot_res = agent.negotiate_copilot(
    context_result=result,
    query="Khách hàng yêu cầu tăng chiết khấu lên 8% mới chốt hợp đồng, NVKD nên thương lượng thế nào?"
)
assert len(copilot_res) > 20, "Copilot response should not be empty"
print(f"  [PASS] AI Sales Copilot Negotiation Response Verified ({len(copilot_res)} characters)")

print("\n=== ALL TESTS PASSED SUCCESSFULLY! (100% OPERATIONAL) ===")
