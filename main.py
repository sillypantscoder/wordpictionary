from http.server import BaseHTTPRequestHandler, HTTPServer
import games
from sys import stdout
import pygame
import threading
import time

hostName = "0.0.0.0"
serverPort = 11233

numberOfGames = 7
activeGames: "list[games.Game]" = [
	games.Game() for g in range(numberOfGames)
]

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

def get(path):
	if path == "/":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": ("""<!DOCTYPE html>
<html>
\t<head>
\t\t<title>Word Pictionary</title>
\t\t<style>
iframe {
\twidth: 60vh;
\theight: 50em;
\tborder: none;
\toutline: 0.05em solid #000;
}
\t\t</style>
\t</head>
\t<body>
\t\t<h1>Word Pictionary - Results</h1>
""" + ''.join([f'\t\t<iframe src="/{g}/results"></iframe>' for g in range(numberOfGames)]) + """
\t</body>
</html>""" if show_results else """<!DOCTYPE html>
<html>
\t<head>
\t\t<title>Word Pictionary</title>
\t\t<style>
iframe {
\twidth: 60vh;
\theight: 50em;
\tborder: none;
\toutline: 0.05em solid #000;
}
\t\t</style>
\t</head>
\t<body>
\t\t<h1>Word Pictionary</h1>
""" + ''.join([f'\t\t<iframe src="/{g}/"></iframe>' for g in range(numberOfGames)]) + """
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
		res = game.get("/" + gamepath, gameno)
		return res
	else:
		print(f"Bad request to {path}")
		return {
			"status": 404,
			"headers": {},
			"content": "404"
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
		res = get(self.path)
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

def async_pygame():
	global running
	global show_results
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
			res += f"Game {i + 1} status: {activeGames[i].drawingProgress} ({['Waiting for word', 'Word', 'Waiting for draw', 'Drawing'][activeGames[i].drawingProgress]})\n"
			if curchar == str(i + 1):
				activeGames[i].drawingProgress -= 1
				if activeGames[i].drawingProgress < 0: activeGames[i].drawingProgress += 4
		# DECREMENT ALL OPTION
		res += f"\n(D) Decrement all games' status\n"
		if curchar == "d":
			for g in range(len(activeGames)):
				activeGames[g].drawingProgress -= 1
				if activeGames[g].drawingProgress < 0: activeGames[g].drawingProgress += 4
		# CLOSE WINDOW MESSAGE
		res += f"Press Ctrl-C then Enter to stop the server\n"
		# SHOW RESULTS OPTION
		res += f"(S) Show results: {'Yes' if show_results else 'No'}"
		if curchar == "s":
			show_results = not show_results
		# Flip
		maxwidth = max([len(l) for l in res.split("\n")])
		e = f"\n=={'=' * maxwidth}=="
		print('\n'.join([f'| {l.ljust(maxwidth)} |' for l in res.split('\n')]) + e)
		time.sleep(1)

if __name__ == "__main__":
	running = True
	show_results = False
	webServer = HTTPServer((hostName, serverPort), MyServer)
	webServer.timeout = 1
	print("Server started http://%s:%s" % (hostName, serverPort))
	threading.Thread(target=async_pygame).start()
	while running:
		try:
			webServer.handle_request()
		except KeyboardInterrupt:
			running = False
	webServer.server_close()
	print("Server stopped - Press Enter to exit")
	print("JBDF results:")
	for g in range(len(activeGames)):
		res = activeGames[g].get_jbdf_content()
		print(f"GAME {g + 1} - {res}\n")

