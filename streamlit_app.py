import streamlit as st
import random
import requests
import os

# --- KONFIGURACJA ---
st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")

def pobierz_foto(n_pl, n_lat):
    """Próbuje pobrać zdjęcie. Jeśli nie ma w 2 sekundy, odpuszcza."""
    api = "https://pl.wikipedia.org/w/api.php"
    for fraza in [n_lat, n_pl]:
        params = {
            "action": "query", "format": "json", "prop": "pageimages",
            "titles": fraza, "pithumbsize": 500
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

def laduj_liste():
    """Wczytuje Twoje 1076 gatunków z pliku."""
    dane = {}
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    czesci = linia.strip().split(";")
                    if len(czesci) == 2:
                        dane[czesci[0].strip()] = czesci[1].strip()
    return dane

# --- LOGIKA ---
baza = laduj_liste()

if 'grzyb' not in st.session_state:
    st.session_state.grzyb = None
if 'foto' not in st.session_state:
    st.session_state.foto = None

# --- PANEL BOCZNY ---
st.sidebar.title("📊 Statystyki")
st.sidebar.write(f"Wszystkich gatunków: **{len(baza)}**")
if st.sidebar.button("Odśwież bazę"):
    st.cache_data.clear()
    st.rerun()

# --- GŁÓWNA STRONA ---
st.title("🍄 Profesjonalny Trener Grzybiarza")

if st.button("Następny grzyb ➡️"):
    gatunki = list(baza.items())
    random.shuffle(gatunki)
    
    with st.spinner("Szukam grzyba ze zdjęciem..."):
        znaleziono = False
        # Sprawdzamy tylko pierwsze 50 losowych, żeby nie wieszać strony
        for p, l in gatunki[:50]:
            url = pobierz_foto(p, l)
            if url:
                st.session_state.grzyb = (p, l)
                st.session_state.foto = url
                znaleziono = True
                break
        
        if not znaleziono:
            st.error("Nie udało się znaleźć zdjęcia. Kliknij jeszcze raz!")
        else:
            st.rerun()

# --- FORMULARZ ---
if st.session_state.foto:
    st.image(st.session_state.foto)
    
    # Formularz z poprawną składnią (zwróć uwagę na dwukropek!)
    with st.form(key="quiz_form"):
        tryb = st.radio("Zgadujesz:", ["Polską nazwę", "Łacińską nazwę"], horizontal=True)
        odp = st.text_input("Twoja odpowiedź:")
        submit = st.form_submit_button("Sprawdź")
        
        if submit:
            n_pl, n_lat = st.session_state.grzyb
            poprawna = n_pl if tryb == "Polską nazwę" else n_lat
            if odp.strip().lower() == poprawna.lower():
                st.success(f"✅ Świetnie! To: {poprawna}")
                st.balloons()
            else:
                st.error(f"❌ Nie. To: {poprawna}")
else:
    st.info("Kliknij przycisk powyżej, aby wylosować grzyba.")
