from threading import Thread

from bots.services.service import Service


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def service_manager(services: list[Service]) -> list[Thread]:
    errors = []
    for svc in services:
        try:
            svc.check()
        except Exception as ex:
            errors += [str(ex)]

    if len(errors) > 0:
        raise Exception("services check failed: {}".format("\n".join(errors)))

    result = []
    for svc in services:
        result += [svc.start()]

    return result
