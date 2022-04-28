from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading

drawingProgress = 0
submits = [
	{
		"word": "Starting image",
		"img": ["M 0 0 L 500 0 L 500 500 Z", "M 250 250 L 0 500 L 250 500 Z"]
	}
]

hostName = "localhost"
serverPort = 8080

def read_file(filename):  
	f = open(filename, "r")
	t = f.read()
	f.close()
	return t

def write_file(filename, content):
	f = open(filename, "w")
	f.write(content)
	f.close()

def get(path):
	global drawingProgress
	if path == "/": #                             / -> /wait
		return {
			"status": 302,
			"headers": {
				"Location": "/wait"
			},
			"content": ""
		}
	if path == "/wait": #                         /wait
		if drawingProgress == 0:
			return {
				"status": 302,
				"headers": {
					"Location": "/word.html"
				},
				"content": ""
			}
		elif drawingProgress == 2:
			return {
				"status": 302,
				"headers": {
					"Location": "/draw.html"
				},
				"content": ""
			}
		else:
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": """<!DOCTYPE html>
<html>
\t<head>
\t\t<title>Waiting</title>
\t\t<link href="wait.css" rel="stylesheet" type="text/css" />
\t\t<script>setTimeout(() => { location.reload() }, Math.random() * 20000)</script>
\t\t<link rel="icon" type="image/x-icon" href="wait.ico">
\t</head>
\t<body>
\t\tWaiting for other players...
\t</body>
</html>"""
			}
	elif path == "/word.html": #                  /word.html
		if drawingProgress:
			#drawingProgress = 1
			return {
				"status": 302,
				"headers": {
					"Location": "/wait"
				},
				"content": ""
			}
		else:
			drawingProgress = 1
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": read_file("public_files/word.html")
			}
	elif path == "/draw.html": #                  /draw.html
		if drawingProgress != 2:
			drawingProgress = 3
			return {
				"status": 302,
				"headers": {
					"Location": "/wait"
				},
				"content": ""
			}
		else:
			drawingProgress = 3
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": read_file("public_files/draw.html")
			}
	elif path == "/style.css": #                  /style.css
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/css"
			},
			"content": read_file("public_files/style.css")
		}
	elif path == "/last_photo.svg": #             /last_photo.svg
		r = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520">
\t<style>
\t\tpath{fill:none;stroke:black;stroke-width:10px;stroke-linecap:round;stroke-linejoin:round;}</style>
\t<g style="transform: translate(10px, 10px);">"""
		img = submits[-1]["img"]
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
	elif path == "/waitnext": #                   /waitnext
		if drawingProgress in [1, 3]:
			return {
				"status": 302,
				"headers": {
					"Location": "/wait"
				},
				"content": ""
			}
		else:
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": """<!DOCTYPE html>
<html>
\t<head>
\t\t<title>Waiting</title>
\t\t<link href="wait.css" rel="stylesheet" type="text/css" />
\t\t<script>setTimeout(() => { location.reload() }, 5000)</script>
\t\t<link rel="icon" type="image/x-icon" href="wait.ico">
\t</head>
\t<body>
\t\tWaiting for the next player to start...
\t</body>
</html>"""
			}
	elif path == "/wait.css": #                   /wait.css
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/css"
			},
			"content": read_file("public_files/wait.css")
		}
	elif path == "/last_word": #                  /last_word
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/plain"
			},
			"content": submits[-1]["word"]
		}
	elif path == "/thanks": #                     /thanks
		drawingProgress = 0
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": """<!DOCTYPE html>
<html>
\t<head>
\t\t<title>Waiting</title>
\t\t<link href="wait.css" rel="stylesheet" type="text/css" />
\t\t<script>setTimeout(() => { location.replace("/waitnext") }, 5000)</script>
\t\t<link rel="icon" type="image/x-icon" href="wait.ico">
\t</head>
\t<body>
\t\tSubmitted!
\t</body>
</html>"""
		}
	else: # 									404 page
		return {
			"status": 404,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": f"<html><head><title>Task Manager</title></head>\n<body>\n\
<h1>Not Found</h1><p><a href='/' style='color: rgb(0, 0, 238);'>Return home</a></p>\
\n</body></html>"
		}

def post(path, body):
	global drawingProgress
	if path == "/submit_word": #				  /submit_word
		submits.append({ "word": json.loads(body)["word"], "img": [] })
		drawingProgress = 2
		return {
			"status": 200,
			"headers": {},
			"content": ""
		}
	elif path == "/submit_drawing": #			  /submit_drawing
		submits[-1]["img"] = json.loads(body)["p"]
		return {
			"status": 200,
			"headers": {},
			"content": ""
		}
	else:
		return {
			"status": 404,
			"headers": {
				"Content-Type": "text/html"
			},
			"content": f"<html><head><title>Task Manager</title></head>\n<body>\n\
<h1>Not Found</h1><p><a href='/' style='color: rgb(0, 0, 238);'>Return home</a></p>\
\n</body></html>"
		}

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		res = get(self.path)
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		self.wfile.write(res["content"].encode("utf-8"))
	def do_POST(self):
		content_len = int(self.headers.get('Content-Length'))
		post_body = self.rfile.read(content_len).decode("utf-8")
		res = post(self.path, post_body)
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

def async_showstate():
	print()
	while running:
		print("Current state: " + str(drawingProgress) + " - " + ["Waiting for word", "Word", "Waiting for draw", "Drawing"][drawingProgress])
		prevDrawingProgress = drawingProgress
		iters = 0
		while drawingProgress == prevDrawingProgress and iters < 10000 and running: iters += 0.001

if __name__ == "__main__":
	running = True
	webServer = HTTPServer((hostName, serverPort), MyServer)
	print("Server started http://%s:%s" % (hostName, serverPort))
	#threading.Thread(target=async_showstate).start()
	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		pass
	webServer.server_close()
	print("Server stopped.")
	running = False
