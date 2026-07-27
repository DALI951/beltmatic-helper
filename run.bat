@echo off
title Beltmatic Helper
echo.
echo   Installing dependencies...
echo.
pip install flask pywebview --quiet 2>nul
echo   Starting Beltmatic Helper...
echo.
python app.py
pause
