"""
Life Guide AI - Enhanced with Scripture-Based Backgrounds
Features:
- Session-based data retention (no login required)
- In-app notifications and reminders
- Custom background image support (local files OR scripture-based)
- Automatic backgrounds based on user's faith
- User journey tracking and history
- Personalized guidance from Gemini AI
"""

import streamlit as st
import google.generativeai as genai
from datetime import datetime
import time
import os
from pathlib import Path
import requests
import base64
from io import BytesIO

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="The AI Life Guide",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AI CONFIG ---
genai.configure(api_key=st.secrets["AI_API_KEY"])

# --- FAITH TO BACKGROUND IMAGE MAPPING ---
# These are free-to-use images from Unsplash and Pexels
FAITH_BACKGROUNDS = {
    "Hinduism": {
        "url": "https://images.unsplash.com/photo-1599092027257-28b80e0d9a6b?auto=format&fit=crop&w=1200&q=80",
        "description": "🕉️ Sacred Mandala & Spiritual Patterns"
    },
    "Christianity": {
        "url": "https://images.unsplash.com/photo-1559327615-cd4628902d4a?auto=format&fit=crop&w=1200&q=80",
        "description": "✝️ Light & Serenity"
    },
    "Islam": {
        "url": "https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?auto=format&fit=crop&w=1200&q=80",
        "description": "☪️ Islamic Geometric Patterns"
    },
    "Buddhism": {
        "url": "https://images.unsplash.com/photo-1465101162946-4377e57745c3?auto=format&fit=crop&w=1200&q=80",
        "description": "☸️ Peaceful Zen Garden"
    },
    "Judaism": {
        "url": "https://images.unsplash.com/photo-1606148162298-69e1f7a47c0c?auto=format&fit=crop&w=1200&q=80",
        "description": "✡️ Star of David & Heritage"
    },
    "Sikhism": {
        "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
        "description": "☬ Golden Temple Inspired"
    },
    "Spiritualism": {
        "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
        "description": "✨ Cosmic & Spiritual Energy"
    },
    "Taoism": {
        "url": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=1200&q=80",
        "description": "☯️ Yin-Yang Balance"
    },
    "Atheism": {
        "url": "https://images.unsplash.com/photo-1519904981063-b0cf448d479e?auto=format&fit=crop&w=1200&q=80",
        "description": "🌌 Universe & Nature"
    },
}

# --- SESSION STATE INITIALIZATION ---
if "user_data" not in st.session_state:
    st.session_state.user_data = []

if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {
        "faith": "",
        "favorite_path": "Find Help"
    }

if "reminder_triggered" not in st.session_state:
    st.session_state.reminder_triggered = False

if "notification_counter" not in st.session_state:
    st.session_state.notification_counter = 0

if "background_image" not in st.session_state:
    st.session_state.background_image = None

if "custom_bg_path" not in st.session_state:
    st.session_state.custom_bg_path = None

if "current_bg_type" not in st.session_state:
    st.session_state.current_bg_type = "default"

# --- BACKGROUND IMAGE SETUP FROM LOCAL ---
def set_background_from_file(image_path):
    """Set background from local file"""
    try:
        with open(image_path, "rb") as image_file:
            data = base64.b64encode(image_file.read()).decode()
            
        file_ext = Path(image_path).suffix.lower()
        if file_ext in ['.jpg', '.jpeg']:
            mime_type = "image/jpeg"
        elif file_ext == '.png':
            mime_type = "image/png"
        elif file_ext == '.gif':
            mime_type = "image/gif"
        else:
            mime_type = "image/jpeg"
        
        css = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:{mime_type};base64,{data}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        [data-testid="stAppViewContainer"]::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: -1;
            pointer-events: none;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
        st.session_state.current_bg_type = "custom"
        return True
    except Exception as e:
        st.warning(f"Error loading background: {str(e)}")
        return False

# --- BACKGROUND IMAGE SETUP FROM URL (Scripture-based) ---
def set_background_from_url(image_url, faith_name="Unknown"):
    """Set background from URL (scripture/faith based)"""
    try:
        with st.spinner(f"🌟 Loading {faith_name} scripture background..."):
            response = requests.get(image_url, timeout=10)
            
        if response.status_code == 200:
            data = base64.b64encode(response.content).decode()
            mime_type = response.headers.get('content-type', 'image/jpeg')
            
            css = f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:{mime_type};base64,{data}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            
            [data-testid="stAppViewContainer"]::before {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: -1;
                pointer-events: none;
            }}
            </style>
            """
            st.markdown(css, unsafe_allow_html=True)
            st.session_state.current_bg_type = "faith"
            return True
        else:
            st.warning("Failed to load background image from URL")
            return False
            
    except Exception as e:
        st.warning(f"Error loading background: {str(e)}")
        return False

# --- MAIN STYLING ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
}

h1 {
    text-align: center;
    color: #FFD700;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
    font-family: 'Georgia', serif;
    font-size: 3em;
    margin-bottom: 0px;
}

h2 {
    color: #FFD700;
    text-shadow: 2px 2px 6px rgba(0,0,0,0.5);
    font-family: 'Georgia', serif;
}

h3, h4 {
    color: #FFE680;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.5);
}

h4.subtitle {
    text-align: center;
    opacity: 0.9;
    margin-top: -15px;
    font-style: italic;
    color: #E6E6FA;
}

p, label, span, div {
    color: #F0F0F0 !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}

textarea, input[type="text"], input[type="time"], select {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border: 2px solid rgba(255, 215, 0, 0.4) !important;
    border-radius: 10px !important;
    padding: 12px !important;
    color: #F0F0F0 !important;
    font-size: 1em !important;
}

textarea:focus, input:focus, select:focus {
    border-color: rgba(255, 215, 0, 0.8) !important;
    background-color: rgba(255, 255, 255, 0.15) !important;
}

button[kind="primary"] {
    background: linear-gradient(90deg, #ffb400, #ffdd55) !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.6) !important;
    padding: 12px 24px !important;
    font-size: 1em !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(90deg, #ffd966, #ffe699) !important;
    box-shadow: 0 0 20px rgba(255, 255, 0, 0.8) !important;
    transform: scale(1.02);
}

[data-testid="stSidebar"] {
    background-color: rgba(0, 0, 0, 0.6) !important;
    backdrop-filter: blur(5px);
}

[data-testid="stExpander"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 215, 0, 0.2) !important;
    border-radius: 8px !important;
}

hr {
    border-color: rgba(255, 215, 0, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# --- NOTIFICATION FUNCTION ---
def show_notification(message, notification_type="info", emoji="ℹ️"):
    """Show in-app notification"""
    st.session_state.notification_counter += 1
    if notification_type == "success":
        st.toast(f"✨ {message}", icon="🎉")
    elif notification_type == "warning":
        st.toast(f"⚠️ {message}", icon="⚠️")
    elif notification_type == "error":
        st.toast(f"❌ {message}", icon="❌")
    else:
        st.toast(f"{emoji} {message}", icon="ℹ️")

# --- REMINDER FUNCTION ---
def check_and_show_reminder():
    """Check if it's time for a reminder"""
    current_hour = datetime.now().hour
    
    reminder_messages = [
        "🌙 Remember, seeking guidance is a sign of strength.",
        "✨ Take a moment to reflect on your spiritual journey.",
        "🕊️ Peace begins within. Breathe deeply and be present.",
        "💭 Your thoughts are valid. Consider sharing them with your guide.",
        "🙏 May wisdom and compassion guide your path today.",
    ]
    
    reminder_hours = [9, 12, 15, 18, 21]
    
    if current_hour in reminder_hours and not st.session_state.reminder_triggered:
        import random
        message = random.choice(reminder_messages)
        st.balloons()
        st.info(f"🔔 **Daily Reminder:** {message}")
        st.session_state.reminder_triggered = True
    elif current_hour not in reminder_hours:
        st.session_state.reminder_triggered = False

# --- BACKGROUND CUSTOMIZATION SIDEBAR ---
def show_background_settings():
    """Show background customization in sidebar with scripture option"""
    st.sidebar.subheader("🎨 Customize Background")
    
    bg_option = st.sidebar.radio(
        "Choose background:",
        ["Default (Dark)", "Scripture Theme", "Upload Image", "Local File Path"]
    )
    
    if bg_option == "Scripture Theme":
        st.sidebar.write("**🕉️ Select Your Faith:**")
        
        faith_list = list(FAITH_BACKGROUNDS.keys())
        selected_faith = st.sidebar.selectbox(
            "Choose a faith:",
            faith_list,
            index=0
        )
        
        faith_info = FAITH_BACKGROUNDS[selected_faith]
        st.sidebar.write(f"_{faith_info['description']}_")
        
        if st.sidebar.button("📿 Apply Scripture Background", use_container_width=True):
            bg_url = faith_info['url']
            if set_background_from_url(bg_url, selected_faith):
                show_notification(f"Scripture background applied!", "success", "📿")
                st.session_state.user_preferences["faith"] = selected_faith
            else:
                show_notification("Failed to load scripture background", "error", "❌")
    
    elif bg_option == "Upload Image":
        uploaded_file = st.sidebar.file_uploader(
            "Choose an image file",
            type=["jpg", "jpeg", "png", "gif"]
        )
        if uploaded_file is not None:
            temp_path = f"temp_bg_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.custom_bg_path = temp_path
            if set_background_from_file(temp_path):
                show_notification("Background updated!", "success", "🎨")
            else:
                st.session_state.custom_bg_path = None
    
    elif bg_option == "Local File Path":
        local_path = st.sidebar.text_input(
            "Enter image file path:",
            placeholder="e.g., /home/user/Downloads/background.jpg"
        )
        
        if local_path and st.sidebar.button("Load Local Image"):
            if os.path.exists(local_path):
                st.session_state.custom_bg_path = local_path
                if set_background_from_file(local_path):
                    show_notification("Background loaded successfully!", "success", "🎨")
            else:
                st.warning(f"File not found: {local_path}")
                st.session_state.custom_bg_path = None
    
    else:
        st.session_state.custom_bg_path = None
        st.session_state.current_bg_type = "default"
        st.sidebar.caption("Dark theme - Default appearance")

# --- HISTORY DISPLAY ---
def show_user_history():
    """Display user journey history in sidebar"""
    st.sidebar.subheader("📖 Your Journey")
    
    if st.session_state.user_data:
        st.sidebar.write(f"**Total Sessions:** {len(st.session_state.user_data)}")
        st.sidebar.divider()
        
        for idx, entry in enumerate(reversed(st.session_state.user_data), 1):
            with st.sidebar.expander(
                f"📝 {entry['path']} - {entry['timestamp'][:10]}"
            ):
                st.write(f"**Faith:** {entry['faith']}")
                st.write(f"**Path:** {entry['path']}")
                st.write(f"**Your Concern:**")
                st.write(f"_{entry['trouble'][:150]}..._")
                st.divider()
                st.write(f"**Guidance Received:**")
                st.write(entry['response'][:300] + "...")
                st.caption(f"_Received at: {entry['timestamp']}_")
    else:
        st.sidebar.info("Your spiritual journey begins now... 🌱")

# --- PREFERENCES SIDEBAR ---
def show_preferences():
    """Show user preferences in sidebar"""
    st.sidebar.subheader("⚙️ Preferences")
    
    st.session_state.user_preferences["faith"] = st.sidebar.text_input(
        "🕊️ Your Faith/Philosophy:",
        value=st.session_state.user_preferences["faith"],
        placeholder="e.g., Hinduism, Buddhism, etc."
    )
    
    st.session_state.user_preferences["favorite_path"] = st.sidebar.selectbox(
        "🪶 Favorite Path:",
        ["Find Help", "Seek Purpose", "Reflect Within", "Discover Peace"],
        index=0
    )
    
    if st.sidebar.checkbox("Remember my preferences", value=True):
        show_notification("Preferences saved for this session!", "info", "💾")

# --- REMINDERS SETTINGS ---
def show_reminder_settings():
    """Show reminder settings in sidebar"""
    st.sidebar.subheader("🔔 Reminders & Notifications")
    
    enable_reminders = st.sidebar.checkbox(
        "Enable session reminders",
        value=True
    )
    
    if enable_reminders:
        reminder_frequency = st.sidebar.selectbox(
            "Reminder frequency:",
            ["Every 3 hours", "Every 6 hours", "Daily at noon", "Custom"]
        )
        
        if reminder_frequency == "Custom":
            st.sidebar.write("_Reminders will show at: 9 AM, 12 PM, 3 PM, 6 PM, 9 PM_")
    
    if st.session_state.notification_counter > 0:
        st.sidebar.caption(
            f"📬 Notifications shown: {st.session_state.notification_counter}"
        )

# --- MAIN APP ---
def main():
    st.markdown("<h1>🌙 Life Guide AI</h1>", unsafe_allow_html=True)
    st.markdown(
        "<h4 class='subtitle'>By TejasWasan08 | Your Spiritual Companion</h4>",
        unsafe_allow_html=True
    )
    
    check_and_show_reminder()
    
    with st.sidebar:
        show_background_settings()
        st.divider()
        show_preferences()
        st.divider()
        show_reminder_settings()
        st.divider()
        show_user_history()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.write("### 🙏 Share Your Spiritual Journey")
        
        faith = st.text_input(
            "🕊️ Your Faith or Philosophy:",
            value=st.session_state.user_preferences.get("faith", ""),
            placeholder="e.g., Hinduism, Buddhism, Christianity, Islam, etc.",
            key="faith_input"
        )
        
        path = st.selectbox(
            "🪶 Choose your path:",
            ["Find Help", "Seek Purpose", "Reflect Within", "Discover Peace"],
            index=0,
            key="path_input"
        )
        
        trouble = st.text_area(
            "💭 Speak your heart, traveler:",
            placeholder="What troubles your spirit? Share your concerns, questions, or what you seek...",
            height=150,
            key="trouble_input"
        )
        
        save_prefs = st.checkbox("Remember my faith preference", value=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            seek_guidance = st.button(
                "🔮 Seek Guidance",
                use_container_width=True,
                key="seek_btn"
            )
        
        with col_btn2:
            auto_bg = st.button(
                "🕉️ Scripture BG",
                use_container_width=True,
                key="auto_bg_btn",
                help="Auto-apply background based on your faith"
            )
        
        with col_btn3:
            clear_form = st.button(
                "🗑️ Clear",
                use_container_width=True,
                key="clear_btn"
            )
        
        if auto_bg and faith:
            for faith_key in FAITH_BACKGROUNDS.keys():
                if faith.lower() in faith_key.lower() or faith_key.lower() in faith.lower():
                    bg_url = FAITH_BACKGROUNDS[faith_key]['url']
                    if set_background_from_url(bg_url, faith_key):
                        show_notification(f"Scripture background applied for {faith_key}!", "success", "📿")
                    break
            else:
                st.info(f"💡 Available faiths: {', '.join(FAITH_BACKGROUNDS.keys())}")
        
        if clear_form:
            st.session_state.faith_input = ""
            st.session_state.trouble_input = ""
            show_notification("Form cleared!", "info", "✨")
            st.rerun()
        
        if seek_guidance:
            if not faith or not trouble:
                show_notification(
                    "Please fill in all fields to receive guidance",
                    "warning",
                    "⚠️"
                )
                st.warning("🕊️ Please share your faith and your concern to receive personalized guidance.")
            else:
                if save_prefs:
                    st.session_state.user_preferences["faith"] = faith
                
                model = genai.GenerativeModel("gemini-2.5-flash")
                prompt = f"""You are a wise, compassionate spiritual AI guide rooted in the {faith} tradition. 
The seeker comes to you to {path.lower()}. They share: {trouble}

Provide deeply thoughtful, poetic, and comforting spiritual guidance that:
- Acknowledges their concern with empathy
- lighter language for the user to understand (write as if someone is helping you out on text messages) (you can use casual language)
- can use hinglish too
- Draws on wisdom from {faith} teachings if relevant
- Offers practical spiritual perspective and advice
- Is warm, non-judgmental, and uplifting
- Uses a calm, reflective tone
- Helps them see their situation with clarity and hope
- Try to correlate the problem with their life and provide a solution from {faith} scripture


Keep the response to 3-4 paragraphs."""
                
                try:
                    with st.spinner("🌟 Seeking divine wisdom..."):
                        response = model.generate_content(prompt)
                        ai_response = response.text
                    
                    st.divider()
                    st.markdown("### ✨ Divine Whisper")
                    st.markdown(
                        f"""
                        <div style="
                            background-color: rgba(255, 215, 0, 0.1);
                            border-left: 4px solid #FFD700;
                            padding: 20px;
                            border-radius: 8px;
                            color: #F0F0F0;
                            font-style: italic;
                        ">
                        {ai_response}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.divider()
                    
                    st.session_state.user_data.append({
                        "faith": faith,
                        "path": path,
                        "trouble": trouble,
                        "response": ai_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    show_notification("Guidance received and saved!", "success", "✨")
                    time.sleep(0.5)
                    st.balloons()
                    
                except Exception as e:
                    show_notification(
                        f"Connection error: {str(e)[:50]}",
                        "error",
                        "❌"
                    )
                    st.error(f"The spirits are troubled: {str(e)}")
    
    st.divider()
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f2:
        st.caption(
            f"🌍 Session active | 📊 Queries: {len(st.session_state.user_data)} | "
            f"Background: {st.session_state.current_bg_type}"
        )

if __name__ == "__main__":
    main()
