import os
from pathlib import Path

def general(folder: str):
	for i in Path(os.getcwd() + folder ).glob("*.*"):
		os.remove(i)

folders = ["/audio","/converted","/encoded","/logs", "/temp"]
for folder in folders:
	general(folder)
