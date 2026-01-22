import streamlit as st
import random
import requests
import os

# 1. Prosta konfiguracja
st.set_page_config(page_title="Mushroom Quiz", layout="centered")

def pobierz_foto(nazwa):
    if not nazwa or len(nazwa) < 3: return None
    # Wikipedia potrzebuje czystej nazwy (bez ukośników i spacji na końcach)
    fraza = nazwa.split('/')[0].strip()
    api = "https://pl.wikipedia.org/w/api.php"
    params = {
        "action": "query", "format": "json", "prop": "pageimages",
        "titles": fraza, "pithumbsize": 800, "redirects": 1
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
                    czesci = linia.strip().split(";")
                    if len(czesci) >= 2:
                        # Zapisujemy tylko "czyste" nazwy do quizu
                        lista.append((czesci[0].strip(), czesci[1].strip()))
    return lista

# Pamięć sesji
if 'foto_url' not in st.session_state: st.session_state.foto_url = None
if 'poprawne' not in st.session_state: st.session_state.poprawne = None

baza = wczytaj_baze()

st.title("🍄 Quiz: Co to za grzyb?")

# Główny przycisk
if st.button("LOSUJ NASTĘPNEGO ➡️"):
    with st.spinner("Przeszukuję Twoją listę..."):
        kandydaci = list(baza)
        random.shuffle(kandydaci)
        znaleziono = False
        
        # Sprawdzamy do 20 pozycji, żeby szybko znaleźć zdjęcie
        for p1, p2 in kandydaci[:20]:
            url = pobierz_foto(p1) or pobierz_foto(p2)
            if url:
                st.session_state.foto_url = url
                st.session_state.poprawne = (p1, p2)
                znaleziono = True
                break
        
        if znaleziono:
            st.rerun()
        else:
            st.error("Nie znaleziono zdjęcia. Kliknij jeszcze raz!")

# Wyświetlanie zdjęcia i formularza
if st.session_state.foto_url:
    st.image(st.session_state.foto_url, use_container_width=True)
    
    with st.form(key="quiz_input"):
        odp = st.text_input("Twoja odpowiedź:")
        sprawdz = st.form_submit_button("Sprawdź")
        
        if sprawdz:
            n1, n2 = st.session_state.poprawne
            # Porównujemy odpowiedź z obiema nazwami z listy
            if odp.strip().lower() in [n1.lower(), n2.lower()]:
                st.success(f"✅ BRAWO! To: {n1}")
                st.balloons()
            else:
                st.error(f"❌ NIE. To: {n1}")
else:
    st.info("Kliknij przycisk powyżej, aby wylosować grzyba z Twojej bazy (151 sztuk).")
