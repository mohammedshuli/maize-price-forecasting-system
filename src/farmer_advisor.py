# src/farmer_advisor.py
"""
Farmer Advisor Service.
This module is a presentation layer that translates the structured output from
 the decision engine into plain-language guidance for the dashboard.
"""

from typing import Any, Dict, List


def build_summary(decision: Dict[str, Any]) -> str:
    """Build a short summary message suitable for dashboard display."""
    action = decision.get("action", "SELL_NOW")
    reasons = decision.get("reasons", [])

    if action == "SELL_NOW":
        return "Market prices are expected to decline or remain unattractive, so selling soon is recommended."
    if action == "STORE_PARTIALLY":
        return "Market conditions suggest a cautious approach, so selling part of the harvest and storing the rest is advised."
    return "Market conditions appear favourable for storing maize for a later sale."


def build_reasoning(decision: Dict[str, Any]) -> str:
    """Translate the technical decision reasons into plain language."""
    reasons = decision.get("reasons", [])
    if not reasons:
        return "The recommendation is based on the current market and storage conditions."

    if any("declining" in reason.lower() for reason in reasons):
        return "The expected increase in price is unlikely to outweigh the risks of waiting."
    if any("loss" in reason.lower() for reason in reasons):
        return "The expected increase in price is unlikely to cover storage and transport costs."
    if any("moderate" in reason.lower() for reason in reasons):
        return "The outlook is mixed, so a balanced approach is more appropriate."
    return "The recommendation is based on the current market trend and the expected cost of storage."


def build_storage_advice(action: str) -> str:
    """Create practical storage advice based on the chosen action."""
    if action == "SELL_NOW":
        return "Sell through trusted buyers or cooperatives and compare offers before finalising the sale."
    if action == "STORE_PARTIALLY":
        return "Sell enough maize to meet urgent cash needs, then store the remainder in a clean, dry place."
    return "Dry the maize thoroughly, keep it in a clean and dry store, and inspect it regularly for pests or moisture."


def build_risk_message(risk_level: str) -> str:
    """Translate the technical risk level into farmer-friendly guidance."""
    normalized = (risk_level or "").strip().upper()
    if normalized == "LOW":
        return "The outlook is relatively stable, but market conditions can still change."
    if normalized == "MEDIUM":
        return "Prices may change unexpectedly. Monitor the market before making large decisions."
    return "There is considerable uncertainty. Avoid relying only on this forecast when making major decisions."


def build_action_plan(action: str) -> List[str]:
    """Create a simple step-by-step plan for the chosen action."""
    if action == "SELL_NOW":
        return [
            "Compare offers from local buyers or cooperatives.",
            "Sell within the next few weeks if the market remains favourable.",
            "Keep records of the sale and any transport costs.",
        ]
    if action == "STORE_PARTIALLY":
        return [
            "Set aside enough maize to meet immediate cash needs.",
            "Store the remaining maize in a clean, dry place.",
            "Review market conditions again after one month.",
        ]
    return [
        "Dry the maize thoroughly before storage.",
        "Store the maize using good storage practices and regular inspection.",
        "Review market prices again before deciding whether to sell.",
    ]


def build_farmer_message(decision: Dict[str, Any]) -> Dict[str, Any]:
    """Return a structured advisory message object for the dashboard."""
    action = decision.get("action", "SELL_NOW")
    risk_level = str(decision.get("risk_level", "High"))

    return {
        "summary": build_summary(decision),
        "recommendation": action,
        "reasoning": build_reasoning(decision),
        "storage_advice": build_storage_advice(action),
        "risk_message": build_risk_message(risk_level),
        "action_plan": build_action_plan(action),
    }


def generate_farmer_plan(
    bags: int,
    advice: Dict[str, Any],
    current_price_100kg: float,
    storage_type: str,
    cash_need: str,
    storage_cost: float = 0.0,
    transport_cost: float = 0.0,
) -> Dict[str, Any]:
    """
    Preserve the legacy bag-allocation output for compatibility with older dashboard usage.

    This function remains a compatibility wrapper and does not perform decision logic.
    """
    current_income = (current_price_100kg / 100) * 90 * bags

    if advice.get("utabiri_wa_bei") and len(advice["utabiri_wa_bei"]) > 0:
        next_price_90kg = advice["utabiri_wa_bei"][0]["per_gunia_90kg"]
    else:
        next_price_90kg = (current_price_100kg / 100) * 90

    wait_income = next_price_90kg * bags
    total_deductions = storage_cost + transport_cost
    difference = wait_income - current_income - total_deductions

    diff_label = "Faida" if difference >= 0 else "Hasara"
    is_profit = difference >= 0

    if cash_need == "Ndiyo":
        sell_now_bags = round(bags * 0.5, 1)
        keep_bags = round(bags - sell_now_bags, 1)
    else:
        action = advice.get("action", "UZA SASA")
        if action == "UZA SASA":
            sell_now_bags = float(bags)
            keep_bags = 0.0
        elif action == "SUBIRI KIDOGO":
            sell_now_bags = round(bags * 0.4, 1)
            keep_bags = round(bags - sell_now_bags, 1)
        else:
            sell_now_bags = round(bags * 0.2, 1)
            keep_bags = round(bags - sell_now_bags, 1)

    if storage_type == "Mifuko maalum":
        storage_advice = "Mahindi yanaweza kuhifadhiwa vizuri kwa kutumia mifuko maalum."
    elif storage_type == "Ghala":
        storage_advice = "Ghala linaweza kuwa chaguo bora ikiwa linadumishwa vizuri."
    else:
        storage_advice = "Kama utatumia magunia ya kawaida, hakikisha mahali pa kuhifadhi ni kavu."

    if advice.get("action") != "UZA SASA":
        market_note = "Bei inatoa nafasi nzuri kwa subira. Endelea kufuatilia soko."
    else:
        market_note = "Ikiwa unataka kuepuka hatari, kuuza sasa ni njia salama."

    return {
        "current_income": current_income,
        "wait_income": wait_income,
        "difference": difference,
        "diff_label": diff_label,
        "is_profit": is_profit,
        "sell_now_bags": sell_now_bags,
        "keep_bags": keep_bags,
        "storage_advice": storage_advice,
        "market_note": market_note,
        "total_deductions": total_deductions,
    }
