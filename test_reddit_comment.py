#!/usr/bin/python
# tests comment reply using comment id
# main()

import praw
import sys

from auth_my import *
from ravelry import *
from linkrav_bot import process_comment

def main():

	ravelry = Ravelry (ravelry_accesskey, ravelry_personalkey)
	reddit = praw.Reddit("LinkRav_Bot by /u/banangranola")
	
	arg = sys.argv[1]
	if "http" in arg:
		arg = arg[-7:]

	id = "t1_" + arg
	comment = reddit.get_info(thing_id = id)
	
	print process_comment(ravelry, comment)

main()
