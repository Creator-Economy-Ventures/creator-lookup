# import json
# from scrape2_hashtag_posts import scrape_users

# def remove_duplicates(hashtag_uid, count):
#     # Get the user_info data
#     user_info = scrape_users(hashtag_uid, count)

#     # Create a dict to keep track of seen author_ids
#     seen_author_ids = {}

#     # Counter for duplicates
#     duplicate_count = 0

#     # Iterate over users in user_info
#     for i in reversed(range(len(user_info))):  # iterate in reverse to safely delete elements
#         user = user_info[i]
#         author_id = user['user_profile']['author_uid']  # extract author_id
#         if author_id in seen_author_ids:
#             # if we've already seen this author_id, remove this user and increment duplicate counter
#             del user_info[i]
#             duplicate_count += 1
#             continue  # Skip the rest of this loop iteration because the user is a duplicate

#         # if we haven't seen this author_id, add it to seen_author_ids
#         seen_author_ids[author_id] = True

#     return user_info, duplicate_count


def remove_duplicates(user_info):
    seen_author_ids = set()
    unique_users = []
    duplicate_count = 0

    for user in user_info:
        author_id = user['user_profile']['author_uid']
        if author_id not in seen_author_ids:
            unique_users.append(user)
            seen_author_ids.add(author_id)
        else:
            duplicate_count += 1

    return unique_users, duplicate_count
