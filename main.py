from http.server import BaseHTTPRequestHandler, HTTPServer
import games
from sys import stdout

hostName = "localhost"
serverPort = 8080

activeGames: "list[games.Game]" = [
	games.Game(),
	games.Game(),
	games.Game(),
	games.Game(),
	games.Game()
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
			"content": """<!DOCTYPE html>
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
\t\t<iframe src="/0/"></iframe>
\t\t<iframe src="/1/"></iframe>
\t\t<iframe src="/2/"></iframe>
\t\t<iframe src="/3/"></iframe>
\t\t<iframe src="/4/"></iframe>
\t</body>
</html>"""
		}
	elif path == "/results":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": """<!DOCTYPE html>
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
\t\t<iframe src="/0/results"></iframe>
\t\t<iframe src="/1/results"></iframe>
\t\t<iframe src="/2/results"></iframe>
\t\t<iframe src="/3/results"></iframe>
\t\t<iframe src="/4/results"></iframe>
\t</body>
</html>"""
		}
	elif path.split("/")[1].isdigit():
		gamepath = "/".join(path.split("/")[2:])
		if gamepath == "refresh": print(f"[R{path.split('/')[1]}]", end="")
		else: print(f"Request to game {path.split('/')[1]} at /{gamepath}")
		stdout.flush()
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
		print(f"POST to game {path.split('/')[1]} at /{gamepath}")
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

if __name__ == "__main__":
	running = True
	webServer = HTTPServer((hostName, serverPort), MyServer)
	print("Server started http://%s:%s" % (hostName, serverPort))
	#threading.Thread(target=game.async_showstate).start()
	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		pass
	webServer.server_close()
	print("Server stopped.")
	running = False
