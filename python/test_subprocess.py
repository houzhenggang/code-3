#!/usr/bin/env python2.6
# coding: utf-8

import subprocess

child = subprocess.Popen(["ping", "-c", "5", "www.baidu.com"])
child.wait()
print("parent process")


child1 = subprocess.Popen(["ls", "-l"], stdout=subprocess.PIPE)
child2 = subprocess.Popen(["wc"], stdin=child1.stdout, stdout=subprocess.PIPE)
out = child2.communicate()
print(out)
