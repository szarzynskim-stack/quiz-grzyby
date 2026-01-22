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

if 'foto' not in st.session_state: st.session_state.foto = None
if 'nazwy' not in st.session_state: st.session_state.nazwy = None

baza_pelna = wczytaj_baze()

# --- PANEL BOCZNY: KALENDARZ 2026 ---
st.sidebar.title("📅 Rok 2026")
miesiac = st.sidebar.slider("Wybierz miesiąc", 1, 12, 1)
st.sidebar.subheader(calendar.month_name[miesiac])

cal = calendar.monthcalendar(2026, miesiac)
dzien_wybrany = None

for week in cal:
    cols = st.sidebar.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            if cols[i].button(str(day), key=f"d_{day}_{miesiac}"):
                dzien_wybrany = day

# --- LOGIKA WYBORU GRZYBA (TUTAJ BYŁ BŁĄD - NAPRAWIONO) ---
if dzien_wybrany:
    random.seed((miesiac * 31) + dzien_wybrany)
    if baza_pelna:
        # NAPRAWIONA LINIA:
        ile_grzybow = min(len(baza_pelna), 25)
        partia = random.sample(baza_pelna, ile_grzybow)
        
        with st.spinner("Szukam zdjęcia..."):
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
                st.sidebar.error("Brak zdjęć w tej partii.")

# --- WIDOK GŁÓWNY ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.session_state.foto:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.image(st.session_state.foto, use_container_width=True)
    with c2:
        with st.form(key="quiz_form"):
            odp = st.text_input("Twoja odpowiedź:")
            if st.form_submit_button("Sprawdź"):
                n1, n2 = st.session_state.nazwy
                if odp.strip().lower() in [n1.lower(), n2.lower()]:
                    st.success(f"✅ BRAWO! To: {n1} / {n2}")
                    st.balloons()
                else:
                    st.error(f"❌ NIE. To: {n1} / {n2}")
    
    if st.button("Następny grzyb 🔄"):
        st.session_state.foto = None
        st.rerun()
else:
    st.info("👈
