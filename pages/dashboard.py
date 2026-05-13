import streamlit as st
import pandas as pd
from db.database import get_history

st.set_page_config(page_title="SignalForge Dashboard", layout="wide")

st.title("📊 SignalForge Insights Dashboard")
st.markdown("Track your research history and outreach quality.")

history = get_history()

if not history:
    st.info("No outreach runs yet. Start by generating one on the home page!")
else:
    df = pd.DataFrame(history)
    
    # Rename columns for display
    display_df = df[['created_at', 'prospect_name', 'company_name', 'role', 'hook', 'quality_score', 'status']]
    display_df.columns = ['Date', 'Prospect', 'Company', 'Role', 'Hook', 'Quality Score', 'Status']
    
    st.dataframe(display_df, use_container_width=True)
    
    st.divider()
    
    selected_prospect = st.selectbox("Select a prospect to view full details", options=df['prospect_name'].tolist())
    
    if selected_prospect:
        row = df[df['prospect_name'] == selected_prospect].iloc[0]
        st.subheader(f"Details for {row['prospect_name']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Company:** {row['company_name']}")
            st.markdown(f"**Role:** {row['role']}")
            st.markdown(f"**Date:** {row['created_at']}")
            st.markdown(f"**Quality Score:** {row['quality_score']}/10")
            
        with col2:
            st.markdown(f"**Selected Hook:** {row['hook']}")
            
        st.markdown("### Final Email Draft")
        st.markdown(f"**Subject:** {row['email_subject']}")
        st.text_area("Email Body", value=row['email_body'], height=400, disabled=True)
        
        st.markdown("### LinkedIn Message")
        st.text_area("LinkedIn Draft", value=row['linkedin_draft'], height=200, disabled=True)
