@echo off
cd /d "%~dp0"
call venvLocal\Scripts\activate.bat
streamlit run app.py
call deactivate
pause