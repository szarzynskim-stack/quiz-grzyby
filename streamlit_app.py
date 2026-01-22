import streamlit as st
import random
import requests
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Trener Grzybiarza 1000", page_icon="🍄", layout="wide")

def pobierz_zdjecie(nazwa_pl, nazwa_lat):
    """Pobiera zdjęcie z Wikipedii. Zwraca None, jeśli nie znajdzie."""
    for fraza in [nazwa_lat, nazwa_pl]:
        api_url = "https://pl.wikipedia.org/w/api.php"
        params = {
            "action": "query", "format": "json", "prop": "pageimages",
            "titles": fraza, "pithumbsize": 800
        }
        try:
            r = requests.get(api_url, params=params, timeout=2)
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            for p in pages:
                if "thumbnail" in pages[p]:
                    return pages[p]["thumbnail"]["source"]
        except:
            continue
    return None

def wczytaj_grzyby():
    """Ładuje gatunki z pliku txt."""
    lista = {}
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    p, l = linia.strip().split(";")
                    lista[p.strip()] = l.strip()
    return lista

# --- START APLIKACJI ---
baza = wczytaj_grzyby()

# Inicjalizacja sesji
if 'grzyb_teraz' not in st.session_state:
    st.session_state.grzyb_teraz = None
if 'foto_url' not in st.session_state:
    st.session_state.foto_url = None

# PANEL BOCZNY
with st.sidebar:
    st.header("📊 Statystyki")
    st.write(f"Wszystkich gatunków: **{len(baza)}**")
    if st.button("Wyczyść pamięć i odśwież"):
        st.cache_data.clear()
        st.session_state.grzyb_teraz = None
        st.session_state.foto_url = None
        st.rerun()

# GŁÓWNA CZĘŚĆ
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    gatunki = list(baza.items())
    random.shuffle(gatunki)
    
    with st.spinner("Szukam grzyba ze zdjęciem..."):
        znaleziono = False
        # Sprawdzamy pierwsze 25 losowych grzybów
        for n_pl, n_lat in gatunki[:25]:
            url = pobierz_zdjecie(n_pl, n_lat)
            if url:
                st
