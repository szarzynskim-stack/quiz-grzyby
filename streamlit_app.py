import streamlit as st
import random
import requests
import os

# 1. Konfiguracja strony
st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")

# 2. Funkcja pobierania zdjęcia - maksymalnie uproszczona
def pobierz_foto(nazwa):
    if not nazwa:
        return None
    api = "https://pl.wikipedia.org/w/api.php"
    # Czyścimy nazwę z białych znaków
    fraza = nazwa.strip()
    params = {
        "action": "query", "format": "json", "prop": "pageimages",
        "titles": fraza, "pithumbsize": 800, "redirects": 1
    }
    try:
        r = requests.get(api, params=params, timeout=3).json()
        pages = r.get("query", {}).get("pages", {})
        for p in pages:
            if "thumbnail" in pages[p]:
                return pages[p]["thumbnail"]["source"]
    except:
        pass
    return None

# 3. Wczytywanie Twojej bazy (151 grzybów)
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

# Inicjalizacja stanu
if 'foto_url' not in st.session_state: st.session_state.foto_url = None
if 'poprawne' not in st.session_state: st.session_state.poprawne = None

baza = wczytaj_baze()

# PANEL BOCZNY
st.sidebar.title("🍄 Statystyki")
st.sidebar.metric("Grzybów w bazie", len(baza))
if st.sidebar.button("Odśwież plik"):
    st.cache_data.clear()
    st.rerun()

# STRONA GŁÓWNA
st.title("🍄 Profesjonalny Trener Grzybiarza")

# 4. Przycisk losowania
if st.button("Następny grzyb ➡️"):
    if not baza:
        st.error("Nie znaleziono pliku grzyby_lista.txt!")
    else:
        with st.spinner("Szukam zdjęcia..."):
            # Próbujemy wylosować grzyba ze zdjęciem (max 20 prób, żeby nie muliło)
            znaleziono = False
            probki = random.sample(baza, min(len(baza), 20))
            
            for p1, p2 in probki:
                url = pobierz_foto(p1) or pobierz_foto(p2)
                if url:
                    st.session_state.foto_url = url
                    st.session_state.poprawne = (p1, p2)
                    znaleziono = True
                    break
            
            if znaleziono:
                st.rerun()
            else:
                st.warning("Wikipedia nie zwróciła zdjęć dla wylosowanej partii. Spróbuj jeszcze raz!")

# 5. Wyświetlanie quizu
if st.session_state.foto_url:
    st.image(st.session_state.foto_url, use_container_width=True)
    
    with st.form(key="quiz_form"):
        odp = st.text_input("Co to za grzyb?")
        submit = st.form_submit_button("Sprawdź")
        
        if submit:
            n1, n2 = st.session_state.poprawne
            if odp.strip().lower() in [n1.lower(), n2.lower()]:
                st.success(f"✅ BRAWO! To {n1} ({n2})")
                st.balloons()
            else:
                st.error(f"❌ NIE. To {n1} ({n2})")
else:
    st.info("Kliknij przycisk powyżej, aby wylosować grzyba!")
