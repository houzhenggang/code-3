#!/usr/bin/lua

file = io.open("b.b", "r")
local buf, msg
local i = 1
local size = file:seek("end")
print(size)
file:seek("set")
buf, msg = file:read( size )
print(buf)
print(tostring(msg))
--[[
while true do
    buf, msg = file:read( 123 )
    print(i)
    i = i + 1
    print('buf = ', buf)

    if buf == nil then
        print('ERROR')
        print('msg = ',tostring(msg))
        break
    end
    print('=--------=')
    if buf == '\n' then
        print('end')
        break
    end

end

print(buf)
--]]
