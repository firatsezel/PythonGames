# -*- coding: utf-8 -*-

import sfml as sf
from random import randint
import sys
from forbiddenfruit import curse


def new_intersects(obj, rectangle):
    l, t, w, h = rectangle
    rectangle = sf.Rectangle((l, t), (w, h))

    left = max(obj.left, rectangle.left)
    top = max(obj.top, rectangle.top)
    right = min(obj.right, rectangle.right)
    bottom = min(obj.bottom, rectangle.bottom)

    if left < right and top < bottom:
        return sf.Rectangle((left, top), (right - left, bottom - top))


curse(sf.Rectangle, 'intersects', new_intersects)

WIDTH = 800
HEIGHT = 640
TITLE = "PY"
LIFETIME = 100

settings = sf.ContextSettings()

settings.antialiasing_level = 8

FPS = 60
SPEED_FACTOR = 60
MARGIN = 50


class ParticleInfo:
    def __init__(self, velocity, lifetime):
        self.velocity = velocity
        self.lifetime = lifetime


class ParticleSystem:
    def __init__(self):
        self.v_array = None
        self.particles = None

    def load(self, size):
        self.v_array = sf.VertexArray(
            sf.PrimitiveType.POINTS, size
        )
        p_list = []

        for i in xrange(size):
            x = randint(-100, 100)
            y = randint(-100, 100)

            lifetime = randint(1, LIFETIME)

            p_info = ParticleInfo(sf.Vector2(x, y), lifetime)
            p_list.append(p_info)

        self.particles = dict(zip(self.v_array, p_list))


class Game:
    def __init__(self):

        self.window = sf.RenderWindow(sf.VideoMode(WIDTH, HEIGHT), TITLE, sf.Style.DEFAULT, settings)
        self.window.framerate_limit = FPS
        self.clock = sf.Clock()
        # arkaplan
        self.background_texture = None
        self.background = [None, None, None, None, None,
                           None, None, None, None, None,
                           None, None, None, None, None,
                           None, None, None, None, None,
                           None, None, None, None, None, None]

        #star
        self.star = None
        self.star_text = None
        self.starFall = False

        # top
        self.ball = sf.CircleShape(35)
        #self.ball.origin = self.ball.radius, self.ball.radius
        self.ball.position = self.window.size / 2
        self.ballLastHit = -1
        self.alliens = [None, None, None, None]

        # sol cubuk
        self.p_left_txt = None
        self.p_left = None

        # sag cubuk
        self.p_right_txt = None
        self.p_right = None
        self.p_system = ParticleSystem()
        self.p_system.load(2000)
        for i in self.p_system.particles.keys():
            i.position = self.ball.position
            i.color = sf.Color(
                randint(0, 255), randint(0, 255), randint(0, 255)
            )

        x = randint(3, 5)
        y = randint(3, 5)

        if randint(0, 1) % 2 == 0:
            x *= -1.0
        if randint(0, 1) % 2 == 0:
            y *= -1.0

        self.ball_vel = sf.Vector2(x, y)
        self.ball_sound = None
        self.leftkoz = 0
        self.rightkoz = 0

        # score değişkenleri
        self.left_score = 0
        self.right_score = 0

        self.font = None

    def run(self):
        if not self.load_assets():
            sys.exit(-1)

        self.star.position = sf.Vector2(randint(50, 800), randint(50, 600))

        while self.window.is_open:
            for e in self.window.events:
                self.event_handler(e)
            elapsed_time = self.clock.restart().seconds

            self.window.title = "Python - %.2f" % \
                                (1.0 / elapsed_time)

            x = randint(0, 15)
            if x < 15 and self.starFall is True:
                self.star.position = sf.Vector2(randint(100, 400), randint(100, 400))
                self.starFall = False

            for i, j in self.p_system.particles.iteritems():
                i.position += j.velocity * elapsed_time
                j.lifetime -= 1
                if j.lifetime <= 0:
                    j.lifetime = randint(1, LIFETIME)
                    x, y = self.ball.position
                    x += 40
                    y += 40
                    i.position = x, y
            self.update(elapsed_time)
            self.render()

    def event_handler(self, event):
        if type(event) is sf.CloseEvent:
            self.window.close()

    def update(self, delta):
        # Hareket ettirme
        self.ball.move(self.ball_vel * delta * SPEED_FACTOR)

        if sf.Keyboard.is_key_pressed(sf.Keyboard.W):
            self.p_left.move(sf.Vector2(0, -5) * delta * SPEED_FACTOR)
        elif sf.Keyboard.is_key_pressed(sf.Keyboard.S):
            self.p_left.move(sf.Vector2(0, +5) * delta * SPEED_FACTOR)

        if sf.Keyboard.is_key_pressed(sf.Keyboard.UP):
            self.p_right.move(sf.Vector2(0, -5) * delta * SPEED_FACTOR)
        elif sf.Keyboard.is_key_pressed(sf.Keyboard.DOWN):
            self.p_right.move(sf.Vector2(0, +5) * delta * SPEED_FACTOR)

        # cubukların sınırları asmaması
        if self.p_left.position.y < 0:
            x, y = self.p_left.position
            y = 0
            self.p_left.position = sf.Vector2(x, y)
        elif self.p_left.position.y > HEIGHT - self.p_left.global_bounds.height:
            x, y = self.p_left.position
            y = HEIGHT - self.p_left.global_bounds.height
            self.p_left.position = sf.Vector2(x, y)

        if self.p_right.position.y < 0:
            x, y = self.p_right.position
            y = 0
            self.p_right.position = sf.Vector2(x, y)
        elif self.p_right.position.y > HEIGHT - self.p_right.global_bounds.height:
            x, y = self.p_right.position
            y = HEIGHT - self.p_right.global_bounds.height
            self.p_right.position = sf.Vector2(x, y)

        # kenar çarpışma tespiti
        if not self.ball.global_bounds.height - 75 < self.ball.position.y < HEIGHT - self.ball.global_bounds.height:
            x, y = self.ball_vel
            y *= -1.0
            self.ball_vel = sf.Vector2(x, y)

        # cubuk carpisma tespiti
        if self.p_left.global_bounds.intersects(self.ball.global_bounds):
            #self.ball = sf.Sprite(self.alliens[randint(0, 3)])
            self.ballLastHit = 0
            x, y = self.ball_vel
            x *= -1.0 * 1.05
            self.ball_vel = sf.Vector2(x, y)
            self.ball_sound.play()
        elif self.p_right.global_bounds.intersects(self.ball.global_bounds):
            #self.ball = sf.Sprite(self.alliens[randint(0, 3)])
            self.ballLastHit = 1
            x, y = self.ball_vel
            x *= -1.0 * 1.05
            self.ball_vel = sf.Vector2(x, y)
            self.ball_sound.play()

        # star çarpma kontrolü
        if self.star.global_bounds.intersects(self.ball.global_bounds):
            self.starFall = True
            if self.ballLastHit == 0:
                self.left_score += 1
            elif self.ballLastHit == 1:
                self.right_score += 1

        # hız aşımı kontrolü
        x, y = self.ball_vel
        if x > 10:
            x = 10
            self.ball_vel = sf.Vector2(x, y)
        elif x < -10:
            x = -10
            self.ball_vel = sf.Vector2(x, y)

        # kale kontrolu
        if not self.ball.global_bounds.height / 2 < self.ball.position.x < WIDTH - self.ball.global_bounds.height / 2:
            #skor ver
            if self.ball.global_bounds.height / 2 >= self.ball.position.x:
                self.right_score += 1
            else:
                self.left_score += 1

            # sol cubuk
            x = self.p_left.global_bounds.width / 2
            y = (HEIGHT - self.p_left.global_bounds.height) / 2
            self.p_left.position = sf.Vector2(x, y)

            #sag cubuk
            x = (WIDTH - self.p_right.global_bounds.width * 1.5)
            y = (HEIGHT - self.p_right.global_bounds.height) / 2
            self.p_right.position = sf.Vector2(x, y)

            self.ball.position = self.window.size / 2
            x = randint(3, 5)
            y = randint(3, 5)

            if randint(0, 1) % 2 == 0:
                x *= -1.0
            if randint(0, 1) % 2 == 0:
                y *= -1.0

            self.ball_vel = sf.Vector2(x, y)

    def render(self):
        self.window.clear()
        for i in range(21):
            self.window.draw(self.background[i])
        self.window.draw(self.ball)
        self.window.draw(self.p_left)
        self.window.draw(self.p_right)
        self.window.draw(self.star)

        # Fontlar
        scr_lft_text = sf.Text(str(self.left_score))
        scr_lft_text.font = self.font
        scr_lft_text.character_size = 60
        x = (self.window.size.x / 2) - scr_lft_text.global_bounds.width - MARGIN
        y = 50
        scr_lft_text.position = sf.Vector2(x, y)
        scr_lft_text.color = sf.Color.WHITE

        scr_rght_text = sf.Text(str(self.right_score))
        scr_rght_text.font = self.font
        scr_rght_text.character_size = 60
        x = (self.window.size.x / 2) + scr_rght_text.global_bounds.width + MARGIN
        y = 50
        scr_rght_text.position = sf.Vector2(x, y)
        scr_rght_text.color = sf.Color.WHITE

        self.window.draw(scr_lft_text)
        self.window.draw(scr_rght_text)

        vel_text = sf.Text(str(self.ball_vel.x))
        vel_text.position = 100, 25
        vel_text.font = self.font
        vel_text.character_size = 20
        vel_text.color = sf.Color.WHITE

        self.window.draw(vel_text)
        self.window.draw(self.p_system.v_array)

        self.window.display()

    def load_assets(self):
        try:
            self.alliens[0] = sf.Texture.from_file('assets/images/ballAlien.png')
            self.alliens[1] = sf.Texture.from_file('assets/images/ballAlYel.png')
            self.alliens[2] = sf.Texture.from_file('assets/images/alienBlue.png')
            self.alliens[3] = sf.Texture.from_file('assets/images/pinkAlien.png')

            self.ball = sf.Sprite(self.alliens[0])

            self.star_text = sf.Texture.from_file('assets/images/star.png')
            self.star = sf.Sprite(self.star_text)

            self.p_left_txt = sf.Texture.from_file('assets/images/gallswall.png')
            self.p_left = sf.Sprite(self.p_left_txt)
            x = self.p_left.global_bounds.width / 2
            y = (HEIGHT - self.p_left.global_bounds.height) / 2
            self.p_left.position = sf.Vector2(x, y)

            self.p_right_txt = sf.Texture.from_file('assets/images/woodwall.png')
            self.p_right = sf.Sprite(self.p_right_txt)
            x = (WIDTH - self.p_right.global_bounds.width * 1.5)
            y = (HEIGHT - self.p_right.global_bounds.height) / 2
            self.p_right.position = sf.Vector2(x, y)

            buffer = sf.SoundBuffer.from_file('assets/sounds/tone1.ogg')
            self.ball_sound = sf.Sound(buffer)

            self.font = sf.Font.from_file('assets/fonts/kenvector_future_thin.ttf')

            self.background_texture = sf.Texture.from_file("assets/images/grassMowed.png")
            x = 0
            y = 0
            for i in range(21):
                self.background[i] = sf.Sprite(self.background_texture)
                self.background[i].position = x, y
                x += 160
                if i % 5 == 0 and i is not 0:
                    y += 160
                    x = 0

        except IOError:
            return False

        return True


if __name__ == '__main__':
    r = Game()
    r.run()