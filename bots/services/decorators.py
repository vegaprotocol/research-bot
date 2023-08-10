import multiprocessing

def threaded(fn):
	def wrapper(*args, **kwargs):
		thread = multiprocessing.Process(target=fn, args=args, kwargs=kwargs)
		thread.start()
		return thread
	return wrapper