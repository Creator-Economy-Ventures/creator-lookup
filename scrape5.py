import json
import logging

def remove_users(user_info):
    # Filter the user_info list to include only users with 50,000 or more TikTok followers
    filtered_user_info = []

    for user in user_info:
        try:
            # Accessing the 'tiktok_followers' key safely using the `get` method
            followers_count = user.get('user_profile', {}).get('tiktok_followers', 0)

            if followers_count >= 1000:
                filtered_user_info.append(user)
        except Exception as e:
            # Log the error along with the specific user data that caused it
            logging.error(f"Error processing user {user}: {str(e)}")

    #         # Generate a JSON file
    # with open('(Scraper Final)/user_info.json', 'w') as json_file:
    #     json.dump(filtered_user_info, json_file)

    return filtered_user_info

# Logging at the beginning of your script
# logging.basicConfig(level=logging.ERROR, filename='scrape5.log')
