from http.server import BaseHTTPRequestHandler, HTTPServer
import games

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

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == "/": return
		gameno = int(self.path.split("/")[1])
		game = activeGames[gameno]
		path = self.path.split("/")[2]
		res = game.get("/" + path, gameno)
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		c = res["content"]
		if type(c) == str: c = c.encode("utf-8")
		self.wfile.write(c)
	def do_POST(self):
		if self.path == "/": return
		gameno = int(self.path.split("/")[1])
		game = activeGames[gameno]
		path = self.path.split("/")[2]
		res = game.post("/" + path, self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"), gameno)
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		self.wfile.write(res["content"].encode("utf-8"))
	def log_message(self, format: str, *args) -> None:
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
