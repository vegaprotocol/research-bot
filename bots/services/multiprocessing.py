import multiprocessing

from bots.services.service import Service

def threaded(fn):
	def wrapper(*args, **kwargs):
		thread = multiprocessing.Process(target=fn, args=args, kwargs=kwargs)
		thread.start()
		return thread
	return wrapper

def service_manager(services: list[Service]) -> list[multiprocessing.Process]:
	errors = []
	for svc in services:
		try:
			if callable(getattr(svc, 'check', None)):
				svc.check()
		except Exception as ex:
			errors += [str(ex)]

	if len(errors) > 0:
		raise Exception("services check failed: {}".format("\n".join(errors)))

	result = []
	for svc in services:
		result += [svc.start()]

	return result