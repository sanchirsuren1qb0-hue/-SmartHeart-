import streamlit as st
from textblob import TextBlob
import json
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Ухаалаг Зүрх", page_icon="💖")

# ГЭРЛЭН ДОХИОНЫ ХАРАГДАЦ (STYLE)
def light_style(status):
    colors = {
        "УЛААН": "#ff4b4b",
        "ШАР": "#ffa500",
        "НОГООН": "#28a745"
    }
    c = colors.get(status, "#grey")
    html = f"""
    <div style="display: flex; align-items: center; background-color: #f0f2f6; padding: 10px; border-radius: 10px; border-left: 5px solid {c}; margin-bottom: 10px;">
        <div style="width: 20px; height: 20px; background-color: {c}; border-radius: 50%; margin-right: 15px; box-shadow: 0 0 10px {c};"></div>
        <b style="color: #31333F;">ТӨЛӨВ: {status}</b>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ӨГӨГДЛИЙН САНГИЙН ТОХИРГОО
USER_DB = "users.json"
DATA_DB = "data.json"

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'users' not in st.session_state: st.session_state['users'] = load_data(USER_DB)
if 'db' not in st.session_state: st.session_state['db'] = load_data(DATA_DB)

# AI ЛОГИК
def get_ai_advice(text):
    red_flags = ["хараа", "загна", "үх", "ална", "зод", "гөлөг", "новш"]
    is_red = any(w in text.lower() for w in red_flags)
    score = TextBlob(text).sentiment.polarity
    status = "УЛААН" if (is_red or score < -0.4) else ("ШАР" if score < 0 else "НОГООН")
    
    return {
        "status": status,
        "teacher_msg": "🍎 Багшаас: Багш нь чамайг үргэлж дэмжих болно. Маргааш уулзаад ярилцъя.",
        "parent_msg": "🏠 Гэр бүлээс: Миний хүү/охин бидэнд хамгийн үнэтэй эрдэнэ. Бид чамдаа хайртай.",
        "p_advice": "👨‍👩‍👧‍👦 Зөвлөмж: Хүүхдээ зүгээр л тэврээд, сонсож өгөөрэй. Битгий зэмлээрэй."
    }

# NAVIGATION (САЙДБАР)
user_role = st.sidebar.radio("Нэвтрэх хэсэг:", ["Сурагч", "Багш", "Эцэг эх"])

# 1. СУРАГЧИЙН ТАЛБАР
if user_role == "Сурагч":
    st.title("📝 Миний нууц тэмдэглэл")
    names = list(st.session_state['users'].keys())
    if names:
        s_name = st.selectbox("Нэрээ сонгоно уу:", ["Сонгох"] + names)
        s_pin = st.text_input("Код:", type="password")
        s_entry = st.text_area("Сэтгэлээ нээж бичээрэй...")
        visibility = st.radio("Хэн харах боломжтой вэ?", ["Зөвхөн багш харна", "Багш болон эцэг эх харна"])
        
        if st.button("Илгээх"):
            if s_name != "Сонгох" and s_pin == st.session_state['users'][s_name]['s_pin']:
                advice = get_ai_advice(s_entry)
                if s_name not in st.session_state['db']: st.session_state['db'][s_name] = {"history": []}
                st.session_state['db'][s_name]['history'].append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "entry": s_entry, "status": advice['status'],
                    "teacher_msg": advice['teacher_msg'], "parent_msg": advice['parent_msg'],
                    "p_advice": advice['p_advice'], "visibility": visibility
                })
                save_data(DATA_DB, st.session_state['db'])
                st.success("Амжилттай илгээгдлээ. ❤️")
                st.info(advice['teacher_msg'])
                if visibility == "Багш болон эцэг эх харна": st.info(advice['parent_msg'])
            else: st.error("Код буруу байна.")
    else: st.warning("Багш сурагчдыг бүртгээгүй байна.")

# 2. БАГШИЙН ТАЛБАР
elif user_role == "Багш":
    st.title("👩‍🏫 Багшийн удирдлага")
    if st.text_input("Нууц үг:", type="password") == "1234":
        t1, t2 = st.tabs(["📊 Архив", "➕ Сурагч нэмэх"])
        with t1:
            for name, data in st.session_state['db'].items():
                with st.expander(f"👤 {name}"):
                    for h in reversed(data['history']):
                        light_style(h['status'])
                        st.write(f"**{h['time']}** | 👀 {h['visibility']}")
                        st.write(f"💬 {h['entry']}")
                        st.divider()
        with t2:
            n_n = st.text_input("Сурагчийн нэр:")
            n_s = st.text_input("Сурагчийн код:")
            n_p = st.text_input("Эцэг эхийн код:")
            if st.button("Хадгалах"):
                st.session_state['users'][n_n] = {"s_pin": n_s, "p_pin": n_p}
                save_data(USER_DB, st.session_state['users'])
                st.success("Бүртгэгдлээ!")

# 3. ЭЦЭГ ЭХИЙН ТАЛБАР
else:
    st.title("👨‍👩‍👧‍👦 Эцэг эхийн хяналт")
    p_name = st.selectbox("Хүүхдийн нэр:", ["Сонгох"] + list(st.session_state['users'].keys()))
    p_pin = st.text_input("Код:", type="password")
    if st.button("Архив харах"):
        if p_name != "Сонгох" and p_pin == st.session_state['users'][p_name]['p_pin']:
            history = st.session_state['db'].get(p_name, {}).get('history', [])
            found = False
            for h in reversed(history):
                if h['visibility'] == "Багш болон эцэг эх харна":
                    found = True
                    light_style(h['status'])
                    st.write(f"🕒 {h['time']}")
                    st.write(f"**Хүүхдийн бичсэн:** {h['entry']}")
                    st.warning(f"💡 {h['p_advice']}")
                    st.divider()
            if not found: st.info("Нээлттэй тэмдэглэл алга.")
        else: st.error("Код буруу.")
