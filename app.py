from dotenv import load_dotenv
import os
import csv
import json
from flask import Flask, request, render_template, Response, stream_with_context, jsonify, send_file
from scrape1_hashtag_uid import scrape_hashtag
from scrape2_hashtag_posts import scrape_users
from scrape3_remove_duplicates import remove_duplicates
from scrape4_user_posts import scrape_user_posts
from scrape5 import remove_users
from scrape6_insta import update_instagram_info
from scrape7_emails import update_user_info_with_emails
from scrape8_consolidate_emails import consolidate_emails
from scrape9_mongo import insert_user_data_to_mongodb
import asyncio



# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def save_temp_data(step, data):
    with open(f'Temp Data/temp_data_{step}.json', 'w') as json_file:
        json.dump(data, json_file)


def generate(hashtag, count):
    # Creating an asynchronous event loop using asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield f"Step 1: Scraping UID for #{hashtag}...<br>"
    hashtag_uid = scrape_hashtag(hashtag)
    yield f"Step 1 complete!...<br>" 

    yield f"Step 2: Scraping Users from #{hashtag} UID: {hashtag_uid}...<br>"
    user_info = loop.run_until_complete(scrape_users(hashtag_uid, count))
    for user in user_info:
        user['original_post']['original_hashtag'] = hashtag
    yield f"Step 2 complete ({len(user_info)} Users Collected)!...<br>" 
    
    yield f"Step 3: Removing Duplicates...<br>"
    user_info, duplicates_removed = remove_duplicates(user_info)
    save_temp_data('1_user_uid', user_info)  # Save data after Hashtag Scraping
    yield f"Step 3 complete ({duplicates_removed} Duplicates Removed)!...<br>" 
    
    yield f"Step 4: Scraping {len(user_info)} User Posts Data...<br>"
    user_info = loop.run_until_complete(scrape_user_posts(user_info))
    save_temp_data('2_user_profiles', user_info)  # Save data after TikTok Scraping
    users_with_ins_id = [user for user in user_info if user.get("social_media", {}).get("ins_id")]
    yield f"Step 4 complete!...<br>" 

    yield f"Step 5: Finding Users With Instagram ({len(users_with_ins_id)} found)...<br>"
    user_info = remove_users(user_info)
    save_temp_data('3_user_profiles_50k', user_info)  # Save data after TikTok Scraping
    yield "Step 5 complete!...<br>" 

    yield f"Step 6: Scraping User Instagram Info...<br>"
    asyncio.run(update_instagram_info(user_info))
    yield "Step 6 complete!...<br>"

    yield f"Step 7: Finding Emails from TikTok/Instagram Bio...<br>"
    user_info = update_user_info_with_emails(user_info)
    tt_emails = [user for user in user_info if user.get("user_profile", {}).get("tiktok_emails")]
    ig_emails = [user for user in user_info if user.get("user_profile", {}).get("instagram_emails")]
    yield f"Step 7 complete (Emails Found: {len(tt_emails)} TikTok & {len(ig_emails)} Instagram)!...<br>" 

    yield f"Step 8: Consolodating Emails...<br>"
    user_info = consolidate_emails(user_info)
    save_temp_data('3_user_profiles_ig', user_info)  # Save data after Instagram scraping
    email_total = [user for user in user_info if user.get("user_profile", {}).get("email")]
    yield f"Step 8 complete! {len(email_total)} Emails Found<br>"


    yield f"Step 9: Saving user information to MongoDB...<br>"
    uri = "mongodb+srv://jason:jason@social-scraper.1stgz.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
    new_users_added, total_unique_users, updated_users = insert_user_data_to_mongodb(uri, 'master_db', 'user_list', user_info)
    yield f"Step 9 complete!<br>"
    yield f"{new_users_added} new profiles information have been added to MongoDB.<br>"
    yield f"{updated_users} existing profiles have been updated in MongoDB.<br>"
    yield f"Total unique users in master database: {total_unique_users}.<br>"


    # Generate a CSV file
    with open('user_info.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
                'Name', 
                'Email',
                'Original #',
                # 'TikTok Email',
                # 'TikTok Email (bio)',
                # 'Instagram Email',
                # 'Instagram Email (bio)',
                'Country', 
                'TikTok Username', 
                'TikTok Followers',
                'TikTok Bio',
                'Instagram Username', 
                'Instagram Followers', 
                'Instagram Bio', 
                'Youtube Name',
                f'#{hashtag} Post Link',
                'Author UID',])

        for user in user_info:
            writer.writerow([
                    user['user_profile'].get('name', 'n/a'),
                    user['user_profile'].get('email', 'n/a'),
                    user['original_post'].get('original_hashtag', 'n/a'),
                    # user['user_profile'].get('tiktok_email', 'n/a'),
                    # user['user_profile'].get('tiktok_emails', ['n/a'])[0],
                    # user['user_profile'].get('instagram_email', 'n/a'),
                    # user['user_profile'].get('instagram_emails', ['n/a'])[0],
                    user['user_profile'].get('country', 'n/a'),
                    user['user_profile'].get('username', 'n/a'), 
                    user['user_profile'].get('tiktok_followers', 'n/a'),
                    user['user_profile'].get('tiktok_bio', 'n/a'),
                    user['social_media'].get('ins_id', 'n/a'),
                    user['user_profile'].get('instagram_followers', 'n/a'),
                    user['user_profile'].get('instagram_bio', 'n/a'),
                    user['social_media'].get('youtube_name', 'n/a'),
                    user['original_post'].get('share_url', 'n/a'),
                    user['user_profile'].get('author_uid', 'n/a')])


    yield "Scraping process completed!"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress', methods=['POST'])
def progress():
    hashtag = request.form.get('hashtag')
    count = int(request.form.get('count'))
    return Response(generate(hashtag, count), content_type='text/html')


@app.route('/download')
def download():
    return send_file('user_info.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

