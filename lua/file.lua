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
print("--------------------")
file:seek("set")
local read_size = 0
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

--end

--[[
while true do
    buf, msg = file:read( 123 )
    print(i)
    i = i + 1
    print('buf = ', buf, 'size = ', string.len( buf ))

    if buf == nil and string.len(buf) == size then
        print('ok ',string.len(buf))
        print('msg = ',tostring(msg))
        break
    end
    print('=--------=')
    if buf == '\n' then
        print('end')
        break
    end

end

---]]
