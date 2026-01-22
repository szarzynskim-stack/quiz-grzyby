import streamlit as st
import random
import requests
import os

# 1. Konfiguracja bez zbędnych dodatków
st.set_page_config(page_title="Quiz Grzybowy", layout="centered")

def pobierz_foto(nazwa):
    if not nazwa: return None
    # Czyścimy nazwę z ukośników i spacji, które psuły wyszukiwanie na screenach
    czysta = nazwa.replace("/", " ").strip()
    api = "https://pl.wikipedia.org/w/api.php"
    params = {
        "action": "query", "format": "json", "prop": "pageimages",
        "titles": czysta, "pithumbsize": 800, "redirects": 1
    }
    try:
        r = requests.get(api, params=params, timeout=3).json()
        pages = r.get("query", {}).get("pages", {})
        for p in pages:
            if "thumbnail" in pages[p]:
                return pages[p]["thumbnail"]["source"]
    except: pass
    return None

@st.cache_data
def wczytaj_baze():
    lista = []
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    pary = linia.strip().split(";")
                    if len(pary) >= 2:
                        # Pobieramy czyste nazwy bez śmieci tekstowych
                        n1 = pary[0].split("/")[0].strip()
                        n2 = pary[1].split("/")[0].strip()
                        lista.append((n1, n2))
    return lista

# Zarządzanie stanem aplikacji
if 'foto' not in st.session_state: st.session_state.foto = None
if 'odpowiedz' not in st.session_state: st.session_state.odpowiedz = None

baza = wczytaj_baze()

st.title("🍄 Quiz: Rozpoznaj Grzyba")

# Główny mechanizm
if st.button("LOSUJ NASTĘPNEGO ➡️"):
    with st.spinner("Szukam zdjęcia..."):
        kandydaci = list(baza)
        random.shuffle(kandydaci)
        znaleziono = False
        
        # Sprawdzamy do 15 grzybów, żeby nie zawiesić programu
        for p1, p2 in kandydaci[:15]:
            url = pobierz_foto(p1) or pobierz_foto(p2)
            if url:
                st.session_state.foto = url
                st.session_state.odpowiedz = (p1, p2)
                znaleziono = True
                break
        
        if znaleziono:
            st.rerun()
        else:
            st.error("Wikipedia nie chce dać zdjęć dla tych nazw. Spróbuj jeszcze raz.")

# Wyświetlanie Quizu
if st.session_state.foto:
    st.image(st.session_state.foto, caption="Co to za gatunek?", use_container_width=True)
    
    with st.form("f_quiz"):
        user_input = st.text_input("Twoja odpowiedź:")
        if st.form_submit_button("Sprawdź"):
            n1, n2 = st.session_state.odpowiedz
            if user_input.strip().lower() in [n1.lower(), n2.lower()]:
                st.success(f"✅ BRAWO! To: {n1} / {n2}")
                st.balloons()
            else:
                st.error(f"❌ NIE. Poprawna nazwa to: {n1} / {n2}")
else:
    st.info("Kliknij przycisk powyżej, aby wylosować grzyba z Twojej listy 151 gatunków.")
