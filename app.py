from __future__ import annotations

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
    .hero {
        background: #FFFFFF; color: #000000; padding: 1.6rem 1.8rem;
        border: 1px solid #000000; border-radius: 18px;
        margin-bottom: 1.3rem; box-shadow: none;
    }
    .hero h1, .hero p { color: #000000 !important; }
    .hero h1 { margin: 0; font-size: 2rem; }
    .hero p { margin: .55rem 0 0 0; }
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


def render_hero(subtitle: str = ""):
    st.markdown(
        f'<div class="hero"><h1>FYM Hospitality Group</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )

def render_candidate_home():
    render_hero("Թեստ")
    st.markdown("### Բարի գալուստ")
    st.markdown(
        '<p class="muted">Խնդրում ենք լրացնել Ձեր տվյալները՝ հարցաթերթիկը սկսելու համար։ '
        'Ձեր պատասխանները հասանելի են HR Team-ին։</p>',
        unsafe_allow_html=True,
    )
    with st.form("candidate_details"):
        first = st.text_input("Անուն", max_chars=80)
        last = st.text_input("Ազգանուն", max_chars=80)
        position = st.text_input("Հաստիք", max_chars=120)
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
    st.markdown("**Հարցաթերթիկը բաղկացած է 15 հարցից։ Յուրաքանչյուր հարցի համար ընտրեք մեկ պատասխան։ Տևողությունը՝ 5 րոպե։**")
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
    st.markdown('<div class="question-card">', unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)
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
    render_hero("Հարցաթերթիկի ավարտ")
    st.markdown(
        """
        <div class="success-panel">
            <h2>Շնորհակալություն</h2>
            <p>Ձեր հարցաթերթիկը հաջողությամբ ուղարկվել է։</p>
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
        st.warning("Հարցաթերթիկը ուղարկվել է ժամանակի ավարտի պատճառով։")
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