#!/usr/bin/env python2.6
# coding: utf-8

def laugh():
    print 'hahaha'


def h():
    print 'aaa'
    m  = yield 5
    print m
    d = yield 12
    print 'we are toget'

c = h()
m = c.next()
d = c.send('figgg')

print m, '_', d
#d = c.send('nnnnnn')


print '----------------'

def f():
    print 'aaa'
    m,n = yield
    print 'bbbbb'
    print n, type(n)
    if n < 0:
        print '<0'
    else:
        print '>0'

    print 'bb'
    d = yield 12

dd = f()
dd.next()
