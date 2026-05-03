import streamlit as st
from textblob import TextBlob
import json
import os
from datetime import datetime
import pandas as pd

# AI сан татах
try:
    import nltk
    nltk.data.find('corpora/movie_reviews')
except:
    os.system('python -m textblob.download_corpora')

# Өгөгдөл унших, хадгалах (Алдаанаас сэргийлсэн хувилбар)
def load_json(filename, default_type):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(default_type, f)
        return default_type
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = json.load(f)
            # Хэрэв data.json дотор жагсаалт биш зүйл байвал засах
            if filename == 'data.json' and not isinstance(content, list):
                return []
            return content
    except:
        return default_type

def save_json(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

# Гэрлэн дохио ба AI зөвлөмж
def get_status_info(text):
    analysis = TextBlob(text)
    score = analysis.sentiment.polarity
    if score < -0.1:
        return "УЛААН", "🆘 Багшид: Нэн яаралтай уулз. \n👪 Эцэг эхэд: Сэтгэл зүйн дэмжлэг үзүүл."
    elif score < 0.1:
        return "ШАР", "⚠️ Багшид: Ажиглаж ярилц. \n👪 Эцэг эхэд: Цаг гаргаж ярилц."
    else:
        return "НОГООН", "✅ Багшид: Тогтвортой байна. \n👪 Эцэг эхэд: Урам өг."

def light_html(status):
    color = {"УЛААН": "#ff4b4b", "ШАР": "#ffa500", "НОГООН": "#28a745"}.get(status, "#grey")
    return f'<div style="width:15px;height:15px;background:{color};border-radius:50%;display:inline-block;margin-right:8px;"></div>'

# --- APP-ИЙН ЭХЛЭЛ ---
st.set_page_config(page_title="Ухаалаг Зүрх", page_icon="💖")
role = st.sidebar.radio("Нэвтрэх хэсэг:", ["Сурагч", "Багш", "Эцэг эх"])

users = load_json('users.json', {})
data = load_json('data.json', [])

# --- СУРАГЧИЙН ХЭСЭГ ---
if role == "Сурагч":
    st.title("💖 Сурагчийн булан")
    if users:
        # Сурагч нэрээ жагсаалтаас сонгоно
        names = [v['name'] for k, v in users.items()]
        selected_name = st.selectbox("Нэрээ сонгоно уу:", names)
        # Тухайн нэртэй сурагчийн кодыг олж авах
        sid = [k for k, v in users.items() if v['name'] == selected_name][0]
        
        entered_code = st.text_input("Сурагчийн кодоо оруулна уу:", type="password")
        
        if entered_code == users[sid]['s_code']:
            st.success(f"Сайн уу, {selected_name}!")
            msg = st.text_area("Мэдрэмжээ хуваалцаарай...")
            vis = st.selectbox("Хэнд харуулах вэ?", ["Багш болон эцэг эх харна", "Зөвхөн багш харна"])
            
            if st.button("Илгээх"):
                status, advice = get_status_info(msg)
                new_entry = {
                    "id": sid, "name": selected_name, "msg": msg,
                    "status": status, "advice": advice, "vis": vis,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                data.append(new_entry)
                save_json('data.json', data)
                st.balloons()
                st.success("Илгээгдлээ!")
        elif entered_code:
            st.error("Сурагчийн код буруу байна.")
    else:
        st.info("Бүртгэлтэй сурагч байхгүй байна.")

# --- БАГШИЙН ХЭСЭГ ---
elif role == "Багш":
    st.title("👩‍🏫 Багш")
    if st.text_input("Нууц үг:", type="password") == "1234":
        t1, t2, t3 = st.tabs(["📊 Архив", "➕ Сурагч нэмэх", "🔑 Код хадгалах"])
        
        with t1:
            for entry in reversed(data):
                st.markdown(f"**{light_html(entry['status'])} {entry['name']}** | {entry['time']}", unsafe_content_usage=True)
                st.warning(f"🤖 **AI Зөвлөмж:** \n{entry['advice']}")
                st.divider()

        with t2:
            n_name = st.text_input("Сурагчийн нэр:")
            n_sid = st.text_input("Сурагчийн код (S...):")
            n_pcode = st.text_input("Эцэг эхийн код (P...):")
            if st.button("Бүртгэх"):
                if n_sid and n_name and n_pcode:
                    users[n_sid] = {"name": n_name, "s_code": n_sid, "p_code": n_pcode}
                    save_json('users.json', users)
                    st.success("Амжилттай!")

        with t3:
            if users:
                user_df = pd.DataFrame([{"Нэр": v['name'], "Сурагчийн код": v['s_code'], "Эцэг эхийн код": v['p_code']} for k, v in users.items()])
                st.table(user_df)

# --- ЭЦЭГ ЭХИЙН ХЭСЭГ ---
elif role == "Эцэг эх":
    st.title("👪 Эцэг эх")
    p_code = st.text_input("Эцэг эхийн кодоо оруулна уу:")
    # Эцэг эхийн кодоор сурагчийг хайх
    child_id = None
    for k, v in users.items():
        if v.get('p_code') == p_code:
            child_id = k
            break
            
    if child_id:
        st.subheader(f"✨ {users[child_id]['name']}-ийн төлөв")
        c_logs = [d for d in data if d['id'] == child_id and d['vis'] == "Багш болон эцэг эх харна"]
        if c_logs:
            latest = c_logs[-1]
            st.markdown(f"### {light_html(latest['status'])} Төлөв: {latest['status']}", unsafe_content_usage=True)
            st.warning(f"🤖 **Зөвлөмж:** \n{latest['advice'].split('Эцэг эхэд: ')[1]}")
        else: st.info("Мэдээлэл байхгүй байна.")
