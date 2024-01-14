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
import asyncio


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def save_temp_data(step, data):
    with open(f'(Scraper Final)/Temp Data/temp_data_{step}.json', 'w') as json_file:
        json.dump(data, json_file)

@app.route('/step1', methods=['POST'])
def step1():
    hashtag = request.json.get('hashtag')
    hashtag_uid = scrape_hashtag(hashtag)
    return jsonify(hashtag_uid=hashtag_uid)

@app.route('/step2', methods=['POST'])
def step2():
    hashtag_uid = request.json.get('hashtag_uid')
    count = request.json.get('count')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    user_info = loop.run_until_complete(scrape_users(hashtag_uid, count))
    save_temp_data('1_user_uid', user_info)
    return jsonify(user_info=user_info)

@app.route('/step3', methods=['POST'])
def step3():
    user_info = request.json.get('user_info')
    user_info, duplicates_removed = remove_duplicates(user_info)
    return jsonify(user_info=user_info, duplicates_removed=duplicates_removed)

@app.route('/step4', methods=['POST'])
def step4():
    user_info = request.json.get('user_info')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    user_info = loop.run_until_complete(scrape_user_posts(user_info))
    save_temp_data('2_user_profiles', user_info)
    return jsonify(user_info=user_info)

@app.route('/step5', methods=['POST'])
def step5():
    user_info = request.json.get('user_info')
    user_info = remove_users(user_info)
    return jsonify(user_info=user_info)

@app.route('/step6', methods=['POST'])
def step6():
    user_info = request.json.get('user_info')
    asyncio.run(update_instagram_info(user_info))
    return jsonify(user_info=user_info)

@app.route('/step7', methods=['POST'])
def step7():
    user_info = request.json.get('user_info')
    user_info = update_user_info_with_emails(user_info)
    return jsonify(user_info=user_info)

@app.route('/step8', methods=['POST'])
def step8():
    user_info = request.json.get('user_info')
    user_info = consolidate_emails(user_info)
    save_temp_data('3_user_profiles_ig', user_info)
    return jsonify(user_info=user_info)

@app.route('/step9', methods=['POST'])
def step9():
    user_info = request.json.get('user_info')
    hashtag = request.json.get('hashtag')
    # Code to generate CSV
    return jsonify(message="CSV generated successfully")



@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    hashtag = request.json.get('hashtag')
    count = request.json.get('count')

    try:
        # Step 1
        hashtag_uid = step1().json.get('hashtag_uid')

        # Step 2
        user_info = step2().json.get('user_info')

        # Step 3
        user_info, _ = step3().json.get('user_info')

        # Step 4
        user_info = step4().json.get('user_info')

        # Step 5
        user_info = step5().json.get('user_info')

        # Step 6
        user_info = step6().json.get('user_info')

        # Step 7
        user_info = step7().json.get('user_info')

        # Step 8
        user_info = step8().json.get('user_info')

        # Step 9
        step9().json.get('message')

        return jsonify(status="success", message="Scraping process completed!")

    except Exception as e:
        # Log the exception for debugging
        print(str(e))

        # Return an error response
        return jsonify(status="error", message="An error occurred during the scraping process.")








# ============================


def generate(hashtag, count):
    # Creating an asynchronous event loop using asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield f"Step 1: Scraping UID for #{hashtag}...<br>"
    hashtag_uid = scrape_hashtag(hashtag)
    yield f"Step 1 complete! Step 2: Scraping Users from #{hashtag} UID: {hashtag_uid}...<br>"

    user_info = loop.run_until_complete(scrape_users(hashtag_uid, count))

    yield f"Step 2 complete ({len(user_info)} Users Collected)! Step 3: Removing Duplicates...<br>"
    user_info, duplicates_removed = remove_duplicates(user_info)
    save_temp_data('1_user_uid', user_info)  # Save data after Hashtag Scraping

    yield f"Step 3 complete ({duplicates_removed} Duplicates Removed)! Step 4: Scraping {len(user_info)} User Posts Data...<br>"
    user_info = loop.run_until_complete(scrape_user_posts(user_info))
    save_temp_data('2_user_profiles', user_info)  # Save data after TikTok Scraping

    users_with_ins_id = [user for user in user_info if user.get("social_media", {}).get("ins_id")]
    yield f"Step 4 complete! Step 5: Finding Users With Instagram ({len(users_with_ins_id)} found)...<br>"
    user_info = remove_users(user_info)

    yield "Step 5 complete! Step 6: Scraping User Instagram Info...<br>"
    asyncio.run(update_instagram_info(user_info))

    yield "Step 6 complete! Step 7: Finding Emails from TikTok/Instagram Bio...<br>"
    user_info = update_user_info_with_emails(user_info)

    tt_emails = [user for user in user_info if user.get("user_profile", {}).get("tiktok_emails")]
    ig_emails = [user for user in user_info if user.get("user_profile", {}).get("instagram_emails")]
    yield f"Step 7 complete (Emails Found: {len(tt_emails)} TikTok & {len(ig_emails)} Instagram)! Step 8: Consolodating Emails...<br>"
    user_info = consolidate_emails(user_info)
    save_temp_data('3_user_profiles_ig', user_info)  # Save data after Instagram scraping

    email_total = [user for user in user_info if user.get("user_profile", {}).get("email")]
    yield f"Step 8 complete! Step 9: {len(email_total)} Emails Found! Generating csv...<br>"

    # Generate a CSV file
    with open('(Scraper Final)/user_info.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
                'Name', 
                'Email',
                'TikTok Email',
                'TikTok Email (bio)',
                'Instagram Email',
                'Instagram Email (bio)',
                'TikTok Username', 
                'Author UID',
                'TikTok Followers',
                'TikTok Bio',
                'Country', 
                'Instagram Username', 
                'Instagram Followers', 
                'Instagram Bio', 
                f'#{hashtag} Post Link'])
        for user in user_info:
            writer.writerow([
                    user['user_profile'].get('name', 'n/a'),
                    user['user_profile'].get('email', 'n/a'),
                    user['user_profile'].get('tiktok_email', 'n/a'),
                    user['user_profile'].get('tiktok_emails', ['n/a'])[0],
                    user['user_profile'].get('instagram_email', 'n/a'),
                    user['user_profile'].get('instagram_emails', ['n/a'])[0],
                    user['user_profile'].get('username', 'n/a'), 
                    user['user_profile'].get('author_uid', 'n/a'),
                    user['user_profile'].get('tiktok_followers', 'n/a'),
                    user['user_profile'].get('tiktok_bio', 'n/a'),
                    user['user_profile'].get('country', 'n/a'),
                    user['social_media'].get('ins_id', 'n/a'),
                    user['user_profile'].get('instagram_followers', 'n/a'),
                    user['user_profile'].get('instagram_bio', 'n/a'),
                    user['original_post'].get('share_url', 'n/a')])

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

