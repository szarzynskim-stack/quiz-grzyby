import streamlit as st
import random
import requests
import os

# Konfiguracja wyświetlania
st.set_page_config(page_title="Trener Grzybiarza 2000", page_icon="🍄", layout="wide")

# Funkcja pobierania zdjęć z Wikipedii
def pobierz_foto(n1, n2):
    api = "https://pl.wikipedia.org/w/api.php"
    for fraza in [n1, n2]:
        params = {
            "action": "query", 
            "format": "json", 
            "prop": "pageimages", 
            "titles": fraza, 
            "pithumbsize": 800
        }
        try:
            r = requests.get(api, params=params, timeout=3).json()
            pages = r.get("query", {}).get("pages", {})
            for p in pages:
                if "thumbnail" in pages[p]:
                    return pages[p]["thumbnail"]["source"]
        except: 
            continue
    return None

# Funkcja wczytywania listy (odporna na puste pliki)
@st.cache_data
def wczytaj_baze():
    lista = []
    sciezka = "grzyby_lista.txt"
    if os.path.exists(sciezka):
        with open(sciezka, "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    czesci = linia.strip().split(";")
                    if len(czesci) >= 2:
                        lista.append((czesci[0].strip(), czesci[1].strip()))
    return list(set(lista))

# Inicjalizacja pamięci sesji
if 'aktualny_grzyb' not in st.session_state:
    st.session_state.aktualny_grzyb = None
if 'aktualne_foto' not in st.session_state:
    st.session_state.aktualne_foto = None

baza = wczytaj_baze()

# PANEL BOCZNY
st.sidebar.title("📊 Statystyki")
st.sidebar.metric("Gatunków w Twoim pliku", len(baza))
if st.sidebar.button("🔄 Odśwież listę z GitHub"):
    st.cache_data.clear()
    st.rerun()

# STRONA GŁÓWNA
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    if not baza:
        st.error("Baza jest pusta! Wklej swoje 2000+ wierszy do pliku grzyby_lista.txt.")
    else:
        with st.spinner("Szukam zdjęcia dla losowego gatunku..."):
            testowa_lista = list(baza)
            random.shuffle(testowa_lista)
            znaleziono = False
            
            # Przeszukujemy bazę, aż trafimy na grzyba z fotką
            for g1, g2 in testowa_lista[:60]:
                url = pobierz_foto(g1, g2)
                if url:
                    st.session_state.aktualny_grzyb = (g1, g2)
                    st.session_state.aktualne_foto = url
                    zn
