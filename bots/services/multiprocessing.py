import multiprocessing

from bots.services.service import Service

def threaded(fn):
	def wrapper(*args, **kwargs):
		thread = multiprocessing.Process(target=fn, args=args, kwargs=kwargs)
		thread.start()
		return thread
	return wrapper

def service_manager(services: list[Service]) -> list[multiprocessing.Process]:
	result = []
	for svc in services:
		result += [svc.start()]

	return result