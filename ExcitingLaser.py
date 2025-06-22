import random
import math
import time
import numpy as np

class ExcitingLaser:
    def __init__(self, power, frequency, pulse_duration, pulse_shape='gaussian',
                 noise_level=0, detuning=0, alignment_efficiency=1.0, polarization='sigma+'):
        """
        Initialize the ExcitingLaser.

        Parameters:
            power (float): Nominal laser power.
            frequency (float): Nominal laser frequency (or central wavelength in nm; here 780 nm for Rb87).
            pulse_duration (float): Duration of the laser pulse (seconds).
            pulse_shape (str): Shape of the pulse (e.g., 'gaussian', 'rectangular').
            noise_level (float): Noise level for fluctuations in power and detuning.
            detuning (float): Detuning from the resonance (in the same units as frequency, e.g., nm offset).
            alignment_efficiency (float): Factor (0-1) representing how well the beam is aligned with the atom.
            polarization (str): Nominal polarization ('sigma+', 'sigma-', or 'pi').
        """
        self.power = power
        self.frequency = frequency
        self.pulse_duration = pulse_duration
        self.pulse_shape = pulse_shape
        self.noise_level = noise_level
        self.detuning = detuning
        self.alignment_efficiency = alignment_efficiency
        self.polarization = polarization
        self.pulse_count = 0

    def simulate_noise(self, value):
        """
        Apply Gaussian noise to a given value.
        """
        return value + random.gauss(0, self.noise_level)

    def emit(self):
        """
        Simulate firing a laser pulse.

        This method returns an excitation event dictionary that includes:
            - effective power (including noise and alignment)
            - pulse duration
            - effective detuning (with additional noise)
            - polarization (possibly affected by noise)
            - pulse count
        """
        self.pulse_count += 1

        # Effective power is reduced by any misalignment and fluctuates with noise.
        effective_power = self.simulate_noise(self.power) * self.alignment_efficiency

        # Detuning is also subject to slight fluctuations.
        effective_detuning = self.detuning
        "+ random.gauss(0, self.noise_level * 0.1)"

        # Simulate polarization noise: with a small chance, flip the polarization.
        polarization = self.polarization
        if random.random() < 0.05 * self.noise_level:  # 5% chance weighted by noise level
            if polarization == 'sigma+':
                polarization = 'sigma-'
            elif polarization == 'sigma-':
                polarization = 'sigma+'
            # 'pi' polarization remains unchanged.

        event = {
            'status': 'ready',
            'power': effective_power,
            'frequency': self.frequency,
            'pulse_duration': self.pulse_duration,
            'pulse_shape': self.pulse_shape,
            'detuning': effective_detuning,
            'polarization': polarization,
            'pulse_count': self.pulse_count
        }
        return event

    def set_parameters(self, **kwargs):
        """
        Dynamically adjust the laser's parameters.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Rb87Atom:
    def __init__(self, excited_state_lifetime=26e-9):
        """
        Initialize an Rb87 atom.
        The atom is initially prepared in the 5S1/2, F=1, m_F=0 state.
        """
        self.ground_state = {'F': 1, 'm_F': 0}
        self.state = self.ground_state.copy()
        self.excited_state = None
        self.excited_state_lifetime = excited_state_lifetime

    def calculate_rabi_frequency(self, power_watts):
        """
        Calculate the Rabi frequency Omega (rad/s) given laser power (W) and beam waist (m).

        Parameters:
        - power_watts: Laser power in watts (must be > 0)
        - beam_waist_meters: Radius of the laser beam in meters (must be > 0)

        Returns:
        - Rabi frequency Omega in radians per second, or NaN if inputs are invalid
        """
        # Constants
        hbar = 1.055e-34  # J·s
        mu = 3e-29  # C·m
        epsilon_0 = 8.85e-12  # F/m
        c = 3e8  # m/s

        if power_watts <= 0:
            print("Error: Power and beam waist must be positive values.")
            return np.nan

        # Beam area
        A = np.pi * 10e-6 ** 2
        I = power_watts / A
        argument = 2 * I / (epsilon_0 * c)

        if argument < 0:
            print("Invalid square root: negative intensity expression.")
            return np.nan

        E0 = np.sqrt(argument)
        Omega = (mu * E0) / hbar

        return Omega

    def excite(self, excitation_event):
        """
        Attempt to excite the atom using the excitation event from the laser.
        The excitation probability is given by:

        P_excite = sin^2((Omega * pulse_duration)/2) * exp(-|detuning|/delta_scale)

        where Omega = k * power.
        """
        # Parameters for the simulation.
        k = 1e7  # Scaling constant (units: rad/s per unit power)
        delta_scale = 0.1  # Determines sensitivity to detuning

        power = excitation_event.get('power', 0)
        pulse_duration = excitation_event.get('pulse_duration', 0)
        detuning = excitation_event.get('detuning', 0)

        polarization = excitation_event.get('polarization', 'pi')
        Omega = self.calculate_rabi_frequency(power)  # [rad/s]
        # Calculate Rabi frequency and pulse area.
        Theta = Omega * pulse_duration  # dimensionless pulse area

        # Effect of detuning.
        detuning_factor = math.exp(-abs(detuning) / delta_scale)

        # Excitation probability.
        P_excite = ((math.sin(Theta / 2)) ** 2) * detuning_factor

        # Use Monte Carlo method to decide if excitation occurs.
        if random.random() < P_excite:
            self.excited_state = {
                'state': "5P3/2",
                'F_prime': 0,
                'm_F': 0,
                'laser_polarization': polarization
            }
            self.state = self.excited_state.copy()
            return {'status': 'excited', 'excited_state': self.excited_state, 'P_excite': P_excite}
        else:
            return {'status': 'no_excitation', 'P_excite': P_excite}

    def decay(self):
        """
        Simulate spontaneous emission (decay) of the atom from the excited state.
        The atom decays from the excited state to the ground state.
        Due to selection rules, it will not return to m_F = 0 but instead to a state
        corresponding to m_F = +1 or m_F = -1. In this process, a photon is emitted.
        We generate a photon object (dictionary) that includes:
          - wavelength (nm)
          - frequency (Hz)
          - polarization (e.g., 'sigma+' or 'sigma-')
          - emission_time (timestamp)
          - direction (an example vector)
          - originating_atom (metadata from the atom's final state)
          - emission_probability (set to 1 when a photon is emitted)
          - quantum_state (a basic representation; here we use polarization)
        """
        if self.excited_state is None:
            return {'status': 'failure', 'reason': 'atom not excited'}

        # Determine decay outcome using branching ratios influenced by polarization.
        polarization = self.excited_state.get('laser_polarization', 'pi')
        if polarization == 'sigma+':
            ratio_plus = 0.8
            ratio_minus = 0.2
        elif polarization == 'sigma-':
            ratio_plus = 0.2
            ratio_minus = 0.8
        else:
            ratio_plus = 0.5
            ratio_minus = 0.5

        rand = random.random()
        if rand < ratio_plus:
            final_mF = +1
            photon_polarization = 'sigma+'
        else:
            final_mF = -1
            photon_polarization = 'sigma-'

        final_state = {'F': 1, 'm_F': final_mF}
        self.excited_state = None
        self.state = final_state

        # Create the photon object with the desired properties.
        # For Rb87 D2 line, the wavelength is ~780 nm.
        # Frequency can be approximated as c/λ; using c ≈ 3e8 m/s.
        wavelength = 780  # in nm
        frequency = 3e8 / (780e-9)  # in Hz, roughly 3.84e14 Hz

        photon = {
            'wavelength': wavelength,  # nm
            'frequency': frequency,  # Hz
            'polarization': photon_polarization,  # 'sigma+' or 'sigma-'
            'emission_time': time.time(),  # timestamp in seconds
            'direction': [0, 0, 1],  # Example: along z-axis
            'originating_atom': final_state,  # Metadata from the atom
            'emission_probability': 1.0,  # Since photon is emitted
            'quantum_state': photon_polarization  # Simplified representation
        }

        return {'status': 'decayed', 'final_state': final_state, 'photon': photon}

    def reset(self):
        """Reset the atom to its initial ground state."""
        self.state = self.ground_state.copy()
        self.excited_state = None
        return {'status': 'reset', 'state': self.state}








"""


# Example usage:
if __name__ == "__main__":
    # Initialize the laser and atom.
    laser = ExcitingLaser(
        power=117e-6,
        frequency=780,  # 780 nm resonance for Rb87
        pulse_duration=1.1e-6,
        pulse_shape='gaussian',
        noise_level=0,
        detuning=0.05,  # On resonance
        alignment_efficiency=1,
        polarization='sigma+'
    )


    atom = Rb87Atom()





# Laser emits a pulse.
    excitation_event = laser.emit()
    print("Laser Emission Event:", excitation_event)

    # Atom attempts to get excited.
    result_excite = atom.excite(excitation_event)
    print("Atom Excitation Result:", result_excite)



    # If excited, the atom decays.
    if result_excite['status'] == 'excited':
        result_decay = atom.decay()
        print("Atom Decay Result:", result_decay)

    # Reset the atom for a new cycle.
    result_reset = atom.reset()
    print("Atom Reset Result:", result_reset)





num_trials = 1000  # Number of laser pulses/trials
successes = 0

for i in range(num_trials):
    excitation_event = laser.emit()
    result = atom.excite(excitation_event)
    if result['status'] == 'excited':
        successes += 1
    atom.reset()  # Reset the atom after each trial

print("Out of {} trials, there were {} successful excitations.".format(num_trials, successes))

"""

#"https://www.science.org/doi/pdf/10.1126/science.1143835 we can see in this paper the relevant values for successful excitations."
# the name of the paper Single-Atom Single-Photon Quantum Interface