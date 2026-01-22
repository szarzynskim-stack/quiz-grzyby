import streamlit as st
import requests
import random
from datetime import datetime, timedelta
import json
import os
import pandas as pd

st.set_page_config(page_title="Akademia Grzybiarza - Kalendarz", page_icon="🍄")
st.title("🍄 Trener z inteligentnym kalendarzem")

# --- LOGIKA BAZY DANYCH ---
def laduj_liste():
    grzyby = {}
    try:
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            for linia in f:
                if ";" in linia:
                    pl, lat = linia.strip().split(";")
                    grzyby[pl] = lat
    except: return {"Borowik szlachetny": "Boletus edulis"}
    return grzyby

def laduj_postepy():
    if os.path.exists("postepy.json"):
        with open("postepy.json", "r") as f:
            return json.load(f)
    return {}

def zapisz_postepy(postepy):
    with open("postepy.json", "w") as f:
        json.dump(postepy, f)

BAZA = laduj_liste()
if 'postepy' not in st.session_state:
    st.session_state.postepy = laduj_postepy()

# --- WIDOK KALENDARZA NA BOKU ---
def pokaz_prognoze():
    st.sidebar.header("📅 Twój Kalendarz Nauki")
    dzis = datetime.now().date()
    dni = [(dzis + timedelta(days=i)) for i in range(7)]
    dni_str = [d.strftime("%Y-%m-%d") for d in dni]
    
    plan = []
    for d_str in dni_str:
        ile = list(st.session_state.postepy.values()).count(d_str)
        # Dla dnia dzisiejszego doliczamy też te, które pominęliśmy wcześniej
        if d_str == dzis.strftime("%Y-%m-%d"):
            ile = len([v for v in st.session_state.postepy.values() if v <= d_str])
        
        nazwa_dnia = "Dziś" if d_str == dzis.strftime("%Y-%m-%d") else d
