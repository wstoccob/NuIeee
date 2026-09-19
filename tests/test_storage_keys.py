"""Live MinIO data contains keys with spaces and Cyrillic, which broke the old
path-parameter delete route. New keys must be URL-safe."""

from services.storage import build_object_key, public_url


def test_key_is_url_safe_for_cyrillic_filename():
    key = build_object_key("Z30_1633-Улучшено-Ум. шума.jpg")
    assert key.isascii()
    assert " " not in key
    assert key.endswith(".jpg")


def test_key_is_url_safe_for_spaced_filename():
    key = build_object_key("photo_2026-03-08 23.02.44.jpeg")
    assert " " not in key
    assert key.endswith(".jpeg")


def test_keys_do_not_collide():
    assert build_object_key("a.png") != build_object_key("a.png")


def test_public_url_uses_configured_host():
    url = public_url("abc.jpg")
    assert url == "https://minio.ieee.nu/event-photos/abc.jpg"
