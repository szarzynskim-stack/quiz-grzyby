import streamlit as st
import requests
import random

# Lista grzybów z nazwami łacińskimi
GRZYBY = {
    "Borowik szlachetny": "Boletus edulis",
    "Podgrzybek brunatny": "Imleria badia",
    "Czubajka kania": "Macrolepiota procera",
    "Pieprznik jadalny": "Cantharellus cibarius",
    "Muchomor czerwony": "Amanita muscaria",
    "Muchomor sromotnikowy": "Amanita phalloides",
    "Maślak zwyczajny": "Suillus luteus",
    "Koźlarz babka": "Leccinum scabrum",
    "Mleczaj rydz": "Lactarius deliciosus",
    "Gąska zielonka": "Tricholoma equestre"
}

st.set_page_config(page_title="Trener Grzybiarza", page_icon="🍄")
st.title("🍄 Trener Grzybiarza")

if 'grzyb' not in st.session_state:
    st.session_state.grzyb = random.choice(list(GRZYBY.keys()))

def pobierz_foto(nazwa):
    # Szukamy zdjęcia po nazwie łacińskiej w otwartej bazie Unsplash
    url = f"https://source.unsplash.com/featured/?mushroom,{nazwa.replace(' ', ',')}"
    return url

poziom = st.radio("Poziom trudności:", ["Łatwy (Polski)", "Trudny (Łacina)"])

# Wyświetlanie zdjęcia
img_url = pobierz_foto(GRZYBY[st.session_state.grzyb])
st.image(img_url, caption="Znajdź ten gatunek!", use_container_width=True)

with st.form("quiz_form"):
    if poziom == "Łatwy (Polski)":
        odp = st.selectbox("Wybierz nazwę:", ["---"] + sorted(list(GRZYBY.keys())))
        poprawna = st.session_state.grzyb
    else:
        odp = st.text_input("Wpisz nazwę łacińską:")
        poprawna = GRZYBY[st.session_state.grzyb]

    sprawdz = st.form_submit_button("Sprawdź odpowiedź")
    
    if sprawdz:
        if odp.lower() == poprawna.lower():
            st.success(f"✅ DOSKONALE! To {st.session_state.grzyb}")
            st.balloons()
        else:
            st.error(f"❌ NIESTETY. To jest {st.session_state.grzyb} ({GRZYBY[st.session_state.grzyb]})")

if st.button("Następny grzyb ➡️"):
    st.session_state.grzyb = random.choice(list(GRZYBY.keys()))
    st.rerun()
