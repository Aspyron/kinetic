from dataclasses import dataclass, field
from enum import Enum

from .errors import KineticError


class Severity(Enum):
    WARN = "WARN"
    ERROR = "ERROR"


@dataclass(frozen=True)
class SourceLocation:
    line: int
    column: int

    def render(self) -> str:
        return f"{self.line}:{self.column}"


@dataclass
class Diagnostic:
    severity: Severity
    message: str
    location: SourceLocation | None = None
    hint: str | None = None

    def render(self) -> str:
        prefix = f"kinetic: {self.severity.value.lower()}"
        if self.location is not None:
            prefix += f": {self.location.render()}"
        rendered = f"{prefix}: {self.message}"
        if self.hint is not None:
            rendered += f"\n  hint: {self.hint}"
        return rendered


class DiagnosticsError(KineticError):
    def __init__(self, diagnostic: Diagnostic):
        super().__init__(diagnostic.render())
        self.diagnostic = diagnostic


@dataclass
class Diagnostics:
    warnings: list[Diagnostic] = field(default_factory=list)

    def warn(
        self,
        message: str,
        location: SourceLocation | None = None,
        hint: str | None = None,
    ) -> None:
        diagnostic = Diagnostic(Severity.WARN, message, location, hint)
        key = (
            message,
            location.line if location else None,
            location.column if location else None,
        )
        seen = {
            (w.message, w.location.line if w.location else None,
             w.location.column if w.location else None)
            for w in self.warnings
        }
        if key not in seen:
            self.warnings.append(diagnostic)

    def error(
        self,
        message: str,
        location: SourceLocation | None = None,
        hint: str | None = None,
    ) -> DiagnosticsError:
        return DiagnosticsError(Diagnostic(Severity.ERROR, message, location, hint))

    def render_warnings(self) -> list[str]:
        return [warning.render() for warning in self.warnings]

    def summary(self) -> str:
        warning_count = len(self.warnings)
        parts: list[str] = []
        if warning_count:
            parts.append(
                f"{warning_count} warning{'s' if warning_count != 1 else ''}"
            )
        if not parts:
            return ""
        return "kinetic: " + ", ".join(parts) + " emitted"


@dataclass
class CompilationResult:
    llvm_ir: str
    diagnostics: Diagnostics
