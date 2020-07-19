import argparse
import os
import praw
import time

R_USERNAME = os.environ["USERNAME"]
R_PASSWORD = os.environ["PASSWORD"]
R_CID = os.environ["R_CID"]
R_SECRET = os.environ["R_SECRET"]
R_SUBREDDIT = os.environ["SUBREDDIT"]


def get_subreddits(args):
    subreddits = ""
    subreddits_path = "subreddits.txt"
    if args.path:
        subreddits_path = os.path.join(path, subreddits_path)
    with open("subreddits.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
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
        '-p', '--path', help='set paths to look for default files (keywords.txt, subreddits.txt)', action='store')

    args = parser.parse_args()
    write_to = "posts_replied_to.txt"

    # Create the Reddit instance
    reddit = praw.Reddit(client_id=R_CID, client_secret=R_SECRET,
                         password=R_PASSWORD, user_agent="USERAGENT", username=R_USERNAME)

    # Have we run this code before? If not, create an empty list
    if not os.path.isfile(write_to):
        posts_replied_to = []
    # If we have run the code before, load the list of posts we have replied to
    else:
        # Read the file into a list and remove any empty values
        with open(write_to, "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    while True:
        # Get the top 5 values from our subreddit
        subreddit = reddit.subreddit(get_subreddits(args))
        keywords = get_keywords(args)
        for submission in subreddit.stream.submissions():
            # If we haven't replied to this post before
            print(submission.title)
            if submission.id not in posts_replied_to:
                for keyword in keywords:
                    if keyword in submission.title:
                        print(keyword, submission.title)
                        try:
                            cross_post = submission.crosspost(subreddit=R_SUBREDDIT,
                                                              send_replies=False)
                            break
                        except:
                            time.sleep(900)
                            cross_post = submission.crosspost(subreddit=R_SUBREDDIT,
                                                              send_replies=False)
                            break
                        finally:
                            continue
                        # Store the current id into our list
                        posts_replied_to.append(submission.id)

        # Write our updated list back to the file
        with open(write_to, "w") as f:
            for post_id in posts_replied_to:
                f.write(post_id + "\n")
