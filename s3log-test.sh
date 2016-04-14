#!/bin/bash

PYTHON=/usr/bin/python2.6
ERRLOG=errlog.py
SHOW=show
NAME=dev.partition.log
TMP_FILE_0=tmp_log_0.txt
TMP_FILE_1=tmp_log_1.txt

download_log(){
	$PYTHON $ERRLOG $SHOW $NAME > $TMP_FILE_0
}

remove_tmp_file(){
	rm -rf $TMP_FILE_0
	rm -rf $TMP_FILE_1
}

print_data(){
	cat $TMP_FILE_0 |grep need > $TMP_FILE_1
	cat $TMP_FILE_1 | awk '
		BEGIN {
			printf "ec_name "
			printf "                            "
			printf "partition_id\n"
		}

		{print $6 "  " $7}

		END{
			print "....OK!"
		}
	'
}

run(){

	download_log
	print_data
	remove_tmp_file
}


run


