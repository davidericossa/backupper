import time, os, json
from dateutil.relativedelta import relativedelta
from datetime import datetime 

class Handler:
	backups=[]
	devices=[]
	@classmethod
	def runBackups(cls):
		for backup in cls.backups:
			if backup.isExpired(): 
				print("Backup on DEVICE:'{}' \nof SOURCE{} \nexpired on: {}".format(backup.device.name, backup.source, backup.exp_date))
				print("Start backup ...")
				backup.run()
				print("Success!")

	@classmethod
	def configBackups(cls,devs_configs_json_path="./config.json"):
		with open(devs_configs_json_path, "r") as read_file:
			data=json.load(read_file)
		read_file.close()
		for device_configs in data["devices"]:
			dev=Device(device_configs["name"], device_configs["mount_point"])
			cls.devices.append(dev)
			if dev.isMounted():
				print("{} is mounted".format(dev.name))
				for config in device_configs["configs"]:
					cnf=Config(config["name"], config["path"], config["frequency"])
					backup=Backup(data["source"], dev, cnf)
					cls.backups.append(backup)

class Config:
	def __init__(self, name, path, frequency):
		self.name=name
		self.path=path
		self.frequency=relativedelta()
		for k, v in frequency.items():
			if v!=0: setattr(self.frequency, k, v)

class Device:
	def __init__(self, name, mount_point):
		self.name = name
		self.mount_point=mount_point
	
	def isMounted(self):
		path="{}/{}".format(self.mount_point,self.name)
		return os.path.exists(path)

class Backup:
	def __init__(self, source, device, config):
		self.source=source
		self.device=device
		self.config=config
		self.target="{}/{}/{}".format(device.mount_point, device.name, config.path)
		self.log="{}/log.txt".format(self.target)
		self.frequency=config.frequency
		self.last_run_datetime=datetime.fromtimestamp(os.path.getmtime(self.log))
		self.exp_date=self.last_run_datetime+self.frequency
	
	def isExpired(self):
		now=datetime.now()
		return now>self.exp_date

	def run(self):
		command="echo 'Started at {}' > {}".format(datetime.now(), self.log)
		os.system(command)
		command="rsync -avv --delete {} {} >> {}".format(self.source, self.target, self.log)
		os.system(command)

