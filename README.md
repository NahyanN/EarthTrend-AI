# EarthTrend AI

**Earth System Trend and Multi-Hazard Intelligence Platform**  
Team DINGAN · NASA Space Apps Challenge 2026

EarthTrend AI is a Streamlit proof-of-concept for exploring selected historical natural-hazard datasets through geospatial visualisation, descriptive analytics, statistical trend analysis and exploratory anomaly screening.

## Features

- Dark Earth-intelligence dashboard with a textured, continuously rotating 3D Earth on the overview page
- Multi-hazard map with hazard-layer and year filters
- Separate flood, tornado, landslide and tropical-cyclone analysis pages
- Historical trend summaries using the Mann–Kendall test and Sen's slope
- Exploratory annual Z-score anomaly screening
- Rule-based analytical insights
- PDF briefing and CSV exports

## Data scope

This prototype uses a limited selection of historical data sources; it is not a global hazard-monitoring or forecasting system.

| Hazard | Source and geographic scope |
|---|---|
| Floods | NOAA Storm Events Database — United States, 2015–2025 |
| Tornadoes | NOAA Storm Events Database — United States, 2015–2025 |
| Landslides | USGS landslide inventory — United States |
| Tropical cyclones | IBTrACS — North Indian Ocean |

## Required local data files

The cleaned datasets are not included in this repository. Place them in `data/processed/cleaned/`:

- `floods_clean.parquet`
- `tornadoes_clean.parquet`
- `landslides_clean.parquet`
- `cyclones_clean.parquet`

For trend and anomaly pages, place these optional reports in `outputs/intelligence/`:

- `hazard_trend_analysis.csv`
- `hazard_anomaly_analysis.csv`

The `.gitkeep` files preserve the expected folder structure. Obtain the datasets separately and do not commit large raw data files to this source repository.

## Run locally

Use Python 3.10 or later.

```bash
git clone https://github.com/NahyanN/EarthTrend-AI.git
cd EarthTrend-AI
python -m venv .venv
```

Activate the virtual environment, then install and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The application requires the cleaned Parquet files listed above. It will not run its full dashboard until those files are available in the expected directory.

## Methodology and limitations

- Trend analysis examines monotonic patterns in historical annual record counts; significance does not establish causation.
- Anomaly flags are exploratory statistical outliers based on annual Z-scores. They are not early warnings.
- Landslide annual counts represent dated records in the available inventory and should not be interpreted as a complete annual event-frequency series.
- Cyclone track observations are not the same as unique storms.
- Reporting coverage, missing dates, coordinate quality and collection practices can affect apparent patterns.
- EarthTrend AI analyses historical records. It does not issue operational forecasts or disaster warnings.

## Project structure

```text
EarthTrend-AI/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── processed/cleaned/
└── outputs/
    └── intelligence/
```

The dashboard also uses public CDN resources for web fonts, the 3D globe renderer and Earth imagery; an internet connection is required for those visual elements.
