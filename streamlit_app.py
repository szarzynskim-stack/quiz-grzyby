import streamlit as st
import random
import requests
import os
import calendar
from datetime import datetime

# 1. Konfiguracja i Styl
st.set_page_config(page_title="Trener Grzybiarza 2026", page_icon="🍄", layout="wide")

# 2. Mechanizm pobierania zdjęć (Wikipedia)
def pobierz_foto(nazwa):
    if not nazwa: return None
    api = "https://pl.wikipedia.org/w/api.php"
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
    except:
        pass
    return None

# 3. Wczytywanie Twoich 151 grzybów
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

# 4. Inicjalizacja pamięci programu
if 'grzyb_dnia' not in st.session_state:
    st.session_state.grzyb_dnia = {"foto": None, "nazwy": None}

baza = wczytaj_baze()

# --- PANEL BOCZNY: KALENDARZ 2026 ---
st.sidebar.title("📅 Rok 2026")
miesiac = st.sidebar.selectbox("Miesiąc", list(range(1, 13)), index=0)
st.sidebar.subheader(calendar.month_name[miesiac])

cal = calendar.monthcalendar(2026, miesiac)
dzien_wybrany = None

# Wyświetlanie dni kalendarza jako przyciski
for tyg in cal:
    cols = st.sidebar.columns(7)
    for i, d in enumerate(tyg):
        if d != 0:
            if cols[i].button(str(d), key=f"d_{d}_{miesiac}"):
                dzien_wybrany = d

# --- LOGIKA WYBORU PO KLIKNIĘCIU ---
if dzien_wybrany:
    with st.spinner("Szukam zdjęcia..."):
        # Sprawdzamy wszystkie grzyby po kolei, aż któryś będzie miał zdjęcie
        probki = list(baza)
        random.shuffle(probki)
        znaleziono = False
        
        for g1, g2 in probki[:40]: # Sprawdź pierwsze 40 losowych z Twojej bazy
            url = pobierz_foto(g1) or pobierz_foto(g2)
            if url:
                st.session_state.grzyb_dnia = {"foto": url, "nazwy": (g1, g2)}
                znaleziono = True
                break
        
        if znaleziono:
            st.rerun()
        else:
            st.sidebar.warning("Nie znaleziono zdjęcia dla tej grupy. Kliknij inny dzień!")

# --- WIDOK GŁÓWNY ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.session_state.grzyb_dnia["foto"]:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.image(st.session_state.grzyb_dnia["foto"], use_container_width=True)
    with c2:
        with st.form(key="quiz"):
            st.write("### Co to za grzyb?")
            odp = st.text_input("Twoja odpowiedź:")
            if st.form_submit_button("Sprawdź"):
                n1, n2 = st.session_state.grzyb_dnia["nazwy"]
                if odp.strip().lower() in [n1.lower(), n2.lower()]:
                    st.success(f"✅ BRAWO! To {n1} / {n2}")
                    st.balloons()
                else:
                    st.error(f"❌ BŁĄD. Poprawna nazwa: {n1} / {n2}")
    
    if st.button("Kolejny okaz 🔄"):
        st.session_state.grzyb_dnia = {"foto": None, "nazwy": None}
        st.rerun()
else:
    st.info("👈 Wybierz dzień z kalendarza po lewej stronie, aby rozpocząć.")

st.sidebar.divider()
st.sidebar.metric("Gatunków w bazie", len(baza))
