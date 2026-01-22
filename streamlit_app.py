import streamlit as st
import random
import requests
import os
import calendar
from datetime import datetime

# 1. Konfiguracja strony
st.set_page_config(page_title="Trener Grzybiarza 2026", page_icon="🍄", layout="wide")

# 2. Pobieranie zdjęcia z Wikipedii
def pobierz_foto(nazwa):
    if not nazwa or len(nazwa) < 3: return None
    api = "https://pl.wikipedia.org/w/api.php"
    # Szukamy po pełnej nazwie
    params = {
        "action": "query", "format": "json", "prop": "pageimages",
        "titles": nazwa.strip(), "pithumbsize": 800, "redirects": 1
    }
    try:
        r = requests.get(api, params=params, timeout=5).json()
        pages = r.get("query", {}).get("pages", {})
        for p in pages:
            if "thumbnail" in pages[p]:
                return pages[p]["thumbnail"]["source"]
    except: pass
    return None

# 3. Wczytywanie bazy danych
@st.cache_data
def wczytaj_baze():
    lista = []
    sciezka = "grzyby_lista.txt"
    if os.path.exists(sciezka):
        with open(sciezka, "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    pary = linia.strip().split(";")
                    if len(pary) >= 2:
                        lista.append((pary[0].strip(), pary[1].strip()))
    return lista

# Inicjalizacja sesji
if 'foto' not in st.session_state: st.session_state.foto = None
if 'nazwy' not in st.session_state: st.session_state.nazwy = None

baza_pelna = wczytaj_baze()

# --- PANEL BOCZNY: KALENDARZ 2026 ---
st.sidebar.title("📅 Rok 2026")
miesiac_nr = st.sidebar.slider("Wybierz miesiąc", 1, 12, 1)
st.sidebar.subheader(calendar.month_name[miesiac_nr])

cal = calendar.monthcalendar(2026, miesiac_nr)
dzien_wybrany = None

for week in cal:
    cols = st.sidebar.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            if cols[i].button(str(day), key=f"d_{day}_{miesiac_nr}"):
                dzien_wybrany = day

# --- LOGIKA WYBORU ---
if dzien_wybrany:
    # Ustawiamy ziarno losowania na podstawie daty, by dany dzień miał swoje grzyby
    random.seed((miesiac_nr * 31) + dzien_wybrany)
    if baza_pelna:
        # Losujemy partię do sprawdzenia
        ile = min(len(baza_pelna), 30)
        partia = random.sample(baza_pelna, ile)
        
        with st.spinner("Szukam zdjęcia dla grzybów z tego dnia..."):
            znaleziono = False
            for g1, g2 in partia:
                url = pobierz_foto(g1) or pobierz_foto(g2)
                if url:
                    st.session_state.foto = url
                    st.session_state.nazwy = (g1, g2)
                    znaleziono = True
                    break
            
            if znaleziono:
                st.rerun()
            else:
                st.sidebar.error("Nie znaleziono zdjęć w tej partii.")

# --- WIDOK GŁÓWNY ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.session_state.foto:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.image(st.session_state.foto, use_container_width=True)
    with c2:
        with st.form(key="formularz_quiz"):
            st.write("### Rozpoznaj ten gatunek")
