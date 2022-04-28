# wordpictionary

A game where you draw pictures to go with words, and write words to go with pictures.

## How to play

From 2 to 8 people can play. (More than 8 people can connect but it starts getting kind of boring.)

No initial setup is needed! To start the game, run `python3 main.py` on a local computer. This will start a web server on localhost (on port 8080) running the game. To join the game, simply connect from another device (e.g. https://computername.local:8080). You will be prompted to think of a word to describe the picture. Once you finish, someone else will shortly receive a prompt to draw a picture to go with a word. This will continue until you get tired, with people turning words into pictures and back. The idea is that the people who are writing a word don't know what the word was to create that picture, so they might choose a different word. The words eventually have no relation to the original word. If you want a more exciting game, you can intentionally misinterpret the words and pictures. Have fun!

### Drawing

When you are prompted to draw, a prompt will be shown in the bottom left corner. Tap in the gray area to add points. Tap the last point again to finish the path, or tap the first point in the path to make a closed shape. A path the you are in the middle of making is red, and the last path you've made is green. There are "Undo" and "Submit" buttons at the bottom, next to the prompt.

### Recovering

On some devices, you might accidentally pull down from the top of the page or a similar gesture. When this happens, you will lose your drawing and be redirected to the "waiting" page. To fix this, a "Recover" button will appear on the "waiting" page that lets you go back to the "drawing" page.

## Viewing the Results

When you are done playing, have everyone go to https://computername.local:8080/results. This page shows you the history of words and pictures. You can see how the word changed throughout the game. To stop the server, go to the terminal where you ran `python3 main.py` and press Ctrl+C. **Warning: When you stop the server your results will be lost.** To download your results so you can use them later, go to https://computername.local:8080/results_jbdf and save that file. To view the results later, go to https://jbdf.jasonroman.repl.co/ and click Choose File. Select the file you downloaded, then press Upload, Parse, and then "Open with Word-Pictionary". Scroll down to see your results.

Have fun!
