from functools import update_wrapper, partial

def with_fn(decorator):
	"""
	Allows a decorator to take mode arguments.
	The first argument is the function to decorate, which defaults to None.
	If the decorator is called without the function, it partially evaluates
	itself with the keyword arguments and waits for the function to decorate.
	Check it out:

	>>> @with_fn
	... def test(fn, name='Just'):
	...	 return name
	...
	>>> @test
	... def a(): return
	...
	>>> @test(name='another')
	... def b(): return
	...
	>>> @test(name='python hacker')
	... def c(): return
	...
	>>> ' '.join((a, b, c))
	'Just another python hacker'
	"""
	def real_decorator(fn=None, *args, **kwargs):
		if fn is None:
			return partial(real_decorator, *args, **kwargs)
		return decorator(fn, *args, **kwargs)
	update_wrapper(real_decorator, decorator)
	return real_decorator


@with_fn
def cached_on_one(fn=None, cache_name=None):
	"""
	Use on a property or classmethod. The function will only ever be called
	once.  The first time the property is called, the result will be saved.
	The saved value will be used from then on.

	The value will be stored in the attribute on the first parameter
	(convetionally 'self' for properties, 'cls' for classmethods) named by
	@cache_name, which defaults to an underscore and the name of the function.

	If cache_name is given and fn is not (i.e. you decorate with
	"cache_on_one(cache_name='name')" then this function will wait patiently
	for something to decorate.

	>>> class A(object):
	...	 @cached_on_one
	...	 def difficult(self):
	...		 print 'doing difficult work...'
	...		 return 1
	...
	>>> a = A()
	>>> a.difficult()
	doing difficult work...
	1
	>>> a.difficult()
	1
	>>> a._difficult
	1
	>>> class A(object):
	...	 @cached_on_one(cache_name='a')
	...	 def difficult(self):
	...		 print 'doing difficult work...'
	...		 return 1
	...
	>>> a = A()
	>>> a.difficult()
	doing difficult work...
	1
	>>> a.difficult()
	1
	>>> a.a
	1
	"""
	if cache_name is None and fn.__name__ == '<lambda>':
		raise ValueError('No cache name given for <lambda>')
	cache_name = cache_name or '_%s' % fn.__name__
	def realfn(one):
		if not hasattr(one, cache_name):
			setattr(one, cache_name, fn(one))
		return getattr(one, cache_name)
	update_wrapper(realfn, fn)
	return realfn


@with_fn
def cached_property(fn=None, cache_name=None):
	"""
	Just like cached_on_one, but applies 'property' to the resulting function.
	"""
	return property(cached_on_one(fn, cache_name))


@with_fn
def cached_classmethod(fn=None, cache_name=None):
	"""
	Just like cached_on_one, but applies 'classmethod' to the resulting function.
	"""
	return classmethod(cached_on_one(fn, cache_name))


@with_fn
def cache(fn=None, cache_name=None):
	if cache_name is None and fn.__name__ == '<lambda>':
		raise ValueError('No cache name given for <lambda>')
	cache_name = cache_name or '_%s' % fn.__name__
	def realfn(one, *args, **kwargs):
		cache = one.__dict__.setdefault(cache_name, {})
		key = (args, tuple(sorted(kwargs.items())))
		if key not in cache:
			cache[key] = fn(one, *args, **kwargs)
		return cache[key]
	update_wrapper(realfn, fn)
	return realfn


@with_fn
def decorator(doubledec=None, after=()):
	"""
	Turns a function of (fn, *args, **kwargs) into a decorator that
	decorates function, waits for *args and **kwargs, and then applies
	the decorator.

	Use this when you have a decorator that does no preparation but merely
	creates an inner funtion and immediately returns it.

	@after is a list of decorators that allows you to preform modifications on
	the decorated function once instead of each time it is called, which would
	otherwise be impossible.

	>>> @decorator
	... def add_one_to_first_arg(fn, a):
	...	 return fn(a+1)
	...
	>>> @add_one_to_first_arg
	... def addone(x):
	...	 return x
	...
	>>> addone(2)
	3

	And here's how the after thing works:

	>>> @decorator(after=[add_one_to_first_arg])
	... def add_two_to_first_arg(fn, a):
	...	 return fn(a+1)
	...
	>>> @add_two_to_first_arg
	... def addtwo(x):
	...	 return x
	...
	>>> addtwo(2)
	4
	"""
	def real_decorator(fn):
		fn = reduce(lambda fn, dec: dec(fn), after, fn)
		return lambda *args, **kwargs: doubledec(fn, *args, **kwargs)
	update_wrapper(real_decorator, doubledec)
	return real_decorator
