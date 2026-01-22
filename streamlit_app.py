import streamlit as st
import random
import requests
import os
import calendar
from datetime import datetime

# 1. Konfiguracja
st.set_page_config(page_title="Trener Grzybiarza 2026", page_icon="🍄")

def pobierz_foto(nazwa):
    api = "https://pl.wikipedia.org/w/api.php"
    params = {"action": "query", "format": "json", "prop": "pageimages", "titles": nazwa, "pithumbsize": 800, "redirects": 1}
    try:
        r = requests.get(api, params=params, timeout=5).json()
        pages = r.get("query", {}).get("pages", {})
        for p in pages:
            if "thumbnail" in pages[p]: return pages[p]["thumbnail"]["source"]
    except: pass
    return None

@st.cache_data
def wczytaj_baze():
    lista = []
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    pary = linia.strip().split(";")
                    lista.append((pary[0].strip(), pary[1].strip()))
    return lista

if 'gra' not in st.session_state: st.session_state.gra = {"foto": None, "nazwy": None}

baza = wczytaj_baze()

# --- BOCZNY PANEL: KALENDARZ 2026 ---
st.sidebar.title("📅 Rok 2026")
miesiac = st.sidebar.slider("Miesiąc", 1, 12, datetime.now().month)
cal = calendar.monthcalendar(2026, miesiac)

st.sidebar.write(f"### {calendar.month_name[miesiac]}")
dzien_klikniety = None

for week in cal:
    cols = st.sidebar.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            if cols[i].button(str(day), key=f"d_{day}"):
                dzien_klikniety = day

# --- LOGIKA WYBORU ---
if dzien_klikniety:
    # Wybieramy partię 25 grzybów na dany dzień
    start = (dzien_klikniety + (miesiac * 30)) % (len(baza) if baza else 1)
    partia = baza[start : start + 25]
    
    with st.spinner("Szukam zdjęcia..."):
        random.shuffle(partia)
        for g1, g2 in partia:
            url = pobierz_foto(g1) or pobierz_foto(g2)
            if url:
                st.session_state.gra
