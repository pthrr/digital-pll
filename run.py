#
# Wikipedia example of a PLL
# https://en.wikipedia.org/wiki/Phase-locked_loop
#

import numpy as np
import matplotlib.pyplot as plt

f = 1e6
fs = 100*f
spp = fs / f
numiterations = int(spp*1000)

def tracksig(it):
    period = int(it / spp)
    even = ((period % 2) == 0)

    return 0 if even else 1

if __name__ == "__main__":
    # Initialize variables
    vcofreq = np.zeros(numiterations)
    ervec = np.zeros(numiterations)
    refvec = np.zeros(numiterations)
    sigvec = np.zeros(numiterations)

    # Keep track of last states of reference, signal, and error signal
    qsig = 0
    qref = 0
    lref = 0
    lsig = 0
    lersig = 0
    phs = 0
    freq = 0

    # Loop filter constants (proportional and derivative)
    # Currently powers of two to facilitate multiplication by shifts
    prop = 1 / 128
    deriv = 64

    for it in range(numiterations):
        # Simulate a local oscillator using a 16-bit counter
        phs = np.mod(phs + np.floor(freq / 2 ** 16), 2 ** 16)
        ref = (phs < 32768)
        refvec[it] = ref

        # Get the next digital value (0 or 1) of the signal to track
        sig = tracksig(it)
        sigvec[it] = sig

        # Implement the phase-frequency detector
        rst = not (qsig & qref) # Reset the "flip-flop" of the phase-frequency

        # detector when both signal and reference are high
        qsig = (qsig | (sig & (not lsig))) & rst # Trigger signal flip-flop and leading edge of signal
        qref = (qref | (ref & (not lref))) & rst # Trigger reference flip-flop on leading edge of reference
        lref = ref
        lsig = sig # Store these values for next iteration (for edge detection)
        ersig = qref - qsig # Compute the error signal (whether frequency should increase or decrease)

        # Error signal is given by one or the other flip flop signal
        # Implement a pole-zero filter by proportional and derivative input to frequency
        filtered_ersig = ersig + (ersig - lersig) * deriv;

        # Keep error signal for proportional output
        lersig = ersig;

        # Integrate VCO frequency using the error signal
        freq = freq - 2 ** 16 * filtered_ersig * prop;

        # Frequency is tracked as a fixed-point binary fraction
        # Store the current VCO frequency
        vcofreq[it] = freq / 2 ** 16

        # Store the error signal to show whether signal or reference is higher frequency
        ervec[it] = ersig

    # plot
    fig, ax = plt.subplots(4, 1)
    ax[0].plot(refvec)
    ax[0].set_title('Local signal')
    ax[1].plot(sigvec)
    ax[1].set_title('Input signal')
    ax[2].plot(vcofreq)
    ax[2].set_title('VCO signal')
    ax[3].plot(ervec)
    ax[3].set_title('Error signal')

    fig.tight_layout()
    fig.savefig('res.png', dpi=300)
