import json
import logging
import os

log = logging.getLogger(__name__)

# use get_spdx() to ref the spdx_license info, so it
# only loaded from disk once
_SPDX_LICENSES = None


def load_spdx():
    cwd = os.path.dirname(os.path.abspath(__file__))
    license_path = os.path.join(cwd, 'spdx_licenses.json')
    try:
        with open(license_path, 'r') as fo:
            return json.load(fo)
    except EnvironmentError as exc:
        log.warning('Unable to open %s to load the list of acceptable '
                    'open source licenses: %s', license_path, exc)
        log.exception(exc)
        return {}


def get_spdx():
    global _SPDX_LICENSES

    if not _SPDX_LICENSES:
        _SPDX_LICENSES = load_spdx()

    return _SPDX_LICENSES
