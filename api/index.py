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
        """Renders the official full-screen seamless Streamlit dashboard on Vercel."""
        return """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Trung tâm Vận hành Bán hàng AI - Minh An Company</title>
    <link rel="icon" type="image/x-icon" href="https://streamlit.io/images/brand/streamlit-mark-color.png">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        html, body {
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #F8FAFC;
        }
        #app-frame {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
            outline: none;
            margin: 0;
            padding: 0;
            z-index: 10;
        }
        .loader-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #F8FAFC;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 5;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #1E3A8A;
        }
        .spinner {
            width: 44px;
            height: 44px;
            border: 4px solid #E2E8F0;
            border-top: 4px solid #2563EB;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-bottom: 16px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="loader-overlay" id="loader">
        <div class="spinner"></div>
        <div style="font-weight: 700; font-size: 16px; margin-bottom: 6px;">MINH AN COMPANY • AI SALES CENTER</div>
        <div style="font-size: 13px; color: #64748B;">Đang kết nối trung tâm vận hành bán hàng...</div>
    </div>
    
    <iframe
        id="app-frame"
        src="https://minhanaisales.streamlit.app/?embed=true"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen
        onload="document.getElementById('loader').style.display='none';">
    </iframe>
</body>
</html>"""


# Global exports for Vercel Python runtime discovery
app = handler
application = handler
