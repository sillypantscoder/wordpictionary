import json
import os
import random
import base64

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
		self.drawingProgress: int = 0
		start_imgs = {
			"Triangles": ["M 0 0 L 500 0 L 500 500 Z", "M 250 250 L 0 500 L 250 500 Z"],
			"Circle with rectangle": ["M 250 0 A 1 1 0 0 0 250 500 A 1 1 0 0 0 250 0 Z M 200 50 L 300 50 L 300 450 L 200 450 Z"],
			"4 shapes": ["M 0 0 L 250 0 L 250 250 L 0 250 Z", "M 375 0 A 1 1 0 0 0 375 250 A 1 1 0 0 0 375 0 Z", "M 0 500 L 125 250 L 250 500 Z", "M 375 250 L 292 500 L 500 340 L 250 340 L 458 500 Z"],
			"Twisted diamond": ["M 200 500 L 0 250 L 250 0 L 500 250 L 250 500 L 50 250 L 250 50 L 450 250 L 250 450 L 100 250 L 250 100 L 400 250 L 250 400 L 150 250 L 250 150 L 350 250 L 250 350 L 200 250 L 250 200 L 300 250 L 250 300 L 250 250"],
			"Happy face": ["M 150 0 l 0 250", "M 350 0 l 0 250", "M 50 310 Q 250 500 450 310"]
		}
		chosen_start = random.choice([n for n in start_imgs.keys()])
		self.submits = [
			{
				"word": f"Starting image ({chosen_start})",
				"img": start_imgs[chosen_start]
			}
		]
	def get(self, path, gameno):
		if path == "/": #                             /
			return {
				"status": 302,
				"headers": {
					"Location": f"/"
				},
				"content": ""
			}
		if path == "/check": #                        /check
			if self.drawingProgress == 0:
				return {
					"status": 302,
					"headers": {
						"Location": f"/{gameno}/word.html"
					},
					"content": ""
				}
			elif self.drawingProgress == 2:
				return {
					"status": 302,
					"headers": {
						"Location": f"/{gameno}/draw.html"
					},
					"content": ""
				}
			else:
				return {
					"status": 302,
					"headers": {
						"Location": f"/"
					},
					"content": ""
				}
		elif path == "/word.html": #                  /word.html
			self.drawingProgress = 1
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": read_file("public_files/word.html")
			}
		elif path == "/draw.html": #                  /draw.html
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
	\t\tpath{fill:none;stroke:black;stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}</style>
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
	\t\t<script>setTimeout(() => { location.replace("/?from=""" + str(gameno) + """") }, 5000)</script>
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
\t\t<img src="getphoto/{i}">"""
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
	\t\tpath{fill:none;stroke:black;stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}</style>
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
			r = f"""<!DOCTYPE html>
<html>
\t<head>
\t\t<title>Results</title>
\t</head>
\t<body style="white-space: pre; font-family: monospace;">{self.get_jbdf_content()}</body>
</html>"""
			return {
				"status": 200,
				"headers": {
					"Content-Type": "text/html"
				},
				"content": r
			}
		elif path == "/recover": #                     /recover
			if self.drawingProgress == 1:
				self.drawingProgress -= 1
				# Recovering word.html
				return {
					"status": 302,
					"headers": {
						"Location": f"/{gameno}/word.html"
					},
					"content": ""
				}
			elif self.drawingProgress == 3:
				self.drawingProgress -= 1
				# Recovering draw.html
				return {
					"status": 302,
					"headers": {
						"Location": f"/{gameno}/draw.html"
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
	\t\t<script>setTimeout(() => { location.replace("/""" + str(gameno) + """/wait") }, 5000)</script>
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
	def post(self, path, body, gameno):
		if path == "/submit_word": #				  /submit_word
			self.submits.append({ "word": json.loads(body)["word"], "img": [] })
			self.drawingProgress = 2
			return {
				"status": 200,
				"headers": {},
				"content": ""
			}
		elif path == "/submit_drawing": #			  /submit_drawing
			self.submits[-1]["img"] = json.loads(body)["p"]
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
	def get_jbdf_content(self):
		def btoa(message):
			message_bytes = message.encode('ascii')
			base64_bytes = base64.b64encode(message_bytes)
			base64_message = base64_bytes.decode('ascii')
			return base64_message
		r = "AP"
		for i in self.submits:
			r += "\n" + btoa(i["word"])
			for path in i["img"]:
				r += "*" + btoa(path)
		return r
