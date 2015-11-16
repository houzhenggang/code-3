#!/usr/bin/lua

local restore_sess = {
    running_member_queue = {},
    member_queue = {},
    threads = {},
    nr_ths = 2
}

if restore_sess.member_queue ~= nil then
    print('no eq nil')
end
