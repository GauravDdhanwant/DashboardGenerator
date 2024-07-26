import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import requests

# Function to fetch insights using Llamma 3.1 API
def fetch_insights(api_key, data):
    url = "https://api.llamma3.1/insights"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Function to calculate advanced KPIs
def calculate_advanced_kpis(df):
    kpis = {
        'Mean': df.mean(),
        'Median': df.median(),
        'Std Dev': df.std(),
        'Total Sales': df['Sales'].sum() if 'Sales' in df.columns else None,
        'Customer Retention Rate': (df['Retained Customers'].sum() / df['Total Customers'].sum()) * 100 if 'Retained Customers' in df.columns and 'Total Customers' in df.columns else None,
        'Profitability': (df['Profit'].sum() / df['Revenue'].sum()) * 100 if 'Profit' in df.columns and 'Revenue' in df.columns else None
    }
    return kpis

# Function to generate visualizations
def generate_visualizations(df, n_charts, chart_types):
    st.subheader('Generated Visuals')
    for i in range(n_charts):
        chart_type = chart_types[i]
        if chart_type == 'Line Chart':
            st.line_chart(df)
        elif chart_type == 'Bar Chart':
            st.bar_chart(df)
        elif chart_type == 'Heatmap':
            fig, ax = plt.subplots()
            sns.heatmap(df.corr(), ax=ax, annot=True)
            st.pyplot(fig)
        else:
            st.write(f"Chart {i+1}")
            st.line_chart(df)

# Streamlit layout
st.sidebar.title("Advanced Dashboard Generator")
st.sidebar.header("Upload Data or Connect to Database")

upload_option = st.sidebar.radio("Choose data source:", ("Upload File", "Database Connection"))

if upload_option == "Upload File":
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=['csv', 'xlsx'])
    if uploaded_file:
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.write("File uploaded successfully!")
else:
    db_url = st.sidebar.text_input("Database URL")
    table_name = st.sidebar.text_input("Table Name")
    if st.sidebar.button("Connect"):
        engine = create_engine(db_url)
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        st.sidebar.write("Connected to database successfully!")

if 'df' in locals():
    st.sidebar.header("API Key for Llamma 3.1")
    api_key = st.sidebar.text_input("Enter your API Key", type="password")
    if api_key:
        insights = fetch_insights(api_key, df.to_dict())
        st.sidebar.write("Insights fetched successfully!")
        st.write("Generated Insights:")
        st.write(insights)

    st.sidebar.header("Visualizations")
    n_charts = st.sidebar.slider("Number of visualizations", 1, 10, 3)
    chart_types = st.sidebar.multiselect("Choose chart types:", ["Line Chart", "Bar Chart", "Heatmap"], default=["Line Chart"])

    st.sidebar.header("KPI Calculation")
    if st.sidebar.button("Generate Dashboard"):
        kpis = calculate_advanced_kpis(df)
        st.write("Calculated KPIs")
        st.write(kpis)
        generate_visualizations(df, n_charts, chart_types)
else:
    st.write("Upload a file or connect to a database to proceed.")
