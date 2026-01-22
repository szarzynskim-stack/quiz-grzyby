def usun_duble_z_pliku():
    if os.path.exists("grzyby_lista.txt"):
        with open("grzyby_lista.txt", "r", encoding="utf-8") as f:
            linie = f.readlines()
        
        # Usuwanie duplikatów przy zachowaniu kolejności
        unikalne = []
        widziane = set()
        for linia in linie:
            clean = linia.strip()
            if clean and clean not in widziane:
                unikalne.append(linia)
                widziane.add(clean)
        
        # Jeśli znaleziono duble, nadpisz plik czystą wersją
        if len(unikalne) < len(linie):
            with open("grzyby_lista.txt", "w", encoding="utf-8") as f:
                f.writelines(unikalne)
            st.sidebar.warning(f"Usunięto {len(linie) - len(unikalne)} duplikatów!")

# Wywołaj funkcję naprawczą
usun_duble_z_pliku()
