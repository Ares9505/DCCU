import dropbox
import json
import os
from pathlib import Path
from tinytag import TinyTag
from xattr import listxattr,setxattr,getxattr, removexattr
import logging

def upload_file_to_dropbox(): #
	'''
		upload a single file to dropbox
	'''
	dbx = dropbox.Dropbox('acces_token')
	
	# for file in files:
	dbx.files_upload(open('requirements.txt', 'rb').read(), '/Descargas/requirements1.txt')



def upload_files_to_dropbox(
	dbx : dropbox.Dropbox,
	file_paths: list,
	upload_pagination: int, #cant de archivos a subir en una llamada
	txt_log_counter: int #contador de logs
	 ):
	'''
		Upload files to folder /Descargas in dropbox
		Save a json with upload files 
	'''
	index = txt_log_counter*upload_pagination 
	upload_errors = 0

	for file in file_paths:
		try:
			#Extracting metadata before upload
			artist = getxattr(file, "user.artist").decode("utf-8") # the atributes are given in bytes, its mostbe convert to string using 'decode' function
			title = getxattr(file, "user.title").decode("utf-8")
			
			#Removing metadata before upload
			removexattr(file,"user.artist")
			removexattr(file,"user.title")
		
				
			dbx.files_upload(open(file, 'rb').read(), '/Descargas/' + str(index) + ".txt")
			logging.info(f'{file} was uploaded')		
			with open("logs/{0}.txt".format(txt_log_counter//100) , "a") as log_file:
				log_file.writelines(f'{index},{artist},,{title}\n')

		except:
			logging.warning(f'{file} could\'nt been upload')
			upload_errors += 1
		
		os.remove(file)
		index += 1

	#Using 'if' to avoid repetition of logging.info when there is not files to upload	
	if index != txt_log_counter*upload_pagination:
		logging.info(f'{upload_errors} errors uploadings files')




def main():
	with open("config.json", "r") as json_file:
		config = json.load(json_file)

	#Base directory to upload
	base_dir = os.getcwd() 
	txt_log_counter = 0

	# Creating test files with metadata
	#---------------------------------------
	nombres = ['Alicia', 'Pedro', 'Juan', 'Olivia','Pepe', 'Antonio', 'Lino', 'Juano', 'mariguano']
	for nombre in nombres:
		file_path = f'encoded/{nombre}.txt'
		file=open(file_path,'wb')
		file.write(b'SomeDataBinary')
		file.close()
		setxattr(
			file_path,
			 "user.artist",
			  bytes(nombre,"utf-8"))
		setxattr(
			file_path,
			 "user.title",
			  bytes(nombre,"utf-8"))

	#Cleaning logs folder
	# for i in Path(base_dir + "/logs").glob("*.*"):
	# 	os.remove(i)


	#list of files to upload eficiently without list of the files in the dir
	pagination = 2
	dbx = dropbox.Dropbox(config['dropbox_token'])
	while True:
		file_paths = [j for _,j in zip(range(pagination),Path(base_dir + "/encoded").glob("*.txt"))]	# Conecting with dropbox api
		upload_files_to_dropbox(dbx, file_paths,pagination,txt_log_counter)
		txt_log_counter += 1

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	main()

		
	# Direccion de la api:
	# https://www.dropbox.com/developers/apps/info/qogj8z5rrgn1hgn#permissions
