import shutil
import os
import subprocess
import logging 
import multiprocessing
from storage_control import storageControl
import  time
import psutil

def start_downloader():
	subprocess.run(["python3","download.py"]) #for linux change for "python3 ..."

#TEST CONCUNRRENCY
#--------------------
# def proceso():
# 	subprocess.run("python pros.py")
#--------------------

def listar(instancia: int, base_dir):
	'''
	Copy sessions from folder sessions to medialist with name media_downloader.session
	List id_message for current instance
	Move id_message list to respective downloader instance
	'''
	shutil.copy(
			base_dir + "/session/{}.session".format(instancia),
			base_dir + "/medialist/media_downloader.session"
			 )
	os.chdir(base_dir + "/medialist")
	subprocess.run(["python3","message_list.py"]) #esto se debe cambiar en linux por "python3 message_list.py"
	shutil.move(
		base_dir + "/medialist/splited_json/0.json",
		base_dir + "/Downloader_{}/messages.json".format(instancia)
		)



if __name__ == "__main__":
	logging.basicConfig(level = logging.ERROR)
	logging.info("#####MY FIRST JOB :)####")
	base_dir = os.getcwd()
	downloaders = 5

	# SET ALL STATES = 1
	for instancia in range(downloaders):
		os.chdir(base_dir + "/Downloader_{}".format(instancia))
		with open("state.txt" , "w") as file:
			file.write("1")

	#DOWNLOAD FLOW
	'''
		Check Permanently if any downloader finish by looking the state 
		Start downloader again when finish
	'''
	while True:
		for instancia in range(downloaders):
			os.chdir(base_dir + "/Downloader_{}".format(instancia))
			with open("state.txt" , "r") as file:
				state = file.read()
			
			if state == "1":		
				storageControl(time_between_check = 5,
                       				 min_storage_percent = 60,
                       				 max_storage_percent = 80,
                        			downloader = instancia)		
				listar(instancia,base_dir)
				os.chdir(base_dir + "/Downloader_{}".format(instancia))
				p = multiprocessing.Process(target = start_downloader)
				p.start()
