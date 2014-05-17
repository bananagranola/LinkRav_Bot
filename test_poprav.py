#!/usr/bin/python
# populates settings.testing_sub with ravelry urls
# main()

import logging
import praw
import re
import requests
import signal
import sys

from auth_my import *
from constants import *
from settings import *

logging.basicConfig()
logger = logging.getLogger('poprav_test')
logger.setLevel(logging.DEBUG)

def signal_handler (signal, frame):
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

commented_filename = sys.argv[0] + ".log"

def get_comments(commented_filename):
	try:
		commented_file = open(commented_filename, 'a+')
		commented = set(line.strip() for line in commented_file)
		commented_file.close()
		return commented
	except IOError, e:
		logger.error('IOError: %s', str(e.code))
		return False
def save_comments(commented_filename, comment_id):
	try: 
		commented_file = open(commented_filename, 'a+')
		commented_file.write(comment_id)
		commented_file.write("\n")
		commented_file.close()
	except IOError, e:
		logger.error('IOError: %s', str(e.code))
		return False

def main():
	commented = get_comments(commented_filename)
	if commented == False:
		logger.error("Comments not retrieved.")

	reddit = praw.Reddit('poprav_test by /u/bananagranola')
	try: 
		reddit.login(reddit_username, reddit_password)
	except praw.errors.InvalidUserPass, e:
		logger.error("InvalidUserPass: {}".format(str(e.args)))
		sys.exit(1)
	
	subreddit = reddit.get_subreddit("knitting")
	comments = subreddit.get_comments(limit = comments_limit)
	try:
		for comment in comments:
			test_comment = ""
			if comment.id not in commented:
				matches = re.findall(RAV_MATCH, comment.body, re.IGNORECASE)
				for match in matches:
					test_comment += "{}\n\n".format(match)
			else: 
				logger.info("ALREADY PRINTED: {}".format(comment.id))
				break
					
			if test_comment != "":
				test_comment = "LinkRav\n\n" + test_comment
				submission = reddit.get_info(thing_id = testing_sub)
				logger.info("\n\n{}-----\n\n".format(test_comment))
				submission.add_comment(test_comment)

				commented.add(comment.id)
				saved = save_comments(commented_filename, comment.id)
				if saved == False:
					logger.error("Comments not saved.")

	except requests.exceptions.HTTPError, e:
		logger.error('HTTPError: %s', str(e.args))
		sys.exit(1)
	except praw.errors.ClientException, e:
		logger.error('ClientException: %s', str(e.args))
		sys.exit(1)
	except praw.errors.APIException, e:
		logger.error('APIException: %s', str(e.args))
		sys.exit(1)

main()
