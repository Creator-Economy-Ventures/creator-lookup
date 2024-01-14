import os
import json

def avg_views(user_info):
    # Calculate average views for each user
    for user in user_info: 
        total_views = 0
        total_posts = len(user.get('posts_info', []))
        
        for post in user.get('posts_info', []):
            total_views += post.get('views', 0)
        
        average_views = total_views / total_posts
        user['user_profile']['average_views'] = int(average_views)

    # Calculate average views (removing outliers) for each user
    for user in user_info:
        views = [post.get('views', 0) for post in user.get('posts_info', [])]
        views.sort()
        median_index = len(views) // 4
        median_views = sum(views[median_index:-median_index]) / (len(views) // 2)
        user['user_profile']['average_views_no_outliers'] = int(median_views)


    # Save the user_info list as a JSON file
    json_filename = "user_info_with_views.json"
    with open(json_filename, 'w') as file:
        json.dump(user_info, file, indent=2)
