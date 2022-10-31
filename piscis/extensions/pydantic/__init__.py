from .i18n import patch
import dataclasses

patch()


@dataclasses.dataclass
class FileField:
    name: str
    content_type: str
    mimetype: str
    ext: str
    content: bytes
