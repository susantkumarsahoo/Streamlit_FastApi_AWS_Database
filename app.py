import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Complaint Management", layout="wide")

# Check if FastAPI is running
def check_api():
    try:
        response = requests.get(FASTAPI_URL, timeout=2)
        return response.status_code == 200
    except:
        return False

if not check_api():
    st.error("⚠️ FastAPI server is not running! Please start it first.")
    st.info("Run: python -m uvicorn main:app --host 127.0.0.1 --port 8000")
    st.stop()

st.title("🎯 Complaint Management System")

menu = st.sidebar.radio("📋 Menu", ["Add Complaint", "Upload File", "View & Download"])

# ===== ADD COMPLAINT =====
if menu == "Add Complaint":
    st.header("📝 Add New Complaint")
    
    with st.form("complaint_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", value=datetime.now())
            complaint_number = st.text_input("Complaint Number")
            consumer_number = st.text_input("Consumer Number")
        
        with col2:
            circle = st.text_input("Circle")
            dept = st.text_input("Department")
        
        complaint_details = st.text_area("Complaint Details", height=100)
        remarks = st.text_area("Remarks", height=100)
        
        if st.form_submit_button("💾 Save", use_container_width=True):
            data = {
                "date": date.strftime("%Y-%m-%d"),
                "complaint_details": complaint_details,
                "complaint_number": complaint_number,
                "circle": circle,
                "consumer_number": consumer_number,
                "dept": dept,
                "remarks": remarks
            }
            
            response = requests.post(f"{FASTAPI_URL}/add_complaint", json=data)
            
            if response.status_code == 200:
                st.success("✅ Saved successfully!")
                time.sleep(1)
                st.rerun()

# ===== UPLOAD FILE =====
elif menu == "Upload File":
    st.header("📤 Upload CSV or Excel")
    
    st.info("Required columns: DATE, COMPLAINT DETAILS, COMPLAINT NUMBER, CIRCLE, CONSUMER NUMBER, DEPT, REMARKS")
    
    uploaded_file = st.file_uploader("Choose file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("Preview:")
            st.dataframe(df.head(10), use_container_width=True)
            st.info(f"Total rows: {len(df)}")
            
            if st.button("📥 Upload to Database", use_container_width=True):
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{FASTAPI_URL}/upload", files=files)
                
                if response.status_code == 200:
                    st.success(response.json()["message"])
                else:
                    st.error("Upload failed")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

# ===== VIEW & DOWNLOAD =====
else:
    st.header("📊 View & Download Data")
    
    if st.button("🔄 Load Data", use_container_width=True):
        response = requests.get(f"{FASTAPI_URL}/complaints")
        
        if response.status_code == 200:
            data = response.json()
            
            if data["count"] > 0:
                df = pd.DataFrame(data["complaints"])
                df = df.drop('id', axis=1, errors='ignore')
                
                st.success(f"📈 Total: {data['count']} records")
                
                search = st.text_input("🔍 Search")
                if search:
                    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
                    df = df[mask]
                
                st.dataframe(df, use_container_width=True, height=400)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "⬇️ Download CSV",
                        csv,
                        f"complaints_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    excel_file = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    df.to_excel(excel_file, index=False)
                    
                    with open(excel_file, 'rb') as f:
                        st.download_button(
                            "⬇️ Download Excel",
                            f,
                            f"complaints_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
            else:
                st.warning("No data found")
        else:
            st.error("Failed to load data")