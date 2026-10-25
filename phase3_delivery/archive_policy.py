"""Inspect NPZ size/shape envelopes before a handoff reader allocates arrays."""
import math
import zipfile

import numpy as np

from kaggle_worker.artifacts import valid_name
from .io import MAX_JSON_BYTES

MAX_CHECKPOINT_BYTES = 256*1024**2


def check_npz(stream, outer_size, max_bytes=MAX_CHECKPOINT_BYTES):
    if not 0 <= outer_size <= max_bytes:
        raise ValueError('NPZ exceeds checkpoint byte reservation')
    with zipfile.ZipFile(stream) as arrays:
        infos = arrays.infolist()
        names = [item.filename for item in infos]
        if (len(names) != len(set(names)) or not names or
                any(not valid_name(name) or '/' in name or not name.endswith('.npy') for name in names)):
            raise ValueError('Invalid NPZ array entry inventory')
        total = 0
        for info in infos:
            # The authoritative saver uses np.savez, which stores members without
            # nested compression. Reject a different transport encoding here.
            if info.compress_type != zipfile.ZIP_STORED or info.file_size > max_bytes:
                raise ValueError('Unexpected compressed or oversized NPZ member')
            total += info.file_size
            if total > max_bytes:
                raise ValueError('Expanded NPZ exceeds checkpoint byte reservation')
            with arrays.open(info) as member:
                version = np.lib.format.read_magic(member)
                if version == (1, 0):
                    shape, _, dtype = np.lib.format.read_array_header_1_0(member, max_header_size=10000)
                elif version == (2, 0):
                    shape, _, dtype = np.lib.format.read_array_header_2_0(member, max_header_size=10000)
                else:
                    raise ValueError('Unsupported NPY header version')
                if (dtype.hasobject or dtype.fields is not None or dtype.subdtype is not None or
                        dtype.kind not in 'biufUS' or any(type(n) is not int or n < 0 for n in shape)):
                    raise ValueError('Unsupported dtype or invalid shape in NPZ')
                expected = math.prod(shape)*dtype.itemsize
                if expected > max_bytes or member.tell()+expected != info.file_size:
                    raise ValueError('NPY shape claims bytes absent from its member')
                if info.filename == 'metadata.npy' and expected > MAX_JSON_BYTES:
                    raise ValueError('Checkpoint metadata exceeds JSON byte reservation')
    return {'array_members': len(infos), 'expanded_array_bytes': total}


def check_archive_npz(path):
    checked, peak = 0, 0
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if (len(names) != len(set(names)) or any(not valid_name(name) for name in names if not name.endswith('/')) or
                sum(item.file_size for item in infos) > 4*1024**3):
            raise ValueError('Unsafe or oversized worker archive inventory')
        for info in infos:
            limit = MAX_JSON_BYTES if info.filename.endswith('.json') else MAX_CHECKPOINT_BYTES
            if info.file_size > limit:
                raise ValueError('Archive member exceeds its transport byte reservation')
            if info.filename.endswith('.npz'):
                with archive.open(info) as stream:
                    report = check_npz(stream, info.file_size)
                checked += 1
                peak = max(peak, report['expanded_array_bytes'])
    return {'npz_files_checked': checked, 'largest_expanded_npz_bytes': peak,
            'checkpoint_byte_limit': MAX_CHECKPOINT_BYTES}
