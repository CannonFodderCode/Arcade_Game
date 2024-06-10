# Arcade Game
<HTML>
  <body>
  <h3>Map Making app:</h3>

<p>This game currently features a MapMaker in a sepperate file that allows the user to draw their own maps, using the keys 0, 1 and 2 to place empty squares, blocks and enemies respectively. To export a map, hold space and press the blue button in the bottom right, and it will write the mpa data into the terminal for copying and pasting, and it will also write the map data to the JSON file, so that you can continue editing it later.</p>

<h3>Main program</h3>

<p>The main program is not complete, but currently draws a map image and a collision map from data in the MapBuilding file. The enemies can move and shoot at the player, provided there is a direct line of sight, and the player is within range. The screen follows the player as they move around the map, and drifts towards the players cursor to allow them to look further in whatever direction they are aiming in.</p>
<h3>Next steps:</h3>
<ul>
  <li>Set player spawn point in map data - extract when building level</li>
  <li>Add GUI elements that display player HP, XP, and spaces for ammo and equiped weapons</li>
  <li>Add a test weapon for the player</li>
  <li>Make Pause menu, and main menu screens</li>
  <li>Create a second map which gets loaded upon all enemies in map 1 defeated</li>
</ul>
  </body>
</HTML>
