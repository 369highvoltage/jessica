from typing import Callable
from wpilib.interfaces.pidsource import PIDSource as WPI_PIDSource

class Gains(object):
    def __init__(self, p: float = 0.0, i: float = 0.0, d: float = 0.0, f: float = 0.0, intergral_zone: int = 0, peak_out: float = 0.0):
        self.p = p
        self.i = i
        self.d = d
        self.f = f
        self.intergral_zone = intergral_zone
        self.peak_out = peak_out

class PIDOutput(object):
    def __init__(self, method: Callable[[float], None]):
        self.method = method
    
    def pidWrite(self, output: float):
        self.method(output)

class PIDSource(WPI_PIDSource):
    def __init__(self, method: Callable[[], float], source_type: WPI_PIDSource.PIDSourceType = WPI_PIDSource.PIDSourceType.kDisplacement):
        self.method = method
        self.source_type = source_type

    def setPIDSourceType(self, source_type: WPI_PIDSource.PIDSourceType):
        self.source_type = source_type

    def getPIDSourceType(self) -> WPI_PIDSource.PIDSourceType:
        return self.source_type

    def pidGet(self) -> float:
        return self.method()