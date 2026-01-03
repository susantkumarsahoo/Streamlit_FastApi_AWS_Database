@echo off
echo Starting Streamlit App...
echo ========================================
echo Please wait for FastAPI to start first!
timeout /t 5
python -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1
pause