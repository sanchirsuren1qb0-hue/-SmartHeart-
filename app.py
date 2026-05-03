import streamlit as st
from textblob import TextBlob
import json
import os
from datetime import datetime
import pandas as pd

# AI сангуудыг бэлтгэх
os.system('python -m textblob.download_corpora')

# Файл байгаа эсэхийг шалгах, байхгүй бол үүсгэх
def init_files():
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f: json.dump({}, f)
    if not os.path.exists('data.json'):
        with open('data.json', 'w') as f: json.dump([], f)

init_files()

# Өгөгдөл унших функцууд
def load_users():
    with open('users.json', 'r') as f: return json.load(f)

def save_users(users):
    with open('users.json', 'w') as f: json.dump(users, f)

def load_data():
    with open('data.json', 'r') as f: return json.load(f)

def save_data(data):
    with open('data.json', 'w') as f: json.dump(data, f)

# ГЭРЛЭН ДОХИОНЫ STYLE
def light_style(status):
    colors = {"УЛААН": "#ff4b4b", "ШАР": "#ffa500", "НОГООН": "#28a745"}
    c = colors.get(status, "#grey")
    return f'<div style="width: 20px; height: 20px; background-color: {c}; border-radius: 50%; display: inline-block; margin-right: 10px; box-shadow: 0 0 10px {c};"></div>'

# AI ЗӨВЛӨМЖ ӨГӨХ ФУНКЦ
def get_ai_advice(text):
    analysis = TextBlob(text)
    score = analysis.sentiment.polarity
    
    if score < -0.2:
        return "УЛААН", "🆘 Багшид: Нэн яаралтай ганцаарчилж уулзах шаардлагатай. \n👪 Эцэг эхэд: Хүүхэдтэйгээ маш тайван ярилцаж, мэргэжлийн сэтгэл зүйчид хандахыг зөвлөж байна."
    elif score < 0.1:
        return "ШАР", "⚠️ Багшид: Ойрын хугацаанд анхаарал хандуулж, ажиглаарай. \n👪 Эцэг эхэд: Хүүхдийнхээ сонирхдог зүйлийн талаар ярилцаж, цагийг хамт өнгөрүүлээрэй."
    else:
        return "НОГООН", "✅ Багшид: Сэтгэл зүй тогтвортой байна. Урамшуулаарай. \n👪 Эцэг эхэд: Хүүхдийнхээ эерэг хандлагыг дэмжиж, байнга урам өгч байгаарай."

# APP-ИЙН ҮНДСЭН ХЭСЭГ
st.set_page_config(page_title="Ухаалаг Зүрх", page_icon="💖")
st.sidebar.title("Нэвтрэх хэсэг:")
role = st.sidebar.radio("", ["Сурагч", "Багш", "Эцэг эх"])

users = load_users()
data = load_data()

# --- СУРАГЧ ХЭСЭГ ---
if role == "Сурагч":
    st.title("💖 Ухаалаг Зүрх - Сурагч")
    student_id = st.text_input("Өөрийн кодыг оруулна уу:")
    
    if student_id in users:
        st.success(f"Сайн уу, {users[student_id]['name']}!")
        message = st.text_area("Өнөөдөр сэтгэл санаа нь ямар байна? Юу тохиолдсоноо хуваалцаарай...")
        visibility = st.selectbox("Хэнд харуулах вэ?", ["Багш болон эцэг эх харна", "Зөвхөн багш харна"])
        
        if st.button("Илгээх"):
            status, advice = get_ai_advice(message)
            new_entry = {
                "id": student_id,
                "name": users[student_id]['name'],
                "message": message,
                "status": status,
                "advice": advice,
                "visibility": visibility,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            data.append(new_entry)
            save_data(data)
            st.balloons()
            st.info("Зурвас амжилттай илгээгдлээ. Өөртөө итгэлтэй байгаарай! ✨")
    elif student_id:
        st.error("Код буруу байна!")

# --- БАГШ ХЭСЭГ ---
elif role == "Багш":
    st.title("👩‍🏫 Багшийн удирдлага")
    password = st.text_input("Нууц үг:", type="password")
    
    if password == "1234": # Та нууц үгээ энд өөрчилж болно
        tab1, tab2, tab3 = st.tabs(["📊 Архив", "➕ Сурагч нэмэх", "🔑 Код хадгалах"])
        
        with tab1:
            st.subheader("🗂️ Сэтгэл зүйн архивын жагсаалт")
            for entry in reversed(data):
                st.markdown(f"### {light_style(entry['status'])} ТӨЛӨВ: {entry['status']}", unsafe_content_usage=True)
                st.write(f"**Хэнээс:** {entry['name']} | **Цаг:** {entry['time']}")
                st.info(f"💬 {entry['message']}")
                st.warning(f"🤖 **AI Зөвлөмж:** \n{entry['advice']}")
                st.divider()

        with tab2:
            st.subheader("➕ Шинэ сурагч бүртгэх")
            new_name = st.text_input("Сурагчийн нэр:")
            new_id = st.text_input("Сурагчийн код (Жишээ нь: S01):")
            if st.button("Бүртгэх"):
                if new_id not in users:
                    users[new_id] = {"name": new_name}
                    save_users(users)
                    st.success(f"{new_name} амжилттай бүртгэгдлээ!")
                else:
                    st.warning("Энэ код аль хэдийн бүртгэгдсэн байна.")

        with tab3:
            st.subheader("🔑 Сурагчдын нэвтрэх кодын жагсаалт")
            if users:
                user_list = [{"Нэр": v['name'], "Нэвтрэх код": k} for k, v in users.items()]
                st.table(pd.DataFrame(user_list))
                st.write("💡 Энэ кодыг эцэг эх болон сурагчдад тарааж өгнө үү.")
            else:
                st.info("Бүртгэлтэй сурагч байхгүй байна.")

# --- ЭЦЭГ ЭХ ХЭСЭГ ---
elif role == "Эцэг эх":
    st.title("👪 Эцэг эхийн хяналт")
    child_id = st.text_input("Хүүхдийн кодыг оруулна уу:")
    
    if child_id in users:
        st.subheader(f"✨ {users[child_id]['name']}-ийн төлөв")
        child_data = [d for d in data if d['id'] == child_id and d['visibility'] == "Багш болон эцэг эх харна"]
        
        if child_data:
            latest = child_data[-1]
            st.markdown(f"### {light_style(latest['status'])} Сүүлийн төлөв: {latest['status']}", unsafe_content_usage=True)
            st.warning(f"🤖 **Зөвлөмж:** \n{latest['advice'].split('Эцэг эхэд: ')[1]}")
        else:
            st.info("Одоогоор мэдээлэл байхгүй байна.")
