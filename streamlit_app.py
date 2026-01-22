import streamlit as st
import requests
import random

# Rozszerzona lista grzybów (Nazwa polska : Nazwa łacińska)
# Wybrałem te z "niebieskimi linkami" na Wikipedii
GRZYBY = {
    "Borowik szlachetny": "Boletus edulis",
    "Podgrzybek brunatny": "Imleria badia",
    "Czubajka kania": "Macrolepiota procera",
    "Pieprznik jadalny": "Cantharellus cibarius",
    "Muchomor sromotnikowy": "Amanita phalloides",
    "Muchomor czerwony": "Amanita muscaria",
    "Maślak zwyczajny": "Suillus luteus",
    "Koźlarz babka": "Leccinum scabrum",
    "Mleczaj rydz": "Lactarius deliciosus",
    "Gąska zielonka": "Tricholoma equestre",
    "Opieńka miodowa": "Armillaria mellea",
    "Boczniak ostrygowaty": "Pleurotus ostreatus",
    "Borowik usiatkowany": "Boletus reticulatus",
    "Piaskowiec modrzak": "Gyroporus cyanescens",
    "Siedzun sosnowy": "Sparassis crispa"
}

st.title("🍄 Trener Grzybiarza")

if 'grzyb' not in st.session_state:
    st.session_state.grzyb = random.choice(list(GRZYBY.keys()))

def pobierz_zdjecie(nazwa_lat):
    # Dodano nagłówki (headers), żeby Wikipedia nie blokowała zapytania
    headers = {'User-Agent': 'MonitorGrzybiarza/1.0 (kontakt@twojemail.com)'}
    api_url = f"https://pl.wikipedia.org/w/api.php?action=query&titles={nazwa_lat}&prop=pageimages&format=json&pithumbsize=500"
    
    try:
        res = requests.get(api_url, headers=headers).json()
        pages = res.get("query", {}).get("pages", {})
        for p in pages:
            if "thumbnail" in pages[p]:
                return pages[p]["thumbnail"]["source"]
    except:
        return None
    return None

poziom = st.radio("Wybierz poziom:", ["Łatwy (Polski)", "Trudny (Łacina)"])

current_lat = GRZYBY[st.session_state.grzyb]
img_url = pobierz_zdjecie(current_lat)

if img_url:
    st.image(img_url, use_container_width=True)
else:
    st.info("Ładowanie zdjęcia z Wikipedii... Jeśli nie widzisz obrazka, kliknij 'Następny'")

with st.form("quiz"):
    if poziom == "Łatwy (Polski)":
        opcje = random.sample(list(GRZYBY.keys()), 3)
        if st.session_state.grzyb not in opcje:
            opcje[0] = st.session_state.grzyb
        random.shuffle(opcje)
        odp = st.selectbox("Co to za grzyb?", ["---"] + opcje)
        poprawna = st.session_state.grzyb
    else:
        odp = st.text_input("Wpisz nazwę łacińską:")
        poprawna = current_lat

    submitted = st.form_submit_button("Sprawdź")
    if submitted:
        if odp.lower() == poprawna.lower():
            st.success(f"Brawo! To {st.session_state.grzyb} ({current_lat})")
        else:
            st.error(f"Błąd. To jest: {st.session_state.grzyb}")

if st.button("Następny grzyb"):
    st.session_state.grzyb = random.choice(list(GRZYBY.keys()))
    st.rerun()
