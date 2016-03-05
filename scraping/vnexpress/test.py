from multiprocessing import Process
import os


def info(title):
    print(title)
    print('Module Name: ', __name__)
    if hasattr(os, 'getppid'):
        print('Parent Process ID: ', os.getppid())
    print('Process ID: ', os.getpid())


def f(name):
    info('function f')
    print('Hello ', name)


if __name__ == '__main__':
    info('Main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()