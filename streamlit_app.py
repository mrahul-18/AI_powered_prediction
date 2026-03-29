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

_TEAM_LOGO_FILES = {
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
}


@st.cache_data
def _load_logo_b64(filename: str) -> str:
    p = _LOGOS_DIR / filename
    if not p.is_file():
        return ""
    return base64.b64encode(p.read_bytes()).decode()


@st.cache_data
def _load_ipl_logo_b64() -> str:
    p = _LOGOS_DIR / "ipl logo.png"
    if not p.is_file():
        return ""
    return base64.b64encode(p.read_bytes()).decode()


def _team_logo_src(name: str) -> str:
    fn = _TEAM_LOGO_FILES.get(name)
    if not fn:
        return ""
    b64 = _load_logo_b64(fn)
    return f"data:image/png;base64,{b64}" if b64 else ""


def _ipl_logo_src() -> str:
    b64 = _load_ipl_logo_b64()
    return f"data:image/png;base64,{b64}" if b64 else ""


st.set_page_config(page_title="IPL Win Predictor", page_icon="🏏", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #f0f0f0;
    }
    .ipl-header {
        display: flex; justify-content: center; padding: 1rem 0 0.5rem;
    }
    .ipl-header img { height: 100px; }
    .team-card {
        background: rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1.5rem 1rem;
        text-align: center;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.12);
    }
    .team-card img {
        width: 110px; height: 110px; object-fit: contain; margin-bottom: 0.5rem;
    }
    .team-card h3 { margin: 0; font-size: 1.1rem; }
    .vs-badge {
        font-size: 2.2rem; font-weight: 800; color: #facc15;
        text-shadow: 0 0 20px rgba(250,204,21,0.5);
        display: flex; align-items: center; justify-content: center; height: 100%;
    }
    .result-card {
        background: rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.15);
        margin-top: 1rem;
    }
    .prob-bar {
        height: 38px; border-radius: 19px; overflow: hidden;
        background: rgba(255,255,255,0.1);
        margin: 0.8rem 0;
        display: flex;
    }
    .prob-fill-winner {
        height: 100%; display: flex; align-items: center;
        justify-content: center; font-weight: 700; font-size: 0.95rem;
        color: #fff; border-radius: 19px 0 0 19px;
    }
    .prob-fill-loser {
        height: 100%; display: flex; align-items: center;
        justify-content: center; font-weight: 700; font-size: 0.95rem;
        color: #fff; border-radius: 0 19px 19px 0; flex: 1;
    }
    .winner-label {
        font-size: 1.6rem; font-weight: 800; margin-bottom: 0.2rem;
    }
    .ground-tag {
        display: inline-block; background: rgba(255,255,255,0.12);
        padding: 0.25rem 1rem; border-radius: 20px;
        font-size: 0.85rem; margin-top: 0.5rem;
    }
    div[data-testid="stSelectbox"] label { color: #e0e0e0 !important; }

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
        width: 55%;
        max-width: 340px;
        opacity: 0.07;
        filter: grayscale(20%);
    }

    /* Toggle switch styling */
    .toggle-container {
        display: flex; justify-content: center; margin: 1.2rem 0 1.5rem;
    }
    .toggle-wrapper {
        display: inline-flex; background: rgba(255,255,255,0.08);
        border-radius: 30px; padding: 4px;
        border: 1px solid rgba(255,255,255,0.15);
    }
    .toggle-btn {
        padding: 0.5rem 2rem; border-radius: 26px; font-weight: 700;
        font-size: 0.95rem; cursor: pointer; transition: all 0.3s;
        border: none; color: #94a3b8; background: transparent;
    }
    .toggle-btn.active {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #fff; box-shadow: 0 4px 15px rgba(99,102,241,0.4);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="ipl-header"><img src="{_ipl_logo_src()}" alt="IPL"></div>',
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='text-align:center; margin:0 0 0.3rem;'>IPL Win Predictor</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#94a3b8; margin-bottom:0.5rem;'>"
    "Select teams & venue to get win probabilities</p>",
    unsafe_allow_html=True,
)

# ── Toggle switch: Before Toss / After Toss ──
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

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


def _render_bg_logos(t1: str, t2: str):
    """Inject a fixed full-screen overlay with both team logos, split half-half."""
    src1 = _team_logo_src(t1)
    src2 = _team_logo_src(t2)
    if not src1 or not src2:
        return
    st.markdown(
        f"""<div class="bg-logos-overlay">
            <div class="bg-logo-half">
                <img src="{src1}" alt="{t1}">
            </div>
            <div class="bg-logo-half">
                <img src="{src2}" alt="{t2}">
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def _render_matchup(t1: str, t2: str):
    c1, c_vs, c2 = st.columns([2, 1, 2])
    with c1:
        st.markdown(
            f"""<div class="team-card">
                <img src="{_team_logo_src(t1)}" alt="{t1}">
                <h3>{t1}</h3>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_vs:
        st.markdown('<div class="vs-badge">VS</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            f"""<div class="team-card">
                <img src="{_team_logo_src(t2)}" alt="{t2}">
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
    l_color = TEAM_COLORS.get(loser, "#64748b")
    w_pct = max(wp * 100, 5)
    w_logo = _team_logo_src(winner)
    l_logo = _team_logo_src(loser)
    st.markdown(
        f"""<div class="result-card">
            <div class="winner-label" style="color:{w_color};">
                <img src="{w_logo}" width="36" style="vertical-align:middle; margin-right:8px;">
                {winner}
            </div>
            <p style="margin:0; color:#94a3b8;">is predicted to win</p>
            <div class="prob-bar">
                <div class="prob-fill-winner" style="width:{w_pct:.1f}%; background:{w_color};">
                    {wp*100:.1f}%
                </div>
                <div class="prob-fill-loser" style="background:{l_color};">
                    {lp*100:.1f}%
                </div>
            </div>
            <p style="margin:0.4rem 0 0;">
                <img src="{w_logo}" width="28" style="vertical-align:middle;">
                <strong>{winner}</strong>  {wp*100:.1f}%
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <img src="{l_logo}" width="28" style="vertical-align:middle;">
                <strong>{loser}</strong>  {lp*100:.1f}%
            </p>
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


# ── Before Toss ──
if st.session_state.mode == "before":
    st.subheader("Before Toss Prediction")
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

# ── After Toss ──
else:
    st.subheader("After Toss Prediction")
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
