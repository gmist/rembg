import filetype
import io
import pyheif
from PIL import Image


def is_image(file_name):
    fi_type = filetype.guess(file_name)

    if fi_type is None or fi_type.mime.find("image") < 0:
        return None

    return fi_type.mime


def heic_to_bytes(f):
    heif_file = pyheif.read(f.read())
    b = io.BytesIO()
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    image.save(b, format='JPEG')
    b.seek(0)
    return b
