import asyncio
import requests
import streamlit as st
from yt_dlp import YoutubeDL
from streamlit_option_menu import option_menu
from pyktok import pyktok
import snscrape.modules.twitter as sntwitter
import twint
import os
import sys
import re
import bs4
from tqdm import tqdm
from pathlib import Path
import instaloader
import json
import subprocess
from urllib.request import urlopen, URLError
import time
import threading

# Set up the page configuration and sidebar
st.set_page_config(page_title='Dashboard', page_icon="🌍", layout="wide")
st.sidebar.image("logo.png", caption="online video downloader")
st.title("viddeoWonsdder")

# User-agent to mimic a browser request for Reddit
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def youtube_downloader():
    st.title("YouTube Video Download")
    video_url = st.text_input(label="Enter your YouTube video URL")
    
    if st.button('Download YouTube Video'):
        if 'youtube.com' in video_url or 'youtu.be' in video_url:
            try:
                # Options to download best video and audio
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',  # Select best video and audio
                    'merge_output_format': 'mp4',  # Merge audio and video into MP4
                    'outtmpl': '%(title)s.%(ext)s',
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    st.write("Downloading...")
                    info_dict = ydl.extract_info(video_url, download=True)
                    
                    video_title = info_dict.get('title', 'video')
                    video_file = f"{video_title}.mp4"

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
            pyktok.save_tiktok_multi_urls(video_urls, True, 'tiktok_data.csv', 1)
            st.write(f"Downloading TikTok videos from: {video_urls}")
            
            st.write("### Enjoy your video(s)")
            st.write("To download the video(s), check your current directory for the downloaded files.")
        
        except Exception as e:
            st.warning(f"An error occurred: {e}")


def par_of_twitter(video_url, file_name):

    response = requests.get(video_url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

    download_path = os.path.join(Path.home(), "streamlit", file_name)
    

    with open(download_path, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()
    print("Video downloaded successfully!")


def download_twitter_video():
    st.title("Twitter video download")
    video_url = st.text_input(label="Enter your YouTube video URL")
    if st.button('Download Twitter Video'):
        if 'twitter.com' in video_url or 'x.com' in video_url:
            try :

                api_url = f"https://twitsave.com/info?url={video_url}"
                st.write("downloading")
                response = requests.get(api_url)
                data = bs4.BeautifulSoup(response.text, "html.parser")
                download_button = data.find_all("div", class_="origin-top-right")[0]
                quality_buttons = download_button.find_all("a")
                highest_quality_url = quality_buttons[0].get("href") # Highest quality video url
                
                file_name = data.find_all("div", class_="leading-tight")[0].find_all("p", class_="m-2")[0].text # Video file name
                file_name = re.sub(r"[^a-zA-Z0-9]+", ' ', file_name).strip() + ".mp4" # Remove special characters from file name
                
                st.write(file_name,highest_quality_url)
                download_video(highest_quality_url, file_name)
            except Exception as e:
                st.warning(f"���️ Failed to download the Twitter video: {e}")
        else:
            st.error("��️ Enter a valid Twitter URL")

def download_instagram_video():
    st.title("Instagram video download")
    post_url = st.text_input(label="Enter your Instagram post URL")
    if st.button("Download Instagram video"):
        if 'instagram.com' in post_url:
            try:
                
                st.video(post_url)
                # Create an instance of Instaloader
                loader = instaloader.Instaloader()
                
                # Get the shortcode from the post URL
                shortcode = post_url.split('/')[-2]
                
                # Load the post by shortcode
                post = instaloader.Post.from_shortcode(loader.context, shortcode)
                
                # Check if it's a video post
                if post.is_video:
                    # Download the video
                    video_path = loader.download_post(post, target=f"{post.owner_username}_{shortcode}")
                    print(f" Video downloaded successfully: {post.owner_username}_{shortcode}.mp4")
                    
                    # Display the video using st.video()
                    st.write("### Enjoy your video")
                    st.write(f"Video file saved as: {post.owner_username}_{shortcode}.mp4")
                else:
                    print("The provided URL does not point to a video.")
            except Exception as e:
                st.warning(f"⚠️ Failed to download the Instagram video: {e}")
        else:
            st.error("☢️ Enter a valid Instagram post URL")

def facebook_video_downloader():
    st.title("Facebook Video Downloader")
    post_url = st.text_input("Enter your video URL:")
    output_folder = "Output"
    keep_raw_files = False

    def downloadFile(link, file_name):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
        }
        try:
            resp = requests.get(link, headers=headers).content
        except Exception as e:
            st.error(f"Failed to open {link}: {str(e)}")
            return
        with open(os.path.join(output_folder, file_name), 'wb') as f:
            f.write(resp)

    def downloadVideo(link):
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Viewport-Width': '1463'
        }
        try:
            resp = requests.get(link, headers=headers)
        except Exception as e:
            st.error(f"Failed to open {link}: {str(e)}")
            return
        link = resp.url.split('?')[0]
        resp = resp.text
        splits = link.split('/')
        video_id = ''
        for ids in splits:
            if ids.isdigit():
                video_id = ids
        try:
            target_video_audio_id = resp.split('"id":"{}"'.format(video_id))[1].split(
                '"dash_prefetch_experimental":[')[1].split(']')[0].strip()
        except:
            target_video_audio_id = resp.split('"video_id":"{}"'.format(video_id))[1].split(
                '"dash_prefetch_experimental":[')[1].split(']')[0].strip()
        list_str = "[{}]".format(target_video_audio_id)
        sources = json.loads(list_str)
        video_link = resp.split('"representation_id":"{}"'.format(sources[0]))[
            1].split('"base_url":"')[1].split('"')[0]
        video_link = video_link.replace('\\', '')
        audio_link = resp.split('"representation_id":"{}"'.format(sources[1]))[
            1].split('"base_url":"')[1].split('"')[0]
        audio_link = audio_link.replace('\\', '')
        st.write("Downloading video...")
        downloadFile(video_link, 'video.mp4')
        st.write("Downloading audio...")
        downloadFile(audio_link, 'audio.mp4')
        st.write("Merging files...")
        video_path = os.path.join(output_folder, 'video.mp4')
        audio_path = os.path.join(output_folder, 'audio.mp4')
        combined_file_path = os.path.join(output_folder, 'merged_final.mp4')
        cmd = f'ffmpeg -hide_banner -loglevel error -i "{video_path}" -i "{audio_path}" -c copy "{combined_file_path}"'
        subprocess.call(cmd, shell=True)
        st.write("Re-encoding to H.264 format...")
        reencoded_file_path = os.path.join(output_folder, f'{video_id}.mp4')
        cmd_reencode = f'ffmpeg -hide_banner -loglevel error -i "{combined_file_path}" -c:v libx264 -c:a aac "{reencoded_file_path}"'
        subprocess.call(cmd_reencode, shell=True)
        os.remove(os.path.join(output_folder, 'video.mp4'))
        os.remove(os.path.join(output_folder, 'audio.mp4'))
        os.remove(combined_file_path)
        st.success(f"Done! Please check in the {output_folder} folder")

    if st.button("Download"):
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        downloadVideo(post_url)

# Sidebar navigation menu
def sideBar():
# with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "YouTube",  "TikTok", "Twitter","instagram","facebook"],
        icons=["house", "youtube", "tiktok", "twitter","instagram","facebook"],
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
elif selected == "instagram":
    download_instagram_video()
elif selected == "facebook":
    facebook_video_downloader()


# Theme for hiding Streamlit default style
hide_st_style="""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
#st.markdown(hide_st_style, unsafe_allow_html=True)
