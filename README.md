# Arcade Game
<HTML>
  <body>
    <h1>This project is currently on hold while I learn to use the Unity engine, as I hope to re-make it in C# with GPU rendering</h1>
  <h3>Map Making app:</h3>

<p>This game currently features a partially complete MapMaker in a sepperate file that allows the user to draw their own maps, using the keys 0, 1 and 2 to place empty squares, blocks and enemies respectively, and by pressing 9, place the players spawn point. To export a map, hold space and press the blue button in the bottom right, and it will write the map data into the terminal for copying and pasting, and it will also write the map data to the JSON file, so that you can continue editing it later. Pressing esc will bring up a thumbnail of each saved map in the file, and allow the user to edit one by clicking on it to open it in the main editor.</p>

<h3>Main program</h3>

<p>The main program is far from complete, but currently draws a map image and a collision map from data in the MapBuilding file. The enemies can move and shoot at the player, provided there is a direct line of sight, and the player is within range. The screen follows the player as they move around the map, and drifts towards the players cursor to allow them to look further in whatever direction they are aiming in. in the top-right is a counter of currently alive enemies, and the top-left shows the players current HP. pressing escape will pause the game, and allow the user to quit by clicking the button or reset the game by pressing the reset button. Unpause the game by pressing escape again. Currently the player has a few basic weapons to allow testing of enemy HP mechanics, and bullet collision detection, however later on this will all be re-worked from scratch to become fully customisable</p>

<h4>A full list of intended additions can be found at the top of "main.py"</h4>
  </body>
</HTML>
