from math import *


class Camera(object):
    def __init__(self, x=0, y=0, z=0, pitch=0, yaw=0, roll=0):
        self.x = x
        self.y = y
        self.z = z
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll

    def move(self, dx, dy, dz):
        pitch = self.pitch
        yaw = self.yaw
        if pitch > 90 or pitch < -90:
            pitch = -pitch
            dx = -dx
            dy = -dy
            dz = -dz
        self.z += dx * cos(radians(yaw - 90)) + dz * cos(radians(yaw))
        self.x -= dx * sin(radians(yaw - 90)) + dz * sin(radians(yaw))
        self.y += dy * sin(radians(pitch - 90)) + dz * sin(radians(pitch))

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

    def direction(self):
        m = cos(radians(self.pitch))

        dy = -sin(radians(self.pitch))
        dx = cos(radians(self.yaw - 90)) * m
        dz = sin(radians(self.yaw - 90)) * m
        return dx, dy, dz
