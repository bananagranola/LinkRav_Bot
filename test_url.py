#!/usr/bin/python
# tests ravelry.url_to_string
# main()

import sys
from auth_my import *
from ravelry import *

def main():
	ravelry = Ravelry (ravelry_accesskey, ravelry_personalkey)
	print ravelry.url_to_string (sys.argv[1])

main()
