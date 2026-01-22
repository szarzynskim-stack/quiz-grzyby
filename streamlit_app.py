import streamlit as st
import random
import requests
import os

# 1. Podstawowa konfiguracja
st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")

# 2. Funkcja pobierania zdjęcia - Wikipedia
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
    except:
        pass
    return None

# 3. Wczytywanie bazy
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

# 4. Zarządzanie sesją
if 'gra' not in st.session_state:
    st.session_state.gra = {"foto": None, "nazwy": None}

baza_pelna = wczytaj_baze()

# PANEL BOCZNY
st.sidebar.header("📅 Ustawienia nauki")
dzien = st.sidebar.number_input("Wybierz dzień nauki (partia grzybów):", min_value=1, value=1)
rozmiar_partii = 20  # np. 20 grzybów na jeden dzień
start = (dzien - 1) * rozmiar_partii
stop = start + rozmiar_partii
baza_dzisiejsza = baza_pelna[start:stop]

st.sidebar.write(f"Dziś uczysz się pozycji: {start} - {stop}")
st.sidebar.metric("Grzybów w bazie", len(baza_pelna))

# PRZYCISK ODŚWIEŻANIA
if st.sidebar.button("Wyczyść pamięć / Nowa lista"):
    st.cache_data.clear()
    st.rerun()

# STRONA GŁÓWNA
st.title("🍄 Trener Grzybiarza - Wyzwanie")

if st.button("Losuj grzyba z dzisiejszej partii ➡️"):
    if not baza_dzisiejsza:
        st.warning("Ta partia jest pusta. Zmień dzień w panelu bocznym!")
    else:
        with st.spinner("Szukam zdjęcia..."):
            temp_lista = list(baza_dzisiejsza)
            random.shuffle(temp_lista)
            znaleziono = False
            
            for g1, g2 in temp_lista:
                # Próbujemy obu nazw
                url = pobierz_foto(g1) or pobierz_foto(g2)
                if url:
                    st.session_state.gra = {"foto": url, "nazwy": (g1, g2)}
                    znaleziono = True
                    break
            
            if not znaleziono:
                st.error("Nie znaleziono zdjęć dla grzybów z tej partii. Spróbuj inny dzień!")
            else:
                st.rerun()

# WYŚWIETLANIE QUIZU
if st.session_state.gra["foto"]:
    st.image(st.session_state.gra["foto"], use_container_width=True)
    
    # Formularz z poprawną składnią (dwukropek!)
    with st.form(key="quiz_form"):
        odp = st.text_input("Jak się nazywa ten grzyb?")
        submit = st.form_submit_button("Sprawdź")
        
        if submit:
            n1, n2 = st.session_state.gra["nazwy"]
            if odp.strip().lower() in [n1.lower(), n2.lower()]:
                st.success(f"✅ DOSKONALE! To: {n1} / {n2}")
                st.balloons()
            else:
                st.error(f"❌ NIESTETY. Poprawna nazwa to: {n1} lub {n2}")

else:
    st.info("Wybierz dzień w menu po lewej i kliknij 'Losuj grzyba'.")
