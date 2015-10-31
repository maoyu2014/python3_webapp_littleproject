#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Default configurations.
'''

__author__ = 'maoyu'

configs = {
	'debug': True,
	'db': {
		'host':'127.0.0.1',
		'port':3360,
		'user':'www-data',
		'password':'www-data',
		'db':'awesome'
	},
	'session': {
		'secret':'Awesome'
	}
}