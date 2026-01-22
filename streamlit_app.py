import streamlit as st
import random
import requests
import os

st.set_page_config(page_title="Trener Grzybiarza - Test", page_icon="🍄")

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
                        lista.append((pary[0].strip(), pary[1].strip()))
    return lista

if 'foto' not in st.session_state: st.session_state.foto = None
if 'nazwy' not in st.session_state: st.session_state.nazwy = None

baza = wczytaj_baze()

st.title("🍄 Test Trenera")

if st.button("LOSUJ GRZYBA ➡️"):
    if not baza:
        st.error("Baza 151 grzybów nie wczytała się!")
    else:
        with st.spinner("Przeszukuję bazę..."):
            probki = random.sample(baza, min(len(baza), 10))
            znaleziono = False
            szukane_nazwy = [] # Log do sprawdzania błędów
            
            for g1, g2 in probki:
                szukane_nazwy.append(f"{g1} / {g2}")
                url = pobierz_foto(g1) or pobierz_foto(g2)
                if url:
                    st.session_state.foto = url
                    st.session_state.nazwy = (g1, g2)
                    znaleziono = True
                    break
            
            if znaleziono:
                st.rerun()
            else:
                st.warning("Wikipedia nie znalazła zdjęć dla tych nazw:")
                st.write(szukane_nazwy) # To nam jutro powie, co jest nie tak

if st.session_state.foto:
    st.image(st.session_state.foto, use_container_width=True)
    with st.form("quiz"):
        odp = st.text_input("Co to za okaz?")
        if st.form_submit_button("Sprawdź"):
            n1, n2 = st.session_state.nazwy
            if odp.strip().lower() in [n1.lower(), n2.lower()]:
                st.success(f"✅ DOBRZE! To: {n1} / {n2}")
            else:
                st.error(f"❌ ŹLE. To: {n1} / {n2}")
