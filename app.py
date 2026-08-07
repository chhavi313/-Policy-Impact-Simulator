import os

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv

from population import generate_population
from reactions import run_simulation
from aggregate import aggregate_results

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

st.set_page_config(
    page_title="Policy Impact Simulator",
    page_icon="🗳️",
    layout="wide",
)

CREAM = "#0A0E1A"         
PAPER = "#111A2E"         
PAPER_TINT = "#16223D"    
INK = "#E8EDF7"           
TEXT = INK
MUTED = "#8792AC"         
BORDER = "#223052"        
SHADOW = "#00030A"        

VIOLET = "#3B82F6"        
VIOLET_SOFT = "#152544"   
CORAL = "#818CF8"         
PINK = "#22D3EE"          
SUN = "#FBBF24"           
MINT = "#2DD4BF"          
SKY = "#38BDF8"           
RED = "#F87171"           
ORANGE = "#FB923C"        

EMPLOYMENT_COLORS = {"Unemployed": CORAL, "Salaried": VIOLET, "Business Owner": SKY}
EMPLOYMENT_ICONS = {"Unemployed": "◇", "Salaried": "◆", "Business Owner": "▲"}
EMPLOYMENT_EMOJI = {"Unemployed": "🔍", "Salaried": "💼", "Business Owner": "🏬"}
INCOME_DOTS = {"Poor": "$", "Middle Class": "$$", "Wealthy": "$$$"}

EXAMPLE_POLICIES = {
    "— pick an example, or write your own below —": "",
    "Remove fuel subsidy": "The government eliminates the fuel subsidy, causing fuel prices to rise by approximately 30% within one month.",
    "4-day work week mandate": "All companies with 50+ employees must move to a mandatory 4-day, 32-hour work week at full pay.",
    "Universal Basic Income pilot": "A universal basic income of $500/month is introduced for all adult citizens, funded by a new 3% wealth tax on assets above $2M.",
    "Small business tax cut": "Corporate tax rate for businesses with under $1M annual revenue is cut from 21% to 12%.",
    "Carbon tax with dividend": "A $50/ton carbon tax is imposed on all fossil fuel emissions, with revenue returned to citizens as an equal per-person dividend.",
    "Rent increase cap": "Annual rent increases are capped at 3% for all residential units in cities with over 500,000 people.",
    "Minimum wage hike": "The federal minimum wage is raised from $7.25 to $15/hour, phased in over 2 years.",
    "Free public university": "Tuition at public universities is eliminated entirely, funded by a 1% increase in payroll tax.",
    "Congestion pricing": "Vehicles entering the city center on weekdays must pay a $15 congestion charge during peak commuting hours.",
    "Single-use plastic ban": "All single-use plastic bags and utensils are banned from retail and food service, effective in 6 months.",
    "Remote-work payroll tax": "Employers must pay a $2/day tax per employee who works from home, with revenue funding public transit upgrades.",
}


def support_color(pct):
    if pct >= 60:
        return MINT
    if pct <= 40:
        return RED
    return SUN



def icon_search(color, size=18):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none">'
            f'<circle cx="10" cy="10" r="7" stroke="{color}" stroke-width="2.2"/>'
            f'<line x1="15.4" y1="15.4" x2="21" y2="21" stroke="{color}" stroke-width="2.2" stroke-linecap="round"/>'
            f'</svg>')


def icon_flask(color, size=18):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none">'
            f'<path d="M9 2h6M10 2v6.4L4.7 18.6A2 2 0 0 0 6.5 21.5h11a2 2 0 0 0 1.8-2.9L14 8.4V2" '
            f'stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="9.5" cy="16.2" r="1.15" fill="{color}"/>'
            f'<circle cx="13.2" cy="17.6" r="0.9" fill="{color}"/>'
            f'</svg>')


def icon_grid(color, size=18):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none">'
            f'<rect x="3" y="3" width="7.5" height="7.5" rx="2" fill="{color}"/>'
            f'<rect x="13.5" y="3" width="7.5" height="7.5" rx="2" fill="{color}" opacity="0.55"/>'
            f'<rect x="3" y="13.5" width="7.5" height="7.5" rx="2" fill="{color}" opacity="0.55"/>'
            f'<rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2" fill="{color}" opacity="0.3"/>'
            f'</svg>')


def icon_trophy(color, size=18):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none">'
            f'<path d="M7 4h10v5a5 5 0 0 1-10 0V4Z" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M7 5H4a1 1 0 0 0-1 1v1a4 4 0 0 0 4 4M17 5h3a1 1 0 0 1 1 1v1a4 4 0 0 1-4 4" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
            f'<path d="M12 14v3m-3 3h6m-3-3v3" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
            f'</svg>')


def icon_cloud(color, size=18):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none">'
            f'<path d="M7 18a4.5 4.5 0 0 1-.6-8.96A5.5 5.5 0 0 1 17.2 8.1 4 4 0 0 1 17 18H7Z" fill="{color}"/>'
            f'</svg>')


def icon_bars(color, size=18):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none">'
            f'<rect x="3" y="12" width="4.5" height="9" rx="1.2" fill="{color}" opacity="0.5"/>'
            f'<rect x="9.75" y="7" width="4.5" height="14" rx="1.2" fill="{color}"/>'
            f'<rect x="16.5" y="3" width="4.5" height="18" rx="1.2" fill="{color}" opacity="0.8"/>'
            f'</svg>')


def icon_notes(color, size=18):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none">'
            f'<rect x="4" y="3" width="16" height="18" rx="2.5" stroke="{color}" stroke-width="2"/>'
            f'<line x1="8" y1="8.5" x2="16" y2="8.5" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>'
            f'<line x1="8" y1="12.5" x2="16" y2="12.5" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>'
            f'<line x1="8" y1="16.5" x2="12.5" y2="16.5" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>'
            f'</svg>')


def logo_mark(size=34):
    h = round(size * 100 / 110)
    return (f'<svg width="{size}" height="{h}" viewBox="0 0 110 100" fill="none">'
            f'<ellipse cx="55" cy="92" rx="42" ry="6" fill="{INK}" opacity="0.06"/>'
            f'<rect x="14" y="46" width="82" height="46" rx="14" fill="{VIOLET}"/>'
            f'<rect x="42" y="46" width="26" height="7" rx="3" fill="{INK}" opacity="0.18"/>'
            f'<g transform="rotate(-9 55 34)">'
            f'<rect x="38" y="4" width="34" height="52" rx="6" fill="#FFFFFF" stroke="{BORDER}" stroke-width="2"/>'
            f'<path d="M46 30 L54 38 L66 20" stroke="{MINT}" stroke-width="5" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'</g></svg>')


BUBBLE_CORAL = (
    f'<svg width="64" height="74" viewBox="0 0 64 74" fill="none">'
    f'<circle cx="32" cy="30" r="28" fill="{CORAL}"/>'
    f'<path d="M24 54 L16 70 L34 58 Z" fill="{CORAL}"/>'
    f'<circle cx="22" cy="26" r="3" fill="#fff"/><circle cx="42" cy="26" r="3" fill="#fff"/>'
    f'<path d="M20 36 Q32 48 44 36" stroke="#fff" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
    f'</svg>'
)
BUBBLE_SUN = (
    f'<svg width="50" height="58" viewBox="0 0 50 58" fill="none">'
    f'<circle cx="25" cy="23" r="21" fill="{SKY}"/>'
    f'<path d="M31 42 L38 55 L22 45 Z" fill="{SKY}"/>'
    f'<circle cx="17" cy="20" r="2.4" fill="#fff"/><circle cx="33" cy="20" r="2.4" fill="#fff"/>'
    f'<line x1="17" y1="30" x2="33" y2="30" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
    f'</svg>'
)
BUBBLE_SKY = (
    f'<svg width="40" height="46" viewBox="0 0 40 46" fill="none">'
    f'<circle cx="20" cy="18" r="16" fill="{VIOLET}"/>'
    f'<path d="M14 32 L9 42 L22 34 Z" fill="{VIOLET}"/>'
    f'<circle cx="14" cy="16" r="1.8" fill="#fff"/><circle cx="26" cy="16" r="1.8" fill="#fff"/>'
    f'<path d="M13 22 Q20 29 27 22" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
    f'</svg>'
)
SPARK_PINK = (f'<svg width="18" height="18" viewBox="0 0 18 18">'
              f'<g stroke="{PINK}" stroke-width="2.2" stroke-linecap="round">'
              f'<line x1="9" y1="2" x2="9" y2="16"/><line x1="2" y1="9" x2="16" y2="9"/></g></svg>')
SPARK_VIOLET = (f'<svg width="14" height="14" viewBox="0 0 14 14">'
                f'<g stroke="{VIOLET}" stroke-width="2" stroke-linecap="round">'
                f'<line x1="7" y1="1" x2="7" y2="13"/><line x1="1" y1="7" x2="13" y2="7"/></g></svg>')


def persona_badge(status, size=26):
    color = EMPLOYMENT_COLORS.get(status, MUTED)
    glyph = EMPLOYMENT_ICONS.get(status, "•")
    return (f'<span class="mono" style="display:inline-flex;align-items:center;justify-content:center;'
            f'width:{size}px;height:{size}px;min-width:{size}px;border-radius:50%;background:{color};'
            f'color:#fff;font-size:{size * 0.5:.0f}px;line-height:1;">{glyph}</span>')


def mood_face(vcolor, mood, size=64):
    r = size // 2
    if mood == "happy":
        mouth = (f'<path d="M{r - 14} {r + 6} Q{r} {r + 20} {r + 14} {r + 6}" '
                  f'stroke="{vcolor}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    elif mood == "sad":
        mouth = (f'<path d="M{r - 14} {r + 16} Q{r} {r + 4} {r + 14} {r + 16}" '
                  f'stroke="{vcolor}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    else:
        mouth = (f'<line x1="{r - 13}" y1="{r + 10}" x2="{r + 13}" y2="{r + 10}" '
                  f'stroke="{vcolor}" stroke-width="4" stroke-linecap="round"/>')
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<circle cx="{r}" cy="{r}" r="{r - 3}" fill="{vcolor}22" stroke="{vcolor}" stroke-width="2.4"/>'
            f'<circle cx="{r - 11}" cy="{r - 6}" r="3.6" fill="{vcolor}"/>'
            f'<circle cx="{r + 11}" cy="{r - 6}" r="3.6" fill="{vcolor}"/>'
            f'{mouth}</svg>')


def section(eyebrow, title, caption=None, icon_fn=None, accent=VIOLET):
    icon_html = ""
    if icon_fn:
        icon_html = (f'<div class="section-icon" style="background:{accent}1F;">'
                      f'{icon_fn(accent, 17)}</div>')
    cap_html = f'<div class="section-caption">{caption}</div>' if caption else ""
    st.markdown(
        f'<div class="section-head">'
        f'<div class="section-head-row">{icon_html}<div>'
        f'<div class="section-eyebrow" style="color:{accent};">{eyebrow}</div>'
        f'<div class="section-title">{title}</div>'
        f'</div></div>'
        f'{cap_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


PLOTLY_FONT = dict(family="Plus Jakarta Sans, sans-serif", color=INK)
PLOTLY_TITLE_FONT = dict(family="Fredoka, sans-serif", size=15, color=INK)
SUPPORT_SCALE = [[0, RED], [0.5, SUN], [1, MINT]]


st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
h1, h2, h3 {{ font-family: 'Fredoka', sans-serif !important; }}
.mono {{ font-family: 'JetBrains Mono', monospace !important; }}

#MainMenu, footer {{ visibility: hidden; }}
/* Keep the header itself around — it's what hosts the ">" arrow used to
   reopen the sidebar once it's been collapsed — but hide the toolbar
   (menu/deploy button) and make its background transparent. Streamlit has
   used a couple of different testids for the reopen arrow across versions
   (`collapsedControl` in older releases, `stSidebarCollapsedControl` in
   newer ones) so both are targeted here, with high z-index so nothing else
   on the page (like the background blobs) can sit on top of it. */
header {{ background: transparent !important; }}
header [data-testid="stToolbar"] {{ visibility: hidden; }}
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {{
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
    position: relative !important;
    z-index: 999999 !important;
    pointer-events: auto !important;
}}
[data-testid="collapsedControl"] *,
[data-testid="stSidebarCollapsedControl"] * {{
    visibility: visible !important;
    opacity: 1 !important;
}}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg {{
    fill: {INK} !important; stroke: {INK} !important;
}}
.stApp {{ background: {CREAM}; }}
.block-container {{ padding-top: 1.4rem; max-width: 1200px; }}

@keyframes floaty {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
@keyframes pulseDot {{ 0%, 100% {{ transform: scale(1); opacity: 1; }} 50% {{ transform: scale(1.3); opacity: .65; }} }}
@media (prefers-reduced-motion: reduce) {{
    .hero-illustration {{ animation: none !important; }}
}}

/* --- ambient background blobs --- */
.bg-blob {{ position: fixed; border-radius: 50%; filter: blur(90px); pointer-events: none; z-index: -1; }}

/* --- hero --- */
.hero-card {{
    position: relative; z-index: 1;
    background: linear-gradient(135deg, {PAPER} 0%, {VIOLET_SOFT} 130%);
    border: 1px solid {BORDER}; border-radius: 26px;
    padding: 30px 36px; margin-bottom: 26px;
    display: flex; align-items: center; justify-content: space-between; gap: 24px; flex-wrap: wrap;
    box-shadow: 0 18px 46px -22px {SHADOW}CC;
}}
.hero-eyebrow {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; font-weight: 700;
    letter-spacing: 0.16em; text-transform: uppercase; color: {VIOLET};
    display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
}}
.hero-title {{ font-family: 'Fredoka', sans-serif; font-weight: 700; font-size: 2.2rem; color: {INK}; line-height: 1.08; }}
.hero-title span {{ color: {CORAL}; }}
.hero-sub {{ font-size: 0.94rem; color: {MUTED}; margin-top: 10px; max-width: 480px; line-height: 1.5; }}
.hero-illustration {{ position: relative; width: 210px; height: 150px; flex: none; animation: floaty 4.5s ease-in-out infinite; }}
@media (max-width: 900px) {{ .hero-illustration {{ display: none; }} }}

/* --- section headers --- */
.section-head {{ margin: 36px 0 16px 0; position: relative; z-index: 1; }}
.section-head-row {{ display: flex; align-items: center; gap: 12px; }}
.section-icon {{ width: 36px; height: 36px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex: none; }}
.section-eyebrow {{ font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 2px; }}
.section-title {{ font-family: 'Fredoka', sans-serif; font-weight: 600; font-size: 1.32rem; color: {INK}; }}
.section-caption {{ font-size: 0.86rem; color: {MUTED}; margin-top: 5px; margin-left: 48px; }}

/* --- KPI cards --- */
.kpi-card {{
    background: {PAPER}; border: 1px solid {BORDER}; border-radius: 20px;
    padding: 18px 20px; min-height: 108px; position: relative; overflow: hidden;
    box-shadow: 0 10px 26px -18px {SHADOW}CC; transition: transform .15s ease;
}}
.kpi-card:hover {{ transform: translateY(-3px); }}
.kpi-value {{ font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.9rem; color: {INK}; line-height: 1.1; }}
.kpi-label {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 0.7rem; letter-spacing: 0.07em; text-transform: uppercase; color: {MUTED}; margin-top: 8px; }}
.kpi-icon {{ position: absolute; top: 14px; right: 14px; width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }}

/* --- verdict banner --- */
.verdict {{
    position: relative; overflow: hidden; border-radius: 24px; padding: 26px 30px; margin: 6px 0 28px 0;
    background: linear-gradient(120deg, var(--vtint) 0%, {PAPER} 78%);
    border: 1px solid var(--vcolor); box-shadow: 0 18px 44px -26px var(--vcolor);
    display: flex; align-items: center; gap: 22px; flex-wrap: wrap;
}}
.verdict-face {{ flex: none; }}
.verdict-label {{ font-family: 'Fredoka', sans-serif; font-weight: 700; font-size: 1.55rem; color: {INK}; letter-spacing: 0.005em; }}
.verdict-sub {{ font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: {MUTED}; margin-top: 6px; }}
.verdict-pct {{ font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 2.6rem; color: var(--vcolor); margin-left: auto; }}
.confetti {{ position: absolute; border-radius: 50%; opacity: 0.55; }}

/* --- winners / losers panel --- */
.rank-panel {{ background: {PAPER}; border: 1px solid {BORDER}; border-radius: 20px; padding: 18px 20px; min-height: 200px; box-shadow: 0 10px 26px -18px {SHADOW}AA; }}
.rank-panel-title {{ font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }}
.rank-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px dashed {BORDER}; gap: 10px; }}
.rank-row:last-child {{ border-bottom: none; }}
.rank-left {{ display: flex; align-items: center; gap: 10px; }}
.rank-name {{ font-size: 0.88rem; color: {INK}; font-weight: 600; }}
.rank-meta {{ font-size: 0.72rem; color: {MUTED}; }}
.rank-pct {{ font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.98rem; flex: none; }}

/* --- segment cards / pills --- */
.pill {{ display: inline-block; padding: 4px 12px; border-radius: 999px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; margin-right: 8px; }}

/* --- live sim dots --- */
.pulse-dot {{ display: inline-block; width: 13px; height: 13px; border-radius: 50%; margin: 3px; box-shadow: 0 0 0 3px {CREAM}, 0 2px 6px -2px {SHADOW}CC; }}

/* --- buttons --- */
div.stButton > button {{
    border-radius: 999px !important; font-family: 'Fredoka', sans-serif !important; font-weight: 600 !important;
    padding: 0.6rem 1.7rem !important; border: none !important;
    background: linear-gradient(120deg, {VIOLET}, {PINK}) !important; color: #fff !important;
    box-shadow: 0 12px 26px -12px {VIOLET} !important; transition: transform .15s ease, box-shadow .15s ease !important;
}}
div.stButton > button:hover {{ transform: translateY(-2px); box-shadow: 0 16px 32px -12px {VIOLET} !important; }}
div.stButton > button:disabled {{ background: {BORDER} !important; color: {MUTED} !important; box-shadow: none !important; }}

/* --- inputs --- */
.stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {{
    border-radius: 16px !important; border: 1.5px solid {BORDER} !important; background: {PAPER} !important;
    color: {INK} !important;
}}
.stTextArea textarea::placeholder {{ color: {MUTED} !important; opacity: 1; }}
.stTextArea textarea:focus {{ border-color: {VIOLET} !important; box-shadow: 0 0 0 3px {VIOLET_SOFT} !important; }}

/* --- alerts / charts / expanders --- */
.stAlert {{ border-radius: 16px !important; }}
div[data-testid="stPlotlyChart"] {{ background: {PAPER}; border: 1px solid {BORDER}; border-radius: 20px; padding: 12px; box-shadow: 0 10px 26px -18px {SHADOW}AA; }}
div[data-testid="stExpander"] {{ border: 1px solid {BORDER} !important; border-radius: 16px !important; background: {PAPER} !important; margin-bottom: 10px; overflow: hidden; }}
/* --- sidebar --- */
section[data-testid="stSidebar"] {{
    background: {PAPER_TINT}; border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] > div {{ padding: 1.6rem 1.35rem 2rem; }}
section[data-testid="stSidebar"] h3 {{
    color: {INK} !important; font-size: 1.02rem !important; margin: 2px 0 14px 0 !important;
}}
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {{ color: {MUTED} !important; }}
section[data-testid="stSidebar"] hr {{ border-color: {BORDER}; margin: 22px 0; }}
section[data-testid="stSidebar"] .stSlider label {{ color: {INK} !important; font-size: 0.86rem !important; font-weight: 500; }}
section[data-testid="stSidebar"] [data-baseweb="slider"] > div > div {{ background: {BORDER} !important; }}
section[data-testid="stSidebar"] [data-baseweb="slider"] div[role="slider"] {{
    background: {VIOLET} !important; box-shadow: 0 0 0 4px {VIOLET}33 !important;
}}
section[data-testid="stSidebar"] div[data-testid="stTickBar"] {{ display: none; }}
section[data-testid="stSidebar"] div[role="radiogroup"] label {{
    background: {PAPER}; border: 1px solid {BORDER}; border-radius: 12px;
    padding: 9px 12px !important; margin-bottom: 7px; transition: border-color .15s ease;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{ border-color: {VIOLET}88; }}
section[data-testid="stSidebar"] div[role="radiogroup"] p {{ color: {INK} !important; font-size: 0.83rem !important; }}

/* --- empty state --- */
.empty-card {{ background: {PAPER}; border: 1.5px dashed {BORDER}; border-radius: 22px; padding: 44px 30px; text-align: center; margin-top: 12px; }}
.empty-title {{ font-family: 'Fredoka', sans-serif; font-weight: 600; font-size: 1.18rem; color: {INK}; margin-top: 16px; }}
.empty-sub {{ font-size: 0.9rem; color: {MUTED}; margin-top: 6px; }}

hr {{ border-color: {BORDER}; }}
</style>
""", unsafe_allow_html=True)

if "simulations" not in st.session_state:
    st.session_state.simulations = []
if "active_sim_index" not in st.session_state:
    st.session_state.active_sim_index = None


st.markdown(f"""
<div class="bg-blob" style="width:440px; height:440px; background:{VIOLET}; top:-190px; left:-150px; opacity:.16;"></div>
<div class="bg-blob" style="width:380px; height:380px; background:{MINT}; bottom:-170px; right:-130px; opacity:.14;"></div>
<div class="bg-blob" style="width:320px; height:320px; background:{SUN}; top:32%; right:-180px; opacity:.13;"></div>

<div class="hero-card">
  <div>
    <div class="hero-eyebrow">{logo_mark(20)} CIVIC SIMULATION LAB</div>
    <div class="hero-title">Policy Impact <span>Simulator</span></div>
    <div class="hero-sub">Describe a policy and watch a synthetic population react — support, sentiment,
      and group-by-group breakdowns, generated live. An exploratory thought experiment, not a forecast.</div>
  </div>
  <div class="hero-illustration">
    <div style="position:absolute; top:2px; left:2px;">{BUBBLE_CORAL}</div>
    <div style="position:absolute; top:-6px; right:0;">{BUBBLE_SUN}</div>
    <div style="position:absolute; bottom:20px; right:-10px;">{BUBBLE_SKY}</div>
    <div style="position:absolute; bottom:-6px; left:38px;">{logo_mark(130)}</div>
    <div style="position:absolute; top:44px; left:-4px;">{SPARK_VIOLET}</div>
    <div style="position:absolute; top:0px; left:150px;">{SPARK_PINK}</div>
  </div>
</div>
""", unsafe_allow_html=True)

if not GEMINI_API_KEY:
    st.error(
        "No Gemini API key found. Add `GEMINI_API_KEY=your_key` to the `.env` file "
        "in this folder (see `.env.example`), then restart the app."
    )


with st.sidebar:
    st.markdown(f'<div class="section-eyebrow" style="color:{VIOLET};">⚙ CONFIG</div>', unsafe_allow_html=True)
    st.markdown("### Simulation Settings")
    population_size = st.slider("Population size (simulated)", 1_000, 1_000_000, 50_000, step=1_000)
    max_segments = st.slider(
        "Segment detail (more = richer breakdown, slower)",
        6, 27, 15,
        help="The population is modeled as this many representative demographic segments, "
             "each getting one AI-generated reaction, weighted by population share.",
    )

    st.divider()
    if st.session_state.simulations:
        st.markdown(f'<div class="section-eyebrow" style="color:{PINK};">🕘 HISTORY</div>', unsafe_allow_html=True)
        st.markdown("### Past Runs")
        labels = [s["label"] for s in st.session_state.simulations]
        chosen = st.radio("View a run:", labels, index=len(labels) - 1, label_visibility="collapsed")
        st.session_state.active_sim_index = labels.index(chosen)


section("INPUT", "Define the Policy", "Pick an example to start fast, or write your own from scratch.",
        icon_fn=icon_search, accent=VIOLET)

col_input, col_example = st.columns([3, 1.2])
with col_example:
    example_choice = st.selectbox("Examples", list(EXAMPLE_POLICIES.keys()), label_visibility="collapsed")

with col_input:
    default_text = EXAMPLE_POLICIES.get(example_choice, "") if example_choice != list(EXAMPLE_POLICIES.keys())[0] else ""
    policy_text = st.text_area(
        "Describe the policy to simulate",
        value=default_text,
        height=100,
        placeholder="e.g. Remove the fuel subsidy, causing prices to rise ~30%...",
        label_visibility="collapsed",
    )

run_clicked = st.button("▶  Run Simulation", type="primary", disabled=not GEMINI_API_KEY)

if run_clicked:
    if not policy_text.strip():
        st.error("Please describe a policy to simulate.")
    else:
        segments = generate_population(population_size=population_size, max_segments=max_segments)
        segment_dicts = [s.to_dict() for s in segments]

        section("RUNNING", "Simulating Population Reactions",
                "Each segment gets its own AI-generated reaction, live.",
                icon_fn=icon_flask, accent=CORAL)
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        live_grid = st.empty()

        dots_html_parts = []

        def _progress(done, total, latest_result):
            progress_bar.progress(done / total)
            status_text.markdown(
                f'<span class="mono" style="font-size:0.85rem; color:{MUTED};">'
                f'{latest_result["label"]} → {latest_result["support_pct"]}% support '
                f'({latest_result["count"]:,} people)</span>',
                unsafe_allow_html=True,
            )
            color = support_color(latest_result["support_pct"])
            dots_html_parts.append(
                f'<span class="pulse-dot" style="background:{color};" title="{latest_result["label"]}: {latest_result["support_pct"]}%"></span>'
            )
            live_grid.markdown(f'<div>{"".join(dots_html_parts)}</div>', unsafe_allow_html=True)

        results = run_simulation(segment_dicts, policy_text, GEMINI_API_KEY, GEMINI_MODEL, progress_callback=_progress)

        progress_bar.empty()
        status_text.empty()
        live_grid.empty()

        failed_count = sum(1 for r in results if r.get("error"))
        if failed_count:
            first_err = next((r.get("error_message") for r in results if r.get("error")), "unknown error")
            st.error(
                f"{failed_count} of {len(results)} segments failed and fell back to a neutral 50% placeholder. "
                f"First error: `{first_err}`. Check your terminal for full logs, and verify "
                f"GEMINI_API_KEY / GEMINI_MODEL in `.env`."
            )

        aggregated = aggregate_results(results)
        label = f"#{len(st.session_state.simulations) + 1}: {policy_text[:40]}{'...' if len(policy_text) > 40 else ''}"
        st.session_state.simulations.append({
            "label": label, "policy_text": policy_text, "population_size": population_size,
            "results": results, "aggregated": aggregated,
        })
        st.session_state.active_sim_index = len(st.session_state.simulations) - 1
        st.rerun()

if st.session_state.active_sim_index is not None and st.session_state.simulations:
    sim = st.session_state.simulations[st.session_state.active_sim_index]
    agg = sim["aggregated"]
    seg_df = agg["segment_df"]
    support = agg["overall_support"]
    sentiment = agg["overall_sentiment"]

    section("RESULTS", "Simulation Report", "Here's how your synthetic population reacted.",
            icon_fn=icon_notes, accent=VIOLET)
    st.markdown(
        f'<div style="color:{MUTED}; font-size:0.92rem; margin-bottom:18px;">'
        f'<span class="mono" style="color:{INK}; font-weight:600;">POLICY —</span> {sim["policy_text"]}</div>',
        unsafe_allow_html=True,
    )


    if support >= 65:
        verdict, vcolor, mood = "STRONG SUPPORT", MINT, "happy"
    elif support >= 55:
        verdict, vcolor, mood = "LEANS SUPPORTIVE", MINT, "happy"
    elif support >= 45:
        verdict, vcolor, mood = "DEEPLY DIVIDED", SUN, "meh"
    elif support >= 35:
        verdict, vcolor, mood = "LEANS OPPOSED", ORANGE, "sad"
    else:
        verdict, vcolor, mood = "BACKLASH LIKELY", RED, "sad"

    sentiment_label = "Positive" if sentiment > 0.15 else ("Negative" if sentiment < -0.15 else "Mixed")

    confetti_html = ""
    if support >= 65:
        spots = [(10, "8%", 7, MINT), (18, "92%", 5, SUN), (70, "88%", 6, PINK), (74, "5%", 5, VIOLET)]
        confetti_html = "".join(
            f'<span class="confetti" style="top:{t}px; left:{l}; width:{s}px; height:{s}px; background:{c};"></span>'
            for t, l, s, c in spots
        )

    st.markdown(f"""<div class="verdict" style="--vcolor:{vcolor}; --vtint:{vcolor}1A;">
{confetti_html}
<div class="verdict-face">{mood_face(vcolor, mood, 64)}</div>
<div>
<div class="verdict-label">{verdict}</div>
<div class="verdict-sub">Weighted sentiment: {sentiment:+.2f} ({sentiment_label}) across {len(sim['results'])} segments</div>
</div>
<div class="verdict-pct">{support:.0f}%</div>
</div>""", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, f"{support:.0f}%", "Overall Support", vcolor, "%"),
        (k2, f"{sentiment:+.2f}", "Sentiment Index", SKY, "♡"),
        (k3, f"{agg['total_population']:,}", "Simulated Population", VIOLET, "◍"),
        (k4, f"{len(sim['results'])}", "Segments Modeled", PINK, "▦"),
    ]
    for col, value, label_txt, accent, glyph in kpis:
        with col:
            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-icon" style="background:{accent}1F; color:{accent};">'
                f'<span class="mono" style="font-weight:700; font-size:13px;">{glyph}</span></div>'
                f'<div class="kpi-value">{value}</div><div class="kpi-label">{label_txt}</div></div>',
                unsafe_allow_html=True,
            )

    section("POPULATION MAP", "The Simulated Society", "Block size = population share · color = support level.",
            icon_fn=icon_grid, accent=SKY)

    treemap_df = seg_df.copy()
    fig_tree = px.treemap(
        treemap_df,
        path=[px.Constant("Population"), "employment_status", "income_tier", "ethnicity"],
        values="count",
        color="support_pct",
        color_continuous_scale=SUPPORT_SCALE,
        range_color=[0, 100],
        hover_data={"count": True, "support_pct": True},
    )
    fig_tree.update_traces(
        textinfo="label+percent parent",
        marker=dict(line=dict(color=PAPER, width=3)),
        textfont=PLOTLY_FONT,
    )
    fig_tree.update_layout(
        height=420, margin=dict(t=8, b=8, l=8, r=8),
        paper_bgcolor=PAPER, plot_bgcolor=PAPER,
        font=PLOTLY_FONT,
        coloraxis_colorbar=dict(title=dict(text="Support %", font=PLOTLY_FONT), tickfont=PLOTLY_FONT),
    )
    st.plotly_chart(fig_tree, width="stretch")

    section("RANKINGS", "Supporters & Opposers", icon_fn=icon_trophy, accent=SUN)
    top3 = seg_df.sort_values("support_pct", ascending=False).head(3)
    bottom3 = seg_df.sort_values("support_pct", ascending=True).head(3)

    def rank_rows(df):
        rows = ""
        for _, row in df.iterrows():
            color = support_color(row["support_pct"])
            dots = INCOME_DOTS.get(row["income_tier"], "")
            rows += (
                f'<div class="rank-row">'
                f'<div class="rank-left">{persona_badge(row["employment_status"])}'
                f'<div><span class="rank-name">{row["label"]}</span><br>'
                f'<span class="rank-meta">{row["count"]:,} people · <span class="mono">{dots}</span></span></div></div>'
                f'<div class="rank-pct" style="color:{color};">{row["support_pct"]}%</div>'
                f'</div>'
            )
        return rows

    wcol, lcol = st.columns(2)
    with wcol:
        st.markdown(
            f'<div class="rank-panel" style="--accent:{MINT};">'
            f'<div class="rank-panel-title">{icon_trophy(MINT, 15)} MOST SUPPORTIVE</div>{rank_rows(top3)}</div>',
            unsafe_allow_html=True,
        )
    with lcol:
        st.markdown(
            f'<div class="rank-panel" style="--accent:{RED};">'
            f'<div class="rank-panel-title">{icon_cloud(RED, 15)} MOST OPPOSED</div>{rank_rows(bottom3)}</div>',
            unsafe_allow_html=True,
        )

    section("BREAKDOWN", "Support by Group", icon_fn=icon_bars, accent=MINT)

    def breakdown_chart(df, category_col, title):
        fig = px.bar(
            df, x=category_col, y="support_pct", title=title,
            color="support_pct",
            color_continuous_scale=SUPPORT_SCALE,
            range_color=[0, 100],
            text=df["support_pct"].round(0).astype(int).astype(str) + "%",
        )
        fig.update_traces(textfont=PLOTLY_FONT, marker_line_width=0)
        fig.update_layout(
            height=300, margin=dict(t=40, b=10, l=10, r=10),
            coloraxis_showscale=False, yaxis_title="Support %", xaxis_title="",
            paper_bgcolor=PAPER, plot_bgcolor=PAPER, font=PLOTLY_FONT,
            title_font=PLOTLY_TITLE_FONT,
        )
        fig.update_xaxes(gridcolor=BORDER)
        fig.update_yaxes(gridcolor=BORDER, range=[0, 100])
        return fig

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.plotly_chart(breakdown_chart(agg["by_income_tier"], "income_tier", "By Income Tier"), width="stretch")
    with b2:
        st.plotly_chart(breakdown_chart(agg["by_employment_status"], "employment_status", "By Employment"), width="stretch")
    with b3:
        st.plotly_chart(breakdown_chart(agg["by_ethnicity"], "ethnicity", "By Ethnicity"), width="stretch")
    with b4:
        fig_hist = px.histogram(seg_df, x="sentiment_score", nbins=10, title="Sentiment Spread", color_discrete_sequence=[SKY])
        fig_hist.update_layout(
            height=300, margin=dict(t=40, b=10, l=10, r=10),
            xaxis_title="Sentiment", yaxis_title="Segments",
            paper_bgcolor=PAPER, plot_bgcolor=PAPER, font=PLOTLY_FONT,
            title_font=PLOTLY_TITLE_FONT,
        )
        fig_hist.update_xaxes(gridcolor=BORDER)
        fig_hist.update_yaxes(gridcolor=BORDER)
        st.plotly_chart(fig_hist, width="stretch")

    # --- Segment detail ---
    section("DETAIL", "Segment-by-Segment",
            "Each card is one representative slice of the population, weighted by its share of the total.",
            icon_fn=icon_notes, accent=PINK)

    for _, row in seg_df.iterrows():
        color = support_color(row["support_pct"])
        emoji = EMPLOYMENT_EMOJI.get(row["employment_status"], "🔹")
        with st.expander(
            f"{row['label']}   ·   {row['support_pct']}% support   ·   {row['count']:,} people ({row['weight'] * 100:.1f}%)",
            icon=emoji,
        ):
            st.markdown(
                f'<span class="pill" style="background:{color}22; color:{color};">{row["support_pct"]}% SUPPORT</span>'
                f'<span class="pill" style="background:{SKY}22; color:{SKY};">SENTIMENT {row["sentiment_score"]:+.2f}</span>',
                unsafe_allow_html=True,
            )
            quote = row.get("quote", "")
            if quote:
                st.markdown(
                    f'<div style="font-family:\'Fredoka\',sans-serif; font-size:1.02rem; color:{INK}; '
                    f'font-style:italic; border-left:3px solid {color}; padding:2px 0 2px 14px; margin:12px 0;">'
                    f'“{quote}”</div>',
                    unsafe_allow_html=True,
                )
            st.write(row.get("rationale", ""))
            cbc1, cbc2 = st.columns(2)
            with cbc1:
                st.markdown(f'<span class="mono" style="font-size:0.75rem; color:{MINT}; font-weight:700;">BENEFITS PERCEIVED</span>', unsafe_allow_html=True)
                for b in row.get("key_benefits", []) or []:
                    st.markdown(f'<div style="margin:5px 0; color:{INK};"><span style="color:{MINT};">●</span>&nbsp; {b}</div>', unsafe_allow_html=True)
            with cbc2:
                st.markdown(f'<span class="mono" style="font-size:0.75rem; color:{RED}; font-weight:700;">CONCERNS RAISED</span>', unsafe_allow_html=True)
                for c in row.get("key_concerns", []) or []:
                    st.markdown(f'<div style="margin:5px 0; color:{INK};"><span style="color:{RED};">●</span>&nbsp; {c}</div>', unsafe_allow_html=True)
else:
    st.markdown(f"""<div class="empty-card">
{logo_mark(84)}
<div class="empty-title">Ready when you are</div>
<div class="empty-sub">Describe a policy above and hit <b>Run Simulation</b> to see how your synthetic population reacts.</div>
</div>""", unsafe_allow_html=True)
