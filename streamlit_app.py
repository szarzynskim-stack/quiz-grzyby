import streamlit as st
import random
import requests
import os

# 1. Konfiguracja strony
st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")

# 2. Proste pobieranie zdjęcia
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

# 3. Wczytywanie Twojej listy 151 grzybów
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

# Inicjalizacja pamięci
if 'grzyb' not in st.session_state:
    st.session_state.grzyb = {"foto": None, "nazwy": None}

baza = wczytaj_baze()

# --- PANEL BOCZNY ---
st.sidebar.title("🍄 Statystyki")
st.sidebar.metric("Liczba grzybów w bazie", len(baza))
if st.sidebar.button("Odśwież bazę z GitHub"):
    st.cache_data.clear()
    st.rerun()

# --- STRONA GŁÓWNA ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

# Główny przycisk
if st.button("LOSUJ GRZYBA ➡️"):
    if not baza:
        st.error("Nie znaleziono pliku grzyby_lista.txt lub jest on pusty!")
    else:
        with st.spinner("Szukam zdjęcia w bazie 151 grzybów..."):
            # Mieszamy listę i szukamy pierwszego, który ma zdjęcie
            testowa_lista = list(baza)
            random.shuffle(testowa_lista)
            
            znaleziono = False
            for n1, n2 in testowa_lista:
                # Sprawdzamy obie nazwy (polska/łacina)
                url = pobierz_foto(n
