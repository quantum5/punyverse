from math import sin, cos, tan, atan, sqrt, radians


class KeplerOrbit(object):
    def __init__(self, sma, eccentricity, inclination=0):
        self.sma = sma
        self.eccentricity = eccentricity
        self.inclination = radians(inclination)
        self.__true_anomaly_factor = sqrt((1 + eccentricity)/(1 - eccentricity))
        self.__distance_factor = sma * (1 - eccentricity ** 2)
        self.__sin_inclination = sin(self.inclination)
        self.__cos_inclination = cos(self.inclination)

    def eccentric_anomaly(self, mean_anomaly):
        e1 = mean_anomaly
        e2 = mean_anomaly + self.eccentricity * sin(e1)
        while abs(e1 - e2) > 0.000001:
            e1, e2 = e2, mean_anomaly + self.eccentricity * sin(e2)
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

        x, z = (x * self.__cos_inclination - z * self.__sin_inclination,
                x * self.__sin_inclination + z * self.__cos_inclination)

        return x, y, z
