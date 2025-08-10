from instacapture import InstaStory, InstaPost
import os

def download_media(username, cookies, download_path, log_callback, progress_callback, cancel_event, download_stories=True, download_posts=True):
    """
    Downloads stories and/or posts for a given Instagram username.

    Args:
        username (str): The Instagram username.
        cookies (dict): The cookies for authentication.
        download_path (str): The path to save the downloaded media.
        log_callback (function): A function to call for logging progress.
        progress_callback (function): A function to call to update progress (0-100).
        cancel_event (threading.Event): An event to signal cancellation.
        download_stories (bool): Whether to download stories.
        download_posts (bool): Whether to download posts.
    """
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    original_cwd = os.getcwd()
    os.chdir(download_path)

    try:
        log_callback(f"Starting download for @{username}...")
        progress_callback(0)

        if cancel_event.is_set():
            log_callback(f"Cancelled before starting download for @{username}.")
            return

        total_steps = int(download_stories) + int(download_posts)
        current_step = 0

        # Story download
        if download_stories:
            if cancel_event.is_set():
                log_callback(f"Download cancelled for @{username}.")
                return
            try:
                log_callback(f"Downloading stories for @{username}...")
                story_obj = InstaStory()
                story_obj.cookies = cookies
                story_obj.username = username
                story_obj.story_download()
                log_callback(f"Successfully downloaded stories for @{username}.")
            except Exception as e:
                log_callback(f"Could not download stories for @{username}: {e}")
            current_step += 1
            progress_callback(int((current_step / total_steps) * 100))

        # Post download
        if download_posts:
            if cancel_event.is_set():
                log_callback(f"Download cancelled for @{username}.")
                return
            try:
                log_callback(f"Downloading posts for @{username}...")
                post_obj = InstaPost()
                post_obj.cookies = cookies
                post_obj.reel_id = username
                post_obj.media_download()
                log_callback(f"Successfully downloaded posts for @{username}.")
            except Exception as e:
                log_callback(f"Could not download posts for @{username}: {e}")
            current_step += 1
            progress_callback(int((current_step / total_steps) * 100))

    finally:
        os.chdir(original_cwd)
        progress_callback(100) # Ensure it ends at 100
