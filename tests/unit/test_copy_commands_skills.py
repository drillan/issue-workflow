"""Unit tests for skills and agents copy functionality."""

from pathlib import Path

import pytest

from issue_workflow.services.template import (
    SourceDirectoryNotFoundError,
    TemplateService,
    get_agents_source_dir,
    get_skills_source_dir,
)


class TestCopySkills:
    """Tests for copy_skills functionality in TemplateService."""

    @pytest.fixture
    def template_service(self) -> TemplateService:
        """Create template service instance."""
        return TemplateService()

    @pytest.fixture
    def target_dir(self, tmp_path: Path) -> Path:
        """Create target .claude directory."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        return claude_dir

    def test_copy_skills_creates_skills_directory(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_skills creates .claude/skills directory."""
        template_service.copy_skills(target_dir)

        skills_dir = target_dir / "skills"
        assert skills_dir.exists()
        assert skills_dir.is_dir()

    def test_copy_skills_copies_all_skill_directories(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_skills copies all skill directories with SKILL.md."""
        template_service.copy_skills(target_dir)

        skills_dir = target_dir / "skills"
        expected_skills = [
            "tdd-workflow",
            "code-quality-gate",
            "issue-reporter",
            "doc-updater",
            "start-issue",
            "commit-push-pr",
            "merge-pr",
            "respond-review",
            "review-pr-comments",
            "add-worktree",
        ]
        for skill in expected_skills:
            skill_dir = skills_dir / skill
            assert skill_dir.exists(), f"Skill directory {skill} should exist"
            assert (skill_dir / "SKILL.md").exists(), f"SKILL.md in {skill} should exist"

    def test_copy_skills_preserves_existing_skills(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_skills preserves existing skill directories."""
        skills_dir = target_dir / "skills"
        existing_skill = skills_dir / "existing-skill"
        existing_skill.mkdir(parents=True)
        existing_file = existing_skill / "SKILL.md"
        existing_file.write_text("# Existing Skill")

        template_service.copy_skills(target_dir)

        assert existing_file.exists()
        assert existing_file.read_text() == "# Existing Skill"

    def test_copy_skills_does_not_overwrite_customized_builtin(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that user-customized builtin skills are not overwritten."""
        skills_dir = target_dir / "skills"
        customized_skill = skills_dir / "tdd-workflow"
        customized_skill.mkdir(parents=True)
        customized_file = customized_skill / "SKILL.md"
        customized_content = "# User Customized TDD Workflow\n\nMy custom TDD process."
        customized_file.write_text(customized_content)

        template_service.copy_skills(target_dir)

        assert customized_file.exists()
        assert customized_file.read_text() == customized_content

    def test_copy_skills_returns_skills_directory_path(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_skills returns the skills directory path."""
        result = template_service.copy_skills(target_dir)

        assert result == target_dir / "skills"


class TestGenerateAllWithSkillsAndAgents:
    """Tests for generate_all including skills and agents."""

    @pytest.fixture
    def template_service(self) -> TemplateService:
        """Create template service instance."""
        return TemplateService()

    @pytest.fixture
    def target_dir(self, tmp_path: Path) -> Path:
        """Create target .claude directory."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        return claude_dir

    def test_generate_all_includes_skills(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that generate_all copies skills and agents."""
        from issue_workflow.services.preset_loader import PresetLoader

        loader = PresetLoader()
        preset = loader.load("python")

        generated = template_service.generate_all(preset, target_dir)

        skills_dir = target_dir / "skills"
        agents_dir = target_dir / "agents"
        assert skills_dir in generated
        assert agents_dir in generated
        assert skills_dir.exists()
        assert agents_dir.exists()

    def test_generate_all_does_not_create_plugin_directory(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that generate_all does not create .claude/plugin directory."""
        from issue_workflow.services.preset_loader import PresetLoader

        loader = PresetLoader()
        preset = loader.load("python")

        template_service.generate_all(preset, target_dir)

        plugin_dir = target_dir / "plugin"
        assert not plugin_dir.exists()

    def test_generate_all_does_not_create_commands_directory(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that generate_all does not create .claude/commands directory."""
        from issue_workflow.services.preset_loader import PresetLoader

        loader = PresetLoader()
        preset = loader.load("python")

        template_service.generate_all(preset, target_dir)

        commands_dir = target_dir / "commands"
        assert not commands_dir.exists()


class TestSourceDirectoryHelpers:
    """Tests for get_skills_source_dir and get_agents_source_dir helper functions."""

    def test_get_skills_source_dir_returns_valid_path(self) -> None:
        """Test that get_skills_source_dir returns a valid Path."""
        result = get_skills_source_dir()

        assert isinstance(result, Path)
        assert result.name == "skills"
        assert result.exists()
        assert result.is_dir()

    def test_get_skills_source_dir_contains_skill_directories(self) -> None:
        """Test that the skills source dir contains expected skill directories."""
        skills_dir = get_skills_source_dir()

        expected_skills = [
            "tdd-workflow",
            "code-quality-gate",
            "issue-reporter",
            "doc-updater",
            "start-issue",
            "commit-push-pr",
            "merge-pr",
            "respond-review",
            "review-pr-comments",
            "add-worktree",
        ]
        for skill_name in expected_skills:
            skill_path = skills_dir / skill_name
            assert skill_path.exists(), f"Expected {skill_name} in skills dir"
            assert skill_path.is_dir(), f"Expected {skill_name} to be a directory"

    def test_get_agents_source_dir_returns_valid_path(self) -> None:
        """Test that get_agents_source_dir returns a valid Path (T074)."""
        result = get_agents_source_dir()

        assert isinstance(result, Path)
        assert result.name == "agents"
        assert result.exists()
        assert result.is_dir()

    def test_get_agents_source_dir_contains_agent_files(self) -> None:
        """Test that the agents source dir contains expected agent files (T074)."""
        agents_dir = get_agents_source_dir()

        expected_agents = [
            "git-committer.md",
            "pr-creator.md",
            "pr-merger.md",
            "branch-cleaner.md",
        ]
        for filename in expected_agents:
            assert (agents_dir / filename).exists(), f"Expected {filename} in agents dir"


class TestCopyAgents:
    """Tests for copy_agents functionality in TemplateService (T075)."""

    @pytest.fixture
    def template_service(self) -> TemplateService:
        """Create template service instance."""
        return TemplateService()

    @pytest.fixture
    def target_dir(self, tmp_path: Path) -> Path:
        """Create target .claude directory."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        return claude_dir

    def test_copy_agents_creates_agents_directory(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_agents creates .claude/agents directory."""
        template_service.copy_agents(target_dir)

        agents_dir = target_dir / "agents"
        assert agents_dir.exists()
        assert agents_dir.is_dir()

    def test_copy_agents_copies_all_agent_files(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_agents copies all agent markdown files."""
        template_service.copy_agents(target_dir)

        agents_dir = target_dir / "agents"
        expected_agents = [
            "git-committer.md",
            "pr-creator.md",
            "pr-merger.md",
            "branch-cleaner.md",
        ]
        for agent in expected_agents:
            assert (agents_dir / agent).exists(), f"Agent {agent} should exist"

    def test_copy_agents_preserves_existing_agents(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_agents preserves existing agent files."""
        agents_dir = target_dir / "agents"
        agents_dir.mkdir(parents=True)
        existing_file = agents_dir / "existing-agent.md"
        existing_file.write_text("# Existing Agent")

        template_service.copy_agents(target_dir)

        assert existing_file.exists()
        assert existing_file.read_text() == "# Existing Agent"

    def test_copy_agents_does_not_overwrite_customized_builtin(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that user-customized builtin agents are not overwritten."""
        agents_dir = target_dir / "agents"
        agents_dir.mkdir(parents=True)
        customized_file = agents_dir / "git-committer.md"
        customized_content = "# User Customized Git Committer\n\nMy custom workflow."
        customized_file.write_text(customized_content)

        template_service.copy_agents(target_dir)

        assert customized_file.exists()
        assert customized_file.read_text() == customized_content

    def test_copy_agents_returns_agents_directory_path(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_agents returns the agents directory path."""
        result = template_service.copy_agents(target_dir)

        assert result == target_dir / "agents"

    def test_copy_agents_raises_error_when_source_not_found(self, target_dir: Path) -> None:
        """Test that copy_agents raises SourceDirectoryNotFoundError when source missing."""
        import issue_workflow.services.template as template_module

        service = TemplateService()
        original_func = template_module.get_agents_source_dir
        template_module.get_agents_source_dir = lambda: target_dir / "nonexistent"

        try:
            with pytest.raises(SourceDirectoryNotFoundError):
                service.copy_agents(target_dir)
        finally:
            template_module.get_agents_source_dir = original_func
