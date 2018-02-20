
class Position:
    def __init__(self):
        self.positions = (
            { "name": "floor", "enc_dist": 0.0, "pot_dist": 0.0 },
            { "name": "switch", "enc_dist": 0.0, "pot_dist": 100.0 },
            { "name": "scale-bot", "enc_dist": 40.0, "pot_dist": 0.0 },
            { "name": "scale-mid", "enc_dist": 40.0, "pot_dist": 50.0 },
            { "name": "scale-top", "enc_dist": 40.0, "pot_dist": 100.0 }
        )

        self.index = 0
        self.selected_position = self.positions[self.index]
        self.current_distance = 0
        self.target_distance = 0

        # Internal usage
        def _find_position(self, position_name: str) -> tuple:
            index = 0
            for position in self.positions:
                if position_name in position["name"]:
                    return (index, position)

                index += 1

        # Peek at the next position up. Performs bounds checking.
        # Does not mutate state.
        def next_position(self) -> dict:
            index = min(len(self.positions) - 1, self.index + 1)
            return self.positions[index]

        # Peek at the previous position down. Performs bounds checking.
        # Does not mutate state.
        def prev_position(self) -> dict:
            index = max(0, self.index - 1)
            return self.positions[index]

        # Move the carriage up. Mutates state.
        def up(self):
            self.selected_position = next_position()

        # Move the carriage down. Mutates state.
        def down(self):
            self.selected_position = prev_position()

        # Poll this function in the execute() method.
        def update_position(self, distance):
            self.current_distance = distance
            if distance < prev_position()["enc_dist"]:
                down()
            if distance > next_position()["enc_dist"]:
                up()

        # Go to position based on value.
        def go_to(pos: int):
            pass
            # Drive elevator with encoder value
            # Drive carriage with potentiometer value

        # Go to position based on string.
        def go_to_position(self, pos: str):
            (self.index, self.selected_position) = _find_position(pos)
            go_to(self.selected_position["enc_dist"])