import streamlit as st
import random
import requests
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Trener Grzybiarza 1000+", page_icon="🍄")

# --- FUNKCJE POMOCNICZE ---

def pobierz_obrazek_wikipedii(nazwa_pl, nazwa_lat):
    """Próbuje pobrać zdjęcie z Wikipedii. Zwraca None, jeśli nie znajdzie."""
    frazy = [nazwa_lat, nazwa_pl]
    for fraza in frazy:
        api_url = "https://pl.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "titles": fraza,
            "pithumbsize": 800
        }
        try:
            response = requests.get(api_url, params=params, timeout=5)
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

# --- LOGIKA APLIKACJI ---

baza_grzybow = laduj_baze()
st.sidebar.title("📊 Statystyki")
st.sidebar.write(f"Wszystkich gatunków: **{len(baza_grzybow)}**")

# Inicjalizacja stanu sesji
if 'aktualny_grzyb' not in st.session_state:
    st.session_state.aktualny_grzyb = None
if 'poprawna_odp' not in st.session_state:
    st.session_state.poprawna_odp = ""
if 'zdjecie_url' not in st.session_state:
    st.session_state.zdjecie_url = ""

def nowa_zagadka():
    """Losuje grzyba tak długo, aż znajdzie takiego ze zdjęciem."""
    gatunki = list(baza_grzybow.keys())
    random.shuffle(gatunki) # Miesza listę dla lepszej losowości
    
    for g_pl in gatunki:
        g_lat = baza_grzybow[g_pl]
        url = pobierz_obrazek_wikipedii(g_pl, g_lat)
        if url: # Jeśli znaleziono zdjęcie
            st.session_state.aktualny_grzyb = g_pl
            st.session_state.poprawna_odp = g_lat
            st.session_state.zdjecie_url = url
            return
    st.error("Nie znaleziono żadnego gatunku ze zdjęciem w Twojej bazie!")

# --- INTERFEJS UŻYTKOWNIKA ---

st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    nowa_zagadka()

if st.session_state.zdjecie_url:
    st.image(st.session_state.zdjecie_url, caption="Co to za gatunek?")
    
    with st.form("form_odpowiedz"):
        odp_uzytkownika = st.text_input("Podaj nazwę łacińską:")
        submit = st.form_submit_button("Sprawdź")
        
        if submit:
            if odp_uzytkownika.strip().lower() == st.session_state.poprawna_odp.lower():
                st.success(f"Brawo! To {st.session_state.poprawna_odp}")
                st.balloons()
            else:
                st.error(f"Źle! Poprawna nazwa to: {st.session_state.poprawna_odp}")
                st.info(f"Twoja odpowiedź: {odp_uzytkownika}")

else:
    st.write("Kliknij przycisk powyżej, aby rozpocząć naukę!")

# Stopka z czyszczeniem pamięci
if st.sidebar.button("Wyczyść pamięć (Cache)"):
    st.cache_data.clear()
    st.rerun()
