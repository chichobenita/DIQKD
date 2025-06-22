import random
import math


class OpticFiber:
    def __init__(self, fiber_length, attenuation_dB_per_km, dispersion_ps_per_nm_km=0, group_velocity=2e8):
        """
        Initialize the optical fiber component.

        Parameters:
            fiber_length (float): Length of the fiber in meters.
            attenuation_dB_per_km (float): Attenuation in dB/km.
            dispersion_ps_per_nm_km (float): Dispersion in ps/(nm·km). Default is 0 (i.e., no dispersion).
            group_velocity (float): Speed of light in the fiber (m/s). Default ~2e8 m/s.
        """
        self.fiber_length = fiber_length  # in meters
        self.attenuation_dB_per_km = attenuation_dB_per_km
        # Convert attenuation to dB per meter.
        self.attenuation_dB_per_m = attenuation_dB_per_km / 1000.0
        # Convert dispersion to ps/(nm·m) (if provided)
        self.dispersion = dispersion_ps_per_nm_km / 1000.0
        self.group_velocity = group_velocity  # m/s

    def propagate(self, photon, current_time):
        """
        Simulate the propagation of a photon through the optical fiber.

        The photon dictionary follows this structure:
            {
                'wavelength': wavelength,        # nm
                'frequency': frequency,          # Hz
                'polarization': photon_polarization,  # e.g., 'sigma+' or 'sigma-'
                'emission_time': <timestamp>,    # time when photon was created (s)
                'direction': [0, 0, 1],          # e.g., along z-axis
                'originating_atom': final_state, # metadata from the atom
                'emission_probability': 1.0,     # typically 1.0 for an emitted photon
                'quantum_state': photon_polarization  # simplified representation
            }

        Optionally, if the photon already includes 'pulse_width' (in seconds) and
        'spectral_width' (in nm), the propagation will update the 'pulse_width' to
        account for dispersion.

        Process:
          1. Compute the propagation delay = fiber_length / group_velocity.
          2. Update the photon's arrival time by adding the delay (stored in a new key,
             e.g., 'arrival_time').
          3. Compute the transmission efficiency:
             T = 10^(- (attenuation_dB_per_m * fiber_length) / 10)
          4. Use a Monte Carlo decision to determine if the photon is transmitted:
             If random.random() < T, the photon is transmitted; otherwise, it is lost.
          5. Add a new key 'transmitted' to the photon dictionary.
          6. If the photon is transmitted and contains 'pulse_width' and 'spectral_width',
             update 'pulse_width' using:
             new_pulse_width = sqrt(old_pulse_width^2 + (dispersion * fiber_length * spectral_width * 1e-12)^2)
             (Converting dispersion from ps/(nm·m) to seconds.)

        Returns:
            dict: The updated photon dictionary.
        """
        # Calculate the propagation delay (seconds)
        delay = self.fiber_length / self.group_velocity
        new_arrival_time = current_time + delay

        # Calculate total loss in dB over the fiber length.
        total_loss_dB = self.attenuation_dB_per_m * self.fiber_length
        transmission_efficiency = 10 ** (-total_loss_dB / 10.0)

        # Decide if the photon is transmitted (i.e., not lost).
        if random.random() < transmission_efficiency:
            photon['arrival_time'] = new_arrival_time  # Add a new key for arrival time.
            photon['transmitted'] = True

            # Optionally update pulse width if the photon contains these keys.
            if 'pulse_width' in photon and 'spectral_width' in photon:
                old_pulse_width = photon['pulse_width']  # in seconds
                spectral_width = photon['spectral_width']  # in nm
                # dispersion: self.dispersion in ps/(nm·m); convert to seconds by multiplying by 1e-12.
                dispersion_broadening = self.dispersion * self.fiber_length * spectral_width * 1e-12
                new_pulse_width = math.sqrt(old_pulse_width ** 2 + dispersion_broadening ** 2)
                photon['pulse_width'] = new_pulse_width

            return photon
        else:
            # Photon is lost during propagation.
            photon['transmitted'] = False
            return photon


# Example usage:
if __name__ == "__main__":
    # Define the photon using the attached form.
    photon = {
        'wavelength': 780,  # nm
        'frequency': 3e8 / (740e-9),  # Hz, computed from c/λ
        'polarization': 'sigma+',
        'emission_time': 0,  # starting time (for simulation, set to 0)
        'direction': [0, 0, 1],
        'originating_atom': {'F': 1, 'm_F': +1},
        'emission_probability': 1.0,
        'quantum_state': 'sigma+'
    }

    # Optionally, if dispersion is to be simulated, add pulse_width and spectral_width.
    # For example, a pulse width of 50 ps and spectral width of 1 nm.
    photon['pulse_width'] = 50e-12  # 50 ps in seconds.
    photon['spectral_width'] = 1.0  # 1 nm

    # Create an OpticFiber instance for a fiber of 50 meters,
    # using typical attenuation for 780 nm (e.g., 4 dB/km) and dispersion (e.g., 17 ps/(nm·km)).
    fiber = OpticFiber(
        fiber_length=700,  # meters
        attenuation_dB_per_km=4,  # dB/km
        dispersion_ps_per_nm_km=17  # ps/(nm·km)
    )

    # Assume the photon enters the fiber at simulation time 0.
    current_time = 0
    updated_photon = fiber.propagate(photon, current_time)

    if updated_photon.get('transmitted', False):
        print("Photon was transmitted through the fiber.")
        print("Updated photon properties:")
        for key, value in updated_photon.items():
            print(f"  {key}: {value}")
    else:
        print("Photon was lost during fiber propagation.")


#   link that support our Attenuation "https://www.edmundoptics.com/p/single-mode-optical-fiber-780-970nm-20m/55155/?srsltid=AfmBOoo7Z5Hw3Yz3ZjkD2FwCbWhBPQtaGmy4M1E9Sh3lt7GBssw9XFuk"
#   also in this paper ("https://www.nature.com/articles/s41586-022-04891-y#Sec7") mention under "Discussion and outlook":
#   "Another direction is to improve the reach of the QNL. Here, a limiting factor is attenuation loss of
#   the 780nm photons in long optical fibres, which is already 50% for a 700m long link."
#   Dispersion delay calculate by this equation , Dispersion delay = Dispersion coefficient*Spectral width of the light source


