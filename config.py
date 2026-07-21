# config.py
"""
Central configuration file containing project-wide constants, file paths,
and business rules for the Maize Price Forecasting System.
"""

import os

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Data directories and paths
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "wfp_food_prices_tza.csv")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "data", "outputs")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

# Regional settings
REGIONS = ["Mbeya", "Iringa"]

# Business logic & Decision support constants
HARVEST_MONTHS = [5, 6, 7, 8, 9]  # May to September
CASH_PRESSURE_DISCOUNT = 0.10      # 10% discount due to cash pressure
STORAGE_LOSS_KAWAIDA = 0.20        # 20% loss for normal storage (kawaida)
STORAGE_LOSS_HERMETIC = 0.05       # 5% loss for hermetic/special storage

# Language configurations
SWAHILI_MONTHS = {
    1: "Januari", 2: "Februari", 3: "Machi", 4: "Aprili",
    5: "Mei", 6: "Juni", 7: "Julai", 8: "Agosti",
    9: "Septemba", 10: "Oktoba", 11: "Novemba", 12: "Desemba"
}
