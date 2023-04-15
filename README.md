# wordpictionary

A game where you draw pictures to go with words, and write words to go with pictures.

## How to play

From 3 to 8 people can play. (Only 2 people can play but it gets kind of boring.)

No initial setup is needed! To start the game, run `python3 main.py` on a local computer. This will start a web server on localhost (on port 8080) running the game. To join the game, simply connect from another device (e.g. https://computername.local:8080). (The game will initially be in a 'waiting for people to join' mode. To start the game, type in 'di' in the terminal.) You will be prompted to think of a word to describe the picture. Once you finish, someone else will shortly receive a prompt to draw a picture to go with a word. This will continue until you get tired, with people turning words into pictures and back. The idea is that the people who are writing a word don't know what the word was to create that picture, so they might choose a different word. The words eventually have no relation to the original word. If you want a more exciting game, you can intentionally misinterpret the words and pictures. Have fun!

### Drawing

When you are prompted to draw, a prompt will be shown in the bottom left corner. Tap in the gray area to add points. Tap the last point again to finish the path, or tap the first point in the path to make a closed shape. A path the you are in the middle of making is red, and the last path you've made is green. There are "Undo" and "Submit" buttons at the bottom, next to the prompt.

## Viewing the Results

When you are done playing, type S in the terminal. Everyone will be redirected to a results page. This page shows you the history of words and pictures. You can see how the word changed throughout the game, and who contributed. To stop the server, go to the terminal where you ran `python3 main.py` and press Ctrl+C. **Warning: When you stop the server your results will be lost.** The results will be printed when you stop the server.

Have fun!
