Interceptor.attach(Module.getExportByName("kernel32.dll","IsDebuggerPresent"),{
    onLeave:function(retval){
        retval.replace(ptr(0))
    }
})

const module=Process.getModuleByName("game.exe")

function findFunctionStart(address){
    let current=ptr(address);
    while(true){
        const b1=current.sub(3).readU8();
        const b2=current.sub(2).readU8();
        const b3=current.sub(1).readU8();
        if(b1==0x55 && b2==0x8B && b3==0xEC)
            return current.sub(3);
        else
            current=current.sub(1);
    }
}
Interceptor.attach(module.base.add($func_offset),{
    onLeave:function(retval){
        if(retval.readUtf16String()==="$keyword")
            send({
                type:"address",
                msg:findFunctionStart(this.returnAddress).sub(module.base).toInt32()
            })
    }
})