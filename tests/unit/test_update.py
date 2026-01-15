"""Unit tests for update command models and service methods."""

from pathlib import Path

import pytest

from issue_workflow.models.update import FileChangeInfo, FileChangeType, UpdateResult
from issue_workflow.services.template import TemplateService


class TestFileChangeType:
    """Tests for FileChangeType enum (T009)."""

    def test_added_value(self) -> None:
        """Test ADDED enum value."""
        assert FileChangeType.ADDED.value == "added"

    def test_updated_value(self) -> None:
        """Test UPDATED enum value."""
        assert FileChangeType.UPDATED.value == "updated"

    def test_deleted_value(self) -> None:
        """Test DELETED enum value."""
        assert FileChangeType.DELETED.value == "deleted"

    def test_unchanged_value(self) -> None:
        """Test UNCHANGED enum value."""
        assert FileChangeType.UNCHANGED.value == "unchanged"


class TestFileChangeInfo:
    """Tests for FileChangeInfo dataclass."""

    def test_creation_with_required_fields(self) -> None:
        """Test creating FileChangeInfo with required fields."""
        info = FileChangeInfo(
            path=Path(".claude/commands/test.md"),
            change_type=FileChangeType.ADDED,
        )
        assert info.path == Path(".claude/commands/test.md")
        assert info.change_type == FileChangeType.ADDED
        assert info.source_path is None

    def test_creation_with_source_path(self) -> None:
        """Test creating FileChangeInfo with source path."""
        info = FileChangeInfo(
            path=Path(".claude/commands/test.md"),
            change_type=FileChangeType.UPDATED,
            source_path=Path("/source/commands/test.md"),
        )
        assert info.source_path == Path("/source/commands/test.md")

    def test_is_frozen(self) -> None:
        """Test FileChangeInfo is immutable."""
        info = FileChangeInfo(
            path=Path(".claude/commands/test.md"),
            change_type=FileChangeType.ADDED,
        )
        with pytest.raises(AttributeError):
            info.path = Path("other.md")  # type: ignore[misc]


class TestUpdateResult:
    """Tests for UpdateResult dataclass (T008)."""

    def test_default_values(self) -> None:
        """Test UpdateResult default values."""
        result = UpdateResult()
        assert result.commands_changes == []
        assert result.skills_changes == []
        assert result.errors == []
        assert result.dry_run is False

    def test_added_count_empty(self) -> None:
        """Test added_count with no changes."""
        result = UpdateResult()
        assert result.added_count == 0

    def test_added_count_with_changes(self) -> None:
        """Test added_count with added files."""
        result = UpdateResult(
            commands_changes=[
                FileChangeInfo(
                    path=Path("a.md"),
                    change_type=FileChangeType.ADDED,
                    source_path=Path("s/a.md"),
                ),
                FileChangeInfo(
                    path=Path("b.md"),
                    change_type=FileChangeType.UPDATED,
                    source_path=Path("s/b.md"),
                ),
            ],
            skills_changes=[
                FileChangeInfo(
                    path=Path("skill/"),
                    change_type=FileChangeType.ADDED,
                    source_path=Path("s/skill/"),
                ),
            ],
        )
        assert result.added_count == 2

    def test_updated_count(self) -> None:
        """Test updated_count property."""
        result = UpdateResult(
            commands_changes=[
                FileChangeInfo(
                    path=Path("a.md"),
                    change_type=FileChangeType.UPDATED,
                    source_path=Path("s/a.md"),
                ),
            ],
        )
        assert result.updated_count == 1

    def test_deleted_count(self) -> None:
        """Test deleted_count property."""
        result = UpdateResult(
            commands_changes=[
                FileChangeInfo(
                    path=Path("a.md"),
                    change_type=FileChangeType.DELETED,
                ),
            ],
        )
        assert result.deleted_count == 1

    def test_has_changes_true(self) -> None:
        """Test has_changes returns True when there are changes."""
        result = UpdateResult(
            commands_changes=[
                FileChangeInfo(
                    path=Path("a.md"),
                    change_type=FileChangeType.ADDED,
                    source_path=Path("s/a.md"),
                ),
            ],
        )
        assert result.has_changes is True

    def test_has_changes_false_empty(self) -> None:
        """Test has_changes returns False when no changes."""
        result = UpdateResult()
        assert result.has_changes is False

    def test_has_changes_false_only_deleted(self) -> None:
        """Test has_changes returns False when only deleted (warning only)."""
        result = UpdateResult(
            commands_changes=[
                FileChangeInfo(
                    path=Path("a.md"),
                    change_type=FileChangeType.DELETED,
                ),
            ],
        )
        assert result.has_changes is False

    def test_has_errors_true(self) -> None:
        """Test has_errors returns True when there are errors."""
        result = UpdateResult(errors=[(Path("a.md"), "Permission denied")])
        assert result.has_errors is True

    def test_has_errors_false(self) -> None:
        """Test has_errors returns False when no errors."""
        result = UpdateResult()
        assert result.has_errors is False

    def test_success_true(self) -> None:
        """Test success returns True when no errors."""
        result = UpdateResult()
        assert result.success is True

    def test_success_false(self) -> None:
        """Test success returns False when there are errors."""
        result = UpdateResult(errors=[(Path("a.md"), "Error")])
        assert result.success is False

    def test_dry_run_flag(self) -> None:
        """Test dry_run flag is stored correctly."""
        result = UpdateResult(dry_run=True)
        assert result.dry_run is True


class TestUpdateCommands:
    """Tests for TemplateService.update_commands method (T010)."""

    def test_detects_added_files(self, tmp_path: Path) -> None:
        """Test detecting newly added command files."""
        # Setup source with new file
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "new-command.md").write_text("# New Command")

        # Setup target without the file
        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)

        # Create service with mocked source dir
        service = TemplateService()
        # Mock the source directory
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            assert result.added_count == 1
            assert result.commands_changes[0].change_type == FileChangeType.ADDED
        finally:
            template_module.get_commands_source_dir = original_func

    def test_detects_updated_files(self, tmp_path: Path) -> None:
        """Test detecting updated command files."""
        # Setup source with modified file
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "existing.md").write_text("# Updated Content")

        # Setup target with old version
        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)
        (commands_target / "existing.md").write_text("# Old Content")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            assert result.updated_count == 1
            assert result.commands_changes[0].change_type == FileChangeType.UPDATED
        finally:
            template_module.get_commands_source_dir = original_func

    def test_detects_deleted_files(self, tmp_path: Path) -> None:
        """Test detecting files in target but not in source."""
        # Setup empty source
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)

        # Setup target with extra file
        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)
        (commands_target / "extra.md").write_text("# Extra")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            assert result.deleted_count == 1
            assert result.commands_changes[0].change_type == FileChangeType.DELETED
        finally:
            template_module.get_commands_source_dir = original_func

    def test_applies_changes_when_not_dry_run(self, tmp_path: Path) -> None:
        """Test files are actually updated when dry_run=False."""
        # Setup source with new file
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "new-command.md").write_text("# New Command Content")

        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=False)
            assert result.added_count == 1
            # Verify file was actually copied
            assert (commands_target / "new-command.md").exists()
            assert (commands_target / "new-command.md").read_text() == "# New Command Content"
        finally:
            template_module.get_commands_source_dir = original_func

    def test_no_changes_when_identical(self, tmp_path: Path) -> None:
        """Test no changes detected when files are identical."""
        # Setup source and target with identical file
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "same.md").write_text("# Same Content")

        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)
        (commands_target / "same.md").write_text("# Same Content")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            assert result.added_count == 0
            assert result.updated_count == 0
            assert result.has_changes is False
        finally:
            template_module.get_commands_source_dir = original_func


class TestUpdateSkills:
    """Tests for TemplateService.update_skills method (T011)."""

    def test_detects_added_directories(self, tmp_path: Path) -> None:
        """Test detecting newly added skill directories."""
        # Setup source with new skill directory
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)
        (source_dir / "new-skill").mkdir()
        (source_dir / "new-skill" / "skill.md").write_text("# New Skill")

        # Setup target without the directory
        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        skills_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        try:
            result = service.update_skills(target_dir, dry_run=True)
            assert result.added_count == 1
            assert result.skills_changes[0].change_type == FileChangeType.ADDED
        finally:
            template_module.get_skills_source_dir = original_func

    def test_detects_updated_directories(self, tmp_path: Path) -> None:
        """Test detecting updated skill directories."""
        # Setup source with modified skill
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)
        (source_dir / "existing-skill").mkdir()
        (source_dir / "existing-skill" / "skill.md").write_text("# Updated Skill")

        # Setup target with old version
        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        (skills_target / "existing-skill").mkdir(parents=True)
        (skills_target / "existing-skill" / "skill.md").write_text("# Old Skill")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        try:
            result = service.update_skills(target_dir, dry_run=True)
            assert result.updated_count == 1
            assert result.skills_changes[0].change_type == FileChangeType.UPDATED
        finally:
            template_module.get_skills_source_dir = original_func

    def test_detects_deleted_directories(self, tmp_path: Path) -> None:
        """Test detecting directories in target but not in source."""
        # Setup empty source
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)

        # Setup target with extra directory
        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        (skills_target / "extra-skill").mkdir(parents=True)
        (skills_target / "extra-skill" / "skill.md").write_text("# Extra")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        try:
            result = service.update_skills(target_dir, dry_run=True)
            assert result.deleted_count == 1
            assert result.skills_changes[0].change_type == FileChangeType.DELETED
        finally:
            template_module.get_skills_source_dir = original_func

    def test_applies_changes_when_not_dry_run(self, tmp_path: Path) -> None:
        """Test directories are actually updated when dry_run=False."""
        # Setup source with new skill
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)
        (source_dir / "new-skill").mkdir()
        (source_dir / "new-skill" / "skill.md").write_text("# New Skill Content")

        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        skills_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        try:
            result = service.update_skills(target_dir, dry_run=False)
            assert result.added_count == 1
            # Verify directory was actually copied
            assert (skills_target / "new-skill").exists()
            assert (skills_target / "new-skill" / "skill.md").read_text() == "# New Skill Content"
        finally:
            template_module.get_skills_source_dir = original_func


class TestDryRunCommands:
    """Tests for dry-run flag in update_commands (T019)."""

    def test_dry_run_does_not_create_files(self, tmp_path: Path) -> None:
        """Test dry-run does not create files."""
        # Setup source with new file
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "new-command.md").write_text("# New Command")

        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            # Changes are detected
            assert result.added_count == 1
            assert result.dry_run is True
            # But file is NOT created
            assert not (commands_target / "new-command.md").exists()
        finally:
            template_module.get_commands_source_dir = original_func

    def test_dry_run_does_not_update_files(self, tmp_path: Path) -> None:
        """Test dry-run does not update existing files."""
        # Setup source with modified file
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "existing.md").write_text("# Updated Content")

        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)
        (commands_target / "existing.md").write_text("# Original Content")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            # Changes are detected
            assert result.updated_count == 1
            # But file is NOT updated
            assert (commands_target / "existing.md").read_text() == "# Original Content"
        finally:
            template_module.get_commands_source_dir = original_func


class TestDryRunSkills:
    """Tests for dry-run flag in update_skills (T020)."""

    def test_dry_run_does_not_create_directories(self, tmp_path: Path) -> None:
        """Test dry-run does not create directories."""
        # Setup source with new skill
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)
        (source_dir / "new-skill").mkdir()
        (source_dir / "new-skill" / "skill.md").write_text("# New Skill")

        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        skills_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        try:
            result = service.update_skills(target_dir, dry_run=True)
            # Changes are detected
            assert result.added_count == 1
            assert result.dry_run is True
            # But directory is NOT created
            assert not (skills_target / "new-skill").exists()
        finally:
            template_module.get_skills_source_dir = original_func

    def test_dry_run_does_not_update_directories(self, tmp_path: Path) -> None:
        """Test dry-run does not update existing directories."""
        # Setup source with modified skill
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)
        (source_dir / "existing-skill").mkdir()
        (source_dir / "existing-skill" / "skill.md").write_text("# Updated Skill")

        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        (skills_target / "existing-skill").mkdir(parents=True)
        (skills_target / "existing-skill" / "skill.md").write_text("# Original Skill")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        try:
            result = service.update_skills(target_dir, dry_run=True)
            # Changes are detected
            assert result.updated_count == 1
            # But directory is NOT updated
            assert (skills_target / "existing-skill" / "skill.md").read_text() == "# Original Skill"
        finally:
            template_module.get_skills_source_dir = original_func


class TestEdgeCases:
    """Tests for edge cases (T025)."""

    def test_source_directory_not_found_commands(self, tmp_path: Path) -> None:
        """Test error when commands source directory does not exist."""
        from issue_workflow.services.template import SourceDirectoryNotFoundError

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: tmp_path / "nonexistent"

        try:
            with pytest.raises(SourceDirectoryNotFoundError):
                service.update_commands(tmp_path / ".claude")
        finally:
            template_module.get_commands_source_dir = original_func

    def test_source_directory_not_found_skills(self, tmp_path: Path) -> None:
        """Test error when skills source directory does not exist."""
        from issue_workflow.services.template import SourceDirectoryNotFoundError

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: tmp_path / "nonexistent"

        try:
            with pytest.raises(SourceDirectoryNotFoundError):
                service.update_skills(tmp_path / ".claude")
        finally:
            template_module.get_skills_source_dir = original_func

    def test_empty_source_directory(self, tmp_path: Path) -> None:
        """Test handling of empty source directory."""
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)

        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            assert result.added_count == 0
            assert result.updated_count == 0
            assert result.has_changes is False
        finally:
            template_module.get_commands_source_dir = original_func

    def test_multiple_changes_combined(self, tmp_path: Path) -> None:
        """Test result correctly combines multiple change types."""
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "new.md").write_text("# New")
        (source_dir / "updated.md").write_text("# Updated Content")

        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)
        (commands_target / "updated.md").write_text("# Old Content")
        (commands_target / "deleted.md").write_text("# Deleted")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            assert result.added_count == 1
            assert result.updated_count == 1
            assert result.deleted_count == 1
            assert result.has_changes is True
        finally:
            template_module.get_commands_source_dir = original_func
