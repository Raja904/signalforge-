import streamlit as st
import pandas as pd
from db.database import get_history
import urllib.parse
import streamlit.components.v1 as components

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
        
        # Gmail Draft Link
        subject_encoded = urllib.parse.quote(row['email_subject'])
        body_encoded = urllib.parse.quote(row['email_body'])
        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&tf=1&su={subject_encoded}&body={body_encoded}"
        st.link_button("📧 Draft in Gmail", gmail_url)
        
        st.markdown("### LinkedIn Message")
        st.text_area("LinkedIn Draft", value=row['linkedin_draft'], height=200, disabled=True)
        
        # Copy to Clipboard and Open LinkedIn hack
        li_encoded = row['linkedin_draft'].replace("'", "\\'").replace("\n", "\\n")
        copy_open_html = f"""
            <button style="
                width: 100%;
                background-color: #0e1117;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 0.5rem;
                border-radius: 0.5rem;
                cursor: pointer;
                font-family: inherit;
                font-size: 1rem;
                margin-top: 10px;
            " onclick="navigator.clipboard.writeText('{li_encoded}').then(() => {{
                window.open('https://www.linkedin.com/messaging/', '_blank');
            }})">
                💬 Copy & Open LinkedIn
            </button>
        """
        components.html(copy_open_html, height=70)
