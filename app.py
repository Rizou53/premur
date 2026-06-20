import streamlit as st
import math

st.set_page_config(page_title="Prémur IA", layout="wide")

st.title("🏗️ Prémur IA - V9")

treillis_data = {
    "ST10": {"vertical": 6, "horizontal": 6},
    "ST15C": {"vertical": 7, "horizontal": 7},
    "ST25C": {"vertical": 7, "horizontal": 7},
    "ST25CS": {"vertical": 7, "horizontal": 7},
    "ST40C": {"vertical": 7, "horizontal": 7},
    "ST50C": {"vertical": 8, "horizontal": 8},
    "ST60": {"vertical": 8, "horizontal": 8},
    "ST60V": {"vertical": 12, "horizontal": 10},
}

enrobage_data = {
    "XC1": 20, "XC2": 25, "XC3": 30, "XC4": 30,
    "XD1": 35, "XD2": 40, "XD3": 45,
    "XS1": 35, "XS2": 40, "XS3": 45,
    "XF1": 30, "XF2": 35, "XF3": 40, "XF4": 45,
    "XA1": 35, "XA2": 40, "XA3": 45,
}

ENROBAGE_INTERIEUR = 15
EPAISSEUR_MIN_PAROI = 50
NOYAU_MIN = 70
PLUS_RETOURNEMENT = 5

def arrondi_5_superieur(valeur):
    return math.ceil(valeur / 5) * 5

def calcul_paroi(enrobage_ext, treillis, type_paroi, ajout_retournement=0):
    vertical = treillis_data[treillis]["vertical"]
    horizontal = treillis_data[treillis]["horizontal"]

    if type_paroi == 2:
        fil_1 = horizontal
        fil_2 = vertical
    else:
        fil_1 = vertical
        fil_2 = horizontal

    epaisseur_theorique = (
        enrobage_ext
        + fil_1
        + fil_2
        + ENROBAGE_INTERIEUR
        + ajout_retournement
    )

    epaisseur_avec_min = max(EPAISSEUR_MIN_PAROI, epaisseur_theorique)
    epaisseur_paroi = arrondi_5_superieur(epaisseur_avec_min)

    enrobage_interieur = epaisseur_paroi - enrobage_ext - fil_1 - fil_2

    return epaisseur_theorique, epaisseur_paroi, enrobage_interieur

def afficher_resultats(titre, ajout_retournement=0):
    st.subheader(titre)

    cols = st.columns(4)

    for col, (nom_scenario, type_p1, type_p2) in zip(cols, scenarios):
        with col:
            st.markdown(f"### {nom_scenario}")

            st.write("**Paroi 1**")
            enrobage_1 = st.number_input(
                f"Enrobage P1 — {classe_1}",
                min_value=0,
                value=enrobage_base_1,
                step=5,
                key=f"{titre}_enrobage_p1_{nom_scenario}_{classe_1}"
            )

            ep_theo_1, ep_paroi_1, enr_int_1 = calcul_paroi(
                enrobage_1, treillis_1, type_p1, ajout_retournement
            )

            st.write(f"Épaisseur théorique : **{ep_theo_1} mm**")
            st.write(f"Épaisseur usine retenue : **{ep_paroi_1} mm**")
            st.write(f"Enrobage int. réel : **{enr_int_1} mm**")

            st.write("**Paroi 2**")
            enrobage_2 = st.number_input(
                f"Enrobage P2 — {classe_2}",
                min_value=0,
                value=enrobage_base_2,
                step=5,
                key=f"{titre}_enrobage_p2_{nom_scenario}_{classe_2}"
            )

            ep_theo_2, ep_paroi_2, enr_int_2 = calcul_paroi(
                enrobage_2, treillis_2, type_p2, ajout_retournement
            )

            st.write(f"Épaisseur théorique : **{ep_theo_2} mm**")
            st.write(f"Épaisseur usine retenue : **{ep_paroi_2} mm**")
            st.write(f"Enrobage int. réel : **{enr_int_2} mm**")

            noyau = epaisseur_totale_mm - ep_paroi_1 - ep_paroi_2

            st.write(f"Noyau : **{noyau:.0f} mm**")

            if noyau < 0:
                st.error("❌ Non conforme : épaisseur totale insuffisante")
            elif noyau < NOYAU_MIN:
                st.error("❌ Non conforme : noyau inférieur à 70 mm")
            else:
                st.success("✅ Conforme")

            if enrobage_1 != enrobage_base_1:
                st.warning(f"⚠️ Enrobage P1 changé à la main : {enrobage_1} mm")

            if enrobage_2 != enrobage_base_2:
                st.warning(f"⚠️ Enrobage P2 changé à la main : {enrobage_2} mm")

epaisseur_totale_cm = st.number_input(
    "Épaisseur totale du prémur (cm)",
    min_value=10,
    value=20,
    step=5
)

epaisseur_totale_mm = epaisseur_totale_cm * 10

col1, col2 = st.columns(2)

with col1:
    st.header("Paroi 1")
    classe_1 = st.selectbox("Classe d’exposition Paroi 1", list(enrobage_data.keys()))
    treillis_1 = st.selectbox("Treillis Paroi 1", list(treillis_data.keys()))

with col2:
    st.header("Paroi 2")
    classe_2 = st.selectbox("Classe d’exposition Paroi 2", list(enrobage_data.keys()))
    treillis_2 = st.selectbox("Treillis Paroi 2", list(treillis_data.keys()))

enrobage_base_1 = enrobage_data[classe_1]
enrobage_base_2 = enrobage_data[classe_2]

scenarios = [
    ("Type 2-2", 2, 2),
    ("Type 3-2", 3, 2),
    ("Type 3-3", 3, 3),
    ("Type 2-3", 2, 3),
]

afficher_resultats("Résultats normaux", ajout_retournement=0)

st.write("---")

afficher_resultats(
    "Résultats mur retourné (+5 mm par paroi)",
    ajout_retournement=PLUS_RETOURNEMENT
)
