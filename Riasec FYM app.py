import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="Թեստ",
    page_icon="📋",
    layout="centered"
)

# ----------------------------
# FILE STORAGE
# ----------------------------

RESULTS_FILE = "results.csv"

if not os.path.exists(RESULTS_FILE):
    pd.DataFrame(
        columns=[
            "First Name",
            "Last Name",
            "Position",
            "Submitted",
            "Profile",
            "Answers"
        ]
    ).to_csv(RESULTS_FILE, index=False)

# ----------------------------
# HR PASSWORD
# ----------------------------

if "hr_password" not in st.session_state:
    st.session_state.hr_password = "1234"

# ----------------------------
# QUESTIONS
# ----------------------------

questions = [
    ("Պատրաստել խոհանոցային պահարաններ։", "R"),
    ("Ուսումնասիրել ջրի աղտոտվածությունը նվազեցնելու եղանակները։", "I"),
    ("Գրել գրքեր, պատմվածքներ կամ պիեսներ։", "A"),
    ("Երեխաներին սովորեցնել կարդալ։", "S"),
    ("Հիմնել սեփական բիզնեսը։", "E"),
    ("Ստեղծել էլեկտրոնային աղյուսակ՝ տեղեկատվությունը կազմակերպելու համար։", "C"),
    ("Վերանորոգել կենցաղային տեխնիկան։", "R"),
    ("Մշակել նոր դեղամիջոց։", "I"),
    ("Նվագել երաժշտական գործիքով։", "A"),
    ("Օգնել թմրանյութերի կամ ալկոհոլի օգտագործման հետ կապված խնդիրներ ունեցող մարդկանց։", "S"),
    ("Բանակ