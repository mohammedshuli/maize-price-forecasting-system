# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.decision_support import get_recommendation

st.set_page_config(
    page_title="Mshauri wa Bei ya Mahindi",
    page_icon="🌾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── custom styling for a cleaner, more professional mobile look ──
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 800;
        color: #2d5016;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #555;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .action-card {
        border-radius: 14px;
        padding: 1.3rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .action-card-sell { background-color: #fdecea; border: 2px solid #e74c3c; }
    .action-card-wait-short { background-color: #fef9e7; border: 2px solid #f39c12; }
    .action-card-wait-long { background-color: #eafaf1; border: 2px solid #27ae60; }
    .action-label {
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }
    .action-message {
        font-size: 1.0rem;
        line-height: 1.5;
    }
    .split-card {
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 700;
    }
    .price-now {
        text-align: center;
        font-size: 1.6rem;
        font-weight: 800;
        color: #2d5016;
    }
    .price-label {
        text-align: center;
        color: #777;
        font-size: 0.85rem;
    }
    .footer-note {
        text-align: center;
        color: #999;
        font-size: 0.75rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🌾 Mshauri wa Bei ya Mahindi</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>Mfumo wa kukusaidia kuamua kuuza au kuhifadhi "
    "mahindi yako — Mbeya na Iringa</div>",
    unsafe_allow_html=True
)

# ── INPUTS ──────────────────────────────────────────────
st.markdown("### 📥 Jaza Taarifa Zako")

mkoa = st.selectbox("Uko mkoa gani?", ["Mbeya", "Iringa"])

idadi_magunia = st.number_input(
    "Una magunia mangapi ya mahindi sasa hivi? (gunia moja ≈ 90kg)",
    min_value=1, value=10, step=1
)

needs_cash = st.radio(
    "Je una shida ya pesa ya haraka sasa hivi (ada, matibabu, n.k)?",
    ["Hapana", "Ndiyo"], horizontal=True
)

cash_portion = 0.0
if needs_cash == "Ndiyo":
    cash_portion = st.slider(
        "Sehemu ya magunia unayotaka kuuza sasa kwa shida hiyo (%)",
        10, 100, 50, step=10
    ) / 100.0

storage_choice = st.radio(
    "Utahifadhi mahindi yaliyobaki kwa namna gani?",
    ["Magunia ya kawaida", "Mifuko maalum (Hermetic bags)"],
    horizontal=True
)
storage_quality = "kawaida" if storage_choice == "Magunia ya kawaida" else "hermetic"

st.write("")

# ── ACTION BUTTON ───────────────────────────────────────
if st.button("🚀 PATA USHAURI WAKO", use_container_width=True, type="primary"):

    forecast = pd.read_csv(f"data/outputs/{mkoa.lower()}_forecast.csv", parse_dates=["date"])
    clean = pd.read_csv(f"data/processed/{mkoa.lower()}_clean.csv", parse_dates=["date"])

    current_price = clean["price"].iloc[-1]
    current_date = clean["date"].iloc[-1]

    rec = get_recommendation(
        current_date=current_date,
        current_price_100kg=current_price,
        forecast_dates=forecast["date"].tolist(),
        forecast_prices_100kg=forecast["forecast"].tolist(),
        ci_lower_1m_100kg=forecast["lower_95"].iloc[0],
        ci_upper_1m_100kg=forecast["upper_95"].iloc[0],
        storage_quality=storage_quality
    )

    # ── split logic: cash need first, then engine recommendation ──
    if needs_cash == "Ndiyo":
        sell_now_magunia = round(idadi_magunia * cash_portion, 1)
        baki_magunia = round(idadi_magunia - sell_now_magunia, 1)
    elif rec["action"] == "UZA SASA":
        sell_now_magunia = idadi_magunia
        baki_magunia = 0.0
    elif rec["action"] == "SUBIRI KIDOGO":
        sell_now_magunia = round(idadi_magunia * 0.5, 1)
        baki_magunia = round(idadi_magunia - sell_now_magunia, 1)
    else:
        sell_now_magunia = 0.0
        baki_magunia = idadi_magunia

    st.write("---")
    st.markdown("### 📋 Ushauri Wako")

    card_class = {
        "UZA SASA": "action-card-sell",
        "SUBIRI KIDOGO": "action-card-wait-short",
        "SUBIRI ZAIDI": "action-card-wait-long"
    }[rec["action"]]

    icon = {"UZA SASA": "🚨", "SUBIRI KIDOGO": "🟡", "SUBIRI ZAIDI": "✅"}[rec["action"]]

    st.markdown(f"""
    <div class="action-card {card_class}">
        <div class="action-label">{icon} {rec['action']}</div>
        <div class="action-message">{rec['message_sw']}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── current price, big and clear ──
    st.markdown(
        f"<div class='price-now'>{rec['bei_ya_sasa']['per_gunia_90kg']:,} TZS</div>"
        f"<div class='price-label'>Bei ya sasa kwa gunia moja (90kg) — {mkoa}</div>",
        unsafe_allow_html=True
    )

    st.write("")

    # ── sell/store split, two clear cards side by side ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<div class='split-card' style='background-color:#fdecea;color:#c0392b;'>"
            f"💰 Uza Sasa<br>{sell_now_magunia} Magunia</div>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"<div class='split-card' style='background-color:#eafaf1;color:#1e8449;'>"
            f"🏠 Hifadhi<br>{baki_magunia} Magunia</div>",
            unsafe_allow_html=True
        )

    st.write("")
    st.caption(
        f"📦 Tunadhania upotevu wa hifadhi wa {rec['storage_loss_assumed_pct']}% "
        f"katika miezi 3 kwa aina ya hifadhi uliyochagua."
    )

    # ── forecast table ──
    st.write("---")
    st.markdown("#### 📈 Makadirio ya Bei (Gunia 90kg)")

    rows = [{"Kipindi": "Bei ya Leo", "Bei (TZS)": rec["bei_ya_sasa"]["per_gunia_90kg"]}]
    for f in rec["utabiri_wa_bei"]:
        rows.append({"Kipindi": f["mwezi"], "Bei (TZS)": f["per_gunia_90kg"]})
    df_table = pd.DataFrame(rows)
    st.dataframe(
        df_table.style.format({"Bei (TZS)": "{:,.0f}"}),
        use_container_width=True, hide_index=True
    )

    # ── simple optional chart ──
    with st.expander("📊 Ona Mchoro wa Bei (si lazima)"):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=["Leo"] + [f["mwezi"] for f in rec["utabiri_wa_bei"]],
            y=[rec["bei_ya_sasa"]["per_gunia_90kg"]] + [f["per_gunia_90kg"] for f in rec["utabiri_wa_bei"]],
            mode="lines+markers",
            line=dict(color="#2d5016", width=3),
            marker=dict(size=10)
        ))
        fig.update_layout(
            height=300, margin=dict(l=10, r=10, t=20, b=10),
            yaxis_title="TZS kwa gunia", plot_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "<div class='footer-note'>Mfumo huu ni wa kusaidia maamuzi tu — "
    "tafadhali tumia busara yako pia. | EASTC BDS Project</div>",
    unsafe_allow_html=True
)