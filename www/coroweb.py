#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'maoyu'

import asyncio, os, inspect, logging, functools
from urllib import parse
from aiohttp import web

from www.apis import APIError

def get(path):
	'''
	Define decorator @get('/path')
	:param text:
	:return:
	'''
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			return func(*args, **kw)
		wrapper.__method__ = 'GET'
		wrapper.__route__ = path
		return wrapper
	return decorator

def post(path):
	'''
	Define decorator @post('/path')
	:param path:
	:return:
	'''
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			return func(*args, **kw)
		wrapper.__method__ = 'POST'
		wrapper.__route__ = path
		return wrapper
	return decorator

# 获得函数fn中 没有默认值 的 命名关键字 参数列表
def get_required_kw_args(fn):
	args=[]
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
			args.append(name)
	return tuple(args)

# 获得函数fn中所有 命名关键字 参数列表
def get_named_kw_args(fn):
	args=[]
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY :
			args.append(name)
	return tuple(args)

# 判断函数fn中是否有 命名关键字
def has_named_kw_args(fn):
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY :
			return True

# 判断函数fn中是否有 关键字参数
def has_var_kw_arg(fn):
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.VAR_KEYWORD:
			return True

# 判断函数fn中是否需要存下request本身
def has_request_arg(fn):
	sig = inspect.signature(fn)
	params = sig.parameters
	found = False
	for name, param in params.items():
		if name=='request':
			found = True
			continue
		# 以下这段代码真心觉得有点难懂哎！！！
		if found and (param.kind != inspect.Parameter.VAR_KEYWORD and param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY):
			raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))

class RequestHandler(object):
	def __init__(self, app, fn):
		self._app = app
		self._func = fn
		self._has_request_arg = has_request_arg(fn)
		self._has_var_kw_arg = has_var_kw_arg(fn)
		self._has_named_kw_args = has_named_kw_args(fn)
		self._named_kw_args = get_named_kw_args(fn)
		self._required_kw_args = get_required_kw_args(fn)

	@asyncio.coroutine
	def __call__(self, request):
		kw = None
		# 如何有 关键字参数 或者有 命名关键字参数 或者有 没有默认值的命名关键字参数
		# 那么，就获取所有的参数信息
		if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
			# POST情况下
			if request.method == 'POST':
				if not request.content_type:
					return web.HTTPBadRequest('Missing Content-Type')
				ct = request.content_type.lower()
				if ct.startwith('application/json'):
					params = yield from request.json()
					if not isinstance(params, dict):
						return web.HTTPBadRequest('JSON body must be object')
					kw = params
				elif ct.startwith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
					params = yield from request.post()
					kw = dict(**params)
				else:
					return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)
			# GET情况下
			# 注意，这里是再开一个if，而不是用elif，
			# 因为一个request请求可以同时包含post和get
			if request.method == 'GET':
				qs = request.query_string
				if qs:
					kw = dict()
					# 有True表示空值被保存，默认的False值表示忽略空值
					for k, v in parse.parse_qs(qs, True).items():
						kw[k] = v[0]

		if kw is None:
			kw = dict(**request.math_info)
		else:
			# 如果没有 关键字参数 只有 有命名关键字参数
			if not self._has_var_kw_arg and self._named_kw_args:
				# 把所有的命名关键字参数保存到copy中
				copy = dict()
				for name in self._named_kw_args:
					if name in kw:
						copy[name] = kw[name]
				# 删掉所有的 非命名关键字参数
				kw = copy

				# 其实，以下这段代码我真心不知道在干嘛，
				# 所有的命名关键字不是已经都存入copy，然后copy又赋值给了kw了么
				# 重复一下的意义何在？
				for k,v in request.math_info.items():
					if k in kw:
						logging.info('Duplicate arg name in named arg and kw args: %s' % k)
					kw[k] = v

		# 如果需要存下request整个对象
		if self._has_request_arg:
			kw['request'] = request

		# 保证所有的 没有默认值的 命名关键字参数 都有实参
		if self._required_kw_args:
			for name in self._required_kw_args:
				if not name in kw:
					return web.HTTPBadRequest('Missing argument: %s' % name)

		logging.info('call with args: %s' % str(kw))
		try:
			r = yield from self._func(**kw)
			return r
		except APIError as e:
			return dict(error=e.error, data=e.data, message=e.message)

def add_route(app, fn):
	method = getattr(fn, '__method__', None)
	path = getattr(fn, '__path__', None)
	if path is None or method is None:
		raise ValueError('@get or @post not defined in %s.' % str(fn))
	if not asyncio.iscoroutinefuncton(fn) and not inspect.isgeneratorfunction(fn):
		fn = asyncio.coroutine(fn)
	logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
	app.router.add_route(method, path, RequestHandler(app, fn))

def add_routes(app, module_name):
	n = module_name.rfind('.') #找到模块名的最右边的“.”的位置
	if n==(-1):
		# 动态导入模块
		# 等效于import module_name
		mode = __import__(module_name, globals(), locals())
	else:
		name = module_name[n+1:]
		prename = module_name[:n]
		# 动态导入模块
		# note that __import__('A.B', ...)
		# returns package A when fromlist is empty,
		# return B when fromlist is not empty.
		# 所以，__import__(prename, globals(), locals(), [name])
		# 返回prename字符串中的最后一个package或者模块，假设名为kk
		# 在用getarrt获得kk中的那个名字为name的模块
		mod = getattr(__import__(prename, globals(), locals(), [name]), name)
	for attr in dir(mod):
		if attr.startswith('_'):
			continue
		fn = getattr(mod, attr)
		if callable(fn):
			method = getattr(fn, '__method__', None)
			path = getattr(fn, '__path__', None)
			if method and path:
				add_route(app, fn)

def add_static(app):
	# __file__ 当前py文件的完整路径+名称
	# os.path.abspath(path) 返回path规范化的绝对路径。
	# os.path.dirname(path)返回path的目录。其实就是os.path.split(path)的第一个元素。
	# os.path.join(path1[, path2[, ...]]) 将多个路径组合后返回，第一个绝对路径之前的参数将被忽略。
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
	app.router.add_static('/static/', path)
	logging.info('add static %s => %s' % ('/static/', path))

























