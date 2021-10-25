from  pydub import AudioSegment
from pydub.utils import mediainfo
from pathlib import Path
import os
import logging
from cryptography.fernet import Fernet
import base64
from tinytag import TinyTag
from xattr import setxattr, getxattr
import shutil
import time
import multiprocessing
# import magic # for extract file type by magic number


def single_convert(audio,base_dir, source_dir, storage_dir, tags):
	
	audio_converted = audio.export(
					storage_dir, 
					format = "ogg",
					 bitrate="96000",
					 tags = tags #adding audio_metadata
					 )

	logging.info("{0} converted".format(source_dir))

	#handling duplicate error at converted folder
	try:		
		shutil.move(storage_dir, base_dir + "/converted/")
	except:
		logging.info(f'{Path(storage_dir).name} deleted post convertion, already exist in converted folder ')
		os.remove(storage_dir)



def convert_media(base_dir: Path, pagination: int):
	'''
		-Convert .mp3 and .flac audios from folder '/audios'
		in oog 96kbs coping from original the artis an title metadata 
		-Storage ogg in tem_converted folder
		-Remove original .mp3 or .flac audio
		-Move converted media to converted folder
		-Manage duplicate post and pre convertion
	'''
	counter = 0
	errors_counter = 0
	convert_processes = []

	for paths,_,files in os.walk(base_dir + "/audio/"):
		for file in files:
			storage_dir = base_dir + "/temp/" + str(Path(file).stem) + ".ogg"
			source_dir = os.path.join(paths,file)
			
			#handling audio duplicated error
			if (
				os.path.exists(paths+ "/../converted/" + str(Path(file).stem) + ".ogg") or
			 	os.path.exists(paths+ "/../encoded/" + str(Path(file).stem) + ".txt")):
				
				os.remove(source_dir)
				logging.warning(f'{source_dir} already being processed, file deleted')	

			else:
				
				#Extracting metadata from original file
				audio_meta = TinyTag.get(source_dir)
				if audio_meta.artist and audio_meta.title:
					tags = {
						"artist": audio_meta.artist,
						"title" : audio_meta.title 
						}
				else:
					tags ={
						"artist": "ERROR",
						"title": "ERROR"
						}	

				#Convertion by extentions type
				if Path(file).suffix == ".mp3":	
					audio = AudioSegment.from_mp3( source_dir)
					os.remove(source_dir)			
					p1 = multiprocessing.Process(target = single_convert, args = [audio, base_dir, source_dir, storage_dir, tags])
					p1.start()
					convert_processes.append(p1)

				elif Path(file).suffix == ".flac":
					audio = AudioSegment.from_file(source_dir, "flac")				
					os.remove(source_dir)
					p1 = multiprocessing.Process(target = single_convert, args = [audio, base_dir, source_dir, storage_dir, tags])
					p1.start()
					convert_processes.append(p1)

				else:
					logging.warning("The file located at" + paths + "was not converted")
					errors_counter +=1
					logging.info("{0} processed to convert".format(source_dir))
				
				
				counter+=1
				if counter == pagination:
					break
		if counter != 0:
			logging.info("{0} being processed file(s), {1} error(s)". format(counter, errors_counter))

		for p in convert_processes:
			p.join()


def generate_key():
	'''
		Genarate key and store it in mykey.key
	'''
	key = Fernet.generate_key()
	with open("mykey.key","wb") as key_file:
		key_file.write(key) 



def encrypt_file(file : Path,key : str):
	'''
		Encrypt file using a key 
		the encryted file will be store in out.txt
	'''
	fernet = Fernet(key) # generating key

	with open(file, 'rb') as original_file:
		original_file_data = original_file.read()
	
	encrypted_file_data = fernet.encrypt(original_file_data) # encripting data
	
	with open("out.ini", 'wb') as encrypted_file:
		encrypted_file.write(encrypted_file_data)



def decrypt_file(file : Path, key : str):
	'''
		Decrypt file using a key 
		the decryted file will be store in out.mp3
	'''
	fernet = Fernet(key)

	with open(file, "rb") as encryted_file:
		encrypted_file_data = encryted_file.read()

	decrypted_file_data = fernet.decrypt(encrypted_file_data)

	with open("out.mp3", "wb") as decrypted_file:
		decrypted_file.write(decrypted_file_data)




def file_partial_encode_base64(file_path, base_dir): #se codificaran los 100 primeros bits
	'''
		*Save song metadata from file
		*Overwrite first 150 bits information with base64 equivalent, the rest of the 
		bytestream remain iqual
		*Write the song metadata from original file to encoded file

	'''
	original_audio_tags = TinyTag.get(file_path)	
	
	with open(file_path, "rb") as file:
		data = file.read()
	partial_data_encoded = base64.encodebytes(data[:150])
	
	#concat byte strings
	data_encoded = b''.join([partial_data_encoded,data[150:]])	
	
	encoded_files_paths = base_dir + "/temp/" + file_path.stem + ".txt"
	with open(encoded_files_paths, "wb") as file_to:
		file_to.write(data_encoded)

	#Adding original metadata
	setxattr(
		encoded_files_paths,
		"user.artist",
		bytes(original_audio_tags.artist,'utf-8'), # the atribute most by a byte-like object
		)
	
	setxattr(
		encoded_files_paths,
		"user.title",
		bytes(original_audio_tags.title,'utf-8'), # the atribute most by a byte-like object
		)

	try:
		shutil.move(encoded_files_paths, base_dir + "/encoded" )
		logging.info(f'{file_path} was encoded')
		os.remove(file_path)

	except shutil.Error:
		logging.warning(f'{file_path} already being processed, duplicate deleted')
		os.remove(encoded_files_paths)
		os.remove(file_path)


def file_partial_decode_base64(file_path):
	with open(file_path, "rb") as file:
		data = file.read()

	partial_data_decoded = base64.decodebytes(data[:203])	
	#concat byte string
	data_encoded = b''.join([partial_data_decoded,data[203:]])
	
	with open("decoded/" + file_path.stem + ".ogg", "wb") as file_to:
		file_to.write(data_encoded)	



def main():
	base_dir = os.getcwd()
	#convert_media(base_dir, 5)

	file_partial_decode_base64(Path('/root/DCCU/Last_DCCU/DCCU/encoded/13. Mauro Moraes, Luiz Marenco - Deixa Pra Mim (128).txt'))
	audio = TinyTag.get('/root/DCCU/Last_DCCU/DCCU/decoded/13. Mauro Moraes, Luiz Marenco - Deixa Pra Mim (128).ogg')
	print(audio.artist, audio.title)
	#getting key
	# with open("mykey.key",'rb') as file:
	# 	key = file.read()


	#getting file to encript from root directory
	# p=Path(base_dir)
	# p_mp3 =[p for p in p.glob("*.ogg")]

	# #encrypt
	# encrypt_file(p_mp3[0], key)


	# # #getting file to decrypt
	# p=Path(base_dir)
	# p_txt=[p for p in p.glob("*.ini")]
	# print(p_txt)
	# # #decrypt
	# # decrypt_file(p_txt[1], key) 


	


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	# main()

	# base_dir = os.getcwd()

	# convert_media(base_dir,100)
	# paths_files = [p for p in Path(base_dir + '/converted').glob("*.ogg")]
	# for path in paths_files:
	# 	file_partial_encode_base64(path)

	
	# print(magic.from_file("encoded")) #para saber el tipo de archivo
	
	os.path.exist()


#Tareas
#Probar codificar en vez de encriptar X
#Annadir manejo de errores a conversion de media
	#que cuando el arrchivo exista se borre e storage dir
#Definir en el loging que converter es quien lo ejecuta
#Agregar 


