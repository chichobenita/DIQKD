import random
import math

class Rb87Atom:
    def __init__(self, excited_state_lifetime=26e-9):
        """
        Initialize an Rb87 atom.

        The atom is initially prepared in the 5S₁/₂, F=1, m_F=0 state.
        excited_state_lifetime: Lifetime of the excited state (seconds).
        """
        self.ground_state = {'F': 1, 'm_F': 0}
        self.state = self.ground_state.copy()
        self.excited_state = None
        self.excited_state_lifetime = excited_state_lifetime

    def excite(self, excitation_event):
        """
        Simulate the excitation of the atom using the provided excitation event.

        excitation_event: dict with keys:
            - 'power': effective laser power after noise and alignment adjustments.
            - 'pulse_duration': duration of the laser pulse.
            - 'detuning': effective detuning.
            - 'polarization': laser polarization.

        The excitation probability is modeled via a Rabi-like formula:
            P_excite = sin^2((Omega * pulse_duration)/2) * exp(-|detuning|/delta_scale)
        where Omega is proportional to the effective power.
        """
        # Constants (these are scaling factors; in a full simulation, they would be derived from physical parameters)
        k = 1e7  # Scaling factor to convert power to Rabi frequency
        delta_scale = 0.1  # Determines how strongly detuning affects the probability

        power = excitation_event.get('power', 0)
        pulse_duration = excitation_event.get('pulse_duration', 0)
        detuning = excitation_event.get('detuning', 0)
        polarization = excitation_event.get('polarization', 'pi')

        # Calculate effective Rabi frequency and pulse area.
        Omega = k * power
        Theta = Omega * pulse_duration

        # Detuning factor (the greater the detuning, the lower the excitation probability)
        detuning_factor = math.exp(-abs(detuning) / delta_scale)

        # Calculate the excitation probability.
        P_excite = (math.sin(Theta / 2)) ** 2 * detuning_factor

        if random.random() < P_excite:
            # Excitation is successful. The atom is excited to the 5P₃/₂, F'=0 state.
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

        The atom decays from the excited state to the ground state. Due to selection rules,
        it will not return to m_F = 0 but instead ends up in a superposition (modeled here probabilistically)
        of m_F = +1 and m_F = -1. The branching ratios are influenced by the polarization of the excitation.

        Returns a dict with the final atomic state and the correlated photon polarization.
        """
        if self.excited_state is None:
            return {'status': 'failure', 'reason': 'atom not excited'}

        polarization = self.excited_state.get('laser_polarization', 'pi')
        # Adjust branching ratios based on the excitation polarization.
        if polarization == 'sigma+':
            ratio_plus = 0.8
            ratio_minus = 0.2
        elif polarization == 'sigma-':
            ratio_plus = 0.2
            ratio_minus = 0.8
        else:  # For pi or other polarizations, assume equal probability.
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
        # Reset excited state and update the current state.
        self.excited_state = None
        self.state = final_state
        return {'status': 'decayed', 'final_state': final_state, 'photon_polarization': photon_polarization}

    def reset(self):
        """
        Reset the atom to its initial state.
        """
        self.state = self.ground_state.copy()
        self.excited_state = None
        return {'status': 'reset', 'state': self.state}


# Example usage:
if __name__ == "__main__":
    # Initialize the laser and atom.
    laser = ExcitingLaser(
        power=1.2,
        frequency=780,  # 780 nm resonance for Rb87
        pulse_duration=20e-9,  # e.g., 20 ns pulse
        pulse_shape='gaussian',
        noise_level=0.1,
        detuning=0,  # On resonance
        alignment_efficiency=0.95,
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
