#!/bin/bash

function usage()
{
	echo -e " sport dport\n"
}

if [ $# -ne 2 ]; then
	usage $0
	exit 0
fi


sip="10.216.25.45"
dip="10.216.25.44"

sport=$1
dport=$2

eth="eth0"

rmmod make_skb_xmit
insmod ./make_skb_xmit.ko SIP=$sip DIP=$dip SPORT=$sport DPORT=$dport ETH=$eth 
