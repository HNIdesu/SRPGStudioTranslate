from argparse import ArgumentParser
from step1.detect import DetectHandler
from step3.patch import PatchHandler
from step2.fetch import FetchHandler
import sys

def patch(args):
    PatchHandler(args).process()
def fetch(args):
    FetchHandler(args).process()
def detect(args):
    DetectHandler(args).process()

parser=ArgumentParser()
subparser=parser.add_subparsers()

patch_parser=subparser.add_parser("patch")
patch_parser.add_argument("game_directory")
patch_parser.add_argument("mo_file")
patch_parser.add_argument("-p","--password",required=False,default="key")
patch_parser.set_defaults(func=patch)

fetch_parser=subparser.add_parser("fetch")
fetch_parser.add_argument("game_directory")
fetch_parser.add_argument("-r","--rva",required=True)
fetch_parser.set_defaults(func=fetch)

detect_handler=subparser.add_parser("detect")
detect_handler.add_argument("game_directory")
detect_handler.add_argument("project_path")
detect_handler.add_argument("-w","--keyword",required=False,default="新規スイッチ")
detect_handler.set_defaults(func=detect)

if len(sys.argv)<=1:
    parser.print_help()
else:
    parser.parse_args()

