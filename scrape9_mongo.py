from pymongo import MongoClient

def connect_to_mongodb(uri, db_name, collection_name):
    # Create a new client and connect to the server
    client = MongoClient(uri)
    # Access the specified database and collection
    db = client[db_name]
    collection = db[collection_name]
    return collection

def insert_user_data_to_mongodb(uri, db_name, collection_name, user_info):
    # Connect to the MongoDB collection
    collection = connect_to_mongodb(uri, db_name, collection_name)

    # Keep track of newly inserted and updated records
    new_users_added = 0
    updated_users = 0

    # Iterate through the user_info and add them to the collection if not duplicates
    for user in user_info:
        # Using the author_uid as the unique identifier
        author_uid = user['user_profile']['author_uid']
        existing_record = collection.find_one({"user_profile.author_uid": author_uid})

        if existing_record:
            # Update the existing record with the latest information
            collection.update_one({"user_profile.author_uid": author_uid}, {"$set": user})
            updated_users += 1
        else:
            # Insert the individual user's data
            collection.insert_one(user)
            new_users_added += 1

    total_unique_users = collection.count_documents({})  # Get the total count of documents in the collection

    print(f"Inserted {new_users_added} new users into {db_name}.{collection_name}")
    print(f"Updated {updated_users} existing users")
    return new_users_added, total_unique_users, updated_users  # You may also return the count of updated users if needed



    # print(f"Inserted {len(user_info) - duplicates} new users into {db_name}.{collection_name}")
    # print(f"Skipped {duplicates} duplicate users")
    # return inserted_users, total_unique_users

# Usage
# uri = "mongodb+srv://jason:jason@social-scraper.1stgz.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
# user_info = [...]  # Replace this with your scraped user_info list
# insert_user_data_to_mongodb(uri, 'master_db', 'user_list', user_info)
