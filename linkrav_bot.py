#!/usr/bin/python
# LinkRav_Bot
# by /u/bananagranola
# posts ravelry information on settings.bot_subreddit
# main()

# import libs
import logging
import praw
import re
import requests
import signal
import sys

# import linkrav_bot modules
from auth_my import *
from constants import *
from settings import *
from ravelry import *
from pattern import *
from project import *
from yarn import *

# basic logging
logging.basicConfig()
logger = logging.getLogger('linkrav_bot')
logger.setLevel(logging.INFO)
	
# ctrl-c handling
def signal_handler(signal, frame):
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# check if comment has already been processed
def is_processed (reddit, comment):
	already_processed = False

	if re.search(comment.author.name, reddit_username, re.IGNORECASE):
		already_processed = True
		logger.debug("OWN POST: %s", comment.id)
		return already_processed

	# hacky workaround to populate child replies
	comment = reddit.get_submission(comment.permalink).comments[0]

	for comment_reply in comment.replies:
		# check if direct child 
		if comment_reply.parent_id == "t1_{}".format(comment.id):
			# check if bot already commented
			if re.search(comment_reply.author.name, reddit_username, re.IGNORECASE):
				already_processed = True
				logger.debug("ALREADY PROCESSED: %s", comment.id)
				return already_processed

# delete comments with lots of downvotes
def delete_downvotes (user):
	user_comments = user.get_comments(limit = 20)
	for user_comment in user_comments:
		score = user_comment.score
		if score < karma_floor:
			user_comment.delete()
			logger.debug("DELETING: %s", user_comment.id)

# process comments
def process_comment (ravelry, reddit, comment):
	comment_reply = ""
	# check if comment called linkrav
	if re.search('.*LinkRav.*', comment.body, re.IGNORECASE):
		matches = re.findall(RAV_MATCH, comment.body, re.IGNORECASE)
	else:
		return ""

	# check if previously processed
	if is_processed (reddit, comment) == True:
		return ""

	# iterate through matches
	if matches is not None:
		logger.debug("COMMENT PERMALINK: %s", comment.permalink)

		matches = set(matches)
		
		# append to comments
		for match in matches:
			match_string = ravelry.url_to_string (match)
			if match_string is not None:
				comment_reply += match_string
				comment_reply += "*****\n"

	# log and post comment
	if comment_reply != "":
		comment_reply = START_NOTE + comment_reply + END_NOTE
		logger.debug("\n\n-----%s-----\n\n", comment_reply)

	# return comment text
	return comment_reply

def main(subreddit):

	try:
		# log into ravelry
		ravelry = Ravelry(ravelry_accesskey, ravelry_personalkey)

		# log in to reddit
		reddit = praw.Reddit('linkrav by /u/bananagranola')
		try: reddit.login(reddit_username, reddit_password)
		except praw.errors.InvalidUserPass, e:
			logger.error("InvalidUserPass: %s", e.args)
			sys.exit(1)

		# retrieve subreddit
		if subreddit is None:
			subreddit = reddit.get_subreddit(bot_subreddit)
		else: # for purposes of looping
			subreddit.refresh()

		# retrieve comments
		comments = subreddit.get_comments(limit = comments_limit)
		
		# iterate through comments
		for comment in comments:

			# process comment
			comment_reply = process_comment (ravelry, reddit, comment)

			# post, handling rate limit error
			if comment_reply != "":
				while True:
					try:
						reply = comment.reply (comment_reply)
						logger.info(reply.permalink)
						break
					except praw.errors.RateLimitExceeded, e:
						logger.debug("RateLimitExceeded. Sleeping.")
						time.sleep(60)
	
		delete_downvotes(reddit.get_redditor(reddit_username))

	except requests.exceptions.ConnectionError, e:
		logger.error('ConnectionError: %s', str(e.args))
		sys.exit(1)
	except requests.exceptions.HTTPError, e:
		logger.error('HTTPError: %s', str(e.args))
		sys.exit(1)
	except requests.exceptions.Timeout, e:
		logger.error('Timeout: %s', str(e.args))
		sys.exit(1)
	except praw.errors.ClientException, e:
		logger.error('ClientException: %s', str(e.ERROR_TYPE))
		sys.exit(1)
	except praw.errors.ExceptionList, e:
		logger.error('ExceptionList: %s', str(e.errors))
		sys.exit(1)
	except praw.errors.APIException, e:
		logger.error('APIException: %s', str(e.ERROR_TYPE))
		sys.exit(1)

if __name__ == "__main__":
	subreddit = None
	main (subreddit)

