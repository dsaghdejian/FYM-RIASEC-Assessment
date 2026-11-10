from datetime import datetime
import os
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Էջի կարգավորումներ
st.set_page_config(
    page_title="FYM Hospitality Group - Պաշտոնական Թեստավորում",
    page_icon="🏢",
    layout="centered",
)

# Գաղտնի PIN/Password-ի սկզբնական կարգավորում (Session State)
if "hr_pin" not in st.session_state:
    st.session_state.hr_pin = "1234"

# UI/UX Ոճավորում՝ հիմնված նկարի դիզայնի վրա
st.markdown(
    """
    <style>
    /* Ֆոնի և ընդհանուր տեքստի ոճավորում */
    .stApp {
        background-color: #F8F9FA;
        color: #1E293B;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Տեքստերի հստակ ընթեռնելիություն */
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: #0F172A !important;
    }

    /* st.info / st.success բլոկների գույների ուղղում (որպեսզի տեքստը լինի մուգ ու հստակ երևացող) */
    .stAlert {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .stAlert p {
        color: #0F172A !important;
        font-size: 16px !important;
        font-weight: 500 !important;
    }

    /* Գլխավոր վերնագրի տարբերանշան (Badge) */
    .top-badge {
        text-align: center;
        margin-bottom: 5px;
    }
    .top-badge span {
        background-color: #E2E8F0;
        color: #475569 !important;
        font-size: 13px;
        font-weight: 600;
        padding: 4px 16px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Քարտերի (Cards) ոճավորում */
    .custom-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }

    /* Մուգ կապույտ / սև հիմնական կոճակներ (Dark Navy Button like in Image) */
    .stButton>button, .stFormSubmitButton>button {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 0.65rem 1.5rem !important;
        width: 100% !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
    }

    /* Մուտքագրման դաշտեր (Input Fields) */
    .stTextInput input {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 15px !important;
    }
    .stTextInput input:focus {
        border-color: #0F172A !important;
        box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.1) !important;
    }

    /* Radio buttons / Multiple choice options */
    .stRadio label {
        color: #0F172A !important;
        font-size: 16px !important;
        font-weight: 500 !important;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #0F172A !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Խիստ հակախարդախություն (Copy/Paste, Right click արգելափակում + էջից դուրս գալու alert)
anti_cheat_code = """
<script>
document.addEventListener('copy', (e) => { e.preventDefault(); });
document.addEventListener('paste', (e) => { e.preventDefault(); });
document.addEventListener('cut', (e) => { e.preventDefault(); });
document.addEventListener('contextmenu', (e) => { e.preventDefault(); });

window.addEventListener('blur', function() {
    alert("Զգուշացում․ Արգելված է դուրս գալ էջից կամ բացել այլ պատուհաններ թեստի ընթացքում։");
});
</script>
<style>
body {
    user-select: none !important;
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
}
</style>
"""
components.html(anti_cheat_code, height=0, width=0)

DATA_FILE = "riasec_results.csv"

def save_result(data):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])
    df.to_csv(DATA_FILE, index=False)

RIASEC_QUESTIONS = [
    {"id": 1, "text": "Պատրաստել խոհանոցային պահարաններ։", "type": "R"},
    {"id": 2, "text": "Ուսումնասիրել ջրի աղտոտվածությունը նվազեցնելու եղանակները։", "type": "I"},
    {"id": 3, "text": "Գրել գրքեր, պատմվածքներ կամ պիեսներ։", "type": "A"},
    {"id": 4, "text": "Երեխաներին սովորեցնել կարդալ։", "type": "S"},
    {"id": 5, "text": "Հիմնել սեփական բիզնեսը։", "type": "E"},
    {"id": 6, "text": "Ստեղծել էլեկտրոնային աղյուսակ՝ տեղեկատվությունը կազմակերպելու համար։", "type": "C"},
    {"id": 7, "text": "Վերանորոգել կենցաղային տեխնիկան։", "type": "R"},
    {"id": 8, "text": "Մշակել նոր դեղամիջոց։", "type": "I"},
    {"id": 9, "text": "Նվագել երաժշտական գործիքով։", "type": "A"},
    {"id": 10, "text": "Օգնել թմրանյութերի կամ ալկոհոլի օգտագործման հետ կապված խնդիրներ ունեցող մարդկանց։", "type": "S"},
    {"id": 11, "text": "Բանակցել գործարար պայմանագրերի շուրջ։", "type": "E"},
    {"id": 12, "text": "Ստուգել փաստաթղթերն ու ձևաթղթերը՝ սխալները հայտնաբերելու համար։", "type": "C"},
    {"id": 13, "text": "Էլեկտրոնային դետալների պատրաստում։", "type": "R"},
    {"id": 14, "text": "Մանրադիտակով ուսումնասիրել արյան նմուշները։", "type": "I"},
    {"id": 15, "text": "Մշակել նկարազարդումներ ամսագրերի կամ կայքերի համար։", "type": "A"},
]

SCALE_OPTIONS = {
    "Բոլորովին համաձայն չեմ": 1,
    "Համաձայն չեմ": 2,
    "Ո՛չ համաձայն եմ, ո՛չ համաձայն չեմ": 3,
    "Համաձայն եմ": 4,
    "Լիովին համաձայն եմ": 5,
}

TRAIT_DESCRIPTIONS = {
    "R": {
        "name": "Իրատեսական (Realistic)",
        "strengths": "Գործնական են, հմուտ գործիքների և տեխնիկայի հետ աշխատելիս, նախընտրում են հստակ ու շոշափելի արդյունքներ:",
        "weaknesses": "Կարող են դժվարությամբ շփվել կամ խուսափել վերացական վերլուծական խնդիրներից ու սոցիալական բարդ բանակցություններից:",
    },
    "I": {
        "name": "Հետազոտական (Investigative)",
        "strengths": "Վերլուծական միտք, խորը մտածողություն, գիտական և տրամաբանական խնդիրների լուծման ունակություն:",
        "weaknesses": "Հաճախ խուսափում են հապճեպ որոշումներից, կարող են պակաս գործնական լինել առօրյա վարչական հարցերում:",
    },
    "A": {
        "name": "Գեղարվեստական (Artistic)",
        "strengths": "Ստեղծարարություն, ինքնատիպություն, երևակայություն, ճկունություն մոտեցումներում:",
        "weaknesses": "Կարող են դժվարությամբ ենթարկվել խիստ կանոնակարգված և առօրյա միօրինակ կառուցվածքներին:",
    },
    "S": {
        "name": "Սոցիալական (Social)",
        "strengths": "Բարձր էմպաթիա, հաղորդակցման գերազանց հմտություններ, ուսուցանելու և մարդկանց օգնելու ձգտում:",
        "weaknesses": "Կարող են չափազանց զգայուն լինել կոնֆլիկտների նկատմամբ, դժվարությամբ կայացնել կոշտ վարչական որոշումներ:",
    },
    "E": {
        "name": "Ձեռներեց (Enterprising)",
        "strengths": "Առաջնորդական հատկություններ, համոզելու կարողություն, ռիսկի դիմելու պատրաստակամություն և նպատակասլացություն:",
        "weaknesses": "Կարող են անհբերեր լինել մանրամասն վերլուծությունների նկատմամբ և անտեսել փաստաթղթավորման կարևորությունը:",
    },
    "C": {
        "name": "Ավանդական (Conventional)",
        "strengths": "Կարգապահություն, մանրազնին ուշադրություն դետալների նկատմամբ, տվյալների և փաստաթղթերի հետ աշխատելու հմտություն:",
        "weaknesses": "Կարող են դժվարությամբ հարմարվել անսպասելի փոփոխություններին և նորարարական ոչ ստանդարտ մոտեցումներին:",
    },
}

if "page" not in st.session_state:
    st.session_state.page = "home"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0

# --- ԳԼԽԱՎՈՐ ՄՈՒՏՔԻ ԷՋ (Նկարի Դիզայնով) ---
if st.session_state.page == "home":
    st.markdown("<div class='top-badge'><span>ՊԱՇՏՈՆԱԿԱՆ ԹԵՍՏԱՎՈՐՈՒՄ</span></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; margin-bottom: 2px;'>FYM Hospitality Group</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-size: 28px; margin-top: 0; text-decoration: underline; text-decoration-color: #0F172A;'>ԹԵՍՏ</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Տեղեկատվական Բլոկ (Instruction Card)
    st.markdown(
        """
        <div class='custom-card'>
            <p style='font-size: 16px; line-height: 1.6; margin-bottom: 10px;'>
                <strong>ℹ️ Մտածեք այն իրավիճակների մասին, երբ ձեր հետաքրքրություններն ու նախասիրությունները տարբերվում են։</strong>
            </p>
            <p style='font-size: 15px; color: #475569 !important; margin: 0;'>
                Գնահատե՛ք, թե որքան հաճույքով կանեիք յուրաքանչյուր գործունեությունը։ Գնահատե՛ք միայն ձեր իրական հետաքրքրվածությունը։
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Թեկնածուի տվյալների մուտքագրման քարտ (Candidate Details Card)
    st.markdown("<h3 style='font-size: 20px; font-weight: 700;'>🪪 ԴԻՄՈՐԴԻ ՏՎՅԱԼՆԵՐԸ</h3>", unsafe_allow_html=True)
    
    with st.form("candidate_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("ԱՆՈՒՆ *", placeholder="Մուտքագրեք անունը")
        with col2:
            last_name = st.text_input("ԱԶԳԱՆՈՒՆ *", placeholder="Մուտքագրեք ազգանունը")
        
        position = st.text_input("ՀԱՅՑՎՈՂ ՊԱՇՏՈՆԸ *", placeholder="օր. Restaurant Manager, Receptionist, HR Assistant")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("Սկսել Թեստավորումը ➔")

        if submit_btn:
            if first_name and last_name and position:
                st.session_state.candidate_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "position": position,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                st.session_state.start_time = time.time()
                st.session_state.current_q_index = 0
                st.session_state.answers = {}
                st.session_state.page = "test"
                st.rerun()
            else:
                st.error("Խնդրում ենք լրացնել բոլոր պարտադիր դաշտերը (*):")

    st.markdown("---")
    with st.expander("🔐 HR / Admin Մուտք"):
        hr_pass = st.text_input("Մուտքագրեք HR PIN գաղտնաբառը", type="password")
        if st.button("Մուտք գործել HR վահանակ"):
            if hr_pass == st.session_state.hr_pin:
                st.session_state.page = "hr_dashboard"
                st.rerun()
            else:
                st.error("Սխալ PIN գաղտնաբառ:")

# --- ԹԵՍՏԻ ԷՋ ---
elif st.session_state.page == "test":
    st.markdown("<div class='top-badge'><span>FYM HOSPITALITY GROUP</span></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Պաշտոնական Թեստավորում</h2>", unsafe_allow_html=True)

    elapsed_time = time.time() - st.session_state.start_time
    time_left = 300 - elapsed_time

    if time_left <= 0:
        st.warning("Ժամանակն սպառվել է:")
        st.session_state.page = "finished"
        st.rerun()

    mins, secs = divmod(int(time_left), 60)
    st.sidebar.markdown(f"### ⏱️ Մնացած ժամանակը: `{mins:02d}:{secs:02d}`")
    st.sidebar.markdown(f"**Թեկնածու:** {st.session_state.candidate_data.get('first_name')} {st.session_state.candidate_data.get('last_name')}")

    total_questions = len(RIASEC_QUESTIONS)
    current_idx = st.session_state.current_q_index

    st.progress((current_idx + 1) / total_questions)
    st.markdown(f"#### Հարց {current_idx + 1} / {total_questions}")

    q = RIASEC_QUESTIONS[current_idx]

    with st.form(f"question_form_{current_idx}"):
        st.markdown(
            f"""
            <div class='custom-card'>
                <h3 style='font-size: 20px; color: #0F172A !important; margin: 0;'>{q['text']}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        default_index = None
        if q["id"] in st.session_state.answers:
            val = st.session_state.answers[q["id"]]
            keys_list = list(SCALE_OPTIONS.keys())
            for idx, k in enumerate(keys_list):
                if SCALE_OPTIONS[k] == val:
                    default_index = idx
                    break

        ans = st.radio(
            "Ընտրեք ձեր վերաբերմունքը․",
            options=list(SCALE_OPTIONS.keys()),
            index=default_index,
            key=f"radio_{q['id']}",
        )

        col1, col2 = st.columns(2)
        with col1:
            prev_btn = st.form_submit_button("⬅️ Նախորդ") if current_idx > 0 else None
        with col2:
            next_btn = st.form_submit_button("Հաջորդ ➡️" if current_idx < total_questions - 1 else "Ավարտել 🏁")

        if next_btn:
            if ans is None:
                st.error("Խնդրում ենք ընտրել պատասխան նախքան շարունակելը:")
            else:
                st.session_state.answers[q["id"]] = SCALE_OPTIONS[ans]
                if current_idx < total_questions - 1:
                    st.session_state.current_q_index += 1
                    st.rerun()
                else:
                    scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
                    for question in RIASEC_QUESTIONS:
                        q_id = question["id"]
                        q_type = question["type"]
                        val = st.session_state.answers.get(q_id, 3)
                        scores[q_type] += val

                    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                    top_types = "".join([item[0] for item in sorted_scores[:3]])

                    final_record = {
                        **st.session_state.candidate_data,
                        "scores": str(scores),
                        "top_result": top_types,
                        "details": str(sorted_scores),
                    }
                    save_result(final_record)
                    st.session_state.page = "finished"
                    st.rerun()

        if prev_btn and current_idx > 0:
            if ans is not None:
                st.session_state.answers[q["id"]] = SCALE_OPTIONS[ans]
            st.session_state.current_q_index -= 1
            st.rerun()

    time.sleep(1)
    st.rerun()

# --- ԱՎԱՐՏԻ ԷՋ ---
elif st.session_state.page == "finished":
    st.markdown("<h1 style='text-align: center;'>FYM Hospitality Group</h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class='custom-card' style='border-left: 5px solid #10B981;'>
            <h3 style='color: #0F172A !important; margin-top: 0;'>✅ Շնորհակալություն թեստը հաջողությամբ հանձնելու համար:</h3>
            <p style='font-size: 16px; color: #334155 !important; line-height: 1.6;'>
                Ձեր պատասխանները հաջողությամբ գրանցվեցին: Գաղտնիության պահպանման կանոնների համաձայն՝ արդյունքները հասանելի են միայն գործատուին։
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Վերադառնալ գլխավոր էջ"):
        st.session_state.page = "home"
        st.session_state.answers = {}
        st.session_state.candidate_data = {}
        st.session_state.current_q_index = 0
        st.rerun()

# --- HR / ADMIN ՎԱՀԱՆԱԿ ---
elif st.session_state.page == "hr_dashboard":
    st.markdown("<h1 style='text-align: center;'>FYM Hospitality Group</h1>", unsafe_allow_html=True)
    st.subheader("🔐 HR Անձնակազմի Վահանակ (RIASEC Արդյունքներ)")
    st.markdown("---")

    # PIN Փոխելու Հնարավորություն (Change PIN Feature)
    with st.expander("🔑 Փոխել HR PIN Գաղտնաբառը"):
        with st.form("change_pin_form"):
            current_p = st.text_input("Ընթացիկ PIN", type="password")
            new_p = st.text_input("Նոր PIN", type="password")
            confirm_p = st.text_input("Կրկնել Նոր PIN-ը", type="password")
            pin_submit = st.form_submit_button("Պահպանել Նոր PIN-ը")

            if pin_submit:
                if current_p == st.session_state.hr_pin:
                    if new_p and new_p == confirm_p:
                        st.session_state.hr_pin = new_p
                        st.success("HR PIN-ը հաջողությամբ փոխվեց:")
                    else:
                        st.error("Նոր PIN-երը չեն համապատասխանում:")
                else:
                    st.error("Ընթացիկ PIN-ը սխալ է:")

    st.markdown("<br>", unsafe_allow_html=True)

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            st.subheader("Գրանցված թեկնածուների ցանկ")
            st.dataframe(df[["timestamp", "first_name", "last_name", "position", "top_result"]], use_container_width=True)

            st.markdown("---")
            st.subheader("Թեկնածուի մանրամասն վերլուծություն")

            candidate_names = (df["first_name"] + " " + df["last_name"] + " (" + df["position"] + ")").tolist()
            selected_cand = st.selectbox("Ընտրեք թեկնածուին", candidate_names)

            if selected_cand:
                idx = candidate_names.index(selected_cand)
                row = df.iloc[idx]

                st.markdown(f"### 👤 {row['first_name']} {row['last_name']}")
                st.markdown(f"**Պաշտոն:** {row['position']}")
                st.markdown(f"**Ամսաթիվ:** {row['timestamp']}")
                top_res = row["top_result"]
                st.markdown(f"**Գլխավոր RIASEC կոդը:** `{top_res}`")

                st.markdown("---")
                st.markdown("#### Համապատասխան տիպերի վերլուծություն (Ուժեղ և թույլ կողմեր):")

                for char in top_res:
                    if char in TRAIT_DESCRIPTIONS:
                        trait_info = TRAIT_DESCRIPTIONS[char]
                        with st.expander(f"Տիպ: {trait_info['name']} ({char})"):
                            st.markdown(f"**💪 Ուժեղ կողմեր:** {trait_info['strengths']}")
                            st.markdown(f"**⚠️ Թույլ կողմեր / Ռիսկեր:** {trait_info['weaknesses']}")
        else:
            st.info("Դեռևս գրանցված արդյունքներ չկան:")
    else:
        st.info("Տվյալների բազան դեռ դատարկ է:")

    st.markdown("---")
    if st.button("🚪 Դուրս գալ HR վահանակից"):
        st.session_state.page = "home"
        st.rerun()