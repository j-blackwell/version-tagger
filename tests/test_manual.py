import pytest
import packaging.version as version

from dunamai import Version

from version_tagger import (
    _validate_manual,
    _update_version,
)


def test_validate_manual_valid():
    assert _validate_manual(Version("1.2.3"), "2.0.0") is True
    assert _validate_manual(Version("1.9.3"), "1.10.0") is True


def test_validate_manual_invalid():
    with pytest.raises(version.InvalidVersion):
        _validate_manual(Version("2.0.0"), "1.9.0")
    with pytest.raises(version.InvalidVersion):
        _validate_manual(Version("1.10.0"), "1.9.9")
    with pytest.raises(version.InvalidVersion):
        _validate_manual(Version("1.10.0"), "not a valid version")


def test_update_version_manual():
    v = Version("1.2.3")
    manual = "2.1.0"
    assert (
        _update_version(
            v,
            major=False,
            minor=False,
            patch=False,
            manual=manual,
        )
        == manual
    )
