#!/usr/bin/env python2.6
# coding: utf-8


def bubble_sort(arry):
    n = len(arry)
    for i in range(n):
        for j in range(1, n-i):
            if arry[ j - 1 ] > arry[ j ]:
                arry[ j - 1 ], arry[ j ] = arry[ j ], arry[ j - 1 ]

    return arry

arry = [ 6, 7, 2, 1, 8]

print 'before  sort '
print arry

arry = bubble_sort(arry)
print 'after  sorted '
print arry


def select_sort(arry):
    n = len(arry)
    for i in range( n ):
        min =  i
        for j in range(i + 1, n):
            if arry[ j ] < arry[ min ]:
                    min = j

        arry[ min ] ,arry[ i ] = arry[ i ], arry[ min ]

    return arry

arry = [ 6, 7, 2, 1, 8]

print 'i11 before  sort '
print arry

arry = select_sort(arry)
print '22 after  sorted '
print arry


def insert_sort(arry):
    n = len(arry)
    for i in range(1, n):
        if arry[ i ] < arry[ i - 1]:
            tmp = arry[ i ]
            index  = i

            for j in range(i-1 , -1 , -1):
                if arry[j] > tmp:
                    arry[ j +1 ] = arry[ j ]
                    index = j
                else:
                    break
            arry[ index ] = tmp

    return arry


arry = [ 6, 7, 2, 1, 8]

print '33 before  sort '
print arry

arry = insert_sort(arry)
print '33 after  sorted '
print arry
