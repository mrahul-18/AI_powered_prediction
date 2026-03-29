"""Streamlit IPL Win Predictor – consumes the FastAPI backend."""

from __future__ import annotations

import base64
from pathlib import Path

import requests
import streamlit as st

API_BASE = "https://nonexpiatory-paroxysmally-semaj.ngrok-free.dev"

_LOGOS_DIR = Path(__file__).resolve().parent / "team logos"

TEAM_NAMES = [
    "Chennai Super Kings",
    "Delhi Capitals",
    "Gujarat Titans",
    "Kolkata Knight Riders",
    "Lucknow Super Giants",
    "Mumbai Indians",
    "Punjab Kings",
    "Rajasthan Royals",
    "Royal Challengers Bengaluru",
    "Sunrisers Hyderabad",
]

GROUND_NAMES = [
    "Ahmedabad",
    "Bengaluru",
    "Chandigarh",
    "Chennai",
    "Delhi",
    "Dharamsala",
    "Guwahati",
    "Hyderabad",
    "Jaipur",
    "Kolkata",
    "Lucknow",
    "Mullanpur",
    "Mumbai",
    "New Chandigarh",
    "Pune",
    "Visakhapatnam",
]

TEAM_COLORS = {
    "Chennai Super Kings": "#FBBF24",
    "Delhi Capitals": "#1D4ED8",
    "Gujarat Titans": "#1E3A5F",
    "Kolkata Knight Riders": "#6B21A8",
    "Lucknow Super Giants": "#0EA5E9",
    "Mumbai Indians": "#1E40AF",
    "Punjab Kings": "#DC2626",
    "Rajasthan Royals": "#EC4899",
    "Royal Challengers Bengaluru": "#B91C1C",
    "Sunrisers Hyderabad": "#F97316",
}

_ALL_LOGO_FILES: dict[str, str] = {
    "Chennai Super Kings": "Chennai Super Kings.png",
    "Delhi Capitals": "Delhi Capitals.png",
    "Gujarat Titans": "Gujarat Titans.png",
    "Kolkata Knight Riders": "Kolkata Knight Riders.png",
    "Lucknow Super Giants": "Lucknow Super Giants.svg.png",
    "Mumbai Indians": "Mumbai Indians.png",
    "Punjab Kings": "Punjab Kings.png",
    "Rajasthan Royals": "Rajasthan Royals.png",
    "Royal Challengers Bengaluru": "Royal Challengers Bengaluru.png",
    "Sunrisers Hyderabad": "Sunrisers Hyderabad.png",
    "IPL": "ipl logo.png",
}


@st.cache_data
def _load_logo_b64(filename: str) -> str:
    p = _LOGOS_DIR / filename
    if not p.is_file():
        return ""
    return base64.b64encode(p.read_bytes()).decode()


def _logo_src(name: str) -> str:
    fn = _ALL_LOGO_FILES.get(name, "")
    if not fn:
        return ""
    b64 = _load_logo_b64(fn)
    return f"data:image/png;base64,{b64}" if b64 else ""


# ─── Page config ───
st.set_page_config(page_title="IPL Win Predictor", page_icon="🏏", layout="wide")

# ─── CSS ───
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

    .stApp {
        background: linear-gradient(160deg, #0a0a1a 0%, #121236 40%, #1a0a2e 70%, #0d0d20 100%);
        color: #f0f0f0;
        font-family: 'Inter', sans-serif;
    }

    /* Animated starfield background */
    .stApp::before {
        content: '';
        position: fixed; top: 0; left: 0;
        width: 100vw; height: 100vh;
        background-image:
            radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.15) 50%, transparent 50%),
            radial-gradient(1px 1px at 30% 60%, rgba(255,255,255,0.12) 50%, transparent 50%),
            radial-gradient(1px 1px at 50% 10%, rgba(255,255,255,0.1) 50%, transparent 50%),
            radial-gradient(1px 1px at 70% 80%, rgba(255,255,255,0.08) 50%, transparent 50%),
            radial-gradient(1px 1px at 90% 40%, rgba(255,255,255,0.12) 50%, transparent 50%),
            radial-gradient(2px 2px at 15% 85%, rgba(255,255,255,0.06) 50%, transparent 50%),
            radial-gradient(2px 2px at 85% 15%, rgba(255,255,255,0.06) 50%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* IPL header */
    .ipl-hero {
        text-align: center;
        padding: 2rem 0 0.5rem;
        position: relative;
        z-index: 1;
    }
    .ipl-hero img {
        height: 110px;
        filter: drop-shadow(0 0 30px rgba(99,102,241,0.3));
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    .ipl-hero h1 {
        font-size: 2.4rem;
        font-weight: 900;
        margin: 0.6rem 0 0.2rem;
        background: linear-gradient(135deg, #e0e7ff, #a5b4fc, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    .ipl-hero p {
        color: #64748b;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Glass cards */
    .team-card {
        background: rgba(255,255,255,0.04);
        border-radius: 20px;
        padding: 1.8rem 1rem;
        text-align: center;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.08);
        transition: transform 0.3s, box-shadow 0.3s;
        position: relative; z-index: 1;
    }
    .team-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99,102,241,0.15);
    }
    .team-card img {
        width: 120px; height: 120px; object-fit: contain;
        margin-bottom: 0.7rem;
        filter: drop-shadow(0 4px 12px rgba(0,0,0,0.4));
    }
    .team-card h3 {
        margin: 0; font-size: 1.05rem; font-weight: 700;
        color: #e2e8f0;
    }

    /* VS */
    .vs-badge {
        font-size: 2.6rem; font-weight: 900;
        background: linear-gradient(135deg, #facc15, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
        filter: drop-shadow(0 0 20px rgba(250,204,21,0.4));
        display: flex; align-items: center; justify-content: center;
        height: 100%;
        position: relative; z-index: 1;
    }

    /* Result card */
    .result-card {
        background: rgba(255,255,255,0.05);
        border-radius: 22px;
        padding: 2.2rem 2rem;
        text-align: center;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        margin-top: 1.5rem;
        position: relative; z-index: 1;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .winner-label {
        font-size: 1.8rem; font-weight: 900; margin-bottom: 0.3rem;
        display: flex; align-items: center; justify-content: center; gap: 10px;
    }
    .winner-label img {
        filter: drop-shadow(0 2px 8px rgba(0,0,0,0.4));
    }
    .prob-bar {
        height: 44px; border-radius: 22px; overflow: hidden;
        background: rgba(255,255,255,0.06);
        margin: 1rem 0;
        display: flex;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }
    .prob-fill-winner {
        height: 100%; display: flex; align-items: center;
        justify-content: center; font-weight: 800; font-size: 1rem;
        color: #fff; border-radius: 22px 0 0 22px;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    .prob-fill-loser {
        height: 100%; display: flex; align-items: center;
        justify-content: center; font-weight: 800; font-size: 1rem;
        color: #fff; border-radius: 0 22px 22px 0; flex: 1;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    .result-teams {
        display: flex; justify-content: center; align-items: center;
        gap: 2rem; margin-top: 0.6rem; flex-wrap: wrap;
    }
    .result-teams .rt-item {
        display: flex; align-items: center; gap: 8px; font-weight: 600;
    }
    .result-teams img { filter: drop-shadow(0 2px 6px rgba(0,0,0,0.3)); }
    .ground-tag {
        display: inline-block;
        background: rgba(255,255,255,0.08);
        padding: 0.35rem 1.2rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 0.8rem;
        color: #94a3b8;
        border: 1px solid rgba(255,255,255,0.06);
    }

    /* Selectbox styling */
    div[data-testid="stSelectbox"] label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }

    /* Background split logos overlay */
    .bg-logos-overlay {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        pointer-events: none;
        z-index: 0;
        display: flex;
    }
    .bg-logo-half {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .bg-logo-half img {
        width: 60%;
        max-width: 380px;
        opacity: 0.06;
        filter: grayscale(30%) blur(1px);
    }

    /* Divider */
    .section-divider {
        width: 60px; height: 3px; margin: 1rem auto;
        background: linear-gradient(90deg, #6366f1, #a78bfa);
        border-radius: 3px;
    }

    /* Subheader */
    .mode-title {
        text-align: center; font-size: 1.3rem; font-weight: 800;
        color: #c7d2fe; margin-bottom: 0.2rem;
        position: relative; z-index: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Header ───
st.markdown(
    f"""<div class="ipl-hero">
        <img src="{_logo_src('IPL')}" alt="IPL">
        <h1>IPL Win Predictor</h1>
        <p>Powered by NeonTech Labs | Select teams & venue to get win probabilities</p>
    </div>""",
    unsafe_allow_html=True,
)

# ─── Mode toggle ───
if "mode" not in st.session_state:
    st.session_state.mode = "before"

_c_left, _c_toggle, _c_right = st.columns([2, 3, 2])
with _c_toggle:
    tc1, tc2 = st.columns(2)
    with tc1:
        if st.button(
            "⚡ Before Toss",
            key="sw_before",
            type="primary" if st.session_state.mode == "before" else "secondary",
            use_container_width=True,
        ):
            st.session_state.mode = "before"
    with tc2:
        if st.button(
            "🪙 After Toss",
            key="sw_after",
            type="primary" if st.session_state.mode == "after" else "secondary",
            use_container_width=True,
        ):
            st.session_state.mode = "after"

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ─── Helpers ───
def _render_bg_logos(t1: str, t2: str):
    src1, src2 = _logo_src(t1), _logo_src(t2)
    if not src1 or not src2:
        return
    st.markdown(
        f"""<div class="bg-logos-overlay">
            <div class="bg-logo-half"><img src="{src1}" alt="{t1}"></div>
            <div class="bg-logo-half"><img src="{src2}" alt="{t2}"></div>
        </div>""",
        unsafe_allow_html=True,
    )


def _render_matchup(t1: str, t2: str):
    c1, c_vs, c2 = st.columns([2, 1, 2])
    with c1:
        st.markdown(
            f"""<div class="team-card">
                <img src="{_logo_src(t1)}" alt="{t1}">
                <h3>{t1}</h3>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_vs:
        st.markdown('<div class="vs-badge">VS</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            f"""<div class="team-card">
                <img src="{_logo_src(t2)}" alt="{t2}">
                <h3>{t2}</h3>
            </div>""",
            unsafe_allow_html=True,
        )


def _render_result(data: dict):
    winner = data["winner"]
    loser = data["loser"]
    wp = data["win_probability"]
    lp = data["lose_probability"]
    ground = data["ground"]
    w_color = TEAM_COLORS.get(winner, "#22c55e")
    l_color = TEAM_COLORS.get(loser, "#475569")
    w_pct = max(wp * 100, 8)
    w_logo = _logo_src(winner)
    l_logo = _logo_src(loser)
    st.markdown(
        f"""<div class="result-card">
            <div class="winner-label" style="color:{w_color};">
                <img src="{w_logo}" width="40">
                {winner}
            </div>
            <p style="margin:0; color:#64748b; font-size:0.9rem;">is predicted to win</p>
            <div class="prob-bar">
                <div class="prob-fill-winner"
                     style="width:{w_pct:.1f}%; background: linear-gradient(90deg, {w_color}, {w_color}cc);">
                    {wp*100:.1f}%
                </div>
                <div class="prob-fill-loser"
                     style="background: linear-gradient(90deg, {l_color}cc, {l_color});">
                    {lp*100:.1f}%
                </div>
            </div>
            <div class="result-teams">
                <div class="rt-item">
                    <img src="{w_logo}" width="30">
                    <span style="color:{w_color};">{winner} — {wp*100:.1f}%</span>
                </div>
                <div class="rt-item">
                    <img src="{l_logo}" width="30">
                    <span style="color:{l_color};">{loser} — {lp*100:.1f}%</span>
                </div>
            </div>
            <div class="ground-tag">📍 {ground}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def _call_api(endpoint: str, params: dict) -> dict | None:
    url = f"{API_BASE}/{endpoint}"
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            detail = (
                r.json().get("detail", r.text)
                if r.headers.get("content-type", "").startswith("application/json")
                else r.text
            )
            st.error(f"API error ({r.status_code}): {detail}")
            return None
        return r.json()
    except requests.ConnectionError:
        st.error("Cannot reach the API server. Make sure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


# ─── Before Toss ───
if st.session_state.mode == "before":
    st.markdown('<div class="mode-title">Before Toss Prediction</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        bt_team1 = st.selectbox("Team 1", TEAM_NAMES, index=None, placeholder="Select Team 1", key="bt_t1")
    with col2:
        bt_team2 = st.selectbox("Team 2", TEAM_NAMES, index=None, placeholder="Select Team 2", key="bt_t2")
    with col3:
        bt_ground = st.selectbox("Ground", GROUND_NAMES, index=None, placeholder="Select Ground", key="bt_g")

    if bt_team1 and bt_team2:
        _render_bg_logos(bt_team1, bt_team2)
        _render_matchup(bt_team1, bt_team2)

    if st.button("Predict Winner", key="btn_bt", type="primary", use_container_width=True):
        if not bt_team1 or not bt_team2 or not bt_ground:
            st.warning("Please select both teams and a ground.")
        elif bt_team1 == bt_team2:
            st.warning("Team 1 and Team 2 must be different.")
        else:
            with st.spinner("Predicting..."):
                data = _call_api("before_toss", {"team1": bt_team1, "team2": bt_team2, "ground": bt_ground})
            if data:
                _render_result(data)

# ─── After Toss ───
else:
    st.markdown('<div class="mode-title">After Toss Prediction</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        at_bat = st.selectbox("Team Batting First", TEAM_NAMES, index=None, placeholder="Select Batting Team", key="at_bat")
    with col2:
        at_field = st.selectbox("Team Fielding First", TEAM_NAMES, index=None, placeholder="Select Fielding Team", key="at_field")
    with col3:
        at_ground = st.selectbox("Ground", GROUND_NAMES, index=None, placeholder="Select Ground", key="at_g")

    if at_bat and at_field:
        _render_bg_logos(at_bat, at_field)
        _render_matchup(at_bat, at_field)

    if st.button("Predict Winner", key="btn_at", type="primary", use_container_width=True):
        if not at_bat or not at_field or not at_ground:
            st.warning("Please select both teams and a ground.")
        elif at_bat == at_field:
            st.warning("Batting and fielding teams must be different.")
        else:
            with st.spinner("Predicting..."):
                data = _call_api("after_toss", {"team_batting": at_bat, "team_fielding": at_field, "ground": at_ground})
            if data:
                _render_result(data)
