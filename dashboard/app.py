# dashboard/app.py
"""
Maize Market Advisor - Streamlit dashboard.
This module is a presentation layer only. It receives structured analysis from the
backend decision engine and displays it to the farmer in a guided workflow.
"""

import os
import sys
from typing import Any, Dict

import altair as alt
import pandas as pd
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.decision_support import (
    analyze_forecast,
    assess_risk,
    evaluate_economics,
    explain_decision,
    generate_decision,
)
from src.farmer_advisor import build_farmer_message

st.set_page_config(
    page_title="Mfumo wa Utabiri wa Bei za Mahindi",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css(css_file_name: str) -> None:
    """Load the dashboard stylesheet if it exists."""
    css_path = os.path.join(os.path.dirname(__file__), css_file_name)
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as handle:
            st.markdown(f"<style>{handle.read()}</style>", unsafe_allow_html=True)


load_css("styles.css")


def format_currency(value: float, unit: str = "TSh") -> str:
    """Format values as currency for display."""
    try:
        return f"{unit} {value:,.0f}"
    except Exception:
        return f"{unit} {value}"


def format_date(value: Any) -> str:
    """Format date values in a simple human-readable way."""
    return pd.to_datetime(value).strftime("%d %b %Y")


@st.cache_data
def load_region_data(region: str) -> Dict[str, Any] | None:
    """Load the latest market data and forecast data for one region."""
    forecast_path = f"data/outputs/{region.lower()}_forecast.csv"
    clean_path = f"data/processed/{region.lower()}_clean.csv"

    if not os.path.exists(forecast_path) or not os.path.exists(clean_path):
        return None

    forecast = pd.read_csv(forecast_path, parse_dates=["date"])
    clean = pd.read_csv(clean_path, parse_dates=["date"])

    latest = clean.iloc[-1]
    wholesale = float(latest["price"])

    return {
        "region": region,
        "date": latest["date"],
        "wholesale_100kg": wholesale,
        "price_per_kg": round(wholesale / 100, 1),
        "bag_90kg_value": round((wholesale / 100) * 90, 1),
        "forecast": forecast,
    }


def describe_trend(trend_direction: str) -> str:
    """Create a short explanation of the observed trend."""
    if trend_direction == "Increasing":
        return "Bei zinatarajiwa kuongezeka kidogo kwa miezi michache ijayo."
    if trend_direction == "Decreasing":
        return "Bei zinatarajiwa kushuka kwa miezi michache ijayo."
    return "Bei zinatarajiwa kubaki karibu na kiwango cha sasa."

st.markdown("###")
st.write("chaguaa mkoa unapo taka kupata ushauri wa mauzo ya mahindi")
mbeya = load_region_data("Mbeya")
iringa = load_region_data("Iringa")
region_options = [name for name, data in (("Mbeya", mbeya), ("Iringa", iringa)) if data is not None]
selected_region = st.selectbox("Mkoa", region_options, index=0)
region_data = mbeya if selected_region == "Mbeya" else iringa

if region_data is None:
    st.error("Hakuna data ya soko inayopatikana kwa mkoa huu kwa sasa.")
    st.stop()

with st.sidebar:
    st.markdown(
        "<div class='sidebar-card'><div class='sidebar-title'>🏛️ Taarifa za mradi</div><div class='sidebar-text'>Mfumo wa usaidizi wa maamuzi kwa wakulima wa mahindi.</div><div class='sidebar-meta'>Mkoa: Mbeya na Iringa<br/>Aina: Utabiri wa bei na ushauri wa mauzo</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='sidebar-card'><div class='sidebar-title'>📌 Lengo kuu</div><div class='sidebar-text'>mfumo huu utakusaidia kujua mwenendo mzima wa soko la mahindi pamoja na bei zijazo ili kuweza kufanya maamuzi sahihi</div></div>", unsafe_allow_html=True)

st.markdown(
    "<div class='hero-section'><div class='hero-content'><div class='hero-chip'>🌾 Mfumo wa msaada wa maamuzi kwa wakulima</div><div class='hero-title'>Mfumo wa Utabiri wa Bei za Mahindi na Msaada wa Maamuzi</div><div class='hero-text'>Mfumo huu unakusaidia kufanya uamuzi bora wa kuuza au kuhifadhi mahindi yako kulingana na mwenendo wa soko.</div><div class='hero-actions'><div class='hero-note'>Mkoa: <b>"
    + selected_region
    + "</b> • Tarehe ya utabiri: "
    + format_date(region_data["date"])
    + "</div></div></div></div>",
    unsafe_allow_html=True,
)

st.markdown("### 🌽  Karibu katika mfumo huu")
st.write("Kila sehemu ya mfumo huu inalenga kukusaidia namna ya kufanya maamuzi sahihi juu ya mavuno yako")

st.markdown("### Hali ya sasa ya soko ilivyo mkoani")
market_cols = st.columns(4)
with market_cols[0]:
    st.markdown("<div class='info-card'><div class='card-title'>💰 Bei ya sasa</div><div class='card-value'>" + format_currency(region_data["wholesale_100kg"]) + "</div><div class='card-note'>Kwa kilo 100</div></div>", unsafe_allow_html=True)
with market_cols[1]:
    st.markdown("<div class='info-card'><div class='card-title'>📊 Bei kwa kilo 1</div><div class='card-value'>" + format_currency(region_data["price_per_kg"], "TSh/kg") + "</div><div class='card-note'>Kulingana na bei ya soko</div></div>", unsafe_allow_html=True)
with market_cols[2]:
    st.markdown("<div class='info-card'><div class='card-title'>🧺 Thamani ya gunia la kilo 90</div><div class='card-value'>" + format_currency(region_data["bag_90kg_value"]) + "</div><div class='card-note'>Kikadirio cha thamani ya gunia</div></div>", unsafe_allow_html=True)
with market_cols[3]:
    st.markdown("<div class='info-card'><div class='card-title'>🏪 Hali ya soko</div><div class='card-value'>Inafaa</div><div class='card-note'>Taarifa ya sasa ya soko</div></div>", unsafe_allow_html=True)

st.markdown("### 📈 3. Mwenendo wa bei kwa miezi ijayo")
forecast_df = region_data["forecast"].copy()
market_analysis = analyze_forecast(
    current_date=region_data["date"],
    current_price_100kg=region_data["wholesale_100kg"],
    forecast_dates=forecast_df["date"].tolist(),
    forecast_prices_100kg=forecast_df["forecast"].tolist(),
)

forecast_plot = forecast_df[["date", "forecast"]].rename(columns={"forecast": "bei"})
line_chart = (
    alt.Chart(forecast_plot)
    .mark_line(color="#2E7D32", strokeWidth=3)
    .encode(
        x=alt.X("date:T", title="Tarehe"),
        y=alt.Y("bei:Q", title="Bei (TSh/100kg)"),
    )
)
latest_point = (
    alt.Chart(forecast_plot.tail(1))
    .mark_point(size=140, color="#F4A300", filled=True)
    .encode(x="date:T", y="bei:Q")
)
latest_label = (
    alt.Chart(forecast_plot.tail(1))
    .mark_text(dx=0, dy=-12, fontSize=12, color="#263238")
    .encode(x="date:T", y="bei:Q", text=alt.Text("bei:Q", format=".0f"))
)
chart = (
    (line_chart + latest_point + latest_label)
    .properties(height=320, background="white")
    .configure_axis(gridColor="#376104", labelFontSize=12, titleFontSize=13)
    .configure_view(strokeWidth=0)
)
st.altair_chart(chart, use_container_width=True)
st.info(describe_trend(market_analysis["trend_direction"]))

st.markdown("### 🧑‍🌾 Taarifa za mkulima, chagua mapendekezo yaliopo ili kuweza kupata ushauri sahihi")
st.markdown("<div class='form-shell'>", unsafe_allow_html=True)
with st.form("farmer_form"):
    col1, col2 = st.columns(2)
    with col1:
        bags = st.number_input("Unataka kuuza magunia mangapi?", min_value=1, value=10, step=1)
        storage_available = st.radio("Je, unaweza kuhifadhi mahindi yako kwa usalama?", ["Ndiyo", "Hapana"], index=0)
        urgency = st.selectbox(
            "Una uhitaji wa fedha kwa kiasi gani?",
            ["Haraka iwezekanavyo", "Ndani ya mwezi mmoja", "Naweza kusubiri miezi 2-3"],
            index=0,
        )
    with col2:
        storage_method = st.selectbox(
            "Unahifadhi mahindi kwa kutumia nini?",
            ["Uhifadhi wa jadi", "Mifuko ya PICS", "Silo ya chuma", "Ghala"],
            index=1,
        )
        st.caption("Taarifa hizi zitaonyeshwa tu kama muktadha wa maamuzi ya kisasa.")

    submitted = st.form_submit_button("Pata ushauri")
st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    economic_analysis = evaluate_economics(
        current_price_100kg=region_data["wholesale_100kg"],
        forecast_prices_100kg=forecast_df["forecast"].tolist(),
        storage_duration_months=3,
        storage_cost=0.0,
        transport_cost=0.0,
        storage_quality="kawaida",
    )

    uncertainty_width_pct = 0.0
    if "lower_95" in forecast_df.columns and "upper_95" in forecast_df.columns:
        uncertainty_width_pct = (
            float(forecast_df["upper_95"].iloc[0]) - float(forecast_df["lower_95"].iloc[0])
        ) / max(float(forecast_df["forecast"].iloc[0]), 1.0)

    risk_assessment = assess_risk(
        uncertainty_width_pct=uncertainty_width_pct,
        storage_loss_pct=economic_analysis["storage_loss_pct"],
        volatility_pct=market_analysis["volatility_pct"],
        profitability_pct=economic_analysis["expected_net_benefit_pct"],
    )

    decision = generate_decision(market_analysis, economic_analysis, risk_assessment)
    explanation = explain_decision(decision, market_analysis, economic_analysis, risk_assessment)
    farmer_message = build_farmer_message(decision)

    st.markdown("### ✅  matokeo ya mfumo kulingana na machaguo yako")
    insight_cols = st.columns(5)
    with insight_cols[0]:
        st.markdown("<div class='info-card'><div class='card-title'>📈 Mwenendo wa bei</div><div class='card-value'>" + market_analysis["trend_direction"] + "</div><div class='card-note'>Mwelekeo wa bei unaotabirika</div></div>", unsafe_allow_html=True)
    with insight_cols[1]:
        st.markdown("<div class='info-card'><div class='card-title'>📊 Mabadiliko yanayotarajiwa</div><div class='card-value'>" + f"{market_analysis['percentage_change_pct']:.1f}%" + "</div><div class='card-note'>Kulingana na ubashiri</div></div>", unsafe_allow_html=True)
    with insight_cols[2]:
        st.markdown("<div class='info-card'><div class='card-title'>🏪 Gharama za kuhifadhi</div><div class='card-value'>" + format_currency(economic_analysis["total_storage_expense"]) + "</div><div class='card-note'>Kulingana na makisio ya mfumo</div></div>", unsafe_allow_html=True)
    with insight_cols[3]:
        st.markdown("<div class='info-card'><div class='card-title'>💰 Faida/hasara inayotarajiwa</div><div class='card-value'>" + ("Faida" if economic_analysis["expected_net_benefit_100kg"] > 0 else "Hasara") + "</div><div class='card-note'>Baada ya gharama za kuhifadhi</div></div>", unsafe_allow_html=True)
    with insight_cols[4]:
        st.markdown("<div class='info-card'><div class='card-title'>⚠ Kiwango cha hatari</div><div class='card-value'>" + risk_assessment["risk_level"] + "</div><div class='card-note'>Kulingana na hatari ya kusubiri</div></div>", unsafe_allow_html=True)

    st.markdown("### ✅ Mapendekezo ya mfumo")
    if decision["action"] == "SELL_NOW":
        recommendation_text = "Uza mahindi yako ndani ya wiki chache zijazo."
        recommendation_class = "sell-now"
    elif decision["action"] == "STORE":
        recommendation_text = "Hifadhi mahindi yako kwa muda mfupi."
        recommendation_class = "store"
    else:
        recommendation_text = "Uza sehemu ya mahindi na uhifadhi yaliyobaki."
        recommendation_class = "store-partial"

    st.markdown(
        f"<div class='recommendation-card {recommendation_class}'><div class='hero-chip'>✅ Hatua inayopendekezwa</div><div class='hero-title' style='font-size: 2rem; margin-bottom: 0.6rem;'>{recommendation_text}</div><div class='hero-text'>{farmer_message['summary']}</div></div>",
        unsafe_allow_html=True,
    )
    st.write(f"**Kwa nini?** {farmer_message['reasoning']}")
    st.write(f"**Matokeo yanayotarajiwa:** {explanation['expected_outcome']}")
    st.write(f"**Hatari:** {farmer_message['risk_message']}")
    st.write("**Masharti yaliyotumika:**")
    for item in explanation["assumptions_used"]:
        st.write(f"- {item}")

    st.markdown("### 📋 machaguo mbalimbali yaliyopatikana")
    comparison_cols = st.columns(3)
    options = [
        ("Uza yote sasa", "Hakikisha fedha za haraka na uepuke hatari ya kusubiri.", "Ndogo", False),
        ("Hifadhi yote", "Kuwa na uwezekano wa faida kubwa lakini hatari ni kubwa zaidi.", "Kati", False),
        ("Uza nusu, hifadhi nusu", "Chaguo la usawa kwa wakulima wenye mahitaji ya fedha na hatari ya soko.", "Ndogo⭐", False),
    ]
    recommended_option = 2 if decision["action"] == "STORE_PARTIALLY" else 0 if decision["action"] == "SELL_NOW" else 1
    options[recommended_option] = (options[recommended_option][0], options[recommended_option][1], options[recommended_option][2], True)

    for idx, (title, note, risk_text, is_recommended) in enumerate(options):
        with comparison_cols[idx]:
            card_class = "comparison-card recommended" if is_recommended else "comparison-card"
            st.markdown(
                f"<div class='{card_class}'><div class='card-title'>{title}</div><div class='card-note'>{note}</div><div class='card-value'>{risk_text}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("### 📝 Hatua unazoweza kufata ili kufanya maamuzi sahihi")
    for step in farmer_message["action_plan"]:
        st.markdown(f"- ✓ {step}")

    st.caption("Ushauri huu unategemea utabiri wa sasa na taarifa ulizoingiza. Unapaswa kuangalia soko tena kwa kawaida.")
else:
    st.info("Jaza taarifa za mkulima ili upate ushauri wa hatua inayofaa.")

st.markdown("<div class='footer-card'>disclaimer:kwa maamuzi zaidi wasiliana na affisa masoko u<br/>Maize Price Forecasting and Decision Support System<br/>Mbeya and Iringa Regions, Tanzania</div>", unsafe_allow_html=True)
