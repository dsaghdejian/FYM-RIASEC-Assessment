import streamlit as st
import pandas as pd
import sqlite3
import json
import hashlib
import datetime
import plotly.express as px

# ==========================================
# CONFIG
# ==========================================

st.set_page_config(
    page_title="Թեստ",
    page_icon="📋",
    layout="wide"
)

DB_FILE = "test.db"

# ==========================================
# DATABASE
# ==========================================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        position TEXT,
        warnings INTEGER DEFAULT 0,
        submit_time TEXT,
        answers TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY,
        hr_password TEXT
    )
    """)

    cur.execute(
        "INSERT OR IGNORE INTO settings(id,hr_password) VALUES(1,?)",
        (hash_password("1234"),)
    )

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_hr_password():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT hr_password FROM settings WHERE id=1")
    result = cur.fetchone()[0]
    conn.close()
    return result

def update_password(password):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "UPDATE settings SET hr_password=? WHERE id=1",
        (hash_password(password),)
    )

    conn.commit()
    conn.close()

def save_candidate(data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO candidates(
        first_name,
        last_name,
        position,
        warnings,
        submit_time,
        answers
    )
    VALUES(?,?,?,?,?,?)
    """,
    (
        data["first_name"],
        data["last_name"],
        data["position"],
        data["warnings"],
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        json.dumps(data["answers"], ensure_ascii=False)
    ))

    conn.commit()
    conn.close()

def get_candidates():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM candidates", conn)
    conn.close()
    return df

# ==========================================
# QUESTIONS
# ==========================================

OPTIONS = {
    "Բոլորովին համաձայն չեմ":1,
    "Համաձայն չեմ":2,
    "Ո՛չ համաձայն եմ, ո՛չ համաձայն չեմ":3,
    "Համաձայն եմ":4,
    "Լիովին համաձայն եմ":5
}

questions = [
"Պատրաստել խոհանոցային պահարաններ։",
"Ուսումնասիրել ջրի աղտոտվածությունը նվազեցնելու եղանակները։",
"Գրել գրքեր, պատմվածքներ կամ պիեսներ։",
"Երեխաներին սովորեցնել կարդալ։",
"Հիմնել սեփական բիզնեսը։",
"Ստեղծել էլեկտրոնային աղյուսակ՝ տեղեկատվությունը կազմակերպելու համար։",
"Վերանորոգել կենցաղային տեխնիկան։",
"Մշակել նոր դեղամիջոց։",
"Նվագել երաժշտական գործիքով։",
"Օգնել թմրանյութերի կամ ալկոհոլի օգտագործման հետ կապված խնդիրներ ունեցող մարդկանց։",
"Բանակցել գործարար պայմանագրերի շուրջ։",
"Ստուգել փաստաթղթերն ու ձևաթղթերը՝ սխալները հայտնաբերելու համար։",
"Էլեկտրոնային դետալների պատրաստում։",
"Մանրադիտակով ուսումնասիրել արյան նմուշները։",
"Մշակել նկարազարդումներ ամսագրերի կամ կայքերի համար։"
]

# RIASEC mapping
# Adjust if needed

question_types = [
"R","I","A","S","E","C",
"R","I","A","S","E","C",
"R","I","A"
]

descriptions = {
"RIA":"Highly practical, analytical and creative.",
"RSE":"Hands-on, people-focused and leadership-oriented.",
"SEC":"Strong teamwork, leadership and organization.",
"RIASEC":"Balanced profile across all dimensions."
}

strengths = {
"R":"Practical problem solving, technical work",
"I":"Analysis, research, investigation",
"A":"Creativity, innovation, imagination",
"S":"Helping others, communication",
"E":"Leadership, persuasion",
"C":"Organization, accuracy"
}

weaknesses = {
"R":"May avoid abstract discussions",
"I":"Can overanalyze",
"A":"May dislike structure",
"S":"May struggle with confrontation",
"E":"May become overly competitive",
"C":"May resist change"
}

# ==========================================
# INITIALIZE
# ==========================================

init_db()

if "page" not in st.session_state:
    st.session_state.page = "home"

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "warnings" not in st.session_state:
    st.session_state.warnings = 0

# ==========================================
# SECURITY JS
# ==========================================

security_js = """
<script>

document.addEventListener('copy',function(e){
e.preventDefault();
});

document.addEventListener('paste',function(e){
e.preventDefault();
});

document.addEventListener('visibilitychange', function() {
 if(document.hidden){
   alert("Զգուշացում: Հայտնաբերվել է էջից դուրս գալու փորձ");
 }
});

window.onblur = function() {
 alert("Զգուշացում: Հայտնաբերվել է պատուհանի փոփոխություն");
};

</script>
"""

st.components.v1.html(security_js,height=0)

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("### HR/Admin")

    if st.button("Admin Login"):
        st.session_state.page = "admin"

# ==========================================
# HOME
# ==========================================

if st.session_state.page == "home":

    st.title("Թեստ")

    st.markdown("""
Գնահատե՛ք, թե որքան հաճույքով կանեիք յուրաքանչյուր գործունեությունը։

Թեստը լրացնելուց անտեսե՛ք ձեր հմտությունները,
պատրաստվածությունն ու աշխատանքի վարձատրությունը։

Գնահատե՛ք միայն ձեր իրական հետաքրքրվածությունը։
""")

    first = st.text_input("Անուն")
    last = st.text_input("Ազգանուն")
    position = st.text_input("Պաշտոն")

    if st.button("Սկսել թեստը"):

        if first and last and position:

            st.session_state.first_name = first
            st.session_state.last_name = last
            st.session_state.position = position

            st.session_state.start_time = datetime.datetime.now()

            st.session_state.page = "test"
            st.rerun()

# ==========================================
# TEST
# ==========================================

elif st.session_state.page == "test":

    total_seconds = 300

    elapsed = (
        datetime.datetime.now()
        - st.session_state.start_time
    ).seconds

    remaining = max(0,total_seconds-elapsed)

    mins = remaining // 60
    secs = remaining % 60

    st.error(f"Մնացած ժամանակը: {mins:02d}:{secs:02d}")

    if remaining <= 0:
        st.warning("Ժամանակը ավարտվել է")
        st.session_state.page="finish"
        st.rerun()

    idx = st.session_state.q_index

    st.progress((idx+1)/len(questions))

    st.subheader(f"Հարց {idx+1} / {len(questions)}")
    st.write(questions[idx])

    answer = st.radio(
        "Ընտրեք",
        list(OPTIONS.keys()),
        key=f"radio_{idx}"
    )

    col1,col2 = st.columns(2)

    with col2:
        if st.button("Հաջորդ"):

            st.session_state.answers[idx] = OPTIONS[answer]

            if idx < len(questions)-1:
                st.session_state.q_index += 1
            else:
                st.session_state.page = "finish"

            st.rerun()

# ==========================================
# FINISH
# ==========================================

elif st.session_state.page == "finish":

    if "submitted" not in st.session_state:

        save_candidate({
            "first_name": st.session_state.first_name,
            "last_name": st.session_state.last_name,
            "position": st.session_state.position,
            "warnings": st.session_state.warnings,
            "answers": st.session_state.answers
        })

        st.session_state.submitted = True

    st.success("Թեստն ավարտված է")

    st.info(
        "Ձեր պատասխանները պաշտպանված են և հասանելի են միայն HR բաժնին։"
    )

    st.warning(
        "Թեստի արդյունքները ձեզ չեն ցուցադրվում։"
    )

    if st.button("Վերադառնալ գլխավոր էջ"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# ADMIN
# ==========================================

elif st.session_state.page == "admin":

    st.title("HR Dashboard")

    password = st.text_input(
        "Password",
        type="password"
    )

    if hash_password(password) == get_hr_password():

        st.success("Access Granted")

        st.subheader("Փոխել գաղտնաբառը")

        new_pw = st.text_input(
            "New Password",
            type="password"
        )

        if st.button("Update Password"):

            if new_pw:
                update_password(new_pw)
                st.success("Password Updated")

        df = get_candidates()

        if len(df) > 0:

            st.subheader("Candidates")

            st.dataframe(df[[
                "id",
                "first_name",
                "last_name",
                "position",
                "submit_time"
            ]])

            counts = {}

            for _, row in df.iterrows():

                ans = json.loads(row["answers"])

                scores = {
                    "R":0,
                    "I":0,
                    "A":0,
                    "S":0,
                    "E":0,
                    "C":0
                }

                for i,val in ans.items():

                    t = question_types[int(i)]
                    scores[t] += val

                code = "".join(
                    sorted(
                        scores,
                        key=scores.get,
                        reverse=True
                    )[:3]
                )

                counts[code] = counts.get(code,0)+1

            chart = pd.DataFrame(
                {
                    "Profile":list(counts.keys()),
                    "Count":list(counts.values())
                }
            )

            fig = px.bar(
                chart,
                x="Profile",
                y="Count",
                color="Profile"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.subheader("Candidate Profiles")

            for _, row in df.iterrows():

                answers = json.loads(row["answers"])

                scores = {
                    "R":0,
                    "I":0,
                    "A":0,
                    "S":0,
                    "E":0,
                    "C":0
                }

                for i,val in answers.items():

                    t = question_types[int(i)]
                    scores[t]+=val

                profile = "".join(
                    sorted(
                        scores,
                        key=scores.get,
                        reverse=True
                    )[:3]
                )

                st.markdown("---")

                st.write(
                    f"### {row['first_name']} {row['last_name']}"
                )

                st.write("Position:", row["position"])
                st.write("Profile:", profile)

                st.write(
                    descriptions.get(
                        profile,
                        "Combined personality profile"
                    )
                )

                for p in profile:

                    st.write(
                        f"✅ {p} Strength:",
                        strengths[p]
                    )

                for p in profile:

                    st.write(
                        f"⚠️ {p} Weakness:",
                        weaknesses[p]
                    )

                st.write("Scores")
                st.json(scores)

    else:
        st.info("Enter HR Password")