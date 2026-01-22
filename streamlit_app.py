import streamlit as st
import requests
import random

st.set_page_config(page_title="Akademia Grzybiarza 1000+", page_icon="🍄")
st.title("🍄 Profesjonalny Quiz Mykologiczny")

# Funkcja wczytująca listę z pliku
@st.cache_data
def laduj_grzyby():
    grzyby = {}
    try:
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    pl, lat = linia.strip().split(";")
                    grzyby[pl] = lat
    except FileNotFoundError:
        return {"Borowik szlachetny": "Boletus edulis"} # Dane ratunkowe
    return grzyby

BAZA = laduj_grzyby()

# Inicjalizacja stanu gry
if 'wybrany' not in st.session_state:
    st.session_state.wybrany = random.choice(list(BAZA.keys()))
if 'licznik_testu' not in st.session_state:
    st.session_state.licznik_testu = 0

def get_wiki(latin):
    url = f"https://pl.wikipedia.org/api/rest_v1/page/summary/{latin.replace(' ', '_')}"
    try:
        res = requests.get(url, headers={'User-Agent': 'QuizBot/1.0'}, timeout=5).json()
        return res.get('thumbnail', {}).get('source'), res.get('extract', 'Brak opisu.')
    except:
        return None, "Błąd połączenia z Wikipedią."

img, info = get_wiki(BAZA[st.session_state.wybrany])

if img: 
    st.image(img, use_container_width=True)
else: 
    st.warning("Brak zdjęcia w bazie Wikipedii dla tego gatunku.")

poziom = st.radio("Wybierz tryb nauki:", ["Polska nazwa", "Nazwa łacińska"])

# Formularz z unikalnym kluczem, który czyści pole po zmianie grzyba
with st.form("quiz_form", clear_on_submit=False):
    cel = st.session_state.wybrany if poziom == "Polska nazwa" else BAZA[st.session_state.wybrany]
    
    # Klucz pola zależy od licznika - gdy licznik rośnie, pole się czyści
    odp = st.text_input("Twoja odpowiedź:", key=f"input_{st.session_state.licznik_testu}")
    
    sprawdz = st.form_submit_button("Sprawdź")
    
    if sprawdz:
        if odp.strip().lower() == cel.lower():
            st.success(f"✅ DOSKONALE! To {st.session_state.wybrany} ({BAZA[st.session_state.wybrany]})")
            st.balloons()
            st.info(info)
        else:
            st.error(f"❌ NIESTETY. Poprawna odpowiedź to: {cel}")

# Przycisk następnego grzyba zwiększa licznik, co wymusza czyszczenie pola tekstowego
if st.button("Następny grzyb ➡️"):
    st.session_state.wybrany = random.choice(list(BAZA.keys()))
    st.session_state.licznik_testu += 1
    st.rerun()
