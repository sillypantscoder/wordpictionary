from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time
import os
import json
from urllib.parse import unquote
import random

hostName = "0.0.0.0"
serverPort = 11112

class URLQuery:
	def __init__(self, q):
		self.orig = q
		self.fields = {}
		for f in q.split("&"):
			s = f.split("=")
			if len(s) >= 2:
				self.fields[s[0]] = s[1]
	def get(self, key):
		if key in self.fields:
			return self.fields[key]
		else:
			return ''

class GameStatus:
	WAITING_TO_START = 0
	WAITING_FOR_FIRST_WORD = 1
	NEEDS_PICTURE = 2
	CREATING_PICTURE = 3
	NEEDS_WORD = 4
	CREATING_WORD = 5

class Game:
	def __init__(self):
		self.history = []
		self.status = GameStatus.WAITING_TO_START
		self.activePlayer = None
	def get(self, path, query, gameno):
		if path == "/check":
			if query.get("name") not in users: return {
				"status": 303,
				"headers": {
					"Location": f"/?" + query.orig
				},
				"content": ""
			}
			# Check for game status openings
			if self.status == GameStatus.WAITING_FOR_FIRST_WORD:
				return {
					"status": 303,
					"headers": {
						"Location": f"/{gameno}/word?" + query.orig
					},
					"content": ""
				}
			if self.status == GameStatus.NEEDS_PICTURE:
				return {
					"status": 303,
					"headers": {
						"Location": f"/{gameno}/draw?" + query.orig
					},
					"content": ""
				}
			if self.status == GameStatus.NEEDS_WORD:
				return {
					"status": 303,
					"headers": {
						"Location": f"/{gameno}/word?" + query.orig
					},
					"content": ""
				}
			return {
				"status": 303,
				"headers": {
					"Location": f"/?" + query.orig
				},
				"content": ""
			}
		elif path == "/draw":
			if self.status == GameStatus.NEEDS_PICTURE:
				self.activePlayer = unquote(query.orig.split("=")[-1])
				self.status = GameStatus.CREATING_PICTURE
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("public_files/draw2.html")
				}
			elif self.status == GameStatus.CREATING_PICTURE:
				if self.activePlayer == unquote(query.orig.split("=")[-1]):
					return {
						"status": 200,
						"headers": {
							"Content-Type": "text/html"
						},
						"content": read_file("public_files/draw2.html")
					}
			return {
				"status": 303,
				"headers": {
					"Location": f"/{gameno}/check?" + query.orig
				},
				"content": ""
			}
		elif path == "/word":
			if self.status == GameStatus.NEEDS_WORD:
				self.activePlayer = unquote(query.orig.split("=")[-1])
				self.status = GameStatus.CREATING_WORD
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("public_files/word.html")
				}
			elif self.status == GameStatus.WAITING_FOR_FIRST_WORD:
				self.activePlayer = unquote(query.orig.split("=")[-1])
				self.status = GameStatus.CREATING_WORD
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("public_files/word.html").replace("/*X", "")
				}
			elif self.status == GameStatus.CREATING_WORD:
				if self.activePlayer == unquote(query.orig.split("=")[-1]):
					if len(self.history) == 0:
						return {
							"status": 200,
							"headers": {
								"Content-Type": "text/html"
							},
							"content": read_file("public_files/word.html").replace("/*X", "")
						}
					return {
						"status": 200,
						"headers": {
							"Content-Type": "text/html"
						},
						"content": read_file("public_files/word.html")
					}
			return {
				"status": 303,
				"headers": {
					"Location": f"/{gameno}/check?" + query.orig
				},
				"content": ""
			}
		elif path == "/last_word":
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/plain"
				},
				"content": self.history[-1]["word"]
			}
		elif path == "/last_photo.svg":
			try:
				r = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520">
\t<style>
\t\tpath{fill:none;stroke:black;stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}</style>
\t<g style="transform: translate(10px, 10px);">"""
				img = self.history[-1]["image"]
				for i in img:
					r += f"""\t\t<path d="{i}" />"""
	 			# """
				r += """\t</g>
</svg>"""
				return {
					"status": 200,
					"headers": {
						"Content-Type": "image/svg+xml"
					},
					"content": r
				}
			except: return {
				"status": 200,
				"headers": {
					"Content-Type": "image/svg+xml"
				},
				"content": ""
			}
		return {
				"status": 303,
				"headers": {
					"Location": f"/?" + query.orig
				},
				"content": ""
			}
	def post(self, path, body, gameno):
		if path == "/submit_drawing":
			self.history[-1]["image"] = json.loads(body)["p"]
			self.history[-1]["imageuser"] = self.activePlayer
			self.activePlayer = None
			self.status = GameStatus.NEEDS_WORD
			return {
				"status": 200,
				"headers": {},
				"content": ""
			}
		elif path == "/submit_word":
			self.history.append({
				"word": json.loads(body)["word"],
				"worduser": self.activePlayer,
				"image": [],
				"imageuser": ""
			})
			self.activePlayer = None
			self.status = GameStatus.NEEDS_PICTURE
			return {
				"status": 200,
				"headers": {},
				"content": ""
			}
		else:
			return {
				"status": 404,
				"headers": {},
				"content": ""
			}
	def can_join(self, name):
		# Name is not in the last two entries
		if len(self.history) == 0: return True
		if self.history[-1]["imageuser"] == "":
			if self.history[-1]["worduser"] == name: return False
			if len(self.history) > 1 and len(users) > 2:
				if self.history[-2]["imageuser"] == name: return False
		else:
			if self.history[-1]["imageuser"] == name: return False
			if self.history[-1]["worduser"] == name: return False
		return True
	def resultHTML(self):
		entries = []
		for i in self.history:
			paths = []
			for j in i["image"]:
				paths.append(f'<path d="{j}" fill="none" stroke="black" stroke-width="1px" />')
			entries.append(f"<div>Phrase by {i['worduser']}</div><h3>{i['word']}</h3><div>Drawing by {i['imageuser']}:</div><svg viewBox='0 0 520 520'>{''.join(paths)}</svg>")
		return ''.join(entries)
	def __repr__(self) -> str:
		entries = []
		for i in self.history:
			paths = []
			for j in i["image"]:
				paths.append(f"\n  - {j}")
			entries.append(f"""\n- \"{i['word']}\" by {i['worduser']}\n- Drawing by {i['imageuser']}:{''.join(paths)}""")
		return ''.join(entries)

activeGames = [Game()]

def read_file(filename):
	f = open(filename, "r")
	t = f.read()
	f.close()
	return t

def bin_read_file(filename):
	f = open(filename, "rb")
	t = f.read()
	f.close()
	return t

def write_file(filename, content):
	f = open(filename, "w")
	f.write(content)
	f.close()

def getGameInfo():
	msg_word = [
		"%s is writing a sentence",
		"%s is deciphering a picture",
		"%s is extremely confused on what this picture is supposed to be",
		"%s is scratching their head",
		"%s is trying to decipher a terrible picture"
	]
	msg_draw = [
		"%s is drawing",
		"%s is creating a masterpiece",
		"%s is working really hard on a picture that will then go unappreciated",
		"%s is trying to figure out how to draw a strange thing"
	]
	info = []
	for game in activeGames:
		if game.status == GameStatus.CREATING_WORD:
			info.append(random.choice(msg_word).replace("%s", game.activePlayer))
		if game.status == GameStatus.CREATING_PICTURE:
			info.append(random.choice(msg_draw).replace("%s", game.activePlayer))
	if len(info) == 0:
		return "<span style='color: red;'>" + random.choice([
			"Uh oh, nobody is doing anything right now...",
			"Oops, everyone else is also just sitting around...",
			"Nothing interesting is happening right now...",
			"Uh oh, nothing is actually happening right now...",
			"It looks like nothing's going on right now...",
			"Everyone else is also bored...",
			"Something went wrong here..."
		]) + '</span>'
	else:
		return random.choice(info)

users = []
pwd = ''.join([random.choice([*"abcdefghijklmnpqrstuvwxyz0123456789"]) for x in range(4)])
pending = []
def get(path, query: URLQuery):
	if path == "/status_" + pwd:
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": """<!DOCTYPE html>
<html>
	<head>
		<title>Game Status</title>
	</head>
	<body>
		<h1>Game Status</h1>
		<div style="font-family: monospace; white-space: pre;" id="t"></div>
		<div><input type="text" enterheyhint="send" onkeydown="if (event.key == 'Enter') sendMsg(this.value)"><button onclick="sendMsg(this.previousElementSibling.value)">Send</button></div>
		<script>
setInterval(() => {
	var x = new XMLHttpRequest()
	x.open("GET", location.pathname + "/s/")
	x.addEventListener("loadend", (e) => {
		document.querySelector("#t").innerText = e.target.responseText
	})
	x.send()
}, 1000)
function sendMsg(t) {
	var x = new XMLHttpRequest()
	x.open("GET", location.pathname + "/s/" + t)
	x.send()
	document.querySelector("input").value = ""
}
		</script>
	</body>
</html>"""
		}
	elif path.startswith("/status_" + pwd + "/s/"):
		d = path[len("/status_" + pwd + "/s/"):]
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/plain"
			},
			"content": get_manager_info(d)
		}
	elif path == "/":
		if showing_results:
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": f"""<!DOCTYPE html>
<html>
	<head>
		<title>Results</title>
		<link href="main.css" rel="stylesheet" type="text/css" />
		<link href="results.css" rel="stylesheet" type="text/css" />
	</head>
	<body>
		<h1>Results</h1>
		{''.join([f"<h2><i>Game #{i + 1}</i></h2>{g.resultHTML()}" for i, g in enumerate(activeGames)])}
	</body>
</html>"""
			}
		if query.get("name") == '':
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": read_file("public_files/login.html")
			}
		if (query.get("name") not in users) and (query.get("name") not in pending):
			pending.append(query.get("name"))
		if query.get("name") in pending:
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": """<!DOCTYPE html>
	<html>
	<head>
		<title>Waiting</title>
		<script>setTimeout(() => { location.reload() }, 3000)</script>
		<link href="main.css" rel="stylesheet" type="text/css" />
		<link href="wait.css" rel="stylesheet" type="text/css" />
		<link rel="icon" type="image/x-icon" href="wait.ico">
	</head>
	<body>
		<p>Wait to join the game</p>
	</body>
	</html>"""
			}
		hasAnyActiveGames = False
		for g in range(len(activeGames)):
			if activeGames[g].status in [GameStatus.WAITING_FOR_FIRST_WORD, GameStatus.NEEDS_PICTURE, GameStatus.NEEDS_WORD]:
				if activeGames[g].can_join(unquote(query.get("name"))):
					return {
						"status": 303,
						"headers": {
							"Location": f"/{g}/check?" + query.orig
						},
						"content": ""
					}
			if activeGames[g].status not in [GameStatus.WAITING_TO_START]:
				hasAnyActiveGames = True
		if not hasAnyActiveGames:
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": read_file("public_files/gamestart.html").replace("{{PLAYERLIST}}", ''.join(['<li>'+unquote(x)+'</li>' for x in users]))
			}
		# No available games...
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": read_file("public_files/wait.html").replace("{{GAMEINFO}}", getGameInfo())
		}
	elif path.split("/")[1].isdigit():
		gamepath = "/".join(path.split("/")[2:])
		#if gamepath == "refresh": print(f"[R{path.split('/')[1]}]", end="")
		#else: print(f"Request to game {path.split('/')[1]} at /{gamepath}")
		#stdout.flush()
		gameno = int(path.split("/")[1])
		game = activeGames[gameno]
		res = game.get("/" + gamepath, query, gameno)
		return res
	else: # 									404 page / public files
		public_files = os.listdir("public_files")
		if path[1:] in public_files:
			h = {}
			if path.split(".")[-1] == "css":
				h["Content-Type"] = "text/css"
			return {
				"status": 200,
				"headers": h,
				"content": bin_read_file(f"public_files/{path}")
			}
		return {
			"status": 404,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": f"<html><head><title>Word Pictionary</title></head>\n<body>\n\
<h1>Not Found</h1><p><a href='/' style='color: rgb(0, 0, 238);'>Return home</a></p>\
\n</body></html>"
		}

def post(path, body):
	print("POST", path, body)
	if path.split("/")[1].isdigit():
		gamepath = "/".join(path.split("/")[2:])
		#print(f"POST to game {path.split('/')[1]} at /{gamepath}")
		gameno = int(path.split("/")[1])
		game = activeGames[gameno]
		res = game.post("/" + gamepath, body, gameno)
		return res
	else:
		print(f"Bad POST to {path}")
		return {
			"status": 404,
			"headers": {},
			"content": "404"
		}

rs = []
class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		zzz = [*self.path]
		if len(zzz) > 1:
			if zzz[1] in [*"0123456789"]:
				zzz[1] = "#"
		zzz = ''.join(zzz)
		if zzz not in rs:
			if not zzz.startswith("/status"):
				print(zzz)
			#rs.append(zzz)
		splitpath = self.path.split("?")
		res: "dict" = get(splitpath[0], URLQuery(''.join(splitpath[1:]))) # type: ignore
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		c = res["content"]
		if type(c) == str: c = c.encode("utf-8")
		self.wfile.write(c)
	def do_POST(self):
		res = post(self.path, self.rfile.read(int(self.headers["Content-Length"])))
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		self.wfile.write(res["content"].encode("utf-8"))
	def log_message(self, format: str, *args) -> None:
		return;
		if 400 <= int(args[1]) < 500:
			# Errored request!
			print(u"\u001b[31m", end="")
		print(args[0].split(" ")[0], "request to", args[0].split(" ")[1], "(status code:", args[1] + ")")
		print(u"\u001b[0m", end="")
		# don't output requests

showing_results = False
def get_manager_info(in_ch):
	global running
	global showing_results
	res = ""
	# LIST OF GAMES
	for i in [[x, activeGames[x]] for x in range(len(activeGames))]:
		res += f"({i[0] + 1} d/i/r) Game {i[0] + 1} status: {i[1].status} ({['Waiting to start', 'Waiting for 1st word', 'Needs picture', 'Creating picture', 'Needs word', 'Creating word'][i[1].status]}) player: {i[1].activePlayer}\n"
		if in_ch == str(i[0] + 1) + "d":
			i[1].status -= 1
			if i[1].status < 0: i[1].status += 4
		if in_ch == str(i[0] + 1) + "i":
			i[1].status += 1
			if i[1].status >= 4: i[1].status -= 4
		if in_ch == str(i[0] + 1) + "r":
			activeGames.remove(i[1])
	# DECREMENT ALL OPTION
	res += f"\n(d d/i) Change all games' status\n"
	if in_ch == "dd":
		for g in range(len(activeGames)):
			activeGames[g].status -= 1
			if activeGames[g].status < 0: activeGames[g].status += 4
	if in_ch == "di":
		for g in range(len(activeGames)):
			activeGames[g].status += 1
			if activeGames[g].status >= 4: activeGames[g].status -= 4
	# USER LIST
	res += f"Registered users:\n"
	for u in [[x, users[x]] for x in range(len(users))]:
		res += f"  (u{u[0] + 1}) {unquote(u[1])}\n"
		if in_ch == "u" + str(u[0] + 1):
			users.remove(u[1])
	res += f"Pending users:\n"
	for u in [[x, pending[x]] for x in range(len(pending))]:
		res += f"  (p{u[0] + 1} a/d) {unquote(u[1])}\n"
		if in_ch == "p" + str(u[0] + 1) + "d":
			pending.remove(u[1])
		if in_ch == "p" + str(u[0] + 1) + "a":
			pending.remove(u[1])
			users.append(u[1])
			activeGames.append(Game())
	# CLOSE WINDOW MESSAGE
	res += f"(x) Stop the server\n"
	if in_ch == "x":
		running = False
	# CLOSE WINDOW MESSAGE
	res += f"(n) New game\n"
	if in_ch == "n":
		activeGames.append(Game())
	# SHOW RESULTS OPTION
	res += f"(s) Show results: {'Yes' if showing_results else 'No'}\n"
	if in_ch == "s":
		showing_results = not showing_results
	# Flip
	maxwidth = max([len(l) for l in res.split("\n")])
	e = f"\n=={'=' * maxwidth}=="
	info = e + '\n' + '\n'.join([f'| {l.ljust(maxwidth)} |' for l in res.split('\n')]) + e
	return info

if __name__ == "__main__":
	running = True
	showing_results = False
	webServer = HTTPServer((hostName, serverPort), MyServer)
	webServer.timeout = 1
	print("Server started http://%s:%s" % (hostName, serverPort))
	print("Status pwd:", pwd)
	while running:
		try:
			webServer.handle_request()
		except KeyboardInterrupt:
			running = False
	webServer.server_close()
	print("Server stopped")
	print("Results:")
	jsonr = []
	for g in range(len(activeGames)):
		res = repr(activeGames[g])
		jsonr.append(activeGames[g].history)
	n = 1
	while os.path.isfile(f"logs/game_{n}.json"): n += 1
	os.system("mkdir -p logs")
	f = open(f"logs/game_{n}.json", "w")
	f.write(json.dumps(jsonr))
	f.close()