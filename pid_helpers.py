from typing import Callable

class PIDOutput(object):
    def __init__(self, method: Callable[[float]]):
        self.method = method
    
    def pidWrite(self, output: float):
        self.method(output)

class PIDSource(object):
    def __init__(self, method: Callable[[float]]):
        self.method = method
    
    def pidGet(self) -> float:
        self.method()