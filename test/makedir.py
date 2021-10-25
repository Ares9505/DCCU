import os
from pathlib import Path 
'''
	For create audio, converted, encoded and temp folders
'''
def mkdirs(folder_list: str):
	
	for folder in folder_list:	
		p = Path(os.getcwd() + "/../" + folder)
		p.mkdir()

folder_list = ["audio","encoded","temp","converted"]
mkdirs(folder_list)