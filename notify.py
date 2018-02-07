import requests
import praw
import time
import json
import os

reddit = praw.Reddit(client_id='zGsOy6Dtyv5TUQ',
                     client_secret='-haf_3Kez9TbWwg2zFtPwy3PsRI',
                     password='BMYBSevMjpO9Jd9s',
                     user_agent='hanzo',
                     username='zeekay')


seen = set()
if os.path.exists('db.json'):
    with open('db.json', 'r') as f:
        seen = set(json.load(f))

# Posts we care about
def reject(post):
    if post.id in seen:
        return True

    tag = post.title.split(' ')[0]

    if tag == '[GPU]':
        return False

    if tag == '[MOBO]':
        return False

    return True

def notify(post):
    res = requests.post('https://hooks.slack.com/services/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',
        data=json.dumps({
            'username': 'gearbot',
            'icon_emoji': ':moneybag:',
            'text': ':fire: <' + post.url +  '|' + post.title + '> :fire:',
        }), headers={'Content-Type': 'application/json'})
    if res.status_code != 200:
        print(res.text)

while True:
    print('checking for submissions...')
    submissions = list(reddit.subreddit('buildapcsales').new(limit=10))

    for post in submissions:
        if reject(post):
            continue

        seen.add(post.id)

        print(post.title, post.permalink)
        print(post.url, '\n')
        notify(post)

    with open('db.json', 'w') as f:
        json.dump(list(seen), f)

    print('sleeping for 60 seconds...')
    time.sleep(60)
