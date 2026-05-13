import streamlit as st
import time
from workflow.graph import create_graph
from db.database import save_run, save_signals, save_draft, update_run_status, get_settings, update_settings
import os
from dotenv import load_dotenv
import urllib.parse
import streamlit.components.v1 as components

load_dotenv()

st.set_page_config(page_title="SignalForge AI", layout="wide")

# Custom CSS to reduce sidebar padding
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {padding-top: 1.5rem !important;}
        [data-testid="stSidebar"] .block-container {padding-top: 0.5rem !important; padding-bottom: 0rem !important;}
        div[data-testid="stVerticalBlock"] > div:has(div.stImage) {margin-top: -1rem !important; margin-bottom: -1rem !important;}
    </style>
""", unsafe_allow_html=True)

st.title("🚀 SignalForge AI")
st.markdown("### AI-Powered B2B Outreach")
st.markdown("Generate high-converting outreach drafts based on real-time web research.")

# Load persistent settings
if 'saved_settings' not in st.session_state:
    st.session_state.saved_settings = get_settings()

# Sidebar for Product Configuration
with st.sidebar:
    st.header("SignalForge Settings")
    
    # High-quality Centered Logo (Medium Size + Balanced Padding)
    logo_path = os.path.join(os.getcwd(), "logo_white.png")
    if os.path.exists(logo_path):
        c1, c2, c3 = st.columns([0.8, 3.4, 0.8])
        with c2:
            st.image(logo_path, use_container_width=True)
    
    product_desc = st.text_area(
        "What are you selling?",
        value=st.session_state.saved_settings.get('product_description', ""),
        help="Describe your product. SignalForge will use this to frame the pitch.",
        height=200
    )
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        your_name = st.text_input("Your Name", value=st.session_state.saved_settings.get('sender_name', ""))
    with col_s2:
        your_role = st.text_input("Your Role", value=st.session_state.saved_settings.get('sender_role', ""))
    
    your_company = st.text_input("Your Company", value=st.session_state.saved_settings.get('sender_company', ""))
        
    if st.button("💾 Save Profile & Product", use_container_width=True):
        new_settings = {
            'product_description': product_desc,
            'sender_name': your_name,
            'sender_role': your_role,
            'sender_company': your_company
        }
        update_settings(new_settings)
        st.session_state.saved_settings = new_settings
        st.session_state.settings_updated_at = time.time()
        st.rerun()

    # Show success message for 5 seconds
    if 'settings_updated_at' in st.session_state:
        elapsed = time.time() - st.session_state.settings_updated_at
        if elapsed < 5:
            st.success("Profile saved.")
            # This will trigger a rerun once the time is up
            time.sleep(0.1) 
            st.rerun()
        else:
            del st.session_state.settings_updated_at
            st.rerun()

# Main Input Form
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Prospect Details")
    with st.form("outreach_form"):
        name = st.text_input("Prospect Name", placeholder="e.g. Alex Chen")
        company = st.text_input("Company Name", placeholder="e.g. Acme Corp")
        role = st.text_input("Role", placeholder="e.g. VP Finance")
        
        submitted = st.form_submit_button("Generate Research & Draft")

if submitted:
    if not name or not company:
        st.error("Please provide at least Name and Company.")
    else:
        # Initialize Run in DB
        run_id = save_run(name, company, role, product_desc)
        
        # Display Progress
        progress_area = st.empty()
        log_area = st.empty()
        
        with st.status("Agent is working...", expanded=True) as status:
            log_placeholder = st.empty()
            all_logs = []
            
            # Setup LangGraph
            app = create_graph()
            
            initial_state = {
                "prospect_name": name,
                "company_name": company,
                "role": role,
                "product_description": product_desc,
                "sender_name": your_name,
                "sender_role": your_role,
                "sender_company": your_company,
                "signals": [],
                "logs": [],
                "is_ghost": False,
                "is_stale": False,
                "is_ambiguous": False
            }
            
            # Execute Workflow via Streaming
            final_state = initial_state
            for output in app.stream(initial_state):
                # output is a dict like {'node_name': {state_updates}}
                for node_name, state_update in output.items():
                    if "logs" in state_update:
                        for log in state_update["logs"]:
                            all_logs.append(log)
                            st.write(log)
                            time.sleep(0.5) # Dramatic pause for "Real-Time" effect
                    # Merge state
                    for key, value in state_update.items():
                        if key == "logs":
                            final_state["logs"].extend(value)
                        else:
                            final_state[key] = value
            
            status.update(label="Research & Drafting Complete!", state="complete", expanded=False)
            
            # Save Results to DB
            save_signals(run_id, final_state['signals'])
            save_draft(
                run_id, 
                final_state['selected_hook'],
                final_state['email_subject'],
                final_state['email_body'],
                final_state['linkedin_draft'],
                final_state['quality_score']
            )
            update_run_status(run_id, "Completed")
            
            # Display Results in col2
            with col2:
                st.success("Draft Generated!")
                
                # Warnings/Edge Cases
                if final_state['is_ghost']:
                    st.warning("👻 Ghost Prospect: No recent news found. Using role-based hook.")
                if final_state['is_stale']:
                    st.warning("📅 Stale Data: News is quite old. Double-check before sending.")
                if final_state['is_ambiguous']:
                    st.warning("❓ Ambiguous Company: Multiple entities found. Verify company details.")
                
                tabs = st.tabs(["📧 Email Draft", "💬 LinkedIn Message", "🔍 Research Signal"])
                
                with tabs[0]:
                    st.markdown(f"**Subject:** {final_state['email_subject']}")
                    edited_body = st.text_area("Body", value=final_state['email_body'], height=450)
                    
                    # Gmail Draft Link
                    subject_encoded = urllib.parse.quote(final_state['email_subject'])
                    body_encoded = urllib.parse.quote(edited_body)
                    gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&tf=1&su={subject_encoded}&body={body_encoded}"
                    
                    st.link_button("📧 Draft in Gmail", gmail_url, use_container_width=True)
                    st.button("Save Edits")
                
                with tabs[1]:
                    edited_li = st.text_area("LinkedIn Draft", value=final_state['linkedin_draft'], height=250)
                    
                    # Copy to Clipboard and Open LinkedIn hack
                    li_encoded = edited_li.replace("'", "\\'").replace("\n", "\\n")
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
                
                with tabs[2]:
                    st.markdown(f"**Hook Used:** {final_state['selected_hook']}")
                    st.markdown(f"**Reasoning:** {final_state['hook_reasoning']}")
                    st.markdown("---")
                    for s in final_state['signals'][:5]:
                        st.markdown(f"- [{s['title']}]({s['link']})\n  *{s['snippet']}*")

        # Show Logs
        with st.expander("View Agent Execution Logs"):
            for log in final_state['logs']:
                st.text(f"➜ {log}")
