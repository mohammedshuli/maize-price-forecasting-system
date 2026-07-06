# Maize Price Forecasting System

This project builds a practical decision-support system for forecasting maize prices in two Tanzanian regions: Iringa and Mbeya. It combines time-series forecasting with a simple Streamlit dashboard that helps users decide whether to sell or store maize based on expected price movements.

## What this project does

- Loads and preprocesses historical maize price data
- Detects outliers and handles missing values
- Trains forecasting models for each region
- Generates price forecasts and confidence intervals
- Provides a web dashboard for actionable recommendations

## Project structure

- dashboard/app.py — Streamlit user interface
- src/ — preprocessing, modeling, validation, and recommendation logic
- data/ — raw, processed, and forecast output data
- models/ — trained forecasting model artifacts
- reports/ — analysis and comparison documents
- notebooks/ — exploratory and development notebooks

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Run the dashboard

Start the application with:

```bash
streamlit run dashboard/app.py
```

## Example workflow

1. Prepare or update the dataset under data/
2. Train or refresh the forecasting models
3. Generate fresh forecasts
4. Open the dashboard to view recommendations

## Notes

- The project is designed for local experimentation and small-scale deployment.
- Forecast outputs are stored in data/outputs/.
- Model artifacts are stored in models/.
