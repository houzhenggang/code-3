#/usr/bin/lua
--co = coroutine.create(function(a, b, c)
--        print("co ",a ,b, c)
        --coroutine.yield()
--end)

co = coroutine.create(function(a, b)
        --print("co ",a ,b, c)
        print("co",coroutine.yield())
end)
coroutine.resume(co)
coroutine.resume(co, 4, 5)
--print(coroutine.status(co))
