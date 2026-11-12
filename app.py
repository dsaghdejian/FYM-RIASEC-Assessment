from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh


# ---------------------------------------------------------------------
# FYM candidate assessment | Streamlit app
# ---------------------------------------------------------------------
FYM_LOGO_PNG = "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"

APP_TITLE = "FYM Hospitality Group"
DB_PATH = Path(os.getenv("FYM_DB_PATH", "fym_assessments.db"))
TEST_SECONDS = 5 * 60
RETENTION_YEARS = 5

st.set_page_config(
    page_title="Թեստ | FYM Hospitality Group",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Monochrome styling. Keep controls white; use black only for text, borders and selected radio dots.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Armenian:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans Armenian', sans-serif; }
    .stApp { background: #FFFFFF !important; color: #000000 !important; }
    [data-testid="stHeader"] { background: #FFFFFF !important; }
    .block-container { max-width: 850px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3, p, label, .stMarkdown, .stCaption, [data-testid="stMarkdownContainer"] { color: #000000 !important; }
    .fym-logo-wrap {
        display: flex !important; justify-content: center !important;
        align-items: center !important; width: 100% !important;
        max-width: 100% !important; height: auto !important;
        max-height: none !important; margin: 1.5rem auto 1.5rem auto !important;
        padding: 1rem 0.5rem !important; box-sizing: border-box !important;
        overflow: visible !important; line-height: normal !important;
    }
    .fym-logo-wrap img {
        display: block !important; width: 55% !important;
        max-width: 380px !important; min-width: 180px !important;
        height: auto !important; min-height: 0 !important;
        max-height: none !important; aspect-ratio: auto !important;
        object-fit: contain !important; object-position: center center !important;
        overflow: visible !important; flex: 0 1 auto !important;
    }
    [data-testid="stMarkdownContainer"] .fym-logo-wrap {
        overflow: visible !important; height: auto !important;
    }
    .hero-subtitle {
        text-align: center;
        margin: 0.5rem auto 1.5rem auto;
    }
    .hero-subtitle h2 {
        font-size: 1.6rem;
        font-weight: 600;
        color: #000000 !important;
        margin: 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E0E0E0;
        display: inline-block;
    }
    .question-card {
        background: #FFFFFF; border: 1px solid #000000; border-radius: 16px;
        padding: 1.5rem; margin: .8rem 0 1rem 0; box-shadow: none;
    }
    .muted, .small-note { color: #333333 !important; }
    .timer {
        background: #FFFFFF; border: 1px solid #000000; color: #000000;
        padding: .65rem 1rem; border-radius: 12px; font-weight: 700;
        text-align: center; font-size: 1.05rem;
    }
    div.stButton > button, div.stFormSubmitButton > button,
    div[data-testid="stDownloadButton"] > button {
        border-radius: 10px; min-height: 2.8rem; font-weight: 600;
        border: 1px solid #000000 !important;
        color: #000000 !important; background: #FFFFFF !important;
        box-shadow: none !important;
    }
    div.stButton > button:hover, div.stButton > button:active,
    div.stButton > button:focus, div.stFormSubmitButton > button:hover,
    div.stFormSubmitButton > button:active, div.stFormSubmitButton > button:focus,
    div[data-testid="stDownloadButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:active,
    div[data-testid="stDownloadButton"] > button:focus {
        color: #000000 !important; background: #FFFFFF !important;
        border-color: #000000 !important; box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div,
    div[data-testid="stTextArea"] textarea {
        background: #FFFFFF !important; color: #000000 !important;
        border-color: #000000 !important;
    }
    div[role="radiogroup"] label { color: #000000 !important; }
    input[type="radio"] { accent-color: #000000 !important; }
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
        background: #FFFFFF !important; border-color: #000000 !important;
    }
    [data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #000000; }
    [data-testid="stSidebar"] * { color: #000000 !important; }
    .success-panel {
        background: #FFFFFF; border: 1px solid #000000; border-radius: 16px;
        padding: 1.5rem; color: #000000; text-align: center;
    }
    .small-note { font-size: .86rem; }
    [data-testid="stAlert"] { background: #FFFFFF !important; color: #000000 !important; border: 1px solid #000000 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

OPTIONS = [
    "Բոլորովին համաձայն չեմ",
    "Համաձայն չեմ",
    "Ո՛չ համաձայն եմ, ո՛չ համաձայն չեմ",
    "Համաձայն եմ",
    "Լիովին համաձայն եմ",
]

# The order below follows the exact activity order supplied.
# Category letters are used internally only and are never shown to candidates.
QUESTIONS: List[Tuple[str, str]] = [
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

DIMENSIONS = {
    "R": "Գործնական (Realistic)",
    "I": "Հետազոտական (Investigative)",
    "A": "Ստեղծագործական (Artistic)",
    "S": "Սոցիալական (Social)",
    "E": "Ձեռնարկատիրական (Enterprising)",
    "C": "Կազմակերպչական (Conventional)",
}

INTERPRETATIONS = {
    "R": {
        "strengths": ["Գործնական խնդիրների լուծում", "Գործողությունների և շոշափելի արդյունքների նկատմամբ կողմնորոշում", "Գործիքների, սարքավորումների կամ նյութերի հետ աշխատելու հետաքրքրվածություն"],
        "risks": ["Կարող է քիչ հետաքրքրվել բացառապես տեսական առաջադրանքներով", "Կարող է նախընտրել հստակ գործողություններն ու չափելի արդյունքները"],
        "environment": "Գործնական, հստակ առաջադրանքներով և տեսանելի արդյունքներով աշխատանքային միջավայր։",
        "interview": ["Պատմե՛ք մի դեպքի մասին, երբ գործնական խնդիր եք լուծել։", "Ինչպե՞ս եք մոտենում նոր սարքավորման կամ աշխատանքային գործիքի սովորելուն։"],
    },
    "I": {
        "strengths": ["Տեղեկատվության ուսումնասիրություն և վերլուծություն", "Պատճառահետևանքային կապերի բացահայտում", "Բարդ հարցերի շուրջ կենտրոնացած աշխատանք"],
        "risks": ["Կարող է երկար ուսումնասիրել նախքան որոշում կայացնելը", "Կարող է նվազ հետաքրքրված լինել առանց վերլուծական բաղադրիչի կրկնվող աշխատանքով"],
        "environment": "Տեղեկատվության վերլուծության, ուսումնասիրման և խնդիրների խորքային հասկացման հնարավորություններով միջավայր։",
        "interview": ["Նկարագրե՛ք, թե ինչպես եք ուսումնասիրել և լուծել բարդ խնդիր։", "Ի՞նչ տվյալներ եք կարևորում որոշում կայացնելիս։"],
    },
    "A": {
        "strengths": ["Նոր գաղափարների և մոտեցումների ստեղծում", "Ինքնուրույն արտահայտվելու և ստեղծագործելու հետաքրքրություն", "Բաց խնդիրների այլընտրանքային լուծումների դիտարկում"],
        "risks": ["Կարող է դժվարանալ չափազանց խիստ կանոններով միջավայրում", "Կարող է նախընտրել ճկունություն՝ հստակ սահմանված ընթացակարգերից"],
        "environment": "Ստեղծագործական ազատություն, նոր գաղափարներ և տարբերակներ փորձարկելու հնարավորություն ունեցող միջավայր։",
        "interview": ["Պատմե՛ք ձեր առաջարկած նոր գաղափարի կամ ստեղծագործական լուծման մասին։", "Ինչպե՞ս եք աշխատում, երբ առաջադրանքի համար մեկ հստակ լուծում չկա։"],
    },
    "S": {
        "strengths": ["Մարդկանց աջակցելու և սովորեցնելու հետաքրքրվածություն", "Համագործակցության և հաղորդակցության նկատմամբ դրական վերաբերմունք", "Մարդկանց կարիքները հասկանալու ձգտում"],
        "risks": ["Կարող է չափազանց մեծ պատասխանատվություն վերցնել ուրիշների խնդիրների համար", "Կարող է պակաս հետաքրքրվել մարդկանց հետ շփում չպահանջող մեկուսացված աշխատանքով"],
        "environment": "Համագործակցային միջավայր՝ մարդկանց հետ շփման, աջակցության և գիտելիքի փոխանցման հնարավորություններով։",
        "interview": ["Նկարագրե՛ք մի իրավիճակ, երբ աջակցել եք գործընկերոջը կամ հաճախորդին։", "Ինչպե՞ս եք արձագանքում տարբեր կարիքներ ու սպասումներ ունեցող մարդկանց։"],
    },
    "E": {
        "strengths": ["Նախաձեռնողականություն և նպատակների առաջմղում", "Համոզելու, բանակցելու և ազդեցություն գործադրելու հետաքրքրություն", "Արդյունքների և հնարավորությունների նկատմամբ կողմնորոշում"],
        "risks": ["Կարող է շտապել գործել՝ նախքան բոլոր մանրամասները դիտարկելը", "Կարող է կորցնել հետաքրքրությունը դանդաղ առաջընթաց ունեցող գործընթացներում"],
        "environment": "Նպատակային միջավայր՝ նախաձեռնություն ցուցաբերելու, որոշումներ կայացնելու և արդյունքի վրա ազդեցություն ունենալու հնարավորությամբ։",
        "interview": ["Պատմե՛ք մի դեպքի մասին, երբ նախաձեռնություն եք ցուցաբերել և հասել նպատակի։", "Ինչպե՞ս եք պատրաստվում բանակցության կամ համոզիչ ներկայացման։"],
    },
    "C": {
        "strengths": ["Կարգուկանոնի և ճշգրտության նկատմամբ ուշադրություն", "Տվյալների, փաստաթղթերի և ընթացակարգերի համակարգում", "Հետևողական և կառուցվածքային աշխատանքի նախընտրություն"],
        "risks": ["Կարող է անհարմար զգալ հաճախակի փոփոխվող կամ չկառուցակարգված միջավայրում", "Կարող է մեծ ուշադրություն դարձնել մանրամասներին՝ երբեմն դանդաղեցնելով ընթացքը"],
        "environment": "Կառուցվածքային միջավայր՝ հստակ ընթացակարգերով, չափանիշներով և կազմակերպված տեղեկատվությամբ։",
        "interview": ["Ինչպե՞ս եք ապահովում փաստաթղթերի կամ տվյալների ճշգրտությունը։", "Պատմե՛ք, թե ինչպես եք կազմակերպել միաժամանակ մի քանի առաջադրանք։"],
    },
}

CODE_COMBINATIONS = {
    "RS": "Գործնական աշխատանքը կարող է առավել հետաքրքիր լինել, երբ այն ներառում է նաև մարդկանց աջակցություն և համագործակցություն։",
    "RI": "Հետաքրքրությունների համադրությունը կարող է միավորել գործնական իրականացումն ու պատճառների ուսումնասիրությունը։",
    "RA": "Կարող է նախընտրել ստեղծագործական մոտեցում ունեցող գործնական առաջադրանքներ։",
    "RE": "Գործնական նախաձեռնությունները և տեսանելի արդյունքի հասնելը կարող են մոտիվացնել։",
    "RC": "Կարող է գնահատել գործնական առաջադրանքների հստակ կազմակերպումն ու ճշգրիտ իրականացումը։",
    "IS": "Վերլուծական հետաքրքրությունը կարող է զուգակցվել գիտելիքը մարդկանց փոխանցելու և աջակցելու ցանկության հետ։",
    "IA": "Կարող է հետաքրքրվել հետազոտությամբ, գաղափարներով և ստեղծագործական արտահայտմամբ։",
    "IE": "Կարող է նախընտրել տվյալների ու գաղափարների հիման վրա հնարավորություններ բացահայտել և առաջ մղել։",
    "IC": "Կարող է համադրել վերլուծական մտածողությունն ու համակարգված տեղեկատվական աշխատանքը։",
    "SA": "Մարդկանց հետ աշխատանքը կարող է առավել գրավիչ լինել ստեղծագործական և արտահայտչական տարրերի առկայությամբ։",
    "SE": "Կարող է հետաքրքրվել մարդկանց հետ համագործակցելով, համոզելով և ընդհանուր նպատակներ առաջ մղելով։",
    "SC": "Կարող է նախընտրել մարդկանց աջակցող աշխատանք՝ հստակ կազմակերպված գործընթացներով։",
    "AE": "Կարող է համադրել նոր գաղափարների ստեղծումն ու դրանք ներկայացնելու կամ առաջ մղելու հետաքրքրությունը։",
    "AC": "Կարող է գնահատել ստեղծագործական աշխատանքը, երբ այն ունի կազմակերպված ընթացք և հստակ պահանջներ։",
    "EC": "Կարող է համադրել նպատակների առաջմղումն ու գործընթացների կազմակերպումը։",
}

def db_connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 260_000)
    return salt.hex() + ":" + digest.hex()

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 260_000
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def init_db():
    with db_connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                position TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                timed_out INTEGER NOT NULL DEFAULT 0,
                answers_json TEXT NOT NULL,
                scores_json TEXT NOT NULL,
                top_code TEXT NOT NULL,
                tab_switches INTEGER NOT NULL DEFAULT 0,
                total_away_seconds REAL NOT NULL DEFAULT 0,
                longest_away_seconds REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        row = conn.execute("SELECT value FROM settings WHERE key='admin_password_hash'").fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO settings(key,value) VALUES(?,?)",
                ("admin_password_hash", hash_password("1234")),
            )
        # Add detailed browser visibility-event history to existing databases safely.
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(candidates)").fetchall()}
        if "tab_events_json" not in columns:
            conn.execute("ALTER TABLE candidates ADD COLUMN tab_events_json TEXT NOT NULL DEFAULT '[]'")
        # Retain only the latest five years of records.
        cutoff = (datetime.now(timezone.utc) - timedelta(days=365 * RETENTION_YEARS)).isoformat()
        conn.execute("DELETE FROM candidates WHERE created_at < ?", (cutoff,))

def get_admin_hash() -> str:
    with db_connect() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key='admin_password_hash'").fetchone()
        return row["value"]

def set_admin_password(new_password: str):
    with db_connect() as conn:
        conn.execute(
            "UPDATE settings SET value=? WHERE key='admin_password_hash'",
            (hash_password(new_password),),
        )

def calculate_scores(answers: Dict[int, int]) -> Dict[str, float]:
    grouped: Dict[str, List[int]] = {letter: [] for letter in DIMENSIONS}
    for idx, (_, letter) in enumerate(QUESTIONS):
        if idx in answers:
            grouped[letter].append(int(answers[idx]))
    # Average by dimension, avoiding an artificial advantage for categories
    # that happen to have more questions in this supplied 15-item set.
    return {
        letter: round(sum(values) / len(values), 2) if values else 0.0
        for letter, values in grouped.items()
    }

def get_top_code(scores: Dict[str, float]) -> str:
    order = sorted(DIMENSIONS.keys(), key=lambda x: (-scores.get(x, 0), x))
    return "".join(order[:3])

def get_interpretation(code: str) -> dict:
    primary, secondary, tertiary = code[0], code[1], code[2]
    p = INTERPRETATIONS[primary]
    s = INTERPRETATIONS[secondary]
    t = INTERPRETATIONS[tertiary]
    combo = CODE_COMBINATIONS.get(primary + secondary, "")
    return {
        "summary": combo,
        "strengths": p["strengths"][:2] + s["strengths"][:1] + t["strengths"][:1],
        "risks": p["risks"][:1] + s["risks"][:1] + t["risks"][:1],
        "environment": p["environment"] + " " + s["environment"],
        "interview": p["interview"] + s["interview"][:1] + t["interview"][:1],
    }

def save_candidate():
    answers = st.session_state.answers
    scores = calculate_scores(answers)
    top_code = get_top_code(scores)
    now = datetime.now(timezone.utc)
    started = st.session_state.started_at
    duration = max(0, int((now - started).total_seconds()))
    with db_connect() as conn:
        conn.execute(
            """INSERT INTO candidates
            (first_name,last_name,position,started_at,completed_at,duration_seconds,
             timed_out,answers_json,scores_json,top_code,tab_switches,total_away_seconds,
             longest_away_seconds,created_at,tab_events_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                st.session_state.first_name.strip(),
                st.session_state.last_name.strip(),
                st.session_state.position.strip(),
                started.isoformat(),
                now.isoformat(),
                duration,
                int(st.session_state.timed_out),
                json.dumps({str(k): v for k, v in answers.items()}, ensure_ascii=False),
                json.dumps(scores, ensure_ascii=False),
                top_code,
                int(st.session_state.get("tab_switches", 0)),
                float(st.session_state.get("total_away", 0.0)),
                float(st.session_state.get("longest_away", 0.0)),
                now.isoformat(),
                json.dumps(st.session_state.get("tab_events", []), ensure_ascii=False),
            ),
        )

def reset_candidate():
    keys = [
        "page", "first_name", "last_name", "position", "answers",
        "started_at", "timed_out", "candidate_submitted", "question_index",
        "tab_switches", "total_away", "longest_away", "away_started", "tab_events", "last_visibility_event_id",
    ]
    for key in keys:
        st.session_state.pop(key, None)
    st.session_state.page = "home"
    st.rerun()

def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"

@st.cache_resource
def get_visibility_component():
    """Create a tiny local Streamlit component that sends tab visibility events to Python."""
    component_dir = Path(tempfile.mkdtemp(prefix="fym_visibility_component_"))
    component_html = r"""
    <!doctype html><html><head><meta charset="utf-8"></head><body>
    <script>
    (() => {
      let sequence = 0;
      const send = (state) => {
        sequence += 1;
        const value = {
          id: String(Date.now()) + "-" + String(sequence),
          state: state,
          timestamp: new Date().toISOString()
        };
        window.parent.postMessage({
          isStreamlitMessage: true,
          type: "streamlit:setComponentValue",
          value: value
        }, "*");
      };
      window.parent.postMessage({
        isStreamlitMessage: true,
        type: "streamlit:componentReady",
        apiVersion: 1
      }, "*");
      window.parent.postMessage({
        isStreamlitMessage: true,
        type: "streamlit:setFrameHeight",
        height: 0
      }, "*");
      document.addEventListener("visibilitychange", () => {
        send(document.visibilityState === "hidden" ? "left" : "returned");
      });
      window.addEventListener("blur", () => {
        if (document.visibilityState !== "hidden") send("left");
      });
      window.addEventListener("focus", () => {
        if (document.visibilityState === "visible") send("returned");
      });
    })();
    </script></body></html>
    """
    (component_dir / "index.html").write_text(component_html, encoding="utf-8")
    return components.declare_component("fym_visibility_tracker", path=str(component_dir))


def record_visibility_event(event):
    """Store browser tab leave/return events in the candidate's Streamlit session."""
    if not isinstance(event, dict):
        return
    event_id = str(event.get("id", ""))
    state = event.get("state")
    timestamp = event.get("timestamp")
    if not event_id or state not in {"left", "returned"}:
        return
    if event_id == st.session_state.get("last_visibility_event_id"):
        return
    st.session_state.last_visibility_event_id = event_id

    try:
        event_time = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
        event_time = event_time.astimezone(timezone.utc)
    except (TypeError, ValueError):
        event_time = datetime.now(timezone.utc)

    events = st.session_state.setdefault("tab_events", [])
    if state == "left":
        # Ignore duplicate blur/visibility notifications while already away.
        if st.session_state.get("away_started") is not None:
            return
        st.session_state.tab_switches = int(st.session_state.get("tab_switches", 0)) + 1
        st.session_state.away_started = event_time
        events.append({"event": "Էջից դուրս եկավ", "timestamp": event_time.isoformat(), "away_seconds": None})
    else:
        away_started = st.session_state.get("away_started")
        if away_started is None:
            return
        away_seconds = max(0.0, (event_time - away_started).total_seconds())
        st.session_state.total_away = float(st.session_state.get("total_away", 0.0)) + away_seconds
        st.session_state.longest_away = max(float(st.session_state.get("longest_away", 0.0)), away_seconds)
        events.append({"event": "Վերադարձավ էջ", "timestamp": event_time.isoformat(), "away_seconds": round(away_seconds, 2)})
        st.session_state.away_started = None


def inject_candidate_restrictions():
    # Browser restrictions are deterrents only; browsers can bypass them.
    components.html(
        """
        <script>
        (() => {
          try {
            const d = window.parent.document;
            if (d.__fymGuardInstalled) return;
            d.__fymGuardInstalled = true;
            d.addEventListener('contextmenu', e => e.preventDefault(), true);
            d.addEventListener('copy', e => e.preventDefault(), true);
            d.addEventListener('cut', e => e.preventDefault(), true);
            d.addEventListener('paste', e => e.preventDefault(), true);
            d.addEventListener('selectstart', e => e.preventDefault(), true);
            d.addEventListener('keydown', e => {
              const k = (e.key || '').toLowerCase();
              if ((e.ctrlKey || e.metaKey) && ['c','v','x','a','p','s'].includes(k)) e.preventDefault();
            }, true);
          } catch (_) {}
        })();
        </script>
        """,
        height=0,
        width=0,
    )
    tracker = get_visibility_component()
    visibility_event = tracker(key="fym_visibility_event", default=None)
    record_visibility_event(visibility_event)


def render_logo():
    st.markdown(
        f'<div class="fym-logo-wrap"><img src="data:image/png;base64,{FYM_LOGO_PNG}" '
        'alt="FYM Hospitality Group" /></div>',
        unsafe_allow_html=True,
    )


def render_hero(subtitle: str = ""):
    render_logo()
    if subtitle:
        st.markdown(
            f'<div class="hero-subtitle"><h2>{subtitle}</h2></div>',
            unsafe_allow_html=True,
        )

def render_candidate_home():
    render_hero("Թեստ")
    st.markdown("### Բարի գալուստ")
    st.markdown(
        '<p class="muted">Խնդրում ենք լրացնել Ձեր տվյալները՝ թեստը սկսելու համար։ '
        'Ձեր պատասխանները հասանելի են HR Team-ին։</p>',
        unsafe_allow_html=True,
    )
    with st.form("candidate_details"):
        first = st.text_input("Անուն", max_chars=80, autocomplete="off")
        last = st.text_input("Ազգանուն", max_chars=80, autocomplete="off")
        position = st.text_input("Հաստիք", max_chars=120, autocomplete="off")
        submitted = st.form_submit_button("Շարունակել", use_container_width=True)
    if submitted:
        if not first.strip() or not last.strip() or not position.strip():
            st.error("Խնդրում ենք լրացնել բոլոր դաշտերը։")
        else:
            st.session_state.first_name = first.strip()
            st.session_state.last_name = last.strip()
            st.session_state.position = position.strip()
            st.session_state.page = "instructions"
            st.rerun()
    st.markdown("---")
    with st.expander("HR / Admin մուտք"):
        st.caption("Մուտքը նախատեսված է միայն լիազորված HR աշխատակիցների համար։")
        if st.button("Բացել HR մուտքը", use_container_width=True):
            st.session_state.page = "admin_login"
            st.rerun()

def render_instructions():
    render_hero("Թեստ")
    st.markdown(
        """
        Գնահատե՛ք, թե որքան հաճույքով կանեիք յուրաքանչյուր գործունեությունը։
        Թեստը լրացնելուց անտեսե՛ք ձեր հմտությունները, պատրաստվածությունն ու աշխատանքի վարձատրությունը։

        **Գնահատե՛ք միայն ձեր իրական հետաքրքրվածությունը։**
        """
    )
    st.markdown("**Թեստը բաղկացած է 15 հարցից։ Յուրաքանչյուր հարցի համար ընտրեք մեկ պատասխան։ Տևողությունը՝ 5 րոպե։**")
    st.markdown(
        '<p class="small-note">Ձեր պատասխանները հասանելի են HR Team-ին։</p>',
        unsafe_allow_html=True,
    )
    if st.button("Սկսել թեստը", use_container_width=True):
        st.session_state.answers = {}
        st.session_state.question_index = 0
        st.session_state.started_at = datetime.now(timezone.utc)
        st.session_state.timed_out = False
        st.session_state.tab_switches = 0
        st.session_state.total_away = 0.0
        st.session_state.longest_away = 0.0
        st.session_state.away_started = None
        st.session_state.tab_events = []
        st.session_state.last_visibility_event_id = None
        st.session_state.page = "assessment"
        st.rerun()

def submit_assessment(timed_out: bool = False):
    st.session_state.timed_out = timed_out
    if not st.session_state.get("candidate_submitted", False):
        save_candidate()
        st.session_state.candidate_submitted = True
    st.session_state.page = "complete"
    st.rerun()

def render_assessment():
    render_logo()
    inject_candidate_restrictions()
    elapsed = (datetime.now(timezone.utc) - st.session_state.started_at).total_seconds()
    remaining = max(0, TEST_SECONDS - int(elapsed))
    if remaining <= 0:
        submit_assessment(timed_out=True)
        return
    st_autorefresh(interval=1000, key="assessment_timer_refresh")
    idx = int(st.session_state.question_index)
    total = len(QUESTIONS)
    mins, secs = divmod(remaining, 60)
    st.markdown(
        f'<div class="timer">Մնացած ժամանակը՝ {mins:02d}:{secs:02d}</div>',
        unsafe_allow_html=True,
    )
    st.progress((idx + 1) / total, text=f"Հարց {idx + 1} / {total}")
    question, _internal_letter = QUESTIONS[idx]
    st.markdown(f"### {question}")
    current = st.session_state.answers.get(idx)
    selected_index = (current - 1) if current else None
    selected = st.radio(
        "Ընտրեք մեկ պատասխան",
        OPTIONS,
        index=selected_index,
        key=f"answer_{idx}",
        label_visibility="collapsed",
    )
    st.caption("Ընտրեք այն տարբերակը, որն առավել ճշգրիտ է արտահայտում Ձեր հետաքրքրվածությունը։")
    if selected:
        st.session_state.answers[idx] = OPTIONS.index(selected) + 1

    left, right = st.columns(2)
    with left:
        if idx > 0 and st.button("Նախորդ", use_container_width=True):
            st.session_state.question_index -= 1
            st.rerun()
    with right:
        if idx < total - 1:
            if st.button("Հաջորդ", use_container_width=True):
                if idx not in st.session_state.answers:
                    st.warning("Խնդրում ենք ընտրել պատասխան՝ շարունակելու համար։")
                else:
                    st.session_state.question_index += 1
                    st.rerun()
        else:
            if st.button("Ավարտել և ուղարկել", use_container_width=True):
                if len(st.session_state.answers) != total:
                    st.warning("Խնդրում ենք պատասխանել բոլոր հարցերին։")
                else:
                    submit_assessment(timed_out=False)

def render_completion():
    render_hero("Թեստի ավարտ")
    st.markdown(
        """
        <div class="success-panel">
            <h2>Շնորհակալություն</h2>
            <p>Ձեր թեստը հաջողությամբ ուղարկվել է։</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("Վերադառնալ գլխավոր էջ", use_container_width=True):
        reset_candidate()

def render_admin_login():
    render_hero("HR / Admin")
    st.markdown("### HR մուտք")
    with st.form("admin_login_form"):
        password = st.text_input("Գաղտնաբառ", type="password")
        submitted = st.form_submit_button("Մուտք գործել", use_container_width=True)
    if submitted:
        if verify_password(password, get_admin_hash()):
            st.session_state.admin_authenticated = True
            st.session_state.page = "admin"
            st.rerun()
        else:
            st.error("Գաղտնաբառը սխալ է։")
    if st.button("Վերադառնալ գլխավոր էջ"):
        st.session_state.page = "home"
        st.rerun()

def load_candidates() -> pd.DataFrame:
    with db_connect() as conn:
        return pd.read_sql_query("SELECT * FROM candidates ORDER BY id DESC", conn)

def render_candidate_report(row):
    scores = json.loads(row["scores_json"])
    answers = json.loads(row["answers_json"])
    code = row["top_code"]
    interpretation = get_interpretation(code)
    st.markdown(f"## {row['first_name']} {row['last_name']} — {row['position']}")
    st.caption(f"Լրացման ամսաթիվ՝ {row['completed_at']} | Տևողություն՝ {format_duration(row['duration_seconds'])}")
    if row["timed_out"]:
        st.warning("Թեստը ուղարկվել է ժամանակի ավարտի պատճառով։")
    st.markdown(f"### Առաջատար համադրություն՝ **{code}**")
    chart_df = pd.DataFrame({
        "Չափում": [DIMENSIONS[k] for k in scores],
        "Միջին միավոր": list(scores.values()),
    })
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            px.bar(chart_df, x="Չափում", y="Միջին միավոր", range_y=[0, 5],
                   title="Չափումների միավորներ"),
            use_container_width=True,
        )
    with c2:
        radar = chart_df.copy()
        radar.loc[len(radar)] = radar.iloc[0]
        st.plotly_chart(
            px.line_polar(radar, r="Միջին միավոր", theta="Չափում", line_close=True,
                          range_r=[0, 5], title="Հետաքրքրությունների պրոֆիլ"),
            use_container_width=True,
        )
    st.markdown("### Չափումների արդյունքներ")
    for letter, label in DIMENSIONS.items():
        st.write(f"**{label}:** {scores.get(letter, 0):.2f} / 5")
    st.markdown("### Հնարավոր ուժեղ կողմեր")
    for item in interpretation["strengths"]:
        st.markdown(f"- {item}")
    st.markdown("### Ուշադրության արժանի կողմեր")
    for item in interpretation["risks"]:
        st.markdown(f"- {item}")
    st.markdown("### Հնարավոր նախընտրելի աշխատանքային միջավայր")
    st.write(interpretation["environment"])
    st.markdown("### Հարցազրույցի առաջարկվող հարցեր")
    for item in interpretation["interview"]:
        st.markdown(f"- {item}")
    st.markdown("### Պատասխաններ")
    answer_rows = []
    for i, (question, _letter) in enumerate(QUESTIONS):
        score = answers.get(str(i))
        answer_rows.append({
            "Հարց": question,
            "Պատասխան": OPTIONS[int(score) - 1] if score else "Չի պատասխանվել",
            "Միավոր": score if score else "—",
        })
    st.dataframe(pd.DataFrame(answer_rows), use_container_width=True, hide_index=True)
    st.markdown("### Թեստի ընթացքի տվյալներ")
    st.write(f"Ժամանակի ավարտին ավտոմատ ուղարկում՝ {'Այո' if row['timed_out'] else 'Ոչ'}")
    st.write(f"Արձանագրված էջափոխումներ՝ {row['tab_switches']}")
    st.write(f"Էջից դուրս գտնվելու ընդհանուր ժամանակ՝ {format_duration(row['total_away_seconds'])}")
    st.write(f"Ամենաերկար բացակայություն՝ {format_duration(row['longest_away_seconds'])}")
    raw_events = row["tab_events_json"] if "tab_events_json" in row.keys() else "[]"
    try:
        event_rows = json.loads(raw_events or "[]")
    except (TypeError, ValueError):
        event_rows = []
    st.markdown("#### Էջից դուրս գալու և վերադառնալու պատմություն")
    if event_rows:
        event_df = pd.DataFrame(event_rows)
        if "timestamp" in event_df.columns:
            event_df["timestamp"] = pd.to_datetime(event_df["timestamp"], errors="coerce", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        if "away_seconds" in event_df.columns:
            event_df["away_seconds"] = event_df["away_seconds"].apply(
                lambda value: "—" if pd.isna(value) else format_duration(value)
            )
        event_df = event_df.rename(columns={
            "event": "Իրադարձություն",
            "timestamp": "Ժամանակ",
            "away_seconds": "Բացակայության տևողություն"
        })
        st.dataframe(event_df, use_container_width=True, hide_index=True)
    else:
        st.write("Էջից դուրս գալու իրադարձություններ չեն արձանագրվել։")
    st.caption("Համակարգը կարող է արձանագրել գնահատման էջի անտեսանելի դառնալը կամ պատուհանի ֆոկուսի կորուստը, սակայն չի կարող որոշել՝ կոնկրետ որ կայքն է բացվել։")

def render_admin():
    render_hero("HR կառավարման վահանակ")
    with st.sidebar:
        st.markdown("## FYM HR")
        st.caption("Լիազորված մուտք")
        if st.button("Դուրս գալ", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.session_state.page = "home"
            st.rerun()
        st.markdown("---")
        st.markdown("### Գաղտնաբառի փոփոխություն")
        with st.form("change_password_form"):
            old = st.text_input("Գործող գաղտնաբառ", type="password")
            new = st.text_input("Նոր գաղտնաբառ", type="password")
            confirm = st.text_input("Կրկնել նոր գաղտնաբառը", type="password")
            change = st.form_submit_button("Փոխել գաղտնաբառը")
        if change:
            if not verify_password(old, get_admin_hash()):
                st.error("Գործող գաղտնաբառը սխալ է։")
            elif len(new) < 10:
                st.error("Նոր գաղտնաբառը պետք է ունենա առնվազն 10 նիշ։")
            elif new != confirm:
                st.error("Նոր գաղտնաբառերը չեն համընկնում։")
            else:
                set_admin_password(new)
                st.success("Գաղտնաբառը հաջողությամբ փոխվեց։")
    df = load_candidates()
    st.markdown("## Թեկնածուների արդյունքներ")
    if df.empty:
        st.info("Դեռ պահպանված թեկնածուների արդյունքներ չկան։")
        return
    df["completed_at"] = pd.to_datetime(df["completed_at"], errors="coerce")
    total = len(df)
    avg_duration = int(df["duration_seconds"].mean())
    col1, col2, col3 = st.columns(3)
    col1.metric("Թեկնածուներ", total)
    col2.metric("Միջին տևողություն", format_duration(avg_duration))
    col3.metric("Ժամանակին ավարտված", int((df["timed_out"] == 0).sum()))
    st.markdown("### Թեկնածուների ցանկ")
    list_df = df[["id", "first_name", "last_name", "position", "completed_at", "top_code"]].copy()
    list_df.columns = ["ID", "Անուն", "Ազգանուն", "Պաշտոն", "Ամսաթիվ", "Առաջատար կոդ"]
    st.dataframe(list_df, use_container_width=True, hide_index=True)
    csv = df.drop(columns=["answers_json", "scores_json"]).to_csv(index=False).encode("utf-8-sig")
    st.download_button("Ներբեռնել թեկնածուների ամփոփ տվյալները (CSV)", csv,
                       file_name="fym_candidates_summary.csv", mime="text/csv")
    candidate_ids = df["id"].astype(int).tolist()
    selected_id = st.selectbox(
        "Ընտրել թեկնածուի ամբողջական հաշվետվությունը",
        candidate_ids,
        format_func=lambda x: (
            f"{df.loc[df['id'] == x, 'first_name'].iloc[0]} "
            f"{df.loc[df['id'] == x, 'last_name'].iloc[0]} — "
            f"{df.loc[df['id'] == x, 'position'].iloc[0]}"
        ),
    )
    selected_row = df.loc[df["id"] == selected_id].iloc[0]
    render_candidate_report(selected_row)
    st.markdown("---")
    st.markdown("### Ընդհանուր վիճակագրություն")
    code_counts = df["top_code"].value_counts().rename_axis("Կոդ").reset_index(name="Քանակ")
    st.plotly_chart(px.bar(code_counts, x="Կոդ", y="Քանակ", title="Առաջատար համադրությունների բաշխում"),
                    use_container_width=True)

def main():
    init_db()
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    page = st.session_state.page
    if page == "home":
        render_candidate_home()
    elif page == "instructions":
        render_instructions()
    elif page == "assessment":
        render_assessment()
    elif page == "complete":
        render_completion()
    elif page == "admin_login":
        render_admin_login()
    elif page == "admin":
        if st.session_state.admin_authenticated:
            render_admin()
        else:
            st.session_state.page = "admin_login"
            st.rerun()
    else:
        st.session_state.page = "home"
        st.rerun()

if __name__ == "__main__":
    main()