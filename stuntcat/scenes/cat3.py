"""
Cat 3 Module.

"""

import math
import random
from typing import Optional

import pygame
from pygame.surface import Surface
from pygame.sprite import DirtySprite, LayeredDirty

from stuntcat.resources import gfx, sfx, music
from stuntcat.scenes.scene import Scene
from stuntcat.scenes.flying_objects import Fish, NotFish
from stuntcat.scenes.elephant import Elephant


class LayeredDirtyAppend(LayeredDirty):
    """ Like a group, except it has append and extend methods like a list.
    """

    def append(self, sprite):
        """
        Append an item to the sprite group.

        :param sprite: the sprite.
        """
        self.add(sprite)

    def extend(self, sprite_list):
        """
        Extend the sprite group with a list of items.

        :param sprite_list: the list.
        """
        for sprite in sprite_list:
            self.add(sprite)


class Lazer(DirtySprite):
    """
    lazer sprite class.
    """
    def __init__(self, container, shark_size):
        DirtySprite.__init__(self, container)
        self.rect = pygame.Rect([150, shark_size[1] - 155, shark_size[0], 10])
        # self.rect.x = -1000
        self.image = Surface((self.rect[2], self.rect[3])).convert()
        self.image.fill((255, 0, 0))


class Shark(DirtySprite): #pylint:disable=too-many-instance-attributes
    """
    Shark sprite class.
    """
    def __init__(self, container, scene, width, height):
        DirtySprite.__init__(self, container)
        self.container = container
        self.scene = scene
        self.width, self.height = width, height

        self.state = 0  #
        self.states = {
            0: 'offscreen',
            1: 'about_to_appear',
            2: 'poise',
            3: 'fire laser',
            4: 'leaving',
        }
        self.last_state = 0
        self.just_happened = None
        self.lazer = None  # type: Optional[Lazer]
        self.lazered = False  # was the cat hit?

        self.timings = {
            'time_between_appearances': 5000,
            'time_of_about_to_appear': 1000,
            'time_of_poise': 1000,
            'time_of_laser': 300,
            'time_of_leaving': 1000
        }

        self.last_animation = 0

        sfx('default_shark.ogg')
        sfx('shark_appear.ogg')
        sfx('shark_gone.ogg')
        sfx('shark_lazer.ogg')
        sfx('zirkus.ogg')
        sfx('cat_laser_2.ogg')
        sfx('cat_laser_3.ogg')

        self.image = gfx('shark.png', convert_alpha=True)
        # gfx('foot_part.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = -1000
        self.rect.y = (self.height - self.image.get_height())

    def update(self, *args, **kwargs):
        debug = True
        if self.just_happened == 'offscreen':
            if debug:
                print(self.just_happened)
            sfx('shark_gone.ogg', stop=1)
            sfx('zirkus.ogg', play=1)

            self.rect.x = -1000
            self.dirty = True

        elif self.just_happened == 'about_to_appear':
            if debug:
                print(self.just_happened)
            music(stop=True)
            sfx('shark_appear.ogg', play=1)
            sfx('zirkus.ogg', stop=1)

        elif self.just_happened == 'poise':
            if debug:
                print(self.just_happened)
            sfx('shark_appear.ogg', stop=1)
            sfx('shark_attacks.ogg', play=1)

            self.rect.x = -30
            self.dirty = True

        elif self.just_happened == 'fire laser':
            self.fire_laserbeam(debug)

        elif self.just_happened == 'leaving':
            if debug:
                print(self.just_happened)
            sfx('shark_attacks.ogg', stop=1)
            sfx('shark_gone.ogg', play=1)
            self.dirty = True
            if self.lazered:
                self.scene.reset_on_death()
                self.lazered = False
            self.lazer.kill()

    def fire_laserbeam(self, debug):
        """
        Fires the shark's head mounted laser cannon.

        :param debug:
        """
        if debug:
            print(self.just_happened)
        self.lazer = Lazer(self.container, (self.width, self.height))
        if self.scene.player_data.cat_location[1] > self.scene.cat_wire_height - 3:
            # sfx('shark_lazer.ogg', play=1)
            print('shark collide')

            sfx('cat_laser_2.ogg', play=1)
            # sfx('cat_laser_3.ogg', play=1)

            self.lazered = True
        else:
            self.lazered = False
            sfx('shark_lazer.ogg', play=1)

    def animate(self, total_time):
        """
        Animate method.

        :param total_time:
        """
        # print('update', self.states[self.state], self.states[self.last_state])
        state = self.states[self.state]
        start_state = self.state

        if state == 'offscreen':
            just_happened = self.state != self.last_state
            self.just_happened = state if just_happened else None
            if total_time > self.last_animation + self.timings['time_between_appearances']:
                self.state += 1
                self.last_animation = total_time

        elif state == 'about_to_appear':
            just_happened = self.state != self.last_state
            self.just_happened = state if just_happened else None
            if total_time > self.last_animation + self.timings['time_of_about_to_appear']:
                self.state += 1
                self.last_animation = total_time

        elif state == 'poise':
            just_happened = self.state != self.last_state
            self.just_happened = state if just_happened else None
            # smoothly update upwards
            self.rect.y = ((self.height -
                            self.image.get_height()) +
                           0.2 *
                           (self.last_animation + self.timings['time_of_poise'] - total_time))
            self.dirty = True

            if total_time > self.last_animation + self.timings['time_of_poise']:
                self.state += 1
                self.last_animation = total_time

        elif state == 'fire laser':
            just_happened = self.state != self.last_state
            self.just_happened = state if just_happened else None
            if total_time > self.last_animation + self.timings['time_of_laser']:
                self.state += 1
                self.last_animation = total_time

        elif state == 'leaving':
            just_happened = self.state != self.last_state
            self.just_happened = state if just_happened else None
            # smoothly update downwards
            self.rect.y = ((self.height -
                            self.image.get_height()) +
                           0.2 *
                           (total_time - self.last_animation))
            self.dirty = True

            if total_time > self.last_animation + self.timings['time_of_leaving']:
                self.state += 1
                if self.state == max(self.states.keys()) + 1:
                    self.state = 0
                self.last_animation = total_time

        self.last_state = start_state

    def collide(self, scene, width, height, cat_location):
        """
        Collide method. Currently broken.

        :param scene:
        :param width:
        :param height:
        :param cat_location:
        """
        # TODO: this doesn't work. It means the laser never fires.
        # if self.state == 2:
        #     if cat_location[1] > height - 130:
        #         print('shark collide')
        #         scene.reset_on_death()


class Cat(DirtySprite):
    """
    Cat sprite class.
    """
    def __init__(self, player_data):
        DirtySprite.__init__(self)
        self.player_data = player_data
        self.image = gfx('cat_unicycle.png', convert_alpha=True)
        self.rect = self.image.get_rect()
        sfx('cat_jump.ogg')
        sfx('cat_wheel.ogg')

        # sfx('cat_jump.ogg', play=1)
        # sfx('cat_wheel.ogg', play=1)

        self.image_direction = [
            pygame.transform.flip(self.image, True, False),
            self.image,
        ]

        self.last_location = [0, 0]
        self.last_direction = True  # right is true
        self.last_rotation = -1

    def update(self, *args, **kwargs):
        direction = self.player_data.cat_speed[0] > 0
        # location = self.cat_holder.cat_location
        location = self.player_data.cat_head_location
        rotation = self.player_data.cat_angle
        # if self.last_location != location:
        #     self.dirty = True
        #     self.rect.x = int(location[0])
        #     self.rect.y = int(location[1])
        if self.last_direction != direction:
            self.dirty = True
            self.image = self.image_direction[int(direction)]
            if random.random() < 0.1:
                sfx('cat_wheel.ogg', play=1)

        if self.last_rotation != rotation or self.last_location != location:
            self.image = pygame.transform.rotate(self.image_direction[int(direction)],
                                                 -self.player_data.cat_angle * 180 / math.pi)
            size = self.image.get_rect().size
            self.dirty = True
            self.rect.x = int(location[0]) - size[0] * 0.5
            self.rect.y = int(location[1]) - size[1] * 0.5

        self.last_location = location[:]
        self.last_direction = direction
        self.last_rotation = rotation

        # draw cat
        # pygame.draw.line(
        #     screen, [0, 0, 255], self.cat_location, self.cat_head_location, 20
        # )
        # pygame.draw.circle(screen, [0, 0, 255], self.cat_head_location, 50, 1)
        # pygame.draw.circle(screen, [0, 255, 0], self.cat_head_location, 100, 1)


class Score(DirtySprite):
    """
    Score class.
    """
    def __init__(self, score_holder):
        """
        score_holder has a 'score' attrib.
        """
        DirtySprite.__init__(self)
        self.score_holder = score_holder
        self.myfont = pygame.font.SysFont("monospace", 30, bold=True)
        self.image = self.myfont.render(str(self.score_holder.player_data.score), True, [0, 0, 0])
        self.rect = self.image.get_rect()
        self.rect.x = 460
        self.rect.y = 451

        self.last_score = self.score_holder.player_data.score

    def update(self, *args, **kwargs):
        if self.last_score != self.score_holder.player_data.score:
            self.dirty = True
            self.image = self.myfont.render(str(self.score_holder.player_data.score),
                                            True, [0, 0, 0])
            self.rect.x = 475 - self.image.get_size()[0] / 2
        self.last_score = self.score_holder.player_data.score


class DeadZone(DirtySprite):
    """
    Dead Zone class.
    """
    def __init__(self, points):
        """
        score_holder has a 'score' attrib.
        """
        DirtySprite.__init__(self)
        zone_color = [255, 0, 0]

        # draw dead zones
        surf = pygame.display.get_surface()
        rect = pygame.draw.polygon(
            surf,
            zone_color,
            points
        )
        self.image = surf.subsurface(rect.clip(surf.get_rect())).copy()
        self.rect = self.image.get_rect()
        self.rect.x = rect.x
        self.rect.y = rect.y


class PlayerData:
    """
    Data about the player that gets passed around a lot at the minute.
    """
    def __init__(self, width, height):
        self._score = 0

        self.angle_to_not_fish = 0.0

        self.cat_start_pos = [width / 2, height - 100]
        self.cat_location = self.cat_start_pos[:]
        self.cat_speed = [0, 0]
        self.cat_angle = 0
        self.cat_angular_vel = 0

        self.cat_head_location = [
            int(self.cat_location[0] + 100 * math.cos(self.cat_angle - math.pi / 2)),
            int(self.cat_location[1] + 100 * math.sin(self.cat_angle - math.pi / 2)),
        ]

    def increment_score(self):
        """
        Increase the score.
        """
        self._score += 1

    def reset(self):
        """
        Reset the player data.
        """
        self.cat_location = self.cat_start_pos[:]
        self.cat_speed = [0, 0]
        self.cat_angle = 0
        self.cat_angular_vel = 0
        self._score = 0

    @property
    def score(self):
        """
        Get the player's score.
        """
        return self._score


class CatUniScene(Scene):#pylint:disable=too-many-instance-attributes
    """
    Cat unicycle scene.
    """
    def __init__(self, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        (width, height) = (1920 // 2, 1080 // 2)
        self.width, self.height = width, height

        # Loading screen should always be a fallback active scene
        self.active = False
        self.first_render = True

        self.myfont = pygame.font.SysFont("monospace", 20)

        self.background = gfx('background.png').convert()
        # self.cat_unicycle = gfx('cat_unicycle.png').convert_alpha()
        # self.fish = gfx('fish.png').convert_alpha()
        # self.foot = gfx('foot.png').convert_alpha()
        # self.foot_part = gfx('foot_part.png').convert_alpha()
        # self.shark = gfx('shark.png').convert_alpha()

        sfx('cat_jump.ogg')
        sfx('eatfish.ogg')

        # cat variables
        self.cat_wire_height = height - 100

        self.cat_speed_max = 8
        self.cat_fall_speed_max = 16

        self.left_pressed = False
        self.right_pressed = False
        self.player_data = PlayerData(width, height)

        # timing
        self.dt_scaled = 0
        self.total_time = 0

        # elephant and shark classes
        self.elephant = Elephant(self)
        self.shark_active = False  # is the shark enabled yet
        self.elephant_active = False
        self.cat = Cat(self.player_data)
        self.score_text = Score(self)

        self.deadzones = []

        # self.deadzones = [
        #     DeadZone(
        #         [
        #             [0, height - 100],
        #             [0.1 * width, height - 100],
        #             [0.1 * width, height],
        #             [0, height],
        #         ],
        #     ),
        #     DeadZone(
        #         [
        #             [0.9 * width, height - 100],
        #             [width, height - 100],
        #             [width, height],
        #             [0.9 * width, height],
        #         ],
        #     ),
        # ]
        self.allsprites = None  # type: Optional[LayeredDirty]
        self.shark = None  # type: Optional[Shark]
        self.init_sprites()

        # lists of things to catch by [posx, posy, velx, vely]
        # self.fish = [[0, height / 2, 10, -5]]

        self.fish = LayeredDirtyAppend()
        self.fish.extend([Fish(self.allsprites, (0, height / 2), (10.0, -5.0))])

        self.not_fish = LayeredDirtyAppend()

        # difficulty varibles
        self.number_of_not_fish = 0

    def init_sprites(self):
        """temp, this will go in the init.
        """
        sprite_list = [
            self.elephant,
            self.cat,
            self.score_text
        ]
        sprite_list += self.deadzones
        self.allsprites = LayeredDirty(
            sprite_list,
            _time_threshold=1000 / 10.0
        )
        scene = self
        self.shark = Shark(self.allsprites, scene, self.width, self.height)
        self.allsprites.add(self.shark)
        self.allsprites.clear(self.screen, self.background)

    # what to do when you die, reset the level
    def reset_on_death(self):
        """
        Reset on death.
        """
        self.player_data.reset()
        self.total_time = 0

        self.elephant.last_animation = 0
        self.elephant.state = 0
        self.elephant.just_happened = None
        self.elephant.dirty = 1
        self.elephant_active = False

        self.shark.last_animation = 0
        self.shark.state = 0
        self.shark_active = False
        self.shark.just_happened = None
        self.shark.dirty = 1

        if self.shark.lazer is not None:
            self.shark.lazer.kill()

    # periodically increase the difficulty
    def increase_difficulty(self):
        """
        Increase the difficulty.
        """
        self.number_of_not_fish = 0
        if self.player_data.score > 3:
            self.number_of_not_fish = 1
        if self.player_data.score > 9:
            self.number_of_not_fish = 1
        if self.player_data.score > 15:
            self.number_of_not_fish = 2
        if self.player_data.score > 19:
            self.number_of_not_fish = 1
        if self.player_data.score > 25:
            self.number_of_not_fish = 2
        if self.player_data.score > 35:
            self.number_of_not_fish = 3
        if self.player_data.score >= 50:
            self.number_of_not_fish = int((self.player_data.score - 20) / 10)

        # TODO: to make it easier to test.
        # if self.player_data.score >= 15:
        #     self.shark_active = True
        if self.player_data.score >= 10:
            self.shark_active = True

        # TODO: to make it easier to test.
        if self.player_data.score >= 20:
            self.elephant_active = True

    def render_sprites(self):
        """
        Render the sprites.
        """
        rects = []
        rects.extend(self.allsprites.draw(self.screen))
        return rects

    def render(self):
        rects = []
        if self.first_render:
            self.first_render = False
            rects.append(self.screen.get_rect())
        rects.extend(self.render_sprites())
        return rects

        # # we draw the sprites, and then the lines over the top.
        # self.render_sprites()
        #
        # screen = self.screen
        # width, height = self.width, self.height
        #
        # if 0:
        #     background_colour = (0, 0, 0)
        #     screen.fill(background_colour)
        #     screen.blit(self.background, (0, 0))
        #
        # self.elephant.render(screen, width, height)
        # self.shark.render(screen, width, height)
        #
        # # draw cat
        # pygame.draw.line(
        #     screen, [0, 0, 255], self.player_data.cat_location, self.cat_head_location, 20
        # )
        # pygame.draw.circle(screen, [0, 0, 255], self.cat_head_location, 50, 1)
        # pygame.draw.circle(screen, [0, 255, 0], self.cat_head_location, 100, 1)
        #
        # # draw dead zones
        # pygame.draw.polygon(
        #     screen,
        #     [255, 0, 0],
        #     [
        #         [0, height - 100],
        #         [0.1 * width, height - 100],
        #         [0.1 * width, height],
        #         [0, height],
        #     ],
        # )
        # pygame.draw.polygon(
        #     screen,
        #     [255, 0, 0],
        #     [
        #         [0.9 * width, height - 100],
        #         [width, height - 100],
        #         [width, height],
        #         [0.9 * width, height],
        #     ],
        # )
        #
        # # draw fish and not fish
        # for fish in self.fish:
        #     pygame.draw.circle(screen, [0, 255, 0], [int(fish.pos[0]), int(fish.pos[1])], 10)
        # for fish in self.not_fish:
        #     pygame.draw.circle(screen, [255, 0, 0], [int(fish.pos[0]), int(fish.pos[1])], 10)
        #
        # # draw score
        # textsurface = self.myfont.render(str(self.player_data.score), True, [0, 0, 0])
        # screen.blit(textsurface, (200, 300))
        # return [screen.get_rect()]

    def tick(self, time_delta):
        self.increase_difficulty()

        self.total_time += time_delta  # keep track of the total number of ms passed during the game
        dt_scaled = time_delta / 17
        self.dt_scaled = dt_scaled
        width, height = self.width, self.height

        # cat physics
        self.player_data.cat_angular_vel *= 0.9 ** dt_scaled  # max(0.9/(max(0.1,dt_scaled)),0.999)

        # add gravity
        self.player_data.cat_speed[1] = min(self.player_data.cat_speed[1] + (1 * dt_scaled),
                                            self.cat_fall_speed_max)

        # accelerate the cat left or right
        if self.right_pressed:
            self.player_data.cat_speed[0] = min(
                self.player_data.cat_speed[0] + 0.3 * dt_scaled, self.cat_speed_max
            )
            self.player_data.cat_angle -= 0.003 * dt_scaled

        if self.left_pressed:
            self.player_data.cat_speed[0] = max(
                self.player_data.cat_speed[0] - 0.3 * dt_scaled, -self.cat_speed_max
            )
            self.player_data.cat_angle += 0.003 * dt_scaled

        # make the cat fall
        angle_sign = 1 if self.player_data.cat_angle > 0 else -1
        self.player_data.cat_angular_vel += 0.0002 * angle_sign * dt_scaled
        self.player_data.cat_angle += self.player_data.cat_angular_vel * dt_scaled
        if ((self.player_data.cat_angle > math.pi / 2 or
             self.player_data.cat_angle < -math.pi / 2) and
                self.player_data.cat_location[1] > height - 160):
            self.reset_on_death()

        # move cat
        self.player_data.cat_location[0] += self.player_data.cat_speed[0] * dt_scaled
        self.player_data.cat_location[1] += self.player_data.cat_speed[1] * dt_scaled
        if (self.player_data.cat_location[1] > self.cat_wire_height and
                self.player_data.cat_location[0] > 0.25 * width):
            self.player_data.cat_location[1] = self.cat_wire_height
            self.player_data.cat_speed[1] = 0
        if self.player_data.cat_location[1] > height:
            self.reset_on_death()
        if self.player_data.cat_location[0] > width:
            self.player_data.cat_location[0] = width
            if self.player_data.cat_angle > 0:
                self.player_data.cat_angle *= 0.7
        self.player_data.cat_head_location = [
            int(self.player_data.cat_location[0] +
                100 * math.cos(self.player_data.cat_angle - math.pi / 2)),
            int(self.player_data.cat_location[1] +
                100 * math.sin(self.player_data.cat_angle - math.pi / 2)),
        ]

        # check for out of bounds
        if (self.player_data.cat_location[0] > 0.98 * width and
                self.player_data.cat_location[1] > self.cat_wire_height - 30):
            # bump the cat back in
            self.player_data.cat_angular_vel -= 0.01 * dt_scaled
            self.player_data.cat_speed[0] = -5
            self.player_data.cat_speed[1] = -20
            # self.reset_on_death()

        # check for collision with the elephant stomp
        if self.elephant_active:
            self.elephant.animate(self.total_time)
            self.elephant.collide(width)
        if self.shark_active:
            self.shark.animate(self.total_time)
            self.shark.collide(self, width, height, self.player_data.cat_location)

        self.allsprites.update(time_delta=self.dt_scaled,
                               height=height,
                               player_data=self.player_data)

        self.spawn_flying_objects(height, width)

    def spawn_flying_objects(self, height, width):
        """
        Throws random objects at the cat.

        :param height:
        :param width:
        """
        # refresh lists
        while len(self.fish) < 1:
            # choose a side of the screen
            if random.choice([0, 1]) == 0:
                self.fish.append(
                    Fish(self.allsprites,
                         (0, height / 2),  # random.randint(0, height / 2),
                         (random.randint(3, 7),
                          -random.randint(5, 12)),
                         )
                )
            else:
                self.fish.append(
                    Fish(self.allsprites,
                         (width, height / 2),  # random.randint(0, height / 2),
                         (-random.randint(3, 7),
                          -random.randint(5, 12)),
                         )
                )
        while len(self.not_fish) < self.number_of_not_fish:
            # choose a side of the screen
            if random.choice([0, 1]) == 0:
                self.not_fish.append(
                    NotFish(self.allsprites,
                            (0, height / 2),  # random.randint(0, height / 2),
                            (random.randint(3, 7),
                             -random.randint(5, 12)),
                            )
                )
            else:
                self.not_fish.append(
                    NotFish(self.allsprites,
                            (width, height / 2),  # random.randint(0, height / 2),
                            (-random.randint(3, 7),
                             -random.randint(5, 12)),
                            )
                )

    def event(self, pg_event):
        if pg_event.type == pygame.KEYDOWN:
            if pg_event.key == pygame.K_RIGHT:
                self.right_pressed = True
                # cat_speed[0] = min(cat_speed[0] + 2, cat_speed_max)
                # cat_angle -= random.uniform(0.02*math.pi, 0.05*math.pi)
            elif pg_event.key == pygame.K_LEFT:
                self.left_pressed = True
                # cat_speed[0] = min(cat_speed[0] - 2, cat_speed_max)
                # cat_angle += random.uniform(0.02*math.pi, 0.05*math.pi)
            elif pg_event.key == pygame.K_a:
                self.player_data.cat_angular_vel -= random.uniform(0.01 * math.pi, 0.03 * math.pi)
            elif pg_event.key == pygame.K_d:
                self.player_data.cat_angular_vel += random.uniform(0.01 * math.pi, 0.03 * math.pi)
            elif pg_event.key == pygame.K_UP:
                if self.player_data.cat_location[1] > self.cat_wire_height - 1:
                    self.player_data.cat_speed[1] -= 25
                    sfx('cat_jump.ogg', play=1)

        elif pg_event.type == pygame.KEYUP:
            if pg_event.key == pygame.K_UP:
                if self.player_data.cat_speed[1] < 0:
                    self.player_data.cat_speed[1] = 0
            elif pg_event.key == pygame.K_RIGHT:
                self.right_pressed = False
            elif pg_event.key == pygame.K_LEFT:
                self.left_pressed = False
