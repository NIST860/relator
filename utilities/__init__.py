def inherits(obj, cls):
	from relator.utilities.iter import expand
	return cls in expand([obj], lambda o: getattr(o, '__bases__', ()))


def do(iterator):
	for _ in iterator:
		pass
