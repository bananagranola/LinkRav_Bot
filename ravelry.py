#!/usr/bin/python
# ravelry api retrieval
# get() and url_to_string()

import base64
import logging
import re
try: import simplejson as json
except ImportError: import json
import urllib2

from constants import *
from pattern import *
from project import *
from yarn import *

logging.basicConfig()
logger = logging.getLogger('linkrav_bot')
logger.setLevel(logging.DEBUG)

class Ravelry:
	def __init__(self, accesskey, personalkey):
		self.accesskey = accesskey
		self.personalkey = personalkey

	def get_json(self, json_url):

		request = urllib2.Request(json_url)
		base64string = base64.encodestring('%s:%s' % (self.accesskey, self.personalkey)).replace('\n', '')
		request.add_header("Authorization", "Basic %s" % base64string)

		try: 
			requested = urllib2.urlopen(request)
		except urllib2.HTTPError, e:
			logger.error ('HTTPError: %s. URL: %s', str(e.args), json_url)
			return None

		try: 
			loaded = json.load(requested)
		except ValueError, e:
			logger.error ('ValueError: %s. URL: %s', str(e.args), json_url)
			return None
	
		return loaded

	def get_redirect(self, url):
		if re.search (".*http://.*", url, re.IGNORECASE) == None:
			url = "http://" + url
		
		try:
			req = urllib2.Request (url)
			res = urllib2.urlopen(req)
			url = res.geturl()
		except urllib2.HTTPError, e:
			logger.error('HTTPError: %s. URL: %s', str(e.args), url)
			return None
		except ValueError, e:
			logger.error('ValueError: %s. URL: %s', str (e.args), url)

		logger.debug("REDIRECTING: %s", url)
		return url

	def url_to_string (self, match):

		# if link shortened, get redirected full url
		if re.search('.*ravel.me.*', match, re.IGNORECASE) != None:
			match = self.get_redirect(match)

		# pattern
		pattern_match = re.search(PAT_REGEX, match, re.IGNORECASE)
		if pattern_match:
			logger.info("PATTERN: %s", match)
			data = self.get_json(PAT_API.format(pattern_match.group(0)))
			pattern = Pattern(data)
			if pattern.fill() == False:
				logger.debug("INVALID PATTERN: %s", match)
				return None
			return pattern.to_string()
            
		# project
		project_match = re.search(PROJ_REGEX, match, re.IGNORECASE)
		if project_match:
			logger.info("PROJECT: %s", match)
			data = self.get_json(PROJ_API.format(project_match.group(0)))
			project = Project(data)
			if project.fill(self) == False:
				logger.debug("INVALID PROJECT: %s", match)
				return None
			return project.to_string()

		# yarn
		yarn_match = re.search(YARN_REGEX, match, re.IGNORECASE)
		if yarn_match:
			logger.info("YARN: %s", match)
			data = self.get_json(YARN_API.format(yarn_match.group(0)))
			yarn = Yarn(data)
			if yarn.fill() == False:
				logger.debug("INVALID YARN: %s", match)
				return None
			return yarn.to_string()

		logger.debug("INVALID: %s", match)
		return None

