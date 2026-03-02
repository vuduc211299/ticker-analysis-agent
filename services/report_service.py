from __future__ import annotations

import re

from schemas.report import ReportSection


def extract_report_sections(report_text: str) -> list[ReportSection]:
    lines = report_text.splitlines()
    sections: list[ReportSection] = []

    current_title: str | None = None
    current_lines: list[str] = []

    for raw_line in lines:
        match = re.match(r"^##\s+(.+)$", raw_line.strip())
        if match:
            if current_title is not None:
                sections.append(
                    ReportSection(
                        title=current_title,
                        content="\n".join(current_lines).strip(),
                    )
                )
            current_title = match.group(1).strip()
            current_lines = []
        else:
            if current_title is not None:
                current_lines.append(raw_line)

    if current_title is not None:
        sections.append(
            ReportSection(
                title=current_title,
                content="\n".join(current_lines).strip(),
            )
        )

    if not sections and report_text.strip():
        sections.append(ReportSection(title="Message", content=report_text.strip()))

    return sections
