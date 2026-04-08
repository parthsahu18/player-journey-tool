import streamlit as st
import pandas as pd
import pyarrow.parquet as pq
import os
import plotly.graph_objects as go
from PIL import Image
import numpy as np

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Player Journey Tool",
    layout="wide",
    page_icon="🎮",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

/* ── ROOT VARIABLES ── */
:root {
    --bg-primary:    #080c14;
    --bg-secondary:  #0d1321;
    --bg-card:       #111827;
    --bg-card2:      #0f1c2e;
    --accent-cyan:   #00d4ff;
    --accent-green:  #00ff9d;
    --accent-orange: #ff7b00;
    --accent-purple: #9b5de5;
    --accent-red:    #ff3860;
    --text-primary:  #e8eaf0;
    --text-muted:    #6b7a99;
    --border:        rgba(0, 212, 255, 0.15);
    --glow-cyan:     0 0 20px rgba(0, 212, 255, 0.3);
    --glow-green:    0 0 20px rgba(0, 255, 157, 0.3);
}

/* ── GLOBAL RESET ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    font-family: 'Exo 2', sans-serif !important;
    color: var(--text-primary) !important;
}

[data-testid="stAppViewContainer"] {
    background-image:
        radial-gradient(ellipse at 10% 20%, rgba(0,212,255,0.04) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(0,255,157,0.03) 0%, transparent 50%);
}

/* ── HEADER ── */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div {
    background: transparent !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: var(--text-primary) !important;
    font-family: 'Exo 2', sans-serif !important;
}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
    font-family: 'Share Tech Mono', monospace !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--accent-cyan) !important;
    box-shadow: var(--glow-cyan) !important;
}

/* ── RADIO ── */
[data-testid="stRadio"] > div {
    gap: 8px !important;
}
[data-testid="stRadio"] label {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    padding: 6px 14px !important;
    transition: all 0.2s ease !important;
    color: var(--text-muted) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 500 !important;
}
[data-testid="stRadio"] label:hover {
    border-color: var(--accent-cyan) !important;
    color: var(--accent-cyan) !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] p {
    color: var(--accent-cyan) !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── SUCCESS / WARNING ALERTS ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border: none !important;
}
.stSuccess {
    background: rgba(0, 255, 157, 0.08) !important;
    border-left: 3px solid var(--accent-green) !important;
    color: var(--accent-green) !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.stWarning {
    background: rgba(255, 123, 0, 0.08) !important;
    border-left: 3px solid var(--accent-orange) !important;
}

/* ── TABS ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--bg-secondary) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 4px !important;
    padding: 0 4px !important;
    border-radius: 8px 8px 0 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 10px 22px !important;
    border-radius: 6px 6px 0 0 !important;
    border: none !important;
    transition: all 0.25s ease !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: var(--accent-cyan) !important;
    background: rgba(0, 212, 255, 0.06) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(0, 212, 255, 0.1) !important;
    color: var(--accent-cyan) !important;
    border-bottom: 2px solid var(--accent-cyan) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 20px !important;
}

/* ── METRIC CARDS ── */
[data-testid="stMetric"] {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 16px 20px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--glow-cyan) !important;
    border-color: rgba(0, 212, 255, 0.4) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 11px !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: var(--accent-cyan) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 28px !important;
}

/* ── SLIDER ── */
[data-testid="stSlider"] > div > div > div {
    background: var(--accent-cyan) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: var(--accent-cyan) !important;
    border-color: var(--accent-cyan) !important;
    box-shadow: var(--glow-cyan) !important;
}
[data-testid="stSlider"] p {
    color: var(--text-primary) !important;
    font-family: 'Exo 2', sans-serif !important;
}

/* ── SUBHEADERS / TEXT ── */
h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 0.05em !important;
}
.stMarkdown p {
    color: var(--text-primary) !important;
    font-family: 'Exo 2', sans-serif !important;
}

/* ── PLOTLY CONTAINER ── */
[data-testid="stPlotlyChart"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 4px 30px rgba(0,0,0,0.5) !important;
    transition: box-shadow 0.3s ease !important;
}
[data-testid="stPlotlyChart"]:hover {
    box-shadow: 0 4px 40px rgba(0, 212, 255, 0.15) !important;
}

/* ── WRITE / CODE TEXT ── */
[data-testid="stText"] {
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--text-muted) !important;
    font-size: 12px !important;
}

/* ── DIVIDER ── */
hr {
    border-color: var(--border) !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: rgba(0, 212, 255, 0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 212, 255, 0.6); }
</style>
""", unsafe_allow_html=True)

# ─── HEADER BANNER ────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0d1321 0%, #111827 50%, #0f1c2e 100%);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(ellipse at 0% 50%, rgba(0,212,255,0.07) 0%, transparent 60%),
                    radial-gradient(ellipse at 100% 50%, rgba(0,255,157,0.05) 0%, transparent 60%);
        pointer-events: none;
    "></div>
    <div style="display:flex; align-items:center; gap: 16px; position:relative;">
        <div style="
            font-size: 40px;
            filter: drop-shadow(0 0 12px rgba(0,212,255,0.6));
        ">🎮</div>
        <div>
            <div style="
                font-family: 'Rajdhani', sans-serif;
                font-size: 32px;
                font-weight: 700;
                color: #e8eaf0;
                letter-spacing: 0.08em;
                line-height: 1;
                text-transform: uppercase;
            ">Player Journey <span style="color: #00d4ff;">Visualization</span> Tool</div>
            <div style="
                font-family: 'Share Tech Mono', monospace;
                font-size: 12px;
                color: #6b7a99;
                margin-top: 6px;
                letter-spacing: 0.1em;
            ">// MATCH ANALYTICS  ·  MOVEMENT TRACKING  ·  HEATMAP INTELLIGENCE</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}

MAP_IMAGES = {
    "AmbroseValley": "assets/AmbroseValley_Minimap.png",
    "GrandRift":     "assets/GrandRift_Minimap.png",
    "Lockdown":      "assets/Lockdown_Minimap.jpg",
}

PLOTLY_DARK = dict(
    paper_bgcolor="rgba(8,12,20,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Share Tech Mono, monospace", color="#e8eaf0"),
    legend=dict(
        bgcolor="rgba(13,19,33,0.9)",
        bordercolor="rgba(0,212,255,0.2)",
        borderwidth=1,
        font=dict(family="Exo 2, sans-serif", size=12, color="#e8eaf0")
    ),
    margin=dict(l=0, r=0, t=0, b=0),
)

AXIS_STYLE = dict(showgrid=False, zeroline=False, showticklabels=False)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def world_to_pixel(x, z, map_name):
    config = MAP_CONFIG[map_name]
    u = (x - config["origin_x"]) / config["scale"]
    v = (z - config["origin_z"]) / config["scale"]
    return u * 1024, (1 - v) * 1024

@st.cache_data
def load_all_data():
    all_frames = []
    base = "sample_data"
    for day_folder in os.listdir(base):
        day_path = os.path.join(base, day_folder)
        if not os.path.isdir(day_path):
            continue
        for fname in os.listdir(day_path):
            fpath = os.path.join(day_path, fname)
            try:
                df = pq.read_table(fpath).to_pandas()
                df['event'] = df['event'].apply(
                    lambda x: x.decode('utf-8') if isinstance(x, bytes) else x
                )
                df['date'] = day_folder
                df['filename'] = fname
                df['is_bot'] = df['user_id'].apply(lambda x: str(x).isdigit())
                all_frames.append(df)
            except:
                continue
    return pd.concat(all_frames, ignore_index=True)

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
with st.spinner("⚡ Initializing data streams..."):
    df_all = load_all_data()

n_events  = len(df_all)
n_files   = df_all['filename'].nunique()
n_matches = df_all['match_id'].nunique() if 'match_id' in df_all.columns else 0
n_players = df_all['user_id'].nunique() if 'user_id' in df_all.columns else 0

st.markdown(f"""
<div style="
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 20px;
">
    {"".join([
        f'''<div style="
            background: linear-gradient(135deg, #111827, #0f1c2e);
            border: 1px solid rgba(0,212,255,0.15);
            border-radius: 10px;
            padding: 14px 18px;
            text-align: center;
            transition: all 0.3s;
        ">
            <div style="font-family:'Share Tech Mono',monospace; font-size:24px; color:{color}; font-weight:700;">{val}</div>
            <div style="font-family:'Rajdhani',sans-serif; font-size:11px; letter-spacing:0.12em; color:#6b7a99; text-transform:uppercase; margin-top:4px;">{label}</div>
        </div>'''
        for val, label, color in [
            (f"{n_events:,}", "Total Events", "#00d4ff"),
            (f"{n_files:,}",  "Data Files",   "#00ff9d"),
            (f"{n_matches:,}","Matches",       "#ff7b00"),
            (f"{n_players:,}","Players",       "#9b5de5"),
        ]
    ])}
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="
    font-family: 'Rajdhani', sans-serif;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #00d4ff;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(0,212,255,0.2);
    padding-bottom: 10px;
    margin-bottom: 16px;
">⚙ Filters</div>
""", unsafe_allow_html=True)

maps = sorted(df_all['map_id'].dropna().unique().tolist())
selected_map = st.sidebar.selectbox("🗺 Map", maps)

dates = sorted(df_all['date'].unique().tolist())
selected_date = st.sidebar.selectbox("📅 Date", dates)

player_type = st.sidebar.radio("👤 Player Type", ["All", "Humans Only", "Bots Only"])

filtered = df_all[
    (df_all['map_id'] == selected_map) &
    (df_all['date'] == selected_date)
]

if player_type == "Humans Only":
    filtered = filtered[filtered['is_bot'] == False]
elif player_type == "Bots Only":
    filtered = filtered[filtered['is_bot'] == True]

matches = sorted(filtered['match_id'].dropna().unique().tolist())
selected_match = st.sidebar.selectbox("🎯 Match", matches)
filtered = filtered[filtered['match_id'] == selected_match]

st.sidebar.markdown(f"""
<div style="
    margin-top: 16px;
    background: rgba(0,212,255,0.06);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 8px;
    padding: 12px 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #6b7a99;
">
    <span style="color:#00d4ff;">EVENTS LOADED</span><br/>
    <span style="font-size:22px; color:#e8eaf0; font-weight:700;">{len(filtered):,}</span>
</div>
""", unsafe_allow_html=True)

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
if len(filtered) > 0:
    filtered = filtered.copy()
    filtered['pixel_x'], filtered['pixel_y'] = zip(*filtered.apply(
        lambda row: world_to_pixel(row['x'], row['z'], selected_map), axis=1
    ))

    positions = filtered[filtered['event'].isin(['Position', 'BotPosition'])]
    kills     = filtered[filtered['event'].isin(['Kill', 'BotKill'])]
    deaths    = filtered[filtered['event'].isin(['Killed', 'BotKilled'])]
    storms    = filtered[filtered['event'] == 'KilledByStorm']
    loots     = filtered[filtered['event'] == 'Loot']

    tab1, tab2, tab3 = st.tabs(["🗺  Journey Map", "⏱  Timeline", "🔥  Heatmap"])

    # ── TAB 1: JOURNEY MAP ────────────────────────────────────────────────────
    with tab1:
        st.markdown("""
        <div style="font-family:'Rajdhani',sans-serif; font-size:20px; font-weight:700;
             color:#00d4ff; letter-spacing:0.08em; text-transform:uppercase;
             margin-bottom:16px; display:flex; align-items:center; gap:8px;">
            <span style="width:3px;height:20px;background:#00d4ff;display:inline-block;border-radius:2px;"></span>
            Player Movement Map
        </div>
        """, unsafe_allow_html=True)

        img = Image.open(MAP_IMAGES[selected_map])
        fig = go.Figure()
        fig.add_layout_image(dict(
            source=img, xref="x", yref="y",
            x=0, y=0, sizex=1024, sizey=1024,
            sizing="stretch", opacity=0.85, layer="below"
        ))

        humans_pos = positions[positions['is_bot'] == False]
        bots_pos   = positions[positions['is_bot'] == True]

        if len(humans_pos) > 0:
            fig.add_trace(go.Scatter(
                x=humans_pos['pixel_x'], y=humans_pos['pixel_y'],
                mode='lines', name='Human Path',
                line=dict(color='#00d4ff', width=2),
                opacity=0.7
            ))
        if len(bots_pos) > 0:
            fig.add_trace(go.Scatter(
                x=bots_pos['pixel_x'], y=bots_pos['pixel_y'],
                mode='lines', name='Bot Path',
                line=dict(color='#ff7b00', width=1.5),
                opacity=0.5
            ))
        if len(loots) > 0:
            fig.add_trace(go.Scatter(
                x=loots['pixel_x'], y=loots['pixel_y'],
                mode='markers', name='Loot',
                marker=dict(color='#ffe066', size=11, symbol='circle',
                            line=dict(color='#fff', width=1)),
            ))
        if len(deaths) > 0:
            fig.add_trace(go.Scatter(
                x=deaths['pixel_x'], y=deaths['pixel_y'],
                mode='markers', name='Death',
                marker=dict(color='#ff3860', size=13, symbol='x',
                            line=dict(color='#ff3860', width=2)),
            ))
        if len(kills) > 0:
            fig.add_trace(go.Scatter(
                x=kills['pixel_x'], y=kills['pixel_y'],
                mode='markers', name='Kill',
                marker=dict(color='#00ff9d', size=12, symbol='star',
                            line=dict(color='#fff', width=1)),
            ))
        if len(storms) > 0:
            fig.add_trace(go.Scatter(
                x=storms['pixel_x'], y=storms['pixel_y'],
                mode='markers', name='Storm Death',
                marker=dict(color='#9b5de5', size=13, symbol='diamond',
                            line=dict(color='#fff', width=1)),
            ))

        fig.update_layout(
            **PLOTLY_DARK,
            xaxis=dict(range=[0, 1024], **AXIS_STYLE),
            yaxis=dict(range=[1024, 0], **AXIS_STYLE),
            width=720, height=720,
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⚡ Total Events", f"{len(filtered):,}")
        col2.metric("☠ Kills",         f"{len(kills):,}")
        col3.metric("💀 Deaths",        f"{len(deaths):,}")
        col4.metric("📦 Loots",         f"{len(loots):,}")

    # ── TAB 2: TIMELINE ───────────────────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div style="font-family:'Rajdhani',sans-serif; font-size:20px; font-weight:700;
             color:#00ff9d; letter-spacing:0.08em; text-transform:uppercase;
             margin-bottom:16px; display:flex; align-items:center; gap:8px;">
            <span style="width:3px;height:20px;background:#00ff9d;display:inline-block;border-radius:2px;"></span>
            Match Timeline Replay
        </div>
        """, unsafe_allow_html=True)

        sorted_df = filtered.sort_values('ts').copy()
        try:
            sorted_df['ts_seconds'] = (
                sorted_df['ts'] - sorted_df['ts'].min()
            ).dt.total_seconds()
        except:
            sorted_df['ts_seconds'] = range(len(sorted_df))

        sorted_df['ts_seconds'] = sorted_df['ts_seconds'].fillna(0)
        max_time = max(int(sorted_df['ts_seconds'].max()), 1)

        st.markdown(f"""
        <div style="font-family:'Share Tech Mono',monospace; font-size:12px; color:#6b7a99;
             margin-bottom:12px;">
            MATCH DURATION: <span style="color:#00ff9d;">{max_time}s</span>
            &nbsp;·&nbsp;
            TOTAL EVENTS: <span style="color:#00d4ff;">{len(sorted_df):,}</span>
        </div>
        """, unsafe_allow_html=True)

        time_slider = st.slider(
            "⏱ Scrub Match Time (seconds)",
            min_value=0, max_value=max_time,
            value=max_time,
            step=max(1, max_time // 100)
        )

        timeline_df     = sorted_df[sorted_df['ts_seconds'] <= time_slider]
        timeline_pos    = timeline_df[timeline_df['event'].isin(['Position', 'BotPosition'])]
        timeline_events = timeline_df[~timeline_df['event'].isin(['Position', 'BotPosition'])]

        img2 = Image.open(MAP_IMAGES[selected_map])
        fig2 = go.Figure()
        fig2.add_layout_image(dict(
            source=img2, xref="x", yref="y",
            x=0, y=0, sizex=1024, sizey=1024,
            sizing="stretch", opacity=0.85, layer="below"
        ))

        if len(timeline_pos) > 0:
            fig2.add_trace(go.Scatter(
                x=timeline_pos['pixel_x'], y=timeline_pos['pixel_y'],
                mode='lines+markers', name='Path',
                line=dict(color='#00d4ff', width=2),
                marker=dict(size=3, color='#00d4ff')
            ))

        EVENT_STYLES = {
            'Kill':          dict(color='#00ff9d', size=12, symbol='star'),
            'BotKill':       dict(color='#7bffcf', size=10, symbol='star'),
            'Killed':        dict(color='#ff3860', size=13, symbol='x'),
            'BotKilled':     dict(color='#ff7b00', size=11, symbol='x'),
            'KilledByStorm': dict(color='#9b5de5', size=13, symbol='diamond'),
            'Loot':          dict(color='#ffe066', size=10, symbol='circle'),
        }
        for event_type, style in EVENT_STYLES.items():
            ev = timeline_events[timeline_events['event'] == event_type]
            if len(ev) > 0:
                fig2.add_trace(go.Scatter(
                    x=ev['pixel_x'], y=ev['pixel_y'],
                    mode='markers', name=event_type,
                    marker=dict(**style, line=dict(color='rgba(255,255,255,0.4)', width=1))
                ))

        # Progress bar overlay
        pct = int((time_slider / max_time) * 100)
        st.markdown(f"""
        <div style="margin: 0 0 12px; font-family:'Share Tech Mono',monospace; font-size:11px; color:#6b7a99;">
            REPLAY PROGRESS
            <div style="background:rgba(255,255,255,0.07); border-radius:4px; height:6px; margin-top:6px; overflow:hidden;">
                <div style="background:linear-gradient(90deg,#00d4ff,#00ff9d); width:{pct}%; height:100%;
                     border-radius:4px; transition:width 0.3s ease;"></div>
            </div>
            <span style="color:#00d4ff;">{time_slider}s</span> / {max_time}s &nbsp;·&nbsp;
            <span style="color:#00ff9d;">{len(timeline_df):,} events shown</span>
        </div>
        """, unsafe_allow_html=True)

        fig2.update_layout(
            **PLOTLY_DARK,
            xaxis=dict(range=[0, 1024], **AXIS_STYLE),
            yaxis=dict(range=[1024, 0], **AXIS_STYLE),
            width=720, height=720,
            showlegend=True,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── TAB 3: HEATMAP ────────────────────────────────────────────────────────
    with tab3:
        st.markdown("""
        <div style="font-family:'Rajdhani',sans-serif; font-size:20px; font-weight:700;
             color:#ff7b00; letter-spacing:0.08em; text-transform:uppercase;
             margin-bottom:16px; display:flex; align-items:center; gap:8px;">
            <span style="width:3px;height:20px;background:#ff7b00;display:inline-block;border-radius:2px;"></span>
            Zone Intelligence Heatmap
        </div>
        """, unsafe_allow_html=True)

        HEATMAP_OPTIONS = {
            "🌐 All Traffic":   positions,
            "⚔ Kill Zones":    kills,
            "💀 Death Zones":   deaths,
            "🌩 Storm Deaths":  storms,
            "📦 Loot Zones":    loots,
        }

        heatmap_type = st.selectbox("Select Analysis Layer", list(HEATMAP_OPTIONS.keys()))
        hmap_df = HEATMAP_OPTIONS[heatmap_type]

        COLORSCALES = {
            "🌐 All Traffic":  "Blues",
            "⚔ Kill Zones":   "Greens",
            "💀 Death Zones":  "Reds",
            "🌩 Storm Deaths": "Purples",
            "📦 Loot Zones":   "YlOrBr",
        }

        img3 = Image.open(MAP_IMAGES[selected_map])
        fig3 = go.Figure()
        fig3.add_layout_image(dict(
            source=img3, xref="x", yref="y",
            x=0, y=0, sizex=1024, sizey=1024,
            sizing="stretch", opacity=0.75, layer="below"
        ))

        if len(hmap_df) > 0:
            fig3.add_trace(go.Histogram2dContour(
                x=hmap_df['pixel_x'],
                y=hmap_df['pixel_y'],
                colorscale=COLORSCALES[heatmap_type],
                reversescale=False,
                opacity=0.65,
                showscale=True,
                contours=dict(showlines=False),
                name=heatmap_type,
                colorbar=dict(
                    thickness=12,
                    len=0.6,
                    bgcolor="rgba(8,12,20,0.8)",
                    bordercolor="rgba(0,212,255,0.2)",
                    borderwidth=1,
                    tickfont=dict(family="Share Tech Mono", color="#e8eaf0", size=10)
                )
            ))

        st.markdown(f"""
        <div style="font-family:'Share Tech Mono',monospace; font-size:12px; color:#6b7a99; margin-bottom:10px;">
            LAYER: <span style="color:#ff7b00;">{heatmap_type}</span>
            &nbsp;·&nbsp;
            DATA POINTS: <span style="color:#00d4ff;">{len(hmap_df):,}</span>
        </div>
        """, unsafe_allow_html=True)

        fig3.update_layout(
            **PLOTLY_DARK,
            xaxis=dict(range=[0, 1024], **AXIS_STYLE),
            yaxis=dict(range=[1024, 0], **AXIS_STYLE),
            width=720, height=720,
        )
        st.plotly_chart(fig3, use_container_width=True)

else:
    st.markdown("""
    <div style="
        background: rgba(255,123,0,0.07);
        border: 1px solid rgba(255,123,0,0.3);
        border-radius: 10px;
        padding: 24px 28px;
        text-align: center;
        font-family: 'Rajdhani', sans-serif;
        font-size: 18px;
        color: #ff7b00;
        letter-spacing: 0.05em;
    ">
        ⚠ No data found for the selected filters — try adjusting map, date, or player type.
    </div>
    """, unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    margin-top: 40px;
    border-top: 1px solid rgba(0,212,255,0.1);
    padding-top: 16px;
    text-align: center;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #2e3a50;
    letter-spacing: 0.1em;
">
    PLAYER JOURNEY TOOL &nbsp;·&nbsp; GAME ANALYTICS PLATFORM &nbsp;·&nbsp; BUILT WITH STREAMLIT + PLOTLY
</div>
""", unsafe_allow_html=True)
