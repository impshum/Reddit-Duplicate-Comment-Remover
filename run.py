import praw
import configparser
import re
import argparse
import schedule
from time import sleep


parser = argparse.ArgumentParser(
    description='Duplicate Comment Remover v2 (by /u/impshum)')
parser.add_argument(
    '-t', '--test', help='test mode', action='store_true')
parser.add_argument(
    '-u', '--user', help='target individual user', type=str)
parser.add_argument(
    '-o', '--once', help='run only once', action='store_true')
args = parser.parse_args()

test_mode, target_user, once_mode = False, False, False

if args.test:
    test_mode = True

if args.user:
    target_user = args.user

if args.once:
    once_mode = True

config = configparser.ConfigParser()
config.read('conf.ini')
reddit_user = config['REDDIT']['reddit_user']
reddit_pass = config['REDDIT']['reddit_pass']
client_id = config['REDDIT']['client_id']
client_secret = config['REDDIT']['client_secret']
target_subreddit = config['SETTINGS']['target_subreddit']
submission_limit = int(config['SETTINGS']['submission_limit'])
sleep_time = int(config['SETTINGS']['sleep_time'])

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     username=reddit_user,
                     password=reddit_pass,
                     user_agent='Duplicate Comment Remover v2 (by /u/impshum)')

removed = ['[deleted]', '[removed]']


class C:
    W, G, R, Y = '\033[0m', '\033[92m', '\033[91m', '\033[93m'


def remove_emoji(string):
    emoji_pattern = re.compile('['
                               u'\U0001F600-\U0001F64F'
                               u'\U0001F300-\U0001F5FF'
                               u'\U0001F680-\U0001F6FF'
                               u'\U0001F1E0-\U0001F1FF'
                               u'\U00002702-\U000027B0'
                               u'\U000024C2-\U0001F251'
                               ']+', flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


def runner():
    for submission in reddit.subreddit(target_subreddit).new(limit=submission_limit):
        thread = {}
        uniques = []
        duplicates = []
        title = submission.title
        submission.comments.replace_more(limit=None)

        for comment in submission.comments.list():
            if comment.author and not comment.locked and comment.author not in removed and comment.body not in removed:
                id = comment.id
                created = comment.created_utc
                body = remove_emoji(comment.body).replace(
                    '*', '').replace(' ', '').replace('\n', '').lower()

                if target_user and target_user == comment.author.name:
                    thread.update({created: {'id': id, 'body': body}})
                elif not target_user:
                    thread.update({created: {'id': id, 'body': body}})

        for k, v in sorted(thread.items()):
            id = v['id']
            body = v['body']

            if body in uniques:
                duplicates.append(id)
            else:
                uniques.append(body)

        if len(title) > 80:
            title = f'{title[0:80].strip()}...'

        print(f'{C.R}{len(duplicates)}{C.W}/{C.G}{len(uniques)} {C.W}{title}{C.W}')
        for duplicate in duplicates:
            if not test_mode:
                comment = reddit.comment(duplicate)
                comment.mod.lock()
                comment.mod.remove()


def main():
    runner()
    if not once_mode:
        schedule.every(sleep_time).minutes.do(runner)
        while True:
            schedule.run_pending()
            sleep(1)


if __name__ == '__main__':
    main()
