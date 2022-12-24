import psutil
import pypresence
import time
import win32gui
from util import *
from config import client_id

# Main process for getting connection
def get_server():
	# get the process ID of the application
	app_name = "dreamseeker.exe"
	for proc in psutil.process_iter():
		if proc.name() == app_name:
			app_pid = proc.pid
			break

	windows=get_hwnds_for_pid(app_pid)
	windowtitles = [i for i in [str(win32gui.GetWindowText(item))
					for item in windows] if i != ""]

	# get a list of network connections
	connections = psutil.net_connections()

	# filter the list of connections by the process ID of the application
	app_connections = [conn for conn in connections if conn.pid == app_pid]

	# filter the list of connections
	filtered_connections = [conn for conn in app_connections if conn.raddr and conn.raddr[0] != "127.0.0.1"]

	for conn in filtered_connections:
		print("This is the server you're connected to " + str(conn.raddr[0]) + ":" + str(conn.raddr[1]))
		break # we're keeping the first one we find

	if len(filtered_connections) == 0:
		return

	server_data = fetch(conn.raddr[0], conn.raddr[1], "status")
	if "ip" not in server_data:
		server_data["ip"] = conn.raddr[0]
	if "port" not in server_data:
		server_data["port"] = conn.raddr[1]
	if "name" not in server_data:
		server_data["name"] = windowtitles[0]
	print(server_data)
	return server_data

# Helper for getting values
def get_content(entry, else_value = ""):
	if entry in status and status[entry]:
		return status[entry]
	else:
		return else_value if else_value else ""

# Let's try running it
while True:
	try:
		rp = pypresence.Client(client_id)
		rp.start()
		break
	except:
		time.sleep(15)

# Main loop
while True:
	try:
		status = get_server()
		if status:				
			# Discord rich presence does actually work with images uploaded elsewhere,
			# but for now, i have no idea how to retrieve the icon from the damn WINDOW!
			activity = {"large_text": "Hosted by " + get_content("host", "Host not found"), "large_image": "ss13", "details": get_content("name", get_content("version", "Space Station 13"))}

			activity["start"] = int(time.time())-int(status["round_duration"])

			map = get_content("map_name", "No Map")
			activity["party_id"] = str(get_content("round_id")) + " " + map #apparently terry has NO revision

			mode = get_content("mode", "dynamic")
			activity["state"] = map + ", " + mode
			activity["buttons"] = [{"label": "Join", "url": "byond://" + str(status["ip"]) + ":" + str(status["port"])}, {"label": "Github (Rich Presence)", "url": "https://github.com/SandPoot/ss13rp-refactor"}]

			popcap = get_content("popcap", "120")
			popcap = "120" if(int(popcap) <= 0) else popcap
			activity["party_size"] = [int(get_content("players"))] + [int(popcap)]

			rp.set_activity(**activity)
			time.sleep(15)
		else:
			print("Nothing to report, clearing activity and sleeping")
			rp.clear_activity()
			time.sleep(15)

	except Exception as e:
		time.sleep(10)
		try:
			rp.clear_activity()
			time.sleep(5)
		except Exception as e:
			while True:
				try:
					rp = pypresence.Client(client_id)
					rp.start()
					break
				except:
					time.sleep(20)
