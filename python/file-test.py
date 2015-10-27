#!/usr/bin/env python2.6
# coding: utf-8

import sys
import time
import logging
import os

import core2cli
import genlog
import serviceconf.ec_status as cnf


SEVEN_DAYS = 7 * 86400
TWENTY_DAYS = 20 * 86400
DEFAULT_INTERVAL = 30 * 60
DEFAULT_SLEEP_TIME = 30 * 60
RESTORE_TIME_THRESHOLD = 24 * 60 *60


logger = genlog.logger


def write_file(fn, buf, offset = 0):

    fd = os.open( fn, os.O_WRONLY | os.O_CREAT )

    try:
        os.fchmod(fd, 0644)
        os.lseek(fd, offset, os.SEEK_SET)
        os.write(fd, buf)
        os.fsync(fd)
    finally:
        os.close(fd)

def read_file(fpath):

    fd = os.open(fpath, os.O_RDONLY)

    try:
        size = os.stat(fpath).st_size
        buf = read_buf(fd, size, fpath)

    finally:
        os.close(fd)

    return buf

def read_buf(fd, size, fpath):

    buf = ''

    try:

        while size > 0:

            tmp = os.read(fd, size)
            if tmp == '':
                break

            buf += tmp
            size -= len(tmp)

        if size != 0:
            logger.error( "read file error")

    except (IOError, OSError) as e:
            logger.error( repr(e) )

    return buf

def _init():

    if not os.path.exists(cnf.LAST_READ_TIME_PATH):
        print 'aaaaaaaa'
        now = int(time.time())
        last_read_time = now - TWENTY_DAYS
        cnf.LAST_READ_TIME = last_read_time
        fpath = cnf.LAST_READ_TIME_PATH
        write_file(fpath, str(last_read_time))

    else:

        print 'bbbbbb'
        fpath = cnf.LAST_READ_TIME_PATH
        cnf.LAST_READ_TIME = read_file(fpath)

    if not os.path.exists(cnf.LAST_RM_TIME_PATH):

        print 'cccccc'
        now = int(time.time())
        last_rm_time =  now - TWENTY_DAYS
        cnf.LAST_RM_TIME = last_rm_time
        fpath = cnf.LAST_RM_TIME_PATH
        write_file(fpath, str(last_rm_time))

    else:

        print 'dddddd'
        fpath = cnf.LAST_RM_TIME_PATH
        cnf.LAST_RM_TIME = read_file(fpath)

def run():

    logger.info( "run")
    print '1 = ',cnf.LAST_READ_TIME_PATH
    print '2 = ',cnf.LAST_RM_TIME_PATH
    print '3 = ',cnf.PID_PATH

    print 'LAST_RM_TIME = ', cnf.LAST_RM_TIME
    print 'LAST_READ_TIME = ', cnf.LAST_READ_TIME

    _init()
    print '2 LAST_RM_TIME = ', cnf.LAST_RM_TIME
    print '2 LAST_READ_TIME = ', cnf.LAST_READ_TIME

    '''
    while True:

        now = int(time.time())

        if LAST_READ_TIME < now - DEFAULT_INTERVAL:

            analyse_data_from_database(LAST_READ_TIME)
            LAST_READ_TIME = LAST_READ_TIME + DEFAULT_INTERVAL
            record_last_read_time_to_local()

        else if LAST_RM_TIME < now - SEVEN_DAYS:

            remove_data_from_database()
            LAST_RM_TIME = LAST_RM_TIME + DEFAULT_INTERVAL
            record_last_rm_time_to_local()

        else:
            time.sleep( DEFAULT_SLEEP_TIME )

    '''

if __name__ == "__main__":

    logger.setLevel( logging.INFO )
    run()
