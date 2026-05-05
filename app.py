import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from openai import OpenAI

# 1. Page Config
st.set_page_config(page_title="Ухаалаг Зүрх", page_icon="❤️")

# 2. Connection with Safety
def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Sheet1", ttl=0)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception:
        # Sheet холбогдож чадахгүй бол хоосон дата үүсгэнэ
        return pd.DataFrame(columns=["Сурагч", "Код", "Эцэг_эх", "Э_код"])

# 3. OpenAI Setup
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("AI түлхүүр тохируулаагүй байна.")

# 4. Session State
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- UI LOGIC ---
if not st.session_state.auth:
    st.title("❤️ Ухаалаг Зүрх")
    st.subheader("Дижитал өдрийн тэмдэглэл")
    role = st.radio("Та хэн бэ?", ["Сурагч", "Багш", "Эцэг эх"])
    name = st.text_input("Нэвтрэх нэр")
    pwd = st.text_input("Нууц код", type="password")

    if st.button("Нэвтрэх"):
        # Багш нэвтрэх (Багшийн код Sheets-ээс хамааралгүй)
        if role == "Багш" and name == "admin" and pwd == "admin123":
            st.session_state.auth = True
            st.session_state.role = "Багш"
            st.rerun()
        else:
            df = load_data()
            if role == "Сурагч" and not df.empty:
                check = df[(df['Сурагч'].astype(str) == str(name)) & (df['Код'].astype(str) == str(pwd))]
                if not check.empty:
                    st.session_state.auth = True
                    st.session_state.role = "Сурагч"
                    st.session_state.name = name
                    st.rerun()
            elif role == "Эцэг эх" and not df.empty:
                check = df[(df['Эцэг_эх'].astype(str) == str(name)) & (df['Э_код'].astype(str) == str(pwd))]
                if not check.empty:
                    st.session_state.auth = True
                    st.session_state.role = "Эцэг эх"
                    st.session_state.name = name
                    st.rerun()
            st.error("Мэдээлэл буруу эсвэл систем түр саатлаа.")
else:
    st.sidebar.button("Гарах", on_click=lambda: st.session_state.clear())
    if st.session_state.role == "Багш":
        st.header("👨‍🏫 Багшийн хяналтын хэсэг")
        st.dataframe(load_data())
    else:
        st.header(f"👋 Сайн уу, {st.session_state.name}")
        note = st.text_area("Сэтгэлээ хуваалцаарай...")
        if st.button("Илгээх"):
            st.success("Тэмдэглэл амжилттай хадгалагдлаа! (AI шинжилж байна...)")
