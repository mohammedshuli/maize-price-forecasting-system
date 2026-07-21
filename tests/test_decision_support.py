import pytest
from datetime import datetime
import pandas as pd
import numpy as np

from src.decision_support import (
    analyze_forecast,
    assess_risk,
    evaluate_economics,
    explain_decision,
    generate_decision,
    get_recommendation,
    to_farmer_units,
)
from src.farmer_advisor import (
    build_action_plan,
    build_reasoning,
    build_risk_message,
    build_storage_advice,
    build_summary,
    generate_farmer_plan,
)
from src.imputation import find_large_gaps, impute_series
from src.verification import verify_raw_data, verify_processed_data, verify_forecast_data


def test_get_recommendation_marks_high_risk_when_storage_cost_outweighs_gain():
    # Existing test logic preserved
    rec = get_recommendation(
        current_date=datetime(2026, 5, 1),
        current_price_100kg=70000,
        forecast_dates=[
            datetime(2026, 6, 1),
            datetime(2026, 7, 1),
            datetime(2026, 8, 1),
        ],
        forecast_prices_100kg=[71000, 72000, 73000],
        ci_lower_1m_100kg=65000,
        ci_upper_1m_100kg=77000,
        storage_quality="kawaida",
    )

    assert rec["action"] == "UZA SASA"
    assert rec["risk_level"] == "high"
    assert rec["storage_loss_assumed_pct"] == 20


def test_analyze_forecast_and_generate_decision_pipeline():
    forecast_dates = [datetime(2026, 6, 1), datetime(2026, 7, 1), datetime(2026, 8, 1)]
    forecast_prices = [71000, 72000, 73000]

    market = analyze_forecast(
        current_date=datetime(2026, 5, 1),
        current_price_100kg=70000,
        forecast_dates=forecast_dates,
        forecast_prices_100kg=forecast_prices,
    )
    economics = evaluate_economics(
        current_price_100kg=70000,
        forecast_prices_100kg=forecast_prices,
        storage_duration_months=3,
        storage_cost=5000,
        transport_cost=3000,
        storage_quality="kawaida",
    )
    risk = assess_risk(
        uncertainty_width_pct=0.4,
        storage_loss_pct=0.2,
        volatility_pct=0.1,
        profitability_pct=economics["expected_net_benefit_pct"],
    )
    decision = generate_decision(market, economics, risk)
    explanation = explain_decision(decision, market, economics, risk)

    assert market["trend_direction"] == "Increasing"
    assert market["average_forecast_price"] == pytest.approx(72000.0)
    assert economics["expected_net_benefit_pct"] < 0
    assert risk["risk_level"] == "High"
    assert decision["action"] == "SELL_NOW"
    assert explanation["recommendation"] == "SELL_NOW"
    assert explanation["reasons"]


def test_to_farmer_units():
    units = to_farmer_units(100000.0)
    assert units["per_kg"] == 1000.0
    assert units["per_gunia_90kg"] == 90000.0


def test_generate_farmer_plan_cash_need():
    advice = {
        "action": "SUBIRI ZAIDI",
        "utabiri_wa_bei": [{"per_gunia_90kg": 100000.0}],
    }
    
    # Test cash_need == "Ndiyo" causes 50% split regardless of high recommendation to wait
    plan_with_cash_need = generate_farmer_plan(
        bags=10,
        advice=advice,
        current_price_100kg=80000.0,
        storage_type="Ghala",
        cash_need="Ndiyo"
    )
    
    assert plan_with_cash_need["sell_now_bags"] == 5.0
    assert plan_with_cash_need["keep_bags"] == 5.0
    
    # Test cash_need == "Hapana" and SUBIRI ZAIDI holds 80% (keep = 8, sell = 2)
    plan_without_cash_need = generate_farmer_plan(
        bags=10,
        advice=advice,
        current_price_100kg=80000.0,
        storage_type="Ghala",
        cash_need="Hapana"
    )
    
    assert plan_without_cash_need["sell_now_bags"] == 2.0
    assert plan_without_cash_need["keep_bags"] == 8.0


def test_farmer_advisor_builds_plain_language_guidance():
    decision = {
        "action": "SELL_NOW",
        "reasons": ["The forecast trend is declining.", "The expected storage outcome is a loss after storage and transport costs."],
        "risk_level": "High",
    }

    summary = build_summary(decision)
    reasoning = build_reasoning(decision)
    storage_advice = build_storage_advice("SELL_NOW")
    risk_message = build_risk_message("High")
    action_plan = build_action_plan("SELL_NOW")

    assert "decline" in summary.lower()
    assert reasoning
    assert storage_advice
    assert "uncertainty" in risk_message.lower()
    assert action_plan


def test_imputation_find_large_gaps():
    series = pd.Series([10.0, np.nan, np.nan, np.nan, np.nan, 20.0])
    series.index = pd.date_range("2020-01-01", periods=6, freq="MS")
    
    gaps = find_large_gaps(series, min_gap_months=4)
    assert len(gaps) == 1
    assert gaps[0]["months"] == 4
    assert gaps[0]["start"] == pd.Timestamp("2020-02-01")
    assert gaps[0]["end"] == pd.Timestamp("2020-05-01")


def test_verification_validates_correct_data():
    raw_df = pd.DataFrame({
        "date": ["2026-01-01"],
        "admin1": ["Mbeya"],
        "market": ["Mbeya Wholesale"],
        "commodity": ["Maize"],
        "pricetype": ["Wholesale"],
        "unit": ["100 KG"],
        "price": [70000.0]
    })
    
    # Assert validation passes (returns True)
    assert verify_raw_data(raw_df) is True


def test_verification_fails_on_corrupt_data():
    raw_df_corrupt = pd.DataFrame({
        "date": ["2026-01-01"],
        "admin1": ["Mbeya"],
        "price": [-500.0]  # Negative price!
    })
    
    with pytest.raises(ValueError):
        verify_raw_data(raw_df_corrupt)
