import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from openai import OpenAI
import os

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="Ухаалаг Зүрх", page_icon="❤️", layout="centered")

# 2. Google Sheets Холболт
conn = st.connection("gsheets", type=GSheetsConnection)

def load_users():
    # Google Sheet-ээс хэрэглэгчийн мэдээллийг унших
    try:
        return conn.read(worksheet="Sheet1")
    except:
        return pd.DataFrame(columns=["Сурагч", "Код", "Эцэг_эх", "Э_код"])

def save_users(df):
    # Google Sheet рүү мэдээлэл хадгалах
    conn.update(worksheet="Sheet1", data=df)
    st.cache_data.clear()

# 3. AI Тохиргоо (Өмнөх тохиргоог хэвээр үлдээв)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_emotion(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Чи бол сэтгэл зүйч. Текстийг уншаад Улаан (Аюултай), Шар (Анхаарах), Ногоон (Хэвийн) өнгөөр оношилж зөвлөгөө өг."},
                  {"role": "user", "content": text}]
    )
    return response.choices[0].message.content

# 4. Session State (Төлөв хадгалах)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- НЭВТРЭХ ХЭСЭГ ---
if not st.session_state.logged_in:
    st.title("❤️ Ухаалаг Зүрх")
    st.subheader("Дижитал өдрийн тэмдэглэл")
    
    role = st.radio("Та хэн бэ?", ["Сурагч", "Багш", "Эцэг эх"])
    username = st.text_input("Нэвтрэх нэр")
    password = st.text_input("Нууц код", type="password")

    if st.button("Нэвтрэх"):
        df = load_users()
        
        if role == "Багш" and username == "admin" and password == "admin123": # Багшийн нэвтрэх код
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = "Багш"
            st.rerun()
            
        elif role == "Сурагч":
            user_row = df[(df['Сурагч'] == username) & (df['Код'].astype(str) == str(password))]
            if not user_row.empty:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "Сурагч"
                st.rerun()
            else:
                st.error("Нэр эсвэл код буруу байна.")
                
        elif role == "Эцэг эх":
            user_row = df[(df['Эцэг_эх'] == username) & (df['Э_код'].astype(str) == str(password))]
            if not user_row.empty:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "Эцэг эх"
                st.rerun()
            else:
                st.error("Нэр эсвэл код буруу байна.")

# --- ҮНДСЭН ХЭСЭГ ---
else:
    st.sidebar.title(f"👋 Сайн уу, {st.session_state.username}")
    if st.sidebar.button("Гарах"):
        st.session_state.logged_in = False
        st.rerun()

    # БАГШИЙН ХЯНАЛТЫН САМБАР
    if st.session_state.role == "Багш":
        st.header("👨‍🏫 Багшийн хяналтын хэсэг")
        
        tab1, tab2 = st.tabs(["📊 Сэтгэл зүйн хяналт", "⚙️ Сурагчдын удирдлага"])
        
        with tab1:
            st.write("Энд сурагчдын илгээсэн тэмдэглэл харагдана.")
            # Тэмдэглэл харуулах код энд үргэлжилнэ...

        with tab2:
            st.subheader("👥 Сурагчдын жагсаалт")
            df = load_users()
            st.dataframe(df)
            
            st.markdown("---")
            st.subheader("❌ Сурагч хасах")
            user_to_delete = st.selectbox("Хасах сурагчийг сонгоно уу:", df['Сурагч'].tolist())
            if st.button("Сурагчийг жагсаалтаас хасах"):
                new_df = df[df['Сурагч'] != user_to_delete]
                save_users(new_df)
                st.success(f"{user_to_delete} амжилттай хасагдлаа.")
                st.rerun()

    # СУРАГЧИЙН ХЭСЭГ
    elif st.session_state.role == "Сурагч":
        st.header("📖 Миний өдрийн тэмдэглэл")
        note = st.text_area("Өнөөдөр ямар байна? Сэтгэлээ хуваалцаарай...")
        if st.button("Илгээх"):
            result = analyze_emotion(note)
            st.info(f"AI Зөвлөмж: {result}")
            # Мэдээллийг хадгалах код...

    # ЭЦЭГ ЭХИЙН ХЭСЭГ
    elif st.session_state.role == "Эцэг эх":
        st.header("👨‍👩‍👧‍👦 Хүүхдийн сэтгэл зүйн байдал")
        st.write("Таны хүүхдийн сэтгэл зүйн ерөнхий төлөв байдал...")
       
