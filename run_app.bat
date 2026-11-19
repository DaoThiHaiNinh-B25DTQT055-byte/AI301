@echo off
title Minh An B2B Sales AI Agent - Localhost
echo ===================================================
echo     KHOI DONG MINH AN B2B SALES AI AGENT HUB
echo ===================================================
echo Dang khoi chay tren http://localhost:8501 ...
echo.
.venv\Scripts\streamlit.exe run app.py --server.port 8501 --server.headless true
pause
