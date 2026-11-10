import streamlit as st
import time

# Page Configuration
st.set_page_config(
    page_title="Թեստ",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Styling & Anti-Cheat Measures (Disable Copy/Paste & Tab Switch Detection Warning)
st.markdown("""
    <style>
    /* Prevent text selection and copy/paste */
    body {
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
    }
    
    .main-title {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
        line-height: 1.5;
    }
    
    .card {
        background-color: #F9FAFB;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #E5E7EB;
    }
    
    .privacy-notice {
        font-size: 0.85rem;
        color: #6B7280;
        text-align: center;
        margin-top: 1.5rem;
    }
    </style>

    <script>
    // Tab switching detection warning
    document.addEventListener("visibilitychange", function() {
        if (document.hidden) {
            alert("Զգուշացում. Արգելված է դուրս գալ թեստի էջից կամ անցնել այլ ներդիրի (Tab):");
        }
    });

    // Block copy, cut, and paste actions
    document.addEventListener('copy', (e) => { e.preventDefault(); alert('Այս գործողությունն արգելված է։'); });
    document.addEventListener('paste', (e) => { e.preventDefault(); alert('Այս գործողությունն արգելված է։'); });
    document.addEventListener('cut', (e) => { e.preventDefault(); alert('Այս գործողությունն արգելված է։'); });
    </script>
""", unsafe_allow_html=True)

# Initialize Session State Variables
if "page" not in st.session_state:
    st.session_state.page = "home"
if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {"name": "", "surname": "", "position": ""}
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "submissions" not in st.session_state:
    st.session_state.submissions = []
if "hr_password" not in st.session_state:
    st.session_state.hr_password = "1234"
if "timer_start" not in st.session_state:
    st.session_state.timer_start = None

# Define Test Questions & Category Mapping (R, I, A, S, E, C)
QUESTIONS = [
    {"id": 1, "text": "Պատրաստել խոհանոցային պահարաններ։", "category": "R"},
    {"id": 2, "text": "Ուսումնասիրել ջրի աղտոտվածությունը նվազեցնելու եղանակները։", "category": "I"},
    {"id": 3, "text": "Գրել գրքեր, պատմվածքներ կամ պիեսներ։", "category": "A"},
    {"id": 4, "text": "Երեխաներին սովորեցնել կարդալ։", "category": "S"},
    {"id": 5, "text": "Հիմնել սեփական բիզնեսը։", "category": "E"},
    {"id": 6, "text": "Ստեղծել էլեկտրոնային աղյուսակ՝ տեղեկատվությունը կազմակերպելու համար։", "category": "C"},
    {"id": 7, "text": "Վերանորոգել կենցաղային տեխնիկան։", "category": "R"},
    {"id": 8, "text": "Մշակել նոր դեղամիջոց։", "category": "I"},
    {"id": 9, "text": "Նվագել երաժշտական գործիքով։", "category": "A"},
    {"id": 10, "text": "Օգնել թմրանյութերի կամ ալկոհոլի օգտագործման հետ կապված խնդիրներ ունեցող մարդկանց։", "category": "S"},
    {"id": 11, "text": "Բանակցել գործարար պայմանագրերի շուրջ։", "category": "E"},
    {"id": 12, "text": "Ստուգել փաստաթղթերն ու ձևաթղթերը՝ սխալները հայտնաբերելու համար։", "category": "C"},
    {"id": 13, "text": "Էլեկտրոնային դետալների պատրաստում։", "category": "R"},
    {"id": 14, "text": "Մանրադիտակով ուսումնասիրել արյան նմուշները։", "category": "I"},
    {"id": 15, "text": "Մշակել նկարազարդումներ ամսագրերի կամ կայքերի համար։", "category": "A"}
]

OPTIONS = {
    "Բոլորովին համաձայն չեմ": 1,
    "Համաձայն չեմ": 2,
    "Ո՛չ համաձայն եմ, ո՛չ համաձայն չեմ": 3,
    "Համաձայն եմ": 4,
    "Լիովին համաձայն եմ": 5
}

ARCHETYPE_DESCRIPTIONS = {
    "R": {
        "name": "Իրատեսական (Realistic)",
        "strengths": "Գործնական են, սիրում են աշխատել գործիքների, մեքենաների և նյութերի հետ, ուժեղ են ֆիզիկական և տեխնիկական խնդիրների լուծման մեջ:",
        "weaknesses": "Կարող են դժվարանալ վերացական տեսական վերլուծությունների կամ սոցիալական երկարատև բանակցությունների ժամանակ:"
    },
    "I": {
        "name": "Հետազոտական (Investigative)",
        "strengths": "Վերլուծական միտք, գիտական հետաքրքրասերություն, խորը հետազոտելու և բարդ օրինաչափություններ բացահայտելու կարողություն:",
        "weaknesses": "Հաճախ խուսափում են ղեկավարելուց, վաճառքից կամ արագ, ինտուիտիվ որոշումներ կայացնելուց առանց մանրամասն տվյալների:"
    },
    "A": {
        "name": "Գեղարվեստական (Artistic)",
        "strengths": "Ստեղծարարություն, ինքնատիպություն, երևակայություն, ճկունություն և նոր գաղափարներ գեներացնելու բարձր հակվածություն:",
        "weaknesses": "Կարող են դժվարությամբ ենթարկվել խիստ կանոնակարգված, առօրյա և միօրինակ վարչական աշխատանքներին:"
    },
    "S": {
        "name": "Սոցիալական (Social)",
        "strengths": "Հաղորդակցման բարձր հմտություններ, էպաթիա, ուրիշներին սովորեցնելու, առաջնորդելու և աջակցելու հակվածություն:",
        "weaknesses": "Կարող են հոգնկություն զգալ կամ խուսափել մեքենաների, թվերի կամ տեխնիկական սարքերի հետ միայնակ երկարատև աշխատանքից:"
    },
    "E": {
        "name": "Ձեռներեցային (Enterprising)",
        "strengths": "Առաջնորդություն, համոզելու կարողություն, ռիսկի դիմելու պատրաստակամություն, նպատակասլացություն և բիզնես մտածելակերպ:",
        "weaknesses": "Կարող են անհամբեր լինել մանրամասն հետազոտական կամ երկարատև փաստաթղթային աշխատանքների նկատմամբ:"
    },
    "C": {
        "name": "Ավանդական (Conventional)",
        "strengths": "Կազմակերպվածություն, ճշգրտություն, ուշադրություն մանրամասների նկատմամբ, կարգապահություն և տվյալների վարման հմտություն:",
        "weaknesses": "Կարող են խուսափել անորոշությունից, չպլանավորված փոփոխություններից և խիստ ստեղծարար ուղղություններից:"
    }
}

# --- PAGE: HOME / REGISTRATION ---
if st.session_state.page == "home":
    st.markdown('<div class="main-title">Թեստ</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Գնահատե՛ք, թե որքան հաճույքով կանեիք յուրաքանչյուր գործունեությունը։ '
        'Թեստը լրացնելուց անտեսե՛ք ձեր հմտությունները, պատրաստվածությունն ու աշխատանքի վարձատրությունը。<br>'
        'Գնահատե՛ք միայն ձեր իրական հետաքրքրվածությունը։</div>',
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Մուտքագրեք ձեր տվյալները")
        name = st.text_input("Անուն", value=st.session_state.candidate_info["name"])
        surname = st.text_input("Ազգանուն", value=st.session_state.candidate_info["surname"])
        position = st.text_input("Հավակնող պաշտոն", value=st.session_state.candidate_info["position"])

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Սկսել թեստը", type="primary", use_container_width=True):
                if name.strip() and surname.strip() and position.strip():
                    st.session_state.candidate_info = {"name": name, "surname": surname, "position": position}
                    st.session_state.answers = {}
                    st.session_state.current_q_index = 0
                    st.session_state.timer_start = time.time()
                    st.session_state.page = "test"
                    st.rerun()
                else:
                    st.error("Խնդրում ենք լրացնել բոլոր դաշտերը նախքան սկսելը։")
        with col2:
            if st.button("HR / Ադմինիստրացիա", use_container_width=True):
                st.session_state.page = "hr_login"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="privacy-notice">🔒 Ձեր պատասխանները լիովին պաշտպանված են, և դրանց հասանելիություն ունի միայն HR բաժինը։</div>',
        unsafe_allow_html=True
    )

# --- PAGE: TEST (Sequential Questions with Timer) ---
elif st.session_state.page == "test":
    # 5-minute (300 seconds) countdown timer logic
    elapsed_time = time.time() - st.session_state.timer_start
    remaining_time = max(0, 300 - int(elapsed_time))

    if remaining_time == 0:
        st.warning("Ժամանակը սպառվեց։ Ձեր պատասխանները ավտոմատ կերպով պահպանվեցին։")
        # Save current session
        st.session_state.submissions.append({
            "info": st.session_state.candidate_info,
            "answers": st.session_state.answers,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        st.session_state.page = "thank_you"
        st.rerun()

    # Timer display formatting
    mins, secs = divmod(remaining_time, 60)
    st.markdown(f"**Մնացած ժամանակը՝ ⏱️ {mins:02d}:{secs:02d}**")

    # Progress bar
    total_q = len(QUESTIONS)
    current_idx = st.session_state.current_q_index
    st.progress((current_idx) / total_q)

    q = QUESTIONS[current_idx]
    st.markdown(f"### Հարց {current_idx + 1} / {total_q}")
    st.markdown(f"#### {q['text']}")

    # Radio options for selection
    selected_option = st.radio(
        "Ընտրեք ձեր պատասխանը.",
        list(OPTIONS.keys()),
        key=f"q_{q['id']}",
        index=list(OPTIONS.keys()).index(
            [k for k, v in OPTIONS.items() if v == st.session_state.answers.get(q['id'])]
        ) if q['id'] in st.session_state.answers else 0
    )

    st.session_state.answers[q['id']] = OPTIONS[selected_option]

    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if current_idx > 0:
            if st.button("⬅️ Նախորդ", use_container_width=True):
                st.session_state.current_q_index -= 1
                st.rerun()
    with col2:
        if current_idx < total_q - 1:
            if st.button("Հաջորդ ➡️", type="primary", use_container_width=True):
                st.session_state.current_q_index += 1
                st.rerun()
        else:
            if st.button("Ավարտել և հանձնել 🎯", type="primary", use_container_width=True):
                st.session_state.submissions.append({
                    "info": st.session_state.candidate_info,
                    "answers": st.session_state.answers,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                st.session_state.page = "thank_you"
                st.rerun()

    time.sleep(1)
    st.rerun()

# --- PAGE: THANK YOU ---
elif st.session_state.page == "thank_you":
    st.markdown('<div class="main-title">Շնորհակալություն</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Ձեր պատասխանները հաջողությամբ պահպանվեցին և ուղարկվեցին HR բաժին։<br>'
        'Այժմ դուք կարող եք փակել էջը կամ վերադառնալ գլխավոր էջ։</div>',
        unsafe_allow_html=True
    )
    if st.button("Վերադառնալ գլխավոր էջ", type="primary", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.candidate_info = {"name": "", "surname": "", "position": ""}
        st.session_state.answers = {}
        st.session_state.current_q_index = 0
        st.rerun()

# --- PAGE: HR LOGIN ---
elif st.session_state.page == "hr_login":
    st.markdown('<div class="main-title">HR Մուտք</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    pwd_input = st.text_input("Մուտքագրեք գաղտնաբառը", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Մուտք գործել", type="primary", use_container_width=True):
            if pwd_input == st.session_state.hr_password:
                st.session_state.page = "hr_dashboard"
                st.rerun()
            else:
                st.error("Սխալ գաղտնաբառ:")
    with col2:
        if st.button("Հետ", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: HR DASHBOARD ---
elif st.session_state.page == "hr_dashboard":
    st.markdown("## 📊 HR Կառավարման Վահանակ - Թեստի Արդյունքներ")

    # Settings tab to change password
    with st.expander("⚙️ Փոխել HR գաղտնաբառը"):
        new_pwd = st.text_input("Նոր գաղտնաբառ", type="password")
        if st.button("Թարմացնել գաղտնաբառը"):
            if new_pwd.strip():
                st.session_state.hr_password = new_pwd
                st.success("Գաղտնաբառը հաջողությամբ փոխվեց։")
            else:
                st.error("Գաղտնաբառը չի կարող դատարկ լինել։")

    if not st.session_state.submissions:
        st.info("Դեռևս չկան լրացված թեստեր։")
    else:
        st.subheader("Թեկնածուների ցանկ")
        for idx, sub in enumerate(st.session_state.submissions):
            info = sub["info"]
            ans = sub["answers"]
            
            # Calculate scores per category
            cat_scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
            for q in QUESTIONS:
                if q["id"] in ans:
                    cat_scores[q["category"]] += ans[q["id"]]

            # Determine top archetype order
            sorted_cats = sorted(cat_scores.items(), key=lambda x: x[1], reverse=True)
            archetype_code = "".join([c[0] for c in sorted_cats[:3]])

            with st.expander(f"👤 {info['surname']} {info['name']} — {info['position']} (Կոդ՝ {archetype_code})"):
                st.write(f"**Ամսաթիվ/Ժամ՝** {sub['timestamp']}")
                st.write(f"**Անհատական միավորներ ըստ բնագավառների՝** {cat_scores}")
                st.write(f"**Հաշվարկված հիմնական արխետիպային կոդը՝** `{archetype_code}`")

                st.markdown("---")
                st.markdown("### Արխետիպային Վերլուծություն և Հատկանիշներ")
                for cat_key, score in sorted_cats:
                    details = ARCHETYPE_DESCRIPTIONS[cat_key]
                    st.markdown(f"**{details['name']} (Միավոր՝ {score}):**")
                    st.markdown(f"- **Ուժեղ կողմեր:** {details['strengths']}")
                    st.markdown(f"- **Թույլ կողմեր / Ռիսկեր:** {details['weaknesses']}")
                    st.markdown("")

    if st.button("Դուրս գալ HR վահանակից", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()