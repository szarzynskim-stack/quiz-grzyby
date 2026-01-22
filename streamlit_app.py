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
                    czesci = linia.strip().split(";")
                    if len(czesci) == 2:
                        p, l = czesci
                        lista[p.strip()] = l.strip()
    return lista

# --- INICJALIZACJA ---
baza = wczytaj_grzyby()

if 'grzyb_teraz' not in st.session_state:
    st.session_state.grzyb_teraz = None
if 'foto_url' not in st.session_state:
    st.session_state.foto_url = None

# --- PANEL BOCZNY ---
with st.sidebar:
    st.header("📊 Statystyki")
    st.write(f"Wszystkich gatunków: **{len(baza)}**")
    if st.button("Wyczyść pamięć i odśwież"):
        st.cache_data.clear()
        st.session_state.grzyb_teraz = None
        st.session_state.foto_url = None
        st.rerun()

# --- GŁÓWNA CZĘŚĆ ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    gatunki = list(baza.items())
    random.shuffle(gatunki)
    
    with st.spinner("Szukam grzyba ze zdjęciem..."):
        znaleziono = False
        # Sprawdzamy pierwsze 40 losowych grzybów, żeby trafić na taki ze zdjęciem
        for n_pl, n_lat in gatunki[:40]:
            url = pobierz_zdjecie(n_pl, n_lat)
            if url:
                st.session_state.grzyb_teraz = (n_pl, n_lat)
                st.session_state.foto_url = url
                znaleziono = True
                break
        
        if not znaleziono:
            st.warning("Wikipedia nie zwróciła zdjęć dla wylosowanej partii. Spróbuj jeszcze raz!")
        else:
            st.rerun()

# --- WYŚWIETLANIE ZAGADKI ---
if st.session_state.foto_url:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.image(st.session_state.foto_url, caption="Rozpoznaj ten gatunek")
    
    with col2:
        # NAPRAWIONY FORMULARZ - z poprawnymi nawiasami i dwukropkiem
        with st.form(key="formularz_quiz"):
            st.subheader("Twoja odpowiedź")
            tryb = st.radio("Zgadujesz:", ["Polską nazwę", "Łacińską nazwę"], horizontal=True)
            odp = st.text_input("Wpisz nazwę:")
            submit = st.form_submit_button("Sprawdź")
            
            if submit:
                n_pl, n_lat = st.session_state.grzyb_teraz
                poprawna = n_pl if tryb == "Polską nazwę" else n_lat
                
                if odp.strip().lower() == poprawna.lower():
                    st.success(f"✅ BRAWO! To: **{poprawna}**")
                    st.balloons()
                else:
                    st.error(f"❌ NIE! Poprawna nazwa to: **{poprawna}**")
else:
    st.info("Kliknij przycisk powyżej, aby zacząć naukę!")
