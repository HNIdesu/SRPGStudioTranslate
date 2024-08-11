import frida
import sys
import os.path as Path
import json
import os
from queue import Queue

class DetectHandler:
    def __init__(self,args):
        self.args=args

    def resource_path(file_name):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS,"step1", file_name)
        return os.path.join(Path.dirname(__file__), file_name)

    def process(self):
        args=self.args
        result_queue=Queue[int](1)
        game_directory=args.game_directory
        os.chdir(game_directory)
        keyword:str=args.keyword
        project_path=args.project_path
        offset=-1
        project_header:list[int]=[]
        with open(project_path,"rb") as br:
            header=br.read(16)
            for b in header:
                project_header.append(b)
            offset=br.read().find(keyword.encode("utf-16le"))+12

        def index(inner_func_addr:int):
            if inner_func_addr==-1:
                pid=frida.get_local_device().spawn(Path.join(game_directory,"game.exe"))
                session=frida.attach(pid)
                def on_message(message:dict,_:bytes):
                    if message["type"]=="send":
                        frida.kill(pid)
                        index(message["payload"]["msg"])
                with open(DetectHandler.resource_path("hook1.js"),"r",encoding="utf-8") as sr:
                    script=session.create_script(sr.read().replace("$project_header", json.dumps(project_header)).replace("$str_offset",hex(offset)))
                script.on("message",on_message)
                script.load()
                frida.resume(pid)
            else:
                pid=frida.get_local_device().spawn(Path.join(game_directory,"game.exe"))
                session=frida.attach(pid)
                def on_message(message:dict,_:bytes):
                    if message["type"]=="send":
                        result_queue.put(message["payload"]["msg"])
                        frida.kill(pid)
                with open(DetectHandler.resource_path("hook2.js") ,"r",encoding="utf-8") as sr:
                    script=session.create_script(sr.read().replace("$func_offset",hex(inner_func_addr)).replace("$keyword",keyword))
                script.on("message",on_message)
                script.load()
                frida.resume(pid)
        index(-1)
        print(f"rva got: {hex(result_queue.get())}")
