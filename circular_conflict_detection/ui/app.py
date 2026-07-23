import streamlit as st
import requests
import json

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="سامانه تشخیص مغایرت بخشنامه‌ها", layout="wide")
st.title("⚖️ سامانه هوشمند تشخیص مغایرت و تعارض بخشنامه‌ها")

uploaded_file = st.file_uploader("فایل JSON بخشنامه را آپلود کنید", type=["json"])

if uploaded_file is not None:
    # نمایش پیش‌نمایش JSON آپلود شده
    json_bytes = uploaded_file.getvalue()
    json_data = json.loads(json_bytes.decode("utf-8"))
    
    st.subheader("پیش‌نمایش بخشنامه ورودی:")
    st.json(json_data)
    
    if st.button("پردازش فایل JSON و بررسی تعارضات"):
        files = {"file": (uploaded_file.name, json_bytes, "application/json")}
        
        try:
            res = requests.post(f"{API_URL}/circulars/upload-json", files=files)
            if res.status_code == 200:
                conflicts = res.json()
                if not conflicts:
                    st.success("✅ هیچ تعارضی با آرشیو بخشنامه‌ها یافت نشد.")
                else:
                    st.warning(f"⚠️ تعداد {len(conflicts)} مورد تعارض کشف شد!")
                    for item in conflicts:
                        with st.expander(f"📌 {item['clauses_involved']} - {item['conflict_type']}"):
                            st.write(f"**توضیحات:** {item['explanation']}")
                            st.write(f"**بند معتبر/برنده:** `{item['winning_clause']}`")
                            if item['requires_human_review']:
                                st.error("🚨 نیازمند بازبینی واحد حقوقی (تعارض بین‌واحدی)")
        except Exception as e:
            st.error(f"خطا در ارتباط با API: {e}")


"""

import streamlit as st
import requests
import json

API_BASE_URL = "http://backend:8000/api/v1/circulars"

st.set_page_config(page_title="سامانه کشف تعارض بخشنامه‌ها", layout="wide")

st.title("⚖️ سامانه هوشمند تشخیص مغایرت و تعارض بخشنامه‌ها")
st.caption("سیستم تحلیل حقوقی تطبیق مقررات بانکی - DATA-ICTChallenge")

tab1, tab2 = st.tabs(["📝 ثبت و بارگذاری بخشنامه (JSON)", "🔍 پایش و بررسی دوره‌ای آرشیو"])

with tab1:
    st.subheader("ثبت بخشنامه جدید و تحلیل آنی مغایرت‌ها")
    uploaded_file = st.file_uploader("فایل JSON بخشنامه را آپلود کنید", type=["json"])
    
    if uploaded_file is not None:
        json_bytes = uploaded_file.getvalue()
        try:
            json_data = json.loads(json_bytes.decode("utf-8"))
            st.json(json_data)
            
            if st.button("پردازش و شناسایی تعارضات"):
                files = {"file": (uploaded_file.name, json_bytes, "application/json")}
                res = requests.post(f"{API_BASE_URL}/upload-json", files=files)
                
                if res.status_code == 200:
                    conflicts = res.json()
                    if not conflicts:
                        st.success("✅ هیچ مغایرت یا تعارضی با آرشیو بخشنامه‌ها یافت نشد.")
                    else:
                        st.warning(f"⚠️ تعداد {len(conflicts)} مورد تعارض شناسایی شد:")
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
                                st.write(f"**توضیحات حقوقی:** {item['explanation']}")
                                if item.get('simple_summary'):
                                    st.success(f"💡 **خلاصه ساده (LLM):** {item['simple_summary']}")
        except Exception as e:
            st.error(f"خطا در پردازش فایل: {e}")

with tab2:
    st.subheader("اجرای پایش دوره‌ای (Periodic Audit) روی کل آرشیو")
    if st.button("شروع پایش دوره‌ای آرشیو"):
        try:
            res = requests.get(f"{API_BASE_URL}/periodic-audit")
            if res.status_code == 200:
                data = res.json()
                st.metric("تعداد بخشنامه‌های بررسی شده", data["total_circulars_checked"])
                st.metric("تعداد تعارض‌های پنهان کشف شده", data["total_conflicts_found"])
                
                for item in data["conflicts"]:
                    st.error(f"تعارض: {item['clauses_involved']} | برنده: {item['winning_clause']}")
        except Exception as e:
            st.error(f"خطا در برقراری ارتباط با سرویس پایش: {e}")

"""