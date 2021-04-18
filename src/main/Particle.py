import pygame
import numpy as np

from . import random_angle, uniform_probability
from . import cfg


class Particle:
    def __init__(self, x, y, status, radius=cfg.PARTICLE_RADIUS, color=cfg.PARTICLE_COLOR, clock_tick=60):
        self.x = x
        self.y = y
        self.status = status

        self.radius = radius
        self.color = color

        self.update_circumference_coordinates()

        self.displacement = cfg.PARTICLE_DISPLACEMENT
        self.angle = random_angle()

        self.vel = cfg.PARTICLE_VELOCITY # velocity

        self.f = 0 # frame
        self.clock_tick = clock_tick

        self.infected_particles = list()
        self.my_boundries = dict()
        self.infected_since = 0
        self.is_masked = False
        self.trans_probab = cfg.TRANSMISSION_PROBABILITY

    def update_circumference_coordinates(self):
        self.top = abs(self.y) - self.radius
        self.right = abs(self.x) + self.radius
        self.bottom = abs(self.y) + self.radius
        self.left = abs(self.x) - self.radius

    def update_coordinates(self):
        dx = np.sin(self.angle) * self.vel
        dy = np.cos(self.angle) * self.vel

        self.x += dx
        self.y -= dy

    def update_2d_vectors(self):
        self.f += 1
        if self.f > self.clock_tick * 2:
            self.f = 0
            self.angle = random_angle()

        self.update_coordinates()
        self.update_circumference_coordinates()

    def is_infected(self):
        return True if self.status == cfg.INFECTED_TYPE else False

    def update_infected_count(self, infected):
        if self.is_infected():
            self.infected_particles.append(infected)

    def _infect(self, infectee, time, probab):
        p = uniform_probability()
        if p <= probab:
            infectee.update_infected_count(self)

            self.status = cfg.INFECTED_TYPE
            self.infected_since = time
            return True

    def infect(self, infectee, time):
        clr = cfg.INFECTED_COLOR
        if not cfg.MASKS:
            t_p = cfg.TRANSMISSION_PROBABILITY
        else:
            if self.is_masked and infectee.is_masked:
                t_p = cfg.MASK_MASK
                clr = cfg.MASKED_INF_COLOR
            elif self.is_masked and not infectee.is_masked:
                t_p = cfg.MASK_NOMASK
            elif not self.is_masked and infectee.is_masked:
                t_p = cfg.NOMASK_MASK
                clr = cfg.MASKED_INF_COLOR
            else:
                t_p = cfg.TRANSMISSION_PROBABILITY

        if self._infect(infectee, time, t_p):
            self.color = clr
            return True

    def recover(self, day):
        if self.is_infected() and (day - self.infected_since) >= cfg.RECOVERED_PERIOD_IN_DAYS:
            self.status = cfg.RECOVERED_TYPE
            self.color = cfg.RECOVERED_COLOR
            return True

    def wear_mask(self):
        if cfg.MASKS:
            will_it_wear = uniform_probability()
            if will_it_wear <= cfg.RATIO_OF_POP_WITH_MASKS:
                self.is_masked = True
                self.color = cfg.MASKED_INF_COLOR if self.is_infected() else cfg.MASKED_SUS_COLOR
                return

