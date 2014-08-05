#!/usr/bin/python
# tests ravelry.url_to_string
# main()

import sys
from auth_my import *
from ravelry import Ravelry

def main():
	ravelry = Ravelry (ravelry_accesskey, ravelry_personalkey)
	
	for i in sys.argv:
		if i != sys.argv[0]:
			print ravelry.url_to_string (i)

main()
