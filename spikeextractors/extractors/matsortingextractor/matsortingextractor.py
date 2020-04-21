from collections import deque
from pathlib import Path
from typing import Union

try:
    import h5py
    from scipy.io.matlab import loadmat, savemat

    HAVE_MAT = True
except ImportError:
    HAVE_MAT = False

from spikeextractors import SortingExtractor

PathType = Union[str, Path]


class MATSortingExtractor(SortingExtractor):
    extractor_name = "MATSortingExtractor"
    installed = HAVE_MAT  # check at class level if installed or not
    is_writable = True
    mode = "file"
    installation_mesg = "To use the MATSortingExtractor install h5py and scipy: \n\n pip install h5py scipy\n\n"  # error message when not installed

    def __init__(self, file_path: PathType):
        super().__init__()

        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        if not isinstance(file_path, Path):
            raise TypeError(f"Expected a str or Path file_path but got '{type(file_path).__name__}'")

        file_path = file_path.resolve()  # get absolute path to this file
        if not file_path.is_file():
            raise ValueError(f"Specified file path '{file_path}' does not exist.")

        self._kwargs = {"file_path": file_path}

        try:  # load old-style (up to 7.2) .mat file
            self._data = loadmat(file_path, matlab_compatible=True)
            self._kwargs["old_style_mat"] = True
        except NotImplementedError:  # new style .mat file
            self._data = h5py.File(file_path, "r+")
            self._kwargs["old_style_mat"] = False

    def _getfield(self, fieldname: str):
        def _drill(d: dict, keys: deque):
            if len(keys) == 1:
                return d[keys.popleft()]
            else:
                return _drill(d[keys.popleft()], keys)

        if self._kwargs["old_style_mat"]:
            return _drill(self._data, deque(fieldname.split("/")))
        else:
            return self._data[fieldname][()]

