import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# --- FILE PATHS & SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATHS = {
    'users': os.path.join(BASE_DIR, 'users.csv'),
    'carbon_entries': os.path.join(BASE_DIR, 'carbon_entries.csv'),
    'points_history': os.path.join(BASE_DIR, 'points_history.csv'),
    'feedback': os.path.join(BASE_DIR, 'feedback.csv'),
    'trash_log': os.path.join(BASE_DIR, 'trash_log.csv'),
    'estate_data': os.path.join(BASE_DIR, 'estate_data.csv'), 
}

# --- CUSTOM CSS INJECTION (Dark & Vibrant Theme) ---
st.markdown( 
    """
    <style>
    /* Global Background: Dark */
    .stApp {
        background-color: #121212; /* Very dark gray for AMOLED/OLED effect */
        color: #FFFFFF;
    }
    
    /* Global Font: Elegant Serif */
    * {
        font-family: 'Times New Roman', Times, serif !important; 
        color: #FFFFFF; /* Default white text for readability */
    }
    
    /* Headers (h1, h2, h3) */
    h1, h2, h3, h4, h5, h6, .css-1dp5vir, .st-emotion-cache-1dp5vir {
        color: #B2FF59 !important; /* Bright Lime Green for headers */
    }

    /* --- LOGIN PAGE STYLING --- */
    
    /* Sidebar Removal on Login View */
    .st-emotion-cache-18ni7ap { 
        visibility: hidden;
        width: 0;
    }
    
    /* Login Card/Container Background */
    .st-emotion-cache-z5ig0e { 
        background-color: #1F1F1F; /* Slightly lighter dark gray for the card */
        border-radius: 12px;
        box-shadow: 0 0 15px rgba(178, 255, 89, 0.4); /* Neon glow effect */
    }

    /* Input Fields (Text Input/Select Box containers) */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #2C2C2C !important; /* Medium dark gray background */
        border: 1px solid #00E676; /* Bright Green border */
        border-radius: 4px;
    }

    /* Input Text Color */
    div[data-baseweb="input"] input, 
    .st-ag, .st-ah, .st-ai, .st-aj, .st-al, .st-am { 
        color: #FFFFFF !important; /* White text in inputs */
        font-weight: bold;
    }
    
    /* --- GENERAL APP STYLES (Buttons & Sidebar) --- */

    /* Sidebar Background (Standard dark Streamlit style) */
    [data-testid="stSidebar"] {
        background-color: #0D0D0D !important;
    }
    
    /* Primary Button Style (Used for major actions like Login/Submit) */
    div.stButton > button {
        background-color: #00C853 !important; /* Deep vibrant green */
        color: #000000 !important; /* Black text on bright button */
        font-weight: bold;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #00E676 !important; /* Brighter green on hover */
        color: #000000 !important; 
    }

    /* Secondary Button Style (Used for Game Quests/Register) */
    div.stButton button[kind="secondary"] {
        background-color: #4A4A4A !important; /* Medium Gray */
        color: #B2FF59 !important; /* Bright Lime Text */
        border: 1px solid #B2FF59 !important;
    }

    div.stButton button[kind="secondary"]:hover {
        background-color: #666666 !important;
        color: #FFFFFF !important;
    }
    
    /* Info/Success/Warning Boxes (Vibrant backgrounds for pop) */
    .stAlert {
        color: #FFFFFF !important;
        background-color: #4A4A4A !important; /* Darker background for alerts */
        border-left: 5px solid #00C853 !important; /* Vibrant indicator bar */
    }
    .stAlert > div { /* Targets the text within the alert box */
        color: #FFFFFF !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --- CRITICAL FALLBACK DATA CREATION ---
def create_mock_csv_if_missing():
    """Creates essential CSV files with headers and mock data if they don't exist."""
    
    if not os.path.exists(FILE_PATHS['users']) or os.path.getsize(FILE_PATHS['users']) == 0:
        mock_users = pd.DataFrame({
            'user_id': [100, 101, 102], 'username': ['EcoUser_A', 'GreenGuru_B', 'Sustainable_C'],
            'hostel_id': [1, 2, 3], 'eco_points': [500, 750, 620],
            'date_joined': [datetime.now().strftime('%Y-%m-%d')] * 3
        })
        mock_users.to_csv(FILE_PATHS['users'], index=False)
    
    if not os.path.exists(FILE_PATHS['estate_data']) or os.path.getsize(FILE_PATHS['estate_data']) == 0:
        mock_estate = pd.DataFrame({
            'total_co2_annual_kg': [9500000.0], 'energy_kwh': [15000000.0], 'year': [datetime.now().year]
        })
        mock_estate.to_csv(FILE_PATHS['estate_data'], index=False)

    if not os.path.exists(FILE_PATHS['carbon_entries']) or os.path.getsize(FILE_PATHS['carbon_entries']) == 0:
         mock_entries = pd.DataFrame({
            'entry_id': [1, 2, 3], 'user_id': [100, 101, 102],
            'date': [(datetime.now() - timedelta(days=d)).strftime('%Y-%m-%d') for d in [21, 14, 7]],
            'num_people': [1] * 3, 'ac_hours': [15, 25, 10], 'water_litres': [400, 500, 350],
            'food_waste_instances': [3, 2, 1], 'bus_rides': [5, 10, 2], 'wastes_meat': [False, True, False],
            'total_cf': [30.5, 45.2, 22.1]
        })
         mock_entries.to_csv(FILE_PATHS['carbon_entries'], index=False)

    for key in ['points_history', 'feedback', 'trash_log']:
        if not os.path.exists(FILE_PATHS[key]) or os.path.getsize(FILE_PATHS[key]) == 0:
            if key == 'points_history': df = pd.DataFrame({'user_id': [], 'date': [], 'points_change': [], 'reason': []})
            elif key == 'feedback': df = pd.DataFrame({'user_id': [], 'date': [], 'comment': []})
            elif key == 'trash_log': df = pd.DataFrame({'user_id': [], 'date': [], 'weight_kg': []})
            df.to_csv(FILE_PATHS[key], index=False)


# --- CORE LOGIC CONSTANTS ---
STUDENT_ACTIVITY_BASE = 35.0 
VITIAN_AVG = {
    'total': STUDENT_ACTIVITY_BASE, 'water_litres': 300, 'bus_rides': 5, 
    'food_waste_instances': 5, 'ac_hours': 20
} 
C_W_FACTOR = 0.003; C_T_FACTOR = 0.1; C_A_FACTOR = 0.5
C_F_MEAT_FACTOR = 1.2; C_F_VEG_FACTOR = 0.5
HOSTEL_MAP = {1: 'Hostel A', 2: 'Hostel B', 3: 'Hostel C', 99: 'Faculty/Staff'}

TIP_DICTIONARY = {
    'water_litres': {'high_impact': "🚿 **Major water usage** detected! Try taking shorter showers (5-7 mins) or use a bucket.", 'medium_impact': "💧 Your water use is above average. Turn off the tap while **brushing your teeth**.", 'excel': "🌊 Excellent job with water conservation! Keep monitoring for any leaks."},
    'bus_rides': {'high_impact': "🚌 High transport impact! For short trips, consider **walking or cycling** instead of the bus.", 'medium_impact': "🚶‍♂️ Above average travel impact. Plan your trips to minimize the number of bus rides you take each week.", 'excel': "🚴 Your transport choices are incredibly eco-friendly! You're a low-carbon commuter."},
    'food_waste_instances': {'high_impact': "🍖🥩 **Excessive food waste!** Especially if it included meat. Only take what you can eat.", 'medium_impact': "🍽️ Noticeable food waste. Start small on your plate; you can always go back for seconds.", 'excel': "🍎 Zero waste hero! You're excellent at managing food and minimizing landfill impact."},
    'ac_hours': {'high_impact': "🌡️ **High AC usage** is costing you points! Use AC only when necessary and try setting the temp higher.", 'medium_impact': "⏱️ Above average AC use. Use a timer and ensure your room is properly sealed (windows/doors).", 'excel': "🍃 Minimal AC usage detected! Keep using natural ventilation or fans where possible."}
}

MOCK_DATA = {
    'globalStats': {'co2ppm': 421.3, 'deforestation': 10.0, 'oceanTemp': 1.2},
    'globalAverage': 33.0,
    'ecoQuotes': ["Every drop saved today is an ocean preserved for tomorrow.", "The Earth does not belong to us. We belong to the Earth.", "Small acts, when multiplied by millions, can transform the world.", "Nature is not a place to visit. It is home."]
}

# --- DYNAMIC AVERAGE CALCULATION ---

def calculate_dynamic_vitan_avg(users_df, estate_df):
    base_avg = STUDENT_ACTIVITY_BASE 
    estate_contribution_weekly = 0.0

    if not estate_df.empty and 'total_co2_annual_kg' in estate_df.columns:
        total_estate_co2 = estate_df['total_co2_annual_kg'].sum()
        num_students = users_df.shape[0] if not users_df.empty else 1000 
        estate_contribution_weekly = (total_estate_co2 / num_students) / 52 
        new_total_avg = base_avg + estate_contribution_weekly
        VITIAN_AVG['total'] = new_total_avg
        st.sidebar.caption(f"Campus CF Added: {estate_contribution_weekly:.2f} kgCO2e/wk")
        return new_total_avg
    else:
        return base_avg


# --- Data Loading and Persistence FIX ---

def standardize_columns(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

@st.cache_resource
def load_data():
    data = {}
    DTYPE_MAPS = {
        'users': {'user_id': int, 'hostel_id': int, 'eco_points': int, 'username': str},
        'carbon_entries': {'entry_id': int, 'user_id': int, 'total_cf': float},
        'points_history': {'user_id': int, 'points_change': int},
        'trash_log': {'user_id': int},
        'estate_data': {'total_co2_annual_kg': float, 'energy_kwh': float},
    }
    
    for key, path in FILE_PATHS.items():
        try:
            df = pd.read_csv(path)
            df = standardize_columns(df)
            
            if key in ['users', 'carbon_entries', 'points_history', 'trash_log'] and 'user_id' not in df.columns:
                potential_id_cols = ['id', 'userid', 'sno', 'serial_number', 'user']
                found_id_col = next((col for col in df.columns if col in potential_id_cols), None)
                if found_id_col: df = df.rename(columns={found_id_col: 'user_id'})
                elif len(df.columns) > 0 and key == 'users': df = df.rename(columns={df.columns[0]: 'user_id'})
            
            if key == 'users' and 'username' not in df.columns:
                potential_name_cols = ['name', 'fullname', 'user_name']
                found_name_col = next((col for col in df.columns if col in potential_name_cols), None)
                if found_name_col: df = df.rename(columns={found_name_col: 'username'})
                elif 'user_id' in df.columns and len(df.columns) > 1:
                    cols_to_check = [col for col in df.columns if col not in ['user_id', 'hostel_id', 'eco_points']]
                    if cols_to_check: df = df.rename(columns={cols_to_check[0]: 'username'})
            
            dtype_map = DTYPE_MAPS.get(key, {})
            valid_dtype_map = {col: dtype for col, dtype in dtype_map.items() if col in df.columns}
            if valid_dtype_map: df = df.astype(valid_dtype_map, errors='ignore')

            data[key] = df
            
            if key == 'users' and ('user_id' not in df.columns or 'username' not in df.columns):
                 st.error(f"Critical error: Could not find 'user_id' OR 'username' in {key}.csv. Please check the file.")
                 data[key] = pd.DataFrame() 

        except Exception as e:
            data[key] = pd.DataFrame()
            
    return data

def save_data(key, df):
    try:
        df.to_csv(FILE_PATHS[key], index=False)
        st.session_state['data'][key] = df
        load_data.clear() 
    except Exception as e:
        st.error(f"Error saving data to {key}.csv: {e}")

# --- Python Implementation of Core Functions (Unchanged) ---

def calculate_footprint(inputs):
    c_f = C_F_MEAT_FACTOR if inputs['wastes_meat'] else C_F_VEG_FACTOR
    total_cf = (C_W_FACTOR * inputs['water_litres']) + \
               (C_T_FACTOR * inputs['bus_rides']) + \
               (c_f * inputs['food_waste_instances']) + \
               (C_A_FACTOR * inputs['ac_hours'])
    return total_cf

def analyze_and_generate_tips(inputs, total_cf):
    category_cf = {
        'water_litres': C_W_FACTOR * inputs['water_litres'], 'bus_rides': C_T_FACTOR * inputs['bus_rides'],
        'food_waste_instances': C_F_MEAT_FACTOR * inputs['food_waste_instances'] if inputs['wastes_meat'] else C_F_VEG_FACTOR * inputs['food_waste_instances'],
        'ac_hours': C_A_FACTOR * inputs['ac_hours']
    }
    
    diffs = {
        'water_litres': inputs['water_litres'] - VITIAN_AVG['water_litres'], 'bus_rides': inputs['bus_rides'] - VITIAN_AVG['bus_rides'],
        'food_waste_instances': inputs['food_waste_instances'] - VITIAN_AVG['food_waste_instances'], 'ac_hours': inputs['ac_hours'] - VITIAN_AVG['ac_hours'],
    }

    results = {'comparison': {}, 'personalized_tips': [], 'excel_tip': "", 'total_cf': total_cf}
    
    if total_cf < VITIAN_AVG['total']: results['comparison']['message'] = f"✅ **BETTER!** Your CF is **{total_cf:.2f}** kgCO2e, below the VITian average of {VITIAN_AVG['total']:.2f}."
    else: results['comparison']['message'] = f"⚠️ **HIGHER!** Your CF is **{total_cf:.2f}** kgCO2e, above the VITIAN average of {VITIAN_AVG['total']:.2f}."

    lowest_impact_ratio = float('inf'); best_category = None
    for category in diffs:
        if diffs[category] > VITIAN_AVG[category] * 0.5: results['personalized_tips'].append(TIP_DICTIONARY[category]['high_impact'])
        elif diffs[category] > 0: results['personalized_tips'].append(TIP_DICTIONARY[category]['medium_impact'])

        ratio = (inputs[category] / VITIAN_AVG[category]) if VITIAN_AVG[category] > 0 else 0
        if ratio < lowest_impact_ratio: lowest_impact_ratio = ratio; best_category = category
    
    if best_category and lowest_impact_ratio < 0.7: results['excel_tip'] = TIP_DICTIONARY[best_category]['excel']
    results['random_tip'] = random.choice(MOCK_DATA['ecoQuotes'])
    
    return results

# --- Session State Initialization (Unchanged) ---

def init_session_state():
    create_mock_csv_if_missing()
    if 'data' not in st.session_state: st.session_state['data'] = load_data()
    if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
    if 'current_view' not in st.session_state: st.session_state['current_view'] = 'Dashboard'
    if 'user_id' not in st.session_state: st.session_state['user_id'] = None
    if 'user_profile' not in st.session_state: st.session_state['user_profile'] = None
    if 'user_inputs' not in st.session_state: st.session_state['user_inputs'] = {'num_people': 1, 'ac_hours': 10, 'water_litres': 500, 'food_waste_instances': 3, 'bus_rides': 5, 'wastes_meat': False}
    if 'analysis_result' not in st.session_state: st.session_state['analysis_result'] = None

# --- Streamlit UI Components ---

def register_new_user(username, hostel_id):
    users_df = st.session_state['data']['users']
    new_user_id = users_df['user_id'].max() + 1 if not users_df.empty and 'user_id' in users_df.columns else 1001
    new_user = pd.DataFrame([{'user_id': new_user_id, 'username': username, 'hostel_id': hostel_id, 'eco_points': 50, 'date_joined': datetime.now().strftime('%Y-%m-%d')}])
    updated_users_df = pd.concat([users_df, new_user], ignore_index=True)
    save_data('users', updated_users_df)
    st.toast(f"Welcome, {username}! Registration successful.", icon='🎉')
    return new_user_id, username, hostel_id

def render_login_page():
    """Renders the stylized login page."""
    
    # Use columns to center the login content
    col_empty, col_main, col_empty2 = st.columns([1, 2, 1])
    
    with col_main:
        st.markdown(f"<h1 style='text-align: center;'>🌱 Green Tracker</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>Track your impact on campus.</p>", unsafe_allow_html=True)
        st.markdown("---")

        users_df = st.session_state['data']['users']
        is_data_ready = not users_df.empty and 'user_id' in users_df.columns and 'username' in users_df.columns
        
        if not is_data_ready:
            st.warning("User data unavailable. Please register a new user below.")
            valid_ids = []
        else:
            valid_ids = users_df['user_id'].tolist()
            
        # --- LOGIN SECTION ---
        with st.container(border=True):
            st.subheader("Existing User Login")
            
            user_id_input = st.selectbox(
                "**Select Existing User ID:**", 
                options=valid_ids if valid_ids else ["No Users Available"],
                disabled=not valid_ids,
                format_func=lambda x: f"ID: {x}"
            )
            
            if st.button("Access Dashboard", use_container_width=True, disabled=not valid_ids, type="primary"):
                user_id = user_id_input
                user_data = users_df[users_df['user_id'] == user_id].iloc[0]
                
                st.session_state['user_id'] = user_id
                st.session_state['user_profile'] = {
                    'id': user_data['user_id'], 'name': user_data['username'], 
                    'hostel_id': user_data['hostel_id'], 
                    'hostel_name': HOSTEL_MAP.get(user_data['hostel_id'], 'Unknown'),
                    'eco_points': user_data['eco_points']
                }
                st.session_state['logged_in'] = True
                st.rerun()

        # --- REGISTRATION SECTION ---
        with st.container(border=True):
            st.subheader("Register New User")
            
            with st.form("registration_form", clear_on_submit=False):
                new_username = st.text_input("Username", max_chars=30)
                
                hostel_options = {name: id for id, name in HOSTEL_MAP.items()}
                selected_hostel_name = st.selectbox(
                    "Hostel/Department:", 
                    options=list(hostel_options.keys()),
                    index=0
                )
                new_hostel_id = hostel_options[selected_hostel_name]
                
                if st.form_submit_button("Register & Login", type="secondary", use_container_width=True):
                    if not new_username:
                        st.error("Please enter a username.")
                    elif 'username' in users_df.columns and users_df['username'].str.lower().eq(new_username.lower()).any():
                        st.error(f"Username '{new_username}' is already taken.")
                    else:
                        new_id, new_name, new_hostel_id = register_new_user(new_username, new_hostel_id)
                        
                        st.session_state['user_id'] = new_id
                        st.session_state['user_profile'] = {
                            'id': new_id, 'name': new_name, 'hostel_id': new_hostel_id, 
                            'hostel_name': HOSTEL_MAP.get(new_hostel_id, 'Unknown'), 'eco_points': 50
                        }
                        st.session_state['logged_in'] = True
                        st.rerun()


def render_sidebar():
    st.sidebar.title("🌱 Green Tracker")
    st.sidebar.metric(
        label="🏆 TOTAL ECO-POINTS", 
        value=st.session_state['user_profile']['eco_points'], 
        delta=f"Hostel: {st.session_state['user_profile']['hostel_name']}"
    )
    
    st.sidebar.divider()

    st.session_state['current_view'] = st.sidebar.radio(
        "Navigation",
        ['Dashboard', 'My History', 'Carbon Quest', 'Leaderboard', 'Global Snapshot'],
        index=['Dashboard', 'My History', 'Carbon Quest', 'Leaderboard', 'Global Snapshot'].index(st.session_state['current_view'])
    )

    st.sidebar.divider()
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.session_state['analysis_result'] = None
        st.rerun()

def render_dashboard():
    user_id = st.session_state['user_id']
    st.header("📋 Your Weekly Impact Submission")
    carbon_entries_df = st.session_state['data']['carbon_entries']
    
    if not carbon_entries_df.empty and 'user_id' in carbon_entries_df.columns:
        last_entry = carbon_entries_df[carbon_entries_df['user_id'] == user_id].sort_values(by='date', ascending=False).head(1)
    else:
        last_entry = pd.DataFrame()
    
    if not last_entry.empty:
        last_date = pd.to_datetime(last_entry.iloc[0]['date']).strftime('%Y-%m-%d')
        st.info(f"Your last entry was **{last_date}** (CF: **{last_entry.iloc[0]['total_cf']:.2f}** kgCO2e). Submit your new weekly data below.")
    else:
        st.info("No previous entries found. Submit your first weekly log!")

    with st.form("impact_form", clear_on_submit=False):
        c1, c2, c3 = st.columns(3)
        with c1: st.session_state['user_inputs']['num_people'] = st.number_input("👥 People in Room", min_value=1, max_value=8, value=st.session_state['user_inputs']['num_people'])
        with c2: st.session_state['user_inputs']['water_litres'] = st.slider("💧 Water Consumed (Litres/week)", min_value=0, max_value=3500, value=st.session_state['user_inputs']['water_litres'])
        with c3: st.session_state['user_inputs']['food_waste_instances'] = st.slider("🍽️ Food Waste (Instances/week)", min_value=0, max_value=20, value=st.session_state['user_inputs']['food_waste_instances'])

        c4, c5, c6 = st.columns(3)
        with c4: st.session_state['user_inputs']['ac_hours'] = st.slider("⚡ AC Usage (Hours/week)", min_value=0, max_value=168, value=st.session_state['user_inputs']['ac_hours'])
        with c5: st.session_state['user_inputs']['bus_rides'] = st.slider("🚌 Bus Rides (Trips/week)", min_value=0, max_value=30, value=st.session_state['user_inputs']['bus_rides'])
        with c6: st.markdown("🥩 **Meat Wasted?**", unsafe_allow_html=True); st.session_state['user_inputs']['wastes_meat'] = st.checkbox("Check if any food waste included meat", value=st.session_state['user_inputs']['wastes_meat'])

        if st.form_submit_button("✨ Submit Data & Get Analysis", use_container_width=True, type="primary"):
            inputs = st.session_state['user_inputs']
            total_cf = calculate_footprint(inputs)
            analysis = analyze_and_generate_tips(inputs, total_cf)
            
            current_entries = st.session_state['data']['carbon_entries']
            new_entry_id = current_entries['entry_id'].max() + 1 if not current_entries.empty and 'entry_id' in current_entries.columns else 1
            new_entry = pd.DataFrame([{'entry_id': new_entry_id, 'user_id': user_id, 'date': datetime.now().strftime('%Y-%m-%d'), 'num_people': inputs['num_people'], 'ac_hours': inputs['ac_hours'], 'water_litres': inputs['water_litres'], 'food_waste_instances': inputs['food_waste_instances'], 'bus_rides': inputs['bus_rides'], 'wastes_meat': inputs['wastes_meat'], 'total_cf': total_cf}])
            save_data('carbon_entries', pd.concat([current_entries, new_entry], ignore_index=True))

            points_gained = 5 + int(max(0, VITIAN_AVG['total'] - total_cf))
            st.session_state['data']['users'].loc[st.session_state['data']['users']['user_id'] == user_id, 'eco_points'] += points_gained
            st.session_state['user_profile']['eco_points'] += points_gained
            save_data('users', st.session_state['data']['users'])

            current_points = st.session_state['data']['points_history']
            new_points_log = pd.DataFrame([{'user_id': user_id, 'date': datetime.now().strftime('%Y-%m-%d'), 'points_change': points_gained, 'reason': 'Weekly Submission'}])
            save_data('points_history', pd.concat([current_points, new_points_log], ignore_index=True))
            
            st.session_state['analysis_result'] = analysis
            st.toast(f"Data submitted! You gained {points_gained} Eco-Points! ✅", icon='🎉')
            st.rerun()

    st.divider()

    analysis_result = st.session_state['analysis_result']
    if analysis_result:
        st.subheader("📊 Carbon Footprint Analysis")
        st.metric(label="Total Weekly Carbon Footprint (kgCO2e)", value=f"{analysis_result['total_cf']:.2f}")
        if analysis_result['total_cf'] < VITIAN_AVG['total']: st.success(analysis_result['comparison']['message'])
        else: st.warning(analysisResult['comparison']['message'])

        comparison_data = pd.DataFrame({'Category': ['You', 'University Avg', 'Global Avg'], 'CO2e': [analysis_result['total_cf'], VITIAN_AVG['total'], MOCK_DATA['globalAverage']]}).set_index('Category')
        st.bar_chart(comparison_data)

        st.divider()

        st.subheader("💡 Personalized Recommendations")
        col_excel, col_tips = st.columns(2)
        with col_excel:
            if analysis_result['excel_tip']: st.info(f"🏆 **Eco-Excellence:** {analysis_result['excel_tip']}")
            else: st.info("⭐ **Note:** No major area of excellence found this week. Keep tracking!")
        with col_tips:
            if analysis_result['personalized_tips']:
                st.error("🚨 **Focus Areas (Improvement):**")
                for tip in analysis_result['personalized_tips']: st.markdown(f"- {tip}")
            else: st.success("😊 **Great Job!** Minimal impact areas found. Keep up the good work!")
        st.caption(f"**Eco-Fact:** {analysis_result['random_tip']}")

def render_history_page():
    user_id = st.session_state['user_id']
    st.title("🕒 My Eco-History")
    col_cf, col_points = st.columns(2)

    with col_cf:
        st.subheader("Carbon Footprint Trend (kgCO2e)")
        cf_history = st.session_state['data']['carbon_entries'][st.session_state['data']['carbon_entries']['user_id'] == user_id].tail(10).copy()
        if not cf_history.empty:
            cf_history['date'] = pd.to_datetime(cf_history['date'])
            cf_history = cf_history.set_index('date')
            st.line_chart(cf_history['total_cf'])
        else: st.info("No recorded carbon entries yet.")

    with col_points:
        st.subheader("Eco-Points Earned/Lost")
        points_history = st.session_state['data']['points_history'][st.session_state['data']['points_history']['user_id'] == user_id].tail(10).copy()
        if not points_history.empty:
            points_history['date'] = pd.to_datetime(points_history['date'])
            points_history['cumulative_points'] = points_history['points_change'].cumsum()
            points_history = points_history.set_index('date')
            st.bar_chart(points_history[['points_change', 'cumulative_points']])
        else: st.info("No recorded point history yet.")
    
    st.divider()
    st.subheader("Recent Activity Log")
    st.dataframe(
        st.session_state['data']['carbon_entries'][st.session_state['data']['carbon_entries']['user_id'] == user_id].tail(5)[['date', 'total_cf', 'ac_hours', 'water_litres']], 
        column_config={'total_cf': st.column_config.NumberColumn("CF (kgCO2e)", format="%.2f")}, hide_index=True
    )

def render_game_page():
    st.title("🎮 Carbon Quest: Eco-Challenges")
    st.markdown("""<p style='font-size: 1.1em;'>Complete daily and weekly micro-actions to earn **bonus Eco-Points** and improve your hostel's standing!</p>""", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Daily Missions (10 Points)")
        with st.container(border=True):
            st.markdown("### 1. Water Watch 💧"); st.markdown(f"**Challenge:** Log a shower time under **5 minutes** today."); st.button("I Completed the Water Watch!", key="btn_water", type="secondary")
        with st.container(border=True):
            st.markdown("### 2. Zero-Waste Carry ♻️"); st.markdown("**Challenge:** Use a reusable container/cup for all food/drinks purchased today."); st.button("I Completed the Zero-Waste Carry!", key="btn_detox", type="secondary")

    with col2:
        st.subheader("Weekly Quests (30 Points + Leaderboard Bonus)")
        with st.container(border=True):
            st.markdown("### 1. Meatless Monday/Any-Day 🥩➡️🥦"); st.markdown("**Quest:** Go one full day this week without consuming any meat product."); st.button("I Completed the Meatless Day!", key="btn_lunch", type="primary")
        with st.container(border=True):
            st.markdown("### 2. Sustainable Commute 🚴"); st.markdown("**Quest:** Take zero bus rides for 3 consecutive days this week (Walk/Cycle only)."); st.button("I Completed the Sustainable Commute!", key="btn_commute", type="primary")
    
    st.divider()
    st.subheader("Leaderboard Bonus"); st.warning("The user who logs completion for the most Quests this week gets a **+100 Point Bonus**!")

def render_leaderboard():
    st.title("🏆 Leaderboard")
    users_df = st.session_state['data']['users'].copy()
    individual_df = users_df.sort_values(by='eco_points', ascending=False).reset_index(drop=True)
    individual_df['Rank'] = individual_df.index + 1
    individual_df['Hostel'] = individual_df['hostel_id'].map(HOSTEL_MAP)

    hostel_df = individual_df.groupby(['hostel_id', 'Hostel'])['eco_points'].sum().reset_index()
    hostel_df.columns = ['hostel_id', 'Hostel', 'Total Points']
    hostel_df = hostel_df.sort_values(by='Total Points', ascending=False).reset_index(drop=True)
    hostel_df['Rank'] = hostel_df.index + 1

    col_hostel, col_individual = st.columns(2)
    with col_hostel:
        st.subheader("🏢 Hostel Rankings (Total Points)")
        def format_rank(rank):
            if rank == 1: return "🥇"
            elif rank == 2: return "🥈"
            elif rank == 3: return "🥉"
            return str(rank)
        display_hostel = hostel_df.head(5); display_hostel['Rank'] = display_hostel['Rank'].apply(format_rank)
        st.dataframe(display_hostel[['Rank', 'Hostel', 'Total Points']], column_config={'Rank': st.column_config.TextColumn("Rank"), 'Total Points': st.column_config.NumberColumn("Total Points", format="%d 🏆")}, hide_index=True)

    with col_individual:
        st.subheader("👤 Top Eco-Warriors")
        display_individual = individual_df.head(10); display_individual['Rank'] = display_individual['Rank'].apply(format_rank)
        st.dataframe(display_individual[['Rank', 'username', 'Hostel', 'eco_points']], column_config={'Rank': st.column_config.TextColumn("Rank"), 'username': 'Name', 'Hostel': 'Hostel', 'eco_points': st.column_config.NumberColumn("Points", format="%d 🏆")}, hide_index=True)

def render_global_snapshot():
    st.title("🌎 Global Environmental Snapshot")
    col_co2, col_deforest, col_ocean = st.columns(3)
    with col_co2: st.metric(label="CO₂ PPM (Current)", value=MOCK_DATA['globalStats']['co2ppm'], delta="+2.5 since last year")
    with col_deforest: st.metric(label="Hectares Lost/Year (Millions)", value=f"{MOCK_DATA['globalStats']['deforestation']:.1f}M", delta="-0.2M (Slowing down)")
    with col_ocean: st.metric(label="Ocean Temp Rise (°C)", value=f"+{MOCK_DATA['globalStats']['oceanTemp']}", delta="Rising")
    st.divider()
    
    st.subheader("Your Contribution to University Waste Reduction")
    trash_log_df = st.session_state['data']['trash_log']
    if not trash_log_df.empty and 'user_id' in trash_log_df.columns:
        total_trash_entries = trash_log_df.shape[0]
        user_trash_entries = trash_log_df[trash_log_df['user_id'] == st.session_state['user_id']].shape[0]
    else: total_trash_entries = 0; user_trash_entries = 0
    st.markdown(f"You have logged **{user_trash_entries}** successful trash deposits out of **{total_trash_entries}** total logs across the university.")
    st.progress(user_trash_entries / (total_trash_entries if total_trash_entries > 0 else 1))


# --- Main App Execution ---

def main():
    init_session_state()

    if 'data' in st.session_state and not st.session_state['data']['users'].empty:
        calculate_dynamic_vitan_avg(st.session_state['data']['users'], st.session_state['data']['estate_data'])
    
    st.set_page_config(
        page_title="Green Tracker Dashboard", 
        layout="wide", 
        initial_sidebar_state="expanded" if st.session_state['logged_in'] else "collapsed",
        menu_items=None
    )

    if not st.session_state['logged_in']:
        render_login_page()
    else:
        render_sidebar()
        
        if st.session_state['current_view'] == 'Dashboard':
            render_dashboard()
        elif st.session_state['current_view'] == 'My History':
            render_history_page()
        elif st.session_state['current_view'] == 'Carbon Quest':
            render_game_page()
        elif st.session_state['current_view'] == 'Leaderboard':
            render_leaderboard()
        elif st.session_state['current_view'] == 'Global Snapshot':
            render_global_snapshot()

if __name__ == "__main__":
    main()