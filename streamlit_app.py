import streamlit as st
import requests
import random
from datetime import datetime, timedelta
import json
import os
import pandas as pd

# --- FUNKCJA NAPRAWCZA (USUWA DUBLE) ---
def usun_duble_z_pliku():
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            linie = f.readlines()
        unikalne = []
        widziane = set()
        for linia in linie:
            clean = linia.strip()
            if clean and clean not in widziane:
                unikalne.append(linia + "\n")
                widziane.add(clean)
        if len(unikalne) < len(linie):
            with open("grzyby_lista.txt", "w", encoding="utf-8") as f:
                f.writelines(unikalne)

st.set_page_config(page_title="Akademia Grzybiarza 1000+", page_icon="🍄", layout="wide")
usun_duble_z_pliku()

# --- LOGIKA DANYCH ---
@st.cache_data
def laduj_liste():
    grzyby = {}
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    pl, lat = linia.strip().split(";")
                    grzyby[pl] = lat
    return grzyby if grzyby else {"Borowik szlachetny": "Boletus edulis"}

def laduj_postepy():
    if os.path.exists("postepy.json"):
        try:
            with open("postepy.json", "r") as f: return json.load(f)
        except: return {}
    return {}

def zapisz_postepy(postepy):
    with open("postepy.json", "w") as f: json.dump(postepy, f)

BAZA = laduj_liste()
if 'postepy' not in st.session_state:
    st.session_state.postepy = laduj_postepy()

# --- SIDEBAR ---
def pokaz_sidebar():
    st.sidebar.header("📅 Twój Plan Nauki")
    dzis = datetime.now().date()
    plan = []
    for i in range(7):
        d = dzis + timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        if i == 0:
            ile = len([v for v in st.session_state.postepy.values() if v <= d_str])
        else:
            ile = list(st.session_state.postepy.values()).count(d_str)
        plan.append({"Data": d.strftime("%m-%d"), "Grzyby": ile})
    st.sidebar.table(pd.DataFrame(plan))
    st.sidebar.metric("Gatunków w bazie", len(BAZA))

pokaz_sidebar()

# --- QUIZ ---
def losuj_grzyba():
    dzis = datetime.now().strftime("%Y-%m-%d")
    do_powtorki = [g for g in BAZA.keys() if st.session_state.postepy.get(g, "2000-01-01") <= dzis]
    return random.choice(do_powtorki) if do_powtorki else random.choice(list(BAZA.keys()))

if 'wybrany' not in st.session_state:
    st.session_state.wybrany = losuj_grzyba()
if 'licznik' not in st.session_state:
    st.session_state.licznik = 0

st.title("🍄 Profesjonalny Trener Grzybiarza")

def get_wiki(latin):
    url = f"https://pl.wikipedia.org/api/rest_v1/page/summary/{latin.replace(' ', '_')}"
    try:
        res = requests.get(url, headers={'User-Agent': 'QuizBot/1.0'}, timeout=5).json()
        return res.get('thumbnail', {}).get('source'), res.get('extract', 'Brak opisu.')
    except: return None, ""

img, info = get_wiki(BAZA[st.session_state.wybrany])
col1, col2 = st.columns([1, 1])

with col1:
    if img: st.image(img, use_container_width=True)
    else: st.info("Szukam zdjęcia w archiwach...")

with col2:
    poziom = st.radio("Zgadujesz:", ["Nazwa polska", "Nazwa łacińska"])
    with st.form("quiz"):
