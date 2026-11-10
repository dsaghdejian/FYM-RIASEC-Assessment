from datetime import datetime
import os
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Էջի կարգավորումներ
st.set_page_config(
    page_title="FYM Hospitality Group - RIASEC Assessment",
    page_icon="🏢",
    layout="centered",
)

# Ոճավորում և գույներ (Սպիտակ ֆոն, սև տառատեսակ, բաց կանաչ կոճակներ)
st.markdown(
    """
    <style>
    /* Հիմնական ֆոն և տառեր */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: #000000 !important;
    }
    
    /* Բաց կանաչ կոճակներ */
    .stButton>button, .stFormSubmitButton>button {
        background-color: #E8F5E9 !important;
        color: #000000 !important;
        border: 1px solid #A5D6A7 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover {
        background-color: #C8E6C9 !important;
        border-color: #81C784 !important;
    }

    /* Radio կոճակների և մուտքագրման դաշտերի հստակեցում */
    .stRadio label {
        color: #000000 !important;
        font-size: 16px !important;
    }
    .stTextInput input {
        color: #000000 !important;
        background-color: #FAFAFA !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 6px !important;
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

document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.warn("User left the screen at: " + new Date().toISOString());
    }
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

# Տվյալների պահպանման ֆայլ
DATA_FILE = "riasec_results.csv"


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
        "text": (
            "Մշակել նկարազարդումներ ամսագրերի կամ կայքերի համար։"
        ),
        "type": "A",
    },
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

# Session State-ի սկզբնական կարգավորումներ
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

# --- ՄՈՒՏՔԻ ԷՋ (ԳԼԽԱՎՈՐ) ---
if st.session_state.page == "home":
  st.markdown(
      "<h1 style='text-align: center; color: #000000;'>FYM Hospitality"
      " Group</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<h3 style='text-align: center; color: #333333;'>Մասնագիտական"
      " Հետաքրքրությունների Թեստ</h3>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  st.write(
      "Խնդրում ենք լրացնել ձեր տվյալները թեստը սկսելու համար։"
      " Յուրաքանչյուր հարցի համար ընտրե՛ք ձեզ առավել համապատասխան"
      " տարբերակը։"
  )

  with st.form("candidate_form"):
    first_name = st.text_input("Անուն")
    last_name = st.text_input("Ազգանուն")
    position = st.text_input("Հավակնող պաշտոն")
    submit_btn = st.form_submit_button("Սկսել թեստը")

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
        st.error("Խնդրում ենք լրացնել բոլոր դաշտերը:")

  st.markdown("---")
  with st.expander("HR Մուտք (Միայն լիազորված անձանց համար)"):
    hr_pass = st.text_input("Մուտքագրեք HR գաղտնաբառը", type="password")
    if st.button("Մուտք գործել HR վահանակ"):
      if hr_pass == "1234":
        st.session_state.page = "hr_dashboard"
        st.rerun()
      else:
        st.error("Սխալ գաղտնաբառ:")

# --- ԹԵՍՏԻ ԷՋ (ՄԵԿԱԿԱՆ ՀԱՐՑ ՅՈՒՐԱՔԱՆՉՅՈՒՐ ԷՋՈՒՄ) ---
elif st.session_state.page == "test":
  st.markdown(
      "<h2 style='text-align: center; color: #000000;'>FYM Hospitality"
      " Group</h2>",
      unsafe_allow_html=True,
  )

  elapsed_time = time.time() - st.session_state.start_time
  time_left = 300 - elapsed_time  # 5 րոպե

  if time_left <= 0:
    st.warning("Ժամանակն սպառվել է:")
    st.session_state.page = "finished"
    st.rerun()

  mins, secs = divmod(int(time_left), 60)
  st.sidebar.markdown(f"### ⏱️ Մնացած ժամանակը: `{mins:02d}:{secs:02d}`")
  st.sidebar.markdown(
      f"**Թեկնածու:** {st.session_state.candidate_data.get('first_name')}"
      f" {st.session_state.candidate_data.get('last_name')}"
  )

  total_questions = len(RIASEC_QUESTIONS)
  current_idx = st.session_state.current_q_index

  st.progress((current_idx + 1) / total_questions)
  st.markdown(
      f"#### Հարց {current_idx + 1} / {total_questions}"
  )

  q = RIASEC_QUESTIONS[current_idx]

  with st.form(f"question_form_{current_idx}"):
    st.markdown(f"### {q['text']}")
    
    # Նախորդ պատասխանի վերականգնում (եթե արդեն պատասխանել է ու հետ է եկել)
    default_index = 2
    if q["id"] in st.session_state.answers:
      val = st.session_state.answers[q["id"]]
      # Գտնել արժեքին համապատասխան ինդեքսը
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
      prev_btn = (
          st.form_submit_button("⬅️ Նախորդ") if current_idx > 0 else None
      )
    with col2:
      next_btn = st.form_submit_button(
          "Հաջորդ ➡️" if current_idx < total_questions - 1 else "Ավարտել 🏁"
      )

    if next_btn:
      st.session_state.answers[q["id"]] = SCALE_OPTIONS[ans]
      if current_idx < total_questions - 1:
        st.session_state.current_q_index += 1
        st.rerun()
      else:
        # Հաշվել և պահպանել արդյունքները
        scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
        for question in RIASEC_QUESTIONS:
          q_id = question["id"]
          q_type = question["type"]
          val = st.session_state.answers.get(q_id, 3)
          scores[q_type] += val

        sorted_scores = sorted(
            scores.items(), key=lambda x: x[1], reverse=True
        )
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
      st.session_state.answers[q["id"]] = SCALE_OPTIONS[ans]
      st.session_state.current_q_index -= 1
      st.rerun()

# --- ԱՎԱՐՏԻ ԷՋ ---
elif st.session_state.page == "finished":
  st.markdown(
      "<h1 style='text-align: center; color: #000000;'>FYM Hospitality"
      " Group</h1>",
      unsafe_allow_html=True,
  )
  st.success("Շնորհակալություն թեստը հաջողությամբ հանձնելու համար:")
  st.info(
      "Ձեր պատասխանները գրանցվեցին: Արդյունքները հասանելի են միայն"
      " գործատուին։"
  )

  if st.button("Վերադառնալ գլխավոր էջ"):
    st.session_state.page = "home"
    st.session_state.answers = {}
    st.session_state.candidate_data = {}
    st.session_state.current_q_index = 0
    st.rerun()

# --- HR / ADMIN ՎԱՀԱՆԱԿ ---
elif st.session_state.page == "hr_dashboard":
  st.markdown(
      "<h1 style='text-align: center; color: #000000;'>FYM Hospitality"
      " Group</h1>",
      unsafe_allow_html=True,
  )
  st.subheader("🔐 HR Անձնակազմի Վահանակ (RIASEC Արդյունքներ)")
  st.markdown("---")

  if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
      st.subheader("Գրանցված թեկնածուների ցանկ")
      st.dataframe(
          df[["timestamp", "first_name", "last_name", "position", "top_result"]]
      )

      st.markdown("---")
      st.subheader("Թեկնածուի մանրամասն վերլուծություն")

      candidate_names = (
          df["first_name"] + " " + df["last_name"] + " (" + df["position"] + ")"
      ).tolist()
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
        st.markdown(
            "#### Համապատասխան տիպերի վերլուծություն (Ուժեղ և թույլ"
            " կողմեր):"
        )

        for char in top_res:
          if char in TRAIT_DESCRIPTIONS:
            trait_info = TRAIT_DESCRIPTIONS[char]
            with st.expander(f"Տիպ: {trait_info['name']} ({char})"):
              st.markdown(
                  f"**💪 Ուժեղ կողմեր:** {trait_info['strengths']}"
              )
              st.markdown(
                  f"**⚠️ Թույլ կողմեր / Ռիսկեր:** {trait_info['weaknesses']}"
              )
    else:
      st.info("Դեռևս գրանցված արդյունքներ չկան:")
  else:
    st.info("Տվյալների բազան դեռ դատարկ է:")

  st.markdown("---")
  if st.button("🚪 Դուրս գալ HR վահանակից"):
    st.session_state.page = "home"
    st.rerun()