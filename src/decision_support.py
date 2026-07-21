# src/decision_support.py
"""
Decision Support Module.
Provides a simple staged decision engine for maize sales and storage advice.
The forecasting pipeline remains unchanged; this module converts forecast data
into market, economic, risk, and decision outputs.
"""

from datetime import datetime
from typing import Any, Dict, List

from config import (
    CASH_PRESSURE_DISCOUNT,
    HARVEST_MONTHS,
    STORAGE_LOSS_HERMETIC,
    STORAGE_LOSS_KAWAIDA,
    SWAHILI_MONTHS,
)


def to_farmer_units(price_per_100kg: float) -> Dict[str, float]:
    """
    Converts a 100kg wholesale price to standard farmer units:
    1kg price and 90kg gunia price.
    """
    price_per_kg = price_per_100kg / 100
    return {
        "per_kg": round(price_per_kg),
        "per_gunia_90kg": round(price_per_kg * 90),
    }


def analyze_forecast(
    current_date: datetime,
    current_price_100kg: float,
    forecast_dates: List[datetime],
    forecast_prices_100kg: List[float],
) -> Dict[str, Any]:
    """
    Analyses the forecast series and produces a structured market summary.

    Parameters:
        current_date: Most recent observed date.
        current_price_100kg: Current wholesale price per 100kg.
        forecast_dates: Sequence of forecast dates.
        forecast_prices_100kg: Forecast prices for each date.

    Returns:
        A dictionary containing current price, average forecast, trend direction,
        and the strongest and weakest expected months.
    """
    if not forecast_prices_100kg:
        raise ValueError("Forecast prices cannot be empty.")

    current_price = float(current_price_100kg)
    forecast_prices = [float(price) for price in forecast_prices_100kg]
    average_forecast = sum(forecast_prices) / len(forecast_prices)

    if current_price <= 0:
        percentage_change_pct = 0.0
    else:
        percentage_change_pct = ((average_forecast - current_price) / current_price) * 100

    if percentage_change_pct > 2.0:
        trend_direction = "Increasing"
    elif percentage_change_pct < -2.0:
        trend_direction = "Decreasing"
    else:
        trend_direction = "Stable"

    strongest_month_index = max(range(len(forecast_prices)), key=forecast_prices.__getitem__)
    weakest_month_index = min(range(len(forecast_prices)), key=forecast_prices.__getitem__)

    strongest_month = forecast_dates[strongest_month_index] if forecast_dates else None
    weakest_month = forecast_dates[weakest_month_index] if forecast_dates else None

    return {
        "current_price_100kg": current_price,
        "average_forecast_price": round(average_forecast, 2),
        "average_forecast_price_100kg": round(average_forecast, 2),
        "percentage_change_pct": round(percentage_change_pct, 2),
        "trend_direction": trend_direction,
        "strongest_month": strongest_month,
        "weakest_month": weakest_month,
        "strongest_month_price_100kg": round(forecast_prices[strongest_month_index], 2),
        "weakest_month_price_100kg": round(forecast_prices[weakest_month_index], 2),
        "is_harvest_season": getattr(current_date, "month", None) in HARVEST_MONTHS,
        "volatility_pct": round(abs(percentage_change_pct) / 100.0, 4),
    }


def evaluate_economics(
    current_price_100kg: float,
    forecast_prices_100kg: List[float],
    storage_duration_months: int = 3,
    storage_cost: float = 0.0,
    transport_cost: float = 0.0,
    storage_quality: str = "kawaida",
) -> Dict[str, Any]:
    """
    Evaluates whether storing maize for a number of months is financially worthwhile.

    Parameters:
        current_price_100kg: Current wholesale price per 100kg.
        forecast_prices_100kg: Forecast prices for each period.
        storage_duration_months: Number of months to store.
        storage_cost: Explicit storage cost in local currency.
        transport_cost: Explicit transport cost in local currency.
        storage_quality: Storage system category used to estimate expected losses.

    Returns:
        A structured economic assessment including expected revenue, losses, and net benefit.
    """
    if not forecast_prices_100kg:
        raise ValueError("Forecast prices cannot be empty.")

    current_price = float(current_price_100kg)
    storage_loss_pct = (
        STORAGE_LOSS_KAWAIDA if storage_quality == "kawaida" else STORAGE_LOSS_HERMETIC
    )

    target_index = min(storage_duration_months - 1, len(forecast_prices_100kg) - 1)
    future_price = float(forecast_prices_100kg[target_index])

    revenue_if_sold_now = current_price
    revenue_if_stored = future_price
    storage_loss_value = revenue_if_stored * storage_loss_pct
    total_storage_expense = storage_cost + transport_cost + storage_loss_value
    expected_net_benefit_100kg = revenue_if_stored - revenue_if_sold_now - total_storage_expense
    expected_net_benefit_pct = (
        (expected_net_benefit_100kg / current_price) * 100 if current_price else 0.0
    )

    return {
        "revenue_if_sold_now_100kg": round(revenue_if_sold_now, 2),
        "revenue_if_stored_100kg": round(revenue_if_stored, 2),
        "storage_loss_pct": storage_loss_pct,
        "storage_loss_value": round(storage_loss_value, 2),
        "storage_cost": round(storage_cost, 2),
        "transport_cost": round(transport_cost, 2),
        "total_storage_expense": round(total_storage_expense, 2),
        "expected_net_benefit_100kg": round(expected_net_benefit_100kg, 2),
        "expected_net_benefit_pct": round(expected_net_benefit_pct, 2),
        "expected_profit_or_loss": "Profit" if expected_net_benefit_100kg > 0 else "Loss",
        "storage_duration_months": storage_duration_months,
    }


def assess_risk(
    uncertainty_width_pct: float,
    storage_loss_pct: float,
    volatility_pct: float,
    profitability_pct: float,
) -> Dict[str, Any]:
    """
    Evaluates the overall risk of waiting based on uncertainty, storage loss,
    volatility, and profitability.

    Returns:
        A dictionary with a numeric risk score, a categorical risk level, and explanation.
    """
    uncertainty_component = max(0.0, float(uncertainty_width_pct))
    storage_component = max(0.0, float(storage_loss_pct))
    volatility_component = max(0.0, float(volatility_pct))
    profitability_component = max(0.0, -float(profitability_pct) / 100.0)

    risk_score = min(
        100.0,
        (uncertainty_component + storage_component + volatility_component + profitability_component) * 100.0,
    )

    if risk_score > 70.0:
        risk_level = "High"
    elif risk_score > 40.0:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if risk_level == "High":
        explanation = (
            "The combination of large uncertainty, storage loss, and weak profitability makes waiting risky."
        )
    elif risk_level == "Medium":
        explanation = (
            "There is a moderate chance that waiting could be worthwhile, but the outcome remains uncertain."
        )
    else:
        explanation = (
            "The forecast and cost assumptions suggest that waiting is relatively safe."
        )

    return {
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "explanation": explanation,
    }


def generate_decision(
    market_analysis: Dict[str, Any],
    economic_analysis: Dict[str, Any],
    risk_assessment: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Combines the market, economic, and risk analyses into a single recommendation.

    Returns:
        A structured decision object with an action and explicit reasons.
    """
    reasons: List[str] = []

    if market_analysis["trend_direction"] == "Decreasing":
        reasons.append("The forecast trend is declining.")
    elif market_analysis["trend_direction"] == "Increasing":
        reasons.append("The forecast trend is improving.")
    else:
        reasons.append("The forecast trend is broadly stable.")

    if economic_analysis["expected_profit_or_loss"] == "Loss":
        reasons.append("The expected storage outcome is a loss after storage and transport costs.")
    else:
        reasons.append("The expected storage outcome remains profitable after costs.")

    if risk_assessment["risk_level"] == "High":
        reasons.append("Risk is high because uncertainty and storage exposure are significant.")
    elif risk_assessment["risk_level"] == "Medium":
        reasons.append("Risk is moderate, so a partial approach is more robust.")
    else:
        reasons.append("Risk is low, so waiting is acceptable.")

    if risk_assessment["risk_level"] == "High" or economic_analysis["expected_net_benefit_pct"] <= 0:
        action = "SELL_NOW"
    elif risk_assessment["risk_level"] == "Medium" or economic_analysis["expected_net_benefit_pct"] < 5.0:
        action = "STORE_PARTIALLY"
    else:
        action = "STORE"

    return {
        "action": action,
        "reasons": reasons,
        "market_trend": market_analysis["trend_direction"],
        "economic_outcome": economic_analysis["expected_profit_or_loss"],
        "risk_level": risk_assessment["risk_level"],
    }


def explain_decision(
    decision: Dict[str, Any],
    market_analysis: Dict[str, Any],
    economic_analysis: Dict[str, Any],
    risk_assessment: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Translates the staged decision into a structured explanation object.

    Returns:
        A dictionary suitable for later use by the dashboard or other presentation layers.
    """
    if decision["action"] == "SELL_NOW":
        expected_outcome = (
            "Selling now is expected to avoid further losses and reduce exposure to uncertainty."
        )
    elif decision["action"] == "STORE_PARTIALLY":
        expected_outcome = (
            "A partial storage strategy balances expected future gains against storage and uncertainty risks."
        )
    else:
        expected_outcome = (
            "Storing the crop is expected to produce a positive net benefit after costs."
        )

    return {
        "recommendation": decision["action"],
        "reasons": decision["reasons"],
        "expected_outcome": expected_outcome,
        "assumptions_used": [
            "Forecast prices are treated as the main signal for future market value.",
            "Storage loss is estimated using the selected storage quality.",
            "Transport and storage costs are included in the economic assessment.",
        ],
        "important_cautions": [
            "Forecasts are uncertain and can change over time.",
            "Actual market conditions may differ from the forecast.",
            "The decision is based on the current assumptions and should be revisited regularly.",
        ],
        "market_summary": market_analysis,
        "economic_summary": economic_analysis,
        "risk_summary": risk_assessment,
    }


def get_recommendation(
    current_date: datetime,
    current_price_100kg: float,
    forecast_dates: List[datetime],
    forecast_prices_100kg: List[float],
    ci_lower_1m_100kg: float,
    ci_upper_1m_100kg: float,
    storage_quality: str = "kawaida",
) -> Dict[str, Any]:
    """
    Formulates a selling recommendation based on current price, forecasted price,
    seasonal discount, and prediction intervals.

    This function preserves the legacy output structure while using the new staged engine internally.
    """
    market_analysis = analyze_forecast(
        current_date=current_date,
        current_price_100kg=current_price_100kg,
        forecast_dates=forecast_dates,
        forecast_prices_100kg=forecast_prices_100kg,
    )
    economic_analysis = evaluate_economics(
        current_price_100kg=current_price_100kg,
        forecast_prices_100kg=forecast_prices_100kg,
        storage_duration_months=3,
        storage_cost=0.0,
        transport_cost=0.0,
        storage_quality=storage_quality,
    )

    ci_width_pct = (
        (ci_upper_1m_100kg - ci_lower_1m_100kg) / current_price_100kg if current_price_100kg else 0.0
    )
    risk_assessment = assess_risk(
        uncertainty_width_pct=ci_width_pct,
        storage_loss_pct=economic_analysis["storage_loss_pct"],
        volatility_pct=market_analysis["volatility_pct"],
        profitability_pct=economic_analysis["expected_net_benefit_pct"],
    )
    decision = generate_decision(market_analysis, economic_analysis, risk_assessment)

    if decision["action"] == "SELL_NOW":
        action = "UZA SASA"
        message_sw = (
            "Bei ni hatarishi na uwezekano wa kupungua ni mkubwa. "
            "Kulingana na data, ni busara kuuza sasa ukitaka kupunguza hatari."
        )
        risk_level = "high"
    elif decision["action"] == "STORE_PARTIALLY":
        action = "SUBIRI KIDOGO"
        message_sw = (
            "Kuna mtazamo wa kupanda kidogo, lakini usipoteze macho. "
            "Kuhifadhi kwa hali nzuri na uangalie soko ni muhimu."
        )
        risk_level = "medium"
    else:
        action = "SUBIRI ZAIDI"
        message_sw = (
            "Mwelekeo wa bei unatisha na kuna nafasi nzuri ya faida. "
            "Hifadhi vizuri na usikimbilie kuuza mapema."
        )
        risk_level = "low"

    monthly_forecasts = []
    for date, price in zip(forecast_dates, forecast_prices_100kg):
        month_name = SWAHILI_MONTHS[date.month]
        year = date.year
        units = to_farmer_units(price)
        monthly_forecasts.append(
            {
                "mwezi": f"{month_name} {year}",
                "per_kg": units["per_kg"],
                "per_gunia_90kg": units["per_gunia_90kg"],
            }
        )

    gain_1m = (forecast_prices_100kg[0] - current_price_100kg) / current_price_100kg if current_price_100kg else 0.0
    gain_3m = (
        forecast_prices_100kg[2] - current_price_100kg
    ) / current_price_100kg if len(forecast_prices_100kg) > 2 and current_price_100kg else 0.0

    return {
        "action": action,
        "message_sw": message_sw,
        "bei_ya_sasa": to_farmer_units(current_price_100kg),
        "utabiri_wa_bei": monthly_forecasts,
        "gain_1m_pct": round(gain_1m * 100, 1),
        "gain_3m_pct": round(gain_3m * 100, 1),
        "storage_loss_assumed_pct": round(economic_analysis["storage_loss_pct"] * 100, 1),
        "risk_level": risk_level,
    }