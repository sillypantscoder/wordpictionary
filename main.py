from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time
import os
import json

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
	def get(self, path, query, gameno):
		if path == "/check":
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
					"Location": f"/"
				},
				"content": ""
			}
		elif path == "/draw":
			if self.status == GameStatus.NEEDS_PICTURE:
				self.status = GameStatus.CREATING_PICTURE
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("public_files/draw.html")
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
				self.status = GameStatus.CREATING_WORD
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("public_files/word.html")
				}
			if self.status == GameStatus.WAITING_FOR_FIRST_WORD:
				self.status = GameStatus.CREATING_WORD
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("public_files/word.html").replace("/*X", "")
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
			self.history[-1]["imageuser"] = json.loads(body)["user"]
			self.status = GameStatus.NEEDS_WORD
			return {
				"status": 200,
				"headers": {},
				"content": ""
			}
		elif path == "/submit_word":
			self.history.append({
				"word": json.loads(body)["word"],
				"worduser": json.loads(body)["user"],
				"image": [],
				"imageuser": ""
			})
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
		if self.history[-1]["worduser"] == name: return False
		if self.history[-1]["imageuser"] == name: return False
		if len(self.history) > 1 and len(users) > 2:
			if self.history[-2]["worduser"] == name: return False
			if self.history[-2]["imageuser"] == name: return False
		return True
	def resultHTML(self):
		entries = []
		for i in self.history:
			paths = []
			for j in i["image"]:
				paths.append(f"<path d=\"{j}\" fill=\"none\" stroke=\"black\" stroke-width=\"1px\" />")
			entries.append(f"<h1>{i['word']}<span style='font-size: 1rem;'> by {i['worduser']}</span></h1><div>Drawing by {i['imageuser']}:</div><svg viewBox='0 0 520 520'>{''.join(paths)}</svg>")
		return ''.join(entries)
	def __repr__(self) -> str:
		entries = []
		for i in self.history:
			paths = []
			for j in i["image"]:
				paths.append(f"\n  - {j}")
			entries.append(f"\n- \"{i['word']}\" by {i['worduser']}\n- Drawing by {i['imageuser']}:{''.join(paths)}")
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

users = []
def get(path, query: URLQuery):
	if path == "/":
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
	</head>
	<body>
		<h1>Results</h1>
		{''.join([f"<h2 style='background:black;color:white;margin:1em;padding:1em;border-radius:1em;'><i>Game #{i + 1}</i></h2>{g.resultHTML()}" for i, g in enumerate(activeGames)])}
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
		if query.get("name") not in users:
			users.append(query.get("name"))
			activeGames.append(Game())
		for g in range(len(activeGames)):
			if activeGames[g].can_join(query.get("name")):
				if activeGames[g].status in [GameStatus.WAITING_FOR_FIRST_WORD, GameStatus.NEEDS_PICTURE, GameStatus.NEEDS_WORD]:
					return {
						"status": 303,
						"headers": {
							"Location": f"/{g}/check?" + query.orig
						},
						"content": ""
					}
		# No available games...
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": ("""<!DOCTYPE html>
<html>
\t<head>
\t\t<title>Waiting</title>
\t\t<script>setTimeout(() => { location.reload() }, Math.random() * 20000)</script>
\t\t<link href="main.css" rel="stylesheet" type="text/css" />
\t\t<link rel="icon" type="image/x-icon" href="wait.ico">
\t</head>
\t<body>
\t\tWaiting for other players...<br><br>
\t\t<button onclick="location.reload()">Refresh</button>
\t</body>
</html>""")
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

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
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
def async_manager():
	global running
	global showing_results
	# Get char
	chars = []
	def getChar():
		if len(chars) > 0:
			return chars.pop()
		else:
			return ''
	def async_get_chars():
		while running:
			chars.append(input())
	threading.Thread(target=async_get_chars, name="pygame_get_chars_thread", args=[]).start()
	# Main loop
	running = True
	while running:
		curchar = getChar().lower()
		res = ""
		# LIST OF GAMES
		for i in range(len(activeGames)):
			res += f"({i + 1} d/i/r) Game {i + 1} status: {activeGames[i].status} ({['Waiting to start', 'Waiting for 1st word', 'Needs picture', 'Creating picture', 'Needs word', 'Creating word'][activeGames[i].status]})\n"
			if curchar == str(i + 1) + "d":
				activeGames[i].status -= 1
				if activeGames[i].status < 0: activeGames[i].status += 4
			if curchar == str(i + 1) + "i":
				activeGames[i].status += 1
				if activeGames[i].status >= 4: activeGames[i].status -= 4
			if curchar == str(i + 1) + "r":
				activeGames.pop(i)
		# DECREMENT ALL OPTION
		res += f"\n(D d/i) Change all games' status\n"
		if curchar == "dd":
			for g in range(len(activeGames)):
				activeGames[g].status -= 1
				if activeGames[g].status < 0: activeGames[g].status += 4
		if curchar == "di":
			for g in range(len(activeGames)):
				activeGames[g].status += 1
				if activeGames[g].status >= 4: activeGames[g].status -= 4
		# USER LIST
		res += f"Users:\n"
		for u in range(len(users)):
			res += f"  (u{u + 1}) {users[u]}\n"
			if curchar == "u" + str(u + 1):
				users.pop(u)
		# CLOSE WINDOW MESSAGE
		res += f"Press Ctrl-C then Enter to stop the server\n"
		# CLOSE WINDOW MESSAGE
		res += f"(N) New game\n"
		if curchar == "n":
			activeGames.append(Game())
		# SHOW RESULTS OPTION
		res += f"(S) Show results: {'Yes' if showing_results else 'No'}\n"
		if curchar == "s":
			showing_results = not showing_results
		"""# GAME CHECKING OPTION
		res += f"(G) Game checking: {'Yes' if allow_game_checking else 'No'}"
		if curchar == "g":
			allow_game_checking = not allow_game_checking"""
		# Flip
		maxwidth = max([len(l) for l in res.split("\n")])
		e = f"\n=={'=' * maxwidth}=="
		print('\n'.join([f'| {l.ljust(maxwidth)} |' for l in res.split('\n')]) + e)
		time.sleep(1)

if __name__ == "__main__":
	running = True
	showing_results = False
	webServer = HTTPServer((hostName, serverPort), MyServer)
	webServer.timeout = 1
	print("Server started http://%s:%s" % (hostName, serverPort))
	threading.Thread(target=async_manager).start()
	while running:
		try:
			webServer.handle_request()
		except KeyboardInterrupt:
			running = False
	webServer.server_close()
	print("Server stopped")
	print("Results:")
	for g in range(len(activeGames)):
		res = repr(activeGames[g])
		print(f"\nGame {g}:{res}")
	print("\nPress Enter to exit...")
