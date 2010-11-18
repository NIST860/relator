def irange(start, stop, step=1):
    """
    >>> list(irange(1, 10))
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> list(irange(5, 1, -1))
    [5, 4, 3, 2, 1]
    """
    return xrange(start, stop+step, step)


def unzip(iterable):
    """
    Unzips an iterable of any bredth into multiple lists.
    @iterable must be an iterable of uniform bredth,
    i.e. a list of n-tuples where n is constant.

    >>> x, y, z = unzip((
    ...     (1, 'one', 'i'),
    ...     (2, 'two', 'ii'),
    ...     (3, 'three', 'iii'),
    ... ))
    >>> x
    [1, 2, 3]
    >>> y
    ['one', 'two', 'three']
    >>> z
    ['i', 'ii', 'iii']

    It's not the most efficient implementation, but it's sexy.
    """
    zipped = list(iterable)
    if len(zipped) is 0:
        raise ValueError("You can't unzip an empty list.")
    return [[items[i] for items in zipped] for i in range(len(zipped[0]))]


def expand(list, getmore):
	from itertools import chain
	return chain(list, *[expand(getmore(i), getmore) for i in list])
