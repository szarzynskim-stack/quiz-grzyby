import streamlit as st
import random
import requests
import os

# --- KONFIGURACJA ---
st.set_page_config(page_title="Trener Grzybiarza 1000", page_icon="🍄")

def pobierz_obrazek(nazwa_pl, nazwa_lat):
    """Pobiera url zdjęcia. Zwraca None, jeśli nie znajdzie."""
    for fraza in [nazwa_lat, nazwa_pl]:
        api_url = "https://pl.wikipedia.org/w/api.php"
        params = {
            "action": "query", "format": "json", "prop": "pageimages",
            "titles": fraza, "pithumbsize": 500
        }
        try:
            res = requests.get(api_url, params=params, timeout=3).json()
            pages = res.get("query", {}).get("pages", {})
            for p in pages:
                if "thumbnail" in pages[p]:
                    return pages[p]["thumbnail"]["source"]
        except:
            continue
    return None

def laduj_baze():
    """Wczytuje unikalne gatunki (usuwa duplikaty)."""
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

if 'grzyb' not in st.session_state:
    st.session_state.grzyb = None
if 'foto' not in st.session_state:
    st.session_state.foto = None

# --- SIDEBAR ---
st.sidebar.header("📊 Statystyki")
st.sidebar.write(f"Wszystkich gatunków w pliku: **{len(baza)}**")
if st.sidebar.button("Wyczyść Cache"):
    st.cache_data.clear()
    st.rerun()

# --- GŁÓWNA PĘTLA ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    # Losujemy tak długo, aż znajdziemy zdjęcie
    gatunki = list(baza.items())
    random.shuffle(gatunki)
    znalazlem = False
    
    with st.spinner("Szukam gatunku z dostępnym zdjęciem..."):
        for nazwa_pl, nazwa_lat in gatunki:
            url = pobierz_obrazek(nazwa_pl, nazwa_lat)
            if url:
                st.session_state.grzyb = (nazwa_pl, nazwa_lat)
                st.session_state.foto = url
                znalazlem = True
                break
    
    if not znalazlem:
        st.error("Nie znaleziono zdjęć dla gatunków w bazie.")

# --- WYŚWIETLANIE QUIZU ---
if st.session_state.foto:
    st.image(st.session_state.foto, use_container_width=True)
    
    # Naprawiony formularz (poprawne wcięcia)
    with st.form("quiz_form"):
        st.write("Podaj nazwę łacińską tego grzyba:")
        odp = st.text_input("Twoja odpowiedź:", key="input_odp")
        sprawdz = st.form_submit_button("Sprawdź")
        
        if sprawdz:
            poprawna = st.session_state.grzyb[1]
            if odp.strip().lower() == poprawna.lower():
                st.success(f"Genialnie! To faktycznie **{poprawna}**")
                st.balloons()
            else:
                st.error(f"Niestety nie. To: **{poprawna}**")
else:
    st.info("Kliknij przycisk powyżej, aby wylosować grzyba ze zdjęciem.")
