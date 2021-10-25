import time
import subprocess
import multiprocessing
import logging

def download_master():
	subprocess.run(["python3","Autodownloader.py"])

def CCU():
	subprocess.run(["python3","main.py"])

if __name__ == "__main__":
	logging.basicConfig(filename= "std.log", format = '%(asctime)s %(message)s', 
			filemode = 'w')
	p1 = multiprocessing.Process(target = download_master)
	p2 = multiprocessing.Process(target = CCU)
	p1.start()
	time.sleep(10)
	p2.start()
	p1.join()
	p2.join()
