from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# Access the API keys
google_api_key = os.getenv('GOOGLE_API_KEY')
# Define YouTube API key (replace with your own API key)
youtube_api_key = os.getenv('YOUTUBE_API_KEY')

st.set_page_config(layout="wide")
# Initialize Streamlit app title and description
st.title("Pregnancy AI Assistant")
st.write("Get quick, reliable answers to your pregnancy-related questions. Leveraging AI to provide accurate and timely information to expectant mothers.")

def stream_data(script):
    for word in script.split(" "):
        yield word + " "
        time.sleep(0.02)

# Initialize the ChatGoogleGenerativeAI instance
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key)

# Function to perform web scraping based on user query
def scrape_links(query):
    # Replace spaces in the query with plus signs for URL encoding
    query = query.replace(" ", "+")
    
    # Example: Using Google search to fetch links related to the query
    url = f"https://www.google.com/search?q={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all('div', class_='tF2Cxc')
            
            links = []
            for result in search_results:
                link = result.find('a')['href']
                links.append(link)
            
            return links
        
        else:
            st.error("Failed to retrieve search results.")
            return None
    
    except Exception as e:
        st.error(f"Error occurred during web scraping: {str(e)}")
        return None

# Function to fetch YouTube videos using YouTube Data API
def fetch_youtube_videos(query):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=3  # Number of videos to fetch (adjust as needed)
    )
    response = request.execute()
    return response.get('items', [])


# Display user query input and answer generation button if files are processed
# Create two columns
col1, col2 = st.columns([2, 1.4])

# Column 1: Left side for text input
with col1:
    user_query = st.text_input(
        "Ask any pregnancy-related question",
        placeholder="What are the symptoms in the first trimester?"
    )

if st.button("Get Answer"):
    with st.spinner("Generating Answer...."):
        result = llm.invoke(user_query)
        st.write("Question: ", user_query)
        st.write("Answer:")
        st.write_stream(stream_data(result.content))
        
        # Perform web scraping based on the user's query
        scraped_links = scrape_links(user_query)
        if scraped_links:
            st.markdown("**Useful Links:**")
            for link in scraped_links[:3]:  # Display up to 3 links
                st.markdown(f"- [{link}]({link})")

        videos = fetch_youtube_videos(user_query)
        if videos:
            st.markdown("**Related Videos:**")
            
            # Define CSS style for flex container
            st.markdown(
                """
                <style>
                .video-container {
                    display: flex;
                    flex-direction: row;
                    flex-wrap: wrap;
                    gap: 10px; /* Adjust the gap between videos */
                    justify-content: flex-start; /* Align items from left to right */
                }
                .video-container iframe {
                    width: 300px; /* Adjust width of each video */
                    height: 200px; /* Adjust height of each video */
                    border: 1px solid #ccc; /* Add border for clarity */
                    border-radius: 10px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # Start the video container
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            
            # Create a list to hold the iframes for each video
            iframe_codes = []
            # Iterate over each video and embed using iframe
            for video in videos:
                video_id = video['id']['videoId']
                iframe_code = f'<iframe width="300" height="200" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
                iframe_codes.append(iframe_code)

            # Concatenate the iframe codes into a single string
            iframe_codes_str = " ".join(iframe_codes)
            
            # Display the video container with all iframes inside
            st.markdown(f'<div class="video-container">{iframe_codes_str}</div>', unsafe_allow_html=True)
        else:
            st.warning("No videos found.")

