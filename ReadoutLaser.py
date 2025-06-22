import random
import math
import time


class ReadingLaser:
    def __init__(self, wavelength, power, pulse_duration, noise_level):
        """
        Initialize the ReadingLaser with readout parameters.

        Args:
            wavelength (float): Readout fluorescence wavelength in nm (e.g., 795 nm).
            power (float): Effective power of the readout laser (arbitrary units).
            pulse_duration (float): Duration of the readout pulse (s).
            noise_level (float): Fractional noise level (e.g., 0.1 means ±10% fluctuations).
        """
        self.wavelength = wavelength
        self.power = power
        self.pulse_duration = pulse_duration
        self.noise_level = noise_level

    def select_readout_polarization(self, station):
        """
        Select the polarization of the 795 nm readout pulse using quantum randomness,
        with different sets for Alice and Bob.

        Args:
            station (str): "Alice" or "Bob".

        Returns:
            float: Chosen polarization angle in degrees.
                   For Alice: random choice from [-22.5, 22.5, -45, 0].
                   For Bob: random choice from [22.5, -22.5].
        """
        if station == "Alice":
            options = [-22.5, 22.5, -45, 0]
        elif station == "Bob":
            options = [22.5, -22.5]
        else:
            options = [-22.5, 22.5, -45, 0]
        return random.choice(options)

    def emit_readout_pulse(self, polarization):
        """
        Simulate emission of a 795 nm readout pulse with a given polarization.

        Args:
            polarization (float): Polarization angle in degrees.

        Returns:
            dict: A pulse event dictionary containing:
                  'wavelength', 'power', 'pulse_duration', 'polarization', and 'emission_time'.
        """
        effective_power = self.power * random.uniform(1 - self.noise_level, 1 + self.noise_level)
        pulse_event = {
            'wavelength': self.wavelength,
            'power': effective_power,
            'pulse_duration': self.pulse_duration,
            'polarization': polarization,
            'emission_time': time.time()
        }
        return pulse_event

    def perform_measurement(self, atom_superposition, readout_polarization):
        """
        Perform a projection measurement on the atom's superposition state.

        The atom_superposition is assumed to be a dictionary with two keys:
            'match': the amplitude for the state that corresponds to the readout polarization,
            'no_match': the amplitude for the orthogonal state.
        The probability to measure a "bright" outcome (i.e., the readout pulse matches the atom's state)
        is given by the squared modulus of the 'match' amplitude normalized by the total probability.

        Args:
            atom_superposition (dict): e.g. {'match': complex, 'no_match': complex}
            readout_polarization (float): The polarization angle (in degrees) of the readout pulse.
                (In a more advanced model, this angle would determine the measurement basis. Here we assume
                 that the atom_superposition is already expressed in that basis.)

        Returns:
            str: "bright" if the measurement projects onto the state corresponding to the readout pulse,
                 "dark" otherwise.
        """
        # Calculate probabilities from the amplitudes.
        a_match = atom_superposition.get('match', 0)
        a_no_match = atom_superposition.get('no_match', 0)
        p_match = abs(a_match) ** 2
        p_no_match = abs(a_no_match) ** 2
        total = p_match + p_no_match
        if total == 0:
            # If the superposition is not defined, assume equal chance.
            total = 1.0
            p_match = 0.5
            p_no_match = 0.5

        probability_bright = p_match / total
        # Perform a Monte Carlo selection.
        if random.random() < probability_bright:
            return "bright"
        else:
            return "dark"

    def create_fluorescence_photon(self, measurement_outcome, pulse_event):
        """
        Create a fluorescence photon that encodes the measurement outcome.

        Args:
            measurement_outcome (str): Either "bright" or "dark".
            pulse_event (dict): The readout pulse event from emit_readout_pulse().

        Returns:
            dict: A fluorescence photon dictionary containing:
                  'wavelength', 'frequency', 'polarization', 'emission_time',
                  'direction', 'originating_atom', 'emission_probability', 'quantum_state'.
        """
        wavelength_m = pulse_event['wavelength'] * 1e-9  # convert nm to m
        frequency = 3e8 / wavelength_m
        fluorescence_photon = {
            'wavelength': pulse_event['wavelength'],
            'frequency': frequency,
            'polarization': pulse_event['polarization'],
            'emission_time': pulse_event['emission_time'],
            'direction': [0, 0, 1],
            'originating_atom': measurement_outcome,  # now indicates "bright" or "dark"
            'emission_probability': 1.0,
            'quantum_state': measurement_outcome
        }
        return fluorescence_photon

    def readout(self, entanglement_confirmed, atom_superposition, station):
        """
        Coordinate the state readout process.

        Process:
          1. Verify that entanglement is confirmed.
          2. Use the appropriate QRNG based on station to select the readout pulse polarization.
          3. Prepare a 795 nm readout pulse with the chosen polarization.
          4. Perform a projection measurement on the atom's superposition to decide if the outcome is "bright"
             (i.e. the atom's state corresponds to the selected polarization) or "dark".
          5. Create a fluorescence photon that encodes this measurement outcome.
          6. (Optionally, the trap could be reset afterwards.)

        Args:
            entanglement_confirmed (bool): Whether entanglement is established.
            atom_superposition (dict): The atom's superposition state, e.g.:
                                        {'match': complex, 'no_match': complex}.
            station (str): "Alice" or "Bob" to select the proper polarization set.

        Returns:
            dict or None: The fluorescence photon dictionary representing the readout result,
                          or None if entanglement is not confirmed.
        """
        if not entanglement_confirmed:
            print("Entanglement not confirmed; readout aborted.")
            return None

        # Step 1: Select the readout polarization based on the station.
        selected_polarization = self.select_readout_polarization(station)
        # Step 2: Emit the readout pulse (795 nm) with the selected polarization.
        pulse_event = self.emit_readout_pulse(selected_polarization)
        # Step 3: Perform the measurement on the atom's superposition.
        measurement_outcome = self.perform_measurement(atom_superposition, selected_polarization)
        # Step 4: Generate the fluorescence photon that encodes the outcome.
        fluorescence_photon = self.create_fluorescence_photon(measurement_outcome, pulse_event)
        return fluorescence_photon


# Example usage:
if __name__ == "__main__":
    # Create a ReadingLaser instance with sample parameters:
    reading_laser = ReadingLaser(wavelength=795, power=5, pulse_duration=30e-9, noise_level=0.1)

    # Assume entanglement is confirmed:
    entanglement_confirmed = True

    # Instead of directly providing "bright" or "dark", we provide an atomic superposition.
    # For this example, let's say the atom is in a superposition where the probability amplitudes are:
    # 0.8 for the state that matches the readout polarization and 0.6 for the orthogonal state.
    # (These amplitudes can be complex numbers; here, for simplicity, we use real numbers.)
    atom_superposition = {
        'match': 0.8,
        'no_match': 0.6
    }

    # Specify the station: "Alice" or "Bob" (which determines the set of possible polarizations).
    station = "Alice"

    # Perform the readout.
    fluorescence_photon = reading_laser.readout(entanglement_confirmed, atom_superposition, station)

    if fluorescence_photon is not None:
        print("Fluorescence photon generated:")
        for key, value in fluorescence_photon.items():
            print(f"  {key}: {value}")
    else:
        print("No fluorescence photon generated.")
