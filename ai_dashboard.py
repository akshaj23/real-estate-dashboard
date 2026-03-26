import streamlit as st
import pandas as pd
from groq import Groq

# ==========================================
# 0. INITIALIZE SESSION STATE (MEMORY)
# ==========================================
if 'archetype_target' not in st.session_state:
    st.session_state.archetype_target = "All Properties"
if 'map_target' not in st.session_state:
    st.session_state.map_target = "📍 Show all buildings in this cluster"

if 'last_response' not in st.session_state:
    st.session_state.last_response = ""
if 'mentioned_props' not in st.session_state:
    st.session_state.mentioned_props = []

def jump_to_location(map_label):
    st.session_state.archetype_target = "All Properties"
    st.session_state.map_target = map_label

# ==========================================
# 1. LOAD DATA & PREP CONTEXT
# ==========================================
df = pd.read_csv("leaseup_dashboard_data.csv")

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

Performance by Archetype:
{archetype_txt}

Top 5 Highest Yielding Submarkets (Districts):
{submarket_txt}

Top Recommended Properties by Archetype and Submarket:
{top_props_txt}
"""

# ==========================================
# 2. DASHBOARD UI & SIDEBAR
# ==========================================
st.set_page_config(page_title="Investment AI Assistant", layout="wide")
st.title("🏙️ Real Estate Investment Dashboard")

with st.sidebar:
    st.header("Market Stats")
    st.dataframe(df.groupby('Archetype')['LeaseUpTime'].mean())
    st.write("---")
    st.write("Data processed and ready for NLP analysis.")
    
    # FALLBACK LOGIC: Works on Cloud AND Local Mac!
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        st.warning("Local Mode: Cloud Vault not found.")
        api_key = st.text_input("Paste Groq API Key to test locally:", type="password")

# ==========================================
# 3. GEOTAG BOARD (Interactive Map Explorer)
# ==========================================
st.subheader("📍 Geotag Board: Locality Explorer")
st.write("Filter by investment strategy and jump directly to specific properties on the map.")

filter_col, jump_col, map_col = st.columns([1, 1, 3])
df_coords = df.dropna(subset=['Latitude', 'Longitude', 'Name']).copy()
df_coords['MapLabel'] = df_coords['Name'] + " (" + df_coords['Submarket'] + ")"

with filter_col:
    options = ["All Properties"] + list(df['Archetype'].dropna().unique())
    st.radio("Step 1: Filter by Strategy:", options, key="archetype_target")

if st.session_state.archetype_target == "All Properties":
    type_filtered_df = df_coords.copy()
else:
    type_filtered_df = df_coords[df_coords['Archetype'] == st.session_state.archetype_target].copy()

with jump_col:
    jump_options = ["📍 Show all buildings in this cluster"] + sorted(type_filtered_df['MapLabel'].tolist())
    
    if st.session_state.map_target not in jump_options:
        st.session_state.map_target = "📍 Show all buildings in this cluster"
        
    st.selectbox("Step 2: Select a building:", jump_options, key="map_target")

with map_col:
    if st.session_state.map_target == "📍 Show all buildings in this cluster":
        map_df = type_filtered_df.copy()
    else:
        map_df = type_filtered_df[type_filtered_df['MapLabel'] == st.session_state.map_target].copy()
    
    map_df = map_df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
    if not map_df.empty:
        map_df = map_df[['lat', 'lon']]
        st.map(map_df)
    else:
        st.warning("No GPS coordinates found for this selection.")

# ==========================================
# 4. AI CHAT INTERFACE
# ==========================================
st.subheader("🤖 Ask the Investment Assistant")

with st.form(key="chat_form"):
    user_input = st.text_input("Example: What is the best submarket to rent a Luxury High-Rise, and what are the top properties there?")
    submit_btn = st.form_submit_button("Ask Assistant")

if submit_btn and user_input:
    if not api_key:
        st.error("Please provide an API key in the sidebar to use the AI.")
    else:
        with st.spinner("Analyzing market data..."):
            prompt = f"""
            You are an expert Real Estate Investment Analyst. Use the following data summary to answer the user's question.
            
            DATA CONTEXT:
            {data_summary}
            
            USER QUESTION:
            {user_input}
            
            RESPONSE GUIDELINE:
            - Be concise, professional, and highly specific.
            - If asked for recommendations, rank the top Submarkets and list the SPECIFIC property names.
            - Do not hallucinate.
            """
            
            try:
                # Connected to the updated model
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.session_state.last_response = response.choices[0].message.content
                
                # Scan for properties
                mentioned = []
                for label in df_coords['MapLabel'].unique():
                    name_only = label.split(" (")[0] 
                    if name_only in st.session_state.last_response:
                        mentioned.append(label)
                st.session_state.mentioned_props = mentioned
                
            except Exception as e:
                st.error(f"API Error: {e}")

if st.session_state.last_response:
    st.markdown("### Assistant Response:")
    st.write(st.session_state.last_response)
    
    if st.session_state.mentioned_props:
        st.write("---")
        st.write("**📍 Jump to mentioned properties on the map:**")
        
        btn_cols = st.columns(min(len(st.session_state.mentioned_props), 4)) 
        for i, label in enumerate(st.session_state.mentioned_props):
            name_only = label.split(" (")[0]
            with btn_cols[i % len(btn_cols)]:
                st.button(f"🗺️ View {name_only}", on_click=jump_to_location, args=(label,), key=f"btn_{i}")
