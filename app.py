import streamlit as st
import pandas as pd
import pyarrow.parquet as pq
import os
import plotly.graph_objects as go
from PIL import Image
import numpy as np

st.set_page_config(page_title="Player Journey Tool", layout="wide")
st.title("Player Journey Visualization Tool")

# ─────────────────────────────────────
# MAP CONFIGURATION
# ─────────────────────────────────────

MAP_CONFIG = {
    "AmbroseValley": {"scale": 900, "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581, "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}

MAP_IMAGES = {
    "AmbroseValley": "assets/AmbroseValley_Minimap.png",
    "GrandRift":     "assets/GrandRift_Minimap.png",
    "Lockdown":      "assets/Lockdown_Minimap.jpg",
}

# ─────────────────────────────────────
# COORDINATE CONVERSION
# ─────────────────────────────────────

def world_to_pixel(x, z, map_name):
    config = MAP_CONFIG[map_name]
    u = (x - config["origin_x"]) / config["scale"]
    v = (z - config["origin_z"]) / config["scale"]
    pixel_x = u * 1024
    pixel_y = (1 - v) * 1024
    return pixel_x, pixel_y

# ─────────────────────────────────────
# LOAD ALL DATA
# ─────────────────────────────────────

@st.cache_data
def load_all_data():
    all_frames = []
    base = "sample_data""
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
                df['is_bot'] = df['user_id'].apply(
                    lambda x: str(x).isdigit()
                )
                all_frames.append(df)
            except:
                continue
    return pd.concat(all_frames, ignore_index=True)

with st.spinner("Loading all game data... please wait..."):
    df_all = load_all_data()

st.success(f"Loaded {len(df_all):,} events from {df_all['filename'].nunique()} files!")

# ─────────────────────────────────────
# FILTERS IN SIDEBAR
# ─────────────────────────────────────

st.sidebar.title("Filters")

# Map filter
maps = sorted(df_all['map_id'].dropna().unique().tolist())
selected_map = st.sidebar.selectbox("Select Map", maps)

# Date filter
dates = sorted(df_all['date'].unique().tolist())
selected_date = st.sidebar.selectbox("Select Date", dates)

# Player type filter
player_type = st.sidebar.radio(
    "Player Type",
    ["All", "Humans Only", "Bots Only"]
)

# Filter data by map and date
filtered = df_all[
    (df_all['map_id'] == selected_map) &
    (df_all['date'] == selected_date)
]

# Filter by player type
if player_type == "Humans Only":
    filtered = filtered[filtered['is_bot'] == False]
elif player_type == "Bots Only":
    filtered = filtered[filtered['is_bot'] == True]

# Match filter
matches = sorted(filtered['match_id'].dropna().unique().tolist())
selected_match = st.sidebar.selectbox("Select Match", matches)

# Filter by match
filtered = filtered[filtered['match_id'] == selected_match]

st.sidebar.write(f"Events in this match: {len(filtered):,}")

# ─────────────────────────────────────
# CONVERT COORDINATES
# ─────────────────────────────────────

if len(filtered) > 0:
    filtered = filtered.copy()
    filtered['pixel_x'], filtered['pixel_y'] = zip(*filtered.apply(
        lambda row: world_to_pixel(row['x'], row['z'], selected_map), axis=1
    ))

    # Separate events
    positions = filtered[filtered['event'].isin(['Position', 'BotPosition'])]
    kills     = filtered[filtered['event'].isin(['Kill', 'BotKill'])]
    deaths    = filtered[filtered['event'].isin(['Killed', 'BotKilled'])]
    storms    = filtered[filtered['event'] == 'KilledByStorm']
    loots     = filtered[filtered['event'] == 'Loot']

    # ─────────────────────────────────────
    # TABS
    # ─────────────────────────────────────

    tab1, tab2, tab3 = st.tabs(["Player Journey Map", "Timeline", "Heatmap"])

    # ─────────────────────────────────────
    # TAB 1 — PLAYER JOURNEY MAP
    # ─────────────────────────────────────

    with tab1:
        st.subheader("Player Journey Map")

        img = Image.open(MAP_IMAGES[selected_map])
        fig = go.Figure()

        fig.add_layout_image(
            dict(
                source=img,
                xref="x", yref="y",
                x=0, y=0,
                sizex=1024, sizey=1024,
                sizing="stretch",
                opacity=1,
                layer="below"
            )
        )

        # Movement paths - different color for bots vs humans
        humans_pos = positions[positions['is_bot'] == False]
        bots_pos   = positions[positions['is_bot'] == True]

        if len(humans_pos) > 0:
            fig.add_trace(go.Scatter(
                x=humans_pos['pixel_x'],
                y=humans_pos['pixel_y'],
                mode='lines',
                name='Human Path',
                line=dict(color='blue', width=2),
                opacity=0.6
            ))

        if len(bots_pos) > 0:
            fig.add_trace(go.Scatter(
                x=bots_pos['pixel_x'],
                y=bots_pos['pixel_y'],
                mode='lines',
                name='Bot Path',
                line=dict(color='orange', width=1),
                opacity=0.4
            ))

        if len(loots) > 0:
            fig.add_trace(go.Scatter(
                x=loots['pixel_x'],
                y=loots['pixel_y'],
                mode='markers',
                name='Loot',
                marker=dict(color='yellow', size=10, symbol='circle')
            ))

        if len(deaths) > 0:
            fig.add_trace(go.Scatter(
                x=deaths['pixel_x'],
                y=deaths['pixel_y'],
                mode='markers',
                name='Death',
                marker=dict(color='red', size=12, symbol='x')
            ))

        if len(kills) > 0:
            fig.add_trace(go.Scatter(
                x=kills['pixel_x'],
                y=kills['pixel_y'],
                mode='markers',
                name='Kill',
                marker=dict(color='green', size=10, symbol='star')
            ))

        if len(storms) > 0:
            fig.add_trace(go.Scatter(
                x=storms['pixel_x'],
                y=storms['pixel_y'],
                mode='markers',
                name='Storm Death',
                marker=dict(color='purple', size=12, symbol='diamond')
            ))

        fig.update_layout(
            xaxis=dict(range=[0, 1024], showgrid=False, zeroline=False),
            yaxis=dict(range=[1024, 0], showgrid=False, zeroline=False),
            width=700, height=700,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True
        )

        st.plotly_chart(fig)

        # Stats below map
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Events", len(filtered))
        col2.metric("Kills", len(kills))
        col3.metric("Deaths", len(deaths))
        col4.metric("Loots", len(loots))

    # ─────────────────────────────────────
    # TAB 2 — TIMELINE
    # ─────────────────────────────────────

    with tab2:
        st.subheader("Match Timeline")

        sorted_df = filtered.sort_values('ts')
        sorted_df['ts_seconds'] = (
            sorted_df['ts'] - sorted_df['ts'].min()
        ).dt.total_seconds()

        max_time =max(int(sorted_df['ts_seconds'].max()), 1)

        time_slider = st.slider(
            "Match Time (seconds)",
            min_value=0,
            max_value=max_time,
            value=max_time,
            step=10
        )

        timeline_df = sorted_df[sorted_df['ts_seconds'] <= time_slider]
        timeline_pos = timeline_df[timeline_df['event'].isin(['Position', 'BotPosition'])]
        timeline_events = timeline_df[~timeline_df['event'].isin(['Position', 'BotPosition'])]

        img2 = Image.open(MAP_IMAGES[selected_map])
        fig2 = go.Figure()

        fig2.add_layout_image(
            dict(
                source=img2,
                xref="x", yref="y",
                x=0, y=0,
                sizex=1024, sizey=1024,
                sizing="stretch",
                opacity=1,
                layer="below"
            )
        )

        if len(timeline_pos) > 0:
            fig2.add_trace(go.Scatter(
                x=timeline_pos['pixel_x'],
                y=timeline_pos['pixel_y'],
                mode='lines+markers',
                name='Path so far',
                line=dict(color='blue', width=2),
                marker=dict(size=4)
            ))

        if len(timeline_events) > 0:
            colors = {
                'Kill': 'green', 'BotKill': 'lightgreen',
                'Killed': 'red', 'BotKilled': 'orange',
                'KilledByStorm': 'purple', 'Loot': 'yellow'
            }
            for event_type, color in colors.items():
                ev = timeline_events[timeline_events['event'] == event_type]
                if len(ev) > 0:
                    fig2.add_trace(go.Scatter(
                        x=ev['pixel_x'],
                        y=ev['pixel_y'],
                        mode='markers',
                        name=event_type,
                        marker=dict(color=color, size=10)
                    ))

        fig2.update_layout(
            xaxis=dict(range=[0, 1024], showgrid=False, zeroline=False),
            yaxis=dict(range=[1024, 0], showgrid=False, zeroline=False),
            width=700, height=700,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True
        )

        st.plotly_chart(fig2)
        st.write(f"Showing events up to: {time_slider} seconds into the match")
        st.write(f"Events shown: {len(timeline_df)}")

    # ─────────────────────────────────────
    # TAB 3 — HEATMAP
    # ─────────────────────────────────────

    with tab3:
        st.subheader("Heatmap")

        heatmap_type = st.selectbox(
            "Select Heatmap Type",
            ["All Traffic", "Kill Zones", "Death Zones", "Storm Deaths", "Loot Zones"]
        )

        if heatmap_type == "All Traffic":
            hmap_df = positions
        elif heatmap_type == "Kill Zones":
            hmap_df = kills
        elif heatmap_type == "Death Zones":
            hmap_df = deaths
        elif heatmap_type == "Storm Deaths":
            hmap_df = storms
        elif heatmap_type == "Loot Zones":
            hmap_df = loots

        img3 = Image.open(MAP_IMAGES[selected_map])
        fig3 = go.Figure()

        fig3.add_layout_image(
            dict(
                source=img3,
                xref="x", yref="y",
                x=0, y=0,
                sizex=1024, sizey=1024,
                sizing="stretch",
                opacity=1,
                layer="below"
            )
        )

        if len(hmap_df) > 0:
            fig3.add_trace(go.Histogram2dContour(
                x=hmap_df['pixel_x'],
                y=hmap_df['pixel_y'],
                colorscale='Hot',
                reversescale=True,
                opacity=0.6,
                showscale=True,
                contours=dict(showlines=False),
                name=heatmap_type
            ))

        fig3.update_layout(
            xaxis=dict(range=[0, 1024], showgrid=False, zeroline=False),
            yaxis=dict(range=[1024, 0], showgrid=False, zeroline=False),
            width=700, height=700,
            margin=dict(l=0, r=0, t=0, b=0),
        )

        st.plotly_chart(fig3)
        st.write(f"Showing {len(hmap_df)} data points for {heatmap_type}")

else:
    st.warning("No data found for the selected filters. Please try different options.")