import streamlit as st
import random
import requests
import os

# Konfiguracja strony
st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄", layout="wide")

# Funkcja pobierania zdjęć (Wikipedia API)
def pobierz_foto(n1, n2):
    api = "https://pl.wikipedia.org/w/api.php"
    # Szukamy po obu nazwach
    for fraza in [n1, n2]:
        if not fraza: continue
        params = {
            "action": "query", "format": "json", 
            "prop": "pageimages", "titles": fraza, "pithumbsize": 800
        }
        try:
            r = requests.get(api, params=params, timeout=5).json()
            pages = r.get("query", {}).get("pages", {})
            for p in pages:
                if "thumbnail" in pages[p]:
                    return pages[p]["thumbnail"]["source"]
        except:
            continue
    return None

# Wczytywanie bazy z pliku
@st.cache_data
def wczytaj_baze():
    lista = []
    sciezka = "grzyby_lista.txt"
    if os.path.exists(sciezka):
        with open(sciezka, "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    czesci = linia.strip().split(";")
                    if len(czesci) >= 2:
                        lista.append((czesci[0].strip(), czesci[1].strip()))
    return list(set(lista)) # usuwa duplikaty

# Sesja użytkownika
if 'aktualny_grzyb' not in st.session_state:
    st.session_state.aktualny_grzyb = None
if 'aktualne_foto' not in st.session_state:
    st.session_state.aktualne_foto = None

baza = wczytaj_baze()

# PANEL BOCZNY
st.sidebar.title("🍄 Statystyki")
st.sidebar.metric("Liczba gatunków", len(baza))
if st.sidebar.button("Odśwież bazę"):
    st.cache_data.clear()
    st.rerun()

# STRONA GŁÓWNA
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    if not baza:
        st.error("Baza w pliku txt jest pusta!")
    else:
        with st.spinner("Przeszukuję Wikipedię w poszukiwaniu zdjęcia..."):
            testowa_lista = list(baza)
            random.shuffle(testowa_lista)
            znaleziono = False
            
            # Sprawdzamy do 40 gatunków, aż trafimy na zdjęcie
            for g1, g2 in testowa_lista[:40]:
                url = pobierz_foto(g1, g2)
                if url:
                    st.session_state.aktualny_grzyb = (g1, g2)
                    st.session_state.aktualne_foto = url
                    znaleziono = True
                    break
            
            if not znaleziono:
                st.warning("Nie znaleziono zdjęcia dla wylosowanej partii. Kliknij jeszcze raz!")
            else:
                # Wymuszenie odświeżenia, by pokazać nowe zdjęcie
                st.rerun()

# WYŚWIETLANIE QUIZU
if st.session_state.aktualne_foto:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.image(st.session_state.aktualne_foto, use_container_width=True)
    
    with col2:
        with st.form(key="form_quiz"):
            tryb = st.radio("Zgadujesz nazwę:", ["Polską", "Łacińską"])
            odpowiedz = st.text_input("Twoja odpowiedź:")
            submit = st.form_submit_button("Sprawdź")
            
            if submit:
                g1, g2 = st.session_state.aktualny_grzyb
                # Logika rozpoznawania która nazwa jest polska
                polska_znaki = 'ąćęłńóśźż'
                g1_pl = any(c in g1.lower() for c in polska_znaki)
                
                n_pol = g1 if g1_pl else g2
                n_lat = g2 if g1_pl else g1
                
                cel = n_pol if tryb == "Polską" else n_lat
                
                if odpowiedz.strip().lower() == cel.lower():
                    st.success(f"✅ BRAWO! To: {cel}")
                    st.balloons()
                else:
                    st.error(f"❌ NIE. To: {cel}")
                    st.info(f"Pełne dane: {g1} | {g2}")
else:
    st.info("Kliknij przycisk powyżej, aby rozpocząć!")
