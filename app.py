import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="Wind Energy Dashboard", page_icon="🌪️", layout="wide")

# --- Title ---
st.title("🌪️ Wind Energy Feasibility Dashboard")
st.markdown("**Find out if your location is good for wind energy!** *Built for #1M1B Green Internship*")

# --- Sidebar ---
st.sidebar.markdown("### 📍 Sample Locations to Try:")
st.sidebar.code("Texas: 32.7767, -96.7970")
st.sidebar.code("Iowa: 41.5868, -93.6250")
st.sidebar.code("Kansas: 39.0119, -98.4842")
st.sidebar.code("California: 34.0522, -118.2437")
st.sidebar.markdown("---")


# --- Inputs ---
col1, col2 = st.columns(2)
with col1:
    latitude = st.number_input("📍 Enter Latitude", value=40.0, format="%.4f")
with col2:
    longitude = st.number_input("📍 Enter Longitude", value=-100.0, format="%.4f")

location_name = st.text_input("🏷️ Location Name (Optional)", placeholder="e.g., My Farm, Dallas")

# --- Fetch wind data ---
def fetch_hourly_winds(lat, lon, start, end):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start}&end_date={end}"
        "&hourly=windspeed_10m"
    )
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame({
        "time": pd.to_datetime(data["hourly"]["time"]),
        "wind_speed": data["hourly"]["windspeed_10m"]
    })
    return df

# --- Button ---
if st.button("🔍 Analyze Wind Potential (Live Data)", type="primary"):
    with st.spinner(f"Analyzing wind potential for {latitude}, {longitude}..."):
        end_date = datetime.today()
        start_date = end_date - timedelta(days=7)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        df_hourly = fetch_hourly_winds(latitude, longitude, start_str, end_str)
        df_daily = df_hourly.resample("D", on="time").mean().reset_index()

        st.success(f"✅ Analysis Complete for {location_name if location_name else 'Location'}")

        # --- Chart ---
        fig = px.line(
            df_daily, x="time", y="wind_speed",
            title="Daily Average Wind Speed (last 7 days)",
            labels={"wind_speed": "Wind Speed (m/s)", "time": "Date"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Key Metrics ---
        avg_wind = df_hourly["wind_speed"].mean()

        if 3 <= avg_wind <= 25:
            if avg_wind <= 12:
                power_output = 5 * (avg_wind / 12) ** 3
            else:
                power_output = 5
        else:
            power_output = 0

        capacity_factor = min(power_output / 5 * 100, 100) if power_output > 0 else 0
        annual_energy = power_output * 24 * 365 * (capacity_factor / 100)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌬️ Avg Wind Speed", f"{avg_wind:.1f} m/s")
        col2.metric("⚡ Power Output", f"{power_output:.1f} kW")
        col3.metric("📊 Capacity Factor", f"{capacity_factor:.0f}%")
        col4.metric("🔋 Annual Energy", f"{annual_energy:,.0f} kWh")

        # --- Recommendation ---
        st.markdown("---")
        if avg_wind >= 8:
            st.success("🎯 **EXCELLENT** Wind Resource! Highly recommended for commercial development.")
        elif avg_wind >= 6:
            st.warning("⚠️ **GOOD** Wind Resource. Suitable for small-scale development.")
        elif avg_wind >= 4:
            st.info("📊 **FAIR** Wind Resource. Feasible with efficient turbines.")
        else:
            st.error("❌ **POOR** Wind Resource. Not economically viable.")

        # --- Monthly Synthetic Trends ---
        st.subheader("📈 Seasonal Wind Trends (Synthetic Example)")
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        seasonal_multipliers = [1.15,1.10,1.05,0.95,0.85,0.80,0.75,0.80,0.90,1.00,1.05,1.10]
        monthly_speeds = [avg_wind * m + random.uniform(-0.3, 0.3) for m in seasonal_multipliers]
        monthly_power = [5 * (s/12)**3 if 3 <= s <= 12 else (5 if 12 < s <= 25 else 0) for s in monthly_speeds]

        df_monthly = pd.DataFrame({
            "Month": months,
            "Wind Speed": monthly_speeds,
            "Power Output": monthly_power
        })

        col1, col2 = st.columns(2)
        with col1:
            fig_wind = px.line(df_monthly, x="Month", y="Wind Speed", title="Monthly Avg Wind Speed")
            st.plotly_chart(fig_wind, use_container_width=True)
        with col2:
            fig_power = px.bar(df_monthly, x="Month", y="Power Output", title="Monthly Power Output (kW)")
            st.plotly_chart(fig_power, use_container_width=True)

        # --- Economic Analysis ---
        st.subheader("💰 Economic Analysis (5kW Turbine)")
        turbine_cost = 25000
        installation_cost = 15000
        maintenance_yearly = 1000
        electricity_price = 0.12  # USD per kWh

        annual_revenue = annual_energy * electricity_price
        annual_profit = annual_revenue - maintenance_yearly
        total_investment = turbine_cost + installation_cost

        if annual_profit > 0:
            payback_period = total_investment / annual_profit
            roi_20_year = ((annual_profit * 20) - total_investment) / total_investment * 100
        else:
            payback_period = float("inf")
            roi_20_year = -100

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💲 Initial Investment", f"${total_investment:,}")
        col2.metric("📊 Annual Revenue", f"${annual_revenue:,.0f}")
        col3.metric("⏰ Payback Period", f"{payback_period:.1f} years" if payback_period != float("inf") else "N/A")
        col4.metric("📈 20-Year ROI", f"{roi_20_year:.0f}%")

        # --- Summary ---
        st.subheader("📋 Summary & Next Steps")
        summary_data = {
            "Metric": ["Avg Wind Speed", "Power Output", "Annual Energy", "Capacity Factor", "Economic Viability"],
            "Value": [f"{avg_wind:.1f} m/s", f"{power_output:.1f} kW", f"{annual_energy:,.0f} kWh", f"{capacity_factor:.0f}%", "Good" if roi_20_year > 0 else "Poor"],
            "Rating": ["Excellent" if avg_wind >= 8 else "Good" if avg_wind >= 6 else "Fair" if avg_wind >= 4 else "Poor"] * 5
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        if avg_wind >= 6:
            st.success("""
            ✅ **Recommended Next Steps:**
            1. Conduct detailed wind measurement study (12+ months)  
            2. Check zoning & permitting requirements  
            3. Get quotes from turbine installers  
            4. Apply for renewable energy incentives  
            5. Explore community/shared ownership models  
            """)
        else:
            st.info("""
            💡 **Alternative Recommendations:**
            1. Consider solar energy potential  
            2. Improve energy efficiency first  
            3. Explore nearby community wind projects  
            4. Monitor wind conditions longer term  
            """)

# --- Footer ---
st.markdown("---")
st.markdown("**🌪️ Wind Energy Feasibility Dashboard** | Built with Streamlit | #1M1B Green Internship Project")

