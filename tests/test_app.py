import unittest
from http import HTTPStatus
from typing import NamedTuple
from unittest import mock

from eveskinserver.app import DEFAULT_ICON_NAME, app, generate_sized_icon


class TestEveSkinServer(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True  # type: ignore

    def test_home_status_code(self):
        # when
        response = self.app.get("/")

        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.content_type)
        response.close()

    def test_should_return_file_for_valid_type(self):
        class Case(NamedTuple):
            name: str
            url: str
            want_filename: str
            want_status_code: HTTPStatus

        cases = [
            Case(
                name="valid type 1",
                url="/skin/34599/icon",  # Apocalypse Kador SKIN
                want_filename="2_64.png",
                want_status_code=HTTPStatus.OK,
            ),
            Case(
                name="valid type 2",
                url="/skin/47290/icon",  # Thanatos Eros Blossom SKIN
                want_filename="244_64.png",
                want_status_code=HTTPStatus.OK,
            ),
            Case(
                name="invalid type",
                url="/skin/34/icon",
                want_filename="",
                want_status_code=HTTPStatus.NOT_FOUND,
            ),
            Case(
                name="valid type and size 32",
                url="/skin/47290/icon?size=32",
                want_filename="244_32.png",
                want_status_code=HTTPStatus.OK,
            ),
            Case(
                name="valid type and size 64",
                url="/skin/47290/icon?size=64",
                want_filename="244_64.png",
                want_status_code=HTTPStatus.OK,
            ),
            Case(
                name="valid type and size 128",
                url="/skin/47290/icon?size=128",
                want_filename="244_128.png",
                want_status_code=HTTPStatus.OK,
            ),
            Case(
                name="valid type and size 256",
                url="/skin/47290/icon?size=256",
                want_filename="244_256.png",
                want_status_code=HTTPStatus.OK,
            ),
            Case(
                name="valid type and size 512",
                url="/skin/47290/icon?size=512",
                want_filename="244_512.png",
                want_status_code=HTTPStatus.OK,
            ),
            Case(
                name="valid type and size 1024",
                url="/skin/47290/icon?size=1024",
                want_filename="244_1024.png",
                want_status_code=HTTPStatus.OK,
            ),
            Case(
                name="valid type and invalid size 1",
                url="/skin/47290/icon?size=11",
                want_filename="",
                want_status_code=HTTPStatus.BAD_REQUEST,
            ),
            Case(
                name="valid type and invalid size 2",
                url="/skin/47290/icon?size=abc",
                want_filename="",
                want_status_code=HTTPStatus.BAD_REQUEST,
            ),
            Case(
                name="fallback to default when icon not found for valid type",
                url="/skin/53362/icon",
                want_filename=f"{DEFAULT_ICON_NAME}_64.png",
                want_status_code=HTTPStatus.OK,
            ),
        ]

        for tc in cases:
            with self.subTest(name=tc.name):
                # when
                response = self.app.get(tc.url)

                # then
                self.assertEqual(response.status_code, tc.want_status_code)
                if response.status_code == HTTPStatus.OK:
                    self.assertEqual(response.content_type, "image/png")
                    self.assertEqual(
                        response.headers.get("x-suggested-filename"), tc.want_filename
                    )
                response.close()

    @mock.patch("eveskinserver.app.generate_sized_icon", wraps=generate_sized_icon)
    def test_generated_icons_are_cached(self, mock_generate_sized_icon):
        """when accessing the same icon a 2nd time, then do not generate the icon again"""
        # given
        response_1 = self.app.get("/skin/47290/icon")
        response_1.close()

        # when
        response_2 = self.app.get("/skin/47290/icon")

        # then
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_2.content_type, "image/png")
        self.assertEqual(response_2.headers.get("x-suggested-filename"), "244_64.png")
        self.assertEqual(mock_generate_sized_icon.call_count, 1)
        response_2.close()

    def test_favicon_exists(self):
        # when
        response = self.app.get("/favicon.ico")

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")
        response.close()
