from datetime import datetime
import os
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Էջի կարգավորումներ
st.set_page_config(
    page_title="FYM Hospitality Group", page_icon="🏢", layout="centered"
)

# Գաղտնի հակախարդախություն (Առանց թեկնածուին ծանուցելու՝ արգելափակում ենք copy/paste-ը և նկատում էջից հեռանալը)
anti_cheat_code = """
<script>
document.addEventListener('copy', (e) => { e.preventDefault(); });
document.addEventListener('paste', (e) => { e.preventDefault(); });
document.addEventListener('cut', (e) => { e.preventDefault(); });
document.addEventListener('contextmenu', (e) => { e.preventDefault(); });

// Էջից դուրս գալու (visibility change) հայտնաբերում հանդիսավարի/HR-ի համար
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

# Ֆայլի ուղի տվյալների պահպանման համար (մինչև 5 տարի արխիվացման համար)
DATA_FILE = "riasec_results.csv"


def save_result(data):
  if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
  else:
    df = pd.DataFrame([data])
  df.to_csv(DATA_FILE, index=False)


# RIASEC Հարցաշար և տիպերի բնութագրեր (Ուժեղ և թույլ կողմեր)
RIASEC_QUESTIONS = [
    {
        "id": 1,
        "text": "Պատրաստել խոհանոցային պահարաններ։",
        "type": "R",
    },  # Realistic
    {
        "id": 2,
        "text": "Ուսումնասիրել ջրի աղտոտվածությունը նվազեցնելու եղանակները։",
        "type": "I",
    },  # Investigative
    {
        "id": 3,
        "text": "Գրել գրքեր, պատմվածքներ կամ պիեսներ։",
        "type": "A",
    },  # Artistic
    {"id": 4, "text": "Երեխաներին սովորեցնել կարդալ։", "type": "S"},  # Social
    {
        "id": 5,
        "text": "Հիմնել սեփական բիզնեսը։",
        "type": "E",
    },  # Enterprising
    {
        "id": 6,
        "text": (
            "Ստեղծել էլեկտրոնային աղյուսակ՝ տեղեկատվությունը կազմակերպելու"
            " համար։"
        ),
        "type": "C",
    },  # Conventional
    {
        "id": 7,
        "text": "Վերանորոգել կենցաղային տեխնիկան։",
        "type": "R",
    },
    {
        "id": 8,
        "text": "Մշակել նոր դեղամիջոց։",
        "type": "I",
    },
    {
        "id": 9,
        "text": "Նվագել երաժշտական գործիքով։",
        "type": "A",
    },
    {
        "id": 10,
        "text": (
            "Օգնել թմրանյութերի կամ ալկոհոլի օգտագործման հետ կապված խնդիրներ"
            " ունեցող մարդկանց։"
        ),
        "type": "S",
    },
    {
        "id": 11,
        "text": "Բանակցել գործարար պայմանագրերի շուրջ։",
        "type": "E",
    },
    {
        "id": 12,
        "text": (
            "Ստուգել փաստաթղթերն ու ձևաթղթերը՝ սխալները հայտնաբերելու"
            " համար։"
        ),
        "type": "C",
    },
    {
        "id": 13,
        "text": "Էլեկտրոնային դետալների պատրաստում։",
        "type": "R",
    },
    {
        "id": 14,
        "text": "Մանրադիտակով ուսումնասիրել արյան նմուշները։",
        "type": "I",
    },
    {
        "id": 15,
        "text": "Մշակել նկարազարդումներ ամսագրերի կամ կայքերի համար։",
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

# Session State-ի սկզբնական արժեքներ
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

# --- ՄՈՒՏՔԻ ԷՋ / ՎԵՐՆԱԳԻՐ ---
if st.session_state.page == "home":
  st.title("FYM Hospitality Group")
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
      if first_name and last_name and position:
        st.session_state.candidate_data = {
            "first_name": first_name,
            "last_name": last_name,
            "position": position,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.start_time = time.time()
        st.session_state.page = "test"
        st.rerun()
      else:
        st.error("Խնդրում ենք լրացնել բոլոր դաշտերը:")

  st.markdown("---")
  with st.expander("HR Մուտք (Միայն լիազորված անձանց համար)"):
    hr_pass = st.text_input("Մուտքագրեք HR գաղտնաբառը", type="password")
    if st.button("Մուտք գործել HR վահանակ"):
      # Անվտանգ գաղտնաբառ (կարող եք փոխել ըստ ցանկության)
      if hr_pass == "FYM_HR_2026":
        st.session_state.page = "hr_dashboard"
        st.rerun()
      else:
        st.error("Սխալ գաղտնաբառ:")

# --- ԹԵՍՏԻ ԷՋ (ԲԱԶՄԱՊԱՏԻԿ ԷՋԵՐՈՎ ԵՎ ԺԱՄԱՆԱԿԱՉԱՓՈՎ) ---
elif st.session_state.page == "test":
  # 5 րոպե ժամանակաչափ (300 վայրկյան)
  elapsed_time = time.time() - st.session_state.start_time
  time_left = 300 - elapsed_time

  if time_left <= 0:
    st.warning(
        "Ժամանակն սպառվել է: Ձեր պատասխանները ավտոմատ կերպով կամ կպահպանվեն"
        " կամ կարող եք ուղարկել:"
    )
    st.session_state.page = "finished"
    st.rerun()

  # Ժամանակացույցի վիզուալիզացիա
  mins, secs = divmod(int(time_left), 60)
  st.sidebar.markdown(f"### ⏱️ Մնացած ժամանակը: `{mins:02d}:{secs:02d}`")
  st.sidebar.markdown(
      f"**Թեկնածու:** {st.session_state.candidate_data.get('first_name')}"
      f" {st.session_state.candidate_data.get('last_name')}"
  )

  # Հարցերը տեղադրված են առանձին էջերով (մեկական կամ խմբերով)
  questions_per_page = 3
  total_questions = len(RIASEC_QUESTIONS)
  current_idx = st.session_state.current_q_index

  st.progress((current_idx + questions_per_page) / total_questions)
  st.subheader(
      f"Հարցեր {current_idx + 1} -ից"
      f" {min(current_idx + questions_per_page, total_questions)}"
  )

  batch_questions = RIASEC_QUESTIONS[
      current_idx : current_idx + questions_per_page
  ]

  with st.form("test_page_form"):
    page_answers = {}
    for q in batch_questions:
      st.markdown(f"**Հարց {q['id']}:** {q['text']}")
      ans = st.radio(
          "Ընտրեք ձեր վերաբերմունքը",
          options=list(SCALE_OPTIONS.keys()),
          key=f"q_{q['id']}",
          index=2,  # Լռելյայն՝ «Ո՛չ համաձայն եմ, ո՛չ համաձայն չեմ»
      )
      page_answers[q["id"]] = SCALE_OPTIONS[ans]
      st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
      prev_btn = st.form_submit_button("⬅️ Նախորդ")
    with col2:
      next_btn = st.form_submit_button("Հաջորդ ➡️")

    if next_btn:
      # Պահպանել ընթացիկ պատասխանները
      st.session_state.answers.update(page_answers)
      if current_idx + questions_per_page < total_questions:
        st.session_state.current_q_index += 1.5  # կամ պարզապես +3
        st.session_state.current_q_index = min(
            current_idx + questions_per_page, total_questions
        )
        st.rerun()
      else:
        # Ավարտ
        # Հաշվել արդյունքները և պահպանել
        scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
        for q in RIASEC_QUESTIONS:
          q_id = q["id"]
          q_type = q["type"]
          val = st.session_state.answers.get(q_id, 3)
          scores[q_type] += val

        # Դասավորել ըստ միավորների (բարձրից ցածր)
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
      st.session_state.current_q_index = max(
          0, current_idx - questions_per_page
      )
      st.rerun()

# --- ԱՎԱՐՏԻ ԵՋ (ԹԵԿՆԱԾՈՒԻ ՀԱՄԱՐ) ---
elif st.session_state.page == "finished":
  st.success("Շնորհակալություն թեստը հանձնելու համար:")
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

# --- HR / ADMIN ՎԱՀԱՆԱԿ ---
elif st.session_state.page == "hr_dashboard":
  st.title("🔐 HR Անձնակազմի Վահանակ (RIASEC Արդյունքներ)")
  st.markdown("---")

  if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
      st.subheader("Գրանցված թեկնածուների ցանկ")
      st.dataframe(df[["timestamp", "first_name", "last_name", "position", "top_result"]])

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