import streamlit as st
import requests
import random
from datetime import datetime, timedelta
import json
import os
import pandas as pd

# --- KONFIGURACJA I USUWANIE DUBLE ---
st.set_page_config(page_title="Akademia Grzybiarza 1000+", page_icon="🍄", layout="wide")

def wyczysc_liste():
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            linie = f.readlines()
        unikalne = []
        widziane = set()
        for l in linie:
            c = l.strip()
            if c and c not in widziane:
                unikalne.append(l)
                widziane.add(c)
        if len(unikalne) < len(linie):
            with open("grzyby_lista.txt", "w", encoding="utf-8") as f:
                f.writelines(unikalne)

wyczysc_liste()

# --- LOGIKA BAZY DANYCH ---
@st.cache_data
def laduj_baze():
    dane = {}
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    p, l = linia.strip().split(";")
                    dane[p] = l
    return dane if dane else {"Borowik szlachetny": "Boletus edulis"}

def laduj_postepy():
    if os.path.exists("postepy.json"):
        try:
            with open("postepy.json", "r") as f: return json.load(f)
        except: return {}
    return {}

def zapisz_postepy(p):
    with open("postepy.json", "w") as f: json.dump(p, f)

BAZA = laduj_baze()
if 'postepy' not in st.session_state:
    st.session_state.postepy = laduj_postepy()

# --- PANEL BOCZNY (KALENDARZ) ---
st.sidebar.header("📅 Twój Kalendarz")
dzis = datetime.now().date()
plan = []
for i in range(7):
    data = dzis + timedelta(days=i)
    ds = data.strftime("%Y-%m-%d")
    ile = len([v for v in st.session_state.postepy.values() if v <= ds]) if i == 0 else list(st.session_state.postepy.values()).count(ds)
    plan.append({"Dzień": data.strftime("%m-%d"), "Grzyby": ile})
st.sidebar.table(pd.DataFrame(plan))
st.sidebar.metric("Wszystkich gatunków", len(BAZA))

# --- QUIZ I WIKI ---
def losuj():
    dzis_s = datetime.now().strftime("%Y-%m-%d")
    do_powt = [g for g in BAZA.keys() if st.session_state.postepy.get(g, "2000-01-01") <= dzis_s]
    return random.choice(do_powt) if do_powt else random.choice(list(BAZA.keys()))

if 'aktywny' not in st.session_state: st.session_state.aktywny = losuj()
if 'licznik' not in st.session_state: st.session_state.licznik = 0

def get_wiki(lat):
    u = f"https://pl.wikipedia.org/api/rest_v1/page/summary/{lat.replace(' ', '_')}"
    try:
        r = requests.get(u, headers={'User-Agent': 'MushroomBot/1.0'}, timeout=5).json()
        return r.get('thumbnail', {}).get('source'), r.get('extract', '')
    except: return None, ""

img, info = get_wiki(BAZA[st.session_state.aktywny])

st.title("🍄 Profesjonalny Trener Grzybiarza")
c1, c2 = st.columns([1, 1])

with c1:
    if img: st.image(img, use_container_width=True)
    else: st.info("Szukam zdjęcia...")

with c2:
    tryb = st.radio("Zgadujesz:", ["Polska", "Łacina"])
    with st.form("quiz_form"):
        poprawne = st.session_state.aktywny if tryb == "Polska" else BAZA[st.session_state.aktywny]
        odp = st.text_input("Twoja odpowiedź:", key=f"q_{st.session_state.licznik}")
        if st.form_submit_button("Sprawdź"):
            teraz = datetime.now()
            if odp.strip().lower() == poprawne.lower():
                st.success("✅ Świetnie! Powtórka za 7 dni.")
                st.session_state.postepy[st.session_state.aktywny] = (teraz + timedelta(days=7)).strftime("%Y-%m-%d")
                st.balloons()
                st.write(info)
            else:
                st.error(f"❌ To: {poprawne}. Powtórka jutro.")
                st.session_state.postepy[st.session_state.aktywny] = (teraz + timedelta(days=1)).strftime("%Y-%m-%d")
            zapisz_postepy(st.session_state.postepy)

if st.button("Następny grzyb ➡️"):
    st.session_state.aktywny = losuj()
    st.session_state.licznik += 1
    st.rerun()
