import streamlit as st
import random
import requests
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Trener Grzybiarza 1000", page_icon="🍄", layout="wide")

def pobierz_obrazek_wikipedii(nazwa_pl, nazwa_lat):
    """Pobiera URL zdjęcia z Wikipedii. Zwraca None jeśli nie znajdzie."""
    for fraza in [nazwa_lat, nazwa_pl]:
        api_url = "https://pl.wikipedia.org/w/api.php"
        params = {
            "action": "query", "format": "json", "prop": "pageimages",
            "titles": fraza, "pithumbsize": 800
        }
        try:
            response = requests.get(api_url, params=params, timeout=2)
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for p in pages:
                if "thumbnail" in pages[p]:
                    return pages[p]["thumbnail"]["source"]
        except:
            continue
    return None

def laduj_baze():
    """Wczytuje unikalne gatunki z pliku txt."""
    dane = {}
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    p, l = linia.strip().split(";")
                    dane[p.strip()] = l.strip()
    return dane

# --- INICJALIZACJA DANYCH ---
baza_grzybow = laduj_baze()

if 'aktywny_grzyb' not in st.session_state:
    st.session_state.aktywny_grzyb = None
if 'foto_url' not in st.session_state:
    st.session_state.foto_url = None

# --- PANEL BOCZNY (STATYSTYKI) ---
with st.sidebar:
    st.header("📊 Statystyki")
    st.write(f"Wszystkich gatunków: **{len(baza_grzybow)}**")
    if st.button("Wyczyść Cache / Reset"):
        st.cache_data.clear()
        st.session_state.aktywny_grzyb = None
        st.session_state.foto_url = None
        st.rerun()

# --- GŁÓWNA CZĘŚĆ APLIKACJI ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("Następny grzyb ➡️"):
        gatunki = list(baza_grzybow.items())
        random.shuffle(gatunki)
        
        znalazlem = False
        with st.spinner("Szukam gatunku ze zdjęciem w Wikipedii..."):
            # Sprawdzamy tylko pierwsze 30 wylosowanych, żeby nie muliło
            for n_pl, n_lat in gatunki[:30]:
                url = pobierz_obrazek_wikipedii(n_pl, n_lat)
                if url:
                    st.session_state.aktywny_grzyb = (n_pl, n_lat)
                    st.
