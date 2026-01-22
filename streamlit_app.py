import streamlit as st
import random
import requests
import os
import calendar
from datetime import datetime

# 1. Konfiguracja strony
st.set_page_config(page_title="Trener Grzybiarza 2026", page_icon="🍄", layout="wide")

# 2. Inteligentne pobieranie zdjęcia z Wikipedii
def pobierz_foto(nazwa):
    if not nazwa or len(nazwa) < 3: return None
    api = "https://pl.wikipedia.org/w/api.php"
    
    # Próbujemy: 1. Pełna nazwa, 2. Pierwszy człon (rodzaj)
    frazy = [nazwa, nazwa.split()[0]]
    
    for f in frazy:
        params = {
            "action": "query", "format": "json", "prop": "pageimages",
            "titles": f, "pithumbsize": 800, "redirects": 1
        }
        try:
            r = requests.get(api, params=params, timeout=5).json()
            pages = r.get("query", {}).get("pages", {})
            for p in pages:
                if "thumbnail" in pages[p]:
                    return pages[p]["thumbnail"]["source"]
        except: continue
    return None

# 3. Wczytywanie bazy danych
@st.cache_data
def wczytaj_baze():
    lista = []
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    pary = linia.strip().split(";")
                    if len(pary) >= 2:
                        lista.append((pary[0].strip(), pary[1].strip()))
    return lista

# Inicjalizacja stanu gry
if 'foto' not in st.session_state: st.session_state.foto = None
if 'nazwy' not in st.session_state: st.session_state.nazwy = None

baza_pelna = wczytaj_baze()

# --- PANEL BOCZNY: KALENDARZ 2026 ---
st.sidebar.title("📅 Rok 2026")
miesiac = st.sidebar.slider("Wybierz miesiąc", 1, 12, datetime.now().month)
st.sidebar.subheader(calendar.month_name[miesiac])

cal = calendar.monthcalendar(2026, miesiac)
cols_head = st.sidebar.columns(7)
for i, d in enumerate(['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd']):
    cols_head[i].caption(d)

dzien_wybrany = None
for week in cal:
    cols = st.sidebar.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            if cols[i].button(str(day), key=f"d_{day}_{miesiac}"):
                dzien_wybrany = day

# --- LOGIKA WYBORU GRZYBA ---
if dzien_wybrany:
    # Każdy dzień roku to inna partia (seed zapewnia, że ten sam dzień daje te same grzyby)
    dzien_id = (miesiac * 31) + dzien_wybrany
    random.seed(dzien_id)
    
    # Wybieramy partię 20 grzybów z Twojej listy
    if baza_pelna:
        partia = random.sample(baza_pelna, min(len(
