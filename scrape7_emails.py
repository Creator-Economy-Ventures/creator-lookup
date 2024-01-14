import re
import logging

def extract_emails(text):
    # Regular expression pattern to match email addresses
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    try:
        if text is None:
            logging.warning('extract_emails received None as input.')
            return []
        return re.findall(pattern, text)
    except Exception as e:
        logging.error(f'Unexpected error in extract_emails: {str(e)}')
        return []

def update_user_info_with_emails(user_info):
    for user in user_info:
        tiktok_bio = user['user_profile'].get('tiktok_bio', '')
        instagram_bio = user['user_profile'].get('instagram_bio', '')

        # Extract emails from TikTok and Instagram bios
        tiktok_emails = extract_emails(tiktok_bio)
        instagram_emails = extract_emails(instagram_bio)

        # Update user information with extracted emails (if any)
        if tiktok_emails:
            user['user_profile']['tiktok_emails'] = tiktok_emails
        if instagram_emails:
            user['user_profile']['instagram_emails'] = instagram_emails

    return user_info
