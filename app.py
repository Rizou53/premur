import streamlit as st
import math

st.set_page_config(page_title="Prémur IA V10", layout="wide")

st.title("🏗️ Prémur IA V10")

# -----------------------------
# CONSTANTES
# -----------------------------

ENROBAGE_INTERIEUR = 15
EPAISSEUR_MIN_PAROI = 50
NOYAU_MIN = 70

PLUS_RETOURNEMENT = 5

HA_POUTRELLE_PAROI_1 = 6
HA_POUTRELLE_PAROI_2 = 8

POUTRELLE_MIN = 90
POUTRELLE_MAX = 400
PAS_POUTRELLE = 10

TOLERANCE_POUTRELLE = 2

# -----------------------------
# TREILLIS
# -----------------------------

treillis_data = {
    "PAF10": {"vertical": 6, "horizontal": 6},
    "PAF12": {"vertical": 6, "horizontal": 6},
    "PAF15": {"vertical": 7, "horizontal": 7},

    "ST10": {"vertical": 6, "horizontal": 6},
    "ST15C": {"vertical": 7, "horizontal": 7},
    "ST25C": {"vertical": 7, "horizontal": 7},
    "ST25CS": {"vertical": 7, "horizontal": 7},
    "ST40C": {"vertical": 7, "horizontal": 7},
    "ST50C": {"vertical": 8, "horizontal": 8},
    "ST60": {"vertical": 8, "horizontal": 8},
    "ST60V": {"vertical": 12, "horizontal": 10},
}

# -----------------------------
# CLASSES EXPO
# -----------------------------

enrobage_data = {
    "XC1": 20,
    "XC2": 25,
    "XC3": 30,
    "XC4": 30,

    "XD1": 35,
    "XD2": 40,
    "XD3": 45,

    "XS1": 35,
    "XS2": 40,
    "XS3": 45,

    "XF1": 30,
    "XF2": 35,
    "XF3": 40,
    "XF4": 45,

    "XA1": 35,
    "XA2": 40,
    "XA3": 45,
}
def arrondi_5(valeur):
    return math.ceil(valeur / 5) * 5


def acier_retenu_paroi_1(treillis):
    return max(
        treillis_data[treillis]["vertical"],
        HA_POUTRELLE_PAROI_1
    )


def acier_retenu_paroi_2(treillis):
    return max(
        treillis_data[treillis]["vertical"],
        HA_POUTRELLE_PAROI_2
    )


def calcul_paroi(
    enrobage_ext,
    treillis,
    ajout_retournement=0
):

    vertical = treillis_data[treillis]["vertical"]
    horizontal = treillis_data[treillis]["horizontal"]

    epaisseur_theorique = (
        enrobage_ext
        + vertical
        + horizontal
        + ENROBAGE_INTERIEUR
        + ajout_retournement
    )

    epaisseur_finale = max(
        EPAISSEUR_MIN_PAROI,
        epaisseur_theorique
    )

    epaisseur_finale = arrondi_5(
        epaisseur_finale
    )

    return epaisseur_finale
    
    def hauteur_poutrelle_theorique(
    epaisseur_totale_mm,
    enrobage_p1,
    enrobage_p2,
    treillis_p1,
    treillis_p2
):
    acier_p1 = acier_retenu_paroi_1(treillis_p1)
    acier_p2 = acier_retenu_paroi_2(treillis_p2)

    return (
        epaisseur_totale_mm
        - enrobage_p1
        - enrobage_p2
        - acier_p1
        - acier_p2
    )


def poutrelle_standard_plus_proche(hauteur):
    poutrelles = list(range(POUTRELLE_MIN, POUTRELLE_MAX + 1, PAS_POUTRELLE))

    meilleure = min(
        poutrelles,
        key=lambda p: abs(p - hauteur)
    )

    return meilleure


def calcul_poutrelle_avec_correction(
    epaisseur_totale_mm,
    enrobage_p1,
    enrobage_p2,
    treillis_p1,
    treillis_p2
):
    hauteur_initiale = hauteur_poutrelle_theorique(
        epaisseur_totale_mm,
        enrobage_p1,
        enrobage_p2,
        treillis_p1,
        treillis_p2
    )

    poutrelle = poutrelle_standard_plus_proche(hauteur_initiale)

    bas_tol = poutrelle - TOLERANCE_POUTRELLE
    haut_tol = poutrelle + TOLERANCE_POUTRELLE

    correction = 0
    enrobage_p1_corrige = enrobage_p1
    hauteur_corrigee = hauteur_initiale

    if hauteur_initiale < bas_tol:
        correction = bas_tol - hauteur_initiale
        enrobage_p1_corrige = enrobage_p1 - correction
        hauteur_corrigee = bas_tol

    elif hauteur_initiale > haut_tol:
        correction = hauteur_initiale - haut_tol
        enrobage_p1_corrige = enrobage_p1 + correction
        hauteur_corrigee = haut_tol

    poutrelle_finale = poutrelle_standard_plus_proche(hauteur_corrigee)

    return {
        "hauteur_initiale": hauteur_initiale,
        "hauteur_corrigee": hauteur_corrigee,
        "poutrelle": poutrelle_finale,
        "correction": correction,
        "enrobage_p1_corrige": enrobage_p1_corrige,
    }
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

    classe_1 = st.selectbox(
        "Classe d’exposition Paroi 1",
        list(enrobage_data.keys())
    )

    treillis_1 = st.selectbox(
        "Treillis Paroi 1",
        list(treillis_data.keys())
    )

with col2:
    st.header("Paroi 2")

    classe_2 = st.selectbox(
        "Classe d’exposition Paroi 2",
        list(enrobage_data.keys())
    )

    treillis_2 = st.selectbox(
        "Treillis Paroi 2",
        list(treillis_data.keys())
    )

enrobage_base_1 = enrobage_data[classe_1]
enrobage_base_2 = enrobage_data[classe_2]

scenarios = [
    ("Type 2-2", 2, 2),
    ("Type 3-2", 3, 2),
    ("Type 3-3", 3, 3),
    ("Type 2-3", 2, 3),
]
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
                key=f"{titre}_p1_{nom_scenario}_{classe_1}"
            )

            st.write("**Paroi 2**")
            enrobage_2 = st.number_input(
                f"Enrobage P2 — {classe_2}",
                min_value=0,
                value=enrobage_base_2,
                step=5,
                key=f"{titre}_p2_{nom_scenario}_{classe_2}"
            )

            ep_p1 = calcul_paroi(enrobage_1, treillis_1, ajout_retournement)
            ep_p2 = calcul_paroi(enrobage_2, treillis_2, ajout_retournement)

            noyau = epaisseur_totale_mm - ep_p1 - ep_p2

            poutrelle = calcul_poutrelle_avec_correction(
                epaisseur_totale_mm,
                enrobage_1,
                enrobage_2,
                treillis_1,
                treillis_2
            )

            st.write(f"Paroi 1 : **{ep_p1} mm**")
            st.write(f"Paroi 2 : **{ep_p2} mm**")
            st.write(f"Noyau : **{noyau:.0f} mm**")

            st.write(
                f"Hauteur théorique poutrelle : "
                f"**{poutrelle['hauteur_initiale']:.0f} mm**"
            )

            st.write(
                f"Poutrelle retenue : "
                f"**{poutrelle['poutrelle']} mm**"
            )

            if poutrelle["correction"] > 0:
                st.info(
                    f"Correction enrobage P1 : "
                    f"{enrobage_1} → "
                    f"{poutrelle['enrobage_p1_corrige']:.0f} mm"
                )
            else:
                st.success("Aucune correction poutrelle")

            if enrobage_1 != enrobage_base_1:
                st.warning(
                    f"⚠️ Enrobage P1 changé à la main : {enrobage_1} mm"
                )

            if enrobage_2 != enrobage_base_2:
                st.warning(
                    f"⚠️ Enrobage P2 changé à la main : {enrobage_2} mm"
                )

            if noyau < 0:
                st.error("❌ Non conforme : épaisseur totale insuffisante")
            elif noyau < NOYAU_MIN:
                st.error("❌ Non conforme : noyau inférieur à 70 mm")
            else:
                st.success("✅ Conforme")


afficher_resultats(
    "Résultats normaux",
    ajout_retournement=0
)

st.write("---")

afficher_resultats(
    "Résultats mur retourné (+5 mm par paroi)",
    ajout_retournement=PLUS_RETOURNEMENT
)
