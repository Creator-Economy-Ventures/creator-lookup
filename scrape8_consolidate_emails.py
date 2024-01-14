def consolidate_emails(user_info):
    # Initialize email_user_info as empty list
    email_user_info = []

    for user in user_info:
        # Initialize email as None
        email = None

        # Check for tiktok_emails
        tiktok_emails = user['user_profile'].get('tiktok_emails')
        if tiktok_emails and tiktok_emails[0] != '':
            email = tiktok_emails[0]

        # Check for instagram_emails if no tiktok_emails
        elif (instagram_emails := user['user_profile'].get('instagram_emails')) and instagram_emails[0] != '':
            email = instagram_emails[0]

        # Check for instagram_email if no tiktok_emails and no instagram_emails
        elif (instagram_email := user['user_profile'].get('instagram_email')) and instagram_email != '':
            email = instagram_email

        # Check for tiktok_email if no other emails found
        elif (tiktok_email := user['user_profile'].get('tiktok_email')) and tiktok_email != '':
            email = tiktok_email

        # Assign the determined email to the 'email' field in user_profile
        user['user_profile']['email'] = email if email else ''

        # Update the 'email' field in user_profile only if an email is found
        if email:
            #user['user_profile']['email'] = email
            email_user_info.append(user)

        user_info=email_user_info

    return user_info
