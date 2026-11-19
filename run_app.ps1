# PowerShell launcher for Minh An B2B Sales AI Agent
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "    KHOI DONG MINH AN B2B SALES AI AGENT HUB       " -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Ung dung dang chay tai: http://localhost:8501" -ForegroundColor Green
& .\.venv\Scripts\streamlit.exe run app.py --server.port 8501 --server.headless true
