"""Streamlit IPL Win Predictor – consumes the FastAPI backend."""

import urllib.parse

import requests
import streamlit as st

API_BASE = "https://nonexpiatory-paroxysmally-semaj.ngrok-free.dev"

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

TEAM_LOGO_URLS = {
    "Chennai Super Kings": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/CSK/logos/Roundbig/CSKroundbig.png",
    "Delhi Capitals": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/DC/Logos/Roundbig/DCroundbig.png",
    "Gujarat Titans": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/GT/Logos/Roundbig/GTroundbig.png",
    "Kolkata Knight Riders": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/KKR/Logos/Roundbig/KKRroundbig.png",
    "Lucknow Super Giants": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/LSG/Logos/Roundbig/LSGroundbig.png",
    "Mumbai Indians": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/MI/Logos/Roundbig/MIroundbig.png",
    "Punjab Kings": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/PBKS/Logos/Roundbig/PBKSroundbig.png",
    "Rajasthan Royals": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/RR/Logos/Roundbig/RRroundbig.png",
    "Royal Challengers Bengaluru": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/RCB/Logos/Roundbig/RCBroundbig.png",
    "Sunrisers Hyderabad": "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/SRH/Logos/Roundbig/SRHroundbig.png",
}

IPL_LOGO_URL = "https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadline2025.png"

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

st.set_page_config(page_title="IPL-AGI", page_icon="🏏", layout="wide")

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
    .ipl-header img { height: 90px; }
    .team-card {
        background: rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1.5rem 1rem;
        text-align: center;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.12);
    }
    .team-card img { width: 100px; height: 100px; margin-bottom: 0.5rem; }
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
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="ipl-header"><img src="{IPL_LOGO_URL}" alt="IPL"></div>',
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='text-align:center; margin:0 0 0.3rem;'>IPL Win Predictor</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#94a3b8; margin-bottom:1.5rem;'>"
    "Powered by XGBoost  •  Select teams & venue to get win probabilities</p>",
    unsafe_allow_html=True,
)

tab_before, tab_after = st.tabs(["Before Toss", "After Toss"])


def _format_option(name: str) -> str:
    return name


def _team_logo(name: str) -> str:
    return TEAM_LOGO_URLS.get(name, "")


def _render_matchup(t1: str, t2: str):
    c1, c_vs, c2 = st.columns([2, 1, 2])
    with c1:
        st.markdown(
            f"""<div class="team-card">
                <img src="{_team_logo(t1)}" alt="{t1}">
                <h3>{t1}</h3>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_vs:
        st.markdown('<div class="vs-badge">VS</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            f"""<div class="team-card">
                <img src="{_team_logo(t2)}" alt="{t2}">
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
    st.markdown(
        f"""<div class="result-card">
            <div class="winner-label" style="color:{w_color};">🏆  {winner}</div>
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
                <img src="{_team_logo(winner)}" width="28" style="vertical-align:middle;">
                <strong>{winner}</strong>  {wp*100:.1f}%
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <img src="{_team_logo(loser)}" width="28" style="vertical-align:middle;">
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
            detail = r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text
            st.error(f"API error ({r.status_code}): {detail}")
            return None
        return r.json()
    except requests.ConnectionError:
        st.error("Cannot reach the API server. Make sure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


with tab_before:
    st.subheader("Before Toss Prediction")
    col1, col2, col3 = st.columns(3)
    with col1:
        bt_team1 = st.selectbox("Team 1", TEAM_NAMES, index=None, placeholder="Select Team 1", key="bt_t1")
    with col2:
        bt_team2 = st.selectbox("Team 2", TEAM_NAMES, index=None, placeholder="Select Team 2", key="bt_t2")
    with col3:
        bt_ground = st.selectbox("Ground", GROUND_NAMES, index=None, placeholder="Select Ground", key="bt_g")

    if bt_team1 and bt_team2:
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


with tab_after:
    st.subheader("After Toss Prediction")
    col1, col2, col3 = st.columns(3)
    with col1:
        at_bat = st.selectbox("Team Batting First", TEAM_NAMES, index=None, placeholder="Select Batting Team", key="at_bat")
    with col2:
        at_field = st.selectbox("Team Fielding First", TEAM_NAMES, index=None, placeholder="Select Fielding Team", key="at_field")
    with col3:
        at_ground = st.selectbox("Ground", GROUND_NAMES, index=None, placeholder="Select Ground", key="at_g")

    if at_bat and at_field:
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
