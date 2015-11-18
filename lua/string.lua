#!/usr/bin/lua
local s = "\"hello g122agg qas\""
print(s)

print(string.sub(s,1,2))
local data = "g%da"
i,j = string.find(s, data)
print(i,j)
