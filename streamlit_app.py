import streamlit as st
import random
import requests
import os

# 1. Ustawienia wyglądu
st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")

# 2. Funkcja pobierania zdjęcia - z poprawką na błędy w nazwach
def pobierz_foto(nazwa):
    if not nazwa:
        return None
    # Czyścimy nazwę ze zbędnych spacji i znaków
    czysta_nazwa = nazwa.strip()
    api = "https://pl.wikipedia.org/w/api.php"
    params = {
        "action": "query", "format": "json", "prop": "pageimages",
        "titles": czysta_nazwa, "pithumbsize": 800, "redirects": 1
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

# 3. Wczytywanie bazy - Twoje 151 grzybów
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

# Inicjalizacja pamięci programu
if 'aktywny_grzyb' not in st.session_state:
    st.session_state.aktywny_grzyb = {"foto": None, "nazwy": None}

baza = wczytaj_baze()

# PANEL BOCZNY
st.sidebar.title("🍄 Statystyki")
st.sidebar.metric("Grzybów w bazie", len(baza))
if st.sidebar.button("Wyczyść pamięć i odśwież"):
    st.cache_data.clear()
    st.session_state.aktywny_grzyb = {"foto": None, "nazwy": None}
    st.rerun()

# STRONA GŁÓWNA
st.title("🍄 Profesjonalny Trener Grzybiarza")

# 4. Przycisk losowania - szuka zdjęcia do skutku w Twoich 151 grzybach
if st.button("Następny grzyb ➡️"):
    if not baza:
        st.error("Nie widzę Twojej listy! Sprawdź plik grzyby_lista.txt")
    else:
        with st.spinner("Przeszukuję bazę w poszukiwaniu zdjęcia..."):
            kandydaci = list(baza)
            random.shuffle(kandydaci)
            znaleziono = False
            
            # Próbujemy znaleźć zdjęcie dla pierwszych 50 losowych grzybów
            for n1, n2 in kandydaci[:50]:
                url = pobierz_foto(n1) or pobierz_foto(n2)
                if url:
                    st.session_state.aktywny_grzyb = {"foto": url, "nazwy": (n1, n2)}
                    znaleziono = True
                    break
            
            if znaleziono:
                st.rerun()
            else:
                st.warning("Przeszukałem 50 grzybów i Wikipedia nie zwróciła zdjęć. Sprawdź, czy nazwy w pliku są poprawne (np. Borowik szlachetny)!")

# 5. Wyświetlanie zadania
if st.session_state.aktywny_grzyb["foto"]:
    st.image(st.session_state.aktywny_grzyb["foto"], use_container_width=True)
    
    with st.form(key="quiz"):
        odp = st.text_input("Twoja odpowiedź:")
        if st.form_submit_button("Sprawdź"):
            n1, n2 = st.session_state.aktywny_grzyb["nazwy"]
            if odp.strip().lower() in [n1.lower(), n2.lower()]:
                st.success(f"✅ BRAWO! To: {n1} / {n2}")
                st.balloons()
            else:
                st.error(f"❌ NIE. To: {n1} / {n2}")
else:
    st.info("Kliknij przycisk powyżej, aby zacząć naukę!")
