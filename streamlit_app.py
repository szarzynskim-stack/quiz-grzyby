import streamlit as st
import random
import requests
import os

# 1. Ustawienia
st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")

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
                    # Rozdzielamy linię na polską i łacińską
                    czesci = linia.strip().split(";")
                    if len(czesci) >= 2:
                        polska = czesci[0].strip()
                        lacina = czesci[1].strip()
                        lista.append((polska, lacina))
    return lista

# Inicjalizacja pamięci
if 'foto' not in st.session_state: st.session_state.foto = None
if 'nazwy' not in st.session_state: st.session_state.nazwy = None

baza = wczytaj_baze()

# --- INTERFEJS ---
st.title("🍄 Trener Grzybiarza")

if st.button("LOSUJ GRZYBA ➡️"):
    if not baza:
        st.error("Nie znaleziono pliku grzyby_lista.txt!")
    else:
        with st.spinner("Szukam zdjęcia w Twojej bazie..."):
            kandydaci = list(baza)
            random.shuffle(kandydaci)
            znaleziono = False
            
            for p1, p2 in kandydaci:
                # SZUKAMY OSOBNO: najpierw nazwa polska, potem łacińska
                url = pobierz_foto(p1) or pobierz_foto(p2)
                if url:
                    st.session_state.foto = url
                    st.session_state.nazwy = (p1, p2)
                    znaleziono = True
                    break
            
            if znaleziono:
                st.rerun()
            else:
                st.warning("Nie znaleziono zdjęć dla grzybów z listy.")

if st.session_state.foto:
    st.image(st.session_state.foto, use_container_width=True)
    with st.form("quiz"):
        odp = st.text_input("Co to za grzyb?")
        if st.form_submit_button("Sprawdź"):
            n1, n2 = st.session_state.nazwy
            if odp.strip().lower() in [n1.lower(), n2.lower()]:
                st.success(f"✅ BRAWO! To {n1} ({n2})")
                st.balloons()
            else:
                st.error(f"❌ NIE. To {n1} ({n2})")
else:
    st.info("Kliknij przycisk, aby zacząć.")

st.sidebar.metric("Grzyby w bazie", len(baza))
