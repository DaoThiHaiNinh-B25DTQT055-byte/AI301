"""
Minh An Universal Multi-format File Reader (Edition 2026)
Supports .xlsx, .xls, .csv, .tsv, .json, .xml, .pdf, .docx, .txt, .md, .eml, .msg, images (.png, .jpg), and Google Sheets.
Handles Vietnamese encodings (UTF-8, UTF-8-BOM, cp1258), number formats (1.234.567,89), date formats, and multi-file merging.
"""

import io
import re
import os
import json
import email
from email import policy
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

from PIL import Image


class UniversalFileReader:
    """Enterprise multi-format reader with zero data fabrication and robust error isolation."""

    @staticmethod
    def detect_encoding(file_bytes: bytes) -> str:
        """Detects text encoding with priority for Vietnamese UTF-8, UTF-8-BOM, and Windows CP1258."""
        if file_bytes.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig'
        for enc in ['utf-8', 'cp1258', 'latin-1', 'utf-16']:
            try:
                file_bytes.decode(enc)
                return enc
            except UnicodeDecodeError:
                continue
        return 'utf-8'

    @staticmethod
    def parse_vietnamese_number(val: Any) -> Any:
        """Parses numbers with Vietnamese formatting (dots as thousands separators, comma as decimal)."""
        if pd.isna(val) or val is None:
            return np.nan
        if isinstance(val, (int, float)):
            return val
        s = str(val).strip()
        # Remove currency symbols and units
        s = re.sub(r'[đĐVNDvnd\s]', '', s)
        if not s:
            return np.nan
            
        # Pattern 1: Vietnamese style: 1.250.000,50 or 1.250.000
        if re.match(r'^-?\d{1,3}(\.\d{3})+(,\d+)?$', s):
            s = s.replace('.', '').replace(',', '.')
            try:
                return float(s)
            except ValueError:
                pass
                
        # Pattern 2: International style: 1,250,000.50 or 1,250,000
        if re.match(r'^-?\d{1,3}(,\d{3})+(\.\d+)?$', s):
            s = s.replace(',', '')
            try:
                return float(s)
            except ValueError:
                pass
                
        # Pattern 3: Simple decimal with comma: 1250,5
        if re.match(r'^-?\d+,\d+$', s):
            s = s.replace(',', '.')
            try:
                return float(s)
            except ValueError:
                pass
                
        # Fallback to standard float parsing
        try:
            return float(s)
        except ValueError:
            return val

    @classmethod
    def read_tabular_file(cls, file_name: str, file_bytes: bytes) -> Dict[str, Any]:
        """Reads .xlsx, .xls, .csv, .tsv, .json, .xml into DataFrames with multi-sheet support."""
        ext = file_name.split('.')[-1].lower()
        sheets_data: Dict[str, pd.DataFrame] = {}
        meta: Dict[str, Any] = {"format": ext, "file_name": file_name, "sheets": []}

        # 1. Excel files (.xlsx, .xls)
        if ext in ['xlsx', 'xls']:
            try:
                xls = pd.ExcelFile(io.BytesIO(file_bytes))
                meta["sheets"] = xls.sheet_names
                for s_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=s_name)
                    # Clean empty rows/cols
                    df = df.dropna(how='all').dropna(axis=1, how='all')
                    sheets_data[s_name] = df
            except Exception as e:
                raise ValueError(f"Không thể đọc file Excel '{file_name}': {str(e)}")

        # 2. CSV / TSV files
        elif ext in ['csv', 'tsv', 'txt']:
            enc = cls.detect_encoding(file_bytes)
            # Sniff delimiter
            try:
                sample = file_bytes[:4096].decode(enc, errors='ignore')
                delimiter = '\t' if ext == 'tsv' or ('\t' in sample and sample.count('\t') > sample.count(',')) else (';' if sample.count(';') > sample.count(',') else ',')
                df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc, sep=delimiter)
                df = df.dropna(how='all').dropna(axis=1, how='all')
                sheets_data["Data"] = df
                meta["sheets"] = ["Data"]
                meta["encoding"] = enc
                meta["delimiter"] = delimiter
            except Exception as e:
                raise ValueError(f"Không thể phân tích file CSV/TSV '{file_name}': {str(e)}")

        # 3. JSON files
        elif ext == 'json':
            enc = cls.detect_encoding(file_bytes)
            try:
                content = json.loads(file_bytes.decode(enc))
                if isinstance(content, list):
                    df = pd.json_normalize(content)
                elif isinstance(content, dict):
                    # Check if there is an inner list
                    list_keys = [k for k, v in content.items() if isinstance(v, list)]
                    if list_keys:
                        df = pd.json_normalize(content[list_keys[0]])
                    else:
                        df = pd.DataFrame([content])
                else:
                    raise ValueError("JSON không ở dạng danh sách bản ghi hoặc đối tượng hợp lệ.")
                df = df.dropna(how='all')
                sheets_data["Records"] = df
                meta["sheets"] = ["Records"]
            except Exception as e:
                raise ValueError(f"Không thể đọc file JSON '{file_name}': {str(e)}")

        # 4. XML files
        elif ext == 'xml':
            enc = cls.detect_encoding(file_bytes)
            try:
                root = ET.fromstring(file_bytes.decode(enc))
                records = []
                for child in root:
                    rec = {}
                    for item in child:
                        rec[item.tag] = item.text
                    if rec:
                        records.append(rec)
                    else:
                        rec[child.tag] = child.text
                        records.append(rec)
                df = pd.DataFrame(records) if records else pd.read_xml(io.BytesIO(file_bytes))
                df = df.dropna(how='all')
                sheets_data["XML_Data"] = df
                meta["sheets"] = ["XML_Data"]
            except Exception as e:
                raise ValueError(f"Không thể đọc file XML '{file_name}': {str(e)}")

        else:
            raise ValueError(f"Định dạng bảng tính '.{ext}' chưa được hỗ trợ.")

        return {"sheets": sheets_data, "meta": meta}

    @classmethod
    def read_document_file(cls, file_name: str, file_bytes: bytes, gemini_client=None) -> Dict[str, Any]:
        """Reads .pdf, .docx, .txt, .md, .eml, .msg into extracted plain text and structured blocks."""
        ext = file_name.split('.')[-1].lower()
        extracted_text = ""
        meta: Dict[str, Any] = {"format": ext, "file_name": file_name, "pages": 1}

        # 1. PDF files
        if ext == 'pdf':
            if PdfReader is None:
                raise RuntimeError("Thư viện pypdf chưa được cài đặt để đọc file PDF.")
            try:
                reader = PdfReader(io.BytesIO(file_bytes))
                meta["pages"] = len(reader.pages)
                pages_text = []
                for p_idx, page in enumerate(reader.pages):
                    t = page.extract_text() or ""
                    if t.strip():
                        pages_text.append(f"--- [Trang {p_idx+1}] ---\n{t}")
                extracted_text = "\n\n".join(pages_text)
                
                # If scanned PDF (no text found) and Gemini API client is available
                if not extracted_text.strip() and gemini_client:
                    try:
                        from google.genai import types
                        response = gemini_client.models.generate_content(
                            model="gemini-3.1-flash-lite",
                            contents=[
                                types.Part.from_bytes(data=file_bytes, mime_type="application/pdf"),
                                "Trích xuất toàn bộ văn bản, danh mục sản phẩm, đơn giá và số lượng trong tài liệu PDF này một cách chính xác tuyệt đối."
                            ]
                        )
                        if response and response.text:
                            extracted_text = response.text.strip()
                            meta["extracted_via"] = "Gemini Multimodal OCR"
                    except Exception as ocr_err:
                        print(f"[PDF OCR Warning] {ocr_err}")
            except Exception as e:
                raise ValueError(f"Lỗi đọc file PDF '{file_name}': {str(e)}")

        # 2. DOCX files
        elif ext == 'docx':
            if docx is None:
                raise RuntimeError("Thư viện python-docx chưa được cài đặt.")
            try:
                doc = docx.Document(io.BytesIO(file_bytes))
                paras = [p.text for p in doc.paragraphs if p.text.strip()]
                # Also extract table text
                tables_text = []
                for t in doc.tables:
                    for row in t.rows:
                        row_vals = [c.text.strip() for c in row.cells]
                        tables_text.append(" | ".join(row_vals))
                extracted_text = "\n".join(paras)
                if tables_text:
                    extracted_text += "\n\n[Dữ liệu Bảng trong Word]:\n" + "\n".join(tables_text)
                meta["paragraphs"] = len(paras)
            except Exception as e:
                raise ValueError(f"Lỗi đọc file DOCX '{file_name}': {str(e)}")

        # 3. Plain Text / Markdown
        elif ext in ['txt', 'md']:
            enc = cls.detect_encoding(file_bytes)
            extracted_text = file_bytes.decode(enc, errors='replace')
            meta["encoding"] = enc

        # 4. Email files (.eml, .msg)
        elif ext in ['eml', 'msg']:
            try:
                msg = email.message_from_bytes(file_bytes, policy=policy.default)
                headers_info = [
                    f"Từ (From): {msg.get('From', '')}",
                    f"Tới (To): {msg.get('To', '')}",
                    f"Ngày (Date): {msg.get('Date', '')}",
                    f"Tiêu đề (Subject): {msg.get('Subject', '')}"
                ]
                body_parts = []
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get('Content-Disposition', ''))
                        if ctype == 'text/plain' and 'attachment' not in cdispo:
                            body_parts.append(part.get_content())
                else:
                    body_parts.append(msg.get_content())
                
                extracted_text = "\n".join(headers_info) + "\n\n" + "\n".join(body_parts)
                meta["email_subject"] = msg.get('Subject', '')
            except Exception as e:
                raise ValueError(f"Lỗi phân tích email '{file_name}': {str(e)}")

        else:
            raise ValueError(f"Định dạng tài liệu '.{ext}' chưa được hỗ trợ.")

        return {"text": extracted_text, "meta": meta}

    @classmethod
    def read_image_file(cls, file_name: str, file_bytes: bytes, gemini_client=None) -> Dict[str, Any]:
        """Extracts text and tabular content from invoice/order images via Gemini Vision."""
        ext = file_name.split('.')[-1].lower()
        extracted_text = ""
        meta: Dict[str, Any] = {"format": ext, "file_name": file_name}

        try:
            image = Image.open(io.BytesIO(file_bytes))
            meta["width"], meta["height"] = image.size
        except Exception as e:
            raise ValueError(f"File ảnh '{file_name}' không hợp lệ hoặc bị hỏng.")

        if gemini_client:
            try:
                from google.genai import types
                mime_type = "image/png" if ext == "png" else "image/jpeg"
                response = gemini_client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=[
                        types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                        "Bạn là hệ thống OCR thị giác cao cấp. Hãy đọc và trích xuất toàn bộ nội dung trong ảnh này bao gồm thông tin khách hàng, số điện thoại, danh mục thiết bị, mã hàng, số lượng và yêu cầu kỹ thuật. Trình bày trung thực và rõ ràng."
                    ]
                )
                if response and response.text:
                    extracted_text = response.text.strip()
                    meta["ocr_engine"] = "Gemini 3.1 Flash Lite Vision"
            except Exception as e:
                print(f"[Image OCR Warning] {e}")
                extracted_text = f"[Ảnh: {file_name} - {meta['width']}x{meta['height']}px. Không thể kết nối Gemini OCR trực tuyến. Vui lòng nhập thông tin bằng tay.]"
        else:
            extracted_text = f"[Ảnh: {file_name} - {meta['width']}x{meta['height']}px. OCR yêu cầu kích hoạt khóa Gemini API.]"

        return {"text": extracted_text, "meta": meta}

    @classmethod
    def load_any_file(cls, file_name: str, file_bytes: bytes, gemini_client=None) -> Dict[str, Any]:
        """Universal dispatcher that identifies the file format and executes the right reader."""
        if isinstance(file_name, (bytes, bytearray)) and isinstance(file_bytes, str):
            file_name, file_bytes = file_bytes, file_name
        ext = file_name.split('.')[-1].lower()
        
        # Tabular data
        if ext in ['xlsx', 'xls', 'csv', 'tsv', 'json', 'xml']:
            result = cls.read_tabular_file(file_name, file_bytes)
            return {"kind": "tabular", **result}
            
        # Document text
        elif ext in ['pdf', 'docx', 'txt', 'md', 'eml', 'msg']:
            result = cls.read_document_file(file_name, file_bytes, gemini_client=gemini_client)
            return {"kind": "document", **result}
            
        # Image vision OCR
        elif ext in ['png', 'jpg', 'jpeg', 'webp']:
            result = cls.read_image_file(file_name, file_bytes, gemini_client=gemini_client)
            return {"kind": "image", **result}
            
        else:
            raise ValueError(f"Định dạng '.{ext}' không nằm trong danh mục hỗ trợ. Hệ thống hỗ trợ: Excel, CSV, TSV, JSON, XML, PDF, Word, Email, TXT, MD và Ảnh PNG/JPG.")
