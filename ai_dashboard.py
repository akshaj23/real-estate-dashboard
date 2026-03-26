import streamlit as st
import pandas as pd
import ollama


df = pd.read_csv("df = pd.read_csv("leaseup_dashboard_data.csv"))

market_txt = df.groupby('Market')['LeaseUpTime'].mean().round(2).to_string()
archetype_txt = df.groupby('Archetype')[['LeaseUpTime', 'Premium_to_Submarket_Pct']].mean().round(3).to_string()
submarket_txt = df.groupby('Submarket')['Premium_to_Submarket_Pct'].mean().sort_values(ascending=False).head(5).round(3).to_string()


top_props = df.sort_values('Premium_to_Submarket_Pct', ascending=False).groupby('Archetype').head(5)
top_props_txt = top_props[['Archetype', 'Submarket', 'Name']].to_string(index=False)

data_summary = f"""
Here is the Real Estate Investment Data Summary:

Overall Portfolio:
- Total Properties Analyzed: {len(df)}
- Average Lease-Up Time: {df['LeaseUpTime'].mean():.1f} months

Performance by Archetype (Lease-Up Time and Premium Percentage):
{archetype_txt}

Top 5 Highest Yielding Submarkets (Districts):
{submarket_txt}

Top Recommended Properties by Archetype and Submarket:
{top_props_txt}
"""
st.set_page_config(page_title="Investment AI Assistant", layout="wide")
st.title("🏙️ Real Estate Investment Dashboard")

with st.sidebar:
    st.header("Market Stats")
    st.dataframe(df.groupby('Archetype')['LeaseUpTime'].mean())
    st.write("---")
    st.write("Data processed and ready for NLP analysis.")


st.write("---")
st.subheader("📍 Geotag Explorer: Find the Right Locality")
st.write("Select an investment strategy below to see where those properties are successfully being built.")

col1, col2 = st.columns([1, 3])

with col1:
    options = ["All Properties"] + list(df['Archetype'].dropna().unique())
    selected_type = st.radio("Filter by Property Type:", options)

with col2:
    if selected_type == "All Properties":
        map_df = df.copy()
    else:
        map_df = df[df['Archetype'] == selected_type].copy()
    
    map_df = map_df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
    map_df = map_df.dropna(subset=['lat', 'lon'])
    
    if not map_df.empty:
        st.map(map_df)
    else:
        st.warning("No GPS coordinates found for this selection.")


st.write("---")
st.subheader("🤖 Ask the Investment Assistant")
user_input = st.text_input("Example: What is the best submarket to rent a Luxury High-Rise, and what are the top properties there?")

if user_input:
    with st.spinner("Thinking..."):
        prompt = f"""
        You are an expert Real Estate Investment Analyst. Use the following data summary to answer the user's question.
        
        DATA CONTEXT:
        {data_summary}
        
        USER QUESTION:
        {user_input}
        
        RESPONSE GUIDELINE:
        - Be concise, professional, and highly specific.
        - If asked for recommendations, you MUST rank the top Submarkets (districts) and list the SPECIFIC property names provided in the data.
        - Do not give generic advice. Give data-driven answers naming actual buildings and locations.
        - Do not hallucinate names or numbers.
        """
        
        try:
            response = ollama.chat(model='llama3', messages=[
                {'role': 'user', 'content': prompt},
            ])
            
            st.markdown("### Assistant Response:")
            st.write(response['message']['content'])
        except Exception as e:
            st.error("Error connecting to AI. Make sure Ollama is running.")
