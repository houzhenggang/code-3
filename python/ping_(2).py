#!/usr/bin/env python2.6
# coding: utf-8

"""
    Multiple ping base on: https://github.com/jedie/python-ping/

    :copyleft: 1989-2011 by the python-ping team, see AUTHORS for more details.
    :license: GNU GPL v2, see LICENSE for more details.
"""


import os
import select
import socket
import struct
import sys
import time
import logging, traceback
import threading
import random


dumbLogger = logging.Logger( '_dumb_' )
dumbLogger.setLevel( logging.CRITICAL )


if sys.platform.startswith("win32"):
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time


# ICMP parameters
ICMP_ECHOREPLY = 0 # Echo reply (per RFC792)
ICMP_ECHO = 8 # Echo request (per RFC792)
ICMP_MAX_RECV = 2048 # Max size of incoming buffer

idlock = threading.RLock()
SEED = random.randint( 1, 65535 )
autoincr = 0


class PingError( Exception ): pass
class PingTimeout( PingError ): pass


class Ping( object ):

    def __init__( self, destinations, count=3, deadline=999999999999,
                  timeout=1000, packet_size=55, concurrent=10,
                  logger=dumbLogger ):

        self.update_time()

        self.deadline = self.curtime + deadline / 1000.0
        self.timeout = timeout / 1000.0
        self.packet_size = packet_size
        self.nfree = min( [ concurrent, len( destinations ) ] )
        self.logger = logger

        self.pending = {}
        self.queue = []
        self.finished = {}
        self.dests = []
        self.total = count * len( destinations )
        self.i = 0

        try:
            ips = [ to_ip( x ) for x in destinations ]
        except socket.gaierror as e:
            raise

        hostip = dict( zip( destinations, ips ) )


        peers = {}
        for dest, ip in hostip.items():

            peers[ ip ] = {
                    'ip': ip,
                    'id': gen_id(),
                    'dest': dest,
                    'seq': 0,
                    'time_start': None,
            }

            self.finished[ ip ] = {
                    'ip': ip,
                    'id': peers[ ip ][ 'id' ],
                    'dest': dest,
                    'spent':[],
            }

        self.dests = peers.values()


    def update_time( self ):
        self.curtime = default_timer()


    def run( self ):

        self.update_time()
        self.make_sock()

        while self.total > 0 and self.curtime < self.deadline:
            if self.send_one():
                continue

            self.handle_response()
            self.update_time()

        while self.pending != {} and self.curtime < self.deadline:
            self.handle_response()
            self.update_time()

        return self.make_result()


    def make_result( self ):

        rst = {}
        for ip, e in self.finished.items():
            valid = [ x for x in e[ 'spent' ] if x is not None ]
            lvalid = len( valid )
            o = {
                    'dest': e[ 'dest' ],
                    'ip': ip,
                    'avg': int(sum( valid, 0.0 ) / lvalid) if lvalid else None,
                    'sent': len( e[ 'spent' ] ),
                    'recv': lvalid,
            }
            o[ 'loss' ] = o[ 'sent' ] - o[ 'recv' ]
            rst[ ip ] = o

        return rst


    def make_sock( self ):

        try:
            self.sock = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_RAW,
                    socket.getprotobyname("icmp"))

        except socket.error, (errno, msg):
            if errno == 1:
                etype, evalue, etb = sys.exc_info()
                evalue = etype(
                    "%s - Note that ICMP messages can only be send from processes running as root." % evalue
                )
                raise etype, evalue, etb
            raise


    def finish_one( self, k, v ):

        ent = self.pending[ k ]
        ip = ent[ 'ip' ]

        self.finished[ ip ][ 'spent' ].append( v )
        del self.pending[ k ]

        self.nfree += 1


    def handle_response( self ):

        starttime = default_timer()

        while len( self.queue ) > 0 \
                and self.queue[ 0 ][ 'time_start' ] + self.timeout < starttime:

            e = self.queue.pop( 0 )
            k = '{ip}-{id}-{seq}'.format( **e )
            if k in self.pending:
                self.finish_one( k, None )


        while True:

            try:
                # addr, ip_header, icmp_header = self.receive_one()
                addr, icmp_header = self.receive_one()

                endtime = default_timer()

                if self.deadline < endtime:
                    return

                if starttime + self.timeout < endtime:
                    raise PingTimeout()

            except PingTimeout, e:

                starttime = default_timer()

                timeouts = self.pending.items()
                timeouts.sort( key=lambda x: x[1][ 'time_start' ] )
                for k, ent in timeouts:
                    self.finish_one( k, None )

                return

            else:

                ip, port = addr
                k = '{ip}-{id}-{seq}'.format( ip=ip, **icmp_header )

                if k not in self.pending:
                    continue

                e = self.pending[ k ]
                starttime = default_timer()

                spent = int( endtime * 1000 - e[ 'time_start' ] * 1000 )
                self.finish_one( k, spent )

                return


    def _make_header( self, e, checksum ):
        return struct.pack(
            "!BBHHH", ICMP_ECHO, 0, checksum, e[ 'id' ], e[ 'seq' ]
        )

    def send_one( self ):

        if self.nfree == 0:
            return False

        des = self.dests[ self.i ]
        e = self.make_ent( des )
        k = '{ip}-{id}-{seq}'.format( **e )

        self.pending[ k ] = e
        self.queue.append( e )

        self.i = ( self.i + 1 ) % len( self.dests )
        self.nfree -= 1
        self.total -= 1


        # Make a dummy header with a 0 checksum.
        header = self._make_header( e, 0 )

        padBytes = []
        startVal = 0x42
        for i in range(startVal, startVal + (self.packet_size)):
            padBytes += [(i & 0xff)]  # Keep chars in the 0-255 range
        data = bytes(padBytes)

        checksum = calculate_checksum(header + data)
        header = self._make_header( e, checksum )

        packet = header + data


        e[ 'time_start' ] = default_timer()

        for ii in range( 3 ):
            try:
                self.sock.sendto(packet, (e[ 'ip' ], 1))
                break
            except socket.error as err:
                self.logger.info( repr( err ) )
                pass

        return True


    def make_ent( self, e ):

        e[ 'seq' ] += 1

        return { 'ip':e[ 'ip' ],
                 'dest': e[ 'dest' ],
                 'id':e[ 'id' ],
                 'seq':e[ 'seq' ],
        }


    def receive_one(self):

        starttime = default_timer()

        while True:

            evin, evout, everr = select.select([self.sock], [], [], self.timeout )

            if evin == []:
                self.logger.info( "select timeout" )
                raise PingTimeout()

            if starttime + self.timeout < default_timer():
                raise PingTimeout()

            packet_data, address = self.sock.recvfrom( ICMP_MAX_RECV )


            # ip_header = header2dict(
            #     names=[
            #         "version", "type", "length",
            #         "id", "flags", "ttl", "protocol",
            #         "checksum", "src_ip", "dest_ip"
            #     ],
            #     struct_format="!BBHHHBBHII",
            #     data=packet_data[:20]
            # )
            icmp_header = header2dict(
                names=[
                    "type", "code", "checksum",
                    "id", "seq"
                ],
                struct_format="!BBHHH",
                data=packet_data[20:28]
            )

            if icmp_header[ 'type' ] != ICMP_ECHOREPLY:
                continue


            # packet_size = len(packet_data) - 28
            # ip_in_pack = socket.inet_ntoa(struct.pack("!I", ip_header["src_ip"]))

            return address, icmp_header


def calculate_checksum(source_string):
    """
    A port of the functionality of in_cksum() from ping.c
    Ideally this would act on the string as a series of 16-bit ints (host
    packed), but this works.
    Network data is big-endian, hosts are typically little-endian
    """
    countTo = (int(len(source_string) / 2)) * 2
    sum = 0
    count = 0

    # Handle bytes in pairs (decoding as short ints)
    loByte = 0
    hiByte = 0
    while count < countTo:
        if (sys.byteorder == "little"):
            loByte = source_string[count]
            hiByte = source_string[count + 1]
        else:
            loByte = source_string[count + 1]
            hiByte = source_string[count]
        sum = sum + (ord(hiByte) * 256 + ord(loByte))
        count += 2

    # Handle last byte if applicable (odd-number of bytes)
    # Endianness should be irrelevant in this case
    if countTo < len(source_string): # Check for odd length
        loByte = source_string[len(source_string) - 1]
        sum += ord(loByte)

    sum &= 0xffffffff # Truncate sum to 32 bits (a variance from ping.c, which
                      # uses signed ints, but overflow is unlikely in ping)

    sum = (sum >> 16) + (sum & 0xffff)    # Add high 16 bits to low 16 bits
    sum += (sum >> 16)                    # Add carry from above (if any)
    answer = ~sum & 0xffff                # Invert and truncate to 16 bits
    answer = socket.htons(answer)

    return answer


def is_ip4( ip ):

    ip = ip.split( '.' )

    for s in ip:
        if s == '':
            continue

        if not s.isdigit():
            return False

        i = int( s )
        if i<0 or i>255:
            return False

    return len( ip ) == 4


def to_ip(addr):
    if is_ip4(addr):
        return addr

    ip = socket.gethostbyname(addr)
    return ip


def gen_id():
    global autoincr
    with idlock:
        autoincr += 1
        return ( ( SEED + autoincr ) * 2654435769 ) % ( 1 << 16 )


def header2dict( names, struct_format, data ):
    unpacked_data = struct.unpack(struct_format, data)
    return dict(zip(names, unpacked_data))



if __name__ == '__main__':
    import pprint

    logger = logging.Logger( 'xx' )
    logger.addHandler( logging.StreamHandler( sys.stdout ) )
    logger.setLevel( logging.INFO )

    hosts = [
	'172.16.48.13','172.16.48.23','172.16.164.252','172.16.108.2','172.16.108.3','172.16.108.5','172.16.108.6','172.16.108.12','172.16.108.13','172.16.108.41','172.16.108.42','172.16.108.43','172.16.108.51','172.16.108.52','172.16.108.53','172.16.108.54','172.16.108.55','172.16.108.56','172.16.108.57','172.16.108.58','172.16.108.59','172.16.108.60','172.16.108.62','172.16.108.63','172.16.108.68','172.16.108.69','172.16.108.73','172.16.108.74','172.16.108.75','172.16.108.76','172.16.108.77','172.16.108.79','172.16.108.80','172.16.108.82','172.16.108.85','172.16.108.89','172.16.108.92','172.16.108.93','172.16.108.94','172.16.108.96','172.16.108.97','172.16.108.98','172.16.108.99','172.16.108.100','172.16.108.103','172.16.108.107','172.16.108.108','172.16.108.109','172.16.108.111','172.16.108.112','172.16.108.113','172.16.108.114','172.16.108.115','172.16.108.116','172.16.108.119','172.16.108.121','172.16.108.128','172.16.108.129','172.16.108.130','172.16.108.131','172.16.108.135','172.16.108.136','172.16.108.139','172.16.108.142','172.16.108.143','172.16.108.144','172.16.108.145','172.16.108.146','172.16.108.148','172.16.108.149','172.16.108.150','172.16.108.151','172.16.108.152','172.16.108.153','172.16.108.164','172.16.108.165','172.16.108.171','172.16.108.181','172.16.108.183','172.16.108.184','172.16.108.186','172.16.108.189','172.16.108.191','10.71.216.1','10.71.216.11','10.71.216.12','10.71.216.13','10.71.216.14','10.71.216.15','10.71.216.17','10.71.216.18','10.71.216.19','10.71.216.20','10.71.216.21','10.71.216.22','10.71.216.23','10.71.216.24','10.71.216.25','10.71.216.26','10.71.216.27','10.71.216.28','10.71.216.29','10.71.216.32','10.71.216.33','10.71.216.34','10.71.216.35','10.71.216.37','10.71.216.38','10.71.216.39','10.71.216.41','10.71.216.42','10.71.216.43','10.71.216.44','10.71.216.45','10.71.216.47','10.71.216.48','10.71.216.51','10.71.216.52','10.71.216.53','10.71.216.54','10.71.216.55','10.71.216.56','10.71.216.57','10.71.216.59','10.71.216.60','10.71.216.61','10.71.216.62','10.71.216.63','10.71.216.64','10.71.216.65','10.71.216.67','10.71.216.68','10.71.216.69','10.71.216.70','10.71.216.71','10.71.216.73','10.71.216.74','10.71.216.75','10.71.216.76','10.71.216.77','10.71.216.82','10.71.216.83','10.71.216.88','10.71.216.90','10.71.216.91','10.71.216.92','10.71.216.93','10.71.216.95','10.71.216.96','10.71.216.97','10.71.216.98','10.71.216.99','10.71.216.100','10.71.216.101','10.71.216.102','10.71.216.103','10.71.216.104','10.71.216.105','10.71.216.106','10.71.216.107','10.71.216.108','10.71.216.109','10.71.216.110','10.71.216.112','10.71.216.113','10.71.216.114','10.71.216.115','10.71.216.119','10.71.216.122','10.71.216.128','10.71.216.130','10.71.216.131','10.71.216.132','10.71.216.136','10.71.216.138','10.71.216.143','10.71.216.146','10.71.216.150','10.71.216.158','10.71.216.164','10.71.216.173','10.71.216.175','10.71.216.183','10.71.216.185','10.71.216.187','10.71.216.198','10.71.216.199','10.71.216.205','10.71.216.207','10.71.216.208','10.71.216.219','10.71.216.220','10.71.216.223','10.71.216.230','10.71.216.233','10.71.216.237','10.71.216.243','10.71.216.247','10.71.216.248','10.71.216.249','10.71.216.253','10.71.1.14','10.71.1.15','10.71.1.16','10.71.1.18','10.71.1.30','10.71.1.36','10.71.1.45','10.71.1.51','10.71.1.53','10.71.1.62','10.71.1.64','10.71.1.65','10.71.1.66','10.71.1.72','10.71.1.85','10.71.1.88','10.71.1.92','10.71.1.94','10.71.1.110','10.71.1.121','10.71.1.129','10.71.1.132','10.71.1.141','10.71.1.142','10.71.1.143','10.71.1.150','10.71.1.162','10.71.1.169','10.71.1.188','10.71.1.194','10.71.1.200','10.71.1.229','10.71.1.231','10.71.1.233','10.71.1.237','10.71.1.239','10.71.1.245','10.71.1.246','10.71.1.247','10.71.1.248','10.71.2.1','10.71.2.7','10.71.2.12','10.71.2.13','10.71.2.17','10.71.2.27','10.71.2.33','10.71.2.36','10.71.2.39','10.71.2.44','10.71.2.46','10.71.2.48','10.71.2.49','10.71.2.51','10.71.2.57','10.71.2.65','10.71.2.68','10.71.2.69','10.71.2.72','10.71.2.79','10.71.2.84','10.71.2.87','10.71.2.94','10.71.2.97','10.71.2.101','10.71.2.103','10.71.2.108','10.71.2.119','10.71.2.120','10.71.2.137','10.71.2.155','10.71.2.156','10.71.2.166','10.71.2.168','10.71.2.169','10.71.2.181','10.71.2.191','10.71.2.192','10.71.2.195','10.71.2.199','10.71.2.207','10.71.2.211','10.71.2.215','10.71.2.216','10.71.2.217','10.71.2.219','10.71.2.223','10.71.2.224','10.71.2.226','10.71.2.230','10.71.2.233','10.71.2.235','10.71.2.240','10.71.2.245','10.71.2.247','10.71.2.248','10.71.2.250','10.71.2.252','176.16.177.7','176.16.177.15','176.16.177.17','176.16.177.18','176.16.177.19','176.16.177.21','176.16.177.23','176.16.177.29','176.16.177.30','176.16.177.39','176.16.177.40','176.16.177.42','176.16.177.43','176.16.177.48','176.16.177.49','176.16.177.51','176.16.177.53','176.16.177.55','176.16.177.56','176.16.177.60','176.16.177.64','176.16.177.65','176.16.177.68','176.16.177.70','176.16.177.72','176.16.177.74','176.16.177.75','176.16.177.78','176.16.177.80','176.16.177.85','176.16.177.87','176.16.177.88','176.16.177.90','176.16.177.95','176.16.177.96','176.16.177.98','176.16.177.101','176.16.177.102','176.16.177.105','176.16.177.107','176.16.177.108','176.16.177.109','176.16.177.110','176.16.177.112','176.16.177.113','176.16.177.114','176.16.177.117','176.16.177.120','176.16.177.125','176.16.177.126','176.16.177.127','176.16.177.131','176.16.177.132','176.16.177.134','176.16.177.137','176.16.177.140','176.16.177.143','176.16.177.152','176.16.177.157','176.16.177.159','176.16.177.162','176.16.177.166','176.16.177.168','176.16.177.173','176.16.177.174','176.16.177.175','176.16.177.176','176.16.177.185','176.16.177.187','176.16.177.191','176.16.177.192','176.16.177.193','176.16.177.197','176.16.177.200','176.16.177.201','176.16.177.203','176.16.177.204','176.16.177.206','176.16.177.208','176.16.177.210','176.16.177.216','176.16.177.221','176.16.177.222','176.16.177.223','176.16.177.226','176.16.177.227','176.16.177.230','176.16.177.231','176.16.177.232','176.16.177.235','176.16.177.237','176.16.177.238','176.16.177.240','176.16.177.241','176.16.177.243','176.16.177.245','176.16.177.247','176.16.177.249','176.16.177.250','172.16.113.1','172.16.113.7','172.16.113.8','172.16.113.9','172.16.113.10','172.16.113.14','172.16.113.15','172.16.113.16','172.16.113.17','172.16.113.21','172.16.113.22','172.16.113.23','172.16.113.24','172.16.113.25','172.16.113.30','172.16.113.31','172.16.113.33','172.16.113.35','172.16.113.36','172.16.113.43','172.16.113.44','172.16.113.46','172.16.113.50','172.16.113.55','172.16.113.56','172.16.113.57','172.16.113.58','172.16.113.60','172.16.113.68','172.16.113.69','172.16.113.70','172.16.113.74','172.16.113.76','172.16.113.77','172.16.113.78','172.16.113.81','172.16.113.91','172.16.113.94','172.16.113.96','172.16.113.99','172.16.113.104','172.16.113.105','172.16.113.107','172.16.113.111','172.16.113.112','172.16.113.116','172.16.113.118','172.16.113.119','172.16.113.121','172.16.113.126','172.16.113.127','172.16.113.132','172.16.113.133','172.16.113.134','172.16.113.137','172.16.113.138','172.16.113.143','172.16.113.145','172.16.113.159','172.16.113.162','172.16.113.163','172.16.113.164','172.16.113.165','172.16.113.167','172.16.113.172','172.16.113.178','172.16.113.179','172.16.113.180','172.16.113.181','172.16.113.188','172.16.113.189','172.16.113.190','172.16.113.192','172.16.113.194','172.16.113.196','172.16.113.202','172.16.113.208','172.16.113.210','172.16.113.211','172.16.113.212','172.16.113.213','172.16.113.215','172.16.113.216','172.16.113.218','172.16.113.221','172.16.113.222','172.16.113.223','172.16.113.224','172.16.113.231','172.16.113.252','172.16.113.253','172.16.113.254','172.16.187.1','172.16.187.12','172.16.187.13','172.16.187.14','172.16.187.15','172.16.187.16','172.16.187.18','172.16.187.19','172.16.187.20','172.16.187.21','172.16.187.22','172.16.187.23','172.16.187.24','172.16.187.26','172.16.187.27','172.16.187.28','172.16.187.29','172.16.187.30','172.16.187.31','172.16.187.32','172.16.187.33','172.16.187.34','172.16.187.35','172.16.187.36','172.16.187.37','172.16.187.38','172.16.187.39','172.16.187.40','172.16.187.41','172.16.187.42','172.16.187.43','172.16.187.44','172.16.187.45','172.16.187.46','172.16.187.50','172.16.187.51','172.16.187.52','172.16.187.53','172.16.187.54','172.16.187.55','172.16.187.57','172.16.187.65','172.16.187.67','172.16.187.75','172.16.187.80','172.16.187.84','172.16.187.86','172.16.187.91','172.16.187.96','172.16.187.99','172.16.187.122','172.16.187.124','172.16.187.127','172.16.187.130','172.16.187.132','172.16.187.139','172.16.187.147','172.16.187.149','172.16.187.156','172.16.187.157','172.16.187.162','172.16.187.167','172.16.187.175','172.16.187.178','172.16.187.179','172.16.187.182','172.16.187.183','172.16.187.191','172.16.187.198','172.16.187.206','172.16.187.207','172.16.187.221','172.16.187.222','172.16.187.223','172.16.187.231','172.16.187.239','172.16.187.247','172.16.187.249','10.71.5.1','10.71.5.13','10.71.5.15','10.71.5.21','10.71.5.24','10.71.5.31','10.71.5.40','10.71.5.48','10.71.5.49','10.71.5.51','10.71.5.75','10.71.5.76','10.71.5.77','10.71.5.79','10.71.5.80','10.71.5.84','10.71.5.90','10.71.5.92','10.71.5.109','10.71.5.110','10.71.5.129','10.71.5.141','10.71.5.142','10.71.5.145','10.71.5.148','10.71.5.149','10.71.5.155','10.71.5.158','10.71.5.172','10.71.5.173','10.71.5.178','10.71.5.179','10.71.5.180','10.71.5.185','10.71.5.197','10.71.5.200','10.71.5.204','10.71.5.214','10.71.5.220','10.71.5.223','10.71.5.227','10.71.5.230','10.71.5.231','10.71.5.234','10.71.5.235','10.71.5.236','10.71.5.238','10.71.5.239','10.71.5.240'
	]

    p = Ping( hosts, count=5, concurrent=40, logger = logger )
    rst = p.run()

    pprint.pprint( rst )
