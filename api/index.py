"""
Minh An Company - AI Sales Operations Center (Serverless Entrypoint for Vercel)
Handles HTTP requests, serverless API endpoints, and provides a standalone interactive UI.
Compatible with Vercel Python Runtime (@vercel/python).
"""

import sys
import os
import json
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure project root is in Python module search path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from agent_core import DataLoader, MinhAnSalesAgent
import config

# Global cached agent instance for warm serverless execution
_CACHED_AGENT = None
_CACHED_SAMPLES = None


def get_agent():
    """Initializes and caches the MinhAnSalesAgent instance for serverless invocations."""
    global _CACHED_AGENT
    if _CACHED_AGENT is None:
        p_df, s_df, pol_df = DataLoader.load_default_data()
        _CACHED_AGENT = MinhAnSalesAgent(p_df, s_df, pol_df)
    return _CACHED_AGENT


def get_samples():
    """Loads sample customer requests safely."""
    global _CACHED_SAMPLES
    if _CACHED_SAMPLES is None:
        samples_path = os.path.join(ROOT_DIR, "data", "sample_requests.json")
        try:
            with open(samples_path, "r", encoding="utf-8") as f:
                _CACHED_SAMPLES = json.load(f)
        except Exception:
            _CACHED_SAMPLES = []
    return _CACHED_SAMPLES


class handler(BaseHTTPRequestHandler):
    """
    Standard Vercel Python Serverless Request Handler.
    Supports GET (Health check, Catalog, Web UI) and POST (AI Request Processing).
    """

    def _send_json(self, status_code: int, data: dict):
        response_bytes = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def _send_html(self, status_code: int, html_content: str):
        response_bytes = html_content.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Routes GET requests to API endpoints or the interactive web page."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ["/api/health", "/health"]:
            agent = get_agent()
            api_status = agent.get_api_status()
            self._send_json(200, {
                "status": "healthy",
                "app": "Minh An AI Sales Operations Center",
                "version": "4.0.0",
                "platform": "Vercel Serverless Function",
                "gemini_api": api_status,
                "catalog_items": len(agent.products_df),
                "sales_reps": len(agent.sales_team)
            })
            return

        if path in ["/api/samples", "/samples"]:
            self._send_json(200, get_samples())
            return

        if path in ["/api/catalog", "/catalog"]:
            agent = get_agent()
            catalog = agent.products_df.to_dict(orient="records")
            self._send_json(200, catalog)
            return

        # Default: Render the Serverless Web Dashboard
        samples = get_samples()
        html_page = self._render_web_ui(samples)
        self._send_html(200, html_page)

    def do_POST(self):
        """Processes customer inquiries and returns automated B2B proposals."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ["/api/process", "/api/evaluate", "/process"]:
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8")
                req_data = json.loads(body) if body else {}

                raw_text = req_data.get("text", "").strip()
                custom_opp_id = req_data.get("opp_id", None)

                if not raw_text:
                    self._send_json(400, {"error": "Missing 'text' field in request payload."})
                    return

                agent = get_agent()
                result = agent.process_request(raw_text, custom_opp_id=custom_opp_id)
                self._send_json(200, result)
            except Exception as e:
                self._send_json(500, {
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
            return

        self._send_json(404, {"error": "Endpoint not found."})

    def _render_web_ui(self, samples: list) -> str:
        """Constructs an elegant, standalone single-page web UI for Vercel deployment."""
        samples_json = json.dumps(samples, ensure_ascii=False)
        return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trung tâm Vận hành Bán hàng AI - Minh An Company</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #2563EB;
            --primary-dark: #1E40AF;
            --bg-page: #F8FAFC;
            --card-bg: #FFFFFF;
            --text-main: #0F172A;
            --text-muted: #64748B;
            --border: #E2E8F0;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }}
        body {{ background-color: var(--bg-page); color: var(--text-main); min-height: 100vh; padding: 24px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%); color: white; padding: 28px 32px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25); }}
        .header h1 {{ font-size: 24px; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.5px; }}
        .header p {{ font-size: 14px; opacity: 0.9; }}
        .badge-bar {{ display: flex; gap: 10px; margin-top: 14px; flex-wrap: wrap; }}
        .badge {{ background: rgba(255, 255, 255, 0.2); padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }}
        .card {{ background: var(--card-bg); border-radius: 14px; border: 1px solid var(--border); padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); }}
        .card-title {{ font-size: 16px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; color: var(--primary-dark); }}
        label {{ font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 8px; display: block; }}
        select, textarea {{ width: 100%; padding: 12px; border-radius: 10px; border: 1px solid var(--border); font-size: 14px; margin-bottom: 16px; outline: none; transition: 0.2s; }}
        select:focus, textarea:focus {{ border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }}
        textarea {{ height: 160px; resize: vertical; line-height: 1.5; }}
        .btn-primary {{ background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color: white; padding: 12px 24px; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; width: 100%; transition: 0.2s; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25); }}
        .btn-primary:hover {{ opacity: 0.95; transform: translateY(-1px); }}
        .stepper {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; background: white; padding: 16px 20px; border-radius: 12px; border: 1px solid var(--border); overflow-x: auto; }}
        .step-item {{ text-align: center; min-width: 100px; }}
        .step-circle {{ width: 32px; height: 32px; border-radius: 50%; background: #E2E8F0; color: #64748B; font-weight: 700; font-size: 13px; display: flex; align-items: center; justify-content: center; margin: 0 auto 6px; }}
        .step-circle.active {{ background: #2563EB; color: white; }}
        .step-circle.done {{ background: #10B981; color: white; }}
        .step-title {{ font-size: 11px; font-weight: 700; color: var(--text-main); }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }}
        .info-box {{ background: #F8FAFC; border: 1px solid var(--border); padding: 14px; border-radius: 10px; }}
        .info-label {{ font-size: 12px; color: var(--text-muted); font-weight: 600; margin-bottom: 4px; }}
        .info-val {{ font-size: 15px; font-weight: 700; color: var(--text-main); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ background: #F1F5F9; font-weight: 700; color: var(--text-muted); }}
        .proposal-box {{ background: #F8FAFC; border-left: 4px solid var(--primary); padding: 16px; border-radius: 8px; font-size: 13px; line-height: 1.6; white-space: pre-wrap; }}
        .hidden {{ display: none; }}
        .footer {{ text-align: center; font-size: 12px; color: var(--text-muted); margin-top: 32px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 Trung tâm Vận hành Bán hàng AI - Minh An Company</h1>
            <p>Hệ thống tự động thẩm định quy trình B2B 6 bước, đối soát SKU, kiểm tra tồn kho & đề xuất báo giá.</p>
            <div class="badge-bar">
                <span class="badge">🚀 Vercel Serverless: ONLINE</span>
                <span class="badge">🧠 Multi-format Ingestion: SẴN SÀNG</span>
                <span class="badge">⚡ Quy trình B2B: B1 ➔ B6</span>
            </div>
        </div>

        <div class="card">
            <div class="card-title">📝 Tiếp nhận Yêu cầu từ Khách hàng</div>
            <label>Chọn yêu cầu mẫu thực tế của Minh An:</label>
            <select id="sampleSelect" onchange="loadSample()">
                <option value="">-- Chọn yêu cầu mẫu hoặc tự soạn thảo bên dưới --</option>
            </select>

            <label>Nội dung yêu cầu từ khách hàng doanh nghiệp:</label>
            <textarea id="requestText" placeholder="Dán email, tin nhắn hoặc biểu mẫu yêu cầu của khách hàng vào đây..."></textarea>

            <button class="btn-primary" onclick="processRequest()">⚡ Thẩm định Yêu cầu & Lập Đề xuất Báo giá</button>
        </div>

        <div id="resultCard" class="card hidden">
            <div class="card-title">📊 Kết quả Thẩm định & Hồ sơ Cơ hội B2B</div>
            
            <div id="stepper" class="stepper">
                <div class="step-item"><div class="step-circle done">✓</div><div class="step-title">1. Tiếp nhận</div></div>
                <div class="step-item"><div class="step-circle done">✓</div><div class="step-title">2. Phân loại & TT</div></div>
                <div class="step-item"><div class="step-circle done">✓</div><div class="step-title">3. Hồ sơ & NVKD</div></div>
                <div class="step-item"><div class="step-circle done">✓</div><div class="step-title">4. Tồn kho & Giá</div></div>
                <div class="step-item"><div class="step-circle done">✓</div><div class="step-title">5. Lập Báo giá</div></div>
                <div class="step-item"><div class="step-circle done">✓</div><div class="step-title">6. Cập nhật</div></div>
            </div>

            <div class="grid-2">
                <div class="info-box"><div class="info-label">Mã Hồ sơ Cơ hội</div><div id="resOppId" class="info-val">—</div></div>
                <div class="info-box"><div class="info-label">Khách hàng Doanh nghiệp</div><div id="resCompany" class="info-val">—</div></div>
                <div class="info-box"><div class="info-label">NVKD Phụ trách</div><div id="resRep" class="info-val">—</div></div>
                <div class="info-box"><div class="info-label">Cấp Phê duyệt</div><div id="resApproval" class="info-val">—</div></div>
                <div class="info-box"><div class="info-label">Tổng Doanh thu Báo giá</div><div id="resTotal" class="info-val" style="color:var(--primary);">—</div></div>
                <div class="info-box"><div class="info-label">Thời gian Giao hàng Khả thi</div><div id="resLeadtime" class="info-val">—</div></div>
            </div>

            <div style="margin-top:20px;">
                <label>Chi tiết Danh mục Hạng mục & Đối soát Tồn kho:</label>
                <table>
                    <thead>
                        <tr>
                            <th>Mã SKU</th>
                            <th>Hạng mục Thiết bị</th>
                            <th>Số lượng</th>
                            <th>Tồn khả dụng</th>
                            <th>Đơn giá (VNĐ)</th>
                            <th>Thành tiền (VNĐ)</th>
                        </tr>
                    </thead>
                    <tbody id="itemsTableBody"></tbody>
                </table>
            </div>

            <div style="margin-top:24px;">
                <label>Dự thảo Đề xuất Báo giá gửi Khách hàng:</label>
                <div id="proposalBox" class="proposal-box"></div>
            </div>
        </div>

        <div class="footer">
            <p>💡 <strong>Gợi ý:</strong> Để sử dụng đầy đủ Dashboard đa tab phân tích đồ thị tương tác Plotly & xử lý tệp hàng loạt 20.000 dòng, bạn có thể triển khai lên <strong>Streamlit Community Cloud</strong> hoặc chạy trên máy chủ nội bộ với lệnh: <code>streamlit run app.py</code></p>
            <p style="margin-top:8px;">CÔNG TY CỔ PHẦN CÔNG NGHỆ MINH AN • HỆ THỐNG VẬN HÀNH BÁN HÀNG AI ENTERPRISE</p>
        </div>
    </div>

    <script>
        const samples = {samples_json};
        const sampleSelect = document.getElementById('sampleSelect');
        const requestText = document.getElementById('requestText');

        samples.forEach((s, idx) => {{
            const opt = document.createElement('option');
            opt.value = idx;
            opt.textContent = s.id + ': ' + s.title;
            sampleSelect.appendChild(opt);
        }});

        function loadSample() {{
            const idx = sampleSelect.value;
            if (idx !== "") {{
                requestText.value = samples[idx].raw_text;
            }}
        }}

        // Preload sample 1
        if (samples.length > 0) {{
            sampleSelect.value = "0";
            loadSample();
        }}

        async function processRequest() {{
            const text = requestText.value.trim();
            if (!text) {{ alert('Vui lòng nhập nội dung yêu cầu.'); return; }}
            
            const btn = document.querySelector('.btn-primary');
            btn.textContent = '⏳ Đang thẩm định và lập báo giá...';
            btn.disabled = true;

            try {{
                const resp = await fetch('/api/process', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ text: text }})
                }});
                const data = await resp.json();
                renderResult(data);
            }} catch (err) {{
                alert('Lỗi xử lý yêu cầu: ' + err.message);
            }} finally {{
                btn.textContent = '⚡ Thẩm định Yêu cầu & Lập Đề xuất Báo giá';
                btn.disabled = false;
            }}
        }}

        function renderResult(data) {{
            const resCard = document.getElementById('resultCard');
            resCard.classList.remove('hidden');

            document.getElementById('resOppId').textContent = data.opportunity_id || 'OPP-001';
            document.getElementById('resCompany').textContent = (data.parsed_request || {{}}).company_name || 'Khách hàng liên hệ';
            document.getElementById('resRep').textContent = (data.assigned_sales_rep || {{}}).FullName || 'Chưa gán';
            document.getElementById('resApproval').textContent = (data.evaluation || {{}}).approval_level || data.workflow_step || '—';
            
            const total = (data.evaluation || {{}}).total_final_amount || 0;
            document.getElementById('resTotal').textContent = new Intl.NumberFormat('vi-VN').format(total) + ' đ';
            
            const leadtime = (data.evaluation || {{}}).max_lead_time_days || 2;
            document.getElementById('resLeadtime').textContent = leadtime + ' ngày (' + (leadtime <= 2 ? 'Sẵn kho' : 'Nhập kho bổ sung') + ')';

            // Items table
            const tbody = document.getElementById('itemsTableBody');
            tbody.innerHTML = '';
            const items = (data.evaluation || {{}}).items || [];
            if (items.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#64748B;">Không có hạng mục xác định hoặc cần khách hàng làm rõ</td></tr>';
            }} else {{
                items.forEach(it => {{
                    const p = it.product || {{}};
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${{p.SKU || '—'}}</strong></td>
                        <td>${{it.requested_item || p.ProductName || '—'}}</td>
                        <td>${{it.quantity || 1}}</td>
                        <td>${{p.AvailableStock || 0}}</td>
                        <td>${{new Intl.NumberFormat('vi-VN').format(it.unit_price || 0)}} đ</td>
                        <td><strong>${{new Intl.NumberFormat('vi-VN').format(it.total_price || 0)}} đ</strong></td>
                    `;
                    tbody.appendChild(tr);
                }});
            }}

            // Proposal
            const pBox = document.getElementById('proposalBox');
            if (data.status === 'WAIT_CLARIFICATION' || !data.parsed_request?.is_sufficient) {{
                pBox.textContent = data.clarification_draft || 'Yêu cầu cần làm rõ thêm số lượng hoặc thông tin thiết bị.';
            }} else {{
                pBox.textContent = data.proposal_draft || 'Đã tạo bản dự thảo đề xuất báo giá chuẩn.';
            }}

            resCard.scrollIntoView({{ behavior: 'smooth' }});
        }}
    </script>
</body>
</html>"""


# Global exports for Vercel Python runtime discovery
app = handler
application = handler
