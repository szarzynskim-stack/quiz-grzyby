import streamlit as st
import requests
import random
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="Akademia Grzybiarza - Kalendarz", page_icon="🍄")
st.title("🍄 Trener z inteligentnym kalendarzem")

# --- LOGIKA BAZY DANYCH ---
def laduj_liste():
    grzyby = {}
    try:
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    pl, lat = linia.strip().split(";")
                    grzyby[pl] = lat
    except: return {"Borowik szlachetny": "Boletus edulis"}
    return grzyby

# Ładowanie postępów (kiedy powtórzyć dany grzyb)
def laduj_postepy():
    if os.path.exists("postepy.json"):
        with open("postepy.json", "r") as f:
            return json.load(f)
    return {}

def zapisz_postepy(postepy):
    with open("postepy.json", "w") as f:
        json.dump(postepy, f)

BAZA = laduj_liste()
if 'postepy' not in st.session_state:
    st.session_state.postepy = laduj_postepy()

# --- WYBÓR GRZYBA DO NAUKI ---
def losuj_grzyba():
    dzis = datetime.now().strftime("%Y-%m-%d")
    do_powtorki = [g for g in BAZA.keys() if st.session_state.postepy.get(g, "2000-01-01") <= dzis]
    
    if do_powtorki:
        return random.choice(do_powtorki)
    return random.choice(list(BAZA.keys()))

if 'wybrany' not in st.session_state:
    st.session_state.wybrany = losuj_grzyba()
if 'licznik' not in st.session_state:
    st.session_state.licznik = 0

# --- POBIERANIE DANYCH Z WIKI ---
def get_wiki(latin):
    url = f"https://pl.wikipedia.org/api/rest_v1/page/summary/{latin.replace(' ', '_')}"
    try:
        res = requests.get(url, headers={'User-Agent': 'QuizBot/1.0'}, timeout=5).json()
        return res.get('thumbnail', {}).get('source'), res.get('extract', 'Brak opisu.')
    except: return None, ""

img, info = get_wiki(BAZA[st.session_state.wybrany])

# --- INTERFEJS ---
if img: st.image(img, use_container_width=True)

poziom = st.radio("Tryb:", ["Polska nazwa", "Łacina"])
with st.form("quiz_form"):
    cel = st.session_state.wybrany if poziom == "Polska nazwa" else BAZA[st.session_state.wybrany]
    odp = st.text_input("Twoja odpowiedź:", key=f"in_{st.session_state.licznik}")
    
    if st.form_submit_button("Sprawdź"):
        dzis_dt = datetime.now()
        if odp.strip().lower() == cel.lower():
            st.success(f"✅ BRAWO! Następna powtórka tego grzyba za 7 dni.")
            # Ustawiamy powtórkę za 7 dni
            st.session_state.postepy[st.session_state.wybrany] = (dzis_dt + timedelta(days=7)).strftime("%Y-%m-%d")
            st.balloons()
            st.info(info)
        else:
            st.error(f"❌ BŁĄD. To był: {cel}. Powtórka jutro!")
            # Ustawiamy powtórkę na jutro
            st.session_state.postepy[st.session_state.wybrany] = (dzis_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        
        zapisz_postepy(st.session_state.postepy)

if st.button("Następny grzyb (z kalendarza) ➡️"):
    st.session_state.wybrany = losuj_grzyba()
    st.session_state.licznik += 1
    st.rerun()

# Statystyki na boku
st.sidebar.write(f"Wszystkich grzybów: {len(BAZA)}")
st.sidebar.write(f"Opanowanych (powtórka w przyszłości): {len([v for v in st.session_state.postepy.values() if v > datetime.now().strftime('%Y-%m-%d')])}")
