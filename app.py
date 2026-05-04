import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from openai import OpenAI

# 1. Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="Ухаалаг Зүрх", page_icon="❤️", layout="centered")

# 2. Google Sheets Холболт
conn = st.connection("gsheets", type=GSheetsConnection)

def load_users():
    try:
        # worksheet="Sheet1" гэдгийг таны зураг дээрх нэрээр тохируулав
        df = conn.read(worksheet="Sheet1", ttl=0)
        df.columns = [str(c).strip() for c in df.columns] # Баганы нэрийг цэвэрлэх
        return df
    except Exception as e:
        # Хэрэв Sheet уншихад алдаа гарвал хоосон бүтэц үүсгэх
        return pd.DataFrame(columns=["Сурагч", "Код", "Эцэг_эх", "Э_код"])

def save_users(df):
    try:
        conn.update(worksheet="Sheet1", data=df)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Хадгалахад алдаа гарлаа: {e}")

# 3. OpenAI AI Тохиргоо
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_emotion(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Чи бол сургуулийн сэтгэл зүйч. Хүүхдийн бичсэн текстийг уншаад Улаан (Аюултай), Шар (Анхаарах), Ногоон (Хэвийн) өнгөөр оношилж, тохирох зөвлөгөөг өг."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI холбогдоход алдаа гарлаа: {e}"

# 4. Нэвтрэх төлөвийг удирдах
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- НЭВТРЭХ ЦОНХ ---
if not st.session_state.logged_in:
    st.title("❤️ Ухаалаг Зүрх")
    st.subheader("Дижитал өдрийн тэмдэглэл")
    
    role = st.radio("Та хэн бэ?", ["Сурагч", "Багш", "Эцэг эх"])
    username = st.text_input("Нэвтрэх нэр")
    password = st.text_input("Нууц код", type="password")

    if st.button("Нэвтрэх"):
        df = load_users()
        
        # Багш нэвтрэх (Урьдчилан тохируулсан)
        if role == "Багш" and username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.username = "Багш"
            st.session_state.role = "Багш"
            st.rerun()
            
        # Сурагч нэвтрэх (Sheets-ээс шалгах)
        elif role == "Сурагч":
            if not df.empty and 'Сурагч' in df.columns:
                user_match = df[(df['Сурагч'].astype(str) == str(username)) & (df['Код'].astype(str) == str(password))]
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "Сурагч"
                    st.rerun()
                else:
                    st.error("Нэр эсвэл код буруу байна.")
            else:
                st.error("Сурагчийн дата олдсонгүй.")
                
        # Эцэг эх нэвтрэх (Sheets-ээс шалгах)
        elif role == "Эцэг эх":
            if not df.empty and 'Эцэг_эх' in df.columns:
                user_match = df[(df['Эцэг_эх'].astype(str) == str(username)) & (df['Э_код'].astype(str) == str(password))]
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "Эцэг эх"
                    st.rerun()
                else:
                    st.error("Эцэг эхийн нэр эсвэл код буруу байна.")

# --- ҮНДСЭН ЦОНХ ---
else:
    st.sidebar.title(f"👋 {st.session_state.username}")
    if st.sidebar.button("Гарах"):
        st.session_state.logged_in = False
        st.rerun()

    # 1. БАГШИЙН ХЭСЭГ
    if st.session_state.role == "Багш":
        st.header("👨‍🏫 Багшийн хяналтын хэсэг")
        tab1, tab2 = st.tabs(["📊 Хяналтын самбар", "⚙️ Сурагчдын удирдлага"])
        
        with tab1:
            st.write("Сурагчдын сэтгэл зүйн төлөв байдал (Sheet-ээс шууд):")
            current_data = load_users()
            st.dataframe(current_data)

        with tab2:
            st.subheader("👥 Сурагч хасах")
            df = load_users()
            if not df.empty:
                delete_list = df['Сурагч'].tolist()
                user_to_delete = st.selectbox("Хасах сурагчийг сонгоно уу:", delete_list)
                if st.button("Сурагчийг устгах"):
                    new_df = df[df['Сурагч'] != user_to_delete]
                    save_users(new_df)
                    st.success(f"{user_to_delete} амжилттай устлаа.")
                    st.rerun()

    # 2. СУРАГЧИЙН ХЭСЭГ
    elif st.session_state.role == "Сурагч":
        st.header("📖 Миний өдрийн тэмдэглэл")
        note = st.text_area("Өнөөдөр сэтгэл санаа чинь ямар байна? Хуваалцаарай...", height=150)
        if st.button("Илгээх"):
            with st.spinner("AI шинжилж байна..."):
                result = analyze_emotion(note)
                st.subheader("✨ AI Зөвлөмж:")
                st.info(result)

    # 3. ЭЦЭГ ЭХИЙН ХЭСЭГ
    elif st.session_state.role == "Эцэг эх":
        st.header("👨‍👩‍👧‍👦 Хүүхдийн сэтгэл зүйн байдал")
        st.write(f"Та {st.session_state.username}-ийн мэдээллийг харж байна.")
        st.warning("Энэ хэсэгт хүүхдийн сүүлийн тэмдэглэлүүд харагдах болно.")
