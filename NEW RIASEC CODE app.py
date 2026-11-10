from datetime import datetime
import json
import os
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Էջի կարգավորումներ
st.set_page_config(
    page_title="FYM Hospitality Group", page_icon="🏢", layout="centered"
)

# Ոճավորում (CSS)՝ ավելի գեղեցիկ, կրեատիվ և մաքուր տեսքի համար
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #1f4e78;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #143353;
        color: white;
    }
    h1, h2, h3 {
        color: #1f4e78;
    }
    .timer-box {
        background-color: #eef2f7;
        padding: 10px 15px;
        border-radius: 8px;
        border-left: 5px solid #1f4e78;
        font-weight: bold;
        color: #1f4e78;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Գաղտնի հակախարդախություն (Առանց թեկնածուին ծանուցելու՝ արգելափակում ենք copy/paste-ը)
anti_cheat_code = """
<script>
document.addEventListener('copy', (e) => { e.preventDefault(); });
document.addEventListener('paste', (e) => { e.preventDefault(); });
document.addEventListener('cut', (e) => { e.preventDefault(); });
document.addEventListener('contextmenu', (e) => { e.preventDefault(); });
</script>
"""
components.html(anti_cheat_code, height=0, width=0)

DATA_FILE = "riasec_results.csv"
CONFIG_FILE = "hr_config.json"


def get_hr_password():
  if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
      return json.load(f).get("password", "FYM_HR_2026")
  else:
    default_pass = "FYM_HR_2026"
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
      json.dump({"password": default_pass}, f)
    return default_pass


def set_hr_password(new_pass):
  with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump({"password": new_pass}, f)


def save_result(data):
  if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
  else:
    df = pd.DataFrame([data])
  df.to_csv(DATA_FILE, index=False)


# RIASEC Հարցաշար
RIASEC_QUESTIONS = [
    {"id": 1, "text": "Պատրաստել խոհանոցային պահարաններ։", "type": "R"},
    {
        "id": 2,
        "text": "Ուսումնասիրել ջրի աղտոտվածությունը նվազեցնելու եղանակները։",
        "type": "I",
    },
    {"id": 3, "text": "Գրել գրքեր, պատմվածքներ կամ պիեսներ։", "type": "A"},
    {"id": 4, "text": "Երեխաներին սովորեցնել կարդալ։", "type": "S"},
    {"id": 5, "text": "Հիմնել սեփական բիզնեսը։", "type": "E"},
    {
        "id": 6,
        "text": (
            "Ստեղծել էլեկտրոնային աղյուսակ՝ տեղեկատվությունը կազմակերպելու"
            " համար։"
        ),
        "type": "C",
    },
    {"id": 7, "text": "Վերանորոգել կենցաղային տեխնիկան։", "type": "R"},
    {"id": 8, "text": "Մշակել նոր դեղամիջոց։", "type": "I"},
    {"id": 9, "text": "Նվագել երաժշտական գործիքով։", "type": "A"},
    {
        "id": 10,
        "text": (
            "Օգնել թմրանյութերի կամ ալկոհոլի օգտագործման հետ կապված խնդիրներ"
            " ունեցող մարդկանց։"
        ),
        "type": "S",
    },
    {"id": 11, "text": "Բանակցել գործարար պայմանագրերի շուրջ։", "type": "E"},
    {
        "id": 12,
        "text": (
            "Ստուգել փաստաթղթերն ու ձևաթղթերը՝ սխալները հայտնաբերելու"
            " համար։"
        ),
        "type": "C",
    },
    {"id": 13, "text": "Էլեկտրոնային դետալների պատրաստում։", "type": "R"},
    {"id": 14, "text": "Մանրադիտակով ուսումնասիրել արյան նմուշները։", "type": "I"},
    {
        "id": 15,
        "text": "Մշակել նկարազարդումներ ամսագրերի կամ կայքերի համար։",
        "type": "A",
    },
]

SCALE_OPTIONS = {
    "Ընտրեք պատասխանը...": 0,
    "Բոլորովին համաձայն չեմ": 1,
    "Համաձայն չեմ": 2,
    "Ո՛չ համաձայն եմ, ո՛չ համաձայն չեմ": 3,
    "Համաձայն եմ": 4,
    "Լիովին համաձայն եմ": 5,
}

TRAIT_DESCRIPTIONS = {
    "R": {
        "name": "Իրատեսական (Realistic)",
        "strengths": (
            "Գործնական են, հմուտ գործիքների և տեխնիկայի հետ աշխատելիս,"
            " նախընտրում են հստակ ու շոշափելի արդյունքներ:"
        ),
        "weaknesses": (
            "Կարող են դժվարությամբ շփվել կամ խուսափել վերացական վերլուծական"
            " խնդիրներից ու սոցիալական բարդ բանակցություններից:"
        ),
    },
    "I": {
        "name": "Հետազոտական (Investigative)",
        "strengths": (
            "Վերլուծական միտք, խորը մտածողություն, գիտական և տրամաբանական"
            " խնդիրների լուծման ունակություն:"
        ),
        "weaknesses": (
            "Հաճախ խուսափում են հապճեպ որոշումներից, կարող են պակաս"
            " գործնական լինել առօրյա վարչական հարցերում:"
        ),
    },
    "A": {
        "name": "Գեղարվեստական (Artistic)",
        "strengths": (
            "Ստեղծարարություն, ինքնատիպություն, երևակայություն,"
            " ճկունություն մոտեցումներում:"
        ),
        "weaknesses": (
            "Կարող են դժվարությամբ ենթարկվել խիստ կանոնակարգված և առօրյա"
            " միօրինակ կառուցվածքներին:"
        ),
    },
    "S": {
        "name": "Սոցիալական (Social)",
        "strengths": (
            "Բարձր էմպաթիա, հաղորդակցման գերազանց հմտություններ, ուսուցանելու"
            " և մարդկանց օգնելու ձգտում:"
        ),
        "weaknesses": (
            "Կարող են չափազանց զգայուն լինել կոնֆլիկտների նկատմամբ,"
            " դժվարությամբ կայացնել կոշտ վարչական որոշումներ:"
        ),
    },
    "E": {
        "name": "Ձեռներեց (Enterprising)",
        "strengths": (
            "Առաջնորդական հատկություններ, համոզելու կարողություն, ռիսկի դիմելու"
            " պատրաստակամություն և նպատակասլացություն:"
        ),
        "weaknesses": (
            "Կարող են անհբերեր լինել մանրամասն վերլուծությունների նկատմամբ և"
            " անտեսել փաստաթղթավորման կարևորությունը:"
        ),
    },
    "C": {
        "name": "Ավանդական (Conventional)",
        "strengths": (
            "Կարգապահություն, մանրազնին ուշադրություն դետալների նկատմամբ,"
            " տվյալների և փաստաթղթերի հետ աշխատելու հմտություն:"
        ),
        "weaknesses": (
            "Կարող են դժվարությամբ հարմարվել անսպասելի փոփոխություններին և"
            " նորարարական ոչ ստանդարտ մոտեցումներին:"
        ),
    },
}

# Session States
if "page" not in st.session_state:
  st.session_state.page = "home"
if "candidate_data" not in st.session_state:
  st.session_state.candidate_data = {}
if "answers" not in st.session_state:
  st.session_state.answers = {}
if "start_time" not in st.session_state:
  st.session_state.start_time = None

# --- 1. ԳԼԽԱՎՈՐ / ՄՈՒՏՔԻ ԷՋ ---
if st.session_state.page == "home":
  st.title("🏢 FYM Hospitality Group")
  st.markdown("---")
  st.subheader("Թեստ")

  st.write(
      "Գնահատե՛ք, թե որքան հաճույքով կանեիք յուրաքանչյուր գործունեությունը։"
      " Թեստը լրացնելուց անտեսե՛ք ձեր հմտությունները, պատրաստվածությունն ու"
      " աշխատանքի վարձատրությունը։ Գնահատե՛ք միայն ձեր իրական"
      " հետաքրքրվածությունը։"
  )

  with st.form("candidate_form"):
    first_name = st.text_input("Անուն")
    last_name = st.text_input("Ազգանուն")
    position = st.text_input("Հավակնող պաշտոն")
    submit_btn = st.form_submit_button("Սկսել թեստը")

    if submit_btn:
      if first_name.strip() and last_name.strip() and position.strip():
        st.session_state.candidate_data = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "position": position.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.start_time = time.time()
        st.session_state.answers = {}
        st.session_state.page = "test"
        st.rerun()
      else:
        st.error("Խնդրում ենք լրացնել բոլոր դաշտերը:")

  st.markdown("---")
  with st.expander("🔐 HR Մուտք (Անձնակազմի համար)"):
    hr_pass = st.text_input("Մուտքագրեք HR գաղտնաբառը", type="password")
    if st.button("Մուտք գործել վահանակ"):
      if hr_pass == get_hr_password():
        st.session_state.page = "hr_dashboard"
        st.rerun()
      else:
        st.error("Սխալ գաղտնաբառ:")

# --- 2. ԹԵՍՏԻ ԷՋ (ԲՈԼՈՐ ՀԱՐՑԵՐԸ ՄԵԿ ԷՋՈՒՄ՝ ԺԱՄԱՆԱԿԱՉԱՓՈՎ) ---
elif st.session_state.page == "test":
  # 5 րոպե ժամանակաչափ (300 վայրկյան)
  elapsed_time = time.time() - st.session_state.start_time
  time_left = max(0, 300 - int(elapsed_time))

  mins, secs = divmod(time_left, 60)
  st.markdown(
      f"<div class='timer-box'>⏱️ Մնացած ժամանակը: {mins:02d}:{secs:02d}</div>",
      unsafe_allow_html=True,
  )

  if time_left == 0:
    st.warning("Ժամանակն սպառվել է: Ձեր պատասխանները ավտոմատ կերպով կգրանցվեն:")
    # Ավտոմատ հաշվարկ ժամանակն սպառվելիս
    scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    for q in RIASEC_QUESTIONS:
      val = st.session_state.answers.get(q["id"], 3)
      scores[q["type"]] += val
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_types = "".join([item[0] for item in sorted_scores[:3]])

    final_record = {
        **st.session_state.candidate_data,
        "scores": str(scores),
        "top_result": top_types,
    }
    save_result(final_record)
    st.session_state.page = "finished"
    st.rerun()

  st.markdown("---")
  st.subheader("📝 Հարցաշար")

  with st.form("test_form"):
    page_answers = {}
    for q in RIASEC_QUESTIONS:
      st.markdown(f"**Հարց {q['id']}:** {q['text']}")
      # index=0 դարձնում է առաջին տարբերակը («Ընտրեք պատասխանը...»), ոչ մի կոճակ նախապես նշված չի լինում
      ans = st.selectbox(
          "Ընտրեք տարբերակը",
          options=list(SCALE_OPTIONS.keys()),
          key=f"q_{q['id']}",
          index=0,
      )
      page_answers[q["id"]] = SCALE_OPTIONS[ans]
      st.markdown("---")

    submit_test = st.form_submit_button("Ավարտել և ուղարկել թեստը")

    if submit_test:
      # Ստուգել՝ արդյոք բոլոր հարցերը պատասխանված են
      unanswered = [
          q["id"] for q in RIASEC_QUESTIONS if page_answers[q["id"]] == 0
      ]
      if unanswered:
        st.error(
            "⚠️ Խնդրում ենք պատասխանել բոլոր հարցերին նախքան ուղարկելը։"
            f" Անպատասխան հարցեր: {len(unanswered)}"
        )
      else:
        scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
        for q in RIASEC_QUESTIONS:
          scores[q["type"]] += page_answers[q["id"]]

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_types = "".join([item[0] for item in sorted_scores[:3]])

        final_record = {
            **st.session_state.candidate_data,
            "scores": str(scores),
            "top_result": top_types,
        }
        save_result(final_record)
        st.session_state.page = "finished"
        st.rerun()

  # Թարմացնել էջը ժամանակաչափի աշխատանքի համար
  time.sleep(1)
  st.rerun()

# --- 3. ԹԵԿՆԱԾՈՒԻ ԱՎԱՐՏԱԿԱՆ ԷՋ ---
elif st.session_state.page == "finished":
  st.success("✅ Շնորհակալություն թեստը հանձնելու համար:")
  st.info(
      "Ձեր պատասխանները հաջողությամբ գրանցվեցին: Գաղտնիության"
      " պահպանման կանոնների համաձայն՝ արդյունքները ցուցադրվում են միայն"
      " գործատուին։"
  )

  if st.button("Վերադառնալ գլխավոր էջ"):
    st.session_state.page = "home"
    st.session_state.answers = {}
    st.session_state.candidate_data = {}
    st.rerun()

# --- 4. HR ՎԱՀԱՆԱԿ ---
elif st.session_state.page == "hr_dashboard":
  st.title("🔐 HR Անձնակազմի Վահանակ")
  st.markdown("---")

  tab1, tab2, tab3 = st.tabs(
      [
          "📋 Թեկնածուների ցանկ",
          "📊 Մանրամասն վերլուծություն",
          "⚙️ Կարգավորումներ (Գաղտնաբառ)",
      ]
  )

  with tab1:
    st.subheader("Գրանցված թեկնածուների արդյունքներ")
    if os.path.exists(DATA_FILE):
      df = pd.read_csv(DATA_FILE)
      if not df.empty:
        st.dataframe(
            df[
                ["timestamp", "first_name", "last_name", "position", "top_result"]
            ],
            use_container_width=True,
        )
      else:
        st.info("Դեռևս գրանցված տվյալներ չկան:")
    else:
      st.info("Տվյալների բազան դատարկ է:")

  with tab2:
    st.subheader("Թեկնածուի ուժեղ և թույլ կողմեր")
    if os.path.exists(DATA_FILE):
      df = pd.read_csv(DATA_FILE)
      if not df.empty:
        candidate_names = (
            df["first_name"]
            + " "
            + df["last_name"]
            + " ("
            + df["position"]
            + ")"
        ).tolist()
        selected_cand = st.selectbox(
            "Ընտրեք թեկնածուին", candidate_names, key="cand_select"
        )

        if selected_cand:
          idx = candidate_names.index(selected_cand)
          row = df.iloc[idx]

          st.markdown(f"### 👤 {row['first_name']} {row['last_name']}")
          st.markdown(f"**Պաշտոն:** {row['position']}")
          st.markdown(f"**Ամսաթիվ:** {row['timestamp']}")
          top_res = row["top_result"]
          st.markdown(f"**Գլխավոր RIASEC Կոդ:** `{top_res}`")
          st.markdown("---")

          for char in top_res:
            if char in TRAIT_DESCRIPTIONS:
              trait = TRAIT_DESCRIPTIONS[char]
              with st.expander(
                  f"Տիպ: {trait['name']} ({char})", expanded=True
              ):
                st.markdown(f"💪 **Ուժեղ կողմեր:** {trait['strengths']}")
                st.markdown(f"⚠️ **Թույլ կողմեր / Ռիսկեր:** {trait['weaknesses']}")
      else:
        st.info("Դեռևս տվյալներ չկան:")
    else:
      st.info("Տվյալների բազան դատարկ է:")

  with tab3:
    st.subheader("HR Գաղտնաբառի փոփոխություն")
    current_pass_input = st.text_input(
        "Ընթացիկ գաղտնաբառ", type="password", key="curr_p"
    )
    new_pass_input = st.text_input("Նոր գաղտնաբառ", type="password", key="new_p")
    confirm_pass_input = st.text_input(
        "Հաստատեք նոր գաղտնաբառը", type="password", key="conf_p"
    )

    if st.button("Թարմացնել գաղտնաբառը"):
      if current_pass_input == get_hr_password():
        if new_pass_input and new_pass_input == confirm_pass_input:
          set_hr_password(new_pass_input)
          st.success("✅ Գաղտնաբառը հաջողությամբ փոխվեց:")
        else:
          st.error("❌ Նոր գաղտնաբառերը չեն համընկնում կամ դատարկ են:")
      else:
        st.error("❌ Ընթացիկ գաղտնաբառը սխալ է:")

  st.markdown("---")
  if st.button("🚪 Դուրս գալ HR վահանակից"):
    st.session_state.page = "home"
    st.rerun()