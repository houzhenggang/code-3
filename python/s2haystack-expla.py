import os
import re
import hashlib
import errno
import genlog
import time
import base64
import errno
import genlog

import s2json
import group
import conf
import stoclient
import s2portlock
import partitionStats
import clusterinforeader
import partition
import partition_util
import s2recovery
import s2recovery_util
import haystack
import haystack_version

HAYSTACK_FOLDER = 'haystack'
SWITCH_VERSION_PREFIX = '/switch/'
SYNC_HAYSTACK_FOLDER = 'sync_haystack'

CHUNK_NUM = 12
CREATE_HAYSTACK_LIMIT = 0

logger = genlog.logger

def create(pid, gid):

    #if conf.IDC != '.dx.GZ':
    #    return

    try:

        with s2portlock.PortLock( "s2/group/%s/%s"%(pid, gid) ):

            check_haystack(pid, gid)

            s2recovery.recover_group(pid, gid)
            
			#hash_files = get_hash_files(pid, gid)
			#根据分区号（磁盘号），group id  获取文件名，存放在字典中
			#{'069e6fabca59e1ba3db034950b88aa074708cf30-99532': #'/data6/064247da00014006a370842b2b0c0467/g553698/040/069e6fabca59e1ba3034950b88aa074708cf30-99532', #'8d226c5e0c78a66db32ba0c1d465564f87adc859-69639': #'/data6/064247da00014006a370842b2b0c0467/53698/289/8d226c5e0c78a66db32ba0c1d465564f87adc859-69639', 
			#...}

            hash_files = get_hash_files(pid, gid)
            if len(hash_files) <= CREATE_HAYSTACK_LIMIT:
                logger.info( "s2haystack: part[%s] group[%s] no need to create!" % (pid, gid) )
                return

            create_haystack(pid, gid, hash_files)
			#创建完haystack之后，删除小文件 
            delete_files( hash_files.values() )
            delete_empty_hash_folders(pid, gid)

    except (s2recovery.S2RecoveryError, s2portlock.PortLockError) as e:
        logger.info( repr(e) + ' ' + pid + ' ' + str(gid) )

    except haystack_version.FileDamaged as e:
        logger.info( repr(e) + 'pid: %s, gid:%s create haystack file damaged!')
        check_haystack(pid, gid)


def check_haystack(pid, gid):

    gid = int(gid)
    hpath = get_haystack_path(pid, gid)
    h = haystack.Haystack(hpath)
    if not h.exist():
        return

    logger.info('haystack_check: pid:%s, gid:%d haystack begin checking !'%(pid, gid))

    check_global_version_file(pid, gid)
    check_haystack_files(pid, gid)

    logger.info('haystack_check: pid:%s, gid:%d haystack finish checking !'%(pid, gid))


def create_haystack(pid, gid, files):

    for fn, fpath in files.items():

        checksum = fn.split('-', 1)[0]
		#一致性 检查
        try:
            s2recovery_util.check_file_consistent(fpath, checksum)
        except s2recovery_util.FileDamaged as e:
            logger.info( repr(e) + ' ' + fpath )
            raise group.FileDamaged ( ('pid', pid), ('gid', gid), ('fn', fn) )

    needle_list = create_needle_list(files)
	#创建needle-list  格式如下 
	#[{'file_names': ['069e6fabca59e1ba3db034950b88aa074708cf30-99532'], 'data_parts': [{'path': #'/data6/064247da00014006a370842b2b0c0467/g553698/040/069e6fabca59e1ba3db034950b88aa074708cf30-99532'#, 'size': 229, 'offset': 0}], 'key': #'\x06\x9eo\xab\xcaY\xe1\xba=\xb04\x95\x0b\x88\xaa\x07G\x08\xcf0'},

    hpath = get_haystack_path(pid, gid)
    _mkdir(hpath) #创建 haystack目录

    port = partition.pid_port(pid)

    h = haystack.Haystack(hpath)

    try:

        h.create( needle_list, chunk_num = CHUNK_NUM,
                  switch_version_port = port,
                  switch_version_url = SWITCH_VERSION_PREFIX + pid + '/' + str(gid) )

    except haystack_version.VersionExisted as e:
        logger.info( 'haystack %s %s current version is existed ' % (pid, gid) )


def check_file_name(fn):

    if re.match('^[0-9a-f]{40}-[0-9]+$', fn):
        return True
    else:
        return False

def check_hash_folder_name(folder):

    if folder.isdigit() and len(folder) == 3:
        return True
    else:
        return False

def get_hash_files(pid, gid):

    files = {}

    group_path = group.get_group_path(pid, gid)

    dirs = os.listdir(group_path)

    for h in dirs:
        if check_hash_folder_name(h) == False:
            continue

        path = os.path.join(group_path, h)

        for fn in os.listdir(path):
            if check_file_name(fn) == True:
                files[fn] = os.path.join(path, fn)

    return files

def create_needle_list(files):

    needle_list = []

    for fn, fpath in files.items():

        chk = fn.split('-', 1)[0]
        key = base64.b16decode( chk.lower(), True )

        parts = [ { 'path': fpath, 'offset': 0,
                    'size': os.stat(fpath).st_size }, ]

        needle = { 'key': key, 'data_parts': parts,
                   'file_names': [ fn, ] }
		
        needle_list.append(needle)
		#(Pdb) p needle
		#{'file_names': ['069e6fabca59e1ba3db034950b88aa074708cf30-99532'], 'data_parts': [{'path': #'/data6/064247da00014006a370842b2b0c0467/g553698/040/069e6fabca59e1ba3db034950b88aa074708cf30-99#532', 'size': 229, 'offset': 0}], 'key': #'\x06\x9eo\xab\xcaY\xe1\xba=\xb04\x95\x0b\x88\xaa\x07G\x08\xcf0'}

    return needle_list

def get_haystack_path(pid, gid):

    gpath = group.get_group_path(pid, gid)

    return os.path.join(gpath, HAYSTACK_FOLDER)

def get_haystack_file_path(pid, gid, ver_num, fn_key):

    hpath = get_haystack_path(pid, gid)

    return os.path.join( hpath, 'haystack_%s_%s'%( ver_num, fn_key ) )

def delete_empty_hash_folders(pid, gid):

    gpath = group.get_group_path(pid, gid)
    dirs = os.listdir(gpath)

    for h in dirs:
        if check_hash_folder_name(h) == False:
            continue

        path = os.path.join(gpath, h)
        try:
            os.rmdir(path)
        except OSError as e:
            if len( e.args ) > 0 and e.args[ 0 ] in (errno.ENOENT, errno.ENOTEMPTY):
                pass
            else:
                raise

def filter_gids(gids, start_gid, end_gid):

    gids.sort()

    gs = [x for x in gids if x >=start_gid and x <= end_gid ]

    return gs


def check_global_version_file(pid, gid):

    if is_global_version_file_ok(pid, gid):
        return

    logger.info( 'pid: %s, gid:%s global version file damaged!'%(pid, gid) )
    hpath = get_haystack_path(pid, gid)
    h = haystack.Haystack(hpath)
    empty_file(h.global_version)

    if recovery_global_version_by_attr_file(pid, gid):
        return

    recovery_haystack(pid, gid)

def is_attribute_file_ok(fpath):

    try:
        haystack_version.read_attr_dict(fpath)
    except haystack_version.FileDamaged as e:
        logger.info( 'attribute file is damaged %s' %fpath )
        return False

    return True

def recovery_global_version_by_attr_file(pid, gid):

    hpath = get_haystack_path(pid, gid)
    h = haystack.Haystack(hpath)

    fn = get_latest_attribute_fn(hpath)
    if fn is None:
        return False

    try:
        attr_sha1 = haystack_version.get_file_sha1( os.path.join(hpath, fn) )
    except haystack_version.FileDamaged as e:
        logger.info( 'attribute file is damaged %s' %fn )
        return False

    ver_num =  fn[ len('haystack_') : -len('_attribute') ]

    h.reset_version_num(ver_num, attr_sha1)

    return True

def get_latest_attribute_fn(hpath):

    new_tm = 0
    new_fn = None

    fns = os.listdir(hpath)

    for fn in fns:

        if fn[ -len('attribute'): ] == 'attribute':
            c_time = os.stat( os.path.join(hpath, fn) ).st_ctime

            if c_time > new_tm:
                new_tm = c_time
                new_fn = fn

    if new_fn == None:
        return None

    fpath = os.path.join(hpath, new_fn)
    if is_attribute_file_ok(fpath) == False:
        return None

    return new_fn

def check_haystack_files(pid, gid):

    hpath = get_haystack_path(pid, gid)
    h = haystack.Haystack(hpath)
    ver_num = h.get_latest_version_num()

    fpath = get_haystack_file_path(pid, gid, ver_num, 'attribute')
    if is_attribute_file_ok(fpath) == False:

        logger.info( 'pid: %s gid:%s ver_num:%s attribute file damaged!'%(pid, gid, ver_num) )

        try:
            sha1 = h.get_attr_sha1(ver_num)
            recovery_haystack_file(pid, gid, ver_num, 'attribute', sha1)
        except s2recovery_util.DownloadError as e:
            logger.info( repr(e) + 'pid:%s gid:%d ver_num:%s recovery attribute fail!'%(pid, gid, ver_num) )
            recovery_haystack(pid, gid)
            return

    hfs = get_haystack_files_list(pid, gid)

    for fn_key, sha1 in hfs['files_sha1'].items():

        if not is_haystack_file_ok(pid, gid, hfs['version'], fn_key, sha1):

            logger.info( 'pid: %s gid:%s ver_num:%s fn:%s file damaged!'%(pid, gid, hfs['version'], fn_key) )

            try:
                recovery_haystack_file(pid, gid, hfs['version'], fn_key, sha1)
            except s2recovery_util.DownloadError as e:
                logger.info( repr(e) + 'pid:%s gid:%d ver_num:%s recovery fn:%s fail!'%(pid, gid, hfs['version'], fn_key) )
                break

    else:
        return

    recovery_haystack(pid, gid)

def recovery_haystack(pid, gid):

    logger.info('haystack_check: pid:%s, gid:%d, begin recovering whole haystack !'%(pid, gid))

    try:
        recovery_by_haystack(pid, gid)
    except (haystack_version.FileDamaged, s2recovery_util.DownloadError) as e:
        logger.warn( repr(e) + "pid:%s, gid:%s recovery whole haystack error!"%(pid, gid) )
    else:
        logger.info('haystack_check: pid:%s, gid:%d, finish recovering whole haystack !'%(pid, gid))
        return

    remerge_by_original_files(pid, gid)


def remerge_by_original_files(pid, gid):

    logger.info('haystack_check: pid:%s, gid:%d, begin creating new haystack by original files!'%(pid, gid))

    clear_haystack_original_fns(pid, gid)

    try:
        s2recovery.recover_group(pid, gid)
    except s2recovery.GroupIncomplete as e:
        pass

    hash_files = get_hash_files(pid, gid)
    needle_list = create_needle_list(hash_files)

    hpath = get_haystack_path(pid, gid)
    h = haystack.Haystack(hpath)  
    ver_num = h.get_latest_version_num()

    if ver_num is not None:

        try:

            ver = haystack_version.HaystackVersion(hpath, ver_num)
            needles = ver.get_valid_needle_list( ver.get_damaged_chunks_indexes() )
            needle_list.extend(needles)

        except (haystack_version.VersionNotFound, haystack_version.FileDamaged) as e:
            logger.info( repr(e) + 'version %s error!' % ver_num )

    new_num = h.create_version(needle_list, CHUNK_NUM,
                                switch_version_port = partition.pid_port(pid),
                                switch_version_url = SWITCH_VERSION_PREFIX + pid + '/' + str(gid),
                                force = True)

    delete_files( hash_files.values() )
    delete_empty_hash_folders(pid, gid)

    logger.info('haystack_check: pid:%s, gid:%d, finish creating new haystack by original files, version num is %s !'
                %(pid, gid, ver_num))

def clear_haystack_original_fns(pid, gid):

    hpath = get_haystack_path(pid, gid)
    h = haystack.Haystack(hpath)
    ver_num = h.get_latest_version_num()

    if ver_num is not None:
        empty_file( get_haystack_file_path(pid, gid, ver_num, 'original_file_names') )

def empty_file(path):

    try:
        with open( path, 'w' ) as f:
            f.write('')
    except Exception as e:
        logger.info( repr(e) + path)
        _remove(path)
        with open( path, 'w' ) as f:
            f.write('')

def is_haystack_file_ok(pid, gid, ver_num, fn_key, sha1):

    hpath = get_haystack_path(pid, gid)
    ver = haystack_version.HaystackVersion(hpath, ver_num)

    try:

        fpath = ver.get_file_path(fn_key)
        if os.path.exists(fpath):
            fsha1 = haystack_version.get_file_sha1(fpath)
        else:
            logger.info( 'pid:%s, gid:%d, fn:%s not exist !'%(pid, gid, fpath) )
            return False

    except haystack_version.FileDamaged as e:
        logger.info(repr(e)+ 'pid:%s, gid:%d haystack_%s_%s file is damaged'%(pid, gid, ver_num, fn_key))
        return False

    if sha1 != fsha1:
        logger.info( 'pid:%s, gid:%d haystack_%s_%s file is damaged, sha1 is not right!'
                    %(pid, gid, ver_num, fn_key))
        return False
    else:
        return True


def is_global_version_file_ok(pid, gid):

    hpath = get_haystack_path(pid, gid)
    h = haystack.Haystack(hpath)

    try:
        ver_num = h.get_latest_version_num()
        if ver_num is None:
            return False

    except (OSError, IOError) as e:
        logger.info(repr(e) + 'haystack_check: pid:%s, gid:%d, global_version file damage'%(pid, gid))
        return False

    if os.path.exists( get_haystack_file_path(pid, gid, ver_num, 'attribute') ):
        return True
    else:
        logger.warn( 'haystack_check: pid:%s, gid:%d, global_version file damage'%(pid, gid) )
        return False


def rename_force(src_path, dst_path):

    try:
        os.rename(src_path, dst_path)
    except Exception as e:
        logger.warn( "s2recovery: " + repr(e) )
    else:
        return

    try:
        _remove(dst_path)
        os.rename(src_path, dst_path)
    except Exception as e:
        logger.warn( "s2recovery: " + repr(e) )
    else:
        return

    try:
        rpath = os.path.join( os.path.dirname(dst_path), 'removed' )
        _mkdir(rpath)
        fn = os.path.basename(dst_path)
        os.rename(dst_path, os.path.join( rpath, fn + str( time.time() ) ))

        os.rename(src_path, dst_path)
    except Exception as e:
        logger.warn( "s2recovery: " + repr(e) )
        raise

def download_haystack_file(pid, gid, ver_num, fn_key, sha1):

    hpath = get_haystack_path(pid, gid)
    spath = os.path.join( hpath, SYNC_HAYSTACK_FOLDER )
    _mkdir(spath)

    prts = partition_util.get_sorted_prts(gid)

    for remote_prt in prts:

        remote_pid = remote_prt['partition_id']

        if _prt_dead( remote_pid ) or remote_pid == pid or remote_prt['is_del']:
            continue

        ips = _get_prt_ips(remote_pid)
        port = partition.pid_port( remote_pid, mine = False )
        uri = stoclient.get_haystack_file_uri( remote_pid,
                        {'group_id': gid, 'version': ver_num, 'fn_key': fn_key}, timeout=36000 )

        fpath = os.path.join( spath, 'haystack_%s_%s_'%(ver_num, fn_key) + str( time.time() ) )

        try:
            s2recovery_util.download(fpath, ips, port, uri, sha1)
            break
        except s2recovery_util.DownloadError as e:
            logger.info( repr(e) + " s2recovery: download pid:%s gid:%d haytack haystack_%s_%s file fail! "%
                         (remote_pid, gid, ver_num, fn_key) )
    else:
        raise

    return fpath

def recovery_haystack_file(pid, gid, ver_num, fn_key, sha1):

    src_path = download_haystack_file(pid, gid, ver_num, fn_key, sha1)
    dst_path = get_haystack_file_path(pid, gid, ver_num, fn_key)

    try:
        rename_force(src_path, dst_path)
    except Exception as e:
        _remove(src_path)
        raise

def get_haystack_files_list(pid, gid):

    ips = _get_prt_ips(pid)
    uri = stoclient.get_haystack_files_list_uri( pid, {'group_id': gid}, timeout=36000)
    port = partition.pid_port(pid, mine = False)

    buf = s2recovery_util.http_get_to_buf(ips, port, uri)
    j = s2json.load( buf )

    return j

def download_haystack_from_part(local_pid, remote_pid, gid):

    hpath = get_haystack_path(local_pid, gid)
    spath = os.path.join( hpath, SYNC_HAYSTACK_FOLDER )
    _mkdir(spath)

    files_path = {}

    hfs = get_haystack_files_list(remote_pid, gid)

    try:
        for fn_key, sha1 in hfs['files_sha1'].items():

            fpath = os.path.join( spath, 'haystack_%s_%s_'%(hfs['version'], fn_key) + str( time.time() ) )

            ips = _get_prt_ips(remote_pid)
            port = partition.pid_port( remote_pid, mine = False )

            uri = stoclient.get_haystack_file_uri( remote_pid,
                                {'group_id': gid, 'version': hfs['version'], 'fn_key': fn_key}, timeout=36000 )

            s2recovery_util.download(fpath, ips, port, uri, sha1)

            files_path[fn_key] = fpath

    except Exception as e:
        delete_files( files_path.values() )
        raise

    return hfs['version'], files_path

def download_haystack(pid, gid):

    ver_num = None
    haystack_fpaths = {}

    prts = partition_util.get_sorted_prts(gid)

    for remote_prt in prts:

        remote_pid = remote_prt['partition_id']

        if _prt_dead( remote_pid ) or remote_pid == pid or remote_prt['is_del']:
            continue

        try:
            ver_num, haystack_fpaths = download_haystack_from_part(pid, remote_pid, gid)
            break
        except s2recovery_util.DownloadError as e:
            logger.warn( repr(e) + " s2recovery: pid:%s gid:%d, download haytack fail!"%
                         (remote_pid, gid) )
    else:
        raise

    return ver_num, haystack_fpaths

def recovery_by_haystack(pid, gid):

    hpath = get_haystack_path(pid, gid)
    h = haystack.Haystack(hpath)
    old_num = h.get_latest_version_num()

    ver_num, haystack_fpaths = download_haystack(pid, gid)

    renamed_paths = []

    try:

        attr_sha1 = haystack_version.get_file_sha1( haystack_fpaths['attribute'] )

        for fn_key, src_path in haystack_fpaths.items():

            dst_path = get_haystack_file_path(pid, gid, ver_num, fn_key)
            rename_force(src_path, dst_path)

            renamed_paths.append(dst_path)

        h.reset_version_num( ver_num, attr_sha1 )

    except Exception as e:
        delete_files( renamed_paths )
        delete_files( haystack_fpaths.values() )
        raise

    switch_port = partition.pid_port(pid)
    switch_url = SWITCH_VERSION_PREFIX + pid + '/' + str(gid)
    h._switch_version(switch_port, switch_url)

    if old_num != ver_num:
        h.delete_version(old_num, switch_port, switch_url)

def delete_files(fpaths):

    for path in fpaths:

        try:
            _remove(path)
        except Exception as e:
            logger.warn( repr(e) )

def _mkdir(path):
    try:
        os.mkdir(path, 0755)
    except OSError as e:
        if e[ 0 ] == errno.EEXIST and os.path.isdir( path ):
            pass
        else:
            raise

def _remove(path):
    try:
        os.remove(path)
    except OSError as e:
        if len( e.args ) > 0 and e.args[ 0 ] == errno.ENOENT:
            pass
        else:
            raise

def _prt_dead(pid):

    sts = partitionStats.read_st(pid)
    if sts is None:
        return True

    return sts.get('fail', True)

def _get_prt_ips(pid):

    prt = clusterinforeader.get_prt( pid=pid, full=True )

    ips = prt['inn_ips'] + prt['pub_ips']

    return ips

def create_haystack_all(start_gid=0, end_gid=900000000):

    pids = partition.my_pids()

    for pid in pids:

        create_haystack_partition( pid, int(start_gid), int(end_gid) )

def create_haystack_partition(pid, start_gid=0, end_gid=900000000):

    logger.info("s2haystack: partition[%s] begin creating!" % pid)

    gids = partition.gids_on_partition(pid)

    if int(start_gid) > int(end_gid):
        raise ValueError(start_gid, end_gid)

    gids = filter_gids( gids, int(start_gid), int(end_gid) )

    for gid in gids:

        try:
            create_haystack_group(pid, gid)
        except group.GroupNotFound as e:
            logger.info( repr(e) + "s2haystack: partition[%s] group[%s]!" % (pid, gid) )

    logger.info("s2haystack: partition[%s] finish creating!" % pid)

def create_haystack_group(pid, gid):

    gid = int(gid)

    p = group.get_group_path( pid, gid )
    if not os.path.isdir( p ):
        raise group.GroupNotFound( pid, gid, p )

    logger.info( "s2haystack: part[%s] group[%d] begin creating!" % (pid, gid) )

    create(pid, gid)

    logger.info( "s2haystack: part[%s] group[%d] finish creating!" % (pid, gid) )


if __name__ == "__main__":

    import s2command
    s2command.log_level( 'info' )

    s2command.command(
        create_haystack = {
            'all' : create_haystack_all,
            'partition': create_haystack_partition,
            'group': create_haystack_group,
        },

        check_haystack = {
            'group': check_haystack,
        }
    )
