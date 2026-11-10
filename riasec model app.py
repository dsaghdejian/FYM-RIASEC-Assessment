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
    ("Բանակցել գործարար պայմանագրերի շուրջ։", "E"),
    ("Ստուգել փաստաթղթերն ու ձևաթղթերը՝ սխալները հայտնաբերելու համար։", "C"),
    ("Էլեկտրոնային դետալների պատրաստում։", "R"),
    ("Մանրադիտակով ուսումնասիրել արյան նմուշները։", "I"),
    ("Մշակել նկարազարդումներ ամսագրերի կամ կայքերի համար։", "A"),
]

options = {
    "Բոլորովին համաձայն չեմ": 1,
    "Համաձայն չեմ": 2,
    "Ո՛չ համաձայն եմ, ո՛չ համաձայն չեմ": 3,
    "Համաձայն եմ": 4,
    "Լիովին համաձայն եմ": 5
}

# ----------------------------
# SESSION VARIABLES
# ----------------------------

if "page" not in st.session_state:
    st.session_state.page = "home"

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

# ----------------------------
# HOME PAGE
# ----------------------------

if st.session_state.page == "home":

    st.title("Թեստ")

    st.markdown("""
Գնահատե՛ք, թե որքան հաճույքով կանեիք յուրաքանչյուր գործունեությունը։

Թեստը լրացնելուց անտեսե՛ք ձեր հմտությունները,
պատրաստվածությունն ու աշխատանքի վարձատրությունը։

Գնահատե՛ք միայն ձեր իրական հետաքրքրվածությունը։
""")

    first_name = st.text_input("Անուն")
    last_name = st.text_input("Ազգանուն")
    position = st.text_input("Պաշտոն")

    if st.button("Սկսել"):

        if first_name and last_name and position:

            st.session_state.first_name = first_name
            st.session_state.last_name = last_name
            st.session_state.position = position

            st.session_state.page = "test"

            st.rerun()

# ----------------------------
# TEST PAGE
# ----------------------------

elif st.session_state.page == "test":

    idx = st.session_state.question_index

    total = len(questions)

    st.progress((idx + 1) / total)

    st.subheader(f"Հարց {idx+1} / {total}")

    question_text = questions[idx][0]

    st.write(question_text)

    answer = st.radio(
        "Ընտրեք պատասխանը",
        list(options.keys())
    )

    if st.button("Հաջորդ"):

        st.session_state.answers[idx] = options[answer]

        if idx < total - 1:

            st.session_state.question_index += 1

        else:

            scores = {
                "R": 0,
                "I": 0,
                "A": 0,
                "S": 0,
                "E": 0,
                "C": 0
            }

            for q_index, value in st.session_state.answers.items():

                category = questions[q_index][1]

                scores[category] += value

            profile = "".join(
                sorted(
                    scores,
                    key=scores.get,
                    reverse=True
                )[:3]
            )

            df = pd.read_csv(RESULTS_FILE)

            new_row = pd.DataFrame([{
                "First Name": st.session_state.first_name,
                "Last Name": st.session_state.last_name,
                "Position": st.session_state.position,
                "Submitted": datetime.now(),
                "Profile": profile,
                "Answers": json.dumps(
                    st.session_state.answers,
                    ensure_ascii=False
                )
            }])

            df = pd.concat([df, new_row])

            df.to_csv(RESULTS_FILE, index=False)

            st.session_state.page = "finished"

        st.rerun()

# ----------------------------
# FINISHED PAGE
# ----------------------------

elif st.session_state.page == "finished":

    st.success("Թեստն ավարտված է")

    st.info(
        "Ձեր պատասխանները պաշտպանված են և հասանելի են միայն HR բաժնին։"
    )

    st.warning(
        "Ձեզ չեն ցուցադրվում թեստի արդյունքները։"
    )

    if st.button("Վերադառնալ գլխավոր էջ"):

        st.session_state.clear()

        st.rerun()

# ----------------------------
# ADMIN PAGE
# ----------------------------

st.sidebar.title("HR")

if st.sidebar.button("Admin Login"):
    st.session_state.page = "admin"
    st.rerun()

if st.session_state.page == "admin":

    st.title("HR Dashboard")

    password = st.text_input(
        "Password",
        type="password"
    )

    if password == st.session_state.hr_password:

        st.success("Access Granted")

        new_password = st.text_input(
            "New Password",
            type="password"
        )

        if st.button("Change Password"):

            if new_password:
                st.session_state.hr_password = new_password
                st.success("Password Updated")

        data = pd.read_csv(RESULTS_FILE)

        st.subheader("Candidates")

        st.dataframe(data)

        if not data.empty:

            st.subheader("Profile Statistics")

            profile_counts = (
                data["Profile"]
                .value_counts()
            )

            st.bar_chart(profile_counts)

    elif password:
        st.error("Incorrect Password")