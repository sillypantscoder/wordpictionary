import json
import os
import datetime

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

class Game:
	def __init__(self):
		self.drawingProgress = 0
		self.submits = [
			{
				"word": "Starting image",
				"img": ["M 0 0 L 500 0 L 500 500 Z", "M 250 250 L 0 500 L 250 500 Z"]
			}
		]
		self.drawingTime: datetime.datetime = datetime.datetime.now()
	def get(self, path):
		if path == "/": #                             / -> /wait
			return {
				"status": 302,
				"headers": {
					"Location": "/wait"
				},
				"content": ""
			}
		if path == "/wait": #                         /wait
			if self.drawingProgress == 0:
				return {
					"status": 302,
					"headers": {
						"Location": "/word.html"
					},
					"content": ""
				}
			elif self.drawingProgress == 2:
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
	\t\tWaiting for other players...""" + ('<br>\n\t\t<a href="/recover">Recover</a>' if ((datetime.datetime.now() - self.drawingTime).total_seconds() >= 2) else '') + """
	\t</body>
	</html>"""
				}
		elif path == "/word.html": #                  /word.html
			if self.drawingProgress:
				#self.drawingProgress = 1
				return {
					"status": 302,
					"headers": {
						"Location": "/wait"
					},
					"content": ""
				}
			else:
				self.drawingProgress = 1
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("public_files/word.html")
				}
		elif path == "/draw.html": #                  /draw.html
			if self.drawingProgress != 2:
				self.drawingProgress = 3
				return {
					"status": 302,
					"headers": {
						"Location": "/wait"
					},
					"content": ""
				}
			else:
				self.drawingProgress = 3
				return {
					"status": 200,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": read_file("public_files/draw.html")
				}
		elif path == "/last_photo.svg": #             /last_photo.svg
			r = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520">
	\t<style>
	\t\tpath{fill:none;stroke:black;stroke-width:10px;stroke-linecap:round;stroke-linejoin:round;}</style>
	\t<g style="transform: translate(10px, 10px);">"""
			img = self.submits[-1]["img"]
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
			if self.drawingProgress in [1, 3]:
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
		elif path == "/last_word": #                  /last_word
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/plain"
				},
				"content": self.submits[-1]["word"]
			}
		elif path == "/thanks": #                     /thanks
			self.drawingProgress = 0
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
		elif path == "/results": #                    /results
			r = """<!DOCTYPE html>
	<html>
	\t<head>
	\t\t<title>Results</title>
	\t\t<style>
	.wordheader {
	\tbackground-color: red;
	\tfont-weight: bold;
	\tfont-size: 1.5em;
	\tpadding: 0.3em;
	\tborder-radius: 0.3em;
	\tmargin: 1em 0;
	}
	img {
	\tmax-width: 25em;
	}
	\t\t</style>
	\t\t<link rel="icon" type="image/x-icon" href="results.ico">
	\t</head>
	\t<body>"""
			for i in range(len(self.submits)):
				r += f"""\t\t<div class="wordheader">{self.submits[i]["word"]}</div>
	\t\t<img src="/getphoto/{i}">"""
			r += """\t</body></html>"""
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": r
			}
		elif path.startswith("/getphoto/"): #         /getphoto/<int>
			i = int(path[10:])
			if i >= len(self.submits):
				return {
					"status": 404,
					"headers": {
						"Content-Type": "text/plain"
					},
					"content": "Not found"
				}
			else:
				r = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520">
	\t<style>
	\t\tpath{fill:none;stroke:black;stroke-width:10px;stroke-linecap:round;stroke-linejoin:round;}</style>
	\t<g style="transform: translate(10px, 10px);">"""
				img = self.submits[i]["img"]
				for i in img:
					r += f"""\t\t<path d="{i}" />"""
				r += """\t</g></svg>"""
				return {
					"status": 200,
					"headers": {
						"Content-Type": "image/svg+xml"
					},
					"content": r
				}
		elif path == "/results_jbdf": #                /results_jbdf
			r = """<!DOCTYPE html>
	<html>
	\t<head>
	\t\t<title>Results</title>
	\t</head>
	\t<body style="white-space: pre;"><script>
	\t\t\tvar r = "AP\""""
			for i in self.submits:
				r += f'\n\t\t\tr += "\\n" + btoa("{i["word"]}")' + "".join([f'\n\t\t\tr += "*" + btoa("{path}")' for path in i["img"]])
			r += """\n\t\t\tdocument.body.textContent = r
	\t\t</script></body>
	</html>"""
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": r
			}
		elif path == "/refresh": #                    /refresh
			drawingTime = datetime.datetime.now()
			return {
				"status": 200,
				"headers": {},
				"content": ""
			}
		elif path == "/recover": #                     /recover
			if self.drawingProgress == 1:
				self.drawingProgress -= 1
				# Recovering word.html
				return {
					"status": 302,
					"headers": {
						"Location": "/word.html"
					},
					"content": ""
				}
			elif self.drawingProgress == 3:
				self.drawingProgress -= 1
				# Recovering draw.html
				return {
					"status": 302,
					"headers": {
						"Location": "/draw.html"
					},
					"content": ""
				}
			else:
				return {
					"status": 404,
					"headers": {
						"Content-Type": "text/html"
					},
					"content": """<!DOCTYPE html>
	<html>
	\t<head>
	\t\t<title>Waiting</title>
	\t\t<link href="wait.css" rel="stylesheet" type="text/css" />
	\t\t<script>setTimeout(() => { location.replace("/wait") }, 5000)</script>
	\t\t<link rel="icon" type="image/x-icon" href="wait.ico">
	\t</head>
	\t<body>
	\t\tNothing to recover
	\t</body>
	</html>"""
				}
		else: # 									404 page / public files
			public_files = os.listdir("public_files")
			if path[1:] in public_files:
				return {
					"status": 200,
					"headers": {},
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
	def post(self, path, body):
		submits = self.submits
		if path == "/submit_word": #				  /submit_word
			submits.append({ "word": json.loads(body)["word"], "img": [] })
			self.drawingProgress = 2
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
				"content": f"<html><head><title>Word Pictionary</title></head>\n<body>\n\
	<h1>Not Found</h1><p><a href='/' style='color: rgb(0, 0, 238);'>Return home</a></p>\
	\n</body></html>"
			}
