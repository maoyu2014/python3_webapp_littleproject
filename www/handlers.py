#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import re, time, json, logging, hashlib, base64, asyncio
# from coroweb import get, post
# from models import User, Comment, Blog, next_id

import logging
from www.coroweb import get
from www.models import User

__author__ = 'maoyu'

'url handlers'

@get('/')
def index(request):
	users = yield from User.findAll()
	return {
		'__template__':'test.html',
		'users': users
	}