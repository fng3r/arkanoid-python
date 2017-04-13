Author.
Dmitry Nagaev

Launch.
arkanoid.py

Tests.
tests\test_logic.py

Control.
Left arrow - move ship left
Right arrow - move ship right
Space - release ball
X - shoot
P - pause
Esc - go to main menu

Creating levels.
To create custom level you should create file <number>.txt in directory
'levels'. Only 12 blocks are permitted in a single block's row, the rest of
them  will be ignored. The same thing is about number of block's rows.
Levels will follow in lexicographical order according to filename
corresponding to a specific level.
Each block should be designated as a single symbol:
'C' - Common block
'S' - Strong block
'U' - Unbreakable block
'*' - empty place
Other symbols will be interpreted as empty place.
//