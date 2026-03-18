# Architecture Document

## Tech Stack
- **Python + Streamlit** — Chosen for speed of development and beginner friendliness. Streamlit turns Python scripts into web apps with minimal code.
- **Plotly** — Interactive charts and map overlays with zoom, hover and click support.
- **Pandas + PyArrow** — Reading and processing parquet files efficiently.
- **Pillow** — Loading minimap images as backgrounds.

## Data Flow
1. Raw parquet files stored in sample_data folder
2. All files loaded and combined into one pandas DataFrame
3. Event column decoded from bytes to readable text
4. User ID checked to identify humans vs bots
5. Coordinates converted from game world to minimap pixels
6. Plotly renders the map with overlaid markers and paths

## Coordinate Mapping
Each map has a scale and origin defined in the README.
Formula used:
- u = (x - origin_x) / scale
- v = (z - origin_z) / scale
- pixel_x = u * 1024
- pixel_y = (1 - v) * 1024
The Y axis is flipped because image origin is top-left but game origin is bottom-left.

## Trade Offs
| Decision | Why |
|---|---|
| Streamlit over React | Faster to build, easier to deploy |
| Sample data for deployment | Full dataset too large for GitHub |
| Single page app | Simpler for Level Designers to use |
| Plotly over D3.js | Built in interactivity, less code |

## Assumptions
- Y column represents elevation, not used for 2D mapping
- Bot user IDs are always numeric, human IDs are always UUIDs
- February 14 data is partial as mentioned in README

## What I Would Do With More Time
- Add full dataset support using cloud storage
- Add player comparison across multiple matches
- Add export feature for level designers to save insights
- Add storm progression overlay on the map