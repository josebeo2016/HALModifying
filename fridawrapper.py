import sys
import subprocess
from subprocess import check_output
import re


def frida_server_start_process():
    if (frida_server_check_existing()==None):
        frida_server_subprocess = subprocess.Popen("adb shell \"/data/local/tmp/frida-server &\"", shell=False)
        if frida_server_subprocess:
            return frida_server_subprocess
        else:
            return None


def frida_server_kill_process():
    if frida_server_check_existing():
        a = check_output("adb shell \"ps|grep frida\"", shell=True).decode()
        pids = re.findall("root      (.*)\s1",a)
        for pid in pids:
            pid = pid.strip()
            frida_server_kill = subprocess.Popen("adb shell \"kill -9 "+pid+"\"", shell=False)
        return True
    else: 
        return None

def frida_server_check_existing():
    frida_existing = subprocess.Popen("adb shell \"ps| grep frida-server\"", 
                                       shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data, nothing = frida_existing.communicate()
    if (len(data) != 0):
        frida_existing.kill()
        return True
    else:
        frida_existing.kill()
        return None

# if(frida_server_start_process()):
#     print("[*]Start frida-server")
# else:
#     print("[-]Error starting frida-server")
# frida_server_kill_process()