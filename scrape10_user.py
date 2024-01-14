import httpx
import asyncio
import json
import os

headers = {
        "X-RapidAPI-Key": "d2215a5c9cmsh4da2e98a3219b6ap180b11jsn8540f2e601cf",
        "X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
    }
timeout = 20.0  # You can adjust this value based on your needs

async def async_request(url, headers, params):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params, timeout=timeout)
        return response.json()

async def search_user_by_keyword(keyword, count=1):
    url = "https://tokapi-mobile-version.p.rapidapi.com/v1/search/user"
    querystring = {"keyword": keyword, "count": str(count)}
    response = await async_request(url, headers, querystring)  # Assuming you're using the global HEADERS

    try:
        uid = response['user_list'][0]['user_info']['uid']
        return uid
    except (KeyError, IndexError):
        print("Failed to extract UID from response.")
        return None


    # return await async_request(url, headers, querystring)

async def get_user_posts(user_id, offset=0, count=20, region="GB", with_pinned_posts="1"):
    url = f"https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/{user_id}/posts"
    querystring = {
        "offset": str(offset),
        "count": str(count),
        "region": region,
        "with_pinned_posts": with_pinned_posts
    }
    return await async_request(url, headers, querystring)

def avg_views(user_info):
    # Calculate average views (removing outliers) for the user
    views = [post.get('views', 0) for post in user_info.get('posts_info', [])]
    views.sort()
    median_index = len(views) // 4
    median_views = sum(views[median_index:-median_index]) / (len(views) // 2) if len(views) > 0 else 0
    user_info['user_profile']['average_views_no_outliers'] = int(median_views)



def extract_user_data(data):
    # Extracting user information from the first post
    post = data['aweme_list'][0]
    user_info = {
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

    # Extracting all posts' information
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

    # Update the user_info with the posts_info
    user_info['posts_info'] = posts_info

    # Call avg_views function to calculate average views and add to the user_info
    avg_views(user_info)

    return user_info
    # # Write the data to a JSON file
    # with open("user_info.json", "w") as file:
    #     json.dump(user_info, file, ensure_ascii=False, indent=4)

    # print("User information and posts written to user_info.json")
