"""Tests for --force flag behavior in start-issue SKILL.md.

Validates that the --force flag definition in start-issue/SKILL.md
properly covers TDD user confirmation skipping (Issue #93).
"""

import re

from issue_workflow.services.template import get_skills_source_dir


class TestStartIssueForceFlag:
    """Tests that --force flag in start-issue SKILL.md skips TDD confirmations."""

    def _read_skill(self, skill_name: str) -> str:
        """Read the SKILL.md content for a given skill."""
        skill_path = get_skills_source_dir() / skill_name / "SKILL.md"
        return skill_path.read_text()

    def _extract_phase4_section(self, content: str) -> str:
        """Extract Phase 4 (TDD) section from SKILL.md content."""
        # Find Phase 4 header and extract until Phase 5 or next ### header
        phase4_match = re.search(
            r"(#### Phase 4.*?)(?=#### Phase 5|### Step 5|\Z)",
            content,
            re.DOTALL,
        )
        if phase4_match:
            return phase4_match.group(1)
        return ""

    def test_phase4_has_force_flag_instructions(self) -> None:
        """Phase 4 (TDD) must contain --force specific instructions."""
        content = self._read_skill("start-issue")
        phase4 = self._extract_phase4_section(content)

        assert phase4, "Phase 4 section must exist in start-issue SKILL.md"
        assert "force" in phase4.lower(), "Phase 4 (TDD) section must contain --force instructions"

    def test_force_flag_skips_tdd_user_approval(self) -> None:
        """--force must skip TDD user approval/confirmation within Phase 4."""
        content = self._read_skill("start-issue")
        phase4 = self._extract_phase4_section(content)

        lower_phase4 = phase4.lower()
        # Phase 4 must have a conditional about --force skipping user approval
        has_skip_approval = (
            "force" in lower_phase4
            and ("skip" in lower_phase4 or "without" in lower_phase4)
            and (
                "user approval" in lower_phase4
                or "user confirmation" in lower_phase4
                or "confirmation" in lower_phase4
            )
        )
        assert has_skip_approval, "Phase 4 must state that --force skips user approval/confirmation"

    def test_force_flag_enables_autonomous_tdd_cycle(self) -> None:
        """--force must enable autonomous Red-Green-Refactor in Phase 4."""
        content = self._read_skill("start-issue")
        phase4 = self._extract_phase4_section(content)

        lower_phase4 = phase4.lower()
        has_autonomous = "force" in lower_phase4 and (
            "autonomous" in lower_phase4
            or "automatically" in lower_phase4
            or "without confirmation" in lower_phase4
            or "without user" in lower_phase4
        )
        assert has_autonomous, "Phase 4 must instruct autonomous TDD cycle completion with --force"

    def test_default_flow_preserves_user_confirmation(self) -> None:
        """Default flow (without --force) must preserve user confirmation."""
        content = self._read_skill("start-issue")
        phase4 = self._extract_phase4_section(content)

        lower_phase4 = phase4.lower()
        # Default flow must still mention user approval/confirmation
        has_default_confirmation = (
            "user approval" in lower_phase4
            or "user confirmation" in lower_phase4
            or "get approval" in lower_phase4
            or "ask" in lower_phase4
        )
        assert has_default_confirmation, (
            "Phase 4 must preserve user confirmation requirement in default flow"
        )

    def test_force_flag_description_in_arguments_table(self) -> None:
        """The --force description in Arguments table must reflect TDD skip."""
        content = self._read_skill("start-issue")
        lines = content.split("\n")
        force_line = None
        for line in lines:
            if "`--force`" in line and "|" in line:
                force_line = line
                break

        assert force_line is not None, "--force must be in the Arguments table"
        force_desc = force_line.lower()
        # Description should mention confirmation/interactive skipping (not just plan)
        has_broader_desc = (
            "confirmation" in force_desc
            or "interactive" in force_desc
            or "non-interactive" in force_desc
        )
        assert has_broader_desc, (
            "--force description must mention confirmation/interactive skipping, "
            f"not just plan mode. Got: {force_line}"
        )
