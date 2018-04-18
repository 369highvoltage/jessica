from typing import Dict, Callable, List
import asyncio

class Events(object):
    _events: Dict[str, List[Callable]]
    
    def __init__(self):
        self._events = {}
        self.loop = asyncio.get_event_loop()

    def _create_event(self, name: str):
        if not (name in self._events):
            self._events[name] = []

    def _create_events(self, names: List[str]):
        for name in names:
            self._create_event(name)

    def add_listener(self, event_name: str, callback: Callable):
        if not (event_name in self._events):
            raise ValueError("there is no event named" + str(event_name))
        self._events[event_name].append(callback)

    def add_listeners(self, event_name: str, callbacks: List[Callable]):
        if not (event_name in self._events):
            raise ValueError("there is no event named" + str(event_name))
        self._events[event_name].extend(callbacks)

    def remove_listener(self, event_name: str, callback: Callable):
        if not (event_name in self._events):
            raise ValueError("there is no event named" + str(event_name))
        try:
            self._events[event_name].remove(callback)
        except(ValueError):
            print("didn't find callback namedd '{}' in event named '{}'".format(callback.__name__, event_name))

    def trigger_event(self, event_name: str, data=None):
        if not (event_name in self._events):
            raise ValueError("there is no event named" + str(event_name))
        def do_calls():
            for callback in self._events[event_name]:
                if data is not None:
                    callback(data)
                else:
                    callback()
        self.loop.call_soon(do_calls)