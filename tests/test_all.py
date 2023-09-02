import unittest
from unittest import mock

from eveskinserver.app import DEFAULT_ICON_NAME, app, generate_sized_icon


class TestEveSkinServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_status_code(self):
        result = self.app.get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn("text/html", result.content_type)

    def test_skin_valid_type_1(self):
        """when requesting a valid SKIN type, return corresponding SKIN icon"""
        result = self.app.get("/skin/34599/icon")  # Apocalypse Kador SKIN
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")
        self.assertEqual(result.headers.get("x-suggested-filename"), "2_64.png")

    def test_skin_valid_type_2(self):
        """when requesting a valid SKIN type, return corresponding SKIN icon"""
        result = self.app.get("/skin/47290/icon")  # Thanatos Eros Blossom SKIN
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")
        self.assertEqual(result.headers.get("x-suggested-filename"), "244_64.png")

    def test_skin_invalid_type(self):
        """when requesting an invalid SKIN type, raises 404"""
        result = self.app.get("/skin/34/icon")  # not a SKIN type
        self.assertEqual(result.status_code, 404)

    def test_skin_size_32(self):
        """when requesting a SKIN type with size, return correct SKIN icon an size"""
        result = self.app.get("/skin/47290/icon?size=32")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")
        self.assertEqual(result.headers.get("x-suggested-filename"), "244_32.png")

    def test_skin_size_64(self):
        """when requesting a SKIN type with size, return correct SKIN icon an size"""
        result = self.app.get("/skin/47290/icon?size=64")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")
        self.assertEqual(result.headers.get("x-suggested-filename"), "244_64.png")

    def test_skin_size_128(self):
        """when requesting a SKIN type with size, return correct SKIN icon an size"""
        result = self.app.get("/skin/47290/icon?size=128")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")
        self.assertEqual(result.headers.get("x-suggested-filename"), "244_128.png")

    def test_skin_size_256(self):
        """when requesting a SKIN type with size, return correct SKIN icon an size"""
        result = self.app.get("/skin/47290/icon?size=256")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")
        self.assertEqual(result.headers.get("x-suggested-filename"), "244_256.png")

    def test_skin_size_512(self):
        """when requesting a SKIN type with size, return correct SKIN icon an size"""
        result = self.app.get("/skin/47290/icon?size=512")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")
        self.assertEqual(result.headers.get("x-suggested-filename"), "244_512.png")

    def test_skin_size_1024(self):
        """when requesting a SKIN type with size, return correct SKIN icon an size"""
        result = self.app.get("/skin/47290/icon?size=1024")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")
        self.assertEqual(result.headers.get("x-suggested-filename"), "244_1024.png")

    def test_skin_size_invalid_1(self):
        """when requesting a SKIN type with invalid size,
        then return 400 bad request
        """
        result = self.app.get("/skin/47290/icon?size=11")
        self.assertEqual(result.status_code, 400)

    def test_skin_size_invalid_2(self):
        """when requesting a SKIN type with invalid size,
        then return correct SKIN icon with 64 size
        """
        result = self.app.get("/skin/47290/icon?size=abc")
        self.assertEqual(result.status_code, 400)

    @mock.patch("eveskinserver.app.generate_sized_icon", wraps=generate_sized_icon)
    def test_generated_icons_are_cached(self, mock_generate_sized_icon):
        """when accessing the same icon a 2nd time, then do not generate the icon again"""

        result = self.app.get("/skin/47290/icon")
        result = self.app.get("/skin/47290/icon")

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")
        self.assertEqual(result.headers.get("x-suggested-filename"), "244_64.png")
        self.assertEqual(mock_generate_sized_icon.call_count, 1)

    def test_favicon_exists(self):
        result = self.app.get("/favicon.ico")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")

    def test_skin_default(self):
        """when icon file can not be found, then use default icon"""
        result = self.app.get("/skin/53362/icon")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "image/png")
        self.assertEqual(
            result.headers.get("x-suggested-filename"), f"{DEFAULT_ICON_NAME}_64.png"
        )
