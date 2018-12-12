import praw
import json
from time import time


client_id = 'XXXX'
client_secret = 'XXXX'
reddit_user = 'XXXX'
reddit_pass = 'XXXX'
user_agent = 'Duplicate Remover (by /u/impshum)'

target_subreddit = 'FizzMobile'

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent,
                     username=reddit_user,
                     password=reddit_pass)

start = time()


def get_threads():
    with open('threads.txt') as f:
        data = f.readlines()
        data = [x.strip() for x in data]
    return data


def do_db(token, name):
    with open('data.json') as f:
        data = json.load(f)
    if data.get(token):
        return False
    else:
        data.update({token: name})
        with open('data.json', 'w') as f:
            json.dump(data, f)
        return True


print('\nStarting the stream\n')

for comment in reddit.subreddit(target_subreddit).stream.comments():
    if comment.created_utc > start:
        body = comment.body.replace('*', '').strip().lower()
        user = comment.author.name
        special_threads = get_threads()
        if comment.submission in special_threads:
            if do_db(body, user):
                print(f'New comment: {body}')
            else:
                comment.delete()
                msg = f'Your comment has been removed from {target_subreddit} as it has already been posted. Sorry.'
                reddit.redditor(user).message('Oh noes!', msg)
                print(f'Deleted duplicate: {body}')
