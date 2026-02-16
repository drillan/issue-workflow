"""Tests for --force flag behavior in start-issue SKILL.md.

Validates that the --force flag definition in start-issue/SKILL.md
properly covers TDD user confirmation skipping (Issue #93).
"""

import re
from pathlib import Path

from issue_workflow.services.template import get_skills_source_dir


class TestStartIssueForceFlag:
    """Tests that --force flag in start-issue SKILL.md skips TDD confirmations."""

    def setup_method(self) -> None:
        """Read SKILL.md and extract Phase 4 section once per test."""
        skill_path = get_skills_source_dir() / "start-issue" / "SKILL.md"
        self.content = skill_path.read_text()
        phase4_match = re.search(
            r"(#### Phase 4.*?)(?=#### Phase 5|### Step 5|\Z)",
            self.content,
            re.DOTALL,
        )
        self.phase4 = phase4_match.group(1) if phase4_match else ""
        self.lower_phase4 = self.phase4.lower()

    def test_phase4_has_force_flag_instructions(self) -> None:
        """Phase 4 (TDD) must contain --force specific instructions."""
        assert self.phase4, "Phase 4 section must exist in start-issue SKILL.md"
        assert "force" in self.lower_phase4, (
            "Phase 4 (TDD) section must contain --force instructions"
        )

    def test_force_flag_skips_tdd_user_approval(self) -> None:
        """--force must skip TDD user approval/confirmation within Phase 4."""
        has_skip_approval = (
            "force" in self.lower_phase4
            and ("skip" in self.lower_phase4 or "without" in self.lower_phase4)
            and (
                "user approval" in self.lower_phase4
                or "user confirmation" in self.lower_phase4
                or "confirmation" in self.lower_phase4
            )
        )
        assert has_skip_approval, "Phase 4 must state that --force skips user approval/confirmation"

    def test_force_flag_enables_autonomous_tdd_cycle(self) -> None:
        """--force must enable autonomous Red-Green-Refactor in Phase 4."""
        has_autonomous = "force" in self.lower_phase4 and (
            "autonomous" in self.lower_phase4
            or "automatically" in self.lower_phase4
            or "without confirmation" in self.lower_phase4
            or "without user" in self.lower_phase4
        )
        assert has_autonomous, "Phase 4 must instruct autonomous TDD cycle completion with --force"

    def test_default_flow_preserves_user_confirmation(self) -> None:
        """Default flow (without --force) must preserve user confirmation."""
        has_default_confirmation = (
            "user approval" in self.lower_phase4
            or "user confirmation" in self.lower_phase4
            or "get approval" in self.lower_phase4
            or "ask" in self.lower_phase4
        )
        assert has_default_confirmation, (
            "Phase 4 must preserve user confirmation requirement in default flow"
        )

    def test_force_flag_description_in_arguments_table(self) -> None:
        """The --force description in Arguments table must reflect TDD skip."""
        lines = self.content.split("\n")
        force_line = None
        for line in lines:
            if "`--force`" in line and "|" in line:
                force_line = line
                break

        assert force_line is not None, "--force must be in the Arguments table"
        force_desc = force_line.lower()
        has_broader_desc = (
            "confirmation" in force_desc
            or "interactive" in force_desc
            or "non-interactive" in force_desc
        )
        assert has_broader_desc, (
            "--force description must mention confirmation/interactive skipping, "
            f"not just plan mode. Got: {force_line}"
        )

    def test_source_and_deployed_skill_md_are_in_sync(self) -> None:
        """Source and deployed SKILL.md copies must be identical."""
        deployed_path = Path(".claude/skills/start-issue/SKILL.md")
        assert deployed_path.exists(), "Deployed SKILL.md must exist at .claude/skills/start-issue/"

        source_path = get_skills_source_dir() / "start-issue" / "SKILL.md"
        assert source_path.read_text() == deployed_path.read_text(), (
            "Source and deployed SKILL.md copies have diverged. "
            "Update both files or run the copy command to sync."
        )
