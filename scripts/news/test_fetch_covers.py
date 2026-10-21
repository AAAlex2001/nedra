"""Повтор одной фотографии должен обнаруживаться до записи новой обложки."""

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image, ImageDraw

from fetch_covers import download_cover, image_fingerprint, is_repeated_image, source_key


class CoverDuplicateTests(unittest.TestCase):
    def test_recompression_does_not_make_a_new_photograph(self):
        image = Image.new("RGB", (1200, 675), "#75a6c1")
        draw = ImageDraw.Draw(image)
        for index in range(25):
            x = index * 43
            draw.rectangle((x, 60 + index * 5, x + 27, 620 - index * 9), fill=(index * 9, 70, 190))
        compressed = io.BytesIO()
        image.save(compressed, "JPEG", quality=65)
        compressed.seek(0)
        self.assertTrue(is_repeated_image(Image.open(compressed), [image_fingerprint(image)]))
        self.assertTrue(is_repeated_image(image.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
                                          [image_fingerprint(image)]))
        other = Image.new("RGB", (1200, 675), "green")
        ImageDraw.Draw(other).ellipse((100, 100, 950, 580), fill="red")
        self.assertFalse(is_repeated_image(other, [image_fingerprint(image)]))

    def test_tracking_does_not_make_a_new_source(self):
        self.assertEqual(
            source_key("https://commons.wikimedia.org/wiki/File:Photo.jpg?utm_source=search#license"),
            source_key("https://commons.wikimedia.org/wiki/File:Photo.jpg"),
        )
        self.assertNotEqual(source_key("https://commons.wikimedia.org/?curid=1"),
                            source_key("https://commons.wikimedia.org/?curid=2"))

    def test_duplicate_download_does_not_overwrite_the_previous_cover(self):
        image = Image.new("RGB", (1200, 675), "#2596be")
        ImageDraw.Draw(image).rectangle((100, 100, 700, 500), fill="orange")
        data = io.BytesIO()
        image.save(data, "PNG")
        response = Mock(content=data.getvalue())
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directory:
            target = Path(directory) / "cover.jpg"
            target.write_bytes(b"previous-cover")
            with patch("fetch_covers.requests.get", return_value=response):
                saved = download_cover("https://example.test/photo", target, [image_fingerprint(image)])
            self.assertFalse(saved)
            self.assertEqual(target.read_bytes(), b"previous-cover")

    def test_small_preview_is_not_upscaled_into_a_cover(self):
        data = io.BytesIO()
        Image.new("RGB", (330, 186), "orange").save(data, "PNG")
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directory:
            target = Path(directory) / "cover.jpg"
            with patch("fetch_covers.requests.get", return_value=Mock(content=data.getvalue())):
                self.assertFalse(download_cover("https://example.test/preview", target))
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
