import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="ETC Consulting Dashboard", layout="wide")

# --- Initialize Session State ---
if "data" not in st.session_state:
    st.session_state.data = None

# -------------------------
# SAMPLE COMPANY STRUCTURE
# -------------------------
company_structure = {
    "Household Survey Research": {
        "Sarah Johnson": ["Project 1", "Project 2"],
        "Michael Brown": ["Project 3", "Project 4"]
    },
    "Transportation Research": {
        "David Smith": ["Project 5", "Project 6"]
    },
    "Public Transit Research": {
        "Emily Clark": ["Project 7", "Project 8"]
    },
    "Data Management and Visualization": {
        "James Wilson": ["Project 9", "Project 10"]
    },
    "Community Research": {
        "Anna Martinez": ["Project 11", "Project 12"]
    },
    "Market Development and Communications": {
        "Robert Davis": ["Project 13", "Project 14"]
    },
}

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
page = st.sidebar.radio(
    "Navigation",
    ["Homepage", "Departments", "File Manager"]
)

# -------------------------
# HOMEPAGE
# -------------------------
if page == "Homepage":
    github_raw_url = "https://etcinstitute.com/wp-content/uploads/2023/09/ETC-NewLogo-Horizontal-Web.png"
    try:
        st.image(github_raw_url, width=400)
    except Exception as e:
        st.title("🏢 ETC Consulting Group")
    
    st.header("About Us")
    st.write("We are a data-driven consulting firm specializing in survey research. Our mission is to provide evidence-based solutions that drive measurable impact.")
    
    st.header("Our Expertise")
    st.write("""
    - Household Survey Research  
    - Transportation Research  
    - Public Transit Research  
    - Data Management and Visualization  
    - Community Research
    - Market Development and Communications
    """)

# -------------------------
# DEPARTMENTS SECTION (Modified for Company Overview)
# -------------------------
elif page == "Departments":
    st.title("🏢 Performance Analysis & Goal Tracking")

    if st.session_state.data is None:
        st.warning("⚠️ No data loaded. Please upload the Excel file in File Manager.")
    else:
        df_all = st.session_state.data

        # 1. Selection Filters with "Total Company" Option
        col_a, col_b, col_c = st.columns(3)
        
        dept_options = ["Total Company (All Departments)"] + list(company_structure.keys())
        
        with col_a:
            selected_dept = st.selectbox("Select Department", dept_options)
        
        # Logic to handle Total Company vs Individual Dept
        if selected_dept == "Total Company (All Departments)":
            # AGGREGATION LOGIC: Group all data by Month and Sum values
            df = df_all.groupby("Month").agg({
                "Revenue": "sum",
                "Expenses": "sum",
                "Target_Profit": "sum"
            }).reset_index().sort_values("Month")
            
            display_name = "Total Company Overview"
            manager = "N/A"
            project = "All Projects Combined"
            
            with col_b: st.selectbox("Select Manager", ["Disabled"], disabled=True)
            with col_c: st.selectbox("Select Project", ["Disabled"], disabled=True)
        else:
            # Individual Department Logic
            with col_b:
                manager = st.selectbox("Select Manager", list(company_structure[selected_dept].keys()))
            with col_c:
                project = st.selectbox("Select Project", company_structure[selected_dept][manager])
            
            df = df_all[(df_all['Department'] == selected_dept) & 
                        (df_all['Project'] == project)].sort_values("Month")
            display_name = f"Project: {project}"

        if not df.empty:
            # --- 2. CALCULATIONS ---
            df['Profit'] = df['Revenue'] - df['Expenses']
            
            # Use summed Target_Profit for Company view, or single value for Project view
            PROFIT_GOAL = df['Target_Profit'].iloc[0] if selected_dept != "Total Company (All Departments)" else df['Target_Profit'].sum() / len(df)
            
            avg_profit = df['Profit'].mean()
            total_rev = df['Revenue'].sum()
            avg_margin = (df['Profit'].sum() / total_rev * 100) if total_rev != 0 else 0

            # --- 3. KPI METRICS ---
            st.subheader(f"🎯 {display_name}")
            m1, m2, m3 = st.columns(3)
            profit_delta = ((avg_profit - PROFIT_GOAL) / PROFIT_GOAL * 100) if PROFIT_GOAL != 0 else 0
            
            m1.metric("Avg. Monthly Profit", f"${avg_profit:,.0f}", f"{profit_delta:.1f}% vs Goal")
            m2.metric("Net Profit Margin", f"{avg_margin:.1f}%", "Target: 30%+")
            m3.metric("Combined Profit Goal", f"${PROFIT_GOAL:,.0f}")

            # --- 4. VISUALIZATION ---
            st.write(f"### 📈 {display_name}: Profit Trend vs. Target")
            fig_p, ax_p = plt.subplots(figsize=(10, 4))
            ax_p.plot(df["Month"], df["Profit"], marker='o', label="Actual Profit", color='#2ca02c', linewidth=2)
            ax_p.axhline(y=PROFIT_GOAL, color='#d62728', linestyle='--', label="Target Goal", linewidth=2)
            
            ax_p.fill_between(df["Month"], df["Profit"], PROFIT_GOAL, 
                             where=(df["Profit"] >= PROFIT_GOAL), color='green', alpha=0.15)
            ax_p.fill_between(df["Month"], df["Profit"], PROFIT_GOAL, 
                             where=(df["Profit"] < PROFIT_GOAL), color='red', alpha=0.15)
            
            ax_p.set_ylabel("Amount ($)")
            ax_p.legend(loc='upper left')
            plt.xticks(rotation=45)
            st.pyplot(fig_p)

            # --- 5. BREAKDOWN ---
            st.markdown("---")
            st.write("### 🔍 Revenue & Expense Breakdown")
            col_rev, col_exp = st.columns(2)
            with col_rev:
                st.write("**Monthly Revenue**")
                st.line_chart(df.set_index("Month")["Revenue"])
            with col_exp:
                st.write("**Monthly Expenses**")
                st.line_chart(df.set_index("Month")["Expenses"])
        else:
            st.info("💡 No data found. Please check your filter selection or data content.")

# -------------------------
# FILE MANAGER
# -------------------------
elif page == "File Manager":
    st.title("📁 Data Management")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "csv"])

    if uploaded_file:
        try:
            df_loaded = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            df_loaded.columns = df_loaded.columns.str.strip()
            st.session_state.data = df_loaded
            st.success("File uploaded successfully!")
            st.dataframe(df_loaded.head())
        except Exception as e:
            st.error(f"Error reading file: {e}")
