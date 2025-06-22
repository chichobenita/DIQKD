import random
import math


class SPD:
    def __init__(self, detection_efficiency, dark_count_rate, timing_jitter, dead_time=0):
        """
        Initialize the Single Photon Detector (SPD).

        Parameters:
            detection_efficiency (float): Probability (0 to 1) that an incident photon is detected.
            dark_count_rate (float): Rate of dark counts (false positives) in counts per second.
            timing_jitter (float): Standard deviation (in seconds) for the timing uncertainty.
            dead_time (float, optional): Time after a detection during which the SPD is inactive (in seconds). Default is 0.
        """
        self.detection_efficiency = detection_efficiency
        self.dark_count_rate = dark_count_rate
        self.timing_jitter = timing_jitter
        self.dead_time = dead_time
        self.last_detection_time = -math.inf  # no detections have occurred yet

    def is_available(self, current_time):
        """
        Check if the detector is available (i.e., not in dead time).

        Parameters:
            current_time (float): The current simulation time in seconds.

        Returns:
            bool: True if the detector is available; False otherwise.
        """
        return (current_time - self.last_detection_time) >= self.dead_time

    def detect(self, photon, arrival_time):
        """
        Simulate the detection of an incident photon.

        Parameters:
            photon (dict): A dictionary representing the photon (with properties like wavelength, polarization, etc.).
            arrival_time (float): The time (in seconds) at which the photon arrives at the detector.

        Returns:
            dict: A detection event dictionary with keys:
                  - 'detected': Boolean indicating if an event was registered.
                  - 'detection_time': The time (arrival_time plus jitter) when the event is recorded (if detected).
                  - 'event_type': 'photon' for an actual photon detection, or 'dark_count' if a false count occurred.
                  - 'photon': The original photon dictionary if a photon was detected; None otherwise.
        """
        event = {
            'detected': False,
            'detection_time': None,
            'event_type': None,
            'photon': None
        }

        # Check if the detector is ready (not in dead time)
        if not self.is_available(arrival_time):
            return event  # Detector busy; no detection

        # Decide if the photon is detected based on detection efficiency.
        if random.random() < self.detection_efficiency: #לברר התפלגות
            # Photon detected: add timing jitter.
            jitter = random.gauss(0, self.timing_jitter)
            detection_time = arrival_time + jitter
            event['detected'] = True
            event['detection_time'] = detection_time
            event['event_type'] = 'photon'
            event['photon'] = photon
            self.last_detection_time = detection_time  # Start dead time
            return event

        # If photon not detected, simulate a dark count over a small time window.
        # Here we assume a small window dt (e.g., 1 ns).
        dt = 1e-9  # 1 nanosecond
        if random.random() < self.dark_count_rate * dt:
            jitter = random.gauss(0, self.timing_jitter)
            detection_time = arrival_time + jitter
            event['detected'] = True
            event['detection_time'] = detection_time
            event['event_type'] = 'dark_count'
            event['photon'] = None
            self.last_detection_time = detection_time
            return event

        return event

    def simulate_dark_count(self, current_time):
        """
        Independently simulate a dark count event based on the dark count rate.

        Parameters:
            current_time (float): The current simulation time in seconds.

        Returns:
            dict: A dark count detection event dictionary.
        """
        dt = 1e-9  # 1 ns time window (example)
        if random.random() < self.dark_count_rate * dt:
            jitter = random.gauss(0, self.timing_jitter)
            detection_time = current_time + jitter
            self.last_detection_time = detection_time
            return {
                'detected': True,
                'detection_time': detection_time,
                'event_type': 'dark_count',
                'photon': None
            }
        else:
            return {
                'detected': False,
                'detection_time': None,
                'event_type': None,
                'photon': None
            }

    def reset(self):
        """
        Reset the detector's state, clearing the dead time.
        """
        self.last_detection_time = -math.inf


#   "https://www.spiedigitallibrary.org/conference-proceedings-of-spie/12891/128910M/High-detection-efficiency-silicon-avalanche-photodiode-for-LiDAR/10.1117/12.3003305.full?utm_source=chatgpt.com"
#   this paper show in Fig.8 Detection Efficiency vs Wavelength, in 780nm we get detection efficiency of 50%.


