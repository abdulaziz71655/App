import asyncio
import requests
import streamlit as st
import yt_dlp
from streamlit_option_menu import option_menu
from pyktok import pyktok
import snscrape.modules.twitter as sntwitter
import twint
import os
import re
import bs4
from tqdm import tqdm
from pathlib import Path
import instaloader
import json
import subprocess
from urllib.request import urlopen, URLError

# Set up the page configuration and sidebar
st.set_page_config(page_title='Dashboard', page_icon="🌍", layout="wide")
st.sidebar.image("logo.png", caption="Online Video Downloader")
st.title("VideoWonsdder")

# Inject custom CSS to adjust the video width
st.markdown(
    """
    <style>

    video {
        max-width: 600px;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# User-agent to mimic a browser request for Reddit
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

# Base directory to save videos
base_video_dir = "videos"
platform_dirs = {
    "YouTube": os.path.join(base_video_dir, "YouTube"),
    "TikTok": os.path.join(base_video_dir, "TikTok"),
    "Twitter": os.path.join(base_video_dir, "Twitter"),
    "Instagram": os.path.join(base_video_dir, "Instagram"),
    "Facebook": os.path.join(base_video_dir, "Facebook")
}

# Ensure all platform directories exist
for platform, dir_path in platform_dirs.items():
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def youtube_downloader():
    st.title("YouTube Video Download")
    video_urls = st.text_input(label="Enter your YouTube video URL")
    
    if st.button('Download YouTube Video'):
        if 'youtube.com' in video_urls or 'youtu.be' in video_urls:
            try:
                # Options to download best video and audio
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4', 
                    'outtmpl': f'{platform_dirs["YouTube"]}/%(title)s.%(ext)s',
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    st.write("Downloading...")
                    st.video(video_urls)
                    info_dict = ydl.extract_info(video_urls, download=True)
                    
                    video_title = info_dict.get('title', 'video')
                    video_file = f"{platform_dirs['YouTube']}/{video_title}.mp4"

                    st.write("### Enjoy your video")
                    st.write(f"Video file saved as: `{video_file}`")
            except Exception as e:
                st.warning(f"⚠️ Failed to download the video: {e}")
        else:
            st.error("☢️ Enter a valid YouTube URL")

def tiktok_downloader():
    st.title("TikTok Video Downloader")
    
    # Get video URLs from user input
    video_urls_input = st.text_input(label="Enter your TikTok video URLs (separated by commas)")
    video_urls = [url.strip() for url in video_urls_input.split(',')]
    
    if st.button('Download TikTok Videos'):
        if not video_urls:
            st.warning("Please enter at least one URL.")
            return
        
        try:
            st.write("Starting download...")
            
            # Call the download function
            for video_url in video_urls:
                st.video(video_url)
                pyktok.save_tiktok_multi_urls([video_url], True, f'{platform_dirs["TikTok"]}/tiktok_data.csv', 1)
            
            st.write(f"Downloading TikTok videos from: {video_urls}")
            
            st.write("### Enjoy your video(s)")
            st.write("To download the video(s), check your current directory for the downloaded files.")
        
        except Exception as e:
            st.warning(f"An error occurred: {e}")

def download_video(url, file_name, platform_dir) -> None:
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

    download_path = os.path.join(platform_dir, file_name)

    with open(download_path, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    print("Video downloaded successfully!")
    st.write("Video downloaded successfully!")

def download_twitter_video():
    st.title("Twitter Video Downloader")
    video_urls = st.text_input(label="Enter your Twitter video URL")

    if st.button('Download Twitter Video'):
        if 'twitter.com' in video_urls or 'x.com' in video_urls:
            api_url = f"https://twitsave.com/info?url={video_urls}"
            st.write("downloading......")

            response = requests.get(api_url)
            data = bs4.BeautifulSoup(response.text, "html.parser")
            download_button = data.find_all("div", class_="origin-top-right")[0]
            quality_buttons = download_button.find_all("a")
            highest_quality_url = quality_buttons[0].get("href") # Highest quality video url
            
            file_name = data.find_all("div", class_="leading-tight")[0].find_all("p", class_="m-2")[0].text # Video file name
            file_name = re.sub(r"[^a-zA-Z0-9]+", ' ', file_name).strip() + ".mp4" # Remove special characters from file name
            
            download_video(highest_quality_url, file_name, platform_dirs["Twitter"])
        else:
            st.error("☢️ Enter a valid Twitter URL")

def download_instagram_video():
    st.title("Instagram Video Download")
    video_urls = st.text_input(label="Enter your Instagram post URL")
    
    if st.button("Download Instagram Video"):
        if 'instagram.com' in video_urls:
            try:
                st.video(video_urls)
                loader = instaloader.Instaloader()
                shortcode = video_urls.split('/')[-2]
                post = instaloader.Post.from_shortcode(loader.context, shortcode)
                
                if post.is_video:
                    video_path = loader.download_post(post, target=f"{platform_dirs['Instagram']}/{post.owner_username}_{shortcode}")
                    st.write("### Enjoy your video")
                    st.write(f"Video file saved as: {post.owner_username}_{shortcode}.mp4")
                else:
                    st.warning("The provided URL does not point to a video.")
            except Exception as e:
                st.warning(f"⚠️ Failed to download the Instagram video: {e}")
        else:
            st.error("☢️ Enter a valid Instagram post URL")

def facebook_video_downloader():
    st.title("Facebook Video Downloader")
    video_urls = st.text_input("Enter your video URL:")

    def downloadFile(link, file_name):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
        }
        try:
            resp = requests.get(link, headers=headers).content
        except Exception as e:
            st.error(f"Failed to open {link}: {str(e)}")
            return
        with open(os.path.join(platform_dirs["Facebook"], file_name), 'wb') as f:
            f.write(resp)

    def downloadVideo(link):
        st.video(video_urls)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Dnt': '1',
            'Dpr': '1.3125',
            'Priority': 'u=0, i',
            'Sec-Ch-Prefers-Color-Scheme': 'dark',
            'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="124.0.6367.156", "Google Chrome";v="124.0.6367.156", "Not-A.Brand";v="99.0.0.0"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Model': '""',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Ch-Ua-Platform-Version': '"15.0.0"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

        try:
            resp = requests.get(link, headers=headers).content.decode('utf-8')
            video_id = resp.split('"videoId":"')[1].split('",')[0]
            target_video_audio_id = resp.split('"id":"{}"'.format(video_id))[1].split('"dash_prefetch_experimental":[')[1].split(']')[0].strip()
        except Exception as e:
            print(f"An error occurred: {e}")
        list_str = "[{}]".format(target_video_audio_id)
        sources = json.loads(list_str)
        video_link = resp.split('"representation_id":"{}"'.format(sources[0]))[1].split('"base_url":"')[1].split('"')[0]
        video_link = video_link.replace('\\', '')
        audio_link = resp.split('"representation_id":"{}"'.format(sources[1]))[1].split('"base_url":"')[1].split('"')[0]
        audio_link = audio_link.replace('\\', '')
        st.write("Downloading video...")
        downloadFile(video_link, 'video.mp4')
        st.write("Downloading audio...")
        downloadFile(audio_link, 'audio.mp4')
        st.write("Merging files...")
        video_path = os.path.join(platform_dirs["Facebook"], 'video.mp4')
        audio_path = os.path.join(platform_dirs["Facebook"], 'audio.mp4')
        combined_file_path = os.path.join(platform_dirs["Facebook"], 'merged_final.mp4')
        cmd = f'ffmpeg -hide_banner -loglevel error -i "{video_path}" -i "{audio_path}" -c copy "{combined_file_path}"'
        subprocess.call(cmd, shell=True)
        st.write("Re-encoding to H.264 format...")
        reencoded_file_path = os.path.join(platform_dirs["Facebook"], f'{video_id}.mp4')
        cmd_reencode = f'ffmpeg -hide_banner -loglevel error -i "{combined_file_path}" -c:v libx264 -c:a aac "{reencoded_file_path}"'
        subprocess.call(cmd_reencode, shell=True)
        os.remove(os.path.join(platform_dirs["Facebook"], 'video.mp4'))
        os.remove(os.path.join(platform_dirs["Facebook"], 'audio.mp4'))
        os.remove(combined_file_path)
        st.success(f"Done! Please check in the {platform_dirs['Facebook']} folder")

    if st.button("Download"):
        downloadVideo(video_urls)

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
                    btn = st.download_button(
                        label="Download Video",
                        data=file,
                        file_name=video_file,
                        mime="video/mp4"
                    )

# Sidebar navigation menu
def sideBar():
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "YouTube", "TikTok", "Twitter", "Instagram", "Facebook", "Gallery"],
        icons=["house", "youtube", "tiktok", "twitter", "instagram", "facebook", "image"],
        menu_icon="cast",
        orientation="horizontal",
    )
    return selected

# Main content based on sidebar selection
selected = sideBar()

if selected == "Home":
    st.write("## Welcome to the Video Downloader app!")
    st.markdown("""___""")
    st.write("This app is designed to help you download videos from popular platforms like YouTube, TikTok, Twitter, Instagram, and Facebook.")

elif selected == "YouTube":
    youtube_downloader()

elif selected == "TikTok":
    tiktok_downloader()

elif selected == "Twitter":
    download_twitter_video()

elif selected == "Instagram":
    download_instagram_video()

elif selected == "Facebook":
    facebook_video_downloader()

elif selected == "Gallery":
    video_gallery()

# Theme for hiding Streamlit default style
hide_st_style = """
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
