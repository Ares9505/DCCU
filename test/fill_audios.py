import os
from pathlib import Path
import shutil


def copy_audios_to_audio_folder():
	'''
		Fill audio folder with some audio examples 
	'''
	os.chdir("../")
	base_dir =  os.getcwd()
	files = [Path(i) for i in os.listdir(base_dir + "/temporal")]
	for file in files:
		shutil.copy(base_dir +"/temporal/" + str(file),  base_dir + "/audio" )

copy_audios_to_audio_folder()