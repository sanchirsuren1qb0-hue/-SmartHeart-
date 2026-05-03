import streamlit as st
from textblob import TextBlob
import json
import os
from datetime import datetime
import pandas as pd

# 1. AI САНГ БЭЛТГЭХ (Зөвлөмж харуулахын тулд заавал байх ёстой)
try:
    import nltk
    nltk.data.find('corpora/movie_reviews')
except LookupError:
    os.system('python -m textblob.download_corpora')

# 2. ӨГӨГДӨЛ ХАДГАЛАХ ФАЙЛУУДЫГ ШАЛГАХ
def init_files():
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f: json.dump({}, f)
    if not os.path.exists('data.json'):
        with open('data.json', 'w') as f: json.dump([], f)

init_files()

# Өгөгдөл унших, хадгалах функцууд
def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {} if "users" in filename else []

def save_json(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

# 3. ГЭРЛЭН ДОХИО БОЛОН AI ЗӨВЛӨМЖИЙН ЛОГИК
def get_status_info(text):
    analysis = TextBlob(text)
    # Хэрэв текст монгол бол сэтгэл хөдлөлийг энгийнээр таних оролдлого
    score = analysis.sentiment.polarity
    
    if score < -0.1 or any(word in text.lower() for word in ['айж', 'айдаг', 'хэцүү', 'муу', 'уйл']):
        return "УЛААН", "🆘 Багшид: Нэн яаралтай ганцаарчилж уулзах шаардлагатай. \n👪 Эцэг эхэд: Хүүхэдтэйгээ маш тайван ярилцаж, сэтгэл зүйн дэмжлэг үзүүлнэ үү."
    elif score < 0.1:
        return "ШАР", "⚠️ Багшид: Ойрын хугацаанд ажиглаж, ярилцаарай. \n👪 Эцэг эхэд: Хүүхэддээ цаг гаргаж, сонирхдог зүйлсийнх нь талаар ярилцаарай."
    else:
        return "НОГООН", "✅ Багшид: Сэтгэл зүй тогтвортой байна. Урамшуулаарай. \n👪 Эцэг эхэд: Хүүхдийнхээ эерэг хандлагыг дэмжиж, байнга урам өгөөрэй."

def light_html(status):
    color = {"УЛААН": "#ff4b4b", "ШАР": "#ffa500", "НОГООН": "#28a745"}.get(status, "#grey")
    return f'<div style="width:15px;height:15px;background:{color};border-radius:50%;display:inline-block;margin-right:8px;box-shadow:0 0 5px {color};"></div>'

# 4. APP-ИЙН ХАРАГДАЦ (INTERFACE)
st.set_page_config(page_title="Ухаалаг Зүрх", page_icon="💖")
st.sidebar.title("Нэвтрэх хэсэг:")
role = st.sidebar.radio("", ["Сурагч", "Багш", "Эцэг эх"])

users = load_json('users.json')
data = load_json('data.json')

# --- СУРАГЧИЙН ХЭСЭГ ---
if role == "Сурагч":
    st.title("💖 Ухаалаг Зүрх")
    st.subheader("Сайн уу? Өнөөдөр сэтгэл санаа нь ямар байна?")
    sid = st.text_input("Өөрийн кодыг оруулна уу (Жишээ нь: S01):")
    
    if sid in users:
        st.info(f"Тавтай морил, {users[sid]['name']}!")
        msg = st.text_area("Юу тохиолдсоноо эсвэл мэдрэмжээ энд бичээрэй...")
        vis = st.selectbox("Хэнд харуулах вэ?", ["Багш болон эцэг эх харна", "Зөвхөн багш харна"])
        
        if st.button("Илгээх"):
            status, advice = get_status_info(msg)
            new_entry = {
                "id": sid, "name": users[sid]['name'], "msg": msg,
                "status": status, "advice": advice, "vis": vis,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            data.append(new_entry)
            save_json('data.json', data)
            st.balloons()
            st.success("Зурвас илгээгдлээ. Чи ганцаараа биш шүү! ✨")
    elif sid:
        st.error("Код буруу байна!")

# --- БАГШИЙН ХЭСЭГ ---
elif role == "Багш":
    st.title("👩‍🏫 Багшийн удирдлага")
    pw = st.text_input("Нууц үг:", type="password")
    
    if pw == "1234": # Нууц үгээ энд өөрчилж болно
        t1, t2, t3 = st.tabs(["📊 Сэтгэл зүйн архив", "➕ Сурагч бүртгэх", "🔑 Код хадгалах"])
        
        with t1:
            st.subheader("🗂️ Сурагчдын ирүүлсэн мэдээлэл")
            if not data: st.write("Одоогоор зурвас ирээгүй байна.")
            for entry in reversed(data):
                st.markdown(f"**{light_html(entry['status'])} {entry['name']}** | {entry['time']}", unsafe_content_usage=True)
                st.write(f"💬 {entry['msg']}")
                st.warning(f"🤖 **AI Зөвлөмж:** \n{entry['advice']}")
                st.caption(f"👁️ Харагдах байдал: {entry['vis']}")
                st.divider()

        with t2:
            st.subheader("➕ Шинэ сурагч нэмэх")
            n_name = st.text_input("Сурагчийн нэр:")
            n_id = st.text_input("Сурагчийн код (S01, S02...):")
            if st.button("Бүртгэх"):
                if n_id and n_name:
                    users[n_id] = {"name": n_name}
                    save_json('users.json', users)
                    st.success(f"{n_name} амжилттай бүртгэгдлээ!")
                else: st.warning("Мэдээллээ бүрэн оруулна уу.")

        with t3:
            st.subheader("🔑 Сурагчдын нэвтрэх кодын жагсаалт")
            if users:
                user_df = pd.DataFrame([{"Нэр": v['name'], "Нэвтрэх код": k} for k, v in users.items()])
                st.table(user_df)
                st.write("💡 Та энэ хүснэгтийг хуулж аваад Excel дээр хадгалаарай.")
            else: st.info("Бүртгэлтэй сурагч байхгүй байна.")

# --- ЭЦЭГ ЭХИЙН ХЭСЭГ ---
elif role == "Эцэг эх":
    st.title("👪 Эцэг эхийн хяналт")
    cid = st.text_input("Хүүхдийн кодыг оруулна уу:")
    
    if cid in users:
        st.subheader(f"✨ {users[cid]['name']}-ийн төлөв байдал")
        c_logs = [d for d in data if d['id'] == cid and d['vis'] == "Багш болон эцэг эх харна"]
        if c_logs:
            latest = c_logs[-1]
            st.markdown(f"### {light_html(latest['status'])} Төлөв: {latest['status']}", unsafe_content_usage=True)
            st.warning(f"🤖 **Зөвлөмж:** \n{latest['advice'].split('Эцэг эхэд: ')[1]}")
        else: st.info("Одоогоор мэдээлэл харагдахгүй байна.")
