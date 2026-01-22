import streamlit as st
import requests
import random

# Lista grzybów (Nazwa polska : Nazwa łacińska)
GRZYBY = {
    "Borowik szlachetny": "Boletus edulis",
    "Podgrzybek brunatny": "Imleria badia",
    "Czubajka kania": "Macrolepiota procera",
    "Pieprznik jadalny (Kurka)": "Cantharellus cibarius",
    "Muchomor sromotnikowy": "Amanita phalloides",
    "Muchomor czerwony": "Amanita muscaria",
    "Maślak zwyczajny": "Suillus luteus",
    "Koźlarz babka": "Leccinum scabrum",
    "Mleczaj rydz": "Lactarius deliciosus",
    "Gąska zielonka": "Tricholoma equestre"
}

st.title("🍄 Trener Grzybiarza: Zgadnij co to!")

# Wybór poziomu
poziom = st.radio("Wybierz poziom trudności:", ["Łatwy (Polska nazwa)", "Trudny (Łacińska nazwa)"])

if 'grzyb' not in st.session_state:
    st.session_state.grzyb = random.choice(list(GRZYBY.keys()))

def pobierz_zdjecie(nazwa_lat):
    # Funkcja pobierająca zdjęcie z Wikipedii
    api_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={nazwa_lat}&prop=pageimages&format=json&pithumbsize=500"
    res = requests.get(api_url).json()
    pages = res.get("query", {}).get("pages", {})
    for p in pages:
        return pages[p].get("thumbnail", {}).get("source")
    return None

current_lat = GRZYBY[st.session_state.grzyb]
img_url = pobierz_zdjecie(current_lat)

if img_url:
    st.image(img_url, caption="Co to za gatunek?")
else:
    st.warning("Nie udało się pobrać zdjęcia z Wikipedii. Spróbuj kolejnego!")

# Formularz odpowiedzi
with st.form("quiz"):
    if poziom == "Łatwy (Polska nazwa)":
        odp = st.selectbox("Twoja odpowiedź:", ["---"] + sorted(list(GRZYBY.keys())))
        poprawna = st.session_state.grzyb
    else:
        odp = st.text_input("Wpisz nazwę łacińską (np. Boletus edulis):")
        poprawna = current_lat

    submit = st.form_submit_button("Sprawdź!")
    
    if submit:
        if odp.lower() == poprawna.lower():
            st.success(f"Brawo! To {st.session_state.grzyb} ({current_lat})")
            if st.button("Następny grzyb"):
                st.session_state.grzyb = random.choice(list(GRZYBY.keys()))
                st.rerun()
        else:
            st.error(f"Niestety nie. Spróbuj jeszcze raz!")

if st.button("Losuj innego grzyba"):
    st.session_state.grzyb = random.choice(list(GRZYBY.keys()))
    st.rerun()
