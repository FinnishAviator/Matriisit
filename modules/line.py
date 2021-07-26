# Copyright © NALStudio
# Line class used in NALStudio's Koch's Snoflake and Voronoi Calculator

from typing import Tuple
import math

class Line:
    __slots__ = ("_p1", "_p2", "_dx", "_dy")

    def __init__(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> None:
        self._p1: Tuple[float, float] = point1
        self._p2: Tuple[float, float] = point2
        self._calcDir()

    def Lerp(self, t: float) -> Tuple[float, float]:
        # x = Lerp(self._p1[0], self._p2[0], t)
        # y = Lerp(self._p1[1], self._p2[1], t)
        # return (x, y)

        # Faster
        return (self._p1[0] + self._dx * t, self._p1[1] + self._dy * t)

    def _calcDir(self):
        self._dx = self._p2[0] - self._p1[0]
        self._dy = self._p2[1] - self._p1[1]

    def _calcP2(self):
        self.Point2 = (self._p1[0] + self._dx, self._p1[1] + self._dy)

    @property
    def Distance(self) -> float:
        return math.sqrt(self._dx * self._dx + self._dy * self._dy)

    @Distance.setter
    def Distance(self, value: float):
        divider = self.Distance
        self._dx = (self._dx / divider) * value
        self._dy = (self._dy / divider) * value
        self._calcP2()

    @property
    def Angle(self) -> float:
        return math.degrees(math.atan2(self._dy, self._dx))

    @Angle.setter
    def Angle(self, angle: float):
        theta = math.radians(angle)
        oldDist = self.Distance
        self._dx = math.cos(theta) * oldDist
        self._dy = math.sin(theta) * oldDist
        self._calcP2()

    @property
    def Point1(self) -> Tuple[float, float]:
        return self._p1

    @Point1.setter
    def Point1(self, value: Tuple[float, float]):
        self._p1 = value
        self._calcDir()

    @property
    def Point2(self) -> Tuple[float, float]:
        return self._p2

    @Point2.setter
    def Point2(self, value: Tuple[float, float]):
        self._p2 = value
        self._calcDir()