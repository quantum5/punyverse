from math import sin, cos, tan, atan, sqrt, radians, degrees


class KeplerOrbit(object):
    def __init__(self, sma, eccentricity, inclination=0, longitude=0, argument=0):
        self.sma = sma
        self.eccentricity = eccentricity
        self.inclination = inclination
        self.longitude = longitude
        self.argument = argument
        self.__true_anomaly_factor = sqrt((1 + eccentricity)/(1 - eccentricity))
        self.__distance_factor = sma * (1 - eccentricity ** 2)

    @property
    def inclination(self):
        return degrees(self._inclination)

    @inclination.setter
    def inclination(self, value):
        self.inclination_radian = radians(value)

    @property
    def inclination_radian(self):
        return self._inclination

    @inclination_radian.setter
    def inclination_radian(self, value):
        self._inclination = value
        self.__sin_inclination = sin(self._inclination)
        self.__cos_inclination = cos(self._inclination)

    @property
    def longitude(self):
        return degrees(self._longitude)

    @longitude.setter
    def longitude(self, value):
        self.longitude_radian = radians(value)

    @property
    def longitude_radian(self):
        return self._longitude

    @longitude_radian.setter
    def longitude_radian(self, value):
        self._longitude = value
        self.__sin_longitude = sin(self._longitude)
        self.__cos_longitude = cos(self._longitude)

    @property
    def argument(self):
        return degrees(self._argument)

    @argument.setter
    def argument(self, value):
        self.argument_radian = radians(value)

    @property
    def argument_radian(self):
        return self._argument

    @argument_radian.setter
    def argument_radian(self, value):
        self._argument = value
        self.__sin_argument = sin(self._argument)
        self.__cos_argument = cos(self._argument)

    def eccentric_anomaly(self, mean_anomaly):
        e1 = 0
        e2 = mean_anomaly
        while abs(e1 - e2) > 0.000001:
            e1, e2 = e2, e2 - ((e2 - mean_anomaly - self.eccentricity * sin(e2)) /
                               (1 - self.eccentricity * cos(e2)))
        return e2

    def true_anomaly(self, mean_anomaly):
        eccentric_anomaly = self.eccentric_anomaly(mean_anomaly)
        return 2 * atan(self.__true_anomaly_factor * tan(eccentric_anomaly / 2))

    def orbit(self, mean_anomaly):
        mean_anomaly = radians(mean_anomaly)
        phi = self.true_anomaly(mean_anomaly)
        r = self.__distance_factor / (1 + self.eccentricity * cos(phi))
        x = r * cos(phi)
        y = r * sin(phi)
        z = 0

        # phi = longitude, theta = inclination, psi = argument
        x, y = (x * self.__cos_longitude + y * self.__sin_longitude,
               -x * self.__sin_longitude + y * self.__cos_longitude)
        x, z = (x * self.__cos_inclination + z * self.__sin_inclination,
               -x * self.__sin_inclination + z * self.__cos_inclination)
        x, y = (x * self.__cos_argument + y * self.__sin_argument,
               -x * self.__sin_argument + y * self.__cos_argument)

        return x, y, z
