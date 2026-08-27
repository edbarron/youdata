import sqlite3
import os


DB_PATH = "/home/server-ed/apps/youdata/youdata.db"

print("USING db_utils FROM:", __file__)
print("DB_PATH IS:", DB_PATH)

def insert_video(video_data):
    """
    video_data: Tuple (id, name, views, likes, comments, publication_date, publication_hour, description, thumbnail, channel, youtube_id)
    Actualiza métricas si el video ya existe.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO videos (id, name, views, likes, comments, publication_date, publication_hour, description, thumbnail, channel, youtube_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        name = COALESCE(excluded.name, videos.name),
        views = excluded.views,
        likes = excluded.likes,
        comments = excluded.comments,
        publication_date = COALESCE(excluded.publication_date, videos.publication_date),
        publication_hour = COALESCE(excluded.publication_hour, videos.publication_hour),
        description = COALESCE(excluded.description, videos.description),
        thumbnail = COALESCE(excluded.thumbnail, videos.thumbnail),
        channel = COALESCE(excluded.channel, videos.channel),
        youtube_id = COALESCE(excluded.youtube_id, videos.youtube_id)
    ''', video_data)
    conn.commit()
    conn.close()

def fetch_videos_by_date(publication_date, youtube_id):
    """
    Fetches all videos published on a specific date for the active channel.
    publication_date: Date in the format "YYYY-MM-DD".
    youtube_id: YouTube ID of the active channel.
    Returns a list of tuples containing video data.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM videos 
    WHERE publication_date = ? AND youtube_id = ?
    ''', (publication_date, youtube_id))
    results = cursor.fetchall()
    conn.close()
    return results

def fetch_all_videos(youtube_id):
    """
    Fetches all video records for the active channel.
    youtube_id: YouTube ID of the active channel.
    Returns a list of tuples containing all video data.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM videos 
    WHERE youtube_id = ?
    ''', (youtube_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def insert_channel(channel_data):
    """
    Inserts a channel record into the database.
    channel_data: Tuple (channel_id, youtube_id, channel_name, is_active)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO channels (channel_id, youtube_id, channel_name, is_active)
    VALUES (?, ?, ?, ?)
    ''', channel_data)
    conn.commit()
    conn.close()

def fetch_all_channels():
    """
    Fetches all channel records from the database.
    Returns a list of tuples containing channel data.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM channels')
    results = cursor.fetchall()
    conn.close()
    return results

def set_active_channel(channel_id):
    """
    Sets the active channel by updating the is_active flag.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE channels SET is_active = 0')  # Reset all channels to inactive
    cursor.execute('UPDATE channels SET is_active = 1 WHERE channel_id = ?', (channel_id,))
    conn.commit()
    conn.close()

def fetch_active_channel():
    """
    Fetches the currently active channel.
    Returns a tuple containing the active channel's data or None if no active channel exists.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM channels WHERE is_active = 1 LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    return result

def delete_channel(channel_id):
    """
    Deletes a channel and all associated videos from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Delete videos associated with the channel
        cursor.execute('DELETE FROM videos WHERE youtube_id = (SELECT youtube_id FROM channels WHERE channel_id = ?)', (channel_id,))
        # Delete the channel itself
        cursor.execute('DELETE FROM channels WHERE channel_id = ?', (channel_id,))
        conn.commit()
        print("Channel and its associated data deleted successfully.")
    except Exception as e:
        print(f"An error occurred while deleting the channel: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    # Example usage of the functions
    sample_video = ("12345", "Sample Video", 1000, 100, 50, "2025-01-08", "12:00", "This is a description", "https://example.com/thumbnail.jpg", "Sample Channel", "UC123456789")
    insert_video(sample_video)

    sample_channel = ("1", "UC123456789", "Example Channel", 1)
    insert_channel(sample_channel)

    print("Videos on 2025-01-08:", fetch_videos_by_date("2025-01-08", "UC123456789"))
    print("All videos for channel 'UC123456789':", fetch_all_videos("UC123456789"))
    print("All channels:", fetch_all_channels())
    print("Active channel:", fetch_active_channel())
