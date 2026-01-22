import streamlit as st
import requests
import random

# Lista grzybów (Polska nazwa : Nazwa łacińska)
GRZYBY = {
    "Borowik szlachetny": "Boletus edulis",
    "Podgrzybek brunatny": "Imleria badia",
    "Czubajka kania": "Macrolepiota procera",
    "Pieprznik jadalny": "Cantharellus cibarius",
    "Muchomor czerwony": "Amanita muscaria",
    "Muchomor sromotnikowy": "Amanita phalloides",
    "Maślak zwyczajny": "Suillus luteus",
    "Koźlarz babka": "Leccinum scabrum",
    "Mleczaj rydz": "Lactarius deliciosus",
    "Gąska zielonka": "Tricholoma equestre",
    "Prawdziwek": "Boletus edulis"
}

st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")
st.title("🍄 Trener Grzybiarza")

if 'grzyb' not in st.session_state:
    st.session_state.grzyb = random.choice(list(GRZYBY.keys()))

def get_wiki_image(latin_name):
    # Najbardziej stabilny sposób na pobranie miniatury z Wikipedii
    url = f"https://pl.wikipedia.org/api/rest_v1/page/summary/{latin_name.replace(' ', '_')}"
    headers = {'User-Agent': 'GrzybyQuiz/1.0'}
    try:
        response = requests.get(url, headers=headers).json()
        return response.get('thumbnail', {}).get('source')
    except:
        return None

# Poziom trudności
poziom = st.radio("Wybierz poziom:", ["Łatwy (Polski)", "Trudny (Łacina)"])

# Wyświetlanie zdjęcia
img_url = get_wiki_image(GRZYBY[st.session_state.grzyb])

if img_url:
    st.image(img_url, use_container_width=True)
else:
    st.warning("Szukam zdjęcia w lesie... Jeśli nie ma, kliknij 'Następny'")

with st.form("quiz"):
    if poziom == "Łatwy (Polski)":
        odp = st.selectbox("Co to za grzyb?", ["---"] + sorted(list(GRZYBY.keys())))
        poprawna = st.session_state.grzyb
    else:
        odp = st.text_input("Podaj nazwę łacińską:")
        poprawna = GRZYBY[st.session_state.grzyb]

    if st.form_submit_button("Sprawdź"):
        if odp.lower() == poprawna.lower():
            st.success(f"✅ BRAWO! To {st.session_state.grzyb}")
            st.balloons()
        else:
            st.error(f"❌ PUDŁO! To: {st.session_state.grzyb} ({GRZYBY[st.session_state.grzyb]})")

if st.button("Następny grzyb ➡️"):
    st.session_state.grzyb = random.choice(list(GRZYBY.keys()))
    st.rerun()
