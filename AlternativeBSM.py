import random
import math
import time
from SPD import SPD
import matplotlib.pyplot as plt
import collections

# Simplified BSM class using the alternative approach.
class SimplifiedBSM:
    def __init__(self, coincidence_window, spd_instance, bell_state_weights=None):
        """
        Initialize the simplified BSM class.

        Args:
            coincidence_window (float): Maximum allowed time difference (in seconds)
                                        for two photons to be considered coincident.
            spd_instance (SinglePhotonDetector): An SPD instance to simulate detection.
            bell_state_weights (dict, optional): A dictionary for weighting the Bell state selection.
               Expected keys: 'Ψ⁻', 'Ψ⁺', 'Φ⁺', 'Φ⁻'. If not provided, assume equal weights.
        """
        self.coincidence_window = coincidence_window
        self.spd = spd_instance
        # If not specified, assign equal probability for all four states.
        if bell_state_weights is None:
            self.bell_state_weights = {
                "Ψ⁻": 0.25,
                "Ψ⁺": 0.25,
                "Φ⁺": 0.25,
                "Φ⁻": 0.25
            }
        else:
            self.bell_state_weights = bell_state_weights

    def is_coincident(self, photon1, photon2):
        """
        Check whether the two photons' arrival times are within the coincidence window.

        Args:
            photon1 (dict): Must contain 'arrival_time'.
            photon2 (dict): Must contain 'arrival_time'.

        Returns:
            tuple: (bool, float) where the Boolean is True if the time difference is within the window,
                   and the float is the actual time difference.
        """
        t1 = photon1.get('arrival_time')
        t2 = photon2.get('arrival_time')
        if t1 is None or t2 is None:
            return (False, None)
        time_diff = abs(t1 - t2)
        return (time_diff <= self.coincidence_window, time_diff)

    def choose_bell_state(self):
        """
        Randomly select one of the four Bell states based on equal probability.
        If the chosen state is one of the symmetric states (Φ⁺ or Φ⁻), mark the outcome as ambiguous.

        Returns:
            str: If the randomly chosen state is antisymmetric (Ψ⁻ or Ψ⁺), return that state.
                 If it is symmetric (Φ⁺ or Φ⁻), return "Ambiguous_Symmetric".
        """
        # For simplicity, we select with equal probability
        states = ["Ψ⁻", "Ψ⁺", "Φ⁺", "Φ⁻"]
        chosen = random.choice(states)
        if chosen in ["Φ⁺", "Φ⁻"]:
            return "Ambiguous_Symmetric"
        else:
            return chosen

    def mix_photons(self, photon1, photon2, chosen_state):
        """
        Mix the two input photons into one effective photon.
        For this simplified model, we assume that the effective photon
        represents the joint state as projected onto the chosen Bell state.
        The effective photon's arrival time is taken as the average of the two.

        Args:
            photon1 (dict): First photon.
            photon2 (dict): Second photon.
            chosen_state (str): The Bell state outcome from choose_bell_state.

        Returns:
            dict: An effective photon dictionary that includes all original keys plus
                  a new key 'effective_Bell_state' with the value of chosen_state.
        """
        effective_photon = {}
        # Copy common properties (for example, wavelength, frequency, etc.) from photon1.
        for key in ['wavelength', 'frequency', 'originating_atom', 'emission_probability']:
            effective_photon[key] = photon1.get(key, None)
        # The polarization may now be considered to encode the Bell state information.
        effective_photon['effective_Bell_state'] = chosen_state
        # Set the arrival time as the average of the two.
        t1 = photon1.get('arrival_time', 0)
        t2 = photon2.get('arrival_time', 0)
        effective_photon['arrival_time'] = (t1 + t2) / 2.0
        return effective_photon

    def simulate_detection(self, effective_photon):
        """
        Use the SPD instance to simulate detection of the effective photon.

        Args:
            effective_photon (dict): The effective photon from mix_photons.

        Returns:
            dict: The detection event from the SPD.
        """
        spd_instance.reset()
        arrival_time = effective_photon.get('arrival_time', time.time())
        return self.spd.detect(effective_photon, arrival_time)

    def measure(self, photon1, photon2):
        """
        Perform the complete BSM measurement in the simplified model.

        Process:
          1. Check if the two photons are coincident (using is_coincident).
          2. If not coincident, return an inconclusive measurement.
          3. Otherwise, randomly choose one of the four Bell states (using choose_bell_state).
          4. Mix the two photons into one effective photon that carries the chosen Bell state (using mix_photons).
          5. Simulate detection of the effective photon using the SPD (using simulate_detection).
          6. Return a measurement event dictionary with:
              - 'BSM_success': True if the effective photon was detected.
              - 'Bell_state': The chosen Bell state (or "Ambiguous_Symmetric" if a symmetric state was chosen).
              - 'time_difference': The difference in arrival times between the two input photons.

        Args:
            photon1 (dict): First photon (with 'arrival_time' and 'polarization').
            photon2 (dict): Second photon (with 'arrival_time' and 'polarization').

        Returns:
            dict: A measurement event dictionary.
        """
        result = {
            'BSM_success': False,
            'Bell_state': "Inconclusive",
            'time_difference': None
        }

        # Step 1: Check temporal coincidence.
        coincident, time_diff = self.is_coincident(photon1, photon2)
        result['time_difference'] = time_diff
        if not coincident:
            return result

        # Step 2: Choose a Bell state at random.
        chosen_state = self.choose_bell_state()

        # Step 3: Mix the two photons into one effective photon.
        effective_photon = self.mix_photons(photon1, photon2, chosen_state)

        # Step 4: Simulate detection using the SPD.
        detection_event = self.simulate_detection(effective_photon)
        if detection_event.get('detected'):
            result['BSM_success'] = True
            result['Bell_state'] = chosen_state
        else:
            result['Bell_state'] = "Inconclusive"
        return result


# Example usage:
if __name__ == "__main__":
    # Create two example photons with arrival times (in seconds) and circular polarization.
    photon1 = {
        'arrival_time': 1e-9,  # 1 ns
        'polarization': 'L',
        'wavelength': 780,  # nm
        'frequency': 3e8 / (780e-9),
        'originating_atom': {'F': 1, 'm_F': 0},
        'emission_probability': 1.0,
        'quantum_state': 'L'
    }
    photon2 = {
        'arrival_time': 1.2e-9,  # 1.2 ns (difference 0.2 ns, within coincidence window)
        'polarization': 'R',
        'wavelength': 780,
        'frequency': 3e8 / (780e-9),
        'originating_atom': {'F': 1, 'm_F': 0},
        'emission_probability': 1.0,
        'quantum_state': 'R'
    }

    # Instantiate an SPD with 90% detection efficiency, 100 counts/s dark count rate,
    # 50 ps timing jitter, and 1 µs dead time.
    spd_instance = SPD(
        detection_efficiency=0.6,
        dark_count_rate=100,
        timing_jitter=50e-12,
        dead_time=1e-6
    )

    # Instantiate the simplified BSM class with a coincidence window of 0.5 ns.
    bsm = SimplifiedBSM(coincidence_window=0.5e-9, spd_instance=spd_instance)

    # Perform the measurement.
    outcomes = []
    for  i in range(1000):
        bsm_result = bsm.measure(photon1, photon2)
        print("Simplified BSM Result:", bsm_result)
        result = bsm.measure(photon1, photon2)
        outcomes.append(result['Bell_state'])




# Assume 'outcomes' is a list containing the Bell state result from each trial.
# For example, outcomes = ['Ψ⁻', 'Inconclusive', 'Ψ⁺', ...]
counter = collections.Counter(outcomes)
states = list(counter.keys())
counts = [counter[state] for state in states]

plt.figure(figsize=(8, 6))
bars = plt.bar(states, counts, color='skyblue')
plt.xlabel("Bell State Outcome")
plt.ylabel("Number of Occurrences")
plt.title("Bell State Measurement Outcomes over 1000 Trials")

# Annotate each bar with the count value.
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height, f'{int(height)}',
             ha='center', va='bottom')

plt.show()



