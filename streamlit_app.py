import streamlit as st
import random
import requests
import os

# --- KONFIGURACJA ---
st.set_page_config(page_title="Trener Grzybiarza 1000", page_icon="🍄")

# Funkcja pobierająca obrazek z zabezpieczeniem przed zawieszeniem
def pobierz_obrazek(nazwa_pl, nazwa_lat):
    api_url = "https://pl.wikipedia.org/w/api.php"
    # Szukamy najpierw po łacinie, potem po polsku
    for fraza in [nazwa_lat, nazwa_pl]:
        params = {
            "action": "query", "format": "json", "prop": "pageimages",
            "titles": fraza, "pithumbsize": 600
        }
        try:
            # Bardzo krótki timeout (2 sekundy), żeby aplikacja nie muliła
            res = requests.get(api_url, params=params, timeout=2).json()
            pages = res.get("query", {}).get("pages", {})
            for p in pages:
                if "thumbnail" in pages[p]:
                    return pages[p]["thumbnail"]["source"]
        except:
            continue
    return None

def laduj_baze():
    dane = {}
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    p, l = linia.strip().split(";")
                    dane[p.strip()] = l.strip()
    return dane

# --- INICJALIZACJA ---
baza = laduj_baze()

if 'grzyb_dane' not in st.session_state:
    st.session_state.grzyb_dane = None
if 'foto_url' not in st.session_state:
    st.session_state.foto_url = None

# --- PANEL BOCZNY ---
st.sidebar.header("📊 Statystyki")
st.sidebar.write(f"Gatunki w bazie: **{len(baza)}**")
if st.sidebar.button("Wyczyść Cache / Odśwież"):
    st.cache_data.clear()
    st.session_state.grzyb_dane = None
    st.session_state.foto_url = None
    st.rerun()

# --- GŁÓWNA CZĘŚĆ ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    gatunki = list(baza.items())
    random.shuffle(gatunki)
    
    znaleziono = False
    with st.spinner("Szukam gatunku ze zdjęciem..."):
        # Sprawdzamy pierwsze 20 wylosowanych, żeby nie czekać wiecznie
        for n_pl, n_lat in gatunki[:20]:
            url = pobierz_obrazek(n_pl, n_lat)
            if url:
                st.session_state.grzyb_dane = (n_pl, n_lat)
                st.session_state.foto_url = url
                znaleziono = True
                break
    
    if not znaleziono:
        st.warning("Tym razem Wikipedia nie zwróciła zdjęcia. Spróbuj jeszcze raz!")
    else:
        st.rerun() # Odśwież, żeby pokazać nowe zdjęcie

# --- WYŚWIETLANIE ZAGADKI ---
if st.session_state.foto_url:
    st.image(st.session_state.foto_url, caption="Jak nazywa się ten grzyb?")
    
    with st.form
