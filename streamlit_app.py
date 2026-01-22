import streamlit as st
import random
import requests
import os

st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")

# FUNKCJA POBIERANIA - ULEPSZONA
def pobierz_foto(nazwa):
    if not nazwa: return None
    api = "https://pl.wikipedia.org/w/api.php"
    params = {
        "action": "query", "format": "json", "prop": "pageimages",
        "titles": nazwa.strip(), "pithumbsize": 800, "redirects": 1
    }
    try:
        r = requests.get(api, params=params, timeout=5).json()
        pages = r.get("query", {}).get("pages", {})
        for p in pages:
            if "thumbnail" in pages[p]:
                return pages[p]["thumbnail"]["source"]
    except:
        pass
    return None

# CZYTANIE PLIKU
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
    return list(set(lista))

# SESJA
if 'gra' not in st.session_state:
    st.session_state.gra = {"foto": None, "dane": None}

baza = wczytaj_baze()

st.sidebar.metric("Liczba gatunków", len(baza))
if st.sidebar.button("Odśwież bazę"):
    st.cache_data.clear()
    st.rerun()

st.title("🍄 Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    if not baza:
        st.error("Baza jest pusta!")
    else:
        with st.spinner("Szukam zdjęcia w bazie..."):
            probki = list(baza)
            random.shuffle(probki)
            znaleziono = False
            # Sprawdzamy aż 100 pozycji, żeby wyeliminować błąd "nie wyszukało"
            for g1, g2 in probki[:100]:
                url = pobierz_foto(g1) or pobierz_foto(g2)
                if url:
                    st.session_state.gra = {"foto": url, "dane": (g1, g2)}
                    znaleziono = True
                    break
            
            if not znaleziono:
                st.warning("Przejrzano 100 grzybów i żaden nie miał zdjęcia na Wikipedii. Spróbuj jeszcze raz!")
            else:
                st.rerun()

if st.session_state.gra["foto"]:
    st.image(st.session_state.gra["foto"], use_container_width=True)
    
    with st.form(key="quiz"):
        odp = st.text_input("Co to za grzyb?")
        if st.form_submit_button("Sprawdź"):
            g1, g2 = st.session_state.gra["dane"]
            if odp.strip().lower() in [g1.lower(), g2.lower()]:
                st.success(f"✅ BRAWO! To {g1} / {g2}")
                st.balloons()
            else:
                st.error(f"❌ NIE. To {g1} / {g2}")
