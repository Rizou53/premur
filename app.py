import streamlit as st
import math

st.set_page_config(page_title="Prémur IA V10", layout="wide")
st.title("🏗️ Prémur - CONFIG")

# --- Tableau de sélection -------------------------------------------------
# Une ligne par réglage, une case par choix possible. La case choisie se grise.
# Aucun de ces choix n'entre encore dans le calcul : les règles restent à définir.

EPAISSEURS = ["16", "18", "20", "24", "25", "30", "35", "40"]

SELECTIONS = [
    {"cle": "usine", "intitule": "Usine",
     "options": ["Usine 1", "Usine 2", "Usine 3"], "defaut": None},
    {"cle": "coupe_feu", "intitule": "Coupe-feu",
     "options": ["0,5 H", "1 H", "1,5 H", "2 H", "2,5 H", "3 H", "3,5 H", "4 H"], "defaut": None},
    {"cle": "epaisseur", "intitule": "Épaisseur (cm)",
     "options": EPAISSEURS, "defaut": "20"},
]

# Épaisseurs (cm) qu'une usine ne sait pas produire. Une usine absente de ce
# tableau fabrique toute la gamme. À compléter au fur et à mesure.
EPAISSEURS_HORS_GAMME = {
    "Usine 1": ["16"],
}

def indisponibles(cle_ligne):
    """Options à barrer sur cette ligne, compte tenu des choix déjà faits."""
    if cle_ligne != "epaisseur":
        return set()
    return set(EPAISSEURS_HORS_GAMME.get(st.session_state.get("sel_usine"), []))

def tableau_selections():
    """Dessine les lignes de choix et renvoie {clé: option choisie ou None}."""
    for ligne in SELECTIONS:
        st.session_state.setdefault(f"sel_{ligne['cle']}", ligne["defaut"])

    # Changer d'usine peut retirer de la gamme l'épaisseur déjà choisie : on la
    # relâche, sinon le calcul tournerait sur une épaisseur que l'usine ne fait pas.
    for ligne in SELECTIONS:
        etat = f"sel_{ligne['cle']}"
        if st.session_state[etat] in indisponibles(ligne["cle"]):
            st.session_state[etat] = None

    choisis = {}
    regles_grisees = []

    for ligne in SELECTIONS:
        cle, intitule, options = ligne["cle"], ligne["intitule"], ligne["options"]
        etat = f"sel_{cle}"
        hors_gamme = indisponibles(cle)

        cols = st.columns([1.4] + [1] * len(options), vertical_alignment="center")
        cols[0].markdown(f"<div class='intitule-choix'>{intitule}</div>", unsafe_allow_html=True)

        for indice, (col, option) in enumerate(zip(cols[1:], options)):
            # Recliquer sur la case déjà choisie l'annule : pas d'impasse.
            if col.button(
                option,
                key=f"btn_{cle}_{indice}",
                use_container_width=True,
                disabled=option in hors_gamme,
            ):
                st.session_state[etat] = None if st.session_state[etat] == option else option
                st.rerun()

            if st.session_state[etat] == option:
                regles_grisees.append(f".st-key-btn_{cle}_{indice} button")

        if hors_gamme:
            usine = st.session_state.get("sel_usine")
            cols[0].caption(f"{usine} ne produit pas : {', '.join(sorted(hors_gamme))} cm")

        choisis[cle] = st.session_state[etat]

    if regles_grisees:
        st.markdown(
            "<style>%s { background: rgba(128,128,128,.42) !important; "
            "border-color: rgba(128,128,128,.75) !important; font-weight: 700 !important; }</style>"
            % ", ".join(regles_grisees),
            unsafe_allow_html=True,
        )

    return choisis

def resume_selections(choisis):
    """Ligne de rappel affichée au-dessus des résultats."""
    morceaux = [
        f"{ligne['intitule']} : {choisis[ligne['cle']] or '—'}"
        for ligne in SELECTIONS
    ]
    return " · ".join(morceaux)

st.markdown(
    """
    <style>
    .intitule-choix {
        font-weight: 600; font-size: 0.9rem;
        padding: 6px 4px; opacity: 0.85;
    }
    /* Les cases de choix : bords droits et jointifs, pour un rendu de tableau. */
    [class*="st-key-btn_"] button {
        border-radius: 4px;
        border: 1px solid rgba(128, 128, 128, 0.35);
        padding: 6px 4px;
    }
    /* Hors gamme pour l'usine choisie : encore lisible, mais visiblement inerte. */
    [class*="st-key-btn_"] button:disabled {
        opacity: 0.3;
        border-style: dashed !important;
        background: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

choix = tableau_selections()

st.write("---")

ENROBAGE_INTERIEUR = 15
EPAISSEUR_MIN_PAROI = 50
NOYAU_MIN = 70
PLUS_RETOURNEMENT = 5

HA_POUTRELLE_P1 = 6
HA_POUTRELLE_P2 = 8

POUTRELLE_MIN = 90
POUTRELLE_MAX = 400
PAS_POUTRELLE = 10
TOLERANCE_POUTRELLE = 2

# Diamètres des fils en mm, par treillis puis par type de pose.
# Le treillis n'est pas posé de la même façon en type 2 et en type 3 : les fils
# vertical et horizontal ne sont donc pas les mêmes d'un type à l'autre.
treillis_data = {
    "PAF10": {2: {"vertical": 6, "horizontal": 6}, 3: {"vertical": 6, "horizontal": 6}},
    "ST20V": {2: {"vertical": 6, "horizontal": 6}, 3: {"vertical": 6, "horizontal": 6}},
    "ST20H": {2: {"vertical": 6, "horizontal": 6}, 3: {"vertical": 6, "horizontal": 8}},
    "ST25V": {2: {"vertical": 8, "horizontal": 6}, 3: {"vertical": 6, "horizontal": 6}},
    "ST25H": {2: {"vertical": 6, "horizontal": 6}, 3: {"vertical": 6, "horizontal": 8}},
    "ST30V": {2: {"vertical": 6, "horizontal": 6}, 3: {"vertical": 6, "horizontal": 6}},
    "ST30H": {2: {"vertical": 6, "horizontal": 6}, 3: {"vertical": 6, "horizontal": 6}},
    "ST35V": {2: {"vertical": 8, "horizontal": 6}, 3: {"vertical": 8, "horizontal": 6}},
    "ST35H": {2: {"vertical": 6, "horizontal": 8}, 3: {"vertical": 6, "horizontal": 8}},
    "ST50V": {2: {"vertical": 8, "horizontal": 8}, 3: {"vertical": 8, "horizontal": 8}},
    "ST50H": {2: {"vertical": 6, "horizontal": 8}, 3: {"vertical": 6, "horizontal": 8}},
    "ST60V": {2: {"vertical": 12, "horizontal": 8}, 3: {"vertical": 10, "horizontal": 8}},
    "ST60H": {2: {"vertical": 8, "horizontal": 10}, 3: {"vertical": 6, "horizontal": 10}},
    "ST15C": {2: {"vertical": 6, "horizontal": 6}, 3: {"vertical": 6, "horizontal": 6}},
    "ST25C": {2: {"vertical": 8, "horizontal": 6}, 3: {"vertical": 6, "horizontal": 8}},
    "ST40C": {2: {"vertical": 10, "horizontal": 8}, 3: {"vertical": 8, "horizontal": 10}},
    "ST50C": {2: {"vertical": 10, "horizontal": 8}, 3: {"vertical": 8, "horizontal": 12}},
    "ST65C": {2: {"vertical": 12, "horizontal": 10}, 3: {"vertical": 10, "horizontal": 10}},
}

# Ordre d'affichage des classes d'exposition dans les listes déroulantes.
CLASSES_EXPOSITION = [
    "XC1", "XC2", "XC3", "XC4",
    "XD1", "XD2", "XD3",
    "XS1", "XS2", "XS3",
    "XF1", "XF2", "XF3", "XF4",
    "XA1", "XA2", "XA3",
]

# Enrobage extérieur minimal (mm) par classe d'exposition. Ces valeurs sont
# propres à chaque usine : seule l'Usine 1 est renseignée pour l'instant, les
# autres restent en attente plutôt que d'hériter de chiffres qui ne sont pas
# les leurs.
ENROBAGES_PAR_USINE = {
    "Usine 1": {
        "XC1": 15, "XC2": 15, "XC3": 15,
        "XC4": 20, "XF1": 20,
        "XF2": 25, "XF3": 25, "XS1": 25, "XD1": 25, "XA1": 25,
        "XS2": 30, "XD2": 30, "XA2": 30,
        "XF4": 35,
        "XS3": 40, "XD3": 40, "XA3": 40,
    },
}

def arrondi_5(valeur):
    return math.ceil(valeur / 5) * 5

def fils(treillis, type_paroi):
    return treillis_data[treillis][type_paroi]

def acier_poutrelle_p1(treillis, type_paroi):
    return max(fils(treillis, type_paroi)["vertical"], HA_POUTRELLE_P1)

def acier_poutrelle_p2(treillis, type_paroi):
    return max(fils(treillis, type_paroi)["vertical"], HA_POUTRELLE_P2)

def calcul_paroi(enrobage_ext, treillis, type_paroi, ajout_retournement=0):
    f = fils(treillis, type_paroi)

    epaisseur_theorique = (
        enrobage_ext
        + f["vertical"]
        + f["horizontal"]
        + ENROBAGE_INTERIEUR
        + ajout_retournement
    )

    epaisseur_paroi = arrondi_5(max(EPAISSEUR_MIN_PAROI, epaisseur_theorique))

    return epaisseur_theorique, epaisseur_paroi

def hauteur_poutrelle(
    epaisseur_totale_mm,
    enrobage_p1,
    enrobage_p2,
    treillis_p1,
    treillis_p2,
    type_p1,
    type_p2,
):
    return (
        epaisseur_totale_mm
        - enrobage_p1
        - enrobage_p2
        - acier_poutrelle_p1(treillis_p1, type_p1)
        - acier_poutrelle_p2(treillis_p2, type_p2)
    )

def poutrelle_standard_proche(hauteur):
    poutrelles = list(range(POUTRELLE_MIN, POUTRELLE_MAX + 1, PAS_POUTRELLE))
    return min(poutrelles, key=lambda x: abs(x - hauteur))

def calcul_poutrelle(
    epaisseur_totale_mm,
    enrobage_p1,
    enrobage_p2,
    treillis_p1,
    treillis_p2,
    type_p1,
    type_p2,
):
    h_initiale = hauteur_poutrelle(
        epaisseur_totale_mm,
        enrobage_p1,
        enrobage_p2,
        treillis_p1,
        treillis_p2,
        type_p1,
        type_p2,
    )

    poutrelle = poutrelle_standard_proche(h_initiale)
    bas = poutrelle - TOLERANCE_POUTRELLE
    haut = poutrelle + TOLERANCE_POUTRELLE

    correction = 0
    enrobage_p1_corrige = enrobage_p1
    h_corrigee = h_initiale

    if h_initiale < bas:
        correction = bas - h_initiale
        enrobage_p1_corrige = enrobage_p1 - correction
        h_corrigee = bas

    elif h_initiale > haut:
        correction = h_initiale - haut
        enrobage_p1_corrige = enrobage_p1 + correction
        h_corrigee = haut

    poutrelle_finale = poutrelle_standard_proche(h_corrigee)

    return {
        "hauteur_initiale": h_initiale,
        "hauteur_corrigee": h_corrigee,
        "poutrelle": poutrelle_finale,
        "correction": correction,
        "enrobage_p1_corrige": enrobage_p1_corrige,
    }

# L'enrobage dépend de l'usine : sans usine choisie, on ne sait pas quelle
# table appliquer, donc on ne calcule rien plutôt que de deviner.
if choix["usine"] is None:
    st.warning("Choisissez une usine : les enrobages minimaux lui sont propres.")
    st.stop()

if choix["usine"] not in ENROBAGES_PAR_USINE:
    st.warning(
        f"Les enrobages de {choix['usine']} ne sont pas encore renseignés. "
        "Seule l'Usine 1 est programmée pour l'instant."
    )
    st.stop()

enrobage_data = ENROBAGES_PAR_USINE[choix["usine"]]

if choix["epaisseur"] is None:
    st.warning("Choisissez une épaisseur de prémur pour lancer le calcul.")
    st.stop()

epaisseur_totale_cm = int(choix["epaisseur"])
epaisseur_totale_mm = epaisseur_totale_cm * 10

col1, col2 = st.columns(2)

with col1:
    st.header("Paroi 1")
    classe_1 = st.selectbox("Classe d’exposition Paroi 1", CLASSES_EXPOSITION)
    treillis_1 = st.selectbox("Treillis Paroi 1", list(treillis_data.keys()))

with col2:
    st.header("Paroi 2")
    classe_2 = st.selectbox("Classe d’exposition Paroi 2", CLASSES_EXPOSITION)
    treillis_2 = st.selectbox("Treillis Paroi 2", list(treillis_data.keys()))

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
    st.caption(resume_selections(choix))
    cols = st.columns(4)

    for col, (nom_scenario, type_p1, type_p2) in zip(cols, scenarios):
        with col:
            st.markdown(f"### {nom_scenario}")

            fils_1 = fils(treillis_1, type_p1)
            fils_2 = fils(treillis_2, type_p2)

            st.write("**Paroi 1**")
            st.caption(
                f"{treillis_1} TYPE {type_p1} — "
                f"V {fils_1['vertical']} / H {fils_1['horizontal']}"
            )
            enrobage_1 = st.number_input(
                f"Enrobage P1 — {classe_1}",
                min_value=0,
                value=enrobage_base_1,
                step=5,
                key=f"{titre}_p1_{nom_scenario}_{classe_1}",
            )

            st.write("**Paroi 2**")
            st.caption(
                f"{treillis_2} TYPE {type_p2} — "
                f"V {fils_2['vertical']} / H {fils_2['horizontal']}"
            )
            enrobage_2 = st.number_input(
                f"Enrobage P2 — {classe_2}",
                min_value=0,
                value=enrobage_base_2,
                step=5,
                key=f"{titre}_p2_{nom_scenario}_{classe_2}",
            )

            ep_theo_1, ep_p1 = calcul_paroi(
                enrobage_1, treillis_1, type_p1, ajout_retournement
            )
            ep_theo_2, ep_p2 = calcul_paroi(
                enrobage_2, treillis_2, type_p2, ajout_retournement
            )

            noyau = epaisseur_totale_mm - ep_p1 - ep_p2

            poutrelle = calcul_poutrelle(
                epaisseur_totale_mm,
                enrobage_1,
                enrobage_2,
                treillis_1,
                treillis_2,
                type_p1,
                type_p2,
            )

            st.write(f"Paroi 1 : **{ep_p1} mm**")
            st.write(f"Paroi 2 : **{ep_p2} mm**")
            st.write(f"Noyau : **{noyau:.0f} mm**")

            st.write(f"Hauteur théorique poutrelle : **{poutrelle['hauteur_initiale']:.0f} mm**")
            st.write(f"Poutrelle retenue : **{poutrelle['poutrelle']} mm**")

            ecart = poutrelle["hauteur_initiale"] - poutrelle["poutrelle"]

            st.write(f"Écart poutrelle : {ecart:+.0f} mm")

            if enrobage_1 != enrobage_base_1:
                st.warning(f"⚠️ Enrobage P1 changé à la main : {enrobage_1} mm")

            if enrobage_2 != enrobage_base_2:
                st.warning(f"⚠️ Enrobage P2 changé à la main : {enrobage_2} mm")

            if noyau < 0:
                st.error("❌ Non conforme : épaisseur totale insuffisante")
            elif noyau < NOYAU_MIN:
                st.error("❌ Non conforme : noyau inférieur à 70 mm")
            else:
                st.success("✅ Conforme")

afficher_resultats("Résultats normaux", ajout_retournement=0)

st.write("---")

afficher_resultats("Résultats mur retourné (+5 mm par paroi)", ajout_retournement=PLUS_RETOURNEMENT)
