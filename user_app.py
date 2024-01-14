# user_app.py
from flask import Flask, render_template, request, jsonify, send_file
import asyncio
from scrape10_user import search_user_by_keyword, get_user_posts, extract_user_data  # importing functions from scrape10.py
import re
import csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('user_index.html')


@app.route('/search', methods=['POST'])
def search():
    usernames = request.form.get('usernames', '').strip()

    # Split usernames either by newline or comma
    usernames_list = [name.strip() for name in re.split(r'[\n,]+', usernames) if name.strip()]

    # Placeholder list to store results from scraping each user
    results = []
    # Since you're using asynchronous functions in `scrape10_user.py`, 
    # you will need to create an event loop to run each of them synchronously within this function.
    # Normally, you would use async functions all the way, but Flask isn't natively async-friendly.
    # You'll need to create an event loop for each user:
    for username in usernames_list:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Use the search_user_by_keyword() function from scrape10_user.py
            uid = loop.run_until_complete(search_user_by_keyword(username))
            if uid:
                user_posts = loop.run_until_complete(get_user_posts(uid))
                # Extract the user info from the posts
                user_info = extract_user_data(user_posts)
                results.append(user_info)
        finally:
            loop.close()
    
    # Generate the CSV
    with open('Scraper_Final/user_info.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Name', 
            # 'Email', 
            'Country', 
            'TikTok Username', 
            'TikTok Link', 
            'TikTok Followers', 
            'TikTok Bio',
            'Instagram Username', 
            # 'Instagram Followers', 
            # 'Instagram Bio', 
            'Youtube Name', 
            'Author UID',
            'AVG Views',
            'AVG Views (no outliers)'])

        for user in results:
            tiktok_username = user['user_profile'].get('username', 'n/a')
        
            # Generate the TikTok Link
            tiktok_link = f'https://www.tiktok.com/@{tiktok_username}' if tiktok_username != 'n/a' else 'n/a'

            writer.writerow([
                user['user_profile'].get('name', 'n/a'),
                # user['user_profile'].get('email', 'n/a'),
                user['user_profile'].get('country', 'n/a'),
                tiktok_username,
                tiktok_link,
                user['user_profile'].get('tiktok_followers', 'n/a'),
                user['user_profile'].get('tiktok_bio', 'n/a'),
                user['social_media'].get('ins_id', 'n/a'),
                # user['user_profile'].get('instagram_followers', 'n/a'),
                # user['user_profile'].get('instagram_bio', 'n/a'),
                user['social_media'].get('youtube_name', 'n/a'),
                user['user_profile'].get('author_uid', 'n/a'),
                user['user_profile'].get('average_views', 'n/a'),
                user['user_profile'].get('average_views_no_outliers', 'n/a')
            ])

    return f"Scraping completed for {len(results)} users and data written to CSV!"


    # Return a response that will be displayed in the iframe.
    # You can render it to an HTML template, or simply return a string message.
    # For simplicity, returning a string message:
    # return f"Scraping completed for {len(results)} users!"

@app.route('/download')
def download():
    return send_file('user_info.csv', as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
