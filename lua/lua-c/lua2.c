#include <lua.h>
#include <lauxlib.h>

#include <stdlib.h> /* For function exit() */
#include <stdio.h> /* For input/output */

void bail(lua_State *L, char *msg){
    fprintf(stderr, "\nFATAL ERROR:\n %s: %s\n\n",
        msg, lua_tostring(L, -1));
    exit(1);
}
int lua_func_from_c_func(lua_State *L)
{
    printf("This is C\n");
    return 0;
}
int main(int argc, const char *argv[])
{
    if(argc != 2)
    {
        return 1;
    }
    lua_State *L = luaL_newstate(); 	/* Create new lua state variable */
    
    /* Load Lua libraries, otherwise, the lua function in *.lua will be nil */
    luaL_openlibs(L); 
    
    /* register new lua function in C */
    lua_register(L, "lua_func_from_c", lua_func_from_c_func);

    if( luaL_loadfile(L,argv[1]) ) 	/* Only load the lua script file */
        bail(L, "luaL_loadfile() failed");

    if( lua_pcall(L,0,0,0) ) 		/* Run the loaded lua file */
        bail(L, "lua_pcall() failed"); 
    lua_close(L);                 	/* Close the lua state variable */    

    return 0;
}