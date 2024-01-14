import os
import json
import httpx
from httpx import TimeoutException
import asyncio
from ratelimit import limits, sleep_and_retry
from asyncio import Lock


# Define the rate limit: 100 calls per 60 seconds
RATE_LIMIT_CALLS = 50
RATE_LIMIT_PERIOD = 60


lock = Lock()
scraped_counter = 0

@sleep_and_retry
@limits(calls=RATE_LIMIT_CALLS, period=RATE_LIMIT_PERIOD)
async def fetch_instagram_info(ins_id, session, total_count):
    global scraped_counter

    url = "https://instagram-scraper-2022.p.rapidapi.com/ig/info_username/"
    querystring = {"user": ins_id}
    headers = {
        "X-RapidAPI-Key": os.getenv('INSTAGRAM_RAPIDAPI_KEY'),
        "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com"
    }

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            response = await session.get(url, headers=headers, params=querystring)

            # Incrementing and logging the counter inside the lock
            async with lock:
                scraped_counter += 1
                print(f"{scraped_counter}/{total_count} Instagram Profiles Scraped")  # Print the progress log

            return response.json()
        except TimeoutException:
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay) # Delay before retrying
            else:
                raise

        except Exception as e:
            # Handle other unexpected exceptions
            print(f"An unexpected error occurred for Instagram user {ins_id}: {str(e)}")
            return None



async def update_instagram_info(user_info):
    # Step 1: Filter users with Instagram ID
    users_with_ins_id = [user for user in user_info if user.get("social_media", {}).get("ins_id")]

    # Step 2: Call Instagram API for each user
    total_count = len(users_with_ins_id)
    async with httpx.AsyncClient(timeout=20.0) as session:
        tasks = [fetch_instagram_info(user['social_media']['ins_id'], session, total_count) for user in users_with_ins_id]
        results = await asyncio.gather(*tasks)

    # Step 3: Update users_with_ins_id with Instagram information
    for index, result in enumerate(results):
        instagram_info = result.get('user', {})
        users_with_ins_id[index]['user_profile'].update({
            'instagram_bio': instagram_info.get('biography'),
            'instagram_email': instagram_info.get('public_email'),
            'instagram_followers': instagram_info.get('follower_count'),
            'instagram_following': instagram_info.get('following_count'),
            'instagram_username': instagram_info.get('username'),
            'full_name': instagram_info.get('full_name')
        })

    # Update JSON file for IG Info (REMOVE FOR FULL PRODUCTION)
    with open('user_info_ig.json', 'w') as json_file:
        json.dump(users_with_ins_id, json_file)

    # Step 4: Update the original user_info list
    for user_with_ins_id in users_with_ins_id:
        author_uid = user_with_ins_id['user_profile']['author_uid']
        for user in user_info:
            if user['user_profile']['author_uid'] == author_uid:
                user.update(user_with_ins_id)
                break

    return user_info





