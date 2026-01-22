import streamlit as st
import random
import requests
import os

# 1. Ustawienia podstawowe
st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")

# 2. Funkcja pobierania zdjęcia - Wikipedia
def pobierz_foto(nazwa):
    if not nazwa:
        return None
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
        return None
    return None

# 3. Wczytywanie Twoich 151 grzybów
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

# 4. Pamięć sesji
if 'grzyb_aktywny' not in st.session_state:
    st.session_state.grzyb_aktywny = {"foto": None, "nazwy": None}

baza = wczytaj_baze()

# PANEL BOCZNY
st.sidebar.title("📊 Statystyki")
st.sidebar.write(f"Liczba gatunków: {len(baza)}")
if st.sidebar.button("Odśwież bazę"):
    st.cache_data.clear()
    st.rerun()

# STRONA GŁÓWNA
st.title("🍄 Profesjonalny Trener Grzybiarza")

# 5. Logika przycisku - Szukanie zdjęcia aż do skutku
if st.button("Następny grzyb ➡️"):
    if not baza:
        st.error("Baza jest pusta! Sprawdź plik grzyby_lista.txt")
    else:
        with st.spinner("Szukam zdjęcia w bazie..."):
            # Mieszamy bazę, żeby losować
            kandydaci = list(baza)
            random.shuffle(kandydaci)
            znaleziono = False
            
            # Przeszukujemy bazę w poszukiwaniu zdjęcia
            for n1, n2 in kandydaci:
                url = pobierz_foto(n1) or pobierz_foto(n2)
                if url:
                    st.session_state.grzyb_aktywny = {"foto": url, "nazwy": (n1, n2)}
                    znaleziono = True
                    break
            
            if znaleziono:
                st.rerun()
            else:
                st.warning("Przeszukano bazę, ale Wikipedia nie ma zdjęć dla tych nazw.")

# 6. Wyświetlanie quizu (jeśli zdjęcie istnieje)
if st.session_state.grzyb_aktywny["foto"]:
    st.image(st.session_state.grzyb_aktywny["foto"], use_container_width=True)
    
    with st.form(key="quiz_form"):
        odp = st.text_input("Twoja odpowiedź (polska lub łacińska):")
        submit = st.form_submit_button("Sprawdź")
        
        if submit:
            n1, n2 = st.session_state.grzyb_aktywny["nazwy"]
            if odp.strip().lower() in [n1.lower(), n2.lower()]:
                st.success(f"✅ DOBRZE! To: {n1} / {n2}")
                st.balloons()
            else:
                st.error(f"❌ NIE. To: {n1} / {n2}")
else:
    st.info("Kliknij przycisk powyżej, aby wylosować grzyba!")
