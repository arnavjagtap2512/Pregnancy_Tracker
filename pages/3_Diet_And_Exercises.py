import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
# Load the data
diet_data = pd.read_csv('diet_nutrition.csv')
exercise_data = pd.read_csv('exercise_routines.csv')
diet_chart_data = pd.read_csv('sample_diet_chart.csv')

# CSS to center-align table headers
st.markdown(
    """
    <style>
    th {
        text-align: center !important;
        font-weight: 400;
        color: #6e6e6e !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define functions to get recommendations based on user inputs
def get_custom_diet_recommendations(trimester, dietary_restrictions):
    recommendations = diet_data[diet_data['trimester'] == trimester].copy()

    # Convert dietary restrictions to lowercase for case-insensitive matching
    dietary_restrictions = [restriction.lower() for restriction in dietary_restrictions]

    # Filter based on dietary restrictions
    if 'vegetarian' in dietary_restrictions:
        recommendations.loc[recommendations['food_group'] == 'Proteins', 'examples'] = recommendations.loc[recommendations['food_group'] == 'Proteins', 'examples'].apply(lambda x: ', '.join([item for item in x.split(', ') if 'meat' not in item and 'fish' not in item]))
    if 'vegan' in dietary_restrictions:
        recommendations.loc[recommendations['food_group'] == 'Proteins', 'examples'] = recommendations.loc[recommendations['food_group'] == 'Proteins', 'examples'].apply(lambda x: ', '.join([item for item in x.split(', ') if 'meat' not in item and 'fish' not in item and 'dairy' not in item and 'egg' not in item]))
    if 'gluten-free' in dietary_restrictions:
        recommendations.loc[recommendations['food_group'] == 'Whole Grains', 'examples'] = recommendations.loc[recommendations['food_group'] == 'Whole Grains', 'examples'].apply(lambda x: ', '.join([item for item in x.split(', ') if 'wheat' not in item and 'barley' not in item and 'rye' not in item]))
    if 'lactose intolerant' in dietary_restrictions:
        recommendations.loc[recommendations['food_group'] == 'Dairy or Alternatives', 'examples'] = recommendations.loc[recommendations['food_group'] == 'Dairy or Alternatives', 'examples'].apply(lambda x: ', '.join([item for item in x.split(', ') if 'milk' not in item and 'yogurt' not in item and 'cheese' not in item]))

    # Reset index to remove row numbers
    recommendations = recommendations.reset_index(drop=True)

    return recommendations[['food_group', 'examples']]


def filter_meals(diet_chart_data, trimester, dietary_restrictions, meal_preference):
    filtered_meals = diet_chart_data[diet_chart_data['trimester'] == trimester]
    dietary_restrictions = [restriction.lower() for restriction in dietary_restrictions]
    
    for restriction in dietary_restrictions:
        if restriction == 'lactose intolerant':
            filtered_meals['food'] = filtered_meals['food'].apply(lambda x: ', '.join([item for item in x.split(', ') if 'milk' not in item.lower() and 'yogurt' not in item.lower() and 'cheese' not in item.lower()]))
        elif restriction == 'vegetarian':
            filtered_meals['food'] = filtered_meals['food'].apply(lambda x: ', '.join([item for item in x.split(', ') if 'chicken' not in item.lower() and 'fish' not in item.lower() and 'egg' not in item.lower()]))
        elif restriction == 'vegan':
            filtered_meals['food'] = filtered_meals['food'].apply(lambda x: ', '.join([item for item in x.split(', ') if 'milk' not in item.lower() and 'yogurt' not in item.lower() and 'cheese' not in item.lower() and 'egg' not in item.lower()]))
        elif restriction == 'gluten-free':
            filtered_meals['food'] = filtered_meals['food'].apply(lambda x: ', '.join([item for item in x.split(', ') if 'wheat' not in item.lower() and 'barley' not in item.lower() and 'rye' not in item.lower()]))

    if meal_preference == '3 main meals':
        filtered_meals = filtered_meals[filtered_meals['meal'].isin(['Breakfast', 'Lunch', 'Dinner'])]
    elif meal_preference == '3 main meals with snacks':
        filtered_meals = filtered_meals
    elif meal_preference == '2 main meals':
        filtered_meals = filtered_meals[filtered_meals['meal'].isin(['Lunch', 'Dinner'])]

    return filtered_meals[['meal', 'food']]


def get_custom_exercise_recommendations(trimester, exercise_preferences):
    recommendations = exercise_data[(exercise_data['trimester'] == trimester) & (exercise_data['exercise_type'].isin(exercise_preferences))]
    return recommendations

# Streamlit app
st.title("Pregnancy Diet and Exercise Recommendations")

# Create two columns
col1, col2 = st.columns([2, 0.7])

with col1:
    with st.form(key='quizForm'):
        trimester = st.radio('Which trimester are you in?', ['First Trimester', 'Second Trimester', 'Third Trimester'])
        dietary_restrictions = st.multiselect('Do you have any dietary restrictions?', ['None', 'Vegetarian', 'Vegan', 'Gluten-Free', 'Lactose Intolerant'])
        meal_preference = st.radio('How many meals do you prefer to have in a day?', ['2 main meals', '3 main meals', '3 main meals with snacks', 'Flexible'])
        exercise_preferences = st.multiselect('What type of exercises do you enjoy or prefer?', exercise_data['exercise_type'].unique().tolist())

        # Submit button
        submit_button = st.form_submit_button(label='Submit')

if submit_button:
    diet_recommendations = get_custom_diet_recommendations(trimester, dietary_restrictions)
    exercise_recommendations = get_custom_exercise_recommendations(trimester, exercise_preferences)
    filtered_meals = filter_meals(diet_chart_data, trimester, dietary_restrictions, meal_preference)

    # Create two columns
    col1, col2, col3 = st.columns([1, 0.1, 1])
    with col1:
        # Display Custom Diet Recommendations
        st.subheader('Diet Recommendations')
        st.markdown(
            diet_recommendations.rename(columns={'food_group': 'Food Group', 'examples': 'Examples'}).to_html(index=False),
            unsafe_allow_html=True
        )

    with col2:
        # Add vertical divider line between columns
        st.html(
            '''
                <div class="divider-vertical-line"></div>
                <style>
                    .divider-vertical-line {
                        border-left: 2px solid rgba(49, 51, 63, 0.2);
                        margin-top: 40px;
                        height: 340px;
                    }
                </style>
            '''
        )

    with col3:
        # Display Custom Diet Plan
        st.subheader('Sample Diet Chart')
        st.markdown(
            filtered_meals.to_html(index=False, header=False),
            unsafe_allow_html=True
        )

    # Display Custom Exercise Recommendations
    st.subheader('Exercise Recommendations')
    st.markdown("""
        <style>
            .video-container {
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                border-radius: 10px;
                margin: 20px;
            }
                
            .video-container iframe {
                border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    for index, row in exercise_recommendations.iterrows():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"<h5>{row['exercise']}</h5>", unsafe_allow_html=True)
            description_points = row['description'].split('. ')
            st.markdown("<ul>", unsafe_allow_html=True)
            for point in description_points:
                st.markdown(f"<li>{point}</li>", unsafe_allow_html=True)
            st.markdown("</ul>", unsafe_allow_html=True)
        with col2:
            iframe_code = f'''
            <div class="video-container">
                <iframe width="360" height="200" src="https://www.youtube.com/embed/{row['video_id']}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
            </div>
            '''
            st.markdown(iframe_code, unsafe_allow_html=True)

