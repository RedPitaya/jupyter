import numpy as np
from scipy import signal

class wave():

    def _wavetime (self):
        return (np.linspace(0, 2*np.pi, self.buffer_size, endpoint=False))

    def sine (self, t: np.array = None) -> np.array:
        """Sinus waveform.

        Parameters
        ----------
        t : array_like, optional
            If not time array is provided, a default buffer sized array
            with a 2*PI period will be used.

        Returns
        -------
        waveform : ndarray
            Sinusoidal waveform with samples in the normalized range [-1,+1].

        References
        ----------
        https://docs.scipy.org/doc/numpy/reference/generated/numpy.sin.html

        See Also
        --------
        square, sawtooth
        """
        if t is None: t = self._wavetime()
        return np.sin(t)

    def square (self, duty: float = 0.5, t: np.array = None) -> np.array:
        """Square waveform.

        Parameters
        ----------
        duty : float, optional
            Duty cycle.
        t : array_like, optional
            If not time array is provided, a default buffer sized array
            with a 2*PI period will be used.

        Returns
        -------
        waveform : ndarray
            Square waveform with samples in the normalized range [-1,+1]
            and given duty cycle.

        References
        ----------
        http://scipy.github.io/devdocs/generated/scipy.signal.square.html

        See Also
        --------
        sine, sawtooth
        """
        if t is None: t = self._wavetime()
        return signal.square(t, duty)

    def sawtooth (self, width: float = 0.5, t: np.array = None) -> np.array:
        """Sawtooth waveform.

        Parameters
        ----------
        width : float, optional
            Width of rising versus the falling sawtooth edge.
        t : array_like, optional
            If not time array is provided, a default buffer sized array
            with a 2*PI period will be used.

        Returns
        -------
        waveform : ndarray
            Sawtooth waveform with samples in the normalized range [-1,+1]
            and given width.

        References
        ----------
        http://scipy.github.io/devdocs/generated/scipy.signal.square.html

        See Also
        --------
        sine, square
        """
        if t is None: t = self._wavetime()
        return signal.sawtooth(t, width)
