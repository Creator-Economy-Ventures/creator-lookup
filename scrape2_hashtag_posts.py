import os
from ratelimit import limits, sleep_and_retry
import httpx
import asyncio
import logging
from asyncio import Lock

lock = Lock()
scraped_counter = 0

@sleep_and_retry
@limits(calls=300, period=60)
async def scrape_users(hashtag_uid, count):
    user_info = await get_all_hashtag_posts(hashtag_uid, count)
    return user_info

async def get_all_hashtag_posts(hashtag_uid, count):
    user_info = []
    cursor = 0

    while len(user_info) < count:
        new_info, next_cursor = await get_hashtag_posts(hashtag_uid, count, cursor)
        user_info.extend(new_info)

        if next_cursor is None:
            break

        cursor = next_cursor

    return user_info

async def get_hashtag_posts(hashtag_uid, count, cursor):
    url = f"https://tokapi-mobile-version.p.rapidapi.com/v1/hashtag/posts/{hashtag_uid}"

    querystring = {"count": count, "offset": cursor}

    headers = {
        "X-RapidAPI-Key": os.getenv('RAPIDAPI_KEY'),
        "X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
    }

    max_retries = 3
    retry_delay = 2

    global scraped_counter  # Declare the global variable


    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=querystring)
                data = response.json()

            user_info = []

            for post in data['aweme_list']:
                tiktok_user_info = {
                    'user_profile': {
                    'username': post['author'].get('unique_id', ''),
                    'author_uid': post.get('author_user_id', ''),
                    },
                    'original_post': {
                    'post_id': post.get('aweme_id', ''),
                    'description': post.get('desc', ''),
                    'post_date': post.get('create_time', ''),
                    'share_url': post.get('share_url', ''),

                    }
                }
                user_info.append(tiktok_user_info)

                async with lock:
                    scraped_counter += 1
                    print(f"{scraped_counter}/{count} TikTok Usernames Scraped (From Hashtag)")  # Print the progress log


            next_cursor = None if data['has_more'] == 0 else data['cursor']


            return user_info, next_cursor
        
        except (httpx.ConnectTimeout, httpx.HTTPError) as e:
            if attempt < max_retries - 1:
                logging.warning(f"Error in attempt {attempt}, retrying: {str(e)}")
                await asyncio.sleep(retry_delay)
            else:
                logging.error(f"Max retries reached for hashtag {hashtag_uid}: {str(e)}")
                return [], None

        except Exception as e:
            logging.error(f"An unexpected error occurred for hashtag {hashtag_uid}: {str(e)}")
            return [], None
