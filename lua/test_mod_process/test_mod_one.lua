
mod_one = require("mod_one")

local function test_set()

	local key = 'haha'
	mod_one.set_cache(key)

end

local function test_print()

	mod_one.print_cache()
end

test_set()
test_print()
local test_cache = {123,12}

--mod_one 相当于一个 类 ，在该进程中 mod_one就相当于一个全局变量，test_cache是 类里面的一个成员变量
--不会受到 类 外 同名 变量的影响

test_print()



