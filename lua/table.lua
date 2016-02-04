#!/usr/bin/lua
--[[
local sum = {
    one = {}
}

local mid = { a = 'fad',  b = 90}
table.insert(sum.one, 'fadfaf')

for key, val in pairs(sum.one) do
    print(key, val)
end

print("len = ", #sum.one)
table.remove(sum.one, 1)
print("------------------")
print("len = ", #sum.one)
for key, val in pairs(sum.one) do
    print(key, val)
end

print('==================')
local xuan= {}
xuan[ 1 ] = {mou = 'xuan' }
xuan[ 2 ] = {mou = 'faf' }

for _, h in ipairs( xuan ) do

    print(_, h)
    if h == 'xuan' then
        print("xuan om")
    end
end
--]]
--
--
local mid = { }
table.insert(mid , {num=1, size=2})
table.insert(mid , {num=2, size=4})

for key, val in ipairs(mid) do
    print(key, val)
    print('---------')
    for ii, kk in pairs( val) do
        print(ii, kk)
    end
end

