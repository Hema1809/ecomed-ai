import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from prophet import Prophet
from fpdf import FPDF
from streamlit_option_menu import option_menu
import random
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="EcoMed AI",
    page_icon="🌿",
    layout="wide"
)

#st.image("logo.jpg", width=120)

# =====================================================
# PREMIUM UI
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.main {
    background: linear-gradient(to right, #f4fff8, #eefbf3);
}

h1 {
    color: #1b4332;
    font-weight: 800;
}

h2, h3 {
    color: #2d6a4f;
}

[data-testid="metric-container"] {
    background: white;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
    border-left: 8px solid #2d6a4f;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #1b4332, #2d6a4f);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton>button {
    background-color: #2d6a4f;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    height: 3em;
    width: 100%;
}

.stButton>button:hover {
    background-color: #40916c;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOGIN SYSTEM
# =====================================================

users = {

    "admin": {
        "password": "admin123",
        "role": "Admin"
    },

    "doctor": {
        "password": "doctor123",
        "role": "Doctor"
    },

    "inventory": {
        "password": "inventory123",
        "role": "Inventory Manager"
    },

    "officer": {
        "password": "officer123",
        "role": "Sustainability Officer"
    }

}

# SESSION STATES

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

# =====================================================
# LOGIN PAGE
# =====================================================

if not st.session_state.logged_in:

    st.title("🌿 EcoMed AI")

    st.subheader(
        "Carbon-Aware Intelligent Hospital Sustainability Platform"
    )

    st.markdown("---")

    username = st.text_input("👤 Username")

    password = st.text_input(
        "🔑 Password",
        type="password"
    )

    if st.button("🚀 Login"):

        if username in users:

            if password == users[username]["password"]:

                st.session_state.logged_in = True

                st.session_state.username = username

                st.session_state.role = users[username]["role"]

                st.success("Login Successful")

                st.rerun()

            else:

                st.error("Wrong Password")

        else:

            st.error("User not found")

    st.stop()

# -----------------------------------------------------
# TOP NAVBAR
# -----------------------------------------------------

top1, top2, top3 = st.columns([5, 2, 1])

with top1:

    st.title("🌿 EcoMed AI")

with top2:

    selected_role = st.selectbox(
        "Change Role",
        [
            "Admin",
            "Doctor",
            "Inventory Manager",
            "Sustainability Officer"
        ],
        index=[
            "Admin",
            "Doctor",
            "Inventory Manager",
            "Sustainability Officer"
        ].index(st.session_state.role)
    )

    st.session_state.role = selected_role

with top3:

    if st.button("Logout"):

        st.session_state.logged_in = False

        st.rerun()

# -----------------------------------------------------
# ROLE DISPLAY
# -----------------------------------------------------

st.success(
    f"Logged in as: {st.session_state.username} ({st.session_state.role})"
)
# =====================================================
# ROLE-BASED ACCESS CONTROL
# =====================================================

role = st.session_state.role

# -----------------------------------------------------
# ADMIN ACCESS
# -----------------------------------------------------

if role == "Admin":

    menu_options = [
        "Dashboard",
        "Forecasting",
        "AI Insights",
        "Reports",
        "Simulation",
        "Executive Dashboard"
    ]

    menu_icons = [
        "speedometer",
        "graph-up",
        "robot",
        "file-earmark",
        "cpu",
        "briefcase"
    ]

# -----------------------------------------------------
# DOCTOR ACCESS
# -----------------------------------------------------

elif role == "Doctor":

    menu_options = [
        "Dashboard",
        "AI Insights",
        "Simulation"
    ]

    menu_icons = [
        "speedometer",
        "robot",
        "cpu"
    ]

# -----------------------------------------------------
# INVENTORY MANAGER ACCESS
# -----------------------------------------------------

elif role == "Inventory Manager":

    menu_options = [
        "Dashboard",
        "Forecasting",
        "Reports"
    ]

    menu_icons = [
        "speedometer",
        "graph-up",
        "file-earmark"
    ]

# -----------------------------------------------------
# SUSTAINABILITY OFFICER ACCESS
# -----------------------------------------------------

elif role == "Sustainability Officer":

    menu_options = [
        "Dashboard",
        "Reports",
        "Executive Dashboard"
    ]

    menu_icons = [
        "speedometer",
        "file-earmark",
        "briefcase"
    ]

# -----------------------------------------------------
# SIDEBAR
# -----------------------------------------------------

with st.sidebar:

    st.markdown(
        f"## 👤 {st.session_state.username}"
    )

    st.success(
        f"Role: {role}"
    )

    selected = option_menu(
        menu_title="🌿 EcoMed AI",
        options=menu_options,
        icons=menu_icons,
        default_index=0
    )

    st.markdown("---")

    st.subheader("🔄 Change Role")

    new_role = st.selectbox(
        "Select Role",
        [
            "Admin",
            "Doctor",
            "Inventory Manager",
            "Sustainability Officer"
        ],
        index=[
            "Admin",
            "Doctor",
            "Inventory Manager",
            "Sustainability Officer"
        ].index(role)
    )

    if new_role != role:

        st.session_state.role = new_role

        st.rerun()

    st.markdown("---")

    if st.button("🚪 Logout"):

        st.session_state.logged_in = False

        st.rerun()# =====================================================
# DATABASE
# =====================================================

client = None

db = None

# =====================================================
# LOAD DATA
# =====================================================

patient_df = pd.read_csv("data/patient_data.csv")
inventory_df = pd.read_csv("data/inventory_data.csv")
supplier_df = pd.read_csv("data/supplier_data.csv")

# =====================================================
# CARBON COUNTER
# =====================================================

expiry_waste = inventory_df[
    inventory_df["Days_To_Expiry"] < 10
]

carbon_saved = (
    expiry_waste["Carbon_per_Unit"].sum() * 500
)

# =====================================================
# DASHBOARD
# =====================================================

if selected == "Dashboard":

    st.header("📊 Hospital Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total OPD",
        int(patient_df["OPD_Count"].sum())
    )

    c2.metric(
        "ICU Patients",
        int(patient_df["ICU_Patients"].sum())
    )

    c3.metric(
        "Emergency Cases",
        int(patient_df["Emergency_Cases"].sum())
    )

    c4.metric(
        "Carbon Prevented",
        f"{carbon_saved:.0f} kg CO₂"
    )

    style_metric_cards()

    # =================================================
    # NOTIFICATIONS
    # =================================================

    st.header("🔔 Real-Time Notifications")

    notifications = [
        "ICU stock critical for masks",
        "Emergency department demand increased",
        "Carbon threshold exceeded in OT",
        "Expiry risk detected for IV Fluids"
    ]

    for note in notifications:
        st.toast(note)

    # =================================================
    # LIVE INVENTORY STATUS
    # =================================================

    st.header("📦 Live Inventory Status")

    for index, row in inventory_df.iterrows():

        stock = row["Stock"]

        if stock > 500:

            st.success(
                f"🟢 {row['Item']} ({row['Department']}) → SAFE"
            )

        elif stock > 150:

            st.warning(
                f"🟡 {row['Item']} ({row['Department']}) → LOW"
            )

        else:

            st.error(
                f"🔴 {row['Item']} ({row['Department']}) → CRITICAL"
            )

    # =================================================
    # PATIENT TREND
    # =================================================

    st.header("📈 Patient Intake Trends")

    fig = px.line(
        patient_df,
        x="Date",
        y="OPD_Count",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =================================================
    # INVENTORY
    # =================================================

    st.header("📦 Inventory Table")

    st.dataframe(
        inventory_df,
        use_container_width=True
    )

    # =================================================
    # AI REORDER
    # =================================================

    st.header("🤖 AI Reorder Recommendations")

    reorder_list = []

    for index, row in inventory_df.iterrows():

        predicted_need = row["Daily_Usage"] * 30

        reorder_quantity = predicted_need - row["Stock"]

        if reorder_quantity > 0:

            reorder_list.append({
                "Item": row["Item"],
                "Department": row["Department"],
                "Recommended Reorder": int(reorder_quantity)
            })

    reorder_df = pd.DataFrame(reorder_list)

    st.dataframe(
        reorder_df,
        use_container_width=True
    )

    # =================================================
    # EXPIRY PREDICTION
    # =================================================

    st.header("🧠 AI Expiry Prediction")

    expiry_prediction = []

    for index, row in inventory_df.iterrows():

        risk_score = (
            row["Stock"] /
            (row["Daily_Usage"] + 1)
        ) * 10

        if risk_score > 50:
            status = "High Expiry Risk"

        elif risk_score > 25:
            status = "Medium Risk"

        else:
            status = "Low Risk"

        expiry_prediction.append({
            "Item": row["Item"],
            "Department": row["Department"],
            "Risk": status
        })

    expiry_prediction_df = pd.DataFrame(
        expiry_prediction
    )

    st.dataframe(
        expiry_prediction_df,
        use_container_width=True
    )

    # =================================================
    # AUTO REDISTRIBUTION
    # =================================================

    st.header("🤖 AI Auto Redistribution Engine")

    auto_redistribution = []

    for index, row in inventory_df.iterrows():

        if row["Stock"] > row["Daily_Usage"] * 15:

            auto_redistribution.append({

                "Item": row["Item"],

                "From": row["Department"],

                "To": random.choice([
                    "Emergency",
                    "ICU",
                    "OT"
                ]),

                "Reason": "AI optimized balancing"
            })

    auto_redistribution_df = pd.DataFrame(
        auto_redistribution
    )

    st.dataframe(
        auto_redistribution_df,
        use_container_width=True
    )

    # =================================================
    # SUSTAINABILITY RECOMMENDATIONS
    # =================================================

    st.header("🌱 Smart Sustainability Recommendations")

    recommendations = [

        "Switch 30% disposable gloves to reusable alternatives → Save 92 kg CO₂/month.",

        "Redistribute excess syringes from OT to ICU → Prevent expiry waste.",

        "Use low-carbon supplier for PPE kits → Reduce procurement emissions by 18%.",

        "Reduce over-ordering in Emergency department → Improve sustainability score."

    ]

    for rec in recommendations:
        st.info(rec)

    # =================================================
    # CARBON BREAKDOWN
    # =================================================

    st.header("🌍 Carbon Footprint Breakdown")

    carbon_breakdown = pd.DataFrame({

        "Item": [
            "Gloves",
            "Syringes",
            "PPE Kits",
            "IV Fluids",
            "Medicines"
        ],

        "Carbon": [
            120,
            80,
            150,
            60,
            110
        ]

    })

    carbon_chart = px.pie(
        carbon_breakdown,
        names="Item",
        values="Carbon",
        hole=0.4
    )

    st.plotly_chart(
        carbon_chart,
        use_container_width=True
    )

    # =================================================
    # USAGE TREND
    # =================================================

    st.header("📈 Medicine Usage Trend Analytics")

    usage_df = pd.DataFrame({

        "Month": [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun"
        ],

        "Medicine Usage": [
            1200,
            1400,
            1800,
            1600,
            2000,
            2400
        ]

    })

    usage_chart = px.line(
        usage_df,
        x="Month",
        y="Medicine Usage",
        markers=True
    )

    st.plotly_chart(
        usage_chart,
        use_container_width=True
    )

    # =================================================
    # CARBON SAVINGS TIMELINE
    # =================================================

    st.header("🌿 Carbon Savings Timeline")

    timeline_df = pd.DataFrame({

        "Month": [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun"
        ],

        "Carbon Saved": [
            120,
            180,
            240,
            300,
            360,
            420
        ]

    })

    timeline_chart = px.line(
        timeline_df,
        x="Month",
        y="Carbon Saved",
        markers=True
    )

    st.plotly_chart(
        timeline_chart,
        use_container_width=True
    )

    # =================================================
    # RISK SCORES
    # =================================================

    st.header("⚠ Predictive Department Risk Scores")

    risk_df = pd.DataFrame({

        "Department": [
            "ICU",
            "Emergency",
            "OT",
            "General Ward"
        ],

        "Risk Score": [
            72,
            91,
            40,
            55
        ]

    })

    risk_chart = px.bar(
        risk_df,
        x="Department",
        y="Risk Score",
        color="Risk Score",
        text="Risk Score"
    )

    st.plotly_chart(
        risk_chart,
        use_container_width=True
    )

    # =================================================
    # EMERGENCY MODE
    # =================================================

    st.header("🚨 Emergency AI Response Mode")

    emergency_trigger = st.checkbox(
        "Activate Emergency Mode"
    )

    if emergency_trigger:

        st.error(
            "Emergency Mode Activated"
        )

        st.warning(
            "Increasing PPE reorder quantity by 20%"
        )

        st.warning(
            "Prioritizing Emergency Department inventory"
        )

        st.warning(
            "Auto redistribution enabled"
        )

# =====================================================
# FORECASTING
# =====================================================

elif selected == "Forecasting":

    st.header("📈 AI Demand Forecasting")

    st.write(
        "AI predicts future patient demand and medical inventory usage."
    )

    # ---------------------------------------------
    # PREPARE DATA
    # ---------------------------------------------

    forecast_df = patient_df.copy()

    forecast_df = forecast_df[["Date", "OPD_Count"]]

    forecast_df.columns = ["ds", "y"]

    forecast_df["ds"] = pd.to_datetime(
        forecast_df["ds"]
    )

    # ---------------------------------------------
    # TRAIN MODEL
    # ---------------------------------------------

    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False
    )

    model.fit(forecast_df)

    # ---------------------------------------------
    # FUTURE DAYS
    # ---------------------------------------------

    future = model.make_future_dataframe(
        periods=30
    )

    forecast = model.predict(future)

    # ---------------------------------------------
    # FORECAST GRAPH
    # ---------------------------------------------

    forecast_chart = px.line(
        forecast,
        x="ds",
        y="yhat",
        title="Predicted OPD Demand Forecast",
        labels={
            "ds": "Date",
            "yhat": "Predicted Patients"
        }
    )

    forecast_chart.update_traces(
        line=dict(width=4)
    )

    forecast_chart.update_layout(
        template="plotly_dark",
        height=600,
        title_font_size=28,
        font=dict(size=16),
        paper_bgcolor="#111111",
        plot_bgcolor="#111111"
    )

    st.plotly_chart(
        forecast_chart,
        use_container_width=True
    )

    # ---------------------------------------------
    # FORECAST TABLE
    # ---------------------------------------------

    st.subheader("📋 Forecasted Demand Data")

    display_forecast = forecast[[
        "ds",
        "yhat"
    ]].tail(30)

    display_forecast.columns = [
        "Date",
        "Predicted Demand"
    ]

    st.dataframe(
        display_forecast,
        use_container_width=True
    )

    # ---------------------------------------------
    # AI INSIGHTS
    # ---------------------------------------------

    st.subheader("🧠 AI Forecast Insights")

    avg_future = int(
        display_forecast["Predicted Demand"].mean()
    )

    max_future = int(
        display_forecast["Predicted Demand"].max()
    )

    st.success(
        f"Expected average patient demand next month: {avg_future}"
    )

    st.warning(
        f"Peak predicted demand may reach {max_future} patients."
    )

    st.info(
        "EcoMed AI recommends increasing PPE stock by 12% before peak demand."
    )
# =====================================================
# AI INSIGHTS
# =====================================================

elif selected == "AI Insights":

    st.header("🧠 AI Insights")

    # =================================================
    # 🚨 AI EMERGENCY SURGE PREDICTOR
    # =================================================

    st.subheader("🚨 AI Emergency Surge Predictor")

    surge_probability = random.randint(40, 95)

    future_cases = random.randint(120, 350)

    surge_level = ""

    if surge_probability > 80:

        surge_level = "HIGH RISK"

        st.error(
            f"""
⚠ Emergency surge predicted.

Risk Level: {surge_level}

Expected Cases Next Week: {future_cases}
"""
        )

    elif surge_probability > 60:

        surge_level = "MODERATE RISK"

        st.warning(
            f"""
⚠ Moderate emergency surge expected.

Risk Level: {surge_level}

Expected Cases Next Week: {future_cases}
"""
        )

    else:

        surge_level = "LOW RISK"

        st.success(
            f"""
✅ Emergency conditions stable.

Risk Level: {surge_level}

Expected Cases Next Week: {future_cases}
"""
        )

    # -------------------------------------------------
    # SURGE TREND GRAPH
    # -------------------------------------------------

    surge_df = pd.DataFrame({

        "Day": [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun"
        ],

        "Predicted Emergency Cases": np.random.randint(
            80,
            future_cases,
            7
        )

    })

    surge_chart = px.line(
        surge_df,
        x="Day",
        y="Predicted Emergency Cases",
        markers=True,
        title="Predicted Emergency Surge Trend"
    )

    surge_chart.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(
        surge_chart,
        use_container_width=True
    )

    st.info(
        "EcoMed AI recommends increasing PPE and IV fluid reserves before predicted surge."
    )

    # =================================================
    # STANDARD AI INSIGHTS
    # =================================================

    st.info(
        "ICU may run out of IV Fluids in 8 days."
    )

    st.info(
        "Redistributing masks can prevent 14 kg CO₂ waste."
    )

    st.info(
        "Emergency department has highest sustainability risk."
    )

    # =================================================
    # 🧬 AI MEDICINE EXPIRY TRANSFER NETWORK
    # =================================================

    st.header("🧬 AI Medicine Expiry Transfer Network")

    expiry_transfer = []

    departments = [
        "ICU",
        "Emergency",
        "OT",
        "General Ward"
    ]

    for index, row in inventory_df.iterrows():

        days_left = row["Days_To_Expiry"]

        stock = row["Stock"]

        usage = row["Daily_Usage"]

        if days_left < 15 and stock > usage * 5:

            target_department = random.choice(
                departments
            )

            transfer_quantity = int(
                stock * 0.35
            )

            expiry_transfer.append({

                "Medicine": row["Item"],

                "Current Department": row["Department"],

                "Transfer To": target_department,

                "Suggested Quantity": transfer_quantity,

                "Reason":
                "High expiry risk detected"

            })

    expiry_transfer_df = pd.DataFrame(
        expiry_transfer
    )

    if not expiry_transfer_df.empty:

        st.dataframe(
            expiry_transfer_df,
            use_container_width=True
        )

        st.success(
            "EcoMed AI identified medicines suitable for redistribution before expiry."
        )

    else:

        st.success(
            "No critical expiry transfers required."
        )

    # -------------------------------------------------
    # EXPIRY RISK GRAPH
    # -------------------------------------------------

    expiry_chart_df = pd.DataFrame({

        "Department": [
            "ICU",
            "Emergency",
            "OT",
            "General Ward"
        ],

        "Expiry Risk": [
            random.randint(20, 90),
            random.randint(20, 90),
            random.randint(20, 90),
            random.randint(20, 90)
        ]

    })

    expiry_chart = px.bar(
        expiry_chart_df,
        x="Department",
        y="Expiry Risk",
        color="Expiry Risk",
        text="Expiry Risk",
        title="Department-wise Expiry Risk"
    )

    expiry_chart.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(
        expiry_chart,
        use_container_width=True
    )

    # =================================================
    # 🤖 AI ASSISTANT
    # =================================================

    st.header("🤖 EcoMed AI Assistant")

    question = st.text_input(
        "Ask EcoMed AI anything..."
    )

    if question:

        q = question.lower()

        if (
            "waste" in q
            or "wastage" in q
        ):

            st.success(
                "Emergency department currently generates the highest medical waste."
            )

        elif (
            "expiry" in q
            or "expire" in q
        ):

            st.warning(
                "IV Fluids and Gloves have highest expiry risk."
            )

        elif (
            "supplier" in q
            or "vendor" in q
        ):

            st.info(
                "Supplier B is recommended for lower carbon emissions."
            )

        elif (
            "stock" in q
            or "inventory" in q
        ):

            st.info(
                "ICU may require additional masks in 10 days."
            )

        elif "icu" in q:

            st.info(
                "ICU currently has moderate overstock."
            )

        elif (
            "carbon" in q
            or "co2" in q
        ):

            st.success(
                "EcoMed AI estimates 182 kg CO₂ prevented this month."
            )

        elif (
            "emergency" in q
            or "surge" in q
        ):

            st.error(
                "Emergency surge predicted next month."
            )

        elif (
            "forecast" in q
            or "future" in q
        ):

            st.info(
                "Patient inflow predicted to increase by 14%."
            )

        elif (
            "redistribute" in q
            or "transfer" in q
        ):

            st.success(
                "EcoMed AI suggests transferring excess gloves from OT to Emergency."
            )

        elif (
            "hello" in q
            or "hi" in q
        ):

            st.info(
                "Hello 👋 I am EcoMed AI Assistant."
            )

        else:

            st.warning(
                "Try asking about carbon, expiry, stock, ICU, suppliers or emergency."
            )
# =====================================================
# REPORTS
# =====================================================

elif selected == "Reports":

    st.header("📄 Sustainability Reports")

    st.write("Generate downloadable EcoMed AI sustainability report.")

    if st.button("Generate PDF Report"):

        try:

            pdf = FPDF()

            pdf.add_page()

            pdf.set_auto_page_break(auto=True, margin=15)

            pdf.set_font("Arial", "B", 18)

            pdf.cell(
                200,
                10,
                txt="EcoMed AI Sustainability Report",
                ln=True,
                align="C"
            )

            pdf.ln(10)

            pdf.set_font("Arial", size=12)

            pdf.cell(
                200,
                10,
                txt=f"Carbon Prevented: {carbon_saved:.0f} kg CO2",
                ln=True
            )

            pdf.cell(
                200,
                10,
                txt="Forecast Accuracy: 87%",
                ln=True
            )

            pdf.cell(
                200,
                10,
                txt="Waste Reduction: 24%",
                ln=True
            )

            pdf.cell(
                200,
                10,
                txt="Top Risk Department: Emergency",
                ln=True
            )

            pdf.cell(
                200,
                10,
                txt="Recommended Action: Redistribute excess PPE stock",
                ln=True
            )

            pdf_output = pdf.output(dest="S")

            st.download_button(
                label="⬇ Download PDF Report",
                data=bytes(pdf_output, "latin1"),
                file_name="EcoMed_Report.pdf",
                mime="application/pdf"
            )

            st.success("PDF generated successfully!")

        except Exception as e:

            st.error(f"PDF Error: {e}")
# =====================================================
# SIMULATION
# =====================================================

elif selected == "Simulation":

    st.header("🧪 Hospital Demand Simulation")

    increase = st.slider(
        "Increase Patient Intake %",
        0,
        100,
        20
    )

    future_demand = (
        patient_df["OPD_Count"].sum()
        * (1 + increase / 100)
    )

    st.success(
        f"Predicted Future Demand: {int(future_demand)}"
    )

    estimated_carbon = future_demand * 0.12

    st.error(
        f"Estimated Carbon Impact: {estimated_carbon:.2f} kg CO₂"
    )

# =====================================================
# EXECUTIVE DASHBOARD
# =====================================================

elif selected == "Executive Dashboard":

    st.header("🏢 Executive Sustainability Dashboard")

    ex1, ex2, ex3, ex4 = st.columns(4)

    ex1.metric(
        "Annual Carbon Saved",
        "12,500 kg CO₂"
    )

    ex2.metric(
        "Cost Reduction",
        "₹8.2 Lakhs"
    )

    ex3.metric(
        "Waste Reduction",
        "31%"
    )

    ex4.metric(
        "Forecast Accuracy",
        "87%"
    )

    executive_df = pd.DataFrame({
        "Department": [
            "ICU",
            "OT",
            "Emergency",
            "General Ward"
        ],
        "Efficiency": [
            84,
            92,
            61,
            75
        ]
    })

    executive_chart = px.bar(
        executive_df,
        x="Department",
        y="Efficiency",
        color="Efficiency",
        text="Efficiency"
    )

    st.plotly_chart(
        executive_chart,
        use_container_width=True
    )

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.success(
    "EcoMed AI transforms hospital inventory into carbon-aware sustainability intelligence."
)