#include <lua.h>
#include <lauxlib.h>

#include <stdlib.h> /* For function exit() */
#include <stdio.h> /* For input/output */

void bail(lua_State *L, char *msg){
    fprintf(stderr, "\nFATAL ERROR:\n %s: %s\n\n",
        msg, lua_tostring(L, -1));
    exit(1);
}
int lua_func_from_c(lua_State *L)
{
    printf("This is C\n");
    int argc = lua_gettop(L);    /* number of arguments */
    const char * str = lua_tostring(L,1);    /* the first argument: string */
    int num = lua_tonumber(L,2); /* the second argument: number */
    
    printf("The first argument: %s\n", str);
    printf("The second argument: %d\n", num);

    lua_getglobal(L,"global_var");
    const char * global_str = lua_tostring(L,-1);
    printf("global_var is %s\n", global_str);

    int the_second_ret = 2*num;
    lua_pushstring(L, "the first return");
    lua_pushnumber(L, the_second_ret);
    return 2;            /* tell lua how many variables are returned */
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
    lua_register(L, "lua_func_from_c", lua_func_from_c);

    if( luaL_loadfile(L,argv[1]) ) 	/* Only load the lua script file */
        bail(L, "luaL_loadfile() failed");

    if( lua_pcall(L,0,0,0) ) 		/* Run the loaded lua file */
        bail(L, "lua_pcall() failed"); 
    lua_close(L);                 	/* Close the lua state variable */    

}
