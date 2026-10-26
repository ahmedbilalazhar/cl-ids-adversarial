"""Prepare a byte-preserving private upload for Kaggle's archive expansion.

The reviewed ZIP is Base64-encoded as a non-archive file. A standard-library
notebook bootstrap verifies and restores the exact original bytes before the
unchanged v5 scientific workflow runs. This tool does not upload or dispatch.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path

from phase3_delivery.io import publish_new_bytes, read_verified_bytes

RAW_CHUNK = 3*1024**2
MAX_BUNDLE_BYTES = 2*1024**3
BUNDLE_LINE = "BUNDLE = Path('/kaggle/input/CHANGE-TO-YOUR-PRIVATE-DATASET/qualification.zip')"
CLOCK_LINE = 'SESSION_STARTED = time.monotonic()'


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while block := stream.read(8*1024**2):
            result.update(block)
    return result.hexdigest()


def bootstrap_source(archive_sha, encoded_sha, raw_size, encoded_size):
    """The generated cell intentionally uses only the notebook standard library."""
    return f'''from pathlib import Path
import base64, hashlib, os, tempfile, time

# Upload qualification.zip.b64 as a private Dataset, attach it, then set this path.
ENCODED_BUNDLE = Path('/kaggle/input/CHANGE-TO-YOUR-PRIVATE-DATASET/qualification.zip.b64')
DECODED_BUNDLE = Path('/kaggle/working/phase3-qualification.zip')
UPLOAD_SESSION_STARTED = time.monotonic()

def _upload_sha(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024**2), b''):
            hasher.update(block)
    return hasher.hexdigest()

def _restore_upload():
    if not ENCODED_BUNDLE.is_file() or ENCODED_BUNDLE.stat().st_size != {encoded_size}:
        raise ValueError('Attach the exact private qualification.zip.b64 file and set ENCODED_BUNDLE')
    if _upload_sha(ENCODED_BUNDLE) != {encoded_sha!r}:
        raise ValueError('Encoded private upload bytes changed')
    if DECODED_BUNDLE.exists() or DECODED_BUNDLE.is_symlink():
        if (not DECODED_BUNDLE.is_file() or DECODED_BUNDLE.stat().st_size != {raw_size} or
                _upload_sha(DECODED_BUNDLE) != {archive_sha!r}):
            raise ValueError('Existing decoded bundle differs; preserve it and choose a fresh path')
        return 'existing_exact_bundle_verified'
    DECODED_BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    descriptor, pending = tempfile.mkstemp(prefix='uncommitted-qualification-', dir=DECODED_BUNDLE.parent)
    encoded_hash, archive_hash = hashlib.sha256(), hashlib.sha256()
    encoded_bytes, archive_bytes = 0, 0
    with os.fdopen(descriptor, 'wb') as output, ENCODED_BUNDLE.open('rb') as source:
        while block := source.read(4*1024**2):
            encoded_bytes += len(block)
            if encoded_bytes > {encoded_size}:
                raise ValueError('Encoded upload grew beyond its reservation')
            encoded_hash.update(block)
            decoded = base64.b64decode(block, validate=True)
            archive_bytes += len(decoded)
            if archive_bytes > {raw_size}:
                raise ValueError('Decoded upload exceeded its reservation')
            archive_hash.update(decoded)
            output.write(decoded)
        if (encoded_bytes != {encoded_size} or archive_bytes != {raw_size} or
                encoded_hash.hexdigest() != {encoded_sha!r} or archive_hash.hexdigest() != {archive_sha!r}):
            raise ValueError('Decoded bundle differs from the reviewed original ZIP')
        output.flush()
        os.fsync(output.fileno())
    # Publish only a fully verified ZIP. Failed staging files remain visible.
    os.link(pending, DECODED_BUNDLE)
    try:
        Path(pending).unlink()
    except OSError:
        pass
    return 'exact_original_bundle_restored'

print(_restore_upload())
'''


def adapt_notebook(notebook, bootstrap):
    value = json.loads(json.dumps(notebook))
    if value.get('nbformat') != 4 or value.get('metadata', {}).get('phase3', {}).get('final_dispatchable') is not False:
        raise ValueError('Only the reviewed sealed qualification notebook may be wrapped')
    replacements = {'bundle': 0, 'clock': 0}
    for cell in value['cells']:
        if cell['cell_type'] != 'code':
            continue
        source = ''.join(cell['source'])
        replacements['bundle'] += source.count(BUNDLE_LINE)
        replacements['clock'] += source.count(CLOCK_LINE)
        source = source.replace(BUNDLE_LINE, 'BUNDLE = DECODED_BUNDLE')
        source = source.replace(CLOCK_LINE, 'SESSION_STARTED = UPLOAD_SESSION_STARTED')
        compile(source, 'wrapped-v5-notebook', 'exec')
        cell['source'] = source.splitlines(keepends=True)
    if replacements != {'bundle': 1, 'clock': 1}:
        raise ValueError('Reviewed notebook layout changed; refuse ambiguous source edits')
    compile(bootstrap, 'upload-bootstrap', 'exec')
    value['cells'] = [
        {'cell_type': 'markdown', 'metadata': {}, 'source': [
            '# Phase 3 Kaggle qualification\n',
            'Attach the private `qualification.zip.b64` Dataset and set `ENCODED_BUNDLE` below. '
            'The bootstrap restores the exact reviewed ZIP before the existing v5 cells run. '
            'Start with CPU fixtures and keep full-data confirmation disabled until they pass.\n']},
        {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [],
         'source': bootstrap.splitlines(keepends=True)},
    ]+value['cells']
    value['metadata']['phase3']['upload_transport'] = 'base64-exact-zip-v1'
    return value


def prepare(archive, archive_sha, notebook_path, notebook_sha, output):
    archive, notebook_path, output = Path(archive), Path(notebook_path), Path(output)
    notebook_bytes = read_verified_bytes(notebook_path, notebook_sha)
    notebook = json.loads(notebook_bytes.decode('utf-8'))
    if notebook.get('metadata', {}).get('phase3', {}).get('bundle_sha256') != archive_sha:
        raise ValueError('Notebook and independently supplied archive pins differ')
    # Reuse the bounded single-snapshot copy so encoding cannot race the input.
    from phase3_delivery.io import copy_verified_archive
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    try:
        import tempfile
        with tempfile.TemporaryDirectory(prefix='upload-source-') as directory:
            source = Path(directory)/'reviewed.zip'
            size = copy_verified_archive(archive, source, archive_sha, max_bytes=MAX_BUNDLE_BYTES)
            encoded = output/'qualification.zip.b64'
            with source.open('rb') as stream, encoded.open('xb') as target:
                while block := stream.read(RAW_CHUNK):
                    target.write(base64.b64encode(block))
                target.flush()
                os.fsync(target.fileno())
            encoded_size, encoded_sha = encoded.stat().st_size, sha(encoded)
            if encoded_size != 4*((size+2)//3):
                raise ValueError('Encoded upload size differs from the standard Base64 envelope')
            bootstrap = bootstrap_source(archive_sha, encoded_sha, size, encoded_size)
            adapted = adapt_notebook(notebook, bootstrap)
            adapted['metadata']['phase3'].update({'original_notebook_sha256': notebook_sha,
                                                'encoded_upload_sha256': encoded_sha})
            target = output/'phase3-kaggle-start.ipynb'
            publish_new_bytes(target, (json.dumps(adapted, indent=2)+'\n').encode('utf-8'))
        receipt = {'schema': 'phase3-kaggle-upload-transport-v1', 'status': 'prepared_not_provider_qualified',
                   'archive_sha256': archive_sha, 'archive_bytes': size, 'original_notebook_sha256': notebook_sha,
                   'encoded_upload_sha256': encoded_sha, 'encoded_upload_bytes': encoded_size,
                   'notebook_sha256': sha(target), 'bootstrap_sha256': hashlib.sha256(bootstrap.encode()).hexdigest(),
                   'original_code_changes': ['BUNDLE points to restored original ZIP',
                                             'SESSION_STARTED includes decoding in the original shared budget'],
                   'uploaded': False, 'provider_upload_qualified': False, 'worker_source_changed': False,
                   'final_test_accessed': False, 'final_dispatchable': False}
        publish_new_bytes(output/'receipt.json', (json.dumps(receipt, indent=2, sort_keys=True)+'\n').encode('utf-8'))
        return receipt
    except Exception as exc:
        publish_new_bytes(output/'failure.json', (json.dumps({'status': 'failed_attempt_retained',
                          'exception': type(exc).__name__, 'message': str(exc), 'final_dispatchable': False})+'\n').encode())
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--archive-sha256', required=True)
    parser.add_argument('--notebook', type=Path, required=True)
    parser.add_argument('--notebook-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    receipt = prepare(args.archive, args.archive_sha256, args.notebook, args.notebook_sha256, args.output)
    print({key: receipt[key] for key in ('status', 'archive_bytes', 'encoded_upload_bytes', 'uploaded')})


if __name__ == '__main__':
    main()
