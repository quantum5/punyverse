from __future__ import division

from math import sin, cos, radians, hypot, tan

from punyverse.glgeom import Matrix4f
from punyverse.utils import cached_property


class Camera(object):
    def __init__(self, x=0, y=0, z=0, pitch=0, yaw=0, roll=0):
        self.x = x
        self.y = y
        self.z = z
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll

        self.fov = radians(45)
        self.aspect = 1
        self.znear = 1
        self.zfar = 3000000

        self.speed = 0
        self.roll_left = False
        self.roll_right = False

    def move(self, speed):
        dx, dy, dz = self.direction()
        self.x += dx * speed
        self.y += dy * speed
        self.z += dz * speed

        self.view_matrix = None

    def mouse_move(self, dx, dy):
        if self.pitch > 90 or self.pitch < -90:
            dx = -dx
        if self.yaw + dx >= 360:
            self.yaw = self.yaw + dx - 360
        elif self.yaw + dx < 0:
            self.yaw = 360 - self.yaw + dx
        else:
            self.yaw += dx

        self.pitch -= dy
        if self.pitch < -180:
            self.pitch += 360
        elif self.pitch > 180:
            self.pitch -= 360

        self.view_matrix = None

    def direction(self):
        m = cos(radians(self.pitch))

        dy = -sin(radians(self.pitch))
        dx = cos(radians(self.yaw - 90)) * m
        dz = sin(radians(self.yaw - 90)) * m
        return dx, dy, dz

    def update(self, dt, move):
        if self.roll_left:
            self.roll -= 4 * dt * 10
            self.view_matrix = None
        if self.roll_right:
            self.roll += 4 * dt * 10
            self.view_matrix = None
        if move:
            self.move(self.speed * 10 * dt)

    def reset_roll(self):
        self.roll = 0
        self.view_matrix = None

    def distance(self, x, y, z):
        return hypot(hypot(x - self.x, y - self.y), z - self.z)

    @cached_property
    def view_matrix(self):
        return Matrix4f.from_angles((self.x, self.y, self.z), (self.pitch, self.yaw, self.roll), view=True)

    def projection_matrix(self):
        scale_y = 1 / tan(self.fov / 2)
        scale_x = scale_y / self.aspect
        frustrum = self.znear - self.zfar
        return Matrix4f([scale_x, 0, 0, 0,
                         0, scale_y, 0, 0,
                         0, 0, (self.znear + self.zfar) / frustrum, -1,
                         0, 0, (2 * self.znear * self.zfar) / frustrum, 0])
