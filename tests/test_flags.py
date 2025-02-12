from dunamai import Version

from version_tagger import _update_version


def test_update_version_major():
    v = Version("1.2.3")
    assert (
        _update_version(
            v,
            major=True,
            minor=False,
            patch=False,
            manual="",
        )
        == "2.0.0"
    )


def test_update_version_minor():
    v = Version("1.2.3")
    assert (
        _update_version(
            v,
            major=False,
            minor=True,
            patch=False,
            manual="",
        )
        == "1.3.0"
    )


def test_update_version_patch():
    v = Version("1.2.3")
    assert (
        _update_version(
            v,
            major=False,
            minor=False,
            patch=True,
            manual="",
        )
        == "1.2.4"
    )
