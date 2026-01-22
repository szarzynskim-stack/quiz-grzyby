import streamlit as st
import random
import requests
import os

# --- PODSTAWOWA KONFIGURACJA ---
st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")

def pobierz_foto(n_pl, n_lat):
    """Pobiera zdjęcie z Wikipedii. Szybki timeout, żeby nie muliło."""
    api = "https://pl.wikipedia.org/w/api.php"
    for fraza in [n_lat, n_pl]:
        params = {
            "action": "query", "format": "json", "prop": "pageimages",
            "titles": fraza, "pithumbsize": 600
        }
        try:
            r = requests.get(api, params=params, timeout=1.5).json()
            pages = r.get("query", {}).get("pages", {})
            for p in pages:
                if "thumbnail" in pages[p]:
                    return pages[p]["thumbnail"]["source"]
        except:
            continue
    return None

def wczytaj_baze():
    """Wczytuje listę grzybów z Twojego pliku."""
    dane = {}
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    czesci = linia.strip().split(";")
                    if len(czesci) == 2:
                        dane[czesci[0].strip()] = czesci[1].strip()
    return dane

# --- INICJALIZACJA ---
baza = wczytaj_baze()

if 'grzyb_sesja' not in st.session_state:
    st.session_state.grzyb_sesja = None
if 'foto_sesja' not in st.session_state:
    st.session_state.foto_sesja = None

# --- BOCZNY PANEL ---
st.sidebar.title("📊 Statystyki")
st.sidebar.write(f"Gatunków w Twoim pliku: **{len(baza)}**")
if st.sidebar.button("Wyczyść pamięć i odśwież"):
    st.cache_data.clear()
    st.session_state.grzyb_sesja = None
    st.session_state.foto_sesja = None
    st.rerun()

# --- GŁÓWNA CZĘŚĆ ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    gatunki = list(baza.items())
    random.shuffle(gatunki)
    
    znaleziono = False
    with st.spinner("Szukam zdjęcia w bazie..."):
        # Sprawdzamy tylko 30 losowych, żeby aplikacja nie 'wisiała'
        for p, l in gatunki[:30]:
            url = pobierz_foto(p, l)
            if url:
                st.session_state.grzyb_sesja = (p, l)
                st.session_state.foto_sesja = url
                znaleziono = True
                break
    
    if not znaleziono:
        st.error("Wikipedia nie odpowiedziała na czas. Spróbuj jeszcze raz!")
    else:
        st.rerun()

# --- WYŚWIETLANIE QUIZU ---
if st.session_state.foto_sesja:
    st.image(st.session_state.foto_sesja, caption="Znasz tego grzyba?")
    
    # Formularz z poprawnymi wcięciami i dwukropkiem (rozwiązuje SyntaxError)
    with st.form(key="quiz_form"):
        tryb = st.radio("Zgadujesz:", ["Polską nazwę", "Łacińską nazwę"], horizontal=True)
        odp = st.text_input("Wpisz odpowiedź:")
        submit = st.form_submit_button("Sprawdź")
        
        if submit:
            n_pl, n_lat = st.session_state.grzyb_sesja
            poprawna = n_pl if tryb == "Polską nazwę" else n_lat
            if odp.strip().lower() == poprawna.lower():
                st.success(f"✅ BRAWO! To faktycznie: {poprawna}")
                st.balloons()
            else:
                st.error(f"❌ NIESTETY BŁĄD. To: {poprawna}")
else:
    st.info("Kliknij przycisk powyżej, aby wylosować grzyba.")
