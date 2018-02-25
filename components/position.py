class Position:
    # RPM Multipliers
    ELEVATOR_MULTIPLIER = 1635.15/6317.67
    CARRIAGE_MULTIPLIER = 1.0 - ELEVATOR_MULTIPLIER
    
    # Max heights of each stage.
    ELEVATOR_MAX_HEIGHT = 40
    CARRIAGE_MAX_HEIGHT = 37

    # Conversion factors (counts to inches)
    # CHANGE THESE VALUES
    ELEVATOR_CONV_FACTOR = 0.00134
    CARRIAGE_CONV_FACTOR = 0.000977
    
    def __init__(self):
        # Heights of various objects in inches.
        self.positions = (
            { "name": "floor", "distance": 2.0 },
            { "name": "portal", "distance": 34.0 },
            { "name": "scale_low", "distance": 48.0 },
            { "name": "scale_mid", "distance": 60.0 },
            { "name": "scale_high", "distance": 72.0 }
        )
        
        self.index = 0

        # Tuples
        self.target_position = self.positions[0]

    @property
    def target_distance(self):
        return self.target_position["distance"]

    @property
    def _current_distance(self) -> float:
        counts = self.current_distance()
        carriage_count = counts["elevator"]
        elevator_count = counts["carriage"]
        # Distance (in inches)
        return carriage_count * Position.CARRIAGE_CONV_FACTOR + elevator_count * Position.ELEVATOR_CONV_FACTOR

    def current_distance(self) -> dict:
        raise NotImplementedError

    # Private functions.
    """
        Check and update 
    """
    def _check_position(self):
        if self.current_distance < self.prev_position()["distance"]:
            self.target_position = self.prev_position()
        if self.current_distance > self.next_position()["distance"]:
            self.target_position = self.next_position()
    

    """
        Looks up named position and returns the position & it's index.
    """
    def _find_position(self, position_name: str) -> tuple:
        index = 0
        for position in self.positions:
            if position_name in position["name"]:
                return index, position

            index += 1
    
    """
        Get the next position. Checks upper bound.
    """
    def _get_next_position(self) -> tuple:
        index = min(len(self.positions) - 1, self.index + 1)
        return index, self.positions[index]
    
    """
        Get the previous position. Checks lower bound.
    """
    def _get_prev_position(self) -> tuple:
        index = max(0, self.index - 1)
        return index, self.positions[index]
    
    # Public functions
    """
        Peek at the next position up. Does not mutate state.
    """
    def next_position(self) -> dict:
        (_, position) = self._get_next_position()
        return position

    """
        Peek at the previous position down. Does not mutate state.
    """
    def prev_position(self) -> dict:
        (_, position) = self._get_prev_position()
        return position

    """
        Find and return position based on string.
    """
    def set_position(self, position_name: str) -> dict:
        (self.index, self.target_position) = self._find_position(position_name)
        return self.target_position

    """
        Move the carriage up. Mutates state.
    """
    def up(self) -> dict:
        (self.index, self.target_position) = self._get_next_position()
        return self.target_position

    """
        Move the carriage down. Mutates state.
    """
    def down(self) -> dict:
        (self.index, self.target_position) = self._get_prev_position()
        return self.target_position
    
    """
        Poll this function to determine when to stop the routine (Based on raw distances).
    """
    def is_at_target_distance(self) -> bool:
        return self.target_distance - 0.1 < self._current_distance < self.target_distance + 0.1
    #
    # """
    #     Poll this function to determine when to stop the routine (Based on named positions).
    # """
    # def is_at_target_position(self) -> bool:
    #     return self.target_distance - 0.1 < self.current_distance < self.target_distance + 0.1
    
    # """
    #     Poll this function in the execute() method & pass in the raw encoder values.
    # """
    # def update_distances(self, carriage_count: int, elevator_count: int):
    #     self.current_distance = carriage_count * Position.POTENTIOMETER_CONV_FACTOR + elevator_count * Position.ENCODER_CONV_FACTOR
    #     self._check_position()
    
    """
        Calculate distances for carriage & elevator based on value.
    """
    def get_target_distances(self) -> dict:
        # Carriage cannot go farther than 30 inches. Restrict carriage travel.
        carriage = min(self.target_distance * Position.CARRIAGE_MULTIPLIER, Position.CARRIAGE_MAX_HEIGHT)
        # Elevator moves the remainder of distance.
        elevator = self.target_distance - carriage

        return { # Return distances in counts.
            "carriage": carriage/Position.CARRIAGE_CONV_FACTOR,
            # "carriage": 0,
            "elevator": elevator/Position.ELEVATOR_CONV_FACTOR
        }