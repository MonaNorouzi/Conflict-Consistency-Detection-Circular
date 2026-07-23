import os
import streamlit as st
import requests
import json
import datetime

# Unified the API URL variable name
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

st.set_page_config(page_title="سامانه تشخیص مغایرت بخشنامه‌ها", layout="wide")
st.title("⚖️ سامانه هوشمند تشخیص مغایرت و تعارض بخشنامه‌ها")

tab1, tab2 = st.tabs(["📝 ثبت و ارزیابی متن بخشنامه", "🔍 پایش و بررسی دوره‌ای آرشیو"])

with tab1:
    st.subheader("ورود متن خام بخشنامه جهت تست و تحلیل آنی مغایرت‌ها")
    
    # ADDED: Layout columns to separate metadata from the raw text
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("### 📋 اطلاعات پایه بخشنامه")
        doc_id = st.text_input("شماره بخشنامه", value="C-015")
        doc_type = st.selectbox("نوع بخشنامه", ["Internal", "Regulatory"], format_func=lambda x: "داخلی" if x == "Internal" else "نهاد ناظر (بالادستی)")
        department = st.text_input("واحد صادرکننده", value="اداره اعتبارات")
        doc_date = st.date_input("تاریخ صدور", datetime.date.today())

    with col1:
        default_text = """بند ۱: سقف مجاز برای تمامی تسهیلات قرض‌الحسنه خرد پرداختی به متقاضیان، مبلغ ۱۵۰,۰۰۰,۰۰۰ تومان تعیین می‌شود.
بند ۲: بازپرداخت این تسهیلات حداکثر ۳۶ ماهه خواهد بود."""

        raw_text = st.text_area(
            "متن بخشنامه را در کادر زیر وارد یا پیست کنید:", 
            value=default_text, 
            height=280,
            placeholder="متن کامل یا بخشی از بخشنامه را اینجا بنویسید..."
        )
    
    if st.button("🚀 ارسال متن جهت پردازش و تست", type="primary"):
        if not raw_text.strip():
            st.warning("⚠️ لطفاً ابتدا متنی را وارد کنید.")
        else:
            with st.spinner("در حال تحلیل متن و بررسی تعارضات..."):
                try:
                    # ADDED: We now send the metadata along with the text to the Backend
                    payload = {
                        "text": raw_text,
                        "metadata": {
                            "doc_id": doc_id,
                            "type": doc_type,
                            "department": department,
                            "date": doc_date.isoformat()
                        }
                    }
                    
                    response = requests.post(
                        f"{API_URL}/circulars/process-text",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        conflicts = response.json()
                        if not conflicts:
                            st.success("✅ هیچ مغایرت یا تعارضی با آرشیو بخشنامه‌ها یافت نشد.")
                        else:
                            st.warning(f"⚠️ تعداد {len(conflicts)} مورد تعارض کشف شد:")
                            for item in conflicts:
                                with st.expander(f"📌 {item['clauses_involved']} | نوع: {item['conflict_type']}"):
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.write(f"**بندهای متعارض:** {item['clauses_involved']}")
                                        st.write(f"**بند برنده / معتبر:** `{item['winning_clause']}`")
                                    with col_b:
                                        if item['requires_human_review']:
                                            st.error("🚨 نیازمند بازبینی و تصمیم‌گیری انسانی توسط واحد حقوقی")
                                        else:
                                            st.info("ℹ️ تعارض بر اساس منطق اولویت‌بندی حل شد.")
                                    st.write(f"**توضیحات حقوقی (هوش مصنوعی):** {item['explanation']}")
                                    
                                    if item.get('simple_summary'):
                                        st.success(f"💡 **خلاصه ساده:** {item['simple_summary']}")
                    else:
                        st.error(f"خطا در پاسخ بک‌اند ({response.status_code}): {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ خطا در برقراری ارتباط با سرور بک‌اند: {e}")

with tab2:
    st.subheader("اجرای پایش دوره‌ای (Periodic Audit) روی کل آرشیو")
    if st.button("شروع پایش دوره‌ای آرشیو"):
        try:
            res = requests.get(f"{API_URL}/circulars/periodic-audit")
            if res.status_code == 200:
                data = res.json()
                st.metric("تعداد بخشنامه‌های بررسی شده", data["total_circulars_checked"])
                st.metric("تعداد تعارض‌های پنهان کشف شده", data["total_conflicts_found"])
                
                for item in data["conflicts"]:
                    st.error(f"تعارض: {item['clauses_involved']} | برنده: {item['winning_clause']}")
        except Exception as e:
            st.error(f"خطا در برقراری ارتباط با سرویس پایش: {e}")