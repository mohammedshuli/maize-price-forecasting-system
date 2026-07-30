"""
==========================================================
MAIZE PRICE FORECASTING AND DECISION SUPPORT SYSTEM

Farmer Advisory Service

This module is responsible ONLY for communicating the
decision engine results in farmer-friendly language.

It DOES NOT:

• calculate forecasts
• calculate profitability
• calculate risks
• make business decisions

It ONLY converts structured decision outputs into
clear, practical advice that a farmer can easily
understand.

==========================================================
"""

from typing import Any, Dict, List


# ==========================================================
# COMMON TEXT LIBRARY
# ==========================================================

ACTION_LABELS = {
    "SELL_NOW": "UZA SASA",
    "STORE": "HIFADHI MAHINDI",
    "STORE_PARTIALLY": "UZA SEHEMU, HIFADHI SEHEMU",
}


RISK_LABELS = {
    "LOW": "Hatari ni ndogo",
    "MEDIUM": "Hatari ni ya wastani",
    "HIGH": "Hatari ni kubwa",
}


# ==========================================================
# HELPER
# ==========================================================

def normalize_action(action: str) -> str:
    """
    Ensure an action always has a valid value.
    """

    if not action:
        return "SELL_NOW"

    return action.strip().upper()


def normalize_risk(risk: str) -> str:
    """
    Normalize risk level.
    """

    if not risk:
        return "MEDIUM"

    return risk.strip().upper()

# ==========================================================
# SUMMARY MESSAGE
# ==========================================================

def build_summary(decision: Dict[str, Any]) -> str:
    """
    Build the first message shown to the farmer.

    This should answer one question:

    "Kwa ujumla nifanye nini?"
    """

    action = normalize_action(
        decision.get("action")
    )

    if action == "SELL_NOW":

        return (
            "Kwa kuzingatia hali ya soko kwa sasa pamoja na "
            "utabiri wa bei kwa miezi ijayo, mfumo unapendekeza "
            "uuze mahindi yako mapema ili kuepuka gharama za "
            "kuhifadhi ambazo zinaweza zisirudishwe na ongezeko "
            "la bei linalotarajiwa."
        )

    elif action == "STORE_PARTIALLY":

        return (
            "Kwa hali ya sasa ya soko, ni busara kuuza sehemu "
            "ya mahindi yako ili kupata fedha za matumizi ya "
            "haraka, huku ukihifadhi sehemu iliyobaki kusubiri "
            "mabadiliko ya bei katika kipindi kijacho."
        )

    elif action == "STORE":

        return (
            "Uchambuzi unaonyesha kuwa kuna uwezekano wa bei "
            "kuongezeka katika miezi ijayo. Ikiwa una sehemu "
            "nzuri ya kuhifadhi mahindi, unaweza kusubiri kabla "
            "ya kuuza ili kuongeza mapato."
        )

    return (
        "Mfumo haukuweza kubaini mapendekezo mahsusi. "
        "Endelea kufuatilia taarifa za soko kabla ya kufanya "
        "uamuzi wa kuuza au kuhifadhi mahindi yako."
    )
    
    # ==========================================================
# WHY THIS RECOMMENDATION?
# ==========================================================

def build_reasoning(decision: Dict[str, Any]) -> str:
    """
    Explain WHY the recommendation was made.

    This text should read as if an agricultural extension
    officer is explaining the situation to the farmer.
    """

    action = normalize_action(
        decision.get("action")
    )

    reasons = decision.get("reasons", [])

    if action == "SELL_NOW":

        return (
            "Mfumo umebaini kuwa ongezeko la bei "
            "linalotarajiwa katika miezi ijayo ni dogo "
            "ukilinganisha na gharama pamoja na hatari za "
            "kuhifadhi mahindi kwa muda mrefu. Kwa hali hii, "
            "kuuza mapema kunaweza kukusaidia kupata thamani "
            "nzuri ya mazao yako na kupunguza uwezekano wa "
            "kupata hasara endapo bei zitashuka."
        )

    elif action == "STORE":

        return (
            "Utabiri unaonyesha kuwa bei zinaweza kuongezeka "
            "katika kipindi kijacho. Ikiwa una sehemu salama "
            "ya kuhifadhi mahindi na huhitaji fedha kwa haraka, "
            "kusubiri kwa muda kunaweza kuongeza mapato "
            "utakapouza baadaye."
        )

    elif action == "STORE_PARTIALLY":

        return (
            "Hali ya soko haionyeshi faida kubwa ya kuuza yote "
            "wala kuhifadhi yote. Kwa hiyo, kuuza sehemu ya "
            "mahindi ili kukidhi mahitaji ya sasa na kuhifadhi "
            "sehemu iliyobaki ni njia nzuri ya kupunguza "
            "hatari huku ukibaki na nafasi ya kunufaika endapo "
            "bei zitaongezeka."
        )

    if reasons:

        return (
            "Mapendekezo haya yametolewa baada ya kuchambua "
            "hali ya sasa ya soko, utabiri wa bei pamoja na "
            "gharama zinazoweza kujitokeza wakati wa kuhifadhi "
            "mahindi."
        )

    return (
        "Mfumo umefanya uchambuzi wa taarifa ulizoingiza na "
        "kulinganisha na mwenendo wa soko ili kukupa ushauri "
        "unaoweza kukusaidia kufanya uamuzi bora."
    )
    
    # ==========================================================
# STORAGE AND MARKETING ADVICE
# ==========================================================

def build_storage_advice(action: str) -> str:
    """
    Provide practical advice that a farmer can immediately use.
    """

    action = normalize_action(action)

    if action == "SELL_NOW":

        return (
            "Tafuta wanunuzi tofauti kabla ya kuuza ili "
            "ulinganishe bei. Ikiwezekana, uliza bei kwa "
            "vyama vya ushirika, wafanyabiashara wa eneo lako "
            "au masoko makubwa kabla ya kufanya uamuzi wa mwisho."
        )

    elif action == "STORE_PARTIALLY":

        return (
            "Unaweza kuuza sehemu ya mahindi yako ili kupata "
            "fedha za matumizi ya sasa, kisha uhifadhi sehemu "
            "iliyobaki mahali pakavu na salama. Njia hii "
            "inakusaidia kupunguza hatari na bado kubaki na "
            "nafasi ya kunufaika endapo bei zitaongezeka."
        )

    elif action == "STORE":

        return (
            "Kabla ya kuhifadhi, hakikisha mahindi yamekauka "
            "vizuri. Tumia njia salama za uhifadhi kama "
            "mifuko ya PICS, silo ya chuma au ghala safi "
            "lisilo na unyevunyevu. Kagua mahindi mara kwa "
            "mara ili kuzuia wadudu na upotevu wa mazao."
        )

    return (
        "Endelea kufuatilia taarifa za soko na hakikisha "
        "mahindi yako yanahifadhiwa vizuri ili kupunguza "
        "upotevu wa mazao."
    )
    
    # ==========================================================
# RISK EXPLANATION
# ==========================================================

def build_risk_message(risk_level: str) -> str:
    """
    Explain the level of risk in language that is easy for
    farmers to understand.
    """

    risk = normalize_risk(risk_level)

    if risk == "LOW":

        return (
            "Kwa sasa hatari ya kufanya uamuzi huu ni ndogo. "
            "Hata hivyo, bei za mazao zinaweza kubadilika wakati "
            "wowote kutokana na mabadiliko ya soko, hali ya hewa "
            "au mahitaji ya wanunuzi. Endelea kufuatilia taarifa "
            "za soko mara kwa mara."
        )

    elif risk == "MEDIUM":

        return (
            "Kuna uwezekano wa mabadiliko ya bei katika kipindi "
            "kijacho. Ingawa ushauri huu unaonyesha njia nzuri ya "
            "kufuata, ni muhimu kuendelea kufuatilia taarifa za "
            "soko kabla ya kufanya uamuzi wa mwisho."
        )

    elif risk == "HIGH":

        return (
            "Hali ya soko inaonyesha kutokuwa na uhakika mkubwa. "
            "Bei zinaweza kubadilika haraka kutokana na sababu "
            "kama hali ya hewa, uzalishaji, sera za serikali au "
            "mahitaji ya soko. Ikiwezekana, usifanye maamuzi "
            "makubwa kwa kutegemea utabiri pekee."
        )

    return (
        "Hatari haikuweza kutathminiwa kikamilifu. "
        "Endelea kufuatilia taarifa za soko na ushauri wa "
        "maafisa ugani kabla ya kufanya maamuzi muhimu."
    )
    
    # ==========================================================
# PRACTICAL ACTION PLAN
# ==========================================================

def build_action_plan(action: str) -> List[str]:
    """
    Build a practical step-by-step action plan for the farmer.

    These are the immediate actions the farmer should take
    after receiving the recommendation.
    """

    action = normalize_action(action)

    # ------------------------------------------------------

    if action == "SELL_NOW":

        return [

            "Tembelea wanunuzi au masoko zaidi ya moja ili kulinganisha bei kabla ya kuuza.",

            "Kama bei ni nzuri katika eneo lako, uza mahindi ndani ya kipindi kifupi badala ya kusubiri bila sababu.",

            "Panga usafiri mapema ili kupunguza gharama za kusafirisha mazao.",

            "Hifadhi kumbukumbu za kiasi ulichouza, bei uliyopata na gharama ulizotumia.",

            "Endelea kufuatilia taarifa za soko kwa msimu ujao."

        ]

    # ------------------------------------------------------

    elif action == "STORE_PARTIALLY":

        return [

            "Uza kiasi cha mahindi kitakachokidhi mahitaji yako ya fedha kwa sasa.",

            "Hifadhi mahindi yaliyobaki sehemu kavu, safi na isiyoingia unyevunyevu.",

            "Kagua mahindi mara kwa mara ili kuhakikisha hayashambuliwi na wadudu.",

            "Fuatilia bei za soko kila baada ya wiki chache ili kuona kama zimeanza kupanda.",

            "Fanya uamuzi wa kuuza yaliyobaki endapo bei zitafikia kiwango kizuri."

        ]

    # ------------------------------------------------------

    elif action == "STORE":

        return [

            "Kausha mahindi vizuri kabla ya kuyaingiza ghalani.",

            "Tumia mifuko ya PICS, silo ya chuma au ghala lenye usalama mzuri.",

            "Kagua mahindi mara kwa mara ili kuzuia wadudu, panya na unyevunyevu.",

            "Fuatilia mwenendo wa bei kila mwezi kabla ya kufanya uamuzi wa kuuza.",

            "Uza mahindi pale bei itakapokuwa imeongezeka kwa kiwango kinachoweza kuongeza faida."

        ]

    # ------------------------------------------------------

    return [

        "Endelea kufuatilia taarifa za soko.",

        "Wasiliana na Afisa Ugani au Afisa Masoko ikiwa unahitaji ushauri zaidi."

    ]
    
    # ==========================================================
# BUILD COMPLETE ADVISORY MESSAGE
# ==========================================================

def build_farmer_message(
    decision: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Combine all farmer-facing messages into a single object.

    This function does not make decisions.

    It only prepares information for the dashboard.
    """

    action = normalize_action(
        decision.get("action")
    )

    risk = normalize_risk(
        decision.get("risk_level")
    )

    recommendation = ACTION_LABELS.get(
        action,
        "PENDEKEZO HALIPATIKANI"
    )

    return {

        # Main recommendation
        "recommendation": recommendation,

        # Short summary
        "summary": build_summary(
            decision
        ),

        # Human explanation
        "reasoning": build_reasoning(
            decision
        ),

        # Storage / selling advice
        "storage_advice": build_storage_advice(
            action
        ),

        # Risk explanation
        "risk_message": build_risk_message(
            risk
        ),

        # Practical steps
        "action_plan": build_action_plan(
            action
        ),

        # Raw values (useful for dashboard styling)
        "action": action,

        "risk_level": risk,

    }
    
    # ==========================================================
# LEGACY COMPATIBILITY
# ==========================================================

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
    Compatibility wrapper for older dashboard versions.

    This function no longer makes decisions.

    It simply prepares simple economic summaries
    expected by older interfaces.
    """

    current_income = (
        current_price_100kg / 100
    ) * 90 * bags

    if (
        advice.get("utabiri_wa_bei")
        and len(advice["utabiri_wa_bei"]) > 0
    ):

        future_price = advice["utabiri_wa_bei"][0]["per_gunia_90kg"]

    else:

        future_price = (
            current_price_100kg / 100
        ) * 90

    future_income = future_price * bags

    deductions = (
        storage_cost
        + transport_cost
    )

    difference = (
        future_income
        - current_income
        - deductions
    )

    if difference >= 0:

        diff_label = "Faida"

        is_profit = True

    else:

        diff_label = "Hasara"

        is_profit = False

    # --------------------------------------------------

    action = advice.get("action", "UZA SASA")

    if cash_need == "Ndiyo":

        sell_now = round(bags * 0.5, 1)

        keep = round(bags - sell_now, 1)

    elif action == "UZA SASA":

        sell_now = float(bags)

        keep = 0

    elif action == "SUBIRI KIDOGO":

        sell_now = round(bags * 0.4, 1)

        keep = round(bags - sell_now, 1)

    else:

        sell_now = round(bags * 0.2, 1)

        keep = round(bags - sell_now, 1)

    # --------------------------------------------------

    if storage_type == "Mifuko ya PICS":

        storage_note = (
            "Mifuko ya PICS hupunguza uharibifu wa wadudu "
            "na inaweza kusaidia kuhifadhi ubora wa mahindi."
        )

    elif storage_type == "Silo ya chuma":

        storage_note = (
            "Silo ya chuma ni mojawapo ya njia bora zaidi "
            "za kuhifadhi mahindi kwa muda mrefu."
        )

    elif storage_type == "Ghala":

        storage_note = (
            "Hakikisha ghala ni kavu, safi na halivuji "
            "ili kupunguza hasara."
        )

    else:

        storage_note = (
            "Hifadhi mahindi sehemu kavu na salama "
            "ili kupunguza uharibifu."
        )

    # --------------------------------------------------

    if action == "UZA SASA":

        market_note = (
            "Kwa hali ya sasa ya soko, kuuza mapema "
            "kunaonekana kuwa chaguo salama zaidi."
        )

    elif action == "HIFADHI":

        market_note = (
            "Mfumo unaonyesha kuwa kusubiri kunaweza "
            "kuongeza thamani ya mauzo ikiwa mahindi "
            "yatahifadhiwa vizuri."
        )

    else:

        market_note = (
            "Kuuza sehemu na kuhifadhi sehemu ni njia "
            "ya kupunguza hatari huku ukisubiri soko."
        )

    return {

        "current_income": current_income,

        "wait_income": future_income,

        "difference": difference,

        "diff_label": diff_label,

        "is_profit": is_profit,

        "sell_now_bags": sell_now,

        "keep_bags": keep,

        "storage_advice": storage_note,

        "market_note": market_note,

        "total_deductions": deductions,

    }