import time
import frida
from pyaxmlparser import APK
import glob
from subprocess import check_output
import subprocess
import sys
from fridawrapper import *
import os
import errno
import utils
import config
#index user type
start = int(sys.argv[1])


def static_analysis(apkPath):
    print ("static_analysis (get package, activity")
    packageName = None
    activity = None

    activity_flag = 0
    # Need a aapt Program
    print("apk :{}".format(apkPath))
    cmd = "aapt d badging {} > info.txt".format(apkPath)
    utils.run_cmd(cmd)
    INFO_TXT = "info.txt"
    f = open(INFO_TXT, "r")
    temp = f.readlines()
    f.close()
    for i in temp:
        if i.find("package:") != -1:
            pack_v = i.split()
            if len(pack_v)==1:
                continue
            pack = pack_v[1].replace("name='","")
            packageName = pack.replace("'", "")
        if i.find("launchable-activity:") != -1 and activity_flag == 0:
            acti_v = i.split()
            acti = acti_v[1].replace("name='","")
            activity = acti.replace("'", "")
            activity_flag = 1

    packageName = packageName
    # find processName
    processName_cmd = "aapt list -a {}|grep android:process".format(apkPath)
    processName = utils.run_cmd(processName_cmd)
    try:
        processName = processName.split('Raw:')[1]
        processName = processName.replace('"','').replace(' ','').replace(')','').strip().decode()
        if (':' not in processName):
            processName = processName
            # print("hello from the out side")
        else:
            processName = packageName
    except:
        processName = packageName
    cmd = "rm info.txt"
    utils.run_cmd(cmd)
    print(("(static_analysis) packageName :",packageName,"activity :",activity))
    return packageName, activity, processName

def start_frida(containerName):
    check_cmd = "lxc-attach -n {} -- ./data/local/tmp/cnsl-server > /dev/null 2>&1 &".format(containerName)
    try:
        print("@@@@@@@@@@@@@@@@@@@@@@@@Starting Frida server...")
        result = os.popen(check_cmd)
        result = result.read()
        print("@Frida result: {}".format(result))
    except:
        pass
    return

filename=""
dir = '/root/SMS/FakeInst/'
def getLogdir(filename,dirName):
    log = "/root/SMS/log/FakeInst/"
    logdir = log + filename.replace(dirName,"")
    return logdir
BASE_MANAGER_CMD = "python3 /root/mobilepentest/manager.py"

def destroy_container():
    out=utils.run_cmd("{} --destroy_container".format(BASE_MANAGER_CMD))
    return out
def repair_container():
    # Check container exist. If existed, auto destroy
    out = utils.run_cmd("{} -C".format(BASE_MANAGER_CMD))
    if "ERROR " in out:
            print(out)
    if 'containerexist' in out:
        # Destroy
        destroy_container()
    out = utils.run_cmd("{} --create_container".format(BASE_MANAGER_CMD))
    if "ERROR " in out:
        print(out)
    else:
        print(out)
    print(out)
    print("****************************************************")
    print("START CONTAINER")
    out =utils.run_cmd('{} --start_container'.format(BASE_MANAGER_CMD))
    if "ERROR " in out:
        print(out)
    else:
        print(out)
    print(out)
    time.sleep(5)
    # check container
    print(utils.run_cmd('{} -T'.format(BASE_MANAGER_CMD),timeout=360))
    print("****************************************************")
    print("Done repairing Dynamic environment")
def my_message_handler(message, payload):
	# print(message)
	global filename
	logfile = filename+"_log.txt"
	errlog = filename+"_error.txt"
	if not os.path.exists(os.path.dirname(logfile)):
		try:
			os.makedirs(os.path.dirname(logfile))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise
	if message["type"] == "send":
		if "[-]Error" not in message["payload"]:
			f=open(logfile,"a+").write(message["payload"]+"\n")
		else:
			f=open(errlog,"a+").write(message["payload"]+"\n")
	if message["type"] == "error":
		f=open(errlog,"a+").write(message["description"]+"\n")

# start_frida("hikey321")

filels = list()
for (dirpath, dirnames, filenames) in os.walk(dir):
    filels += [os.path.join(dirpath, file) for file in filenames]

# forward port
# print(check_output("adb forward tcp:12356 tcp:12356"))
time.sleep(3)

for index in range(start,len(filels)):
	repair_container()
	result = {}
	apk_package = ""
	apk_full_path = filels[index]
	# frida_server_kill_process()
	# time.sleep(1)
	# frida_server_start_process()
	try:
		# fetch apk file
		print ("Install application: "+apk_full_path)
		
		filename = getLogdir(apk_full_path,dir)
		# install apk
		print(check_output("adb install "+apk_full_path+"|exit", shell=True,timeout=10).decode())
		# get package name
		apk = APK(apk_full_path)
		package_name = apk.packagename
		print (index)
		print (filename)
		print (package_name)
	except Exception as e:
		f=open("runlog.txt","a+").write("Error in file: "+filename+"\n")
		exit

	docker_id = '192.168.0.36'
	launchable_activity = utils.get_launchable_activity_from_aapt(
        apk_full_path)
	run_apk_res = utils.run_apk(docker_id, package_name, launchable_activity)

    # get all pid of the app while it runs
	pids = utils.get_app_pid(docker_id,package_name)
	result['cpu'] = []
	result['mem'] = []
	# run normal
	try:
		print(check_output("adb shell \"monkey -p "+package_name+" -v 200 -s 1563 --throttle 100\"", shell=True,timeout=10).decode())
	except Exception as e:
		f=open("runlog.txt","a+").write("Error while running: "+filename+"\n")
    # time.sleep(5)
	# logger.debug(pids)
	for pid in pids:
		res = utils.run_adb_cmd(docker_id,"ps -p {} -o \%cpu,\%mem".format(pid))
		print("*************"+res)
		res=res.strip().split('\n')[1].split(' ')
		res = [x for x in res if x]
		result['cpu'].append({
            "pid":pid,
            "usage":res[0]
            })
		result['mem'].append({
            "pid":pid,
            "usage":res[1]
            })
	f=open("{}notfrida.log".format(dir),"a+").write("{}: cpu:{} mem:{}".format(filename,result['cpu'],result['mem']))

	# Monitoring resource manual

	# frida_server_kill_process()
	# # hooking and start apk
	# if (package_name!=""):
	# 	try:
	# 		device = frida.get_remote_device()
	# 		pid = device.spawn([package_name])
	# 		device.resume(pid)
	# 		time.sleep(1)  # Without it Java.perform silently fails
	# 		session = device.attach(pid)
	# 		with open("hookalloverload.js") as f:
	# 			script = session.create_script(f.read())
	# 			script.on("message", my_message_handler)
	# 			script.load()
	# 		# asfd=input("Input in the end!")
	# 		time.sleep(5)
	# 		# print("After finish, please press Enter!")
	# 		input("After finish, please press Enter!")
	# 		# print(check_output("adb shell \"monkey -p "+package_name+" -v 200 -s 1563 --throttle 100\"", shell=True,timeout=10).decode())
			
	# 	except Exception as e1:
	# 		print(e1)
	# 		exit
	# 	finally:
	# 		print("Finally analysis for "+str(index))
	# 		try:
	# 			print(check_output("adb uninstall "+package_name, shell=True,timeout=10).decode())
	# 		except:
	# 			print("error in uninstall")
	# 		exit




	# try:
	# 	applications = device.enumerate_applications()
	# 	pid = list(filter(lambda app: app.identifier == "TalkingSantainstallator.html.app" and app.pid!=0, applications))[0].pid
	# except Exception as e:
	# 	print(e)
	# 	exit