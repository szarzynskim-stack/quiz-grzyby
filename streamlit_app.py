import streamlit as st
import random
import requests
import os
from datetime import datetime
import calendar

# 1. Konfiguracja strony
st.set_page_config(page_title="Trener Grzybiarza - Kalendarz", page_icon="🍄", layout="wide")

# 2. Pobieranie zdjęć (Wikipedia)
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
    except: pass
    return None

# 3. Wczytywanie bazy
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

# 4. Inicjalizacja sesji
if 'wybrany_grzyb' not in st.session_state:
    st.session_state.wybrany_grzyb = None
if 'foto_url' not in st.session_state:
    st.session_state.foto_url = None

baza_pelna = wczytaj_baze()

# --- PANEL BOCZNY Z KALENDARZEM ---
st.sidebar.title("📅 Kalendarz Nauki")

# Wybór miesiąca i roku
teraz = datetime.now()
rok = st.sidebar.selectbox("Rok", [2024, 2025], index=1)
miesiac = st.sidebar.slider("Miesiąc", 1, 12, teraz.month)

# Generowanie kalendarza
cal = calendar.monthcalendar(rok, miesiac)
nazwa_miesiaca = calendar.month_name[miesiac]

st.sidebar.subheader(f"{nazwa_miesiaca} {rok}")

# Interaktywne przyciski dni
cols = st.sidebar.columns(7)
dni_tygodnia = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd']
for i, d_nazwa in enumerate(dni_tygodnia):
    cols[i].write(f"**{d_nazwa}**")

dzien_wybrany = None
for week in cal:
    cols = st.sidebar.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write(" ")
        else:
            if cols[i].button(str(day), key=f"d_{day}"):
                dzien_wybrany = day

# --- LOGIKA WYBORU PARTII ---
# Liczymy "dzień roku" dla unikalności partii
if dzien_wybrany:
    dzien_roku = (miesiac - 1) * 31 + dzien_wybrany
    rozmiar = 30
    start = (dzien_roku - 1) * rozmiar
    stop = start + rozmiar
    partia = baza_pelna[start:stop]
    
    st.session_state.partia_info = f"Dzień {dzien_wybrany}: Pozycje {start}-{stop}"
    
    # Automatyczne losowanie po kliknięciu w dzień
    with st.spinner("Szukam zdjęcia dla tej partii..."):
        probki = list(partia)
        random.shuffle(probki)
        znaleziono = False
        for g1, g2 in probki:
            url = pobierz_foto(g1) or pobierz_foto(g2)
            if url:
                st.session_state.wybrany_grzyb = (g1, g2)
                st.session_state.foto_url = url
                znaleziono = True
                break
        if not znaleziono:
            st.error("Brak zdjęć w tej partii grzybów. Spróbuj inny dzień!")

# --- WIDOK GŁÓWNY ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.session_state.foto_url:
    if 'partia_info' in st.session_state:
        st.caption(st.session_state.partia_info)
        
    c1, c2 = st.columns([2, 1])
    with c1:
        st.image(st.session_state.foto_url, use_container_width=True)
    
    with c2:
        # Formularz - NAPRAWIONA SKŁADNIA Z DWUKROPKIEM
        with st.form(key="quiz_main"):
            st.write("### Rozpoznaj gatunek")
            odp = st.text_input("Twoja odpowiedź:")
            if st.form_submit_button("Sprawdź"):
                n1, n2 = st.session_state.wybrany_grzyb
                if odp.strip().lower() in [n1.lower(), n2.lower()]:
                    st.success(f"✅ BRAWO! To {n1} / {n2}")
                    st.balloons()
                else:
                    st.error(f"❌ NIE. To {n1} / {n2}")
                    
    if st.button("Losuj kolejny z tego samego dnia 🔄"):
        st.rerun()
else:
    st.info("👈 Wybierz dzień z kalendarza po lewej stronie, aby rozpocząć naukę danej partii grzybów.")
    st.sidebar.metric("Grzybów w bazie", len(baza_pelna))
