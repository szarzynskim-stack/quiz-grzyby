import streamlit as st
import requests
import random

st.set_page_config(page_title="Akademia Grzybiarza 1000+", page_icon="🍄")
st.title("🍄 Profesjonalny Quiz Mykologiczny")

# Funkcja wczytująca listę z pliku
@st.cache_data
def laduj_grzyby():
    grzyby = {}
    with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
        for linia in f:
            if ";" in linia:
                pl, lat = linia.strip().split(";")
                grzyby[pl] = lat
    return grzyby

BAZA = laduj_grzyby()

if 'wybrany' not in st.session_state:
    st.session_state.wybrany = random.choice(list(BAZA.keys()))

def get_wiki(latin):
    url = f"https://pl.wikipedia.org/api/rest_v1/page/summary/{latin.replace(' ', '_')}"
    res = requests.get(url, headers={'User-Agent': 'QuizBot/1.0'}).json()
    return res.get('thumbnail', {}).get('source'), res.get('extract', '')

img, info = get_wiki(BAZA[st.session_state.wybrany])

if img: st.image(img, use_container_width=True)
else: st.warning("Brak zdjęcia w bazie. Kliknij Następny.")

poziom = st.radio("Poziom:", ["Polska nazwa", "Łacina"])

with st.form("quiz"):
    cel = st.session_state.wybrany if poziom == "Polska nazwa" else BAZA[st.session_state.wybrany]
    odp = st.text_input("Twoja odpowiedź:")
    if st.form_submit_button("Sprawdź"):
        if odp.lower() == cel.lower():
            st.success(f"✅ GENIALNIE! To {st.session_state.wybrany} ({BAZA[st.session_state.wybrany]})")
            st.info(info) # Pokazuje encyklopedyczny opis grzyba!
            st.balloons()
        else:
            st.error(f"❌ PUDŁO. Poprawna nazwa to: {cel}")

if st.button("Następny grzyb ➡️"):
    st.session_state.wybrany = random.choice(list(BAZA.keys()))
    st.rerun()
