import random
import math


class RealisticBSM:
    def __init__(self, coincidence_window, interference_visibility):
        """
        Initialize the realistic BSM class with effective experimental parameters.

        Args:
            coincidence_window (float): Maximum allowed time difference (in seconds)
                                        for two photons to be considered coincident.
            interference_visibility (float): A value between 0 and 1 representing the
                                             quality of the interference (1 = perfect).
        """
        self.coincidence_window = coincidence_window
        self.interference_visibility = interference_visibility

    def apply_basis_transformation(self, photon):
        """
        Convert the photon's polarization state from circular (L/R) to linear (H/V).

        Transformation:
            |L⟩ = 1/sqrt(2) * (|H⟩ + i|V⟩)
            |R⟩ = 1/sqrt(2) * (|H⟩ - i|V⟩)

        Args:
            photon (dict): Photon dictionary with key 'polarization' ("L" or "R").

        Returns:
            dict: The same photon dictionary updated with a new key 'linear_state'
                  that holds a dictionary with the amplitudes for 'H' and 'V'.
        """
        pol = photon.get('polarization', None)
        if pol is None:
            # No polarization information: leave unchanged.
            return photon

        if pol == "L":
            photon['linear_state'] = {'H': 1 / math.sqrt(2), 'V': 1j / math.sqrt(2)}
        elif pol == "R":
            photon['linear_state'] = {'H': 1 / math.sqrt(2), 'V': -1j / math.sqrt(2)}
        else:
            # If already in a linear form, assume it's provided as needed.
            photon['linear_state'] = pol
        return photon

    def is_coincident(self, photon1, photon2):
        """
        Check if two photons are temporally coincident.

        Args:
            photon1 (dict): Photon dictionary with 'arrival_time'.
            photon2 (dict): Photon dictionary with 'arrival_time'.

        Returns:
            tuple: (bool, float) where the Boolean is True if the absolute difference
                   between the two 'arrival_time' values is within the coincidence window,
                   and the float is the actual time difference.
        """
        t1 = photon1.get('arrival_time', None)
        t2 = photon2.get('arrival_time', None)
        if t1 is None or t2 is None:
            return (False, None)
        time_diff = abs(t1 - t2)
        return (time_diff <= self.coincidence_window, time_diff)

    def simulate_beam_splitter(self, photon1, photon2):
        """
        Simulate interference of two photons on a 50/50 beam splitter.

        In a realistic interference experiment, indistinguishable photons
        interfering on a beam splitter yield outcomes corresponding to only
        two (distinguishable) Bell states. Here we abstract the full unitary
        transformation and use the interference visibility to decide if the
        interference is successful.

        Args:
            photon1 (dict): Photon dictionary with a 'linear_state' key.
            photon2 (dict): Photon dictionary with a 'linear_state' key.

        Returns:
            str or None: Returns a Bell state label ("Ψ⁻" or "Ψ⁺") if the interference
                         is successful; otherwise returns None (indicating an inconclusive outcome).
        """
        # Use interference visibility to decide if interference is "ideal"
        if random.random() < self.interference_visibility:
            # If interference is successful, randomly assign one of the two distinguishable Bell states.
            return random.choice(["Ψ⁻", "Ψ⁺"])
        else:
            # Interference was imperfect; no valid Bell state can be determined.
            return None

    def measure(self, photon1, photon2):
        """
        Perform the complete Bell state measurement (BSM).

        Overall steps:
            1. Check that the two photons are temporally coincident (using is_coincident).
            2. If coincident, convert each photon's polarization from circular to linear (using apply_basis_transformation).
            3. Simulate the interference of the two photons on a 50/50 beam splitter (using simulate_beam_splitter).
            4. If interference is successful, assign one of the two distinguishable Bell states.
            5. Return the measurement event with success flag, Bell state, and time difference.

        Args:
            photon1 (dict): Photon dictionary with at least 'arrival_time' and 'polarization'.
            photon2 (dict): Photon dictionary with at least 'arrival_time' and 'polarization'.

        Returns:
            dict: A dictionary representing the BSM event. For example:
                {
                  'BSM_success': True/False,
                  'Bell_state': "Ψ⁻" or "Ψ⁺" (or "inconclusive"),
                  'time_difference': <float, seconds>
                }
        """
        result = {
            'BSM_success': False,
            'Bell_state': "inconclusive",
            'time_difference': None
        }

        # Step 1: Check temporal coincidence.
        coincident, time_diff = self.is_coincident(photon1, photon2)
        result['time_difference'] = time_diff
        if not coincident:
            return result  # Photons did not arrive within the coincidence window.

        # Step 2: Transform both photons from circular to linear basis.
        photon1 = self.apply_basis_transformation(photon1)
        photon2 = self.apply_basis_transformation(photon2)

        # Step 3: Simulate interference at a 50/50 beam splitter.
        bell_state = self.simulate_beam_splitter(photon1, photon2)
        if bell_state is None:
            return result  # Interference was not ideal enough; measurement inconclusive.

        # Step 4: With successful interference, record the outcome.
        result['BSM_success'] = True
        result['Bell_state'] = bell_state

        return result


# Example usage:
if __name__ == "__main__":
    # Define two example photons with circular polarization and arrival times (in seconds).
    photon1 = {
        'arrival_time': 1e-9,  # 1 ns
        'polarization': 'L',  # left-circular
        # other keys can be present as needed...
    }
    photon2 = {
        'arrival_time': 1.2e-9,  # 1.2 ns (difference of 0.2 ns)
        'polarization': 'R',  # right-circular
    }

    # Instantiate the BSM class with a coincidence window of 0.5 ns and interference visibility of 0.9.
    bsm = RealisticBSM(coincidence_window=0.5e-9, interference_visibility=0.9)

    # Perform the measurement.
    bsm_result = bsm.measure(photon1, photon2)
    print("BSM Result:", bsm_result)
