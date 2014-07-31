#!/usr/bin/python
# tests comment reply using comment id
# main()

import praw
import sys

from auth_my import *
from ravelry import *

def main():

	ravelry = Ravelry (ravelry_accesskey, ravelry_personalkey)
	reddit = praw.Reddit("LinkRav_Bot by /u/banangranola")
	
	arg = sys.argv[1]
	if "http" in arg:
		arg = arg[-7:]
		print arg

	id = "t1_" + arg
	comment = reddit.get_info(thing_id = id)
	
	if re.search('.*LinkRav.*', comment.body, re.IGNORECASE):
		matches = re.findall(RAV_MATCH, comment.body, re.IGNORECASE)

  # create comments
	comment_reply = ""
	for match in matches:
		match_string = ravelry.url_to_string (match)
		if match_string == None:
			comment_reply += INVALID_NOTE.format(match)
		else:
			comment_reply += match_string

	print comment_reply
	
main()
