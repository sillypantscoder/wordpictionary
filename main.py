from http.server import BaseHTTPRequestHandler, HTTPServer
import games
from sys import stdout
import pygame
import threading

hostName = "localhost"
serverPort = 8080

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
	pygame.font.init()
	screensize = [500, 500]
	screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)
	pygame.display.set_caption("Word Pictionary")
	pygame.display.set_icon(pygame.image.load("window.ico"))
	font = pygame.font.SysFont(pygame.font.get_default_font(), 20)
	fontheight = font.render("0", True, (0, 0, 0)).get_height()
	# Main loop
	running = True
	c = pygame.time.Clock()
	while running:
		clickpos = []
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.VIDEORESIZE:
				screensize = event.size
				screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)
			elif event.type == pygame.MOUSEBUTTONUP:
				clickpos.append(event.pos)
		# Drawing
		screen.fill((255, 255, 255))
		# LIST OF GAMES
		for i in range(len(activeGames)):
			r = font.render(f"Game {i + 1} status: {activeGames[i].drawingProgress} ({['Waiting for word', 'Word', 'Waiting for draw', 'Drawing'][activeGames[i].drawingProgress]})", True, (0, 0, 0))
			screen.blit(r, (0, i * fontheight))
			resultsrect = r.get_rect().move(0, i * fontheight)
			for p in clickpos:
				if resultsrect.collidepoint(*p):
					activeGames[i].drawingProgress -= 1
					if activeGames[i].drawingProgress < 0: activeGames[i].drawingProgress += 4
		# DECREMENT ALL OPTION
		r = font.render(f"Click to decrement all games' status", True, (0, 0, 0))
		screen.blit(r, (0, (i + 2) * fontheight))
		resultsrect = r.get_rect().move(0, (i + 2) * fontheight)
		for p in clickpos:
			if resultsrect.collidepoint(*p):
				for g in range(len(activeGames)):
					activeGames[g].drawingProgress -= 1
					if activeGames[g].drawingProgress < 0: activeGames[g].drawingProgress += 4
		# CLOSE WINDOW MESSAGE
		r = font.render(f"Close this window to stop the server", True, (0, 0, 0))
		screen.blit(r, (0, (i + 3) * fontheight))
		# SHOW RESULTS OPTION
		r = font.render(f"Show results: {'Yes' if show_results else 'No'}", True, (0, 0, 0))
		screen.blit(r, (0, (i + 4) * fontheight))
		resultsrect = r.get_rect().move(0, (i + 4) * fontheight)
		for p in clickpos:
			if resultsrect.collidepoint(*p):
				show_results = not show_results
		# Flip
		pygame.display.flip()
		c.tick(60)

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
	print("Server stopped.")
