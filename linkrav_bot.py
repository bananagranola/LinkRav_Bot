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
def is_processed (comment):
	already_processed = False

	if re.search(comment.author.name, reddit_username, re.IGNORECASE):
		already_processed = True
		logger.debug("OWN POST: %s", comment.id)
		return already_processed

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
			logger.info("DELETING: %s", user_comment.id)

# process comments
def process_comment (ravelry, comment):
	# check if comment called linkrav
	if re.search('.*LinkRav.*', comment.body, re.IGNORECASE):
		matches = re.findall(RAV_MATCH, comment.body, re.IGNORECASE)
	else:
		return ""

	# check if previously processed
	if is_processed (comment) == True:
		return ""

	# iterate through matches
	if matches is not None:
		logger.debug("COMMENT PERMALINK: %s", comment.permalink)

		# append to comments
		comment_reply = ""
		for match in matches:
			match_string = ravelry.url_to_string (match)
			if match_string is not None:
				comment_reply += match_string

	# return comment text
	return comment_reply

def main(subreddit):

	try:
		# log into ravelry
		ravelry = Ravelry(ravelry_accesskey, ravelry_personalkey)

		# log in to reddit
		reddit = praw.Reddit('linkrav_bot by /u/bananagranola')
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
			comment_reply = process_comment (ravelry, comment)

			# log and post comment
			if comment_reply != "":
				logger.debug("\n\n-----%s-----\n\n", comment_reply)
				comment_reply = comment_reply + END_NOTE
			
				# handle rate limit error
				while True:
					try:
						comment.reply (comment_reply)
						logger.info(comment_reply)
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
	except praw.errors.APIException, e:
		logger.error('APIException: %s', str(e.ERROR_TYPE))
		sys.exit(1)

subreddit = None
main (subreddit)

