import streamlit as st
import requests

# --- إعداد الصفحة ---
st.set_page_config(page_title="⚡ إدارة الكوارث", layout="wide")

# --- تصميم CSS للواجهة ---
st.markdown("""
<style>
.stApp {
    background-image: url("https://github.com/workmeshari1/disaster-app/blob/6b907779e30e18ec6ebec68b90e2558d91e5339b/assets.png?raw=true");
    background-size: cover;
    background-position: center top;
    background-repeat: no-repeat;
    min-height: 100vh;
    padding-top: 80px;
}
#MainMenu, header, footer {
    visibility: hidden;
}
h1 { font-size:32px !important; color:#ffffff; text-align:center; margin-top:-60px; }
h2 { font-size:24px !important; color:#ffffff; }
div.stButton > button:first-child {
    background-color: #ff6600;
    color: white;
    font-size: 18px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ دائرة إدارة الكوارث والأزمات الصناعية")

# --- إدخال البحث ---
query = st.text_input("اكتب وصف الحالة أو الكلمة:")

# --- زر البحث ---
if st.button("بحث"):
    if not query.strip():
        st.warning("❌ يرجى إدخال كلمة للبحث")
    else:
        try:
            # رابط الـ API المحلي
            api_url = f"https://crisis-pypw.onrender.com/search?query={query}"
            response = requests.get(api_url)
            data = response.json()

            results = data.get("results", [])
            if not results:
                st.info("❌ لم يتم العثور على نتائج مشابهة.")
            else:
                st.subheader(f"🔍 نتائج البحث لـ: {query}")
                for r in results:
                    st.markdown(
                        f"""
                        <div style='background:#1f1f1f;color:#fff;padding:12px;border-radius:10px;direction:rtl;text-align:right;font-size:18px;margin-bottom:10px;'>
                            <b>الوصف:</b> {r.get("الوصف", "—")}<br>
                            <b>الإجراء:</b> <span style='background:#ff6600;color:#0a1e3f;padding:4px 8px;border-radius:6px;'>{r.get("الإجراء","—")}</span><br>
                            <span style='font-size:14px;color:orange;'>درجة التشابه: {r.get("درجة_التشابه", 0):.2f}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        except Exception as e:
            st.error(f"❌ خطأ في الاتصال بالـ API: {str(e)}")
