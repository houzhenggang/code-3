#!/usr/bin/lua

file = io.open("b.b", "r")
local buf, msg
local i = 1
local size = file:seek("end")
print(size)
file:seek("set")


buf, msg = file:read( 3 )
if buf == nil then
    print("buf = nil , msg = ", msg)
end

--[[

while true do
    buf, msg = file:read( 3 )
    print(i)
    i = i + 1
    print('buf = ', buf, 'size = ', string.len( buf ))
    read_size = read_size  + string.len( buf )
    print("read_size = ", read_size)
    if buf ~= nil and size == read_size then
        print("nil ok size = ", string.len( buf ) )
        print("msg = ", msg )
        break
    end
end
--]]
