#!/usr/bin/env python3
"""Portable Common CLI for live account facts and complete plan quotes."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import warnings


_identity_path = Path(__file__).with_name("host_identity.py")
_source_root = Path(__file__).resolve().parents[1]
if (not _identity_path.is_file() and _source_root.parts[-3:] == ("ecosystems", "common", "skill")
        and not (_source_root / "adapter.json").exists() and not (_source_root / "build-info.json").exists()
        and (_source_root.parents[2] / "release-manifest.json").is_file()):
    _identity_path = _source_root.parents[2] / "shared/host-identity/lux3d/scripts/host_identity.py"
_spec = importlib.util.spec_from_file_location("_lux3d_common_host_identity", _identity_path)
identity_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(identity_support)
CliError = identity_support.CliError
find_skill_root = identity_support.find_skill_root
find_runtime = identity_support.find_runtime


def load_runtime(runtime_root):
    module_name = "_lux3d_common_commerce_client"
    spec = importlib.util.spec_from_file_location(module_name, runtime_root / "commerce_client.py")
    if spec is None or spec.loader is None:
        raise CliError("CLI_RUNTIME_UNAVAILABLE", "The bundled commerce runtime could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    # Internal imports must resolve to this package, even when the calling
    # process previously imported another Lux3D installation.
    internal = {path.stem for path in runtime_root.glob("*.py")}
    saved = {name: sys.modules.pop(name) for name in internal if name in sys.modules}
    sys.path.insert(0, str(runtime_root))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            spec.loader.exec_module(module)
    except ModuleNotFoundError as exc:
        if exc.name in {"requests", "urllib3", "certifi", "charset_normalizer", "idna"}:
            raise CliError("CLI_DEPENDENCY_MISSING", "Run scripts/setup_runtime.py and retry with its returned Python interpreter.") from None
        raise CliError("CLI_RUNTIME_UNAVAILABLE", "The bundled commerce runtime could not be loaded.") from None
    except (ImportError, OSError):
        raise CliError("CLI_RUNTIME_UNAVAILABLE", "The bundled commerce runtime could not be loaded.") from None
    finally:
        sys.path.pop(0)
        for name in internal:
            sys.modules.pop(name, None)
        sys.modules.update(saved)
    return module


def load_items(path, runtime):
    try:
        with Path(path).expanduser().open("rb") as stream:
            data = stream.read(runtime.MAX_REQUEST_BYTES + 1)
        if len(data) > runtime.MAX_REQUEST_BYTES:
            raise runtime.CommerceError("PRICING_REQUEST_INVALID")
        encoded = data.decode("utf-8-sig")
    except (OSError, UnicodeError):
        raise CliError("CLI_ITEMS_UNAVAILABLE", "The quote items file could not be read as UTF-8 JSON.") from None
    return runtime.normalize_items(runtime.load_items_json(encoded))


def add_metadata_arguments(parser):
    """Accept known collection metadata supplied by the host agent. Author: yinjie."""
    parser.add_argument("--model-name", metavar="NAME", help="Actual host model supplied by the agent when known.")
    parser.add_argument("--client-region", metavar="REGION", help="Known client location; independent of the service region.")


def build_parser():
    parser = identity_support.SafeArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("balance", "quote"):
        child = commands.add_parser(command)
        child.add_argument("--host-name", metavar="NAME", help="Actual application name automatically supplied by the host agent.")
        child.add_argument("--region", required=True, choices=identity_support.REGIONS, help="Explicit service region.")
        if command == "quote":
            add_metadata_arguments(child)
            child.add_argument("--items", required=True, metavar="FILE")
            child.add_argument("--review", metavar="FILE")
            child.add_argument("--journal", metavar="FILE")
    for name in ("init", "report", "feedback", "retry"):
        child = commands.add_parser(name)
        child.add_argument("--region", required=True, choices=("cn", "international"))
        child.add_argument("--journal", required=True, metavar="FILE")
        if name != "retry":
            add_metadata_arguments(child)
        if name == "retry":
            child.add_argument("--kind", required=True, choices=("report", "feedback"))
            child.add_argument("--request-id", required=True)
        elif name != "init":
            child.add_argument("--request", required=True, metavar="FILE")
        child.add_argument("--host-name", metavar="NAME")
    return parser


def execute(args, runtime, host):
    region = identity_support.select_region(args.region)
    items = load_items(args.items, runtime) if args.command == "quote" else None
    identity = {"source": host["source"]}
    if host["source"] == identity_support.SOURCE:
        identity["agent_name"] = host["agentName"]
    client = runtime.CommerceClient(**identity)
    try:
        if args.command in {"init", "report", "feedback", "retry"}:
            return runtime.collection_support.execute_command(
                args, client, runtime.load_items_json, runtime.MAX_REQUEST_BYTES,
                error_type=runtime.CommerceError)
        review_options = {}
        if getattr(args, "review", None) or getattr(args, "journal", None):
            review_options["review"] = runtime.collection_support.load_review(
                args, client, runtime.load_items_json, runtime.MAX_REQUEST_BYTES,
                error_type=runtime.CommerceError)
        account = client.get_account(region=region)
        if args.command == "balance":
            return account
        if not review_options.get("review"):
            try:
                metadata = runtime.collection_support.command_metadata(args)
            except (TypeError, ValueError):
                raise runtime.CommerceError("COLLECTION_REQUEST_INVALID") from None
            if metadata:
                review_options["context"] = metadata
        quote = client.create_quote(region=region, unique_id=account["uniqueId"], items=items, **review_options)
        return {"account": account, "quote": quote}
    finally:
        client.close()


def main(argv=None):
    runtime = None
    try:
        args = build_parser().parse_args(argv)
        skill = find_skill_root(__file__)
        identity_support.load_adapter(skill)
        host = identity_support.resolve_host_identity(host_name=args.host_name)
        identity_support.select_region(args.region)
        runtime = load_runtime(find_runtime(__file__, skill))
        result = execute(args, runtime, host)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as exc:
        if isinstance(exc, CliError) or (runtime and isinstance(exc, runtime.CommerceError)):
            error = exc.to_dict()
        else:
            error = {"code": "CLI_INTERNAL_ERROR", "message": "The commerce command failed safely.", "retryable": False}
        print(json.dumps({"error": error}, ensure_ascii=True), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
