import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from openai import OpenAI

# 1. Page Config
st.set_page_config(page_title="Ухаалаг Зүрх", page_icon="❤️")

# 2. Connection with safety
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Sheet1-ээс өгөгдлийг унших
        df = conn.read(worksheet="Sheet1", ttl=0)
        # Баганын нэрсийг цэвэрлэх
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        return pd.DataFrame(columns=["Сурагч", "Код", "Эцэг_эх", "Э_код"])

# 3. AI Setup
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("API Key тохируулаагүй байна.")

def get_ai_advice(text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Чи бол сэтгэл зүйч. Зөвлөгөө өг."},
                      {"role": "user", "content": text}]
        )
        return response.choices[0].message.content
    except:
        return "AI одоогоор хариулах боломжгүй байна."

# 4. Login Logic
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("❤️ Ухаалаг Зүрх")
    role = st.selectbox("Та хэн бэ?", ["Сурагч", "Багш", "Эцэг эх"])
    name = st.text_input("Нэр")
    pwd = st.text_input("Код", type="password")

    if st.button("Нэвтрэх"):
        data = load_data()
        if role == "Багш" and name == "admin" and pwd == "admin123":
            st.session_state.auth = True
            st.session_state.role = "Багш"
            st.rerun()
        elif role == "Сурагч" and not data.empty:
            user = data[(data['Сурагч'].astype(str) == str(name)) & (data['Код'].astype(str) == str(pwd))]
            if not user.empty:
                st.session_state.auth = True
                st.session_state.role = "Сурагч"
                st.session_state.name = name
                st.rerun()
        elif role == "Эцэг эх" and not data.empty:
            user = data[(data['Эцэг_эх'].astype(str) == str(name)) & (data['Э_код'].astype(str) == str(pwd))]
            if not user.empty:
                st.session_state.auth = True
                st.session_state.role = "Эцэг эх"
                st.session_state.name = name
                st.rerun()
        else:
            st.error("Нэвтрэх мэдээлэл буруу байна.")
else:
    st.sidebar.button("Гарах", on_click=lambda: st.session_state.update({"auth": False}))
    
    if st.session_state.role == "Багш":
        st.header("📊 Хяналтын самбар")
        st.write("Нийт бүртгэлтэй хэрэглэгчид:")
        st.dataframe(load_data())
    elif st.session_state.role == "Сурагч":
        st.header(f"👋 Сайн уу, {st.session_state.name}")
        note = st.text_area("Өнөөдөр сэтгэл санаа чинь ямар байна?")
        if st.button("Илгээх"):
            with st.spinner("AI шинжилж байна..."):
                advice = get_ai_advice(note)
                st.info(advice) 
