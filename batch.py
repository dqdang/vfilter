import argparse
import os
import praw
import time

try:
    R_USERNAME = os.environ["USERNAME"]
    R_PASSWORD = os.environ["PASSWORD"]
    R_CID = os.environ["R_CID"]
    R_SECRET = os.environ["R_SECRET"]
    R_SUBREDDIT = os.environ["SUBREDDIT"]

except KeyError as e:
    with open("creds.txt", "r") as f:
        R_USERNAME = f.readline().strip()
        R_PASSWORD = f.readline().strip()
        R_CID = f.readline().strip()
        R_SECRET = f.readline().strip()
        R_SUBREDDIT = f.readline().strip()


def get_subreddits(args):
    subreddits = ""
    subreddits_path = "subreddits.txt"
    if args.path:
        subreddits_path = os.path.join(path, subreddits_path)
    with open("subreddits.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                subreddits += line + "+"
    subreddits = subreddits[:-2]
    return subreddits


def get_keywords(args):
    keywords = set()
    keywords_path = "keywords.txt"
    if args.path:
        keywords_path = os.path.join(path, keywords_path)
    with open(keywords_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                keywords.add(line)
    return keywords


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Filter a subreddit by keywords')
    parser.add_argument(
        '-p', '--path', help='Set paths to look for default files (keywords.txt, subreddits.txt)', action='store')

    args = parser.parse_args()
    write_to = "submitted.txt"
    if args.path:
        write_to = os.path.join(args.path, write_to)

    reddit = praw.Reddit(client_id=R_CID, client_secret=R_SECRET,
                         password=R_PASSWORD, user_agent="USERAGENT", username=R_USERNAME)

    if not os.path.isfile(write_to):
        submitted = []
    else:
        with open(write_to, "r") as f:
            submitted = f.read()
            submitted = submitted.split("\n")
            submitted = set(filter(None, submitted))

    try:
        subreddits = get_subreddits(args)
        print(subreddits)
        subreddit = reddit.subreddit(subreddits)
        keywords = get_keywords(args)
        search_results = []
        for keyword in keywords:
            search_results += list(subreddit.search(keyword, limit=2000))
        for submission in search_results:
            print(submission.title)
            if submission.id not in submitted:
                for keyword in keywords:
                    if keyword in submission.title:
                        try:
                            cross_post = submission.crosspost(subreddit=R_SUBREDDIT,
                                                              send_replies=False)
                            submitted.add(submission.id)
                            break

                        except:
                            print("Waiting... 0 minutes")
                            time.sleep(300)
                            print("Waiting... 5 minutes")
                            time.sleep(300)
                            print("Waiting... 10 minutes")
                            time.sleep(300)
                            print("Done waiting... 15 minutes")
                            cross_post = submission.crosspost(subreddit=R_SUBREDDIT,
                                                              send_replies=False)
                            submitted.add(submission.id)
                            break

        with open(write_to, "w+") as f:
            for post_id in submitted:
                f.write(post_id + "\n")
                print(post_id)

    except Exception as e:
        print(e)
        exit()
