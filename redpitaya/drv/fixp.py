class fixp (object):
    """Fixed point basic class."""
    __init__(self, s: bool, m: int, f: int):
        self.s = s
        self.m = m
        self.f = f

    @property
    def num(self) -> int:
        """Number of possible values."""
        return (         (1<<(v.s+v.m+v.f))        )

    @property
    def max(self) -> int:
        """Maximum value (positive)."""
        return (       (+(1<<(    v.m+v.f))-1)     )

    @property
    def min(self) -> int:
        """Minimum value (nagetive or zero for unsigned)."""
        return ((v.s ? (-(1<<(    v.m+v.f))  ) : 0))

    @property
    def unit(self) -> int:
        """Unit (1) value."""
        return (         (1<<(        v.f))        )

    @property
    def bits(self) -> int:
        """Number of used bits."""
        return (             (v.s+v.m+v.f)         )

    def float2fixp(self, value: float) -> int:
        """Conversion from ``float`` fixed point."""
        if ((not self.s) and (value < 0)):
            raise ValueError("This fixed point number is unsigned, so negative values are not supported.")
        else:
            return int(value*self.unit)

    def fixp2float(self, value: int) -> float:
        """Conversion from ``float`` fixed point."""
        return (float(value)/float(self.unit))
