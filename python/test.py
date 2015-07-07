#!/usr/bin/env python2.6
# coding: utf-8
a = 1
def change_integer(a):
    a = a + 1
    return a

print change_integer(a)
print a

b = [1,2,3]
def change_list(b):
    b[0] = b[0] + 1
    return b

print change_list(b)
print b

class Human(object):
    def __init__(self, more_word):
        print 'we haha,more ',more_word
    laugh = 'hahaha'
    def show_laugh(self):
        print self.laugh
    def laugh_100th(self):
        for i in range(100):
            self.show_laugh()

mou = 123
li_lei = Human(mou)
#li_lei.laugh_100th()

#f = open("123.c","r")
#content = f.readline()
#print content

def func(*name):
    print type(name)
    print name

func(1,4,6)
func(1,2,3,4,54)

def func2(**name):
    print type(name)
    print name

func2(a=1,b=3)

S = 'abcdefghijk'
for i in range(0,len(S),2):
    print S[i]

for (index,char) in enumerate(S):
    print index
    print char

ta = [1,2,3]
tb = [9,8,7]
tc = ['a','b','c']

for (a,b,c) in zip(ta,tb,tc):
    print a,b,c


for line in open('123.c'):
    print line


def gen():
    a = 100
    yield a
    a = a * 8
    yield a
    yield 1000

for i in gen():
    print i


def func3(a):
    if a > 100:
        return True
    else:
        return False

print filter(func3, [10, 56, 101, 500])

class sample(object):
    def __call__(self, a):
        return a + 5

add = sample()
print (add(2))

with open("2.c","w") as f:
    print(f.closed)
    f.write("hello world ")
print(f.closed)


class bird(object):
    feather = True

class chicken(bird):
    fly = False
    def __init__(self, age):
        self.age = age
    def getAdult(self):
        if self.age > 1.0: return True
        else: return False
    adult = property(getAdult)

print '--------------'
summer  = chicken(2)
print(summer.adult)
summer.age = 0.5
print(summer.adult)
print '--------------'


print(bird.__dict__)
print(chicken.__dict__)
print(summer.__dict__)

class num(object):
    def __init__(self, value):
        self.value = value
    def getNeg(self):
        return -self.value
    def setNeg(self, value):
        self.value = -value
    def delNeg(self):
        print("value also deleted")
        del self.value
    neg = property(getNeg, setNeg,delNeg, "I am negative")

x = num(1.1)
print(x.neg)
x.neg = -22
print(x.value)
print(num.neg.__doc__)
del x.neg


