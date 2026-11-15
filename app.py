import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import json
from io import BytesIO
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(BASE, "data", "processed", "cleaned")
INTELLIGENCE = os.path.join(BASE, "outputs", "intelligence")

st.set_page_config(
    page_title="EarthTrend AI | Earth Intelligence Console",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- VISUAL SYSTEM ----------------
# Original EarthTrend visual identity: dark graphite, muted teal and signal cyan.
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
  --bg: #080f14;
  --panel: #101b22;
  --panel2: #14232b;
  --line: rgba(139, 177, 188, .16);
  --muted: #8da4ad;
  --text: #e7f0f2;
  --cyan: #63d9d0;
  --green: #9bd7a5;
}
html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
.stApp { background: radial-gradient(ellipse at 78% 0%, #142b32 0%, #0b151b 35%, var(--bg) 72%); color: var(--text); }
[data-testid="stHeader"] { background: rgba(8,15,20,.82); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0e1b22 0%, #091218 100%); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] * { color: var(--text); }
.block-container { padding-top: 1.8rem; padding-bottom: 2.2rem; max-width: 1600px; }
h1, h2, h3 { letter-spacing: -.035em; }
h1 { font-weight: 800; }
h2, h3 { font-weight: 700; }
p, label, .stCaption { color: #a9bdc4; }
.eyebrow { color: var(--cyan); font: 500 11px 'DM Mono', monospace; letter-spacing: .16em; text-transform: uppercase; margin-bottom: .45rem; }
.hero-title { font-size: clamp(2rem, 4vw, 3.5rem); line-height: 1.04; font-weight: 800; letter-spacing: -.06em; color: #eff8f8; margin: 0; }
.hero-sub { color: #9db2ba; font-size: .98rem; max-width: 760px; margin-top: .8rem; }
.rule { height: 1px; background: linear-gradient(90deg, rgba(99,217,208,.55), rgba(99,217,208,0)); margin: 1.2rem 0 1.4rem; }
.metric-card { background: linear-gradient(145deg, rgba(20,35,43,.96), rgba(13,25,32,.96)); border: 1px solid var(--line); border-radius: 14px; padding: 17px 18px 15px; min-height: 112px; box-shadow: 0 10px 30px rgba(0,0,0,.12); }
.metric-label { color: #91a9b2; font: 500 10px 'DM Mono', monospace; letter-spacing: .13em; text-transform: uppercase; }
.metric-value { color: #edf7f7; font-size: 1.8rem; font-weight: 800; letter-spacing: -.045em; margin-top: 8px; }
.metric-note { color: var(--cyan); font-size: .75rem; margin-top: 2px; }
.section-kicker { color: var(--cyan); font: 500 10px 'DM Mono', monospace; letter-spacing: .14em; text-transform: uppercase; margin-bottom: .3rem; }
.panel { background: rgba(16,27,34,.78); border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px; }
div[data-testid="stMetric"] { background: rgba(16,27,34,.8); border: 1px solid var(--line); padding: 13px 15px; border-radius: 12px; }
.stButton button, .stDownloadButton button { border-radius: 9px; border: 1px solid rgba(99,217,208,.35); background: #15333a; color: #eafffc; }
.stButton button:hover, .stDownloadButton button:hover { border-color: var(--cyan); color: white; }
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
[data-testid="stAlert"] { border-radius: 10px; }
footer { visibility: hidden; }

/* Motion language: restrained, responsive, and reduced-motion aware */
@keyframes et-rise-in {
  from { opacity: 0; transform: translateY(13px); filter: blur(3px); }
  to   { opacity: 1; transform: translateY(0); filter: blur(0); }
}
@keyframes et-glow {
  0%, 100% { box-shadow: 0 10px 30px rgba(0,0,0,.12); }
  50% { box-shadow: 0 14px 36px rgba(49,190,181,.13); }
}
.block-container { animation: et-rise-in .65s cubic-bezier(.2,.75,.25,1) both; }
.metric-card, .panel, div[data-testid="stMetric"] {
  transition: transform .28s ease, border-color .28s ease, box-shadow .28s ease, background .28s ease;
}
.metric-card:hover, .panel:hover, div[data-testid="stMetric"]:hover {
  transform: translateY(-4px);
  border-color: rgba(99,217,208,.42);
  box-shadow: 0 16px 38px rgba(0,0,0,.24), 0 0 22px rgba(99,217,208,.07);
}
.stButton button, .stDownloadButton button, [data-testid="stSidebar"] [role="radiogroup"] label {
  transition: all .22s ease !important;
}
.stButton button:hover, .stDownloadButton button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(99,217,208,.14);
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: rgba(99,217,208,.08);
  border-radius: 8px;
  transform: translateX(3px);
}
[data-testid="stPlotlyChart"] { animation: et-rise-in .75s ease both; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADING ----------------
@st.cache_data(show_spinner="Loading hazard datasets…")
def load_data():
    paths = {
        "floods": f"{CLEAN}/floods_clean.parquet",
        "tornadoes": f"{CLEAN}/tornadoes_clean.parquet",
        "landslides": f"{CLEAN}/landslides_clean.parquet",
        "cyclones": f"{CLEAN}/cyclones_clean.parquet",
    }
    missing = [name for name, path in paths.items() if not os.path.exists(path)]
    if missing:
        raise FileNotFoundError("Missing cleaned dataset(s): " + ", ".join(missing))
    return {name: pd.read_parquet(path) for name, path in paths.items()}

@st.cache_data

def load_intelligence():
    trend_path = os.path.join(INTELLIGENCE, "hazard_trend_analysis.csv")
    anomaly_path = os.path.join(INTELLIGENCE, "hazard_anomaly_analysis.csv")
    trends = pd.read_csv(trend_path) if os.path.exists(trend_path) else pd.DataFrame()
    anomalies = pd.read_csv(anomaly_path) if os.path.exists(anomaly_path) else pd.DataFrame()
    return trends, anomalies

try:
    data = load_data()
except Exception as exc:
    st.error(f"Could not load project datasets: {exc}")
    st.info("Check that the cleaned Parquet files are present in data/processed/cleaned/.")
    st.stop()

trend_data, anomaly_data = load_intelligence()

# ---------------- HELPERS ----------------
def page_heading(kicker, title, subtitle):
    st.markdown(f'<div class="eyebrow">{kicker}</div><div class="hero-title">{title}</div><div class="hero-sub">{subtitle}</div><div class="rule"></div>', unsafe_allow_html=True)

def metric_card(label, value, note=""):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

def style_fig(fig, height=390):
    fig.update_layout(
        template="plotly_dark", height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, sans-serif", color="#c5d5d9", size=12),
        title=dict(font=dict(size=15, color="#e7f0f2"), x=0.02),
        margin=dict(l=18, r=18, t=55, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a9bdc4")),
        xaxis=dict(gridcolor="rgba(139,177,188,.12)", zerolinecolor="rgba(139,177,188,.12)"),
        yaxis=dict(gridcolor="rgba(139,177,188,.12)", zerolinecolor="rgba(139,177,188,.12)"),
    )
    return fig

def show_annual_trend(df, title, y_label):
    if "analysis_year" not in df.columns:
        st.warning("Year field is unavailable for this dataset.")
        return
    yearly = df.dropna(subset=["analysis_year"]).groupby("analysis_year").size().reset_index(name="events")
    yearly["analysis_year"] = pd.to_numeric(yearly["analysis_year"], errors="coerce")
    yearly = yearly.dropna().sort_values("analysis_year")
    if yearly.empty:
        st.warning("No dated records available for this chart.")
        return
    fig = px.line(yearly, x="analysis_year", y="events", markers=True,
                  labels={"analysis_year": "Year", "events": y_label})
    fig.update_traces(line=dict(color="#63d9d0", width=3), marker=dict(color="#9bd7a5", size=7))
    st.plotly_chart(style_fig(fig, 350), use_container_width=True)

def show_map(df, title):
    required = {"coordinate_valid", "latitude", "longitude"}
    if not required.issubset(df.columns):
        st.warning("Coordinate fields are unavailable for this dataset.")
        return
    points = df[df["coordinate_valid"].fillna(False)].dropna(subset=["latitude", "longitude"]).copy()
    if len(points) > 5000:
        points = points.sample(5000, random_state=42)
    if points.empty:
        st.warning("No valid coordinates available.")
        return
    fig = px.scatter_geo(points, lat="latitude", lon="longitude", projection="natural earth", opacity=.62)
    fig.update_traces(marker=dict(size=4, color="#63d9d0"))
    fig.update_layout(title=title, geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#14242b",
                      showocean=True, oceancolor="#0a151c", showcountries=True,
                      countrycolor="rgba(160,190,195,.22)", showcoastlines=True,
                      coastlinecolor="rgba(160,190,195,.25)"))
    st.plotly_chart(style_fig(fig, 500), use_container_width=True)

def trend_label(row):
    trend = str(row.get("Trend", "unknown")).lower()
    significant = str(row.get("Significant", "False")).lower()
    if significant in ["true", "1"]:
        if trend == "increasing":
            return "Statistically significant increasing trend"
        if trend == "decreasing":
            return "Statistically significant decreasing trend"
    return "No statistically significant monotonic trend detected"

def annual_count(df):
    if "analysis_year" not in df.columns:
        return pd.Series(dtype="int64")
    return df.dropna(subset=["analysis_year"]).groupby("analysis_year").size().sort_index()


def render_rotating_earth_globe(data, max_points=1800):
    """Render a continuously rotating textured 3D Earth with sampled project observations."""
    point_rows = []
    palette = {
        "Floods": "#63d9d0",
        "Tornadoes": "#9bd7a5",
        "Landslides": "#e4b96b",
        "Cyclones": "#e58bb7",
    }

    for hazard, key in [
        ("Floods", "floods"),
        ("Tornadoes", "tornadoes"),
        ("Landslides", "landslides"),
        ("Cyclones", "cyclones"),
    ]:
        df = data[key]
        if key == "cyclones":
            if not {"LAT", "LON"}.issubset(df.columns):
                continue
            pts = df[["LAT", "LON"]].copy()
            pts.columns = ["lat", "lng"]
        else:
            if not {"latitude", "longitude"}.issubset(df.columns):
                continue
            pts = df[["latitude", "longitude"]].copy()
            pts.columns = ["lat", "lng"]
            if "coordinate_valid" in df.columns:
                pts = pts[df["coordinate_valid"].fillna(False).values]
        pts["lat"] = pd.to_numeric(pts["lat"], errors="coerce")
        pts["lng"] = pd.to_numeric(pts["lng"], errors="coerce")
        pts = pts.dropna()
        pts = pts[pts["lat"].between(-90, 90) & pts["lng"].between(-180, 180)]
        if len(pts) > max_points // 4:
            pts = pts.sample(max_points // 4, random_state=42)
        for lat, lng in pts.itertuples(index=False, name=None):
            point_rows.append({
                "lat": float(lat), "lng": float(lng),
                "size": 0.12, "color": palette[hazard], "hazard": hazard
            })

    if not point_rows:
        st.info("No valid geographic observations are available for the globe.")
        return

    points_json = json.dumps(point_rows, separators=(",", ":"))
    html = f"""
    <div id="earthtrend-globe" style="width:100%;height:560px;position:relative;overflow:hidden;background:radial-gradient(ellipse at center,#10232b 0%,#081117 68%);border:1px solid rgba(99,217,208,.18);border-radius:18px;">
      <div id="globe-loading" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#9db2ba;font:12px monospace;letter-spacing:2px;z-index:2;">INITIALISING EARTH MODEL…</div>
      <div style="position:absolute;left:18px;bottom:15px;z-index:3;color:#a9bdc4;font:10px monospace;letter-spacing:1.4px;pointer-events:none;">EARTH OBSERVATION LAYERS · HISTORICAL RECORDS</div>
    </div>
    <script src="https://unpkg.com/globe.gl"></script>
    <script>
      const root = document.getElementById('earthtrend-globe');
      const points = {points_json};
      function bootGlobe() {{
        if (typeof Globe === 'undefined') {{
          document.getElementById('globe-loading').textContent = '3D GLOBE LIBRARY UNAVAILABLE — CHECK INTERNET CONNECTION';
          return;
        }}
        const world = Globe()(root)
          .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
          .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
          .backgroundColor('rgba(0,0,0,0)')
          .showAtmosphere(true)
          .atmosphereColor('#56d9d0')
          .atmosphereAltitude(0.18)
          .pointsData(points)
          .pointLat('lat')
          .pointLng('lng')
          .pointColor('color')
          .pointAltitude(0.012)
          .pointRadius('size')
          .pointResolution(8)
          .pointLabel(d => `<div style="padding:7px 10px;background:#10232b;color:#e7f0f2;border:1px solid #31535a;border-radius:7px;font:12px Manrope,sans-serif">${{d.hazard}} observation</div>`);
        world.width(root.clientWidth);
        world.height(root.clientHeight);
        world.controls().autoRotate = true;
        world.controls().autoRotateSpeed = 0.42;
        world.controls().enableDamping = true;
        world.controls().dampingFactor = 0.08;
        world.controls().minDistance = 145;
        world.controls().maxDistance = 360;
        world.pointOfView({{ lat: 18, lng: 35, altitude: 2.25 }}, 0);
        document.getElementById('globe-loading').style.display = 'none';
        window.addEventListener('resize', () => {{
          world.width(root.clientWidth);
          world.height(root.clientHeight);
        }});
      }}
      if (document.readyState === 'complete') bootGlobe();
      else window.addEventListener('load', bootGlobe);
    </script>
    """
    components.html(html, height=575, scrolling=False)


# ---------------- REPORT GENERATION ----------------
def build_pdf_report(data, trend_data, anomaly_data):
    """Build a compact PDF summary from the currently loaded project outputs."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    except ImportError as exc:
        raise RuntimeError("PDF dependency missing. Install reportlab using requirements.txt.") from exc

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=17*mm, leftMargin=17*mm,
        topMargin=17*mm, bottomMargin=17*mm,
        title="EarthTrend AI - Historical Multi-Hazard Intelligence Briefing",
        author="Team DINGAN",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ETTitle", parent=styles["Title"], textColor=colors.HexColor("#12343b"), fontSize=22, leading=27, spaceAfter=8))
    styles.add(ParagraphStyle(name="ETHeading", parent=styles["Heading2"], textColor=colors.HexColor("#087e80"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="ETBody", parent=styles["BodyText"], fontSize=9, leading=13, textColor=colors.HexColor("#26383d")))
    story = []
    story.append(Paragraph("EarthTrend AI", styles["ETTitle"]))
    story.append(Paragraph("Earth System Trend and Multi-Hazard Intelligence Platform", styles["Heading3"]))
    story.append(Paragraph(f"Historical intelligence briefing · Generated {datetime.now().strftime('%d %b %Y, %H:%M')}", styles["ETBody"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("1. Dataset overview", styles["ETHeading"]))

    rows = [["Dataset", "Records / observations", "Coverage"]]
    coverage = {
        "Floods": "NOAA · United States · 2015–2025",
        "Tornadoes": "NOAA · United States · 2015–2025",
        "Landslides": "USGS · United States inventory",
        "Cyclones": "IBTrACS · North Indian Ocean",
    }
    for label, key in [("Floods", "floods"), ("Tornadoes", "tornadoes"), ("Landslides", "landslides"), ("Cyclones", "cyclones")]:
        df = data[key]
        if key == "cyclones" and "SID" in df.columns:
            season = pd.to_numeric(df.get("SEASON"), errors="coerce")
            subset = df[season.between(2015, 2025)]
            count_text = f"{len(subset):,} track points; {subset['SID'].nunique():,} unique storms"
        else:
            count_text = f"{len(df):,} records"
        rows.append([label, count_text, coverage[label]])
    table = Table(rows, colWidths=[28*mm, 62*mm, 80*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#12343b")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#c9d7d9")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f6f6")]),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(table)

    story.append(Paragraph("2. Statistical trend analysis", styles["ETHeading"]))
    if trend_data.empty:
        story.append(Paragraph("No trend analysis CSV was available when this report was generated.", styles["ETBody"]))
    else:
        trend_rows = [["Hazard", "Trend", "P-value", "Sen slope", "Significant"]]
        for _, r in trend_data.iterrows():
            trend_rows.append([
                str(r.get("Hazard", "—")), str(r.get("Trend", "—")),
                str(r.get("P Value", "—")), str(r.get("Sen Slope", "—")),
                str(r.get("Significant", "—")),
            ])
        t = Table(trend_rows, colWidths=[35*mm, 32*mm, 28*mm, 32*mm, 30*mm], repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#087e80")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#c9d7d9")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f6f6")]),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(t)
        story.append(Spacer(1, 5))
        story.append(Paragraph("Trend results describe monotonic patterns in the analysed historical record counts. Statistical significance does not establish causation or forecast future disasters.", styles["ETBody"]))

    story.append(Paragraph("3. Historical anomaly screening", styles["ETHeading"]))
    if anomaly_data.empty:
        story.append(Paragraph("No anomaly analysis CSV was available when this report was generated.", styles["ETBody"]))
    elif "anomaly" in anomaly_data.columns:
        flagged = anomaly_data[anomaly_data["anomaly"].astype(str).str.lower().isin(["true", "1"])].copy()
        if flagged.empty:
            story.append(Paragraph("No annual records crossed the exploratory absolute Z-score threshold of 2.", styles["ETBody"]))
        else:
            anomaly_rows = [["Hazard", "Year", "Records", "Z-score", "Status"]]
            for _, r in flagged.iterrows():
                anomaly_rows.append([str(r.get("hazard", "—")), str(r.get("analysis_year", "—")), str(r.get("event_count", "—")), str(r.get("z_score", "—")), str(r.get("status", "—"))])
            at = Table(anomaly_rows, colWidths=[36*mm, 20*mm, 28*mm, 25*mm, 48*mm], repeatRows=1)
            at.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#12343b")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 8),
                ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#c9d7d9")),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f6f6")]),
            ]))
            story.append(at)
            story.append(Spacer(1, 5))
            story.append(Paragraph("Anomaly flags are exploratory statistical outliers relative to each series. They are not early warnings or evidence of an impending event.", styles["ETBody"]))

    story.append(Paragraph("4. Geographic coverage and limitations", styles["ETHeading"]))
    limitations = [
        "Flood and tornado data are NOAA Storm Events records for the United States, 2015–2025.",
        "Landslide data are a USGS United States inventory. Annual counts use dated inventory records only and are not a complete annual event-frequency series.",
        "Cyclone data are IBTrACS North Indian Ocean observations. Track-point totals are not unique storm counts.",
        "Reporting coverage, missing dates, coordinate quality and changes in data collection can influence apparent patterns.",
        "EarthTrend AI analyses historical records. It does not provide operational forecasts or disaster early warnings.",
    ]
    for item in limitations:
        story.append(Paragraph("• " + item, styles["ETBody"]))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 12))
    story.append(Paragraph("EarthTrend AI · Team DINGAN · NASA Space Apps Challenge 2026", styles["ETBody"]))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ---------------- NAVIGATION ----------------
st.sidebar.markdown('<div class="eyebrow">EARTH SYSTEMS / 01</div><h2 style="margin:0;letter-spacing:-.05em">EARTH<span style="color:#63d9d0">TREND</span></h2><div style="color:#8da4ad;font:11px DM Mono;letter-spacing:.12em;margin:4px 0 18px">INTELLIGENCE CONSOLE</div>', unsafe_allow_html=True)
page = st.sidebar.radio("WORKSPACE", [
    "Overview", "Multi-Hazard Map", "Flood Analysis", "Tornado Analysis", "Landslide Analysis",
    "Cyclone Analysis", "Trend Intelligence", "Anomaly Intelligence", "AI Insights", "Reports & Exports"
], label_visibility="visible")
st.sidebar.markdown("---")
st.sidebar.markdown("<div class='section-kicker'>PROJECT</div><div style='font-size:13px;font-weight:700'>NASA Space Apps Challenge 2026</div><div style='color:#8da4ad;font-size:12px'>Team DINGAN</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='height:20px'></div><div class='section-kicker'>DATA COVERAGE</div><div style='font-size:12px;color:#a9bdc4;line-height:1.8'>NOAA · United States<br>USGS · United States<br>IBTrACS · North Indian Ocean</div>", unsafe_allow_html=True)

# ---------------- OVERVIEW ----------------
if page == "Overview":
    page_heading("MULTI-HAZARD MONITORING / OVERVIEW", "Earth intelligence,\nmade observable.",
                 "Explore historical hazard activity, geographic distributions and statistical signals across the datasets assembled for EarthTrend AI.")
    floods, tornadoes, landslides, cyclones = (data[k] for k in ["floods", "tornadoes", "landslides", "cyclones"])
    total_records = len(floods) + len(tornadoes) + len(landslides)
    total_storms = cyclones["SID"].nunique() if "SID" in cyclones.columns else 0
    dated_landslides = int(landslides["analysis_date"].notna().sum()) if "analysis_date" in landslides.columns else 0
    cols = st.columns(4, gap="medium")
    with cols[0]: metric_card("FLOOD RECORDS", f"{len(floods):,}", "NOAA · 2015–2025")
    with cols[1]: metric_card("TORNADO RECORDS", f"{len(tornadoes):,}", "NOAA · 2015–2025")
    with cols[2]: metric_card("LANDSLIDE INVENTORY", f"{len(landslides):,}", f"{dated_landslides:,} with dates")
    with cols[3]: metric_card("CYCLONE TRACK DATA", f"{len(cyclones):,}", f"{total_storms:,} unique storm IDs")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.markdown('<div class="section-kicker">01 / ACTIVITY SIGNAL</div><h3 style="margin-top:0">Annual hazard activity</h3>', unsafe_allow_html=True)
        f_year = annual_count(floods).rename("Floods")
        t_year = annual_count(tornadoes).rename("Tornadoes")
        yearly = pd.concat([f_year, t_year], axis=1).fillna(0).rename_axis("Year").reset_index()
        if not yearly.empty:
            fig = px.line(yearly, x="Year", y=["Floods", "Tornadoes"], markers=True)
            fig.update_traces(line=dict(width=3))
            fig.data[0].line.color = "#63d9d0"
            fig.data[1].line.color = "#9bd7a5"
            st.plotly_chart(style_fig(fig, 360), use_container_width=True)
        else:
            st.info("Annual activity is not available for these datasets.")
    with right:
        st.markdown('<div class="section-kicker">02 / INTELLIGENCE STATUS</div><h3 style="margin-top:0">Statistical signals</h3>', unsafe_allow_html=True)
        if trend_data.empty:
            st.warning("Trend report not found. Run the intelligent analytics notebook.")
        else:
            for _, row in trend_data.iterrows():
                significant = str(row.get("Significant", "False")).lower() in ["true", "1"]
                label = str(row.get("Hazard", "Hazard"))
                status = "SIGNIFICANT" if significant else "NO SIGNAL"
                color = "#9bd7a5" if significant else "#8da4ad"
                st.markdown(f"<div class='panel' style='margin-bottom:9px;padding:12px 14px'><div style='display:flex;justify-content:space-between;gap:8px'><b>{label}</b><span style='font:10px DM Mono;color:{color};letter-spacing:.1em'>{status}</span></div><div style='color:#a9bdc4;font-size:12px;margin-top:5px'>{trend_label(row)}</div></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">03 / GEOGRAPHIC CONTEXT</div><h3 style="margin-top:0">Live 3D Earth view</h3>', unsafe_allow_html=True)
    st.caption("A continuously rotating, textured 3D globe with sampled historical observation locations. Drag to rotate, scroll to zoom.")
    render_rotating_earth_globe(data)
    st.markdown(
        "<div style='display:flex;gap:18px;flex-wrap:wrap;color:#a9bdc4;font:11px DM Mono;margin:4px 0 12px'>"
        "<span style='color:#63d9d0'>● FLOODS</span><span style='color:#9bd7a5'>● TORNADOES</span>"
        "<span style='color:#e4b96b'>● LANDSLIDES</span><span style='color:#e58bb7'>● CYCLONES</span></div>",
        unsafe_allow_html=True
    )
    st.info("Scope note: flood and tornado records are NOAA United States events; landslides are a USGS inventory; cyclone tracks are from IBTrACS for the North Indian Ocean. This platform analyses historical records and does not issue forecasts or operational warnings.")


# ---------------- MULTI-HAZARD MAP ----------------
elif page == "Multi-Hazard Map":
    page_heading(
        "GEOSPATIAL INTELLIGENCE / 01",
        "Multi-hazard explorer",
        "Explore geolocated historical records across the available hazard inventories. Filter by hazard and year, inspect the spatial footprint, and export the filtered points."
    )

    hazard_labels = {
        "Floods": "floods",
        "Tornadoes": "tornadoes",
        "Landslides": "landslides",
        "Cyclones": "cyclones",
    }
    chosen_hazards = st.multiselect(
        "HAZARD LAYERS",
        options=list(hazard_labels.keys()),
        default=["Floods", "Tornadoes", "Landslides", "Cyclones"],
    )
    if not chosen_hazards:
        st.info("Select at least one hazard layer to display the map.")
    else:
        frames = []
        for label in chosen_hazards:
            key = hazard_labels[label]
            raw = data[key]
            if key == "cyclones":
                required = {"LAT", "LON", "SEASON"}
                if not required.issubset(raw.columns):
                    continue
                part = raw.copy()
                part["latitude"] = pd.to_numeric(part["LAT"], errors="coerce")
                part["longitude"] = pd.to_numeric(part["LON"], errors="coerce")
                part["analysis_year"] = pd.to_numeric(part["SEASON"], errors="coerce")
                keep = ["latitude", "longitude", "analysis_year"]
                for col in ["SID", "NAME", "ISO_TIME"]:
                    if col in part.columns:
                        keep.append(col)
                part = part[keep].copy()
            else:
                if not {"latitude", "longitude"}.issubset(raw.columns):
                    continue
                part = raw.copy()
                if "analysis_year" not in part.columns:
                    if "analysis_date" in part.columns:
                        part["analysis_year"] = pd.to_datetime(
                            part["analysis_date"], errors="coerce"
                        ).dt.year
                    else:
                        part["analysis_year"] = np.nan
                keep = ["latitude", "longitude", "analysis_year"]
                for col in ["EVENT_TYPE", "STATE", "CZ_NAME", "LS_Type", "BEGIN_DATE"]:
                    if col in part.columns and col not in keep:
                        keep.append(col)
                if "coordinate_valid" in part.columns:
                    part = part[part["coordinate_valid"].fillna(False)]
                part = part[keep].copy()

            part["latitude"] = pd.to_numeric(part["latitude"], errors="coerce")
            part["longitude"] = pd.to_numeric(part["longitude"], errors="coerce")
            part["analysis_year"] = pd.to_numeric(part["analysis_year"], errors="coerce")
            part = part.dropna(subset=["latitude", "longitude"])
            part = part[
                part["latitude"].between(-90, 90)
                & part["longitude"].between(-180, 180)
            ]
            part["Hazard"] = label
            frames.append(part)

        if not frames:
            st.warning("No compatible coordinate records were found for the selected layers.")
        else:
            all_points = pd.concat(frames, ignore_index=True, sort=False)
            available_years = sorted(
                int(y) for y in all_points["analysis_year"].dropna().unique()
                if 1900 <= y <= 2100
            )
            year_options = ["All available years"] + [str(y) for y in available_years]
            selected_year = st.selectbox("YEAR FILTER", year_options, index=0)

            filtered = all_points.copy()
            if selected_year != "All available years":
                filtered = filtered[
                    filtered["analysis_year"] == int(selected_year)
                ]

            m1, m2, m3 = st.columns(3)
            m1.metric("Mapped records", f"{len(filtered):,}")
            m2.metric("Hazard layers", f"{filtered['Hazard'].nunique():,}")
            m3.metric(
                "Years represented",
                f"{filtered['analysis_year'].nunique():,}"
                if filtered["analysis_year"].notna().any() else "Not available"
            )

            max_points = st.slider(
                "Maximum points to render",
                min_value=500,
                max_value=12000,
                value=5000,
                step=500,
                help="Large inventories are sampled for responsive map rendering. The download below contains all filtered records."
            )
            plot_points = filtered
            if len(plot_points) > max_points:
                plot_points = plot_points.sample(max_points, random_state=42)

            if plot_points.empty:
                st.warning("No records match the selected filters.")
            else:
                color_map = {
                    "Floods": "#63d9d0",
                    "Tornadoes": "#9bd7a5",
                    "Landslides": "#e4b96b",
                    "Cyclones": "#e58bb7",
                }
                hover_cols = [
                    c for c in [
                        "analysis_year", "STATE", "CZ_NAME", "EVENT_TYPE",
                        "LS_Type", "NAME", "SID", "ISO_TIME"
                    ] if c in plot_points.columns
                ]
                fig = px.scatter_geo(
                    plot_points,
                    lat="latitude",
                    lon="longitude",
                    color="Hazard",
                    hover_data=hover_cols,
                    color_discrete_map=color_map,
                    projection="natural earth",
                    opacity=0.68,
                )
                fig.update_traces(marker=dict(size=5))
                fig.update_layout(
                    legend_title_text="HAZARD LAYER",
                    geo=dict(
                        bgcolor="rgba(0,0,0,0)",
                        showland=True,
                        landcolor="#14242b",
                        showocean=True,
                        oceancolor="#0a151c",
                        showcountries=True,
                        countrycolor="rgba(160,190,195,.28)",
                        showcoastlines=True,
                        coastlinecolor="rgba(160,190,195,.25)",
                    ),
                )
                st.plotly_chart(style_fig(fig, 590), use_container_width=True)

            st.caption(
                "Coverage note: floods and tornadoes are NOAA United States records; "
                "landslides are a USGS United States inventory; cyclones are IBTrACS "
                "North Indian Ocean track observations. A track observation is not "
                "the same as a unique storm or disaster event."
            )
            csv_bytes = filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download filtered map records (CSV)",
                data=csv_bytes,
                file_name="earthtrend_filtered_hazard_records.csv",
                mime="text/csv",
            )

# ---------------- FLOODS ----------------
elif page == "Flood Analysis":
    df = data["floods"]
    page_heading("HAZARD MODULE / 01", "Flood analysis", "Historical flood-event patterns from the NOAA Storm Events Database · United States · 2015–2025.")
    a, b, c = st.columns(3)
    a.metric("Flood records", f"{len(df):,}")
    valid_coords = int(df["coordinate_valid"].fillna(False).sum()) if "coordinate_valid" in df else 0
    b.metric("Records with coordinates", f"{valid_coords:,}")
    c.metric("Years covered", f"{df['analysis_year'].nunique():,}" if "analysis_year" in df else "—")
    show_annual_trend(df, "Annual flood-event records", "Events")
    cause_col = next((c for c in df.columns if c.upper() == "FLOOD_CAUSE"), None)
    if cause_col:
        causes = df[cause_col].fillna("Not specified").value_counts().head(10).rename_axis("Cause").reset_index(name="Events")
        fig = px.bar(causes, x="Events", y="Cause", orientation="h")
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)
    show_map(df, "Geographic distribution · flood records")

# ---------------- TORNADOES ----------------
elif page == "Tornado Analysis":
    df = data["tornadoes"]
    page_heading("HAZARD MODULE / 02", "Tornado analysis", "Historical tornado-event patterns and reported intensity from NOAA · United States · 2015–2025.")
    a, b, c = st.columns(3)
    a.metric("Tornado records", f"{len(df):,}")
    valid_coords = int(df["coordinate_valid"].fillna(False).sum()) if "coordinate_valid" in df else 0
    b.metric("Records with coordinates", f"{valid_coords:,}")
    c.metric("Years covered", f"{df['analysis_year'].nunique():,}" if "analysis_year" in df else "—")
    show_annual_trend(df, "Annual tornado-event records", "Events")
    scale_col = next((c for c in df.columns if c.upper() == "TOR_F_SCALE"), None)
    if scale_col:
        scales = df[scale_col].fillna("Not specified").value_counts().rename_axis("Scale").reset_index(name="Events")
        fig = px.bar(scales, x="Scale", y="Events")
        st.plotly_chart(style_fig(fig, 350), use_container_width=True)
    show_map(df, "Geographic distribution · tornado records")

# ---------------- LANDSLIDES ----------------
elif page == "Landslide Analysis":
    df = data["landslides"]
    page_heading("HAZARD MODULE / 03", "Landslide analysis", "USGS landslide inventory characteristics and dated-record patterns · United States.")
    a, b, c = st.columns(3)
    a.metric("Inventory records", f"{len(df):,}")
    dated = int(df["analysis_date"].notna().sum()) if "analysis_date" in df else 0
    b.metric("Records with dates", f"{dated:,}")
    c.metric("Dated share", f"{dated / len(df) * 100:.1f}%" if len(df) else "—")
    if "LS_Type" in df:
        types = df["LS_Type"].fillna("Not specified").value_counts().head(15).rename_axis("Type").reset_index(name="Records")
        fig = px.bar(types, x="Records", y="Type", orientation="h")
        st.plotly_chart(style_fig(fig, 420), use_container_width=True)
    show_annual_trend(df, "Dated landslide inventory records by year", "Records")
    st.warning("Yearly landslide counts represent only inventory records with dates. They should not be interpreted as complete annual landslide-event frequency.")
    show_map(df, "Landslide inventory locations")

# ---------------- CYCLONES ----------------
elif page == "Cyclone Analysis":
    df = data["cyclones"].copy()
    page_heading("HAZARD MODULE / 04", "Tropical cyclone analysis", "IBTrACS observations for the North Indian Ocean. Select a season to inspect storm tracks and observation points.")
    if not {"SEASON", "SID", "LAT", "LON"}.issubset(df.columns):
        st.error("The cyclone dataset is missing one or more required columns: SEASON, SID, LAT, LON.")
    else:
        df["analysis_year"] = pd.to_numeric(df["SEASON"], errors="coerce")
        df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
        df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
        df = df[df["analysis_year"].between(2015, 2025)]
        years = sorted(df["analysis_year"].dropna().unique().tolist())
        if not years:
            st.warning("No cyclone observations found for 2015–2025.")
        else:
            selected_year = st.selectbox("CYCLONE SEASON", years, index=len(years)-1)
            season = df[df["analysis_year"] == selected_year].copy()
            a, b = st.columns(2)
            a.metric("Unique storms", f"{season['SID'].nunique():,}")
            b.metric("Track observations", f"{len(season):,}")
            valid = season.dropna(subset=["LAT", "LON", "SID"]).copy()
            if not valid.empty:
                fig = px.scatter_geo(valid, lat="LAT", lon="LON", color="SID", hover_name="NAME" if "NAME" in valid else None, projection="natural earth")
                fig.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#14242b", showocean=True, oceancolor="#0a151c", showcountries=True, countrycolor="rgba(160,190,195,.22)"))
                st.plotly_chart(style_fig(fig, 480), use_container_width=True)
                if "ISO_TIME" in valid.columns:
                    valid["ISO_TIME"] = pd.to_datetime(valid["ISO_TIME"], errors="coerce")
                    valid = valid.sort_values("ISO_TIME")
                fig = px.line(valid, x="LON", y="LAT", color="SID", hover_name="NAME" if "NAME" in valid else None)
                st.plotly_chart(style_fig(fig, 400), use_container_width=True)
            else:
                st.warning("No valid cyclone coordinates for this season.")

# ---------------- TREND INTELLIGENCE ----------------
elif page == "Trend Intelligence":
    page_heading("INTELLIGENCE / 01", "Trend intelligence", "Mann–Kendall testing and Sen’s slope are used to examine monotonic patterns in historical annual records.")
    if trend_data.empty:
        st.warning("Trend analysis report not found. Run the intelligent analytics notebook.")
    else:
        for _, row in trend_data.iterrows():
            with st.container(border=True):
                st.subheader(str(row.get("Hazard", "Hazard")))
                st.write(trend_label(row))
                a, b, c = st.columns(3)
                a.metric("Trend direction", str(row.get("Trend", "—")).title())
                b.metric("P-value", str(row.get("P Value", "—")))
                c.metric("Sen’s slope", str(row.get("Sen Slope", "—")))
                st.caption(f"Period: {row.get('Start Year', '—')}–{row.get('End Year', '—')} · Years analysed: {row.get('Years Analysed', '—')} · Significant: {row.get('Significant', '—')}")
        st.caption("A statistically significant trend describes the analysed record counts. It does not establish causation or predict future disasters.")

# ---------------- ANOMALY INTELLIGENCE ----------------
elif page == "Anomaly Intelligence":
    page_heading("INTELLIGENCE / 02", "Historical anomaly detection", "Annual activity is screened using an exploratory Z-score threshold. Flagged years are statistical outliers, not disaster alerts.")
    if anomaly_data.empty:
        st.warning("Anomaly report not found. Run the intelligent analytics notebook.")
    elif not {"hazard", "analysis_year", "event_count", "z_score", "status", "anomaly"}.issubset(anomaly_data.columns):
        st.error("The anomaly report does not contain the expected columns.")
    else:
        hazard_options = anomaly_data["hazard"].dropna().unique().tolist()
        if hazard_options:
            selected_hazard = st.selectbox("SELECT HAZARD", hazard_options)
            subset = anomaly_data[anomaly_data["hazard"] == selected_hazard].copy()
            fig = px.bar(subset, x="analysis_year", y="event_count", color="status", hover_data=["z_score"])
            st.plotly_chart(style_fig(fig, 380), use_container_width=True)
            flagged = subset[subset["anomaly"].astype(str).str.lower().isin(["true", "1"])]
            st.subheader("Flagged years")
            if flagged.empty:
                st.success("No years crossed the selected anomaly threshold.")
            else:
                st.dataframe(flagged[["analysis_year", "event_count", "z_score", "status"]], use_container_width=True, hide_index=True)
        else:
            st.info("No hazard categories are available in the anomaly report.")

# ---------------- AI INSIGHTS ----------------
elif page == "AI Insights":
    page_heading(
        "INTELLIGENCE / 03",
        "Earth system intelligence",
        "A concise, explainable briefing built from the historical records, trend tests and anomaly screening in this project."
    )

    # Dataset-derived activity summary. These are record counts, not necessarily
    # unique disaster counts; cyclone observations are track points.
    summary_specs = [
        ("Floods", "floods", "NOAA · United States"),
        ("Tornadoes", "tornadoes", "NOAA · United States"),
        ("Landslides", "landslides", "USGS · United States inventory"),
    ]
    st.markdown("<div class='section-kicker'>DATASET PULSE</div>", unsafe_allow_html=True)
    pulse_cols = st.columns(3)
    for col, (label, key, source) in zip(pulse_cols, summary_specs):
        df = data[key]
        yearly = annual_count(df)
        if not yearly.empty:
            peak_year = int(yearly.idxmax())
            peak_count = int(yearly.max())
            note = f"Peak recorded year: {peak_year} · {source}"
        else:
            peak_count = len(df)
            note = source
        with col:
            metric_card(f"{label.upper()} RECORDS", f"{len(df):,}", note)

    cyclone_df = data["cyclones"].copy()
    cyclone_years = pd.to_numeric(cyclone_df.get("SEASON"), errors="coerce") if "SEASON" in cyclone_df else pd.Series(dtype=float)
    cyclone_df["_season"] = cyclone_years
    cyclone_period = cyclone_df[cyclone_df["_season"].between(2015, 2025)] if not cyclone_df.empty else cyclone_df
    unique_storms = int(cyclone_period["SID"].nunique()) if "SID" in cyclone_period else 0
    st.caption(f"Cyclones: {unique_storms:,} unique storms represented by {len(cyclone_period):,} North Indian Ocean track observations (2015–2025).")

    st.markdown("<div class='rule'></div><div class='section-kicker'>STATISTICAL SIGNALS</div>", unsafe_allow_html=True)
    if trend_data.empty:
        st.warning("Trend report unavailable. Run the intelligent analytics notebook to populate this section.")
    else:
        for _, row in trend_data.iterrows():
            hazard = str(row.get("Hazard", "Hazard"))
            trend = str(row.get("Trend", "unknown")).lower()
            significant = str(row.get("Significant", "False")).lower() in ["true", "1"]
            p_value = row.get("P Value", np.nan)
            slope = row.get("Sen Slope", np.nan)
            if significant and trend == "increasing":
                explanation = "The analysed annual record counts show a statistically significant upward monotonic trend."
                signal = "INCREASING · SIGNIFICANT"
            elif significant and trend == "decreasing":
                explanation = "The analysed annual record counts show a statistically significant downward monotonic trend."
                signal = "DECREASING · SIGNIFICANT"
            else:
                explanation = "The analysis did not detect a statistically significant monotonic trend in the available annual records."
                signal = "NO SIGNIFICANT TREND"
            with st.container(border=True):
                left, right = st.columns([3, 1])
                with left:
                    st.markdown(f"**{hazard}**")
                    st.write(explanation)
                    st.caption(f"Analysis period: {row.get('Start Year', '—')}–{row.get('End Year', '—')} · Years analysed: {row.get('Years Analysed', '—')}")
                with right:
                    st.markdown(f"<div class='section-kicker'>SIGNAL</div><div style='font:700 12px DM Mono;color:#63d9d0'>{signal}</div>", unsafe_allow_html=True)
                    st.metric("Sen’s slope", f"{slope:.3g}" if pd.notna(slope) else "—")
                    st.metric("P-value", f"{p_value:.4g}" if pd.notna(p_value) else "—")

    st.markdown("<div class='rule'></div><div class='section-kicker'>UNUSUAL HISTORICAL ACTIVITY</div>", unsafe_allow_html=True)
    if anomaly_data.empty:
        st.warning("Anomaly report unavailable. Run the intelligent analytics notebook to populate this section.")
    elif "anomaly" not in anomaly_data.columns:
        st.error("The anomaly report is missing its anomaly flag column.")
    else:
        flagged = anomaly_data[anomaly_data["anomaly"].astype(str).str.lower().isin(["true", "1"])].copy()
        if flagged.empty:
            st.success("No annual records crossed the exploratory Z-score threshold of |Z| ≥ 2.")
        else:
            sort_col = "z_score" if "z_score" in flagged.columns else None
            if sort_col:
                flagged[sort_col] = pd.to_numeric(flagged[sort_col], errors="coerce")
                flagged = flagged.reindex(flagged[sort_col].abs().sort_values(ascending=False).index)
            show_cols = [c for c in ["hazard", "analysis_year", "event_count", "z_score", "status"] if c in flagged.columns]
            st.dataframe(flagged[show_cols], use_container_width=True, hide_index=True)
            st.caption("A flagged year is unusual relative to the values in its own series. It is not evidence of an impending event or an operational warning.")

    st.markdown("<div class='rule'></div><div class='section-kicker'>INTERPRETATION & DATA LIMITS</div>", unsafe_allow_html=True)
    st.markdown("""
    - **Floods and tornadoes:** NOAA Storm Events records for the United States, 2015–2025.
    - **Landslides:** USGS United States inventory. Annual patterns use dated inventory records only; they are not a complete annual event-frequency series.
    - **Cyclones:** IBTrACS North Indian Ocean observations. Track-point totals must not be interpreted as unique storm counts.
    - **Interpretation:** Reporting coverage, missing dates, location quality and changes in data collection can influence apparent trends and anomalies.
    """)

    # Download a compact briefing table derived from available intelligence outputs.
    if not trend_data.empty or not anomaly_data.empty:
        report_parts = []
        if not trend_data.empty:
            t = trend_data.copy()
            t.insert(0, "Report section", "Trend analysis")
            report_parts.append(t)
        if not anomaly_data.empty:
            a = anomaly_data.copy()
            a.insert(0, "Report section", "Anomaly analysis")
            report_parts.append(a)
        combined = pd.concat(report_parts, ignore_index=True, sort=False)
        st.download_button(
            "Download intelligence briefing data (CSV)",
            data=combined.to_csv(index=False).encode("utf-8"),
            file_name="earthtrend_intelligence_briefing.csv",
            mime="text/csv",
        )

# ---------------- REPORTS & EXPORTS ----------------
elif page == "Reports & Exports":
    page_heading(
        "OUTPUTS / 01",
        "Reports & exports",
        "Generate a downloadable PDF briefing from the datasets and statistical intelligence reports currently loaded by EarthTrend AI."
    )
    st.markdown("### Project report")
    st.write("The PDF includes dataset coverage, record totals, statistical trend results, flagged historical anomalies and interpretation limits.")
    st.info("The report is generated from the current local project files. It does not include live forecasts or external real-time data.")
    if st.button("Generate PDF intelligence report", type="primary"):
        try:
            pdf_bytes = build_pdf_report(data, trend_data, anomaly_data)
            st.session_state["earthtrend_pdf_report"] = pdf_bytes
            st.success("PDF report generated successfully.")
        except Exception as exc:
            st.error(f"Could not generate PDF report: {exc}")
    if st.session_state.get("earthtrend_pdf_report"):
        st.download_button(
            "Download EarthTrend AI report (PDF)",
            data=st.session_state["earthtrend_pdf_report"],
            file_name="EarthTrend_AI_Intelligence_Report.pdf",
            mime="application/pdf",
        )
    st.markdown("### Data exports")
    export_cols = st.columns(2)
    with export_cols[0]:
        if not trend_data.empty:
            st.download_button(
                "Download trend analysis (CSV)",
                data=trend_data.to_csv(index=False).encode("utf-8"),
                file_name="hazard_trend_analysis.csv",
                mime="text/csv",
            )
    with export_cols[1]:
        if not anomaly_data.empty:
            st.download_button(
                "Download anomaly analysis (CSV)",
                data=anomaly_data.to_csv(index=False).encode("utf-8"),
                file_name="hazard_anomaly_analysis.csv",
                mime="text/csv",
            )

# ---------------- FOOTER ----------------
st.markdown("<div class='rule'></div><div style='display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:#718991;font:10px DM Mono;letter-spacing:.08em'><span>EARTH TREND AI · HISTORICAL EARTH SYSTEM ANALYSIS</span><span>TEAM DINGAN · NASA SPACE APPS CHALLENGE 2026</span></div>", unsafe_allow_html=True)