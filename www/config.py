#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Configuration
'''

__author__ = 'maoyu'

from www import config_default

def merge(defaults, overrides):
	r={}
	for k,v in defaults.items():
		if k in overrides:
			if isinstance(v, dict):
				r[k] = merge(v, overrides[k])
			else:
				r[k]=overrides[k]
		else:
			r[k]=v
	return r

configs = config_default.configs

try:
	from www import config_override
	configs = merge(configs, config_override.configs)
except ImportError:
	pass


class Dict(dict):
	def __init__(self, names=(), values=(), **kw):
		super().__init__(**kw)
		for k,v in zip(names, values):
			self[k]=v

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value

def toDict(d):
	D = Dict()
	for k,v in d.items():
		D[k] = toDict(v) if isinstance(v,dict) else v
	return D

configs = toDict(configs)