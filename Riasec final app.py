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

# Ներդաշնակ, մեղմ և պրոֆեսիոնալ դիզայն (Soft Professional Theme)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f9fc;
        color: #2b3e50;
    }
    .stButton>button {
        background-color: #2c5282;
        color: white;
        border-radius: 6px;
        padding: 0.6rem 1.4rem;
        border: none;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #1a365d;
        color: white;
    }
    h1, h2, h3 {
        color: #1a365d;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .timer-card {
        background-color: #edf2f7;
        border-left: 4px solid #2c5282;
        padding: 10px 15px;
        border-radius: 4px;
        font-weight: 600;
        color: #2c5282;
        margin-bottom: 20px;
    }
    .question-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Հակախարդախություն (copy/paste արգելափակում)
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
      return json.load(f).get("password", "1234")
  else:
    default_pass = "1234"  # Լռելյայն գաղտնաբառը 1234
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
    "1. Բոլորովին համաձայն չեմ": 1,
    "2. Համաձայն չեմ": 2,
    "3. Ո՛չ համաձայն եմ, ո՛չ համաձայն չեմ": 3,
    "4. Համաձայն եմ": 4,
    "5. Լիովին համաձայն եմ": 5,
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
            " խդիրներից ու սոցիալական բարդ բանակցություններից:"
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
if "current_q_index" not in st.session_state:
  st.session_state.current_q_index = 0

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
        st.session_state.current_q_index = 0
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

# --- 2. ԹԵՍՏԻ ԷՋ (ՅՈՒՐԱՔԱՆՉՅՈՒՐ ՀԱՐՑ ԱՌԱՆՁԻՆ ԷՋՈՒՄ՝ ԺԱՄԱՆԱԿԱՉԱՓՈՎ) ---
elif st.session_state.page == "test":
  elapsed_time = time.time() - st.session_state.start_time
  time_left = max(0, 300 - int(elapsed_time))  # 5 րոպե = 300 վայրկյան

  mins, secs = divmod(time_left, 60)
  st.markdown(
      f"<div class='timer-card'>⏱️ Մնացած ժամանակը: {mins:02d}:{secs:02d}</div>",
      unsafe_allow_html=True,
  )

  if time_left == 0:
    st.warning(
        "⏰ Ժամանակն սպառվել է: Ձեր պատասխանները ավտոմատ կերպով կգրանցվեն:"
    )
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

  total_q = len(RIASEC_QUESTIONS)
  curr_idx = st.session_state.current_q_index
  q = RIASEC_QUESTIONS[curr_idx]

  st.progress((curr_idx + 1) / total_q)
  st.markdown(f"**Հարց {curr_idx + 1} / {total_q}**")

  st.markdown(
      f"<div class='question-box'><h3>{q['text']}</h3></div>",
      unsafe_allow_html=True,
  )

  with st.form(f"question_form_{q['id']}"):
    # Ուղղահայաց տարբերակներ (horizontal=False)
    selected_option = st.radio(
        "Ընտրեք ձեր պատասխանը",
        options=list(SCALE_OPTIONS.keys()),
        index=None,
        horizontal=False,
    )

    col1, col2 = st.columns(2)
    with col1:
      prev_btn = st.form_submit_button("⬅️ Նախորդ")
    with col2:
      next_btn = (
          st.form_submit_button("Հաջորդ ➡️")
          if curr_idx < total_q - 1
          else st.form_submit_button("Ավարտել թեստը ✅")
      )

    if prev_btn or next_btn:
      if selected_option is None and not (
          prev_btn and curr_idx > 0
      ):  # Եթե պատասխան չի ընտրվել (բացառությամբ նախորդ էջ գնալու)
        st.error("⚠️ Խնդրում ենք ընտրել պատասխան նախքան շարունակելը։")
      else:
        if selected_option is not None:
          st.session_state.answers[q["id"]] = SCALE_OPTIONS[selected_option]

        if next_btn:
          if curr_idx < total_q - 1:
            st.session_state.current_q_index += 1
            st.rerun()
          else:
            # Վերջնական հաշվարկ և պահպանում
            scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
            for item in RIASEC_QUESTIONS:
              qid = item["id"]
              qtype = item["type"]
              val = st.session_state.answers.get(
                  qid, 3
              )  # լռելյայն չեզոք, եթե բաց է թողնվել
              scores[qtype] += val

            sorted_scores = sorted(
                scores.items(), key=lambda x: x[1], reverse=True
            )
            top_types = "".join([item[0] for item in sorted_scores[:3]])

            final_record = {
                **st.session_state.candidate_data,
                "scores": str(scores),
                "top_result": top_types,
            }
            save_result(final_record)
            st.session_state.page = "finished"
            st.rerun()

        if prev_btn:
          if curr_idx > 0:
            st.session_state.current_q_index -= 1
            st.rerun()

  # Ժամանակաչափի աշխատանքի համար էջի թարմացում
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
    st.session_state.current_q_index = 0
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