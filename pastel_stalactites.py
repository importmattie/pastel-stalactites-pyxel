import numpy as np
import pyxel

class App:
    def __init__(self):
        self.version = 'v1.0.0'

        pyxel.init(256, 180, fps=60, caption="Pastel Stalactites (" + self.version + ") by Matt Niznik")

        self.score = 0
        self.distance = 0
        self.ppd = 0 # ppd = "points per distance"; doing per 100 pixels to make it more readable

        self.stal_colors = list(range(0,16))
        del self.stal_colors[7] # white is the border
        del self.stal_colors[0] # black is the background

        self.stal_width = 8
        self.max_stal_height = 150
        self.stal_speed = 1
        self.stals = [] # will initialize when game starts

        self.hero_starting_height = 150
        self.hero_height = self.hero_starting_height
        self.hero_x = 10
        self.hero_width = self.stal_width*2
        self.hero_color = self.random_color()

        self.rotating_font_color = self.random_color()
        self.game_over_message = None
        self.game_state = 'title' # can be 'title', 'playing', 'gameover'

        pyxel.run(self.update, self.draw)

    def update(self):
        if (self.game_state != 'playing'):
            if (pyxel.frame_count % 5):
                self.rotating_font_color = self.random_color()
            if (len(self.stals)):
                self.stals = []

            # check to see if the player wants to move on
            if (pyxel.btnr(pyxel.KEY_SPACE)):
                if (self.game_state == 'title'):
                    self.game_state = 'playing'
                    self.initialize()
                if (self.game_state == 'gameover'):
                    self.game_state = 'title'
        else:
            if (pyxel.btn(pyxel.KEY_UP)):
                self.hero_height = np.minimum(self.hero_height + 1, pyxel.height)
            elif (pyxel.btn(pyxel.KEY_DOWN)):
                self.hero_height = np.maximum(self.hero_height - 1, 4)

            self.update_stal()
            self.update_hero()
            self.check_collision()

    def draw(self):
        pyxel.cls(0)

        # Useful for aligning text
        # pyxel.line(pyxel.width//4, 0, pyxel.width//4, pyxel.height, 7)
        # pyxel.line(pyxel.width//2, 0, pyxel.width//2, pyxel.height, 7)
        # pyxel.line(pyxel.width//4*3, 0, pyxel.width//4*3, pyxel.height, 7)

        if (self.game_state == 'title'):
            pyxel.text(93, pyxel.height//2 - 8, 'PASTEL STALACTITES', self.rotating_font_color)
            pyxel.text(118, pyxel.height//2, self.version, self.rotating_font_color)
            pyxel.text(94, pyxel.height//2 + 8, 'by Matthew Niznik', 11)
            pyxel.text(85, pyxel.height//2 + 24, '(press SPACE to start)', 7)
        elif (self.game_state == 'gameover'):
            pyxel.text(self.game_over_message['x'], pyxel.height//2 - 8, self.game_over_message['msg'], self.rotating_font_color)
            pyxel.text(80, pyxel.height//2 + 8, 'Score: ' + str(int(self.score)), 7)
            pyxel.text(80, pyxel.height//2 + 16, 'Distance: ' + str(self.distance), 7)
            pyxel.text(80, pyxel.height//2 + 24, 'Score/100 px: ' + str(self.ppd), 7)
            pyxel.text(80, pyxel.height//2 + 40, '(press SPACE to continue)', 7)
        else:
            pyxel.rect(self.hero_x, pyxel.height-self.hero_height, self.hero_width, self.hero_height, self.hero_color)
            pyxel.rectb(self.hero_x, pyxel.height-self.hero_height, self.hero_width, self.hero_height, 7)

            pyxel.text(40, pyxel.height - 30, 'Score: ' + str(int(self.score)), 7)
            pyxel.text(40, pyxel.height - 20, 'Distance: ' + str(self.distance), 7)
            pyxel.text(40, pyxel.height - 10, 'Score/100 px: ' + str(self.ppd), 7)

            for i in range(0, len(self.stals)):
                stal = self.stals[i]
                pyxel.rect(stal['x'], 0, self.stal_width, stal['height'], stal['color'])
                pyxel.rectb(stal['x'], 0, self.stal_width, stal['height'], 7)

    def initialize(self):
        for i in range(0, int(256/self.stal_width)+1):
            self.stals.append({
                'x': 255 + (i*self.stal_width),
                'height': np.random.randint(1, self.max_stal_height),
                'color': self.random_color()
            })
        self.hero_height = self.hero_starting_height
        self.score = 0

    def update_stal(self):
        # stals
        if (pyxel.frame_count % 2 == 0):
            for i in range(0,len(self.stals)):
                stal = self.stals[i]
                stal['x'] -= self.stal_speed
                if (stal['x'] < -1*self.stal_width):
                    stal['x'] = 255
                    stal['height'] = np.random.randint(1, 150)
                    stal['color'] = self.random_color()

    def update_hero(self):
        if (pyxel.frame_count % 5 == 0):
            self.hero_color = self.random_color()

    def check_collision(self):
        stal_heights_over_player = []
        for i in range(0,len(self.stals)):
            stal = self.stals[i]
            if (stal['x'] > (self.hero_x - self.stal_width) and stal['x'] < self.hero_x + self.hero_width):
                stal_heights_over_player.append(stal['height'])

        if ((len(stal_heights_over_player) == 0) or (self.hero_height < (pyxel.height - np.max(stal_heights_over_player)))):
            self.update_score()
        else:
            self.game_state = 'gameover'
            self.update_game_over_message()

    def update_score(self):
        min_scoring_height = pyxel.height - self.max_stal_height
        self.score += np.maximum((self.hero_height - min_scoring_height), 0)*0.04
        self.distance += self.stal_speed
        self.ppd = int(100*self.score/self.distance)

    def random_color(self):
        np.random.shuffle(self.stal_colors)
        return self.stal_colors[0]

    def update_game_over_message(self):
        game_over_messages = [
            {'x': 20, 'msg': 'You didn\'t lose; you just found a new way to not win!'},
            {'x': 120, 'msg': 'Oops!'}
        ]
        self.game_over_message = game_over_messages[np.random.randint(0, len(game_over_messages))]

App()
