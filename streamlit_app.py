import streamlit as st
import random
import requests
import os

st.set_page_config(page_title="Trener Grzybiarza 2000", page_icon="🍄")

# FUNKCJA POBIERANIA ZDJĘĆ
def pobierz_foto(nazwa_pl, nazwa_lat):
    api = "https://pl.wikipedia.org/w/api.php"
    # Szukamy najpierw po łacinie (dokładniej), potem po polsku
    for fraza in [nazwa_lat, nazwa_pl]:
        params = {
            "action": "query", "format": "json", "prop": "pageimages",
            "titles": fraza, "pithumbsize": 600
        }
        try:
            r = requests.get(api, params=params, timeout=2).json()
            pages = r.get("query", {}).get("pages", {})
            for p in pages:
                if "thumbnail" in pages[p]:
                    return pages[p]["thumbnail"]["source"]
        except:
            continue
    return None

# FUNKCJA WCZYTYWANIA - CZYTA CAŁY TWÓJ PLIK
@st.cache_data
def wczytaj_pelna_baze():
    lista_grzybow = []
    sciezka = "grzyby_lista.txt"
    if os.path.exists(sciezka):
        with open(sciezka, "r", encoding="utf-8") as f:
            for linia in f:
                # Obsługa różnych separatorów i błędnych linii
                if ";" in linia:
                    czesci = linia.strip().split(";")
                    if len(czesci) >= 2:
                        p, l = czesci[0].strip(), czesci[1].strip()
                        if p and l:
                            lista_grzybow.append((p, l))
    # Usuwamy duplikaty, by nie losować tego samego
    return list(set(lista_grzybow))

# INICJALIZACJA SESJI
if 'grzyb' not in st.session_state:
    st.session_state.grzyb = None
if 'foto' not in st.session_state:
    st.session_state.foto = None

baza = wczytaj_pelna_baze()

# PANEL BOCZNY
st.sidebar.title("🍄 Statystyki")
st.sidebar.write(f"Gatunków w bazie: **{len(baza)}**")
if st.sidebar.button("Odśwież bazę"):
    st.cache_data.clear()
    st.rerun()

# GŁÓWNA STRONA
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    elementy = list(baza)
    random.shuffle(elementy)
    
    with st.spinner("Szukam zdjęcia w Wikipedii..."):
        znaleziono = False
        # Sprawdzamy pierwsze 50 losowych grzybów, aż znajdziemy zdjęcie
        for g_pl, g_lat in elementy[:50]:
            url = pobierz_foto(g_pl, g_lat)
            if url:
                st.session_state.grzyb = (g_pl, g_lat)
                st.session_state.foto = url
                znaleziono = True
                break
        
        if not znaleziono:
            st.error("Nie udało się pobrać zdjęcia dla tej partii. Spróbuj jeszcze raz!")
        else:
            st.rerun()

# INTERFEJS QUIZU
if st.session_state.foto:
    st.image(st.session_state.foto, use_container_width=True)
    
    # NAPRAWIONA SKŁADNIA FORMULARZA (z dwukropkiem)
    with st.form(key="form_quiz"):
        tryb = st.radio("Zgadujesz:", ["Polską nazwę", "Łacińską nazwę"], horizontal=True)
        odp = st.text_input("Twoja odpowiedź:")
        submit = st.form_submit_button("Sprawdź")
        
        if submit:
            n_pl, n_lat = st.session_state.grzyb
            poprawna = n_pl if tryb == "Polską nazwę" else n_lat
            
            if odp.strip().lower() == poprawna.lower():
                st.success(f"✅ BRAWO! To faktycznie: {poprawna}")
                st.balloons()
            else:
                st.error(f"❌ NIE. Poprawna nazwa to: {poprawna}")
else:
    st.info("Kliknij przycisk powyżej, aby wylosować grzyba z Twojej bazy!")
