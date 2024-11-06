import pygame,random
from pygame.locals import *
import numpy as np
import math


def normalize_vector_l2(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


class PositionStorer():

    def __init__(self):
        self.particles = []
        self.attractors = []

    def add_particle(self, mouse_x, mouse_y, radius, color, id):
        self.particles.append(Particle(mouse_x, mouse_y, radius, color, self, id))

    def add_attractor(self, mouse_x, mouse_y, radius, mass, color, id):
        self.attractors.append(Attractor(mouse_x, mouse_y, radius, mass, color, self, id))

    def tick(self):
        for p in self.particles:
            p.tick()
        for a in self.attractors:
            a.tick()


class Particle:

    def __init__(self, startx, starty, radius, color, position_storer, id):
        self.position_storer = position_storer

        self.id = id

        self.x = startx
        self.y = starty
        self.radius = radius

        self.color = color

        self.vel_vec = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])

        # self.acl_vec = np.array([0, 0])

    def tick(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

        self.x = self.x + self.vel_vec[0]
        self.y = self.y + self.vel_vec[1]

        new_acl_vec = np.array([0, 0])
        for attractor in self.position_storer.attractors:
            displacement = np.array([attractor.x - self.x, attractor.y - self.y])
            distance_sq = max(displacement[0] ** 2 + displacement[1] ** 2, attractor.radius ** 2)  # make sure the distance is at least radius
            new_acl_vec = np.add(new_acl_vec, (attractor.mass / distance_sq) * normalize_vector_l2(displacement))

        self.vel_vec = np.add(self.vel_vec, new_acl_vec)

        # self.check_collision()

    def check_collision(self):
        # wall collision y vector switch bc pygame down is positive
        if self.y > ymax - 10:
            self.vel_vec = self.wall_calculate_new_velocity(np.array([0, -1]))
        elif self.y < 10:
            self.vel_vec = self.wall_calculate_new_velocity(np.array([0, 1]))
        elif self.x > xmax - 10:
            self.vel_vec = self.wall_calculate_new_velocity(np.array([-1, 0]))
        elif self.x < 10:
            self.vel_vec = self.wall_calculate_new_velocity(np.array([1, 0]))
        else:
            # particle particle collision
            for p in self.position_storer.particles:
                if p.id != self.id:
                    if self.radius ** 2 > (self.x - p.x) ** 2 + (self.y - p.y) ** 2:
                        push = np.array([self.x - p.x, self.y - p.y])

                        self.x = self.x + 0.5 * push[0]
                        self.y = self.y + 0.5 * push[1]

                        self_vel_vec_holder = self.vel_vec
                        self.vel_vec = p.vel_vec
                        p.vel_vec = self_vel_vec_holder

            for a in self.position_storer.attractors:
                if a.id != self.id:
                    if self.radius ** 2 > (self.x - a.x) ** 2 + (self.y - a.y) ** 2:
                        push = np.array([self.x - a.x, self.y - a.y])

                        self.x = self.x + 0.5 * push[0]
                        self.y = self.y + 0.5 * push[1]

                        self_vel_vec_holder = self.vel_vec
                        self.vel_vec = a.vel_vec
                        a.vel_vec = self_vel_vec_holder

    def wall_calculate_new_velocity(self, surface_normal):
        new_vel_vec = np.subtract(self.vel_vec, surface_normal * (2 * np.dot(self.vel_vec, surface_normal)))
        return new_vel_vec


class Attractor(Particle):

    def __init__(self, startx, starty, radius, mass, color, position_storer, id):
        Particle.__init__(self, startx, starty, radius, color, position_storer, id)
        self.position_storer = position_storer

        self.id = id

        self.x = startx
        self.y = starty
        self.radius = radius
        self.mass = mass

        self.color = color

        self.vel_vec = np.array([0, 0])

        self.acl_vec = np.array([0, 0])

    def tick(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        self.x = self.x + self.vel_vec[0]
        self.y = self.y + self.vel_vec[1]

        new_acl_vec = np.array([0, 0])
        for attractor in self.position_storer.attractors:
            displacement = np.array([attractor.x - self.x, attractor.y - self.y])
            distance_sq = max(displacement[0] ** 2 + displacement[1] ** 2,
                              attractor.radius ** 2)  # make sure the distance is at least radius
            new_acl_vec = np.add(new_acl_vec, (attractor.mass / distance_sq) * normalize_vector_l2(displacement))

        self.vel_vec = np.add(self.vel_vec, new_acl_vec)

        # self.check_collision()


pygame.init()
xmax = 1000
ymax = 1000
screen = pygame.display.set_mode((xmax,ymax))

black = (0,0,0)

white = (255, 255, 255)
blue = (50,50,160)
red = (160, 50, 50)
yellow = (160, 160, 50)
color_var = white

clock = pygame.time.Clock()

pygame.display.set_caption("Particle Sim")

particles = []
id = 0
exit_flag = False
my_position_storer = PositionStorer()

while not exit_flag:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            color = [red, white, blue][random.randint(0, 2)]
            my_position_storer.add_particle(mouse_x, mouse_y, 2, color, id)
            id += 1
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                color = yellow
                my_position_storer.add_attractor(mouse_x, mouse_y, 6, 50, color, id)
                id += 1
            if event.key == pygame.K_c:
                my_position_storer.particles = []
                my_position_storer.attractors = []
                id = 0
        elif event.type == QUIT:
            exit_flag = True

    screen.fill(black)
    my_position_storer.tick()
    pygame.display.flip()
    clock.tick(50)

pygame.quit()
