from dotenv import load_dotenv
import csv
import os
import json


# from flask import Flask, request, render_template, Response, stream_with_context, jsonify, send_file

from scrape4_user_posts import scrape_user_posts
# from scrape5 import remove_users
# from scrape6_insta import update_instagram_info
# from scrape7_emails import update_user_info_with_emails
# from scrape8_consolidate_emails import consolidate_emails
# from scrape9_mongo import insert_user_data_to_mongodb
import asyncio


def load_user_info_from_csv(csv_file_path):
    user_info_list = []
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            user_info = {
                'user_profile': {
                    'author_uid': row['author_uid'],
                    'name': row.get('name', ''),
                    'username': row.get('username', '')
                }
            }
            user_info_list.append(user_info)
    return user_info_list

def save_temp_data(step, data):
    with open(f'Temp Data/temp_data_{step}.json', 'w') as json_file:
        json.dump(data, json_file)


async def call_tiktok_user_api(username_list):
    user_info = username_list
    scraped_users = await scrape_user_posts(user_info)
    save_temp_data('2_user_profiles', scraped_users)  # Save data after TikTok Scraping
    yield f"Step 1 complete!...<br>" 

async def main():
    username_list = load_user_info_from_csv('username_list.csv')
    print(username_list)  # Print the first 5 entries for verification
    async for message in call_tiktok_user_api(username_list):
        print(message)

# Run the main function using the asyncio event loop
asyncio.run(main())





# def generate(username_list):
#     try:
#         # Creating an asynchronous event loop using asyncio
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         yield f"Step 1: Scraping {len(username_list)} User Posts Data...<br>"
#         user_info = scrape_user_posts(username_list)
#         save_temp_data('2_user_profiles', user_info)  # Save data after TikTok Scraping
#         users_with_ins_id = [user for user in user_info if user.get("social_media", {}).get("ins_id")]
#         yield f"Step 1 complete!...<br>" 
#         return user_info
#     except Exception as e:
#         print(e)
#         yield f"Error: {e}...<br>" 
#         return None

