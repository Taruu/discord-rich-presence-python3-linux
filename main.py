from pypresence import Presence # The simple rich presence client in pypresence
import time
import psutil
import subprocess
import json
import os


p = psutil.Process()

res = subprocess.check_output(["xdotool", "getwindowfocus", "getwindowpid"])
with open("config/app.json","r") as file:
    data = json.load(file)

client_id = str(data["application_id"])
get_by_name = data["findRealName"]
small_image = data["small_image"]



with open("config/config_applications.json","r") as file:
    config_applications = json.load(file)


def get_name(): #only linux need add to windows
    res_pid = subprocess.run(["xdotool", "getwindowfocus", "getwindowpid"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    res_str = subprocess.run(["xdotool", "getwindowfocus", "getwindowname"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

    if int(res_pid.returncode) == 0:
        now_process = psutil.Process(int(res_pid.stdout))
        temp_name = now_process.name()
        if temp_name in get_by_name:
            with open("/proc/{}/comm".format(str(now_process.ppid())), "r") as file:
                name = file.read()
            if name.strip().lower() == temp_name.strip().lower(): #java and java fix
                for key_name in config_applications.keys():
                    if key_name in res_str.stdout.decode("utf-8").lower():
                        name = key_name
                        return name,now_process,res_str.stdout.decode("utf-8")
        else:
            name = now_process.name()
            if len(name) < 2:
                name = "Not app?"
        return name,now_process,res_str.stdout.decode("utf-8")
    else:

        full_name_not_intit = res_str.stdout.decode("utf-8")

        if len(full_name_not_intit) < 2:
            full_name_not_intit = "Not app?"

        print("full_name_not_intit",full_name_not_intit)
        for name_app in config_applications.keys():
            if name_app.lower() in full_name_not_intit.lower():
                name = name_app
                return name, None, res_str.stdout.decode("utf-8")

        else:
            print("Not configurate application {}".format(full_name_not_intit))
            return full_name_not_intit[:128], None, None


def get_status(input_status,name=None):
    app = config_applications.get(name.lower())
    if not(input_status) and name:
        if not app:
            status = "This is the status status."
        else:
            status = app["status"]
        return status
    else:
        status = input_status[:128]
        #print(config_applications)
        if app:
            if app.get("mustHideIf"):
                for hideIfhas in app["mustHideIf"]:
                    #print(hideIfhas,hideIfhas in status.lower())
                    if hideIfhas in status.lower():
                        status = app["status"]
                        return status
                else:
                    return status
            else:
                return status
        else:
            return status

def get_large_image(name):
    cfg = config_applications.get(name.lower())
    if cfg:
        if cfg.get('large_image'):
            return cfg["large_image"]
        else:
            return "none_image"
    else:
        return "none_image"

def get_now_active_window():
    name,now_process,status_full = get_name()
    status = get_status(status_full,name)
    if now_process:
        time_start = now_process.create_time()
        pid = now_process.pid
    else:
        time_start = time.time()
        pid = 1
    large_image = get_large_image(name)
    return {"details":name,"state":status,"start":time_start,"small_image":small_image,"large_image":large_image,"large_text":"111","small_text":str(psutil.Process().cpu_percent())}


RPC = Presence(client_id)
RPC.connect()

old_state = get_now_active_window()
RPC.update(**old_state)
while True:
    now_state = get_now_active_window()

    #print(old_state != now_state)
    if (old_state["details"] != now_state["details"]) or (old_state["state"] != now_state["state"]):
        print(now_state)
        old_state = now_state
        RPC.update(**old_state)
    time.sleep(1)
