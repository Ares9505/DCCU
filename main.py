from converter import convert_media, file_partial_encode_base64, file_partial_decode_base64
from pathlib import Path
from uploader import upload_files_to_dropbox
import os
from pydub.utils import mediainfo 
import json
import dropbox
import logging 
import multiprocessing
import shutil
from xattr import setxattr 

def start_process(target, args):
	process = multiprocessing.Process(target = target, args = args)
	process.start()

def convert(base_dir, pagination):
	while True:
		convert_media(base_dir,pagination)

def encode(base_dir, encoding_pagination):
	while True:
		for _,to_encode_path in zip(range(encoding_pagination),Path(base_dir + "/converted").glob("*.ogg")):
			file_partial_encode_base64(to_encode_path,base_dir)	

def upload(
	base_dir: str,
	upload_pagination: int,
	dpx: dropbox.Dropbox,
	txt_log_counter):
	 
	while True:
		file_paths = [j for _,j in zip(range(upload_pagination),Path(base_dir + "/encoded").glob("*.*"))]
		upload_files_to_dropbox(dbx, file_paths, upload_pagination, txt_log_counter)
		if len(file_paths)!= 0:
			txt_log_counter += 1
			config['index'] = txt_log_counter
			with open(base_dir + "/config.json","w") as file:
				json.dump(config, file, indent=6)


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	base_dir = os.getcwd()
	converter_pagination = 64
	encoding_pagination = 1
	upload_pagination = 1
	
	with open(base_dir + "/config.json", "r") as json_file:
                config = json.load(json_file)


	# #Preparing scenary
	# #--------------------------------------
	# for i in Path(base_dir +"/converted").glob("*.*"):
	# 	os.remove(i)

	# for i in Path(base_dir + "/encoded").glob("*.*"):
	# 	os.remove(i)
	
	# for i in Path(base_dir + "/logs").glob("*.*"):
	# 	os.remove(i)

	# for i in Path(base_dir + "/temporal").glob("*.*"):
	# 	shutil.copy(i, base_dir + "/audio")
	# # --------------------------------------

	start_process(convert,[ base_dir, converter_pagination])
	start_process(encode, [base_dir, encoding_pagination])

	# # #Fragment of code tu decode files from encoded folder
	# # # ---------------------------------------------------
	# # # for _,to_encode_path in zip(range(encoding_pagination),Path(base_dir + "/encoded").glob("*.ready")):
	# # # 	file_partial_decode_base64(to_encode_path)
	# # #----------------------------------------------------

	#Test to upload files
	#--------------------------------------
	# nombres = ['Alicia', 'Pedro', 'Juan', 'Olivia','Pepe', 'Antonio', 'Lino', 'Juano', 'mariguano']
	# for nombre in nombres:
	# 	file_path = f'encoded/{nombre}.txt'
	# 	file=open(file_path,'wb')
	# 	file.write(b'SomeDataBinary')
	# 	file.close()
	# 	setxattr(
	# 		file_path,
	# 		 "user.artist",
	# 		  bytes(nombre,"utf-8"))
	# 	setxattr(
	# 		file_path,
	# 		 "user.title",
	# 		  bytes(nombre,"utf-8"))
	#----------------------------------------

	# Conecting with dropbox api
	dbx = dropbox.Dropbox(config['dropbox_token'])
	
	# Upload to dropbox
	start_process(upload,[base_dir, upload_pagination, dbx,config['index']])

	



	
