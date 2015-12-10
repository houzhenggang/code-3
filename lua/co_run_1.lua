-- coroutine_test.lua 文件
--http://www.runoob.com/lua/lua-coroutine.html

co = coroutine.create(
    function(i)
        print(i);
    end
)

coroutine.resume(co, 1)   -- 1
print(coroutine.status(co))  -- dead

print("----------")

co = coroutine.wrap(
    function(i)
        print(i);
    end
)

co(1)

print("----------")

co2 = coroutine.create(
    function()
        for i=1,10 do
            print(i)
            if i == 3 then
                print(coroutine.status(co2))  --running
                print(coroutine.running()) --thread:XXXXXX
            end
            coroutine.yield()
        end
    end
)

coroutine.resume(co2) --1
coroutine.resume(co2) --2
coroutine.resume(co2) --3
coroutine.resume(co2) --4
coroutine.resume(co2) --5

print(coroutine.status(co2))   -- suspended
print(coroutine.running())   --nil
 
print("----------")

