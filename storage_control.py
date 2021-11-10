import psutil
import time



def storageControl(time_between_check: int, #segundos
		min_storage_percent: float, 
		max_storage_percent: float,
		downloader: int #numero del descargador
		):
	storage_used_percent = psutil.disk_usage("/") #folder_usage()   #psutil.disk_usage("/")
	print(f'INFO: downloader{downloader}: Disck usage: {storage_used_percent.percent}%')
	if  storage_used_percent.percent > max_storage_percent:
		print(f'WARNING: autodownloader{downloader}: Max disk usage ({max_storage_percent}%) exceed, downloader{downloader} stopped for a while')
		while storage_used_percent.percent > min_storage_percent:
			storage_used_percent = psutil.disk_usage("/") #folder_usage() #psutil.disk_usage("/")
			print(f'INFO: autodownloader{downloader}: Disck usage: {storage_used_percent.percent}%, dowloader{downloader} waiting for reach Min disck usage')
			time.sleep( time_between_check )
		print(f'INFO: autodownloader{downloader}: Min disk usage reached ({storage_used_percent.percent}%) downloads restarted')

#Add this line to autodowloader
if __name__ == "__main__":
	for i in range(10):
		storageControl(time_between_check = 5,
			min_storage_percent = 15,
		 	max_storage_percent = 20,
		 	downloader = 1)
