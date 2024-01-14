import os
import requests
import json

def update_instagram_info(user_info):
    # Step 1: Filter users with Instagram ID
    users_with_ins_id = [user for user in user_info if user.get("social_media", {}).get("ins_id")]

    # Step 2: Call Instagram API for each user
    results = []
    for user in users_with_ins_id:
        ins_id = user['social_media']['ins_id']
        url = "https://instagram-scraper-2022.p.rapidapi.com/ig/info_username/"
        querystring = {"user": ins_id}
        headers = {
            "X-RapidAPI-Key": os.getenv('INSTAGRAM_RAPIDAPI_KEY'),
            "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        results.append(response.json())

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
    # Update JSON file for IG Info
    with open('Scraper_Final/user_info_ig.json', 'w') as json_file:
        json.dump(users_with_ins_id, json_file)

    # Step 4: Update the original user_info list
    for user_with_ins_id in users_with_ins_id:
        author_uid = user_with_ins_id['user_profile']['author_uid']
        for user in user_info:
            if user['user_profile']['author_uid'] == author_uid:
                user.update(user_with_ins_id)
                break

    return user_info


