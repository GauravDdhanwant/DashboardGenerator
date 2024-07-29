import streamlit as st
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt
import seaborn as sns
from gemini import GeminiClient

# Initialize the Streamlit app
st.set_page_config(page_title="Dashboard Generator", layout="wide")

# Sidebar for user inputs
st.sidebar.header("Dashboard Generator")
st.sidebar.subheader("Upload Data or Connect to Database")

# User input for Gemini API Key
gemini_api_key_input = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not gemini_api_key_input:
    st.error("Gemini API key is not set. Please provide it to proceed.")

# User input for number of visualizations
num_visuals = st.sidebar.slider("Number of Visualizations", 1, 10, 3)

# Option to upload file or connect to database
data_source = st.sidebar.selectbox("Data Source", ["Upload File", "Connect to Database"])

# Load data based on user input
data = None
if data_source == "Upload File":
    uploaded_file = st.sidebar.file_uploader("Choose a file")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
else:
    db_url = st.sidebar.text_input("Database URL")
    table_name = st.sidebar.text_input("Table Name")
    if st.sidebar.button("Load Data"):
        try:
            engine = sqlalchemy.create_engine(db_url)
            data = pd.read_sql_table(table_name, engine)
        except Exception as e:
            st.error(f"Error loading data from database: {str(e)}")

# Function to get insights using Gemini API
def get_insights(api_key, data):
    client = GeminiClient(api_key)
    insights = client.analyze(data)
    return insights

# Function to generate visualizations
def generate_visuals(data, insights, num_visuals):
    visuals = []
    for i in range(num_visuals):
        kpi = insights["KPIs"][i % len(insights["KPIs"])]
        calc_kpi = kpi  # Example calculation to make KPI more meaningful
        fig, ax = plt.subplots()
        if kpi["type"] == "bar":
            sns.barplot(x=data[kpi["x"]], y=data[kpi["y"]], ax=ax)
        elif kpi["type"] == "line":
            sns.lineplot(x=data[kpi["x"]], y=data[kpi["y"]], ax=ax)
        elif kpi["type"] == "scatter":
            sns.scatterplot(x=data[kpi["x"]], y=data[kpi["y"]], ax=ax)
        ax.set_title(f"{kpi['name']} (Calculated: {calc_kpi})")
        visuals.append(fig)
    return visuals

# Main panel for dashboard
if data is not None:
    st.header("Generated Dashboard")
    insights = get_insights(gemini_api_key_input, data)
    visuals = generate_visuals(data, insights, num_visuals)
    for fig in visuals:
        st.pyplot(fig)
else:
    st.info("Please upload a file or connect to a database.")

# Text box for prompting
prompt_text = st.text_area("Customizations Prompt")

# Apply customizations based on user input
if prompt_text:
    st.write(f"Customizations: {prompt_text}")
    # Implement customizations based on prompt_text

