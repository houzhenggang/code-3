#!/usr/bin/lua
impl = {
"dddd","sss",
a=123,
["wee"]="one",
["two"]="linux"
}

print("-------pairs------")
for key, val in pairs(impl) do
    print(key, val)
end
print("-------ipairs------")
for key, val in ipairs(impl) do
    print(key, val)
end
print("-function with impl---")
impl.get_print = function(impl, a, b)
    --print("a and b",a,b)
    return a,b
end

aa, bb = impl:get_print(1,2)
print(aa, bb)

print("-function without impl---")
impl.get_print = function(a, b)
    --print("a and b",a,b)
    return a,b
end

aa, bb = impl.get_print(1,2)
print(aa, bb)
