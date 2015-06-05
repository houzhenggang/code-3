#!/bin/bash - 
#===============================================================================
#   DESCRIPTION: 
#	analyse ping's log
#===============================================================================

ping_dest=(123.125.104.197 114.112.73.194 61.135.169.125)

for ip in ${ping_dest[@]};do
		sent=`cat log |grep $ip|grep sent|wc -l`
		recv=`cat log|grep $ip|grep recv|wc -l`
		echo $ip $sent $recv
		avg=`cat log|grep $ip |awk 'BEGIN{sum=0.0} {if(match($6, "rtt")) sum += $7 }
									  END{print sum}'`
		
		loss=`expr $sent - $recv`
		avg=`expr $avg / $recv`
		echo $ip $sent $recv $loss $avg

done
