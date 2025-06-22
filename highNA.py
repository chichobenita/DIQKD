import math
import random


class HighNAComponent:
    def __init__(self, numerical_aperture, refractive_index, additional_efficiency):
        """
        Initialize the High-NA optics component.

        Parameters:
            numerical_aperture (float): The numerical aperture (NA) of the optics.
            refractive_index (float): The refractive index of the medium (default is 1 for air).
            additional_efficiency (float): A multiplicative factor to account for additional losses
                                           (e.g., imperfect coupling, reflections). Range: 0 to 1.
        """
        self.numerical_aperture = numerical_aperture
        self.refractive_index = refractive_index
        self.additional_efficiency = additional_efficiency
        self.collection_efficiency = self.calculate_collection_efficiency()

    def calculate_collection_efficiency(self):
        """
        Calculate the collection efficiency based on the numerical aperture.

        The half-angle θ is given by:
            θ = arcsin(NA / n)
        And the efficiency is approximated by:
            η = (1 - cos(θ)) / 2
        This represents the fraction of the total solid angle (4π steradians) captured.
        An additional efficiency factor can be applied.
        """
        theta = math.asin(self.numerical_aperture / self.refractive_index)
        eta = (1 - math.cos(theta)) / 2
        return eta * self.additional_efficiency

    def collect(self, photon):
        """
        Simulate the collection of an emitted photon.

        Parameters:
            photon (dict): The photon object/dictionary containing its properties.

        Returns:
            dict: The updated photon dictionary with a 'collected' flag indicating if the photon was
                  successfully captured by the high-NA optics.
        """
        if random.random() < self.collection_efficiency:
            photon['collected'] = True
        else:
            photon['collected'] = False
        return photon


# Example usage:
if __name__ == "__main__":
    # Create a High-NA component with a numerical aperture of 0.5 and perfect additional efficiency.
    high_na = HighNAComponent(numerical_aperture=1, refractive_index=1, additional_efficiency=1.4)
    print("Calculated collection efficiency: {:.2%}".format(high_na.collection_efficiency))

    # Simulate an emitted photon (this would be created by the atom's decay process)
    photon = {
        'wavelength': 780,  # in nm for Rb87
        'frequency': 3.84e14,  # approximate in Hz
        'polarization': 'sigma+',  # as an example
        'emission_time': 0,  # timestamp (placeholder)
        'direction': [0, 0, 1],  # example propagation direction
        'originating_atom': {'F': 1, 'm_F': +1},
        'emission_probability': 1.0,
        'quantum_state': 'sigma+'
    }

    # Use the high-NA component to attempt to collect the photon.
    collected_photon = high_na.collect(photon)
    print("Photon collected:", collected_photon['collected'])


#   https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.129.033601 this paper support of
#   collection efficiency up to 70% and with further optimized to allow for another collection efficiency of 85%.
