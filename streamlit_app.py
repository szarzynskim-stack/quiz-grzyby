import streamlit as st
import random
import requests
import os

# Konfiguracja strony
st.set_page_config(page_title="Trener Grzybiarza 2000", page_icon="🍄", layout="wide")

# FUNKCJA POBIERANIA FOTO Z WIKIPEDII
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

# FUNKCJA WCZYTYWANIA TWOJEJ WIELKIEJ LISTY
@st.cache_data
def wczytaj_wszystko():
    lista = []
    sciezka = "grzyby_lista.txt"
    if os.path.exists(sciezka):
        with open(sciezka, "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    czesci = linia.strip().split(";")
                    if len(czesci) >= 2:
                        # Zapisujemy parę: (część 1, część 2)
                        lista.append((czesci[0].strip(), czesci[1].strip()))
    # Usuwamy duplikaty, by przy 2000 wierszach nie było powtórek
    return list(set(lista))

# ZARZĄDZANIE SESJĄ (PAMIĘĆ APLIKACJI)
if 'aktualny_grzyb' not in st.session_state:
    st.session_state.aktualny_grzyb = None
if 'aktualne_foto' not in st.session_state:
    st.session_state.aktualne_foto = None

# Pobieramy dane
