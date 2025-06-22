import time
import matplotlib.pyplot as plt

# Assume that the following classes have been imported from their modules:
from ExcitingLaser import ExcitingLaser
from ExcitingLaser import Rb87Atom
from highNA import HighNAComponent
from SPD import SPD

def simulate_single_photon_event():
    # Initialize each component with chosen parameters.
    # 1. ExcitingLaser: high power, on-resonance pulse.
    laser = ExcitingLaser(
        power=0.44e-3,            # Effective power (arbitrary units)
        frequency=780,         # Wavelength in nm for Rb87
        pulse_duration=1.1e-6,    # 50 ns pulse
        pulse_shape='gaussian',
        noise_level=0.1,
        detuning=0.0,          # On resonance
        alignment_efficiency=0.95,
        polarization='sigma+'
    )

    # 2. Rb87Atom: initially in the proper state.
    atom = Rb87Atom(excited_state_lifetime=26e-9)

    # 3. HighNAComponent: choose parameters so that, for example, even a simple geometric model
    # would yield 50% but we boost it via additional_efficiency.
    # With NA=1 and refractive_index=1, the simple efficiency is 0.5.
    # Setting additional_efficiency to 1.8 gives 0.9 (90% efficiency).
    high_na = HighNAComponent(
        numerical_aperture=1.0,
        refractive_index=1.0,
        additional_efficiency=1.4
    )

    # 4. SinglePhotonDetector: set a detection efficiency (e.g., 80%), a moderate dark count rate,
    # some timing jitter (e.g., 50 ps), and a small dead time.
    spd = SPD(
        detection_efficiency=0.6,  # 80% chance to detect an incident photon
        dark_count_rate=100,       # 100 counts per second
        timing_jitter=50e-12,      # 50 picoseconds jitter
        dead_time=1e-6             # 1 microsecond dead time
    )

    # ---- Begin Simulation Pipeline ----

    # Step 1: Laser emits a pulse producing an excitation event.
    excitation_event = laser.emit()
    print("Laser emitted excitation event:", excitation_event)

    # Step 2: The atom is excited by the laser.
    excitation_result = atom.excite(excitation_event)
    if excitation_result['status'] != 'excited':
        print("Atom was not excited.")
        return

    print("Atom excitation result:", excitation_result)

    # Step 3: The excited atom decays and produces a photon.
    decay_result = atom.decay()
    photon = decay_result.get('photon')
    if photon is None:
        print("Atom did not emit a photon upon decay.")
        return

    print("Photon generated from decay:", photon)

    # Step 4: High-NA optics attempts to collect the photon.
    collected_photon = high_na.collect(photon)
    if not collected_photon.get('collected', False):
        print("Photon was not collected by the high-NA optics.")
        return

    print("Photon after High-NA collection:", collected_photon)

    # Step 5: (Optional) Simulate a propagation delay in an optical channel.
    propagation_delay = 10e-9  # e.g., 10 ns delay
    arrival_time = time.time() + propagation_delay

    # Step 6: The SPD receives the photon and attempts detection.
    detection_event = spd.detect(collected_photon, arrival_time)
    return detection_event.get('detected', False)


if __name__ == '__main__':
    num_trials = 1000
    detection_results = []

    for _ in range(num_trials):
        detected = simulate_single_photon_event()
        detection_results.append(detected)

    # Count detections and non-detections
    num_detections = sum(1 for result in detection_results if result)
    num_non_detections = num_trials - num_detections

    print(f"Out of {num_trials} trials, there were {num_detections} successful SPD detections.")

    # Plotting the bar chart
    labels = ['Detected', 'Not Detected']
    counts = [num_detections, num_non_detections]

    plt.figure(figsize=(6, 5))
    bars = plt.bar(labels, counts)

    # Add numbers on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 10, str(height),
                 ha='center', va='bottom', fontsize=12)

    plt.title('SPD Detection Results')
    plt.ylabel('Number of Trials')
    plt.ylim(0, max(counts) * 1.1)  # Add a little space above bars
    plt.show()

