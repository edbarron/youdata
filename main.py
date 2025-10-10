from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
from pytz import timezone
from utils import select_time_frame, generate_table, make_period_label, extract_keywords_from_titles_over_views, LATAM_SPANISH_STOPWORDS
from db_utils import insert_video, delete_channel, fetch_videos_by_date, fetch_all_videos, insert_channel, fetch_all_channels, set_active_channel, fetch_active_channel
import os
from dotenv import load_dotenv
from collections import Counter
import re

LOCAL_TIMEZONE = timezone('America/Phoenix') #change to your own timezone
load_dotenv()

def fetch_and_store_videos(youtube_id, date):
    """
    Fetches videos from the given channel for a specific date and stores them in the database.
    """
    API_KEY = os.getenv("YOUTUBE_API_KEY")
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

    try:
        # Search videos uploaded on the specified date by the channel
        request = youtube.search().list(
            part="snippet",
            channelId=youtube_id,
            publishedAfter=f"{date}T00:00:00Z",
            publishedBefore=f"{date}T23:59:59Z",
            maxResults=50
        )
        response = request.execute()

        for item in response.get("items", []):
            video_id = item["id"].get("videoId")
            if not video_id:
                continue

            video_details = youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            ).execute()

            for video in video_details.get("items", []):
                # Convert publication time to local timezone
                published_at_utc = datetime.strptime(
                    video["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                )
                published_at_local = published_at_utc.astimezone(LOCAL_TIMEZONE)

                video_data = (
                    video["id"],
                    video["snippet"]["title"],
                    int(video["statistics"].get("viewCount", 0)),
                    int(video["statistics"].get("likeCount", 0)),
                    int(video["statistics"].get("commentCount", 0)),
                    published_at_local.strftime("%Y-%m-%d"),
                    published_at_local.strftime("%H:%M"),
                    video["snippet"].get("description", ""),
                    video["snippet"]["thumbnails"]["default"]["url"],
                    video["snippet"]["channelTitle"],
                    youtube_id
                )
                insert_video(video_data)

        print(f"Videos for {date} have been successfully stored in the database.")

    except Exception as e:
        print(f"An error occurred while fetching and storing videos: {e}")


def download_data(youtube_id):
    """
    Handles the downloading of video data for a user-defined time frame.
    """
    print("\nStarting data download process...")
    dates = select_time_frame()  # This should show the selection menu
    if dates:
        for date in dates:
            print(f"Downloading data for {date}...")
            fetch_and_store_videos(youtube_id, date)
        print("Download complete.")
        input("\nPress Enter to return to the main menu...")
        
    else:
        print("No valid dates selected. Returning to main menu.")
        input("\nPress Enter to return to the main menu...")



def generate_report(date):
    """
    Generates an Excel report of the top 10 videos for the given date.
    """
    # Fetch videos from the database
    active_channel = fetch_active_channel()
    if not active_channel:
        print("No active channel. Please configure a channel.")
        input("\nPress Enter to return to the main menu...")
        return

    youtube_id = active_channel[1]
    videos = fetch_videos_by_date(date, youtube_id)

    if videos:
        # Updated columns to match the data structure
        columns = ["ID", "Title", "Views", "Likes", "Comments", "Publication Date", "Publication Hour", "Description", "Thumbnail", "Channel", "YouTube ID"]
        df = pd.DataFrame(videos, columns=columns)
        df = df.sort_values(by="Views", ascending=False).head(5000) #expand this limit as much as you need

        file_name = f"top_videos_{date}.xlsx"
        df.to_excel(file_name, index=False)
        print(f"Report generated: {file_name}")
        input("\nPress Enter to return to the main menu...")        

    else:
        print("No videos found in the database for the specified date.")
        input("\nPress Enter to return to the main menu...") 

def generate_report_combined(dates):
    """
    Genera un solo Excel con TODOS los videos de los días en 'dates'.
    """
    active_channel = fetch_active_channel()
    if not active_channel:
        print("No active channel. Please configure a channel.")
        input("\nPress Enter to return to the main menu...")
        return

    youtube_id = active_channel[1]
    columns = ["ID", "Title", "Views", "Likes", "Comments",
               "Publication Date", "Publication Hour", "Description",
               "Thumbnail", "Channel", "YouTube ID"]

    frames = []
    for d in dates:
        vids = fetch_videos_by_date(d, youtube_id)
        if not vids:
            continue
        df = pd.DataFrame(vids, columns=columns)
        df["Query Date"] = d  # etiqueta opcional para saber de qué día vino
        frames.append(df)

    if not frames:
        print("No videos found in the database for the specified dates.")
        input("\nPress Enter to return to the main menu...")
        return

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(by="Views", ascending=False)

    start, end = min(dates), max(dates)
    file_name = f"top_videos_{start}_to_{end}.xlsx"
    combined.to_excel(file_name, index=False)
    print(f"Report generated: {file_name}")
    input("\nPress Enter to return to the main menu...")        
    


def configure_channel():
    """
    Manages channel configurations: add, change, delete, or set active channel.
    """
    while True:
        print("\nChannel Configuration Menu")
        print("1. Add New Channel")
        print("2. List All Channels")
        print("3. Set Active Channel")
        print("4. Delete a Channel")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            channel_id = input("Enter the new channel ID: ")
            youtube_id = input("Enter the YouTube ID: ")
            channel_name = input("Enter the channel name: ")
            insert_channel((channel_id, youtube_id, channel_name, 0))
            print(f"Channel '{channel_name}' added successfully.")

        elif choice == "2":
            channels = fetch_all_channels()
            if channels:
                print("\nChannels:")
                for idx, channel in enumerate(channels, start=1):
                    print(f"{idx}. {channel[2]} (ID: {channel[0]})")
            else:
                print("No channels found.")
                input("\nPress Enter to return to the main menu...")

        elif choice == "3":
            channels = fetch_all_channels()
            if channels:
                print("\nAvailable Channels:")
                for idx, channel in enumerate(channels, start=1):
                    print(f"{idx}. {channel[2]} (ID: {channel[0]})")
                selected = int(input("Select a channel by number: ")) - 1
                if 0 <= selected < len(channels):
                    set_active_channel(channels[selected][0])
                    print(f"Active channel set to: {channels[selected][2]}.")
                else:
                    print("Invalid selection.")
            else:
                print("No channels available. Please add a channel first.")
                input("\nPress Enter to return to the main menu...")

        elif choice == "4":
            channels = fetch_all_channels()
            if channels:
                print("\nAvailable Channels:")
                for idx, channel in enumerate(channels, start=1):
                    print(f"{idx}. {channel[2]} (ID: {channel[0]})")
                selected = int(input("Select a channel to delete by number: ")) - 1
                if 0 <= selected < len(channels):
                    channel_id = channels[selected][0]
                    delete_channel(channel_id)
                    print(f"Channel '{channels[selected][2]}' and its associated data have been deleted.")
                else:
                    print("Invalid selection.")
            else:
                print("No channels available to delete.")

        elif choice == "5":
            print("Exiting channel configuration.")
            break

        else:
            print("Invalid choice. Please try again.")

def display_today_top_videos():
    """
    Fetches and displays the top 10 videos from the day before, ranked by total views.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    active_channel = fetch_active_channel()

    # Ensure there's an active channel
    if not active_channel:
        print("\nNo active channel. Please configure a channel.")
        input("\nPress Enter to return to the main menu...")
        return

    youtube_id = active_channel[1]  # Fetch active channel's YouTube ID
    videos = fetch_videos_by_date(today, youtube_id)

    # Ensure videos exist for the day before 
    if not videos:
        print("\nNo data for today . Please download data first.")
        return

    # Sort videos by total views
    ranked_videos = sorted(videos, key=lambda x: x[2], reverse=True)  # x[2] is `views`

    # Display the top 10 videos
    print(f"\n \033[93mTop 10 Videos from TODAY by Total Views:\033[0m {today}")
    print()
    for idx, video in enumerate(ranked_videos[:10], start=1):
        print(f"{idx}. {video[1]} - \033[92m{video[2]} views\033[0m")  # video[1] is title, video[2] is views
    
    keywords = extract_keywords_from_titles_over_views(ranked_videos[:10])
    keyword_line = ", ".join([f"{word} ({freq})" for word, freq in keywords])
    print(f"\n\033[96mTrending Keywords: {keyword_line}\033[0m")

def display_day_before_top_videos():
    """
    Fetches and displays the top 10 videos from the day before, ranked by total views.
    """
    one_days_ago = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    active_channel = fetch_active_channel()

    # Ensure there's an active channel
    if not active_channel:
        print("\nNo active channel. Please configure a channel.")
        input("\nPress Enter to return to the main menu...")
        return

    youtube_id = active_channel[1]  # Fetch active channel's YouTube ID
    videos = fetch_videos_by_date(one_days_ago, youtube_id)

    # Ensure videos exist for the day before 
    if not videos:
        print("\nNo data for yesterday . Please download data first.")
        return

    # Sort videos by total views
    ranked_videos = sorted(videos, key=lambda x: x[2], reverse=True)  # x[2] is `views`

    # Display the top 10 videos
    print(f"\n \033[93mTop 10 Videos from Yesterday by Total Views: \033[0m{one_days_ago}")
    print()
    for idx, video in enumerate(ranked_videos[:10], start=1):
        print(f"{idx}. {video[1]} - \033[92m{video[2]} views\033[0m")  # video[1] is title, video[2] is views
    
    keywords = extract_keywords_from_titles_over_views(ranked_videos[:10])
    keyword_line = ", ".join([f"{word} ({freq})" for word, freq in keywords])
    print(f"\n\033[96mTrending Keywords: {keyword_line}\033[0m")

def display_day_before_yesterday_top_videos():
    """
    Fetches and displays the top 10 videos from the day before yesterday, ranked by total views.
    """
    two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    active_channel = fetch_active_channel()

    # Ensure there's an active channel
    if not active_channel:
        print("\nNo active channel. Please configure a channel.")
        return

    youtube_id = active_channel[1]  # Fetch active channel's YouTube ID
    videos = fetch_videos_by_date(two_days_ago, youtube_id)

    # Ensure videos exist for the day before yesterday
    if not videos:
        print("\nNo data for the day before yesterday. Please download data first.")
        return

    # Sort videos by total views
    ranked_videos = sorted(videos, key=lambda x: x[2], reverse=True)  # x[2] is `views`

    # Display the top 10 videos
    print(f"\n \033[93mTop 10 Videos from 2 days ago:\033[0m {two_days_ago}")
    print()
    for idx, video in enumerate(ranked_videos[:10], start=1):
        print(f"{idx}. {video[1]} - \033[92m{video[2]} views\033[0m")  # video[1] is title, video[2] is views
    keywords = extract_keywords_from_titles_over_views(ranked_videos[:10])
    keyword_line = ", ".join([f"{word} ({freq})" for word, freq in keywords])
    print(f"\n\033[96mTrending Keywords: {keyword_line}\033[0m")


def main():

    while True:

        os.system('cls' if os.name == 'nt' else 'clear')
            
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"\n📊 \033[91mWelcome to YouData! Today is\033[0m {today}.")

        active_channel = fetch_active_channel()
        if active_channel:
            print(f"\n🎥 Active Channel: \033[91m{active_channel[2]} \033[0m(YouTube ID: {active_channel[1]})")
        else:
            print("\nNo active channel. Please configure a channel.")

        display_today_top_videos()
        display_day_before_top_videos()
        display_day_before_yesterday_top_videos()

        print("\n \033[90m🤖 YouData - Main Menu\033[0m")
        print("\n1. Download Video Data")
        print("2. Consult Top Videos by Date")
        print("3. Generate Excel Report by Date")
        print("4. Change Channel Configuration")
        print("5. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            if active_channel:
                download_data(active_channel[1])
            else:
                print("No active channel. Please configure a channel first.")

        elif choice == "2":
            dates = select_time_frame()
            if dates:
                all_videos = []
                for date in dates:
                    videos = fetch_videos_by_date(date, active_channel[1])
                    if videos:
                        all_videos.extend(videos)

                if all_videos:
                    period_label = make_period_label(dates)
                    channel_name = active_channel[2] if active_channel else None
                    generate_table(all_videos, columns=[5, 1, 2], summary=True,
                                period_label=period_label, channel_name=channel_name)
                else:
                    print("No videos found for the selected dates.")
            else:
                print("No valid date selected.")

        elif choice == "3":
            dates = select_time_frame()
            if dates:
                if len(dates) == 1:
                    generate_report(dates[0])           # comportamiento actual (un día)
                else:
                    generate_report_combined(dates)     # nuevo: un solo Excel combinado
            else:
                print("No valid dates selected.")

        elif choice == "4":
            configure_channel()

        elif choice == "5":
            print("Exiting YouData. Goodbye!")
            break

        else:
            print("Invalid choice. Please select an option from the menu.")

if __name__ == "__main__":
    main()
