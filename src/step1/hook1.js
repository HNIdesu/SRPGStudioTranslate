Interceptor.attach(Module.getExportByName("kernel32.dll","IsDebuggerPresent"),{
    onLeave:function(retval){
        retval.replace(ptr(0))
    }
})

const module=Process.getModuleByName("game.exe")

function compareArrayBuffers(buffer1, buffer2) {
    for (let i = 0; i < buffer1.length; i++) {
        if (buffer1[i] !== buffer2[i]) {
            return false;
        }
    }
    return true;
}
function findFunctionStart(address){
    let current=ptr(address);
    while(true){
        const b1=current.sub(2).readU8();
        const b2=current.sub(1).readU8();
        if(b1==0x57 && b2==0x56)
            return current.sub(2);
        else
            current=current.sub(1);
    }
}

const advapi32=Module.load("advapi32.dll")
Interceptor.attach(advapi32.getExportByName("CryptDecrypt"),{
    onEnter:function(args){
        this.pBuffer=args[4]
        this.pBufferSize=args[5]
    },
    onLeave:function(){
        const bufferSize=ptr(this.pBufferSize).readU32();
        if(bufferSize<=16)return
        const header=ptr(this.pBuffer).readByteArray(16)
        if(!compareArrayBuffers(new Uint8Array(header),$project_header))return
        MemoryAccessMonitor.enable({
            base: ptr(this.pBuffer).add($str_offset),
            size: 1
        },{
            onAccess:function(detials){
                send({
                    type:"address",
                    msg:findFunctionStart(detials.from).sub(module.base).toInt32()
                })
            }
        })
    }
})
