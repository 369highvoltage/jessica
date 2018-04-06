import queue
import threading
import time

class FeedbackController(threading.Thread):
    def __init__(self, event, gains, input_func, output_func, continuous=False, num_samples=8, period=0.05):
        self._continuous = continuous
        self._interrupted = event
        self._running = threading.Event()
        self._target = threading.Event()
        self._mutex = threading.RLock()

        self._input = input_func
        self._output = output_func
        
        # Configuration functions.
        self.set_input_range()
        self.set_output_range()
        self.set_PID(gains)

        self._setpoint = 0.0

        self._error = 0.0
        self._total_error = 0.0
        self._prev_sample = 0.0

        self._period = period
        self._num_samples = num_samples
        self._average_buffer = [0.0]

        threading.Thread.__init__(self)

    def on_target(self) -> bool:
        return self._target.is_set()

    def set_absolute_tolerance(self, abs_value) -> None:
        if self._running.is_set():
            self._attribute_error()

        self._is_on_target = lambda: self._is_at_target(abs_value)

    def set_input_range(self, range=(0.0, 0.0)) -> None:
        if self._running.is_set():
            self._attribute_error()
        
        self._minimum_input = range[0]
        self._maximum_input = range[1]
        self._input_range = range[1] - range[0]

    def set_output_range(self, range=(-1.0, 1.0)) -> None:
        if self._running.is_set():
            self._attribute_error()
        
        self._minimum_output = range[0]
        self._maximum_output = range[1]
    
    def set_percentage_tolerance(self, percentage) -> None:
        if self._running.is_set():
            self._attribute_error()
        
        self._is_on_target = lambda: self._is_at_target_percentage(percentage)
    
    def set_PID(self, gains) -> None:
        if self._running.is_set():
            self._attribute_error()
        
        self._kP = gains[0]
        self._kI = gains[1]*self._period
        self._kD = gains[2]/self._period
        
        if len(gains < 4):
            self._kF = 0.0
        else:
            self._kF = gains[3]
    
    def set_setpoint(self, setpoint) -> None:
        if self._running.is_set():
            self._attribute_error()
        
        self._setpoint = setpoint
    
    def start_controller(self):
        self._running.set()

    def stop_controller(self):
        self._running.clear()
    
    def _attribute_error(self):
        raise AttributeError("Cannot set parameter while thread is running.")

    # Private Methods
    def _calculate(self) -> None:
        """Calculates the feedback value.
        
        Only runs when a value has been received from the queue.
        """
        with self._mutex:
            sample = self._input()
        
        if self._continuous:
            self._error = self._get_continuous_error(self._setpoint - sample)
        else:
            self._error = self._setpoint - sample
        self._total_error += self._error

        result = self._clamp(
            self._kP * self._error + self._kI * self._total_error - self._kD * (sample - self._prev_sample),
            self._minimum_output,
            self._maximum_output
        )

        with self._mutex:
            self._output(result)
        
        self._prev_sample = sample

        if not len(self._average_buffer) < self._num_samples:
            del self._average_buffer[0]
        
        self._average_buffer.append(sample)

    def _clamp(self, value, low, high):
        return max(low, min(value, high))
    
    def _get_continuous_error(self, error) -> float:
        error %= self._input_range
        if abs(error) > self._input_range/2:
            if error > 0:
                return error - self._input_range
            else:
                return error + self._input_range 

    def run(self) -> None:
        self._running.wait()
        while self._running.is_set() or not self._interrupted.is_set():
            self._calculate()
            self._is_on_target()
            time.sleep(self._period)

    def _is_at_target(self, value: float) -> None:
        if not len(self._average_buffer) < self._num_samples:
            if abs(sum(self._average_buffer)/self._num_samples) < value:
                self._target.set()
    
    def _is_at_target_percentage(self, percentage: float) -> None:
        if not len(self._average_buffer) < self._num_samples:
            if abs(sum(self._average_buffer)/self._num_samples) < percentage/100.0 * self._input_range:
                self._target.set()