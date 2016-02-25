
local _M = {}
local test_cache = {}

function _M.set_cache(key)

	test_cache[key] = key
	--test_cache[key] = test_cache[key] or {}
	--table.insert(test_cache[key], key)
end

function _M.get_cache(key)

	return test_cache[key]
end

function _M.print_cache(cache)

	if cache == nil then
		cache = test_cache
	end
	
	for ii, val in pairs(cache) do

		print(ii, val)
	end
end

local function test()

	local test_msg = {'hello', 'word', 'haha'}
	local val 

	for ii, val in pairs(test_msg) do
		_M.set_cache(val)
		val = _M.get_cache(val)

		--print('val = ',val)
	end

end

--test()
--_M.print_cache()

return _M
