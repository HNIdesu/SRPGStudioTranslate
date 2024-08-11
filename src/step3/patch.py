from io import BytesIO
import os.path as Path
from Crypto.Cipher import ARC4
from Crypto.Hash import MD5
import polib
import shutil

class PatchHandler:
    def __init__(self,args):
        self.args=args

    def decrypt_asset(input_buf:bytes,password:str)->bytes:
        h = MD5.new()
        pwd=password.encode("utf-16le")
        h.update(pwd)
        key = h.digest()
        cipher = ARC4.new(key)
        decrypted_data = cipher.decrypt(input_buf)
        return decrypted_data

    def encrypt_asset(input_buf:bytes,password:str)->bytes:
        h = MD5.new()
        pwd=password.encode("utf-16le")
        h.update(pwd)
        key = h.digest()
        cipher = ARC4.new(key)
        encrypted_data = cipher.encrypt(input_buf)
        return encrypted_data
    
    class InvalidDataError(Exception):
        pass
    
    def process(self):
        args=self.args
        game_directory=args.game_directory
        mo_file_path=args.mo_file
        password=args.password
        dts_path=Path.join(game_directory,"data.dts")
        dts_backup_path=Path.join(game_directory,"data.dts.bak")
        if Path.exists(dts_path) and (not Path.exists(dts_backup_path)):
            shutil.copyfile(dts_path,dts_backup_path)
        project_data:bytes=None
        with open(dts_backup_path,"rb") as br:
            signature=br.read(4)
            if signature != b"SDTS":
                raise PatchHandler.InvalidDataError("signature mismatch")
            is_encrypted=int.from_bytes(br.read(4),byteorder="little")==1
            if is_encrypted and (not password):
                raise PatchHandler.InvalidDataError("password is required")
            br.seek(12,1)
            project_offset=int.from_bytes(br.read(4),byteorder="little")+168
            br.seek(project_offset,0)
            project_data=br.read()
            if is_encrypted:
                project_data=PatchHandler.decrypt_asset(project_data,password)
        entry_dict=dict[int,str]()
        mofile=polib.mofile(mo_file_path)
        for entry in mofile:
            entry_dict[int(entry.msgid,base=16)]=entry.msgstr

        with BytesIO() as bw:
            with BytesIO(project_data) as br:
                for id in sorted(entry_dict.keys()):
                    text=entry_dict[id]
                    if(br.tell()<id):
                        bw.write(br.read(id-br.tell()))
                    raw_length= int.from_bytes(br.read(4),byteorder="little")
                    new_str=(text+"\x00").encode("utf-16le")
                    new_length=len(new_str)
                    bw.write(int.to_bytes(new_length,length=4,byteorder="little"))
                    bw.write(new_str)
                    br.seek(raw_length,1)
                bw.write(br.read())
            project_data=PatchHandler.encrypt_asset(bw.getvalue(),password)

        with open(dts_path,"wb") as bw:
            with open(dts_backup_path,"rb") as br:
                bw.write(br.read(project_offset))
            bw.write(project_data)
