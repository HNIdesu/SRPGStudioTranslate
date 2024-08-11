Interceptor.attach(Module.getExportByName("kernel32.dll","IsDebuggerPresent"),{
    onLeave:function(retval){
        retval.replace(ptr(0))
    }
}) 

const module=Process.getModuleByName("game.exe")
if (module){
    const baseAddress=module.base
    Interceptor.attach(baseAddress.add($read_string_rva),{
        onEnter:function(_){
            this.pText=this.context.edx
            this.position=this.context.ecx.add(4).readU32()
        },
        onLeave:function(retval){
            const pt=ptr(this.pText).readPointer();
            if(pt.toInt32()){
                const size=retval.toInt32()
                const data=pt.readByteArray(size)
                send({position:this.position},data)
            }
            
        }
    })
}