import os
import sys
from appium import webdriver
from time import sleep
import threading
import sys
import subprocess
import json
from config import port_config, dir, container_name, aapt, elastic_index, hikeyIP
# from utils import *
import re
import ipaddress
from logger import getLogger
import signal
class Drozer():
    def __init__(self, appPath, appPackage, appActivity,dockerID):
        self.appPath = appPath
        self.appPackage = appPackage
        self.appActivity = appActivity
        self.dockerID = dockerID

    def setUp(self):
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        desired_caps['platformVersion'] = '9.0'
        desired_caps['deviceName'] = 'Android Emulator'
        desired_caps['automationName'] = 'UiAutomator2'
        desired_caps['app'] = self.appPath
        desired_caps['appPackage'] = self.appPackage
        desired_caps['appActivity'] = self.appActivity
        self.driver = webdriver.Remote('http://{}{}/wd/hub'.format(port_config.appium,self.dockerID), desired_caps)

    def tearDown(self):
        self.driver.quit()

    def turn_on(self):
        try:
            print( "Handle toggle ")
            buttons = self.driver.find_elements_by_class_name("android.widget.ToggleButton")
            print( "len_toggle", len(buttons))
            clickCount = 0
            for btn in buttons:
                print( "Clickable object is: ", btn.text)
                clickCount += 1
                try:
                    print( "Clicked: ", btn.text)
                    if ("OFF" in btn.text):
                        btn.click()
                except (TypeError, NameError, IOError, IndexError):
                    print( "handle toggle --- click button error")
            #if no object was clicked, then click the first one
            if clickCount == 0:
                buttons[0].click()

        except (TypeError, NameError, IOError, IndexError):
            print( "handle buttons error")
            pass



 
class TimeOutException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'TimeOutException, {0} '.format(self.message)
        else:
            return 'TimeOutException has been raised'


 
def alarm_handler(signum, frame):
    if (signum == signal.SIGALRM):
        raise TimeOutException()
    else:
        pass

def start_timer(timeout=300): 
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)
 

def find_and_highlight(pattern,text):
    colourFormat = ''
    colourStr = ''
    resetStr = ''
    # No highlight
    lastMatch = 0
    formattedText = ''
    a = re.finditer(pattern, text)
    ismatch = False
    for match in a:
        ismatch=True
        start, end = match.span()
        formattedText += text[lastMatch: start]
        formattedText += colourStr
        formattedText += text[start: end]
        formattedText += resetStr
        lastMatch = end
    if(ismatch):
        formattedText += text[lastMatch:]
    return formattedText

def adb_connect(docker_id):
    """
    Connect to container as root
    """
    run_cmd("adb connect {}:{}".format(docker_id,port_config.adb))
    run_cmd("adb root")
    out = run_cmd("adb connect {}:{}".format(docker_id,port_config.adb))
    return out

def get_app_pid(docker_id,package_name):
    """
    return list of pids (in case app have more than 1 process)
    """
    app_id, gid = find_appid(docker_id, package_name)
    # print(app_id)
    if app_id == "0":
        print("Can't get App_uid")
        return
    processes = run_adb_cmd(docker_id,"ps -A |grep {}".format(app_id)).strip()
    get_pid = processes.replace('\n',' ').split(' ')
    get_pid = [x for x in get_pid if x]
    pids=[]
    for x in range(len(get_pid)):
        if (get_pid[x]==app_id):
            pids.append(get_pid[x+1])
    
    return pids

# def find_appid(docker_id,package_name):
#     cmd_app_id = "ls -l /data/data/{}".format(package_name)
#     app_id = run_adb_cmd(docker_id,cmd_app_id)
#     try:
#         x = re.findall("drwxrws.* 2 (.*) (u|s)",app_id)
#         if(len(x)>0):
#             app_id=x[0][0]
#             return app_id
#         else:
#             return "0"
#     except:
        
#         app_id=0
#         return "0"

# find_appid ver 2.0
def find_appid(docker_id,package_name):
    cmd_app_id = "ls -al /data/data/{}".format(package_name)
    app_id = run_adb_cmd(docker_id,cmd_app_id).split('\n')[1:]
    uid = '0'
    gid = '0'
    for out in app_id:
        out = out.split(' ')
        if out[-1]=='.':
            
            out = [x for x in out if x]
            uid = out[2]
            gid = out[3]
    return uid, gid

def print_output(analysis_id,output):
    logger = getLogger(analysis_id,hikeyIP)
    print("Result:")
    out = json.dumps(output,sort_keys=True, indent=4)
    print(out)
    logger.debug("Result: \n"+out)


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

def start_tcpdump(docker_id,pcap_file,q_opt):
    cmd = "/system/xbin/tcpdump -i wlan0 -Q {} -w {} > /dev/null 2>&1 &".format(q_opt,pcap_file)
    run_adb_cmd(docker_id,cmd)
    return

def stop_tcpdump(docker_id):
    cmd = "killall tcpdump"
    run_adb_cmd(docker_id,cmd)


def run_cmd(cmd,timeout=300):
    try:
        process = subprocess.check_output(cmd, shell=True,timeout=timeout)
        # out, error = process.communicate(timeout=200)
        return process.decode('utf-8').strip()
    except Exception as e:
        return "ERROR {}".format(e).strip()

def run_adb_cmd(docker_id,cmd,timeout=300):
    adb_device = "{}:{}".format(docker_id,port_config.adb)
    adb_cmd = "adb -s {} shell \"{}\"".format(adb_device,cmd)
    # adb_cmd = cmd
    try:
        process = subprocess.check_output(adb_cmd, shell=True,timeout=timeout)
        # out, error = process.communicate(timeout=200)
        return process.decode('utf-8').strip()
    except Exception as e:
        return "ERROR {}".format(e).strip()
# def run_cmd(cmd,timeout=300):
#     # cmd = cmd.split(' ')
#     try:
#         process = subprocess.run(cmd,shell=True,timeout=timeout)
#         out = process.stdout
#         err = process.stderr
#         print("*************************************************{}".format(out))
#         if (err != 'None'):
#             return out
#         else:
#             return "ERROR {}".format(err)
#     except Exception as e:
#         return "ERROR exception {}".format(e)
# def run_cmd(cmd, timeout=300):
#     # p = subprocess32.run(cmd, shell=True, timeout=120)
#     try:
#         p = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#         out, err = p.communicate(timeout = timeout)
#         if err is not None:
#             return out.decode('utf-8')
#         return "ERROR {}".format(err)
#     except subprocess.TimeoutExpired as e:
#         return "ERROR time out"

def check_whitelist_ip(ip,check_ip,check_net):
    """
    check_ip is a list of ip addr that our IP equal to one of this list
    check_net is a list of netaddr that our IP in one of this list
    """
    for wip in check_ip:
        if ipaddress.ip_address(ip) == ipaddress.ip_address(wip):
            return True
    for wnet in check_net:
        if ipaddress.ip_address(ip) in ipaddress.ip_network(wnet):
            return True
    return False

def install_package(docker_id,apk_file):
    adb_device = "{}:{}".format(docker_id,port_config.adb)
    apk_file = "{}/{}".format(dir.share_apk,apk_file)
    start_timer(timeout=7200)
    try:
        out = run_cmd("adb -s {} install {}".format(adb_device,apk_file))
    except TimeOutException as ex:
        return "ERROR timeout!"
    return out

def get_package_name(apk_full_path):
    """
    get package name using aapt tool
    param  apk_absolute_path
    return pacakge_name
    """
    cmd = aapt + ' dump badging ' + apk_full_path + ' | grep "package: name" | awk "{print $2}" | cut -d"\'" -f2'
    result = run_cmd(cmd)
    if "ERROR" in result:
        result = ""
    return result

def run_apk(docker_id,package_name, launchable_activity):
    cmd = 'am start ' + package_name + "/" + launchable_activity
    out = run_adb_cmd(docker_id,cmd)
    return out

def cap(docker_id,analysis_id,cap_dir):
    cmd1 = 'screencap -p /data/local/tmp/{}_{}.jpg'.format(docker_id,analysis_id)
    run_adb_cmd(docker_id,cmd1)
    # CAP_DIR = "{}/".format(dir.out_dir)
    cmd2 = 'cp /var/lib/lxc/{}/data/local/tmp/{}_{}.jpg {}'.format(container_name, docker_id,analysis_id, cap_dir)
    run_cmd(cmd2)

def remove_package(docker_id,package_name):
    """Remove apk from container
    param  apk_absolute_path (string)
    return remove state (string) <Success, Remove Fail>
    """

    # Check the target apk is already installed or not
    install_state = get_install_state_of_apk(docker_id,package_name)
    # If install well, then remove thar apk and get result
    adb_device = "{}:{}".format(docker_id,port_config.adb)
    cmd = 'adb -s {} uninstall {}'.format(adb_device,package_name)
    if install_state:
        result = run_cmd(cmd)
        if ('Failure' in result) or ('ERROR' in result):
            result = "Remove Fail"
            return result
        else:
            result = 'Success'
            return result
    else:
        # If apk not installed then return 
        print('Apk is not installed in container')
        return 'Remove Fail'



def get_install_state_of_apk(docker_id,package_name):
    """Check apk is installed or not
    # param  package_name
    # return if apk install well, then return Ture
    """
    cmd = 'pm list packages -f | grep {}'.format(package_name)
    result = run_adb_cmd(docker_id,cmd)
    print (result)
    if ('package' in result) and ('ERROR' not in result):
        return True
    else:
        return False

def get_container_pid():
    cmd = "ps auxf |grep 'init' |grep -v 'grep' |grep -v 'sbin' |grep -v 'vendor'"
    out = run_cmd(cmd).strip().split(' ')
    if out[0] == '':
        print ('Android Container is not deployed')
        exit(1)
    out = [x for x in out if x]
    cpid = int(out[1])
    return cpid

def save_dir_info_with_find(dir_path, save_file_path):
    # Save directory info with find
    # Param  dir_path (string), save_file path (string) <tmp, sdcard>
    # Return none
    cmd = "find " + dir_path + " 2>&1 | grep -v 'Permission denied' > " + save_file_path
    out = run_cmd(cmd)
    return out

def get_container_wlan_ip(containerName):
    cmd = "lxc-attach -n "+containerName+" -- ip ad | grep wlan0 | grep inet | awk '{print $2}' | cut -d'/' -f1"
    out = run_cmd(cmd)
    return out


def md5hash(file_path):
    # Get hash result using md5sum function
    # Param  data (string)
    # Return hash value (string)
    cmd = "md5sum "+file_path+" | awk '{print $1}'"
    out = run_cmd(cmd).strip()
    md5 = out
    return md5

def sha256hash(file_path):
    # Get hash result using md5sum function
    # Param  data (string)
    # Return hash value (string)
    cmd = "sha256sum "+file_path+" | awk '{print $1}'"
    out = run_cmd(cmd).strip()
    md5 = out
    return md5

def get_launchable_activity_from_aapt(apk_full_path):
    cmd = aapt + ' dump badging ' + apk_full_path + ' | grep "launchable-activity"'
    out = run_cmd(cmd)
    # print (out)
    splited_result = out.split("'")
    return splited_result[1].strip()

def network_sniffing(docker_id,out_pcap,timeout=300):
    """
    Sniff network traffic during <timeout> (seconds)
    and write out put to out_pcap

    """
    adb_device = "{}:{}".format(docker_id,port_config.adb)
    sniff = run_cmd("adb -s {} shell '/system/xbin/tcpdump -i wlan0 -G {} -W 1 -Q inout -w /data/local/tmp/tmp.pcap'".format(adb_device,timeout))
    store_pcap = run_cmd("cp /var/lib/lxc/{}/data/local/tmp/tmp.pcap {}".format(container_name,out_pcap))
    print("[] Sniffing Done!")
