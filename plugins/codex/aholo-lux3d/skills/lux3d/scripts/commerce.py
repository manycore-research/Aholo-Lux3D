#!/usr/bin/env python3
"""Codex-only thin CLI for live Lux3D account and quote facts."""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
import warnings


EXPECTED_ECOSYSTEM = "codex"
EXPECTED_SOURCE = 1


class CliError(RuntimeError):
    """A fixed, non-sensitive CLI failure."""

    def __init__(self, code, message, *, retryable=False):
        self.code = code
        self.message = message
        self.retryable = retryable
        super().__init__(message)

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, _message):
        raise CliError("CLI_ARGUMENT_INVALID", "Invalid commerce command arguments.")


def find_release_unit(script_path=None):
    """Find adapter.json without relying on the current working directory."""
    script = pathlib.Path(script_path or __file__).resolve()
    if len(script.parents) > 3:
        release_unit = script.parents[3]
        if (release_unit / "adapter.json").is_file():
            return release_unit
    raise CliError(
        "CLI_CONFIGURATION_INVALID",
        "The Codex release-unit adapter could not be located.",
    )


def load_source(release_unit):
    try:
        adapter = json.loads(
            (release_unit / "adapter.json").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise CliError(
            "CLI_CONFIGURATION_INVALID",
            "The Codex release-unit adapter is invalid.",
        ) from None
    if (
        not isinstance(adapter, dict)
        or adapter.get("ecosystem") != EXPECTED_ECOSYSTEM
        or type(adapter.get("source")) is not int
        or adapter["source"] != EXPECTED_SOURCE
    ):
        raise CliError(
            "CLI_CONFIGURATION_INVALID",
            "The Codex release-unit adapter is invalid.",
        )
    return adapter["source"]


def find_runtime(script_path, release_unit):
    script = pathlib.Path(script_path).resolve()
    skill_root = script.parent.parent
    bundled = skill_root / "core" / "runtime"
    if (bundled / "commerce_client.py").is_file():
        return bundled
    # Source-checkout execution is a development convenience, never a fallback
    # from a broken installed package to another checkout's shared runtime.
    repository = release_unit.parent.parent
    if release_unit.parent.name == "ecosystems" and (repository / "scripts/build-dist.mjs").is_file():
        source_runtime = repository / "shared" / "core" / "runtime"
        if (source_runtime / "commerce_client.py").is_file():
            return source_runtime
    raise CliError(
        "CLI_RUNTIME_UNAVAILABLE",
        "The bundled Lux3D commerce runtime could not be located.",
    )


def load_runtime(runtime_root):
    module_path = runtime_root / "commerce_client.py"
    module_name = "_lux3d_codex_commerce_client"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise CliError(
            "CLI_RUNTIME_UNAVAILABLE",
            "The bundled Lux3D commerce runtime could not be loaded.",
        )
    module = importlib.util.module_from_spec(spec)
    inserted = str(runtime_root)
    sys.path.insert(0, inserted)
    try:
        # Keep the CLI's stderr machine-readable even when the host has a
        # mismatched optional requests dependency set.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            spec.loader.exec_module(module)
    except ModuleNotFoundError as exc:
        if exc.name in {"requests", "urllib3", "certifi", "charset_normalizer", "idna"}:
            raise CliError(
                "CLI_DEPENDENCY_MISSING",
                "Lux3D Python dependencies are missing. Run scripts/setup_runtime.py "
                "from this installed Skill and retry with the returned Python interpreter.",
            ) from None
        raise CliError(
            "CLI_RUNTIME_UNAVAILABLE",
            "The bundled Lux3D commerce runtime could not be loaded.",
        ) from None
    except (ImportError, OSError):
        raise CliError(
            "CLI_RUNTIME_UNAVAILABLE",
            "The bundled Lux3D commerce runtime could not be loaded.",
        ) from None
    finally:
        if sys.path and sys.path[0] == inserted:
            sys.path.pop(0)
    return module


def load_items(path, runtime):
    try:
        with pathlib.Path(path).expanduser().open("rb") as stream:
            data = stream.read(runtime.MAX_REQUEST_BYTES + 1)
        if len(data) > runtime.MAX_REQUEST_BYTES:
            raise runtime.CommerceError("PRICING_REQUEST_INVALID")
        text = data.decode("utf-8-sig")
    except (OSError, UnicodeError):
        raise CliError(
            "CLI_ITEMS_UNAVAILABLE",
            "The quote items file could not be read as UTF-8 JSON.",
        ) from None
    parsed = runtime.load_items_json(text)
    return runtime.normalize_items(parsed)


def build_parser():
    parser = SafeArgumentParser(
        description="Read live Lux3D account facts or quote a complete call plan."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    balance = commands.add_parser("balance", help="Read the current account snapshot.")
    balance.add_argument("--region", required=True, choices=("cn", "international"))

    quote = commands.add_parser("quote", help="Quote a complete OpenAPI call plan.")
    quote.add_argument("--region", required=True, choices=("cn", "international"))
    quote.add_argument(
        "--items",
        required=True,
        metavar="FILE",
        help="UTF-8 JSON file containing the sequence-keyed items map.",
    )
    return parser


def execute(args, runtime, source):
    items = load_items(args.items, runtime) if args.command == "quote" else None
    client = runtime.CommerceClient(source=source)
    try:
        account = client.get_account(region=args.region)
        if args.command == "balance":
            return account
        quote = client.create_quote(
            region=args.region,
            unique_id=account["uniqueId"],
            items=items,
        )
        return {"account": account, "quote": quote}
    finally:
        client.close()


def error_dict(error, commerce_error_type=None):
    if commerce_error_type is not None and isinstance(error, commerce_error_type):
        return error.to_dict()
    if isinstance(error, CliError):
        return error.to_dict()
    return {
        "code": "CLI_INTERNAL_ERROR",
        "message": "The commerce command failed safely.",
        "retryable": False,
    }


def main(argv=None):
    runtime = None
    try:
        args = build_parser().parse_args(argv)
        release_unit = find_release_unit()
        source = load_source(release_unit)
        runtime_root = find_runtime(__file__, release_unit)
        runtime = load_runtime(runtime_root)
        result = execute(args, runtime, source)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as exc:
        commerce_error_type = getattr(runtime, "CommerceError", None)
        payload = error_dict(exc, commerce_error_type)
        print(json.dumps({"error": payload}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
