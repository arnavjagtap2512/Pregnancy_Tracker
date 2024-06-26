import streamlit as st
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
# Set the title of the app
st.title("Pregnancy Tracker")

# Functions for due date calculations
def get_date_by_conception(date):
    given_date = datetime.strptime(date, '%Y-%m-%d')
    future_date = given_date + timedelta(weeks=38)
    return future_date

def get_date_by_lmp(date):
    given_date = datetime.strptime(date, '%Y-%m-%d')
    future_date = given_date + timedelta(weeks=40)
    return future_date

# Function to calculate current week of pregnancy
def calculate_week_of_pregnancy(start_date, calculation_type):
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    current_date = datetime.today()
    
    if calculation_type == 'Conception Date':
        time_difference = current_date - start_date_obj
    elif calculation_type == 'Last Menstrual Period Date':
        lmp_date = start_date_obj - timedelta(days=14)
        time_difference = current_date - lmp_date
    else:
        raise ValueError('Invalid calculation type. Please specify either "conception" or "lmp".')
    
    # Convert the time difference from milliseconds to weeks
    weeks_elapsed = time_difference.days // 7
    
    # Add 1 to the weeks elapsed, as pregnancy is counted from the start of the LMP or conception
    return weeks_elapsed + 1

# Function to display doughnut chart 
@st.cache_resource()
def plot_doughnut_chart(percentage_completed):
    fig = go.Figure(go.Pie(
        values=[percentage_completed, 100 - percentage_completed],
        labels=['Completed', 'Remaining'],
        hole=.7,
        marker=dict(colors=['#1db954', '#dddddd']),
        textinfo='none',  # Hide all text in the slices
        sort=False,  # Disable sorting to maintain order
        direction='clockwise'  # Set the direction to clockwise
    ))

    fig.update_layout(
        title_text='Pregnancy Progress',
        title_font=dict(size=24),  # Increase font size of the title
        annotations=[dict(text=f'{percentage_completed:.1f}% Completed', x=0.5, y=0.5, font_size=20, showarrow=False)],
        showlegend=False,
        margin=dict(l=0, r=0, t=40, b=0), # Reduce margins to minimize space
        height=300
    )
    
    return fig

# Function to display vertical progress bar using HTML and CSS
def display_vertical_progress_bar(percentage_completed):
    progress_style = f"""
    <style>
    .progress-container {{
        width: 40px;
        height: 260px;
        background-color: #ddd;
        border-radius: 5px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        position: relative;
        top: 40px;
    }}
    .progress-bar {{
        width: 100%;
        height: {percentage_completed}%;
        background-color: #1db954;
        border-radius: 5px 5px 0 0;
    }}
    .progress-marker {{
        width: 100%;
        height: 5px;
        background-color: black;
        position: absolute;
        left: 0;
    }}
    .marker1 {{
        top: 33.3%;
    }}
    .marker2 {{
        top: 66.6%;
    }}
    .marker3 {{
        top: 99%;
    }}
    .label {{
        position: absolute;
        width: 200px;
        left: 74px;
        font-size: 20px;
        font-weight: 500;
        transform: translateY(-50%);
    }}
    .label1 {{
        top: 16.65%;
    }}
    .label2 {{
        top: 50%;
    }}
    .label3 {{
        top: 82.95%;
    }}
    </style>
    """
    progress_html = f"""
    <div class="progress-container">
        <div class="progress-bar"></div>
        <div class="progress-marker marker1"></div>
        <div class="progress-marker marker2"></div>
        <div class="progress-marker marker3"></div>
        <div class="label label1">First Trimester</div>
        <div class="label label2">Second Trimester</div>
        <div class="label label3">Third Trimester</div>
    </div>
    """
    return progress_style + progress_html

# Create two columns
col1, col2 = st.columns([2, 1.5])

with col1:
    # Create a form for user input
    with st.form(key='dateCalculationForm'):
        calculation_type = st.selectbox(
            'Calculation Type:',
            ('Conception Date', 'Last Menstrual Period Date')
        )
        actual_date = st.date_input("Actual Date:")
        
        # Submit button
        submit_button = st.form_submit_button(label='Submit')

# Process form submission
if submit_button:
    if calculation_type == 'Conception Date':
        due_date = get_date_by_conception(actual_date.strftime('%Y-%m-%d'))
    else:
        due_date = get_date_by_lmp(actual_date.strftime('%Y-%m-%d'))
    
    st.write(f"Expected Due Date: {due_date.strftime('%Y-%m-%d')}")
    # Display the selected calculation type and date
    st.write(f"Calculation Type: {calculation_type}")
    st.write(f"{calculation_type}: {actual_date}")

    # Calculate the current week of pregnancy
    week_number = calculate_week_of_pregnancy(str(actual_date), calculation_type)
    
    if 1 <= week_number <= 41 :
        # Display the week number
        st.write(f"You are in week {week_number}.")
        percentage_completed = (week_number / 40) * 100
    
        # Display doughnut chart
        col1, col2 = st.columns([2, 2])
        with col1:
            fig = plot_doughnut_chart(percentage_completed)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            progress_bar = display_vertical_progress_bar(percentage_completed)
            st.markdown(progress_bar, unsafe_allow_html=True)

        st.caption("These charts show the progress of your pregnancy based on the current week. The doughnut chart indicates the overall percentage completed in your 40-week pregnancy journey, while the vertical progress bar highlights your progress through each trimester.")
    else:
        st.warning("The calculated week number is out of the valid range (1-40). Please check the input date.")
    dataset = pd.read_csv('weeks.csv')

    # Select data for week 4 (index 3 since index starts from 0)
    week_data = dataset.iloc[week_number - 2]

    # Extract individual fields
    baby_development = week_data['babyDevelopment']
    pregnancy_symptoms = week_data['pregnancySymptoms']
    pregnancy_checklist = week_data['pregnancyChecklist']
    images = week_data['images'].split(';')

    # Define CSS style for cards
    card_style = """
    <style>
    .card {
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    .card p {
        margin: 0;
    }
    .card ul {
        margin-top: 5px;
        padding-left: 20px;
    }
    .images-container {
        display: flex;
        justify-content: flex-start;
        margin-top: 15px;
    }
    .card-img {
        height: 20rem;
        width: 20rem;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    </style>
    """

    # Display HTML with styled content
    st.markdown(card_style, unsafe_allow_html=True)

    # Display the cards with data
    st.markdown("<h2>Baby Development</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>{baby_development}</div>", unsafe_allow_html=True)

    st.markdown("<h2>Pregnancy Symptoms</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'><ul>{''.join([f'<li>{symptom.strip()}</li>' for symptom in pregnancy_symptoms.split(';')])}</ul></div>", unsafe_allow_html=True)

    st.markdown("<h2>Pregnancy Checklist</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'><ul>{''.join([f'<li>{item.strip()}</li>' for item in pregnancy_checklist.split(';')])}</ul></div>", unsafe_allow_html=True)

    # Display the images
    st.markdown("<h2>Images</h2>", unsafe_allow_html=True)
    image_html = "<div class='images-container'>"
    for image_url in images:
        image_html += f"<img src='{image_url}' class='card-img'>"
    image_html += "</div>"
    st.markdown(image_html, unsafe_allow_html=True)