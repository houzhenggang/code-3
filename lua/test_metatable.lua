#!/usr/bin/lua


--[[
local mytable = setmetatable({key1 = "val 1"},{

	__index = function(mytable, key)
		if key == "key2" then
			return "metable value"
		else
			return mytable[key]
		end
	end
})
--]]

local impl = {
	key2 = "val 2",
	fun = function (key)
		print(key)
	end
	
}

--local mytable = setmetatable({key1 = "val 1"}, { __index = { key2 = "val 2"} })
local mytable = setmetatable({key1 = "val 1"}, { __index = impl })
print(mytable.key1, mytable.key2)
mytable.fun("hello")


