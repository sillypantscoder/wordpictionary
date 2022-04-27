const express = require('express')
const app = express()
const port = 9031

app.use(express.json({limit: "25MB"})) // for parsing application/json
app.use((err, req, res, next) => {
	if (err) {
		console.log("Error: " + err.name + " from IP " + req.ip)
		res.status(413).send(err.name)
	} else {
		next()
	}
})
app.use(express.urlencoded({ extended: true })) // for parsing application/x-www-form-urlencoded
app.use((req, res, next) => {
	var done = false;
	switch (req.url) {
		case "/word.html":
		case "word.html":
			if (drawingProgress) {
				res.redirect(303, "/wait")
				done = true
			}
			drawingProgress = 1
		case "/refresh":
		case "refresh":
			drawingTime = new Date()
			break;
		case "/draw.html":
		case "draw.html":
			if (drawingProgress != 2) {
				res.redirect(303, "/wait")
				done = true
			}
			drawingProgress = 3
			break;
		case "/thanks":
		case "thanks":
			drawingProgress = 0
			break;
	}
	if (! done) {
		next()
	}
})
app.use(express.static('public_files'))


/*

app.get('/path', (req, res) => res.status(200).send(`
HTML data
`))

res.status(200).send(`
HTML data
`)

app.post('/path', (req, res) => {
	req.body.field_in_form
	res.status(200).send(`
HTML data
`)
})

app.put('/path', (req, res) => {
	req.body.field_in_form
	res.status(200).send(`
HTML data
`)
})

<form method='POST' action='/path'>

*/


var submits = [
	{
		word: "Starting image",
		img: ["M 0 0 L 500 0 L 500 500 Z", "M 250 250 L 0 500 L 250 500 Z"]
	}
]
var drawingProgress = 0
var drawingTime = new Date()
app.get('/', (req, res) => {
	res.redirect(301, "/wait")
})
app.get('/last_photo.svg', (req, res) => {
	var r = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520">
\t<style>
\t\tpath{fill:none;stroke:black;stroke-width:10px;stroke-linecap:round;stroke-linejoin:round;}</style>
\t<g style="transform: translate(10px, 10px);">`
	var img = submits[submits.length - 1].img
	for (var i = 0; i < img.length; i++) {
		r += `\t\t<path d="${img[i]}" />`
	}
	r += `\t</g>
</svg>`
	res.set({
		"Content-Type": "image/svg+xml"
	}).send(r)
})
app.get('/last_word', (req, res) => {
	res.send(submits[submits.length - 1].word)
})
app.get('/getphoto/:pid', (req, res) => {
	var r = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520">
\t<style>
\t\tpath{fill:none;stroke:black;stroke-width:10px;stroke-linecap:round;stroke-linejoin:round;}</style>
\t<g style="transform: translate(10px, 10px);">`
	var img = submits[Number(req.params.pid)].img
	for (var i = 0; i < img.length; i++) {
		r += `\t\t<path d="${img[i]}" />`
	}
	r += `\t</g>
</svg>`
	res.set({
		"Content-Type": "image/svg+xml"
	}).send(r)
})
app.post('/submit_word', (req, res) => {
	submits.push({word: req.body.word, img: []})
	drawingProgress = 2
	res.send()
})
app.post('/submit_drawing', (req, res) => {
	submits[submits.length - 1]["img"] = req.body.p
	res.send()
})
app.get('/results', (req, res) => {
	var r = `<!DOCTYPE html>
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
\t<body>`
	for (let i = 0; i < submits.length; i++) {
		const sub = submits[i];
		r += `\n\t\t<div class="wordheader">${sub.word}</div>\n\t\t<img src="/getphoto/${i}">`
	}
	r += `
\t</body>
</html>`
	res.send(r)
})
app.get('/results_jbdf', (req, res) => {
	var r = `<!DOCTYPE html>
<html>
\t<head>
\t\t<title>Results</title>
\t</head>
\t<body style="white-space: pre;"><script>
\t\t\tvar r = "AP"`
	for (let i = 0; i < submits.length; i++) {
		const sub = submits[i];
		r += `\n\t\t\tr += "\\n" + btoa("${sub.word}")`
		for (let p = 0; p < sub.img.length; p++) {
			const path = sub.img[p];
			r += `\n\t\t\tr += "*" + btoa("${path}")`
		}
	}
	r += `\n\t\t\tdocument.body.textContent = r
\t\t</script></body>
</html>`
	res.send(r)
})
app.get('/thanks', (req, res) => {
	res.send(`<!DOCTYPE html>
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
</html>`)
})
app.get('/recover', (req, res) => {
	switch (drawingProgress) {
		case 1:
			drawingProgress--;
			res.redirect(303, "word.html")
			break;
		case 3:
			drawingProgress--;
			res.redirect(303, "draw.html")
			break;
		default:
			res.send(`<!DOCTYPE html>
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
</html>`)
	}
})
app.get('/waitnext', (req, res) => {
	if (drawingProgress == 1 || drawingProgress == 3) {
		res.redirect(303, "/wait")
		return;
	}
	res.send(`<!DOCTYPE html>
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
</html>`)
})
app.get('/wait', (req, res) => {
	if (drawingProgress == 0) {
		res.redirect(303, "/word.html")
	} else if (drawingProgress == 2) {
		res.redirect(303, "/draw.html")
	} else if (new Date()-drawingTime > 2000) {
		res.send(`<!DOCTYPE html>
<html>
\t<head>
\t\t<title>Waiting</title>
\t\t<link href="wait.css" rel="stylesheet" type="text/css" />
\t\t<script>setTimeout(() => { location.reload() }, Math.random() * 20000)</script>
\t\t<link rel="icon" type="image/x-icon" href="wait.ico">
\t</head>
\t<body>
\t\tWaiting for other players...<br>
\t\t<a href="/recover">Recover</a>
\t</body>
</html>`)
	} else {
		res.send(`<!DOCTYPE html>
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
</html>`)
	}
})
app.get('/refresh', (req, res) => {
	res.send()
})

app.listen(port, () => console.log(`Listening at http://localhost:${port}`))

