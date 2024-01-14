import os
import httpx
import asyncio
import logging
from ratelimit import limits, sleep_and_retry
from asyncio import Lock

# API endpoint and headers
url_base = "https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/{}/posts"
querystring = {"count": 5, "with_pinned_posts": "1"}
headers = {
    "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
    "X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
}

# Constants for retry mechanism
max_retries = 3
retry_delay = 2

# Create a lock and counter at module-level or inside a class if you're using one
lock = Lock()
scraped_counter = 0


@sleep_and_retry
@limits(calls=400, period=60)
async def process_user_info(user, index, user_info):
    author_user_id = user['user_profile']['author_uid']
    url = url_base.format(author_user_id)
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=querystring)
                data = response.json()

            # Extracting user information from the return JSON data and updating user_info list (info coming from first post)
            post = data['aweme_list'][0]  # Assuming the response contains data for one post
            new_user_info = {
                'user_profile': {
                    'name': post['author'].get('nickname', ''),
                    'author_uid': post.get('author_user_id', ''),
                    'username': post['author'].get('unique_id', ''),
                    'tiktok_followers': post['author'].get('follower_count', ''),
                    'tiktok_following': post['author'].get('following_count', ''),
                    'tiktok_bio': post['author'].get('signature', ''),
                    'country': post['author'].get('region', ''),
                    'tiktok_email': post['author'].get('has_email', ''),
                    'google': post['author'].get('google_account', ''),
                },
                'social_media': {
                    'ins_id': post['author'].get('ins_id', ''),
                    'yt_id': post['author'].get('youtube_channel_id', ''),
                    'youtube_name': post['author'].get('youtube_channel_title', ''),
                    'twitter_id': post['author'].get('twitter_id', ''),
                    'twitter_name': post['author'].get('twitter_name', ''),
                },
            }
            user_info[index].update(new_user_info)

            posts_info = []
            for post in data['aweme_list']:
                post_info = {
                    'post_uid': post['statistics'].get('aweme_id', ''),
                    'create_time': post.get('create_time', ''),
                    'description': post.get('desc', ''),
                    'desc_language': post.get('desc_language', ''),
                    'advertisement': post.get('is_ads', ''),
                    'region': post.get('region', ''),
                    'url': post.get('share_url', ''),
                    'saved': post['statistics'].get('collect_count', ''),
                    'comments': post['statistics'].get('comment_count', ''),
                    'likes': post['statistics'].get('digg_count', ''),
                    'downloaded': post['statistics'].get('download_count', ''),
                    'views': post['statistics'].get('play_count', ''),
                    'shares': post['statistics'].get('share_count', ''),
                    'shares_whatsapp': post['statistics'].get('whatsapp_share_count', ''),
                }
                posts_info.append(post_info)

            # Update the existing user_info with the posts_info for the current user
            user_info[index]['posts_info'] = posts_info

            # Acquire the lock to ensure exclusive access to the shared counter
            async with lock:
                global scraped_counter
                scraped_counter += 1
                print(f"{scraped_counter}/{len(user_info)} TikTok Profiles Scraped")  # Print the progress log

            return user_info[index]
        
        except (httpx.ConnectTimeout, httpx.HTTPError) as e:
            if attempt < max_retries - 1:
                logging.warning(f"Error in attempt {attempt}, retrying: {str(e)}")
                await asyncio.sleep(retry_delay) # Delay before retrying
            else:
                logging.error(f"Max retries reached for user {author_user_id}: {str(e)}")
                return None

        except Exception as e:
            logging.error(f"An unexpected error occurred for user {author_user_id}: {str(e)}")
            return None


async def scrape_user_posts(user_info):
    tasks = [process_user_info(user, i, user_info) for i, user in enumerate(user_info)]
    await asyncio.gather(*tasks)

    return user_info
