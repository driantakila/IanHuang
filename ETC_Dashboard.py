import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="ETC Consulting Dashboard", layout="wide")

# --- Initialize Session State (To keep data persistent across page refreshes) ---
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
    # 1. Define your GitHub Raw URL
    # IMPORTANT: Ensure the URL points to 'raw.githubusercontent.com', not 'github.com'
    github_raw_url = "https://etcinstitute.com/wp-content/uploads/2023/09/ETC-NewLogo-Horizontal-Web.png"
    
    # 2. Try to display the image from GitHub
    try:
        st.image(github_raw_url, width=400)
    except Exception as e:
        # Fallback if the URL is broken or there is no internet
        st.title("🏢 ETC Consulting Group")
        st.error(f"Error loading logo from GitHub: {e}")
    
    st.header("About Us")
    st.write("""
    We are a data-driven consulting firm specializing in survey research that helps communities 
    and organizations use data to understand needs, evaluate services, and plan improvements. 
    
    Our mission is to provide evidence-based solutions that drive measurable impact.
    """)
    
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
# DEPARTMENTS SECTION (Dynamic Data Connection)
# -------------------------
elif page == "Departments":
    st.title("🏢 Departmental Analysis & Goal Tracking")

    # 1. Check if data exists
    if st.session_state.data is None:
        st.warning("⚠️ No data loaded. Please upload the 'v2' Excel file in File Manager.")
    else:
        df_all = st.session_state.data

        # 2. Selection Filters
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            department = st.selectbox("Select Department", list(company_structure.keys()))
        with col_b:
            manager = st.selectbox("Select Manager", list(company_structure[department].keys()))
        with col_c:
            project = st.selectbox("Select Project", company_structure[department][manager])

        if project:
            # 3. Filter Data for selected project
            df = df_all[(df_all['Department'] == department) & 
                        (df_all['Project'] == project)].sort_values("Month")

            if df.empty:
                st.info(f"💡 No data found for **{project}**. Check if your Excel content matches.")
            else:
                # --- 4. CALCULATIONS (Profit & Margins) ---
                df['Profit'] = df['Revenue'] - df['Expenses']
                
                # Get Target_Profit from Excel (using the first row of selected project)
                PROFIT_GOAL = df['Target_Profit'].iloc[0] if 'Target_Profit' in df.columns else 50000
                
                avg_profit = df['Profit'].mean()
                total_rev = df['Revenue'].sum()
                avg_margin = (df['Profit'].sum() / total_rev * 100) if total_rev != 0 else 0

                # --- 5. KPI METRICS (The "Main Goal" View) ---
                st.subheader(f"🎯 Performance Metrics: {project}")
                m1, m2, m3 = st.columns(3)
                
                # Calculate delta from goal
                profit_delta = ((avg_profit - PROFIT_GOAL) / PROFIT_GOAL * 100)
                
                m1.metric("Avg. Monthly Profit", f"${avg_profit:,.0f}", f"{profit_delta:.1f}% vs Goal")
                m2.metric("Net Profit Margin", f"{avg_margin:.1f}%", "Target: 30%+")
                m3.metric("Monthly Profit Goal", f"${PROFIT_GOAL:,.0f}")

                # --- 6. VISUALIZATION (Profit vs Target Line) ---
                st.markdown("---")
                st.write("### 📈 Profit Trend vs. Target Goal")
                
                fig_p, ax_p = plt.subplots(figsize=(10, 4))
                
                # Plot Actual Profit
                ax_p.plot(df["Month"], df["Profit"], marker='o', label="Actual Profit", color='#2ca02c', linewidth=2)
                
                # Plot Target Line
                ax_p.axhline(y=PROFIT_GOAL, color='#d62728', linestyle='--', label="Target Goal", linewidth=2)
                
                # Fill colors: Green for above goal, Red for below
                ax_p.fill_between(df["Month"], df["Profit"], PROFIT_GOAL, 
                                 where=(df["Profit"] >= PROFIT_GOAL), color='green', alpha=0.15)
                ax_p.fill_between(df["Month"], df["Profit"], PROFIT_GOAL, 
                                 where=(df["Profit"] < PROFIT_GOAL), color='red', alpha=0.15)
                
                ax_p.set_ylabel("Amount ($)")
                ax_p.legend(loc='upper left')
                plt.xticks(rotation=45)
                st.pyplot(fig_p)

                # --- 7. REVENUE & EXPENSE DETAILS ---
                st.markdown("---")
                st.write("### 🔍 Revenue & Expense Breakdown")
                col_rev, col_exp = st.columns(2)
                
                with col_rev:
                    st.write("**Monthly Revenue**")
                    st.line_chart(df.set_index("Month")["Revenue"])
                
                with col_exp:
                    st.write("**Monthly Expenses**")
                    st.line_chart(df.set_index("Month")["Expenses"])
# -------------------------
# FILE MANAGER
# -------------------------
elif page == "File Manager":
    st.title("📁 Data Management")
    st.write("Upload the standardized Excel file to populate the departmental dashboard.")
    
    # Allow both XLSX and CSV formats
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "csv"])

    if uploaded_file:
        st.success("File uploaded successfully!")
        try:
            # Detect file extension and read accordingly
            if uploaded_file.name.endswith('.csv'):
                df_loaded = pd.read_csv(uploaded_file)
            else:
                df_loaded = pd.read_excel(uploaded_file)
            
            # Data Cleaning: Strip whitespaces from column headers
            df_loaded.columns = df_loaded.columns.str.strip()
            
            # Save the dataframe to st.session_state for cross-page access
            st.session_state.data = df_loaded
            
            st.write("### Data Preview")
            st.dataframe(df_loaded.head())
        except Exception as e:
            st.error(f"Error reading file: {e}")