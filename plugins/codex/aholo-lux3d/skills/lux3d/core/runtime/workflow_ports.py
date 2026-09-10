"""Platform-neutral service boundaries consumed by the shared workflow."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from workflow_contracts import (
    SubmissionDecision,
    SubmissionIntent,
    SubmissionReservation,
    SubmissionVerification,
)


class AccountPort(Protocol):
    """Account adapter bound to one immutable ecosystem client source."""

    source: int

    def get_account(self, *, region: str, account_ref: str | None = None) -> Mapping[str, Any]:
        ...


class QuotePort(Protocol):
    """Quote adapter that injects its immutable source into the request body."""

    source: int

    def create_quote(
        self,
        *,
        region: str,
        unique_id: str,
        items: Mapping[str, Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        ...


class QuoteVerificationPort(Protocol):
    def verify_submission(
        self, intent: SubmissionIntent
    ) -> SubmissionVerification:
        ...


class SubmissionGate(Protocol):
    def authorize(self, intent: SubmissionIntent) -> SubmissionDecision:
        ...


class SubmissionRegistryPort(Protocol):
    def reserve(
        self, intent: SubmissionIntent
    ) -> SubmissionReservation:
        ...

    def finalize(
        self,
        intent: SubmissionIntent,
        *,
        outcome: str,
        task_id: str | None = None,
    ) -> None:
        ...

    def lookup(self, *, unique_id: str, request_key: str) -> Mapping[str, Any] | None:
        ...

    def reconcile(
        self, *, unique_id: str, request_key: str, task_id: str
    ) -> None:
        ...


class GenerationPort(Protocol):
    def context(self) -> Mapping[str, str]:
        ...

    def submit(self, request: Mapping[str, Any]) -> str:
        ...

    def query(
        self,
        task_id: str,
        *,
        region: str,
        max_attempts: int,
        interval: float,
        output_slots: tuple[str, ...] | None,
    ) -> Any:
        ...

    def download(self, url: str, output_path: str) -> int:
        ...


class AssemblyPort(Protocol):
    def assemble(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        ...
