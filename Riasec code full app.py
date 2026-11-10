
# -*- coding: utf-8 -*-
"""
Career Interest Assessment — Streamlit App
Candidate-facing: no test name, no results shown.
HR/Admin: password-protected results, statistics, archetype analysis.
"""

import streamlit as st
import pandas as pd
import hashlib
import os
import time
import datetime

# ------------------------------------------------------------- page config
st.set_page_config(page_title="Թեստ", page_icon="📝", layout="centered")

# ------------------------------------------------------------- constants
OPTIONS = [
    "Բոլորովին համաձայն չեմ",
    "Համաձայն չեմ",
    "Ո՛չ համաձայն եմ, ո՛չ համաձայն չեմ",
    "Համաձայն եմ",
    "Լիովին համաձայն եմ",
]

# (question, internal code) — codes are NEVER shown to the candidate
QUESTIONS = [
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

CODES = ["R", "I", "A", "S", "E", "C"]
TEST_DURATION = 300  # 5 minutes
PW_FILE = "admin_password.txt"
RESULTS_FILE = "results.csv"

# ------------------------------------------------------------- archetypes (HR only)
ARCHETYPES = {
    "R": {
        "name": "Գործնական (R)",
        "strengths": "Լավագույնը սովորում է պրակտիկ փորձից։ Ձեռքերով աշխատելու, սարքավորումներով զբաղվելու, վերանորոգելու և կառուցելու ունակություն։ Հուսալի, կայուն և արդյունավետ է ֆիզիկական և տեխնիկական աշխատանքում։",
        "weaknesses": "Կարող է ձանձրանալ գրասենյակային կամ չափազանց մտահորizontային աշխատանքում։ Հաճախ խուսափում է հանրային ելույթներից և երկար խոսակցություններից։",
    },
    "I": {
        "name": "Ուսումնասիրող (I)",
        "strengths": "Վերլուծական մտածողություն, հետազոտական հակում, տրամաբանություն։ Լավն է գիտական, բժշկական, ծրագրային և վերլուծական աշխատանքներում։ Սիրում է լուծել բարդ խնդիրներ։",
        "weaknesses": "Կարող է չափազանց տեխնիկական լինել շփման մեջ, խուսափել էմոցիոնալ որոշումներից։ Հնարավոր է բաց թողնել գործնական մանրամասները։",
    },
    "A": {
        "name": "Արվեստագետ (A)",
        "strengths": "Ստեղծարարություն, երևակայություն, արտահայտչականություն։ Հաջողություն է գրանցում արվեստի, դիզայնի, գրականության և նորարարական ոլորտներում։ Ազատ է մտածում։",
        "weaknesses": "Կարող է լինել անկանոն աշխատաոճի սիրահար, դժվարանում է կառուցվածքված և կրկնվող առաջադրանքների հետ։ Հաճախ զգայուն է քննադատության նկատմամբ։",
    },
    "S": {
        "name": "Կենդանի օգնական (S)",
        "strengths": "Էմպաթիա, հաղորդակցման բարձր հմտություն, ցանկություն օգնելու։ Հարմար է կրթության, առողջապահության, սոցիալական աշխատանքի և ղեկավարման ոլորտներում։",
        "weaknesses": "Կարող է չափազանց զոհաբեր լինել, դժվարանում է մարդկանց հետ կոնֆլիկտել՝ նույնիսկ երբ դա անհրաժեշտ է։ Հնարավոր է խուսափի մեծ ռիսկերից։",
    },
    "E": {
        "name": "Կազմակերպիչ (E)",
        "strengths": "Անգամինություն, համոզչություն, նպատակասլացություն։ Հարմար է վաճառքի, բիզնեսի, կառավարման և բանակցությունների ոլորտներում։ Լավ է աշխատում ճնշման պայմաններում։",
        "weaknesses": "Կարող է անհամբեր լինել մանրամասների և երկար պրոցեսների նկատմամբ։ Հնարավոր է չափազանց մրցակցային լինել թիմային միջավայրում։",
    },
    "C": {
        "name": "Գրագետ կազմակերպիչ (C)",
        "strengths": "Ճշգրտություն, կազմակերպվածություն, հարգանք կանոնների և գործընթացների նկատմամբ։ Հարմար է ֆինանսների, հաշվապահության, փաստաթղթերի և վերահսկողության ոլորտներում։",
        "weaknesses": "Կարող է դժվարանում հարմարվել փոփոխություններին և չձևավորված իրավիճակներին։ Հնարավոր է չափազանց շեշտադրի մանրուքները՝ կորցնելով ընդհանուր պատկերը։",
    },
}

# ------------------------------------------------------------- css
st.markdown("""
<style>
    .stApp { background: linear-gradient(160deg, #f4f6fb 0%, #e9edf7 100%); }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .main-title { font-size: 3rem; font-weight: 800; color: #312e81; text-align: center; margin-bottom: 0.2rem; }
    .subtitle { font-size: 1.15rem; color: #4b5563; text-align: center; margin-bottom: 2rem; line-height: 1.7; }
    .card { background: #ffffff; border-radius: 16px; padding: 2rem 2.2rem;
            box-shadow: 0 8px 30px rgba(49,46,129,0.10); }
    .timer { font-size: 1.6rem; font-weight: 700; color: #dc2626; text-align: center; }
    .warn { color: #b45309; font-size: 0.9rem; text-align: center; }
    .question-text { font-size: 1.35rem; font-weight: 600; color: #1f2937; margin-bottom: 1.2rem; }
    div.stButton > button { background: linear-gradient(90deg, #4f46e5, #7c3aed); color: white;
        border: none; border-radius: 10px; padding: 0.6rem 1.8rem; font-size: 1.05rem; font-weight: 600; }
    div.stButton > button:hover { background: linear-gradient(90deg, #4338ca, #6d28d9); color: white; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------- helpers
def hash_pw(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()

def get_pw_hash():
    if os.path.exists(PW_FILE):
        with open(PW_FILE, "r", encoding="utf-8") as f:
            stored = f.read().strip()
            if stored:
                return stored
    try:
        return st.secrets["hr_password"]
    except Exception:
        return hash_pw("1234")

def check_password(p: str) -> bool:
    return hash_pw(p) == get_pw_hash()

def change_password(new_pw: str):
    with open(PW_FILE, "w", encoding="utf-8") as f:
        f.write(hash_pw(new_pw))

def render_html_component(html_str):
    """Render HTML/JS in a component iframe across Streamlit versions."""
    try:
        import streamlit.components.v1 as components
        return components.html(html_str, height=1)
    except Exception:
        return st.iframe(html_str, height=1)

def anti_cheat_block():
    """Blocks copy/paste/cut, warns on page leave, reports tab switches to the server."""
    js = """
    <script>
    const doc = window.parent.document;
    doc.__ac_cleanup = false;
    if (!doc.__ac_installed) {
        doc.__ac_installed = true;
        const blocked = function(e){ if (!doc.__ac_cleanup) e.preventDefault(); };
        doc.addEventListener('copy',  blocked);
        doc.addEventListener('cut',   blocked);
        doc.addEventListener('paste', blocked);
        doc.addEventListener('visibilitychange', function(){
            if (doc.hidden && !doc.__ac_cleanup) {
                try { Streamlit.setComponentValue("tab_switch_" + Date.now()); } catch(err) {}
            }
        });
        doc.addEventListener('mouseleave', function(e){
            if (e.clientY <= 0 && !doc.__ac_cleanup) {
                try { Streamlit.setComponentValue("page_leave_" + Date.now()); } catch(err) {}
            }
        });
        window.parent.addEventListener('beforeunload', function(e){
            if (doc.__ac_cleanup) return;
            e.preventDefault(); e.returnValue = '';
        });
    }
    </script>
    """
    return render_html_component(js)

def anti_cheat_cleanup():
    """Disable anti-cheat listeners (test is finished)."""
    return render_html_component("""
    <script>window.parent.document.__ac_cleanup = true;</script>
    """)

def load_results():
    if os.path.exists(RESULTS_FILE):
        return pd.read_csv(RESULTS_FILE)
    return pd.DataFrame()

def submit_test():
    answers = [st.session_state.get(f"q{i}", -1) for i in range(len(QUESTIONS))]
    scores = {c: 0 for c in CODES}
    for (q, code), a in zip(QUESTIONS, answers):
        scores[code] += max(a, 0)  # unanswered = 0

    ranked = sorted(CODES, key=lambda c: (-scores[c], CODES.index(c)))
    code3 = "".join(ranked[:3])

    row = {
        "Անուն": st.session_state.first_name,
        "Ազգանուն": st.session_state.last_name,
        "Պաշտոն": st.session_state.position,
        "Ամսաթիվ": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Կոդ": code3,
        "Տաբի փոխարկումներ": st.session_state.get("tab_switches", 0),
    }
    for c in CODES:
        row[c] = scores[c]
    for i in range(len(QUESTIONS)):
        row[f"Պ{i+1}"] = answers[i] if answers[i] >= 0 else "—"

    df = load_results()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(RESULTS_FILE, index=False, encoding="utf-8-sig")
    st.session_state.page = "done"

# ------------------------------------------------------------- session state
defaults = {
    "page": "home", "q_index": 0, "start_time": None,
    "tab_switches": 0, "first_name": "", "last_name": "", "position": "",
    "hr_auth": False, "finished": False, "last_evt": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================= SIDEBAR — HR LOGIN
with st.sidebar:
    st.markdown("## 🔐 HR")
    if not st.session_state.hr_auth:
        pw = st.text_input("Գաղտնաբառ", type="password", key="hr_pw_input")
        if st.button("Մուտք"):
            if check_password(pw):
                st.session_state.hr_auth = True
                st.rerun()
            else:
                st.error("Սխալ գաղտնաբառ")
    else:
        st.success("Դուք մուտք եք գործել")
        if st.button("Դուրս գալ"):
            st.session_state.hr_auth = False
            st.rerun()

# ============================================================= HR DASHBOARD
if st.session_state.hr_auth:
    st.markdown('<div class="main-title">📊 HR Վահանակ</div>', unsafe_allow_html=True)
    df = load_results()

    if df.empty:
        st.info("Դեռևս արդյունքներ չկան։")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Ընդամենը թեկնածու", len(df))
        c2.metric("Վերջին թեկնածու", str(df.iloc[-1]["Անուն"]) + " " + str(df.iloc[-1]["Ազգանուն"]))
        c3.metric("Տաբի փոխարկումներ (վերջին)", int(df.iloc[-1]["Տաբի փոխարկումներ"]))

        st.subheader("Վիճակագրություն ըստ տիպերի")
        st.bar_chart(df.set_index("Կոդ")[[c for c in CODES]].mean(numeric_only=True))

        st.subheader("Թեկնածուների ցանկ")
        st.dataframe(df[["Անուն", "Ազգանուն", "Պաշտոն", "Կոդ", "Ամսաթիվ", "Տաբի փոխարկումներ"]],
                     use_container_width=True)

        st.subheader("Թեկնածուի մանրամասն տվյալներ")
        df["full"] = df["Անուն"].astype(str) + " " + df["Ազգանուն"].astype(str) + " — " + df["Ամսաթիվ"].astype(str)
        sel = st.selectbox("Ընտրեք թեկնածուին", df["full"].tolist())
        cand = df[df["full"] == sel].iloc[0]

        st.markdown(f"**Կոդ՝ {cand['Կոդ']}**")
        for letter in str(cand["Կոդ"]):
            if letter in ARCHETYPES:
                a = ARCHETYPES[letter]
                with st.expander(f"{a['name']}"):
                    st.markdown(f"**Կարողություններ.** {a['strengths']}")
                    st.markdown(f"**Թույլ կողմեր.** {a['weaknesses']}")

        st.markdown("**Պատասխաններ** (0 = Բոլորովին համաձայն չեմ ... 4 = Լիովին համաձայն եմ)")
        ans_rows = []
        for i, (q, _) in enumerate(QUESTIONS):
            ans_rows.append({"Հարց": q, "Պատասխան": cand[f"Պ{i+1}"]})
        st.dataframe(pd.DataFrame(ans_rows), use_container_width=True)

        st.download_button("Ներբեռնել բոլոր արդյունքները (CSV)", df.drop(columns=["full"]).to_csv(index=False).encode("utf-8-sig"),
                           "results.csv", "text/csv")

    st.divider()
    st.subheader("Փոխել գաղտնաբառը")
    np1 = st.text_input("Նոր գաղտնաբառ", type="password", key="np1")
    np2 = st.text_input("Կրկնել նոր գաղտնաբառը", type="password", key="np2")
    if st.button("Պահպանել գաղտնաբառը"):
        if not np1:
            st.error("Գաղտնաբառը դատարկ է")
        elif np1 != np2:
            st.error("Գաղտնաբառները չեն համընկնում")
        else:
            change_password(np1)
            st.success("Գաղտնաբառը փոխված է։")
    st.stop()

# ============================================================= CANDIDATE FLOW
if st.session_state.page == "home":
    st.markdown('<div class="main-title">Թեստ</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Գնահատե՛ք, թե որքան հաճույքով կանեիք յուրաքանչյուր գործունեությունը։ '
        'Թեստը լրացնելուց անտեսե՛ք ձեր հմտությունները, պատրաստվածությունն ու աշխատանքի վարձատրությունը։ '
        '<br>Գնահատե՛ք միայն ձեր իրական հետաքրքրվածությունը։</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.session_state.first_name = st.text_input("Անուն", value=st.session_state.first_name)
    st.session_state.last_name = st.text_input("Ազգանուն", value=st.session_state.last_name)
    st.session_state.position = st.text_input("Պաշտոն", value=st.session_state.position)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")
    if st.button("Սկսել", use_container_width=True):
        if st.session_state.first_name.strip() and st.session_state.last_name.strip() and st.session_state.position.strip():
            st.session_state.page = "test"
            st.session_state.q_index = 0
            st.session_state.start_time = time.time()
            st.session_state.finished = False
            st.session_state.tab_switches = 0
            st.session_state.last_evt = None
            st.rerun()
        else:
            st.error("Խնդրում ենք լրացնել բոլոր դաշտերը։")

elif st.session_state.page == "test":
    # live countdown — refreshes the page once per second
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=1000, key="timer_refresh")
    except ImportError:
        pass  # fallback: timer updates on any user interaction

    evt = anti_cheat_block()
    # count each event only once (component values persist across reruns,
    # so without this check the counter would inflate every second)
    if evt and evt != st.session_state.last_evt:
        st.session_state.last_evt = evt
        if str(evt).startswith("tab_switch") or str(evt).startswith("page_leave"):
            st.session_state.tab_switches += 1

    remaining = TEST_DURATION - (time.time() - st.session_state.start_time)
    if remaining <= 0 and not st.session_state.finished:
        st.session_state.finished = True
        submit_test()
        st.rerun()

    m, s = divmod(int(remaining), 60)
    st.markdown(f'<div class="timer">⏱ {m:02d}:{s:02d}</div>', unsafe_allow_html=True)
    if st.session_state.tab_switches > 0:
        st.markdown(f'<div class="warn">⚠️ Ֆիքսվել է էջի լքում կամ ներդիրի փոխարկում ({st.session_state.tab_switches} անգամ)</div>',
                    unsafe_allow_html=True)

    prog = (st.session_state.q_index + 1) / len(QUESTIONS)
    st.progress(prog, text=f"Հարց {st.session_state.q_index + 1} / {len(QUESTIONS)}")
    st.markdown("")

    q_text, _ = QUESTIONS[st.session_state.q_index]
    st.markdown(f'<div class="question-text">{q_text}</div>', unsafe_allow_html=True)

    prev = st.session_state.get(f"q{st.session_state.q_index}", None)
    st.radio("Ընտրեք մեկը", OPTIONS, index=prev, key=f"q{st.session_state.q_index}",
             label_visibility="collapsed")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.session_state.q_index > 0:
            if st.button("◀ Նախորդը"):
                st.session_state.q_index -= 1
                st.rerun()
    with col3:
        answered = st.session_state.get(f"q{st.session_state.q_index}", None) is not None
        if st.session_state.q_index < len(QUESTIONS) - 1:
            if st.button("Հաջորդը ▶", disabled=not answered):
                st.session_state.q_index += 1
                st.rerun()
        else:
            if st.button("✅ Ավարտել", disabled=not answered, type="primary"):
                st.session_state.finished = True
                submit_test()
                st.rerun()

elif st.session_state.page == "done":
    anti_cheat_cleanup()
    st.markdown('<div class="main-title">✅ Շնորհակալություն</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Ձեր պատասխանները պաշտպանված են և հասանելի են միայն '
        'մարդկային ռեսուրսների բաժնին։</div>',
        unsafe_allow_html=True)
    if st.button("🏠 Վերադառնալ գլխավոր էջ", use_container_width=True):
        for k in defaults:
            st.session_state[k] = defaults[k]
        for i in range(len(QUESTIONS)):
            st.session_state.pop(f"q{i}", None)
        st.rerun()