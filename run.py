import praw
import json
from time import time


client_id = 'XXXX'
client_secret = 'XXXX'
reddit_user = 'XXXX'
reddit_pass = 'XXXX'
user_agent = 'Duplicate Remover (by /u/impshum)'

target_subreddit = 'XXXX'

send_message = 1
delete_post = 1

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent,
                     username=reddit_user,
                     password=reddit_pass)


def get_threads():
    with open('threads.txt') as f:
        data = f.readlines()
        data = [x.strip() for x in data]
    return data


def do_db(token, id):
    with open('data.json') as f:
        data = json.load(f)
    gotcha = data.get(token)
    if gotcha and gotcha != id:
        return False
    else:
        data.update({token: id})
        with open('data.json', 'w') as f:
            json.dump(data, f)
        return True


def stream():
    print('\nStarting the stream\n')
    start = time()
    for comment in reddit.subreddit(target_subreddit).stream.comments():
        if comment.created_utc > start:
            id = comment.id
            user = comment.author.name
            body = comment.body.replace('*', '').strip().lower()
            special_threads = get_threads()
            if comment.submission in special_threads:
                if do_db(body, id):
                    print(f'New comment: {body}')
                else:
                    response(comment, user, body)


def history():
    print('\nTrawling through old comments\n')
    special_threads = get_threads()
    for thread in special_threads:
        submission = reddit.submission(id=thread)
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            id = comment.id
            user = comment.author.name
            body = comment.body.replace('*', '').strip().lower()
            if do_db(body, id):
                print(f'New comment: {body}')
            else:
                response(comment, user, body)


def response(comment, user, body):
    if send_message:
        msg = f'Your comment has been removed from {target_subreddit} as it has already been posted. Sorry.'
        reddit.redditor(user).message('Oh noes!', msg)
    if delete_post:
        comment.mod.delete()
        print(f'Deleted duplicate: {body}')


history()
stream()
