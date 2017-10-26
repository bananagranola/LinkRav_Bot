#!/usr/bin/python
# tests comment reply using comment id
# main()

import praw
import sys

from auth_my import *
from ravelry import Ravelry
from linkrav_bot import process_comment

def main():

	ravelry = Ravelry (ravelry_accesskey, ravelry_personalkey)
        reddit = praw.Reddit(client_id='gk6NskS0CNaveg', user_agent='python:com.example.linkrav_bot:v1.0.0 (by /u/bananagranola)', client_secret='U07acpzudpVqd4fIX4y-MCybt2A')

        arg = sys.argv[1]
	if "https" in arg:
		arg = arg[-8:]

        id = arg[:-1]
	comment = reddit.comment(id)
	
	process_comment(ravelry, comment)

main()
