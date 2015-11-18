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
