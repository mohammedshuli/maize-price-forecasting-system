# ==========================================================
# MAIZE PRICE FORECASTING AND DECISION SUPPORT SYSTEM
#
# Decision Support Engine
#
# This module transforms SARIMA forecasts into practical,
# farmer-oriented recommendations.
#
# Pipeline
#
# Forecast
#      ↓
# Market Analysis
#      ↓
# Economic Analysis
#      ↓
# Risk Analysis
#      ↓
# Decision Generation
#      ↓
# Farmer Explanation
#
# NOTE:
# This module DOES NOT perform forecasting.
# Forecasts are generated elsewhere.
# ==========================================================

from datetime import datetime
from statistics import mean
from typing import Any, Dict, List

from config import (
    CASH_PRESSURE_DISCOUNT,
    HARVEST_MONTHS,
    STORAGE_LOSS_HERMETIC,
    STORAGE_LOSS_KAWAIDA,
    SWAHILI_MONTHS,
)


# ==========================================================
# PRICE CONVERSION
# ==========================================================

def to_farmer_units(price_per_100kg: float) -> Dict[str, float]:
    """
    Convert wholesale prices into units familiar
    to Tanzanian farmers.
    """

    per_kg = price_per_100kg / 100

    return {

        "per_100kg": round(price_per_100kg),

        "per_kg": round(per_kg),

        "per_gunia_90kg": round(per_kg * 90),

    }


# ==========================================================
# MONTH FORMATTER
# ==========================================================

def format_month(date: datetime) -> str:
    """
    Convert datetime into
    Swahili month name.
    """

    return f"{SWAHILI_MONTHS[date.month]} {date.year}"


# ==========================================================
# PERCENT CHANGE
# ==========================================================

def percentage_change(old: float, new: float) -> float:

    if old <= 0:

        return 0.0

    return ((new - old) / old) * 100


# ==========================================================
# VOLATILITY
# ==========================================================

def calculate_volatility(values: List[float]) -> float:
    """
    Simple volatility estimate.

    Higher value
    =
    Less predictable market.
    """

    if len(values) < 2:

        return 0.0

    return (
        (max(values) - min(values))
        / mean(values)
    ) * 100


# ==========================================================
# MARKET SIGNAL
# ==========================================================

def classify_market_signal(change_pct: float) -> str:
    """
    Convert percentage change
    into a human-readable
    market signal.
    """

    if change_pct >= 8:

        return "Strongly Increasing"

    if change_pct >= 3:

        return "Increasing"

    if change_pct <= -8:

        return "Strongly Decreasing"

    if change_pct <= -3:

        return "Decreasing"

    return "Stable"

# ==========================================================
# FORECAST ANALYSIS
# ==========================================================

def analyze_forecast(
    current_date: datetime,
    current_price_100kg: float,
    forecast_dates: List[datetime],
    forecast_prices_100kg: List[float],
) -> Dict[str, Any]:
    """
    Analyse forecast prices and generate
    a structured market summary.

    This function performs NO decision making.

    It only describes the expected market.
    """

    if len(forecast_prices_100kg) == 0:

        raise ValueError(
            "Forecast prices cannot be empty."
        )

    current_price = float(current_price_100kg)

    prices = [
        float(x)
        for x in forecast_prices_100kg
    ]

    avg_price = mean(prices)

    change_pct = percentage_change(
        current_price,
        avg_price,
    )

    trend = classify_market_signal(
        change_pct
    )

    volatility = calculate_volatility(
        prices
    )

    highest_index = prices.index(
        max(prices)
    )

    lowest_index = prices.index(
        min(prices)
    )

    highest_date = forecast_dates[
        highest_index
    ]

    lowest_date = forecast_dates[
        lowest_index
    ]

    highest_price = prices[
        highest_index
    ]

    lowest_price = prices[
        lowest_index
    ]

    if volatility < 3:

        stability = "Stable"

    elif volatility < 8:

        stability = "Moderate"

    else:

        stability = "Unstable"

    if trend == "Strongly Increasing":

        market_message = (
            "Bei zinaonesha dalili nzuri za kuongezeka."
        )

    elif trend == "Increasing":

        market_message = (
            "Bei zinaonekana kupanda taratibu."
        )

    elif trend == "Strongly Decreasing":

        market_message = (
            "Bei zinaonesha mwelekeo mkubwa wa kushuka."
        )

    elif trend == "Decreasing":

        market_message = (
            "Bei zinaonekana kushuka kidogo."
        )

    else:

        market_message = (
            "Bei zinatarajiwa kubaki karibu na kiwango cha sasa."
        )

    return {

        "current_price_100kg":
            round(current_price, 2),

        "average_forecast_price":
            round(avg_price, 2),

        "average_forecast_price_100kg":
            round(avg_price, 2),

        "percentage_change_pct":
            round(change_pct, 2),

        "trend_direction":
            trend,

        "market_signal":
            trend,

        "market_message":
            market_message,

        "volatility_pct":
            round(volatility, 2),

        "market_stability":
            stability,

        "best_month":
            format_month(highest_date),

        "best_month_price":
            round(highest_price, 2),

        "worst_month":
            format_month(lowest_date),

        "worst_month_price":
            round(lowest_price, 2),

        "strongest_month":
            highest_date,

        "weakest_month":
            lowest_date,

        "strongest_month_price_100kg":
            round(highest_price, 2),

        "weakest_month_price_100kg":
            round(lowest_price, 2),

        "is_harvest_season":
            current_date.month in HARVEST_MONTHS,

        "forecast_prices":
            prices,

        "forecast_dates":
            forecast_dates,

    }
    
    # ==========================================================
# ECONOMIC ANALYSIS
# ==========================================================

def evaluate_economics(
    current_price_100kg: float,
    forecast_prices_100kg: List[float],
    storage_duration_months: int = 3,
    storage_cost: float = 0.0,
    transport_cost: float = 0.0,
    storage_quality: str = "kawaida",
) -> Dict[str, Any]:
    """
    Evaluate the financial impact of storing maize.

    This function estimates whether waiting
    is economically worthwhile after
    considering storage losses and costs.

    It performs NO recommendation.
    """

    if len(forecast_prices_100kg) == 0:

        raise ValueError(
            "Forecast prices cannot be empty."
        )

    current_price = float(
        current_price_100kg
    )

    future_index = min(
        storage_duration_months - 1,
        len(forecast_prices_100kg) - 1
    )

    future_price = float(
        forecast_prices_100kg[future_index]
    )

    # --------------------------------------------------
    # Storage losses
    # --------------------------------------------------

    if storage_quality.lower() == "kawaida":

        storage_loss_pct = STORAGE_LOSS_KAWAIDA

    else:

        storage_loss_pct = STORAGE_LOSS_HERMETIC

    storage_loss_value = (
        future_price
        * storage_loss_pct
    )

    # --------------------------------------------------
    # Revenue estimates
    # --------------------------------------------------

    revenue_now = current_price

    revenue_future = future_price

    total_cost = (

        storage_cost

        + transport_cost

        + storage_loss_value

    )

    expected_net = (

        revenue_future

        - revenue_now

        - total_cost

    )

    expected_net_pct = percentage_change(

        revenue_now,

        revenue_future - total_cost,

    )

    # --------------------------------------------------
    # Financial interpretation
    # --------------------------------------------------

    if expected_net > 0:

        outcome = "Profit"

    else:

        outcome = "Loss"

    if expected_net_pct >= 10:

        attractiveness = "Very Good"

    elif expected_net_pct >= 5:

        attractiveness = "Good"

    elif expected_net_pct >= 0:

        attractiveness = "Marginal"

    else:

        attractiveness = "Poor"

    roi = 0.0

    if total_cost > 0:

        roi = (

            expected_net

            / total_cost

        ) * 100

    return {

        "revenue_if_sold_now_100kg":
            round(revenue_now, 2),

        "revenue_if_stored_100kg":
            round(revenue_future, 2),

        "storage_loss_pct":
            storage_loss_pct,

        "storage_loss_value":
            round(storage_loss_value, 2),

        "storage_cost":
            round(storage_cost, 2),

        "transport_cost":
            round(transport_cost, 2),

        "total_storage_expense":
            round(total_cost, 2),

        "expected_net_benefit_100kg":
            round(expected_net, 2),

        "expected_net_benefit_pct":
            round(expected_net_pct, 2),

        "expected_profit_or_loss":
            outcome,

        "economic_attractiveness":
            attractiveness,

        "return_on_storage_pct":
            round(roi, 2),

        "storage_duration_months":
            storage_duration_months,

    }
    
    # ==========================================================
# RISK ASSESSMENT
# ==========================================================

def assess_risk(
    uncertainty_width_pct: float,
    storage_loss_pct: float,
    volatility_pct: float,
    profitability_pct: float,
) -> Dict[str, Any]:
    """
    Assess the overall risk of waiting before selling maize.

    Risk is based on four components:

    • Forecast uncertainty
    • Storage losses
    • Market volatility
    • Expected profitability

    This function performs NO recommendation.
    """

    uncertainty = max(
        0.0,
        float(uncertainty_width_pct)
    )

    storage = max(
        0.0,
        float(storage_loss_pct) * 100
    )

    volatility = max(
        0.0,
        float(volatility_pct)
    )

    profitability_penalty = max(
        0.0,
        -float(profitability_pct)
    )

    # --------------------------------------------------
    # Weighted score
    # --------------------------------------------------

    risk_score = (

        uncertainty * 0.35

        + storage * 0.20

        + volatility * 0.20

        + profitability_penalty * 0.25

    )

    risk_score = min(
        round(risk_score, 2),
        100.0
    )

    # --------------------------------------------------
    # Risk classification
    # --------------------------------------------------

    if risk_score < 25:

        risk_level = "Low"

    elif risk_score < 50:

        risk_level = "Medium"

    elif risk_score < 75:

        risk_level = "High"

    else:

        risk_level = "Very High"

    # --------------------------------------------------
    # Farmer explanation
    # --------------------------------------------------

    if risk_level == "Low":

        explanation = (
            "Hatari ya kusubiri ni ndogo. "
            "Iwapo utahifadhi mahindi vizuri, "
            "nafasi ya kupata matokeo mazuri ipo."
        )

    elif risk_level == "Medium":

        explanation = (
            "Kuna hatari ya wastani. "
            "Ni vizuri kuendelea kufuatilia "
            "bei za soko kabla ya kufanya uamuzi."
        )

    elif risk_level == "High":

        explanation = (
            "Hatari ya kusubiri ni kubwa. "
            "Mabadiliko ya soko au gharama "
            "za kuhifadhi zinaweza kupunguza faida."
        )

    else:

        explanation = (
            "Hatari ni kubwa sana. "
            "Kusubiri kunaweza kusababisha "
            "hasara ikiwa hali ya soko itabadilika."
        )

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------

    confidence = max(
        40,
        round(100 - risk_score)
    )

    return {

        "risk_score":
            risk_score,

        "risk_level":
            risk_level,

        "confidence":
            confidence,

        "uncertainty_component":
            round(uncertainty, 2),

        "storage_component":
            round(storage, 2),

        "volatility_component":
            round(volatility, 2),

        "profitability_component":
            round(profitability_penalty, 2),

        "explanation":
            explanation,

    }
    
    # ==========================================================
# DECISION ENGINE
# ==========================================================

def generate_decision(
    market_analysis: Dict[str, Any],
    economic_analysis: Dict[str, Any],
    risk_assessment: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Determine the most appropriate action for the farmer.

    Possible actions

    • SELL_NOW
    • STORE
    • STORE_PARTIALLY

    This function performs decision logic only.
    """

    price_change = market_analysis["percentage_change_pct"]

    expected_profit = economic_analysis["expected_net_benefit_100kg"]

    risk = risk_assessment["risk_level"]

    reasons = []

    # --------------------------------------------------
    # SELL NOW
    # --------------------------------------------------

    if expected_profit <= 0:

        action = "SELL_NOW"

        reasons.append(
            "Kusubiri hakutegemewi kuongeza faida baada ya gharama za uhifadhi."
        )

    elif risk == "HIGH":

        action = "SELL_NOW"

        reasons.append(
            "Hatari ya kusubiri ni kubwa kuliko faida inayotarajiwa."
        )

    # --------------------------------------------------
    # STORE
    # --------------------------------------------------

    elif price_change >= 5 and risk == "LOW":

        action = "STORE"

        reasons.append(
            "Bei zinatarajiwa kuongezeka kwa kiwango kinachoweza kuongeza mapato."
        )

    # --------------------------------------------------
    # STORE PARTIALLY
    # --------------------------------------------------

    else:

        action = "STORE_PARTIALLY"

        reasons.append(
            "Faida inaweza kupatikana lakini bado kuna hatari fulani ya soko."
        )

    return {

        "action": action,

        "reasons": reasons,

        "risk_level": risk,

        "expected_price_change_pct": round(price_change, 2),

        "expected_net_benefit_100kg":
            economic_analysis["expected_net_benefit_100kg"],

        "expected_net_benefit_pct":
            economic_analysis["expected_net_benefit_pct"],

        "storage_cost":
            economic_analysis["total_storage_expense"],

    }
    
    # ==========================================================
# DECISION EXPLANATION
# ==========================================================

def explain_decision(
    decision: Dict[str, Any],
    market_analysis: Dict[str, Any],
    economic_analysis: Dict[str, Any],
    risk_assessment: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert the technical recommendation into structured
    information that can be displayed by the dashboard.

    This function does NOT make decisions.
    It only explains the result produced by
    generate_decision().
    """

    action = decision["action"]

    price_change = market_analysis["percentage_change_pct"]

    risk = risk_assessment["risk_level"]

    net_benefit = economic_analysis["expected_net_benefit_100kg"]

    # --------------------------------------------------
    # WHY THIS RECOMMENDATION?
    # --------------------------------------------------

    if action == "SELL_NOW":

        why = (
            "Bei zinazotarajiwa katika miezi ijayo zinafanana "
            "au ziko chini ya bei ya sasa. Kusubiri kunaweza "
            "kuongeza gharama za kuhifadhi bila kuongeza faida."
        )

        expected = (
            "Kwa kuuza sasa utaepuka gharama za kuhifadhi na "
            "kupunguza hatari ya kushuka kwa bei."
        )

    elif action == "STORE":

        why = (
            "Mfumo unaonyesha kuwa bei zinaweza kuongezeka kwa "
            "kiwango kinachoweza kufidia gharama za kuhifadhi."
        )

        expected = (
            "Ukihifadhi vizuri mahindi yako unaweza kuuza kwa "
            "bei nzuri zaidi katika miezi ijayo."
        )

    else:

        why = (
            "Kuna nafasi ya bei kuongezeka, lakini bado kuna "
            "kutokuwa na uhakika. Kuuza sehemu na kuhifadhi "
            "sehemu nyingine hupunguza hatari."
        )

        expected = (
            "Utapata fedha za matumizi ya sasa huku ukibakiza "
            "nafasi ya kunufaika endapo bei zitapanda."
        )

    # --------------------------------------------------
    # RISK EXPLANATION
    # --------------------------------------------------

    if risk == "LOW":

        risk_message = (
            "Hatari ni ndogo kutokana na utulivu wa mwenendo wa soko."
        )

    elif risk == "MEDIUM":

        risk_message = (
            "Soko linaweza kubadilika, hivyo endelea kufuatilia "
            "bei kabla ya kufanya maamuzi makubwa."
        )

    else:

        risk_message = (
            "Kuna uwezekano mkubwa wa mabadiliko ya bei. "
            "Inashauriwa kufuatilia taarifa mpya za soko mara kwa mara."
        )

    # --------------------------------------------------
    # SYSTEM FACTORS
    # --------------------------------------------------

    assumptions = [

        "Bei ya sasa ya soko.",

        "Utabiri wa bei kwa miezi mitatu ijayo.",

        "Gharama za kuhifadhi.",

        "Hatari zinazoweza kutokea wakati wa kusubiri.",

        "Makadirio ya faida baada ya gharama.",

    ]

    return {

        "why": why,

        "expected_outcome": expected,

        "risk_explanation": risk_message,

        "system_factors": assumptions,

    }