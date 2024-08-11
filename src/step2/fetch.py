import frida
import os
import os.path as Path
import sys
from queue import Queue
import polib

class FetchHandler:
    def __init__(self,args):
        self.args=args

    def resource_path(resource_name):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, "step2",resource_name)
        return os.path.join(Path.dirname(__file__), resource_name)

    def process(self):
        args=self.args
        game_directory=args.game_directory
        task_queue=Queue[tuple[int,str]]()
        rva=args.rva

        def on_message(message:dict,data:bytes):
            if message["type"]=="send":
                position:int=message["payload"]["position"]
                text=data[:-2].decode("utf-16le")
                task_queue.put((position,text))
                print(text)


        os.chdir(game_directory)
        pid=frida.get_local_device().spawn(Path.join(game_directory,"game.exe"))
        session=frida.attach(pid)

        with open(FetchHandler.resource_path("hook.js") ,"r",encoding="utf-8") as sr:
            script=session.create_script(sr.read().replace("$read_string_rva",rva))
        script.on("message",on_message)
        script.load()
        frida.resume(pid)

        pot_file_path="translation.pot"
        pofile=polib.POFile()
        try:
            while(True):
                (position,text)=task_queue.get(timeout=5)
                entry=polib.POEntry(
                    msgid=hex(position),
                    msgstr=text
                )
                pofile.append(entry)
        except Exception:
            pofile.save(pot_file_path)
            frida.kill(pid)
