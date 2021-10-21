import time


def timeit(f):
    '''
    Measures time of function execution
    '''
    def wrap(*args):
        time1 = time.time()
        _ = f(*args)
        time2 = time.time()
        print(f"\n {f.__name__} worked {round(time2 - time1, 3)} seconds")
    return wrap