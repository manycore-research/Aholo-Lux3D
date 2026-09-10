"""Embed the viewer, decoder resources and original artifacts in one HTML file."""

import base64
import html
import json
import pathlib
import re


VIEWER_ROOT = pathlib.Path(__file__).resolve().parents[1] / "viewer"
SUPPORTED_LOCALES = ("en", "zh-CN")


def write_preview(target, manifest, locale):
    """Generate an offline document; generation is not browser/E2E acceptance."""
    messages = json.loads(
        (VIEWER_ROOT / "locales" / f"{locale}.json").read_text(encoding="utf-8")
    )
    target = pathlib.Path(target)
    assets = {
        artifact["id"]: base64.b64encode(
            (target / artifact["path"]).read_bytes()
        ).decode("ascii")
        for artifact in manifest["artifacts"]
    }
    with (VIEWER_ROOT / "decoders.json").open(encoding="utf-8") as file_obj:
        decoders = json.load(file_obj)
    manifest["preview"] = {"status": "generated", "path": "preview.html", "locale": locale}
    notices = (VIEWER_ROOT / "THIRD_PARTY_NOTICES.txt").read_text(encoding="utf-8")
    payload = json.dumps(
        {
            "manifest": manifest,
            "assets": assets,
            "decoders": decoders,
            "notices": notices,
            "messages": messages,
        },
        ensure_ascii=True,
    )
    # JSON is data, never executable HTML, even when labels contain </script>.
    payload = (
        payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    )
    template_values = {**messages, "title": manifest["title"]}
    replacements = {
        **{f"{{{{{key}}}}}": html.escape(value, quote=True) for key, value in template_values.items()},
        "/*LUX3D_LOCALE*/": locale,
        "/*LUX3D_LOGO*/": "data:image/png;base64,"
        + base64.b64encode((VIEWER_ROOT / "lux3d-logo.png").read_bytes()).decode(
            "ascii"
        ),
        "/*LUX3D_STYLE*/": (VIEWER_ROOT / "style.css").read_text(encoding="utf-8"),
        "/*LUX3D_VIEWER*/": (VIEWER_ROOT / "viewer.bundle.js").read_text(encoding="utf-8"),
        "/*LUX3D_DATA*/": payload,
    }
    # Substitute once so user text and embedded resources are never reinterpreted.
    document = re.sub(
        r"/\*LUX3D_\w+\*/|\{\{[\w.]+\}\}",
        lambda match: replacements[match[0]],
        (VIEWER_ROOT / "template.html").read_text(encoding="utf-8"),
    )
    with (target / "preview.html").open("x", encoding="utf-8") as file_obj:
        file_obj.write(document)
