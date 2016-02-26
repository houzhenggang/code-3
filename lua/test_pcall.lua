function foo( name )

    if type(name) == 'table' then
        error('type error')
    end

    print(name)

end

local name = {} -- 33
local rst, err_msg = pcall(foo, name)
print(rst, err_msg)

