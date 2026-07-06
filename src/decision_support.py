# src/decision_support.py
# adds optional storage_quality parameter -- defaults to "kawaida" (poor/normal)
# if not provided, so the function still works exactly as before for any
# existing calls that don't pass it

SWAHILI_MONTHS = {
    1: "Januari", 2: "Februari", 3: "Machi", 4: "Aprili",
    5: "Mei", 6: "Juni", 7: "Julai", 8: "Agosti",
    9: "Septemba", 10: "Oktoba", 11: "Novemba", 12: "Desemba"
}


def to_farmer_units(price_per_100kg):
    price_per_kg = price_per_100kg / 100
    return {
        "per_kg": round(price_per_kg),
        "per_gunia_90kg": round(price_per_kg * 90)
    }


def get_recommendation(current_date, current_price_100kg,
                        forecast_dates, forecast_prices_100kg,
                        ci_lower_1m_100kg, ci_upper_1m_100kg,
                        storage_quality="kawaida"):

    harvest_months = [5, 6, 7, 8, 9]
    cash_pressure_discount = 0.10

    # storage_quality changes the spoilage assumption directly
    storage_loss_3m = 0.20 if storage_quality == "kawaida" else 0.05

    forecast_1m_100kg = forecast_prices_100kg[0]
    forecast_3m_100kg = forecast_prices_100kg[2]

    gain_1m = (forecast_1m_100kg - current_price_100kg) / current_price_100kg
    gain_3m = (forecast_3m_100kg - current_price_100kg) / current_price_100kg
    ci_width_pct = (ci_upper_1m_100kg - ci_lower_1m_100kg) / current_price_100kg

    is_harvest_season = current_date.month in harvest_months

    net_advantage = gain_3m - storage_loss_3m - (ci_width_pct / 2)
    if is_harvest_season:
        net_advantage -= cash_pressure_discount

    if net_advantage <= 0:
        action = "UZA SASA"
        message_sw = (
            "Uza sasa. Gharama ya kuhifadhi na hatari ya mabadiliko ya bei "
            "ni kubwa kuliko faida inayotarajiwa kwa kusubiri."
        )
    elif net_advantage < 0.15:
        action = "SUBIRI KIDOGO"
        message_sw = (
            "Unaweza kusubiri kwa muda mfupi. Bei inatarajiwa kupanda "
            "kidogo, lakini hakikisha mahindi yamehifadhiwa vizuri."
        )
    else:
        action = "SUBIRI ZAIDI"
        message_sw = (
            "Bei inatarajiwa kupanda kwa kiasi kikubwa katika miezi "
            "ijayo. Ikiwa una namna nzuri ya kuhifadhi, ni vyema kusubiri."
        )

    monthly_forecasts = []
    for date, price in zip(forecast_dates, forecast_prices_100kg):
        month_name = SWAHILI_MONTHS[date.month]
        year = date.year
        units = to_farmer_units(price)
        monthly_forecasts.append({
            "mwezi": f"{month_name} {year}",
            "per_kg": units["per_kg"],
            "per_gunia_90kg": units["per_gunia_90kg"]
        })

    return {
        "action": action,
        "message_sw": message_sw,
        "bei_ya_sasa": to_farmer_units(current_price_100kg),
        "utabiri_wa_bei": monthly_forecasts,
        "gain_1m_pct": round(gain_1m * 100, 1),
        "gain_3m_pct": round(gain_3m * 100, 1),
        "storage_loss_assumed_pct": round(storage_loss_3m * 100, 1)
    }