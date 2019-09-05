# Star Wars Snake Game
A Star Wars themed snake game, using Python3.<br>
Requires pygame.

The goal is to collect the Jedi, and avoid the Sith.<br>
A Sith breaks the snake, so be careful. This also means you can play forever :)<br>
For your convenience, the Jedi are in blue frames, and the Sith are in red frames.<br>

Move the snake: up/down/left/right arrow keys, or 'W','S','A','D', respectively.<br>
Adjust Snake's speed: '+' and '-'.

May The Force Be With You.<br>
:heart::heart::heart:

To install (See note below for Ubuntu/Debian):
```
git clone https://github.com/irisonia/StarWarsSnakeGame.git
cd StarWarsSnakeGame
python3 -m venv .env
source .env/bin/activate
pip install pygame
```

To install on Ubuntu/Debian, you may need the following command after the ```cd``` command:
```
sudo apt-get install python3-venv
```

and then to run
```
python3 -m snake
```
