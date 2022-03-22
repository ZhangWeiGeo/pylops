import numpy as np
from numpy.core.multiarray import normalize_axis_index

from pylops import LinearOperator
from pylops.utils._internal import _value_or_list_like_to_tuple


class Transpose(LinearOperator):
    r"""Transpose operator.

    Transpose axes of a multi-dimensional array. This operator works with
    flattened input model (or data), which are however multi-dimensional in
    nature and will be reshaped and treated as such in both forward and adjoint
    modes.

    Parameters
    ----------
    dims : :obj:`tuple`, optional
        Number of samples for each dimension
    axes : :obj:`tuple`, optional
        Direction along which transposition is applied
    dtype : :obj:`str`, optional
        Type of elements in input array
    name : :obj:`str`, optional
        .. versionadded:: 2.0.0

        Name of operator (to be used by :func:`pylops.utils.describe.describe`)

    Attributes
    ----------
    shape : :obj:`tuple`
        Operator shape
    explicit : :obj:`bool`
        Operator contains a matrix that can be solved explicitly
        (``True``) or not (``False``)

    Raises
    ------
    ValueError
        If ``axes`` contains repeated dimensions (or a dimension is missing)

    Notes
    -----
    The Transpose operator reshapes the input model into a multi-dimensional
    array of size ``dims`` and transposes (or swaps) its axes as defined
    in ``axes``.

    Similarly, in adjoint mode the data is reshaped into a multi-dimensional
    array whose size is a permuted version of ``dims`` defined by ``axes``.
    The array is then rearragned into the original model dimensions ``dims``.

    """

    def __init__(self, dims, axes, dtype="float64", name="T"):
        self.dims = _value_or_list_like_to_tuple(dims)
        ndims = len(self.dims)
        self.axes = [normalize_axis_index(ax, ndims) for ax in axes]

        # find out if all axes are present only once in axes
        if len(np.unique(self.axes)) != ndims:
            raise ValueError("axes must contain each direction once")

        # find out how axes should be transposed in adjoint mode
        self.axesd = np.zeros(ndims, dtype=int)
        self.axesd[self.axes] = np.arange(ndims, dtype=int)

        dimsd = np.zeros(ndims, dtype=int)
        dimsd[self.axesd] = self.dims
        self.dimsd = tuple(dimsd)
        self.axesd = list(self.axesd)

        self.shape = (np.prod(self.dimsd), np.prod(self.dims))
        self.dtype = np.dtype(dtype)
        super().__init__(explicit=False, clinear=True, name=name)

    def _matvec(self, x):
        y = x.reshape(self.dims)
        y = y.transpose(self.axes)
        return y.ravel()

    def _rmatvec(self, x):
        y = x.reshape(self.dimsd)
        y = y.transpose(self.axesd)
        return y.ravel()
