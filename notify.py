from imapclient import IMAPClient, SEEN

import requests
import threading
import praw
import time
import json
import os
import email
import re

# Seen db
seen = set()
if os.path.exists('db.json'):
    with open('db.json', 'r') as f:
        seen = set(json.load(f))

seen_lock = threading.Lock()


# Notify Slack
def notify_slack(url, title):
    print(url + ' | ' + title)
    res = requests.post('https://hooks.slack.com/services/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',
        data=json.dumps({
            'username': 'gearbot',
            'icon_emoji': ':moneybag:',
            'text': ':fire: <' + url + '|' + title + '> :fire:',
        }), headers={'Content-Type': 'application/json'})
    if res.status_code != 200:
        print(res.text)


# Notify Discord
def notify_discord(url, title):
    res = requests.post('https://discordapp.com/api/webhooks/412776843805065216/GX5E7CZtDcF44K0ZlZHCg-C3xyJMQzPSXGrzYoJWvRXMREXHFuYxZF5Gpqs-h898BDo-',
        data=json.dumps({
            'username': 'gearbot',
            'content': title + '\n' + url,
        }), headers={'Content-Type': 'application/json'})
    if res.status_code != 200:
        print(res.text)


# Posts we care about
def reject_reddit(id, title):
    if id in seen:
        return True

    tag = title.split(' ')[0]

    if tag == '[GPU]':
        return False

    if tag == '[MOBO]':
        return False

    if tag == '[PSU':
        return False

    return True


def reddit():
    # Set up reddit api
    reddit = praw.Reddit(client_id='zGsOy6Dtyv5TUQ',
                         client_secret='-haf_3Kez9TbWwg2zFtPwy3PsRI',
                         password='BMYBSevMjpO9Jd9s',
                         user_agent='hanzo',
                         username='zeekay')

    while True:
        # Reddit Posts
        print('checking for submissions...')
        submissions = list(reddit.subreddit('buildapcsales').new(limit=10))

        for post in submissions:
            id = 'reddit' + post.id
            if reject_reddit(id, post.title):
                continue

            try:
                seen_lock.acquire()
                seen.add(id)
            finally:
                seen_lock.release()

            print(post.title, post.permalink)
            print(post.url, '\n')
            notify_slack(post.url, post.title)
            notify_discord(post.url, post.title)

        print('sleeping for 10 seconds...')
        time.sleep(10)


# Emails we care about
def reject_email(id, host):
    if id in seen:
        return True

    if host == 'nowinstock.net':
        return False

    if host == 'blockchainrigs.io':
        return False

    return True


def format_blockchainrigs_email(msg):
    msg = msg.replace('=\r\n', '').replace('\r\n', '').replace('<br>', '').replace('=3D', '=')
    match = re.search(r"^In stock: (.*?) Buy Link : <a href='(.*?)'>", msg, re.MULTILINE)

    if not match:
        return ['', '']

    return [match.group(2), match.group(1)]


def format_nowinstock_email(msg):
    msg = msg.replace('=\r\n', '').replace('\r\n', '').replace('<br>', '').replace('=3D', '=')
    match = re.search(r'^(.*?). Goto: (.*?)NowInStock', msg, re.MULTILINE)

    if not match:
        return ['', '']

    return [match.group(2), match.group(1)]


def email_():
    # Email Constants
    FROM_EMAIL  = 'g34rb0t@gmail.com'
    FROM_PWD    = '4QEN7C07Bz7h'
    SMTP_SERVER = 'imap.gmail.com'

    # Set up email api
    # idle client

    mail_clients = [None, None]

    def reset_connection():
        try:
            print('resetting email connection')
            idle_mail = mail_clients[0] = IMAPClient(SMTP_SERVER, use_uid=True, ssl=True)
            idle_mail.login(FROM_EMAIL, FROM_PWD)
            idle_mail.select_folder('INBOX')
            idle_mail.idle()

            mail = mail_clients[1] = IMAPClient(SMTP_SERVER, use_uid=True, ssl=True)
            mail.login(FROM_EMAIL, FROM_PWD)
            mail.select_folder('inbox')
        except Exception as err:
            print(err)
            reset_connection()

    reset_connection()

    old_time = time.time()

    while True:
        idle_mail = mail_clients[0]
        mail = mail_clients[1]

        print('checking for emails...')

        responses = []
        if time.time() - old_time > 599:
            try:
                responses.extend(idle_mail.idle_done())
            except Exception as err:
                print(err)
                print('idle_done had an issue, continuing')

            reset_connection()
            old_time = time.time()

        try:
            responses.extend(idle_mail.idle_check(timeout=30))
        except Exception as err:
            print(err)
            print('idle_mail had an issue, continuing')
            continue

        print('Server sent:', responses or 'nothing')

        if not responses:
            continue

        try:
            # this is needed to force refresh
            mail.fetch([1], ['RFC822'])
            messages = mail.search(['UNSEEN'])
        except Exception as err:
            print(err)
            print('search had an issue, continuing')
            continue

        print('messages')
        print(messages)

        try:
            items = mail.fetch(messages, ['ENVELOPE', 'RFC822']).items()
        except Exception as err:
            print(err)
            print('fetch had an issue, continuing')
            continue

        for uid, data in items:
            try:
                print('UID')
                print(uid)

                id = 'email' + str(uid)

                mail.set_flags([uid], SEEN)

                envelope = data[b'ENVELOPE']
                host = envelope.sender[0].host.decode()
                if reject_email(id, host):
                    continue

                message = email.message_from_bytes(data[b'RFC822'])

                text = ''
                if message.is_multipart():
                    for payload in message.get_payload():
                        text += payload.get_payload()
                else:
                    text = message.get_payload()

                url = ''
                title = ''
                if host == 'nowinstock.net':
                    [url, title] = format_nowinstock_email(text)
                elif host == 'blockchainrigs.io':
                    [url, title] = format_blockchainrigs_email(text)
                else:
                    print('Host not recognized: ' + host)

                if url and title:
                    notify_slack(url, title)
                    notify_discord(url, title)
                else:
                    print('Could not decode email')
            except Exception as err:
                print(err)


if __name__ == '__main__':
    # reddit_thread = threading.Thread(target=reddit)
    # reddit_thread.start()

    email_thread = threading.Thread(target=email_)
    email_thread.start()

    while True:
        with open('db.json', 'w') as f:
            json.dump(list(seen), f)
            time.sleep(30)

