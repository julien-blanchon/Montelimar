import json
from pathlib import Path

from fastapi.openapi.utils import get_openapi

from ocr_mlx.endpoint import app


def export_openapi(path: Path):
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes,
            ),
            f,
        )


if __name__ == "__main__":
    export_openapi(Path("openapi.json"))
