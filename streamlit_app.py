import streamlit as st
import requests
import random
from datetime import datetime, timedelta
import json
import os
import pandas as pd

st.set_page_config(page_title="Akademia Grzybiarza", page_icon="🍄", layout="wide")

# --- FUNKCJE POMOCNICZE ---
def laduj_liste():
    grzyby = {}
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    pl, lat = linia.strip().split(";")
                    grzyby[pl] = lat
    # Jeśli plik jest pusty, dodaj 2 podstawowe grzyby na start
    if not grzyby:
        grzyby = {"Borowik szlachetny": "Boletus edulis", "Muchomor czerwony": "Amanita muscaria"}
    return grzyby

def laduj_postepy():
    if os.path.exists("postepy.json"):
        try:
            with open("postepy.json", "r") as f:
                return json.load(f)
        except: return {}
    return {}

def zapisz_postepy(postepy):
    with open("postepy.json", "w") as f:
        json.dump(postepy, f)

# --- INICJALIZACJA ---
BAZA = laduj_liste()
if 'postepy' not in st.session_state:
    st.session_state.postepy = laduj_postepy()

# --- BOCZNY PANEL (KALENDARZ) ---
def pokaz_sidebar():
    st.sidebar.header("📅 Twój Plan")
    dzis = datetime.now().date()
    dni = [(dzis + timedelta(days=i)) for i in range(7)]
    
    plan = []
    for d in dni:
        d_str = d.strftime("%Y-%m-%d")
        # Liczymy ile grzybów ma zaplanowaną powtórkę na ten dzień lub wcześniej (dla dzisiaj)
        if d == dzis:
            ile = len([v for v in st.session_state.postepy.values() if v <= d_str])
        else:
            ile = list(st.session_state.postepy.values()).count(d_str)
        
        plan.append({"Data": d.strftime("%m-%d"), "Grzyby": ile})
    
    st.sidebar.table(pd.DataFrame(plan))
    st.sidebar.metric("W bazie", len(BAZA))

pokaz_sidebar()

# --- LOGIKA QUIZU ---
def losuj_grzyba():
    dzis = datetime.now().strftime("%Y-%m-%d")
    # Szukaj grzybów do powtórki na dziś
    do_powtorki = [g for g in BAZA.keys() if st.session_state.postepy.get(g, "2000-01-01") <= dzis]
    if do_powtorki:
        return random.choice(do_powtorki)
    return random.choice(list(BAZA.keys()))

if 'wybrany' not in st.session_state:
    st.session_state.wybrany = losuj_grzyba()
if 'licznik' not in st.session_state:
    st.session_state.licznik = 0

# --- INTERFEJS GŁÓWNY ---
st.title("🍄 Akademia Grzybiarza 1000+")

def get_wiki(latin):
    url = f"https://pl.wikipedia.org/api/rest_v1/page/summary/{latin.replace(' ', '_')}"
    try:
        res = requests.get(url, headers={'User-Agent': 'QuizBot/1.0'}, timeout=5).json()
        return res.get('thumbnail', {}).get('source'), res.get('extract', 'Brak opisu.')
    except: return None, "Błąd pobierania danych."

img, info = get_wiki(BAZA[st.session_state.wybrany])

col1, col2 = st.columns([1, 1])

with col1:
    if img:
        st.image(img, use_container_width=True)
    else:
        st.info("Trwa szukanie zdjęcia...")

with col2:
    poziom = st.radio("Zgadujesz:", ["Nazwa polska", "Nazwa łacińska"])
    with st.form("quiz"):
        cel = st.session_state.wybrany if poziom == "Nazwa polska" else BAZA[st.session_state.wybrany]
        odp = st.text_input("Wpisz nazwę:", key=f"input_{st.session_state.licznik}")
        
        if st.form_submit_button("Sprawdź"):
            dzis_dt = datetime.now()
            if odp.strip().lower() == cel.lower():
                st.success("✅ BRAWO! Powtórka za 7 dni.")
                st.session_state.postepy[st.session_state.wybrany] = (dzis_dt + timedelta(days=7)).strftime("%Y-%m-%d")
                st.balloons()
                st.write(info)
            else:
                st.error(f"❌ To był: {cel}. Powtórka jutro.")
                st.session_state.postepy[st.session_state.wybrany] = (dzis_dt + timedelta(days=1)).strftime("%Y-%m-%d")
            zapisz_postepy(st.session_state.postepy)

if st.button("Następny grzyb ➡️"):
    st.session_state.wybrany = losuj_grzyba()
    st.session_state.licznik += 1
    st.rerun()
