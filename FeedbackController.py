
class FeedbackController():
    def __init__(self, setpoint, events, queues, continuous=False, control_mode="", input_range=(5.0, 5.0), gains=(), output_range=(1.0, 1.0), tolerance=5.0):
        self._continuous = False
        self._enabled, self._target = events
        self._inbound, self._outbound, self._setpoints = queues
        
        # Configuration functions.
        self._set_absolute_tolerance(tolerance)
        self._set_input_range(input_range)
        self._set_output_range(output_range)
        self._set_PID(gains)
        
        # Configuration variables.
        self._continuous = continuous
        self._control_mode = control_mode

        # Setpoint values.
        self._setpoint = setpoint
        self._prev_setpoint = 0.0

        self._error = 0.0
        self._prev_error = 0.0
        self._total_error = 0.0
    
    def execute(self):
        while self._enabled.is_set():
            self._calculate()

    def _is_at_target(self, value: float) -> bool:
        return abs(self._error) < value
    
    def _is_at_target_percentage(self, percentage: float) -> bool:
        return abs(self._error) < percentage/100.0 * self._input_range
    
    def _calculate(self):
        """Calculates the feedback value.
        
        Only runs when a value has been received from the queue.
        """
        if not self._inbound.empty():
            input = self._inbound.get_nowait()

            if self._continuous:
                self._error = self._get_continuous_error(self._setpoint - input)
            else:
                self._error = self._setpoint - input
            
            if self._control_mode == "Velocity":
                self._outbound.put_nowait(self._velocity_calculation())
            else:
                self._outbound.put_nowait(self._position_calculation())
            
            self._prev_error = self._error
            self._on_target()
        
        else:
            self._outbound.put_nowait(self._prev_error)

    def _clamp(self, value, low, high):
        return max(low, min(value, high))
    
    def _feedforward_calculation(self) -> float:
        if self._control_mode == "Velocity":
            return self._kF * self._setpoint
        else:
            t = self._kF * (self._setpoint - self._prev_setpoint)/self._period
            self._prev_setpoint = self._setpoint
            return t
    
    def _get_continuous_error(self, error: float):
        if self._continuous and self._input_range > 0:
            error %= self._input_range

            if abs(error) > self._input_range/2:
                if error > 0:
                    return error - self._input_range
                else:
                    return error + self._input_range

    def _position_calculation(self) -> float:
        if self._kI != 0:
            self._total_error = self._clamp(
                self._total_error + self._error,
                self._minimum_output/self._kI,
                self._maximum_output/self._kI
            )
        
        return self._kP * self._error + self._kI * self._total_error + self._kD * (self._error - self._prev_error) + self._feedforward_calculation()
    
    def _set_absolute_tolerance(self, abs_value):
        self._on_target = lambda: self._is_at_target(abs_value)
    
    def _set_input_range(self, range: tuple) -> None:
        self._minimum_input = range[0]
        self._maximum_input = range[1]
        self._input_range = range[1] - range[0]
    
    def _set_output_range(self, range: tuple) -> None:
        self._minimum_output = range[0]
        self._maximum_output = range[1]

    def _set_percentage_tolerance(self, percentage):
        self._on_target = lambda: self._is_at_target_percentage(percentage)

    def _set_PID(self, gains):
        if gains:
            self._kP = gains[0]
            self._kI = gains[1]
            self._kD = gains[2]
            self._kF = gains[3]
        else:
            self._kP = 0.0
            self._kI = 0.0
            self._kD = 0.0
            self._kF = 0.0

    def _velocity_calculation(self) -> float:
        if self._kP != 0:
            self._total_error = self._clamp(
                self._total_error + self._error,
                self._minimum_output/self._kP,
                self._maximum_output/self._kP
            )

        return self._clamp(
            self._kP * self._total_error + self._kD * self._error + self._feedforward_calculation,
            self._minimum_output,
            self._maximum_output
        )

    def _update_setpoint(self) -> None:
        if not self._setpoints.empty():
            self._setpoint = self._setpoints.get_nowait()



