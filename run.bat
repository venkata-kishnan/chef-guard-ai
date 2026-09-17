@echo off
title NutriScan AI - Food Quality Inspection System
echo ======================================================================
echo          NUTRISCAN AI - FOOD QUALITY INSPECTION SYSTEM
echo ======================================================================
echo.
echo [1/2] Checking Python and dependencies...
py -m pip install -r requirements.txt --quiet
echo.
echo [2/2] Launching NutriScan AI web server...
echo.
echo Server running at: http://127.0.0.1:5000
echo Opening browser...
start http://127.0.0.1:5000
py app.py
pause
