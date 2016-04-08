#!/usr/bin/python
# ravelry api retrieval
# get() and url_to_string()

import base64
import logging
import re
import requests
try: import simplejson as json
except ImportError: import json

import requests

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
		r = requests.get(json_url, auth=(self.accesskey, self.personalkey))
		loaded = json.loads(r.content)
		return loaded

	def get_redirect(self, url):
                if url.startswith("http://") == False:
		    url = "http://" + url
                r = requests.get(url)
                return r.url

	def url_to_string (self, match):

		match = self.get_redirect(match)

		# pattern
		pattern_match = re.search(PAT_REGEX, match, re.IGNORECASE)
		if pattern_match:
			logger.debug("PATTERN: %s", match)
			data = self.get_json(PAT_API.format(pattern_match.group(0)))
			pattern = Pattern(data)
			if pattern.fill() == False:
				logger.debug("INVALID PATTERN: %s", match)
				return None
			return pattern.to_string()
            
		# project
		project_match = re.search(PROJ_REGEX, match, re.IGNORECASE)
		if project_match:
			logger.debug("PROJECT: %s", match)
			data = self.get_json(PROJ_API.format(project_match.group(0)))
			project = Project(data)
			if project.fill(self) == False:
				logger.debug("INVALID PROJECT: %s", match)
				return None
			return project.to_string()

		# yarn
		yarn_match = re.search(YARN_REGEX, match, re.IGNORECASE)
		if yarn_match:
			logger.debug("YARN: %s", match)
			data = self.get_json(YARN_API.format(yarn_match.group(0)))
			yarn = Yarn(data)
			if yarn.fill() == False:
				logger.debug("INVALID YARN: %s", match)
				return None
			return yarn.to_string()

		logger.debug("INVALID: %s", match)
		return None

