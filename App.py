import os
import yt_dlp
import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path

# Set up the page configuration and sidebar
st.set_page_config(page_title='Dashboard', page_icon="🌍", layout="wide")
#st.sidebar.image("logo.png", caption="Online Video Downloader")
st.title("VideoWonsdder")
st.write("## Welcome to the Video Downloader app!")
st.markdown("""___""")
st.write("## This app is designed to help you download videos from popular platforms like YouTube, TikTok, Twitter, Instagram, and Facebook.")

# Inject custom CSS to adjust the video width
st.markdown(
    """
    <style>
    video {
        max-width: 600px;
        width: 100%;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Base directory to save videos
base_video_dir = "videos"
platform_dirs = {
    "videos": os.path.join(base_video_dir, "videos")
}

# Create directories if they don't exist
for directory in platform_dirs.values():
    os.makedirs(directory, exist_ok=True)

def youtube_downloader():
    st.title("Video Downloader")
    video_url = st.text_input("Enter your video URL")

    if st.button('Download Video'):
        if video_url:
            try:
                # Options to download best video and audio
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4', 
                    'outtmpl': f'{platform_dirs["videos"]}/%(title)s.%(ext)s',
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    st.write("Downloading...")
                    info_dict = ydl.extract_info(video_url, download=True)
                    
                    video_title = info_dict.get('title', 'video')
                    video_file = f"{platform_dirs['videos']}/{video_title}.mp4"

                    st.write("### Enjoy your video")
                    st.write(f"Video file saved as: `{video_file}`")
                    st.video(video_file)
            except Exception as e:
                st.warning(f"⚠️ Failed to download the video: {e}")
        else:
            st.error("☢️ Enter a valid URL")

def video_gallery():
    st.title("Video Gallery")
    
    platform_options = list(platform_dirs.keys())
    selected_platform = st.selectbox("Select Platform", platform_options)

    if selected_platform:
        st.write(f"Showing videos for {selected_platform}:")
        platform_dir = platform_dirs[selected_platform]
        
        for video_file in os.listdir(platform_dir):
            if video_file.endswith(".mp4"):
                video_path = os.path.join(platform_dir, video_file)
                st.video(video_path)
                with open(video_path, "rb") as file:
                    st.download_button(
                        label="Download Video",
                        data=file,
                        file_name=video_file,
                        mime="video/mp4"
                    )

# Sidebar navigation menu
def sideBar():
    selected = option_menu(
        menu_title="Main Menu",
        options=["Downloader", "Gallery"],
        icons=["cloud-arrow-down", "image"],
        menu_icon="cast",
        orientation="horizontal",
    )
    return selected

# Main content based on sidebar selection
selected = sideBar()

if selected == "Downloader":
    youtube_downloader()
elif selected == "Gallery":
    video_gallery()
