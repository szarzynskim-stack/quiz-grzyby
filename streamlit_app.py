import streamlit as st
import random
import requests
import os

# 1. Konfiguracja strony - musi być na samym początku
st.set_page_config(page_title="Trener Grzybiarza 2000", page_icon="🍄", layout="wide")

# 2. Funkcja pobierania zdjęć (Wikipedia)
def pobierz_foto(n1, n2):
    api = "https://pl.wikipedia.org/w/api.php"
    for fraza in [n1, n2]:
        params = {
            "action": "query", "format": "json", 
            "prop": "pageimages", "titles": fraza, "pithumbsize": 800
        }
        try:
            r = requests.get(api, params=params, timeout=3).json()
            pages = r.get("query", {}).get("pages", {})
            for p in pages:
                if "thumbnail" in pages[p]:
                    return pages[p]["thumbnail"]["source"]
        except:
            continue
    return None

# 3. Wczytywanie bazy - odporne na błędy w pliku txt
@st.cache_data
def wczytaj_baze():
    lista = []
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    czesci = linia.strip().split(";")
                    if len(czesci) >= 2:
                        lista.append((czesci[0].strip(), czesci[1].strip()))
    return list(set(lista))

# 4. Inicjalizacja sesji
if 'aktualny_grzyb' not in st.session_state:
    st.session_state.aktualny_grzyb = None
if 'aktualne_foto' not in st.session_state:
    st.session_state.aktualne_foto = None

baza = wczytaj_baze()

# 5. Panel boczny
st.sidebar.title("🍄 Statystyki")
st.sidebar.metric("Liczba gatunków", len(baza))
if st.sidebar.button("Wyczyść pamięć i odśwież"):
    st.cache_data.clear()
    st.rerun()

# 6. Interfejs główny
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    if not baza:
        st.error("Baza jest pusta! Sprawdź plik grzyby_lista.txt")
    else:
        with st.spinner("Szukam zdjęcia..."):
            test_lista = list(baza)
            random.shuffle(test_lista)
            znaleziono = False
            # Sprawdzamy pierwsze 60 pozycji, by znaleźć foto
            for g1, g2 in test_lista[:60]:
                url = pobierz_foto(g1, g2)
                if url:
                    st.session_state.aktualny_grzyb = (g1, g2)
                    st.session_state.aktualne_foto = url
                    znaleziono = True
                    break
            
            if not znaleziono:
                st.warning("Nie znaleziono zdjęć w tej partii. Kliknij jeszcze raz!")
            else:
                st.rerun()

# 7. Wyświetlanie quizu (NAPRAWIONA SKŁADNIA)
if st.session_state.aktualne_foto:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.image(st.session_state.aktualne_foto, use_container_width=True)
    
    with col2:
        # TUTAJ BYŁ BŁĄD - dodany klucz i dwukropek
        with st.form(key="quiz_form"):
            tryb = st.radio("Zgadujesz nazwę:", ["Polską", "Łacińską"])
            odpowiedz = st.text_input("Twoja odpowiedź:")
            submit = st.form_submit_button("Sprawdź")
            
            if submit:
                g1, g2 = st.session_state.aktualny_grzyb
                # Proste rozpoznawanie polskiej nazwy
                polska_znaki = 'ąćęłńóśźż'
                g1_pl = any(c in g1.lower() for c in polska_znaki)
                
                n_pol = g1 if g1_pl else g2
                n_lat = g2 if g1_pl else g1
                
                cel = n_pol if tryb == "Polską" else n_lat
                
                if odpowiedz.strip().lower() == cel.lower():
                    st.success(f"✅ DOBRZE! To: {cel}")
                    st.balloons()
                else:
                    st.error(f"❌ BŁĄD. To: {cel}")
                    st.info(f"W bazie: {g1} | {g2}")
else:
    st.info("Kliknij przycisk powyżej, aby zacząć naukę!")
