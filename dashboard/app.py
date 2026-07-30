"""
==========================================================
MAIZE PRICE FORECASTING AND DECISION SUPPORT SYSTEM

Streamlit Dashboard

This dashboard is responsible ONLY for:

• Loading prepared data
• Collecting farmer inputs
• Displaying market information
• Displaying decision support results

No business logic should exist here.
==========================================================
"""

import os
import sys
from typing import Any, Dict

import altair as alt
import pandas as pd
import streamlit as st

# -------------------------------------------------------
# Project path
# -------------------------------------------------------

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from src.decision_support import (
    analyze_forecast,
    assess_risk,
    evaluate_economics,
    explain_decision,
    generate_decision,
)

from src.farmer_advisor import build_farmer_message


# -------------------------------------------------------
# Streamlit
# -------------------------------------------------------

st.set_page_config(

    page_title="Mfumo wa Ushauri wa Mauzo ya Mahindi",

    page_icon="🌽",

    layout="wide",

    initial_sidebar_state="expanded",

)

# -------------------------------------------------------
# CSS
# -------------------------------------------------------

def load_css(css_file: str):

    css_path = os.path.join(
        os.path.dirname(__file__),
        css_file
    )

    if os.path.exists(css_path):

        with open(
            css_path,
            encoding="utf-8"
        ) as f:

            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )


load_css("styles.css")


# -------------------------------------------------------
# Formatting helpers
# -------------------------------------------------------

def format_currency(value: float):

    return f"TSh {value:,.0f}"


def format_date(value):

    return pd.to_datetime(value).strftime("%d %B %Y")


# -------------------------------------------------------
# Reusable Cards
# -------------------------------------------------------

def render_metric_card(title, value, note=""):

    st.markdown(
        f"""
<div class="info-card">

<div class="card-title">
{title}
</div>

<div class="card-value">
{value}
</div>

<div class="card-note">
{note}
</div>

</div>
""",
        unsafe_allow_html=True,
    )


def render_forecast_card(
    month,
    price,
    current_price,
):

    change = (
        (price-current_price)
        / current_price
    )*100

    if change > 1:

        colour = "#2E7D32"

        icon = "📈"

    elif change < -1:

        colour = "#C62828"

        icon = "📉"

    else:

        colour = "#F9A825"

        icon = "➜"

    st.markdown(
        f"""
<div class="forecast-card">

<div class="forecast-month">
{month}
</div>

<div class="forecast-price">
{format_currency(price)}
</div>

<div
class="forecast-change"
style="color:{colour};">

{icon} {change:.1f}%

</div>

</div>
""",
        unsafe_allow_html=True,
    )
    

# ==========================================================
# DATA LOADING
# ==========================================================

@st.cache_data(show_spinner=False)
def load_region_data(region: str) -> Dict[str, Any] | None:
    """
    Load processed market data together with the
    generated SARIMA forecast.
    """

    forecast_path = f"data/outputs/{region.lower()}_forecast.csv"
    clean_path = f"data/processed/{region.lower()}_clean.csv"

    if not os.path.exists(forecast_path):
        return None

    if not os.path.exists(clean_path):
        return None

    forecast = pd.read_csv(
        forecast_path,
        parse_dates=["date"]
    )

    clean = pd.read_csv(
        clean_path,
        parse_dates=["date"]
    )

    latest = clean.iloc[-1]

    wholesale = float(latest["price"])

    return {

        "region": region,

        "date": latest["date"],

        "wholesale_100kg": wholesale,

        "price_per_kg": wholesale / 100,

        "bag_90kg_value": (wholesale / 100) * 90,

        "forecast": forecast,

    }


# ==========================================================
# MARKET DESCRIPTION
# ==========================================================

def describe_trend(direction: str):

    if direction == "Increasing":

        return (
            "Bei za mahindi zinaonekana kuongezeka "
            "katika miezi ijayo."
        )

    elif direction == "Decreasing":

        return (
            "Bei zinaonekana kushuka katika miezi ijayo."
        )

    return (
        "Bei zinatarajiwa kubaki karibu na kiwango "
        "cha sasa."
    )


# ==========================================================
# REGION SELECTION
# ==========================================================

st.write("### 🌍 Chagua Mkoa")

mbeya = load_region_data("Mbeya")
iringa = load_region_data("Iringa")

available_regions = []

if mbeya is not None:
    available_regions.append("Mbeya")

if iringa is not None:
    available_regions.append("Iringa")

selected_region = st.selectbox(
    "Mkoa unaotaka kuchambua",
    available_regions,
)

if selected_region == "Mbeya":
    region_data = mbeya
else:
    region_data = iringa

if region_data is None:

    st.error("Hakuna taarifa za soko.")

    st.stop()


forecast_df = region_data["forecast"]


market_analysis = analyze_forecast(

    current_date=region_data["date"],

    current_price_100kg=region_data["wholesale_100kg"],

    forecast_dates=forecast_df["date"].tolist(),

    forecast_prices_100kg=forecast_df["forecast"].tolist(),

)


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown("## 🌽 Mfumo wa Ushauri")

    st.info(
        """
Mfumo huu unatumia:

• Bei halisi za soko

• Uchambuzi wa kiuchumi

• Tathmini ya uhifadhi

ili kukusaidia kufanya
uamuzi bora wa kuuza
mahindi yako.
"""
    )

    st.success(
        f"""
Mkoa:

**{selected_region}**

Tarehe ya taarifa:

**{format_date(region_data["date"])}**
"""
    )


# ==========================================================
# HERO SECTION
# ==========================================================

st.markdown(
f"""
<div class="hero-section">

<div class="hero-chip">

🌾 Mfumo wa Utabiri wa Bei

</div>

<div class="hero-title">

Fanya Uamuzi Bora wa
Kuuza au Kuhifadhi Mahindi

</div>

<div class="hero-text">

Mfumo huu unakusaidia
kutathmini hali ya soko,
utabiri wa bei pamoja na
hatari zinazoweza kujitokeza
kabla ya kufanya uamuzi.

</div>

<div class="hero-note">

📍 Mkoa:
<b>{selected_region}</b>

&nbsp;&nbsp;&nbsp;

📅 Tarehe:
<b>{format_date(region_data["date"])}</b>

</div>

</div>
""",
unsafe_allow_html=True
)


# ==========================================================
# CURRENT MARKET
# ==========================================================

st.markdown("## 🌾 Hali ya Soko la Leo")

c1, c2, c3, c4 = st.columns(4)

trend = market_analysis["trend_direction"]

if trend == "Increasing":

    trend_text = "📈 Bei zinapanda"

elif trend == "Decreasing":

    trend_text = "📉 Bei zinashuka"

else:

    trend_text = "➜ Bei ni Nzuri"


with c1:

    render_metric_card(

        "Bei ya sasa",

        format_currency(
            region_data["wholesale_100kg"]
        ),

        "Kwa kilo 100"

    )

with c2:

    render_metric_card(

        "Bei kwa kilo",

        format_currency(
            region_data["price_per_kg"]
        ),

        "Kwa bei za rejareja"

    )

with c3:

    render_metric_card(

        "Gunia (90Kg)",

        format_currency(
            region_data["bag_90kg_value"]
        ),

        "Makadirio"

    )

with c4:

    render_metric_card(

        "Mwenendo",

        trend_text,

        "Kutokana na utabiri"

    )
    
    # ==========================================================
# PRICE FORECAST
# ==========================================================

st.markdown("## 📈 Bei Zinazotarajiwa")

st.write(
    """
Hapa chini unaweza kuona makadirio ya
bei pamoja na mabadiliko yanayotarajiwa kwa miezi ijayo.
"""
)

forecast_cards = st.columns(3)

future_prices = forecast_df.head(3)

current_price = region_data["wholesale_100kg"]

for column, (_, row) in zip(forecast_cards, future_prices.iterrows()):

    with column:

        render_forecast_card(

            month=pd.to_datetime(row["date"]).strftime("%B %Y"),

            price=float(row["forecast"]),

            current_price=current_price,

        )


st.markdown("### 📊 Mwenendo wa Bei")

chart_data = future_prices.copy()

chart = (

    alt.Chart(chart_data)

    .mark_line(
        point=True,
        strokeWidth=4,
        color="#2E7D32"
    )

    .encode(

        x=alt.X(
            "date:T",
            title="Mwezi"
        ),

        y=alt.Y(
            "forecast:Q",
            title="Bei (TSh)"
        ),

        tooltip=[
            alt.Tooltip(
                "date:T",
                title="Mwezi"
            ),
            alt.Tooltip(
                "forecast:Q",
                title="Bei"
            ),
        ],

    )

    .properties(
        height=320
    )

)

st.altair_chart(
    chart,
    use_container_width=True
)

st.success(

    describe_trend(
        market_analysis["trend_direction"]
    )

)# ==========================================================
# FARMER INFORMATION
# ==========================================================

st.markdown("## 🧑‍🌾 Tuambie Kuhusu Mahindi Yako")

st.write(
    """
Ili mfumo uweze kutoa ushauri unaokufaa,
tafadhali jibu maswali yafuatayo.
Majibu yako yatasaidia mfumo kufanya
uchambuzi unaozingatia hali yako halisi.
"""
)

with st.form("farmer_information"):

    st.markdown("### 🌽 Taarifa za Mazao")

    col1, col2 = st.columns(2)

    with col1:

        bags = st.number_input(
            "Una magunia mangapi ya mahindi?",
            min_value=1,
            value=10,
            step=1,
        )

        selling_plan = st.radio(
            "Unapanga kufanya nini?",
            [
                "Nataka kuuza yote",
                "Nataka kuuza sehemu",
                "Bado sijafanya uamuzi",
            ],
            index=2,
        )

        storage_available = st.radio(
            "Je, una sehemu salama ya kuhifadhi?",
            [
                "Ndiyo",
                "Hapana",
            ],
            index=0,
        )

    with col2:

        cash_urgency = st.selectbox(
            "Unahitaji fedha lini?",
            [
                "Leo",
                "Wiki hii",
                "Ndani ya mwezi mmoja",
                "Naweza kusubiri zaidi",
            ],
        )

        storage_method = st.selectbox(
            "Unatumia njia gani kuhifadhi mahindi?",
            [
                "Mifuko ya PICS",
                "Ghala",
                "Silo",
                "Njia ya kawaida",
            ],
        )

        experience = st.selectbox(
            "Uzoefu wako wa kuhifadhi mahindi",
            [
                "Mdogo",
                "Wastani",
                "Mkubwa",
            ],
        )

    st.markdown("---")

    st.info(
        """
Mfumo utatumia taarifa hizi pamoja na
utabiri wa bei ili kukupatia ushauri
unaokufaa zaidi.
"""
    )

    submitted = st.form_submit_button(
        "🔍 Changanua na Nipatie Ushauri"
    )
    
# ==========================================================
# SYSTEM ANALYSIS
# ==========================================================

if submitted:

    progress = st.progress(0)

    status = st.empty()

    status.info("🔍 Mfumo unachambua taarifa ulizoingiza...")

    import time

    steps = [

        "✓ Inachambua bei ya sasa ya soko...",

        "✓ Inachambua utabiri wa miezi mitatu ijayo...",

        "✓ Inakadiria gharama na faida inayowezekana...",

        "✓ Inatathmini hatari za kusubiri kuuza...",

        "✓ Inalinganisha mahitaji yako ya fedha...",

        "✓ Inatengeneza ushauri bora kwako..."

    ]

    for i, step in enumerate(steps):

        status.info(step)

        progress.progress((i + 1) / len(steps))

        time.sleep(0.25)


    # ======================================================
    # DECISION ENGINE
    # ======================================================

    economic_analysis = evaluate_economics(

        current_price_100kg=region_data["wholesale_100kg"],

        forecast_prices_100kg=forecast_df["forecast"].tolist(),

        storage_duration_months=3,

        storage_cost=0,

        transport_cost=0,

        storage_quality="kawaida",

    )


    uncertainty_width_pct = 0

    if (
        "lower_95" in forecast_df.columns
        and
        "upper_95" in forecast_df.columns
    ):

        uncertainty_width_pct = (

            float(forecast_df["upper_95"].iloc[0])

            -

            float(forecast_df["lower_95"].iloc[0])

        ) / max(

            float(forecast_df["forecast"].iloc[0]),

            1

        )


    risk_assessment = assess_risk(

        uncertainty_width_pct=uncertainty_width_pct,

        storage_loss_pct=economic_analysis["storage_loss_pct"],

        volatility_pct=market_analysis["volatility_pct"],

        profitability_pct=economic_analysis["expected_net_benefit_pct"],

    )


    decision = generate_decision(

        market_analysis,

        economic_analysis,

        risk_assessment,

    )


    explanation = explain_decision(

        decision,

        market_analysis,

        economic_analysis,

        risk_assessment,

    )


    farmer_message = build_farmer_message(

        decision

    )

    progress.empty()

    status.success("✅ Uchambuzi umekamilika.")
    
# ==========================================================
 # DECISION SUMMARY
 # ==========================================================

    st.markdown("## 📊 Muhtasari wa Uchambuzi")

    summary1, summary2, summary3 = st.columns(3)

    with summary1:

        render_metric_card(

        "📈 Mwelekeo wa Bei",

        "Kupanda"

        if market_analysis["trend_direction"] == "Increasing"

        else

        "Kushuka"

        if market_analysis["trend_direction"] == "Decreasing"

        else

        "Kubaki Sawa",

        "Makadirio ya miezi mitatu"

    )

    with summary2:

       render_metric_card(

        "💵 Bei Inayotarajiwa",

        format_currency(

            market_analysis["average_forecast_price"]

        ),

        "Wastani wa utabiri"

    )

    with summary3:
         

       difference = (

        market_analysis["average_forecast_price"]

        -

        region_data["wholesale_100kg"]

    )

    render_metric_card(

        "📊 Tofauti ya Bei",

        format_currency(abs(difference)),

        "Faida inayoweza kupatikana"

        if difference > 0

        else

        "Kupungua kwa bei"

    )
    
     # ==========================================================
     # FINAL DECISION
     # ==========================================================

    st.markdown("## 🤖 Uamuzi wa Mfumo")

    if decision["action"] == "SELL_NOW":

      recommendation_title = "UUZE MAHINDI YAKO SASA"

      recommendation_icon = "🟢"

      recommendation_class = "sell-now"

    elif decision["action"] == "STORE":

     recommendation_title = "HIFADHI MAHINDI YAKO"

     recommendation_icon = "📦"

     recommendation_class = "store"

    else:

      recommendation_title = "UUZE NUSU, HIFADHI NUSU"

      recommendation_icon = "⚖️"

      recommendation_class = "store-partial"


    st.markdown(
        f"""
<div class="recommendation-card {recommendation_class}">
    <div class="hero-chip">
        {recommendation_icon} UAMUZI WA MFUMO
    </div>
    <div class="hero-title">
        {recommendation_title}
    </div>
    <div class="hero-text">
        {farmer_message["summary"]}
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================================
# WHY THIS DECISION
# ==========================================================

    st.markdown("## 💡 Kwa nini tumekushauri hivyo?")

    if decision["action"] == "SELL_NOW":

      explanation_text = f"""
Bei ya sasa ya mahindi ni nzuri ukilinganisha
na makadirio ya miezi ijayo.

Mfumo umeona kuwa kusubiri kuuza kunaweza
kuongeza gharama za kuhifadhi bila kuongeza
faida ya mauzo.

Kwa hiyo kuuza mapema ndiyo chaguo salama zaidi.
"""

    elif decision["action"] == "STORE":

      explanation_text = f"""
Makadirio yanaonyesha kuwa bei inaweza
kuongezeka katika miezi ijayo.

Iwapo unaweza kuhifadhi mahindi vizuri,
kusubiri kunaweza kukuongezea mapato.
"""

    else:

      explanation_text = f"""
Mfumo umebaini kuwa hakuna faida kubwa
ya kuuza yote sasa wala kuhifadhi yote.

Ndiyo maana unapendekezwa kuuza sehemu
ili kupata fedha za sasa, huku ukihifadhi
sehemu nyingine kusubiri mabadiliko ya soko.
"""

    st.info(explanation_text)

# ==========================================================
# MAPATO
# ==========================================================

    st.markdown("## 💰 Makadirio ya Mapato")

    col1, col2, col3 = st.columns(3)

    sell_now = region_data["wholesale_100kg"] * bags

    future_value = (
      market_analysis["average_forecast_price"]
    * bags
     )

    difference = future_value - sell_now


    with col1:

      render_metric_card(

        "Ukiyauza Leo",

        format_currency(sell_now),

        "Makadirio"

     ) 


    with col2:

      render_metric_card(

        "Ukisubiri miezi ijayo",

        format_currency(future_value),

        "Baada ya miezi 3"

     )


    with col3:

      render_metric_card(

        "Tofauti",

        format_currency(abs(difference)),

        "Faida"

        if difference > 0

        else

        "Hasara"

    )
    
    # ==========================================================
# OTHER OPTIONS
# ==========================================================

    st.markdown("## 🔄 Chaguo Nyingine")

    cards = st.columns(3)

    choices = [

("💰 Uza Yote", "Fedha za haraka lakini hakuna nafasi ya kufaidika endapo bei itapanda."),

("📦 Hifadhi Yote", "Unaweza kupata faida zaidi, lakini pia unaongeza hatari ya hasara."),

("⚖️ Uza Nusu", "Njia ya kati inayopunguza hatari na kukupa fedha za matumizi.")

]

    for column, choice in zip(cards, choices):

      with column:

        st.markdown(

      f"""
     <div class="comparison-card">

     <div class="card-title">

     {choice[0]}

      </div>

     <div class="card-note">

     {choice[1]}

     </div>

     </div>
     """,

       unsafe_allow_html=True,

     )
        
    # ==========================================================
    # HATUA ZA KUFUATA
    # ==========================================================

    st.markdown("## 📝 Hatua Unazopaswa Kuchukua")

    step1, step2, step3 = st.columns(3)

    with step1:
        st.markdown("""
<div class="timeline-card">
    <div class="timeline-number">1</div>
    <div class="timeline-title">Leo</div>
    <div class="timeline-text">
        • Linganisha bei kutoka kwa wanunuzi mbalimbali.<br>
        • Hakikisha umejua gharama za usafirishaji.<br>
        • Andaa mahindi yako kwa ajili ya mauzo au uhifadhi.
    </div>
</div>
""", unsafe_allow_html=True)

    with step2:
        st.markdown("""
<div class="timeline-card">
    <div class="timeline-number">2</div>
    <div class="timeline-title">Ndani ya Wiki Hii</div>
    <div class="timeline-text">
        • Fuatilia mabadiliko ya bei sokoni.<br>
        • Kama mfumo unapendekeza kuuza, usichelewe kufanya maamuzi.<br>
        • Kama unapendekeza kuhifadhi, hakikisha sehemu ya kuhifadhi ni salama.
    </div>
</div>
""", unsafe_allow_html=True)

    with step3:
        st.markdown("""
<div class="timeline-card">
    <div class="timeline-number">3</div>
    <div class="timeline-title">Baada ya Kufanya Uamuzi</div>
    <div class="timeline-text">
        • Hifadhi kumbukumbu za mauzo.<br>
        • Linganisha matokeo na makadirio ya mfumo.<br>
        • Tembelea mfumo tena unapopata taarifa mpya za soko.
    </div>
</div>
""", unsafe_allow_html=True)
        
        
# ==========================================================
# KUMBUKA
# ==========================================================

    st.markdown("## 📌 Kumbuka")

    st.warning(
"""
Mfumo huu unatoa ushauri kwa kutumia:

• Bei halisi za mahindi zilizokusanywa sokoni.

• Mfano wa utabiri wa SARIMA.

• Uchambuzi wa faida, gharama na hatari.

Utabiri hauwezi kutabiri soko kwa uhakika wa asilimia 100.

Iwapo kutatokea mabadiliko makubwa ya hali ya hewa,
sera za serikali, au mahitaji ya soko,
bei zinaweza kubadilika.

Endelea kufuatilia taarifa za soko mara kwa mara
kabla ya kufanya uamuzi wa mwisho.
"""
)

# ==========================================================
# FOOTER
# ==========================================================

    st.markdown(
"""
<div class="footer-card">

<h3>🌽 Maize Price Forecasting and Decision Support System</h3>

<p>

Mfumo huu umetengenezwa kwa ajili ya kuwasaidia
wakulima wa mahindi katika mikoa ya Mbeya na Iringa
kufanya maamuzi bora kuhusu kuuza au kuhifadhi mazao yao.

</p>

<hr>

<p>

Bachelor of Data Science Final Year Project

Eastern Africa Statistical Training Centre (EASTC)

2026

</p>

</div>
""",
unsafe_allow_html=True,
)    
            