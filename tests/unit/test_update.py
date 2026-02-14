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

    def test_unchanged_value(self) -> None:
        """Test UNCHANGED enum value."""
        assert FileChangeType.UNCHANGED.value == "unchanged"


class TestFileChangeInfo:
    """Tests for FileChangeInfo dataclass."""

    def test_added_requires_source_path(self) -> None:
        """Test that ADDED change type requires source_path (Important #2)."""
        with pytest.raises(ValueError, match="source_path"):
            FileChangeInfo(
                path=Path(".claude/commands/test.md"),
                change_type=FileChangeType.ADDED,
                source_path=None,
            )

    def test_updated_requires_source_path(self) -> None:
        """Test that UPDATED change type requires source_path (Important #2)."""
        with pytest.raises(ValueError, match="source_path"):
            FileChangeInfo(
                path=Path(".claude/commands/test.md"),
                change_type=FileChangeType.UPDATED,
                source_path=None,
            )

    def test_added_with_source_path_succeeds(self) -> None:
        """Test that ADDED with source_path is valid."""
        info = FileChangeInfo(
            path=Path(".claude/commands/test.md"),
            change_type=FileChangeType.ADDED,
            source_path=Path("/source/commands/test.md"),
        )
        assert info.source_path == Path("/source/commands/test.md")

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
            change_type=FileChangeType.UNCHANGED,
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
        assert result.agents_changes == []
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

    def test_added_count_includes_agents_changes(self) -> None:
        """Test added_count includes agents_changes (T072)."""
        result = UpdateResult(
            commands_changes=[
                FileChangeInfo(
                    path=Path("a.md"),
                    change_type=FileChangeType.ADDED,
                    source_path=Path("s/a.md"),
                ),
            ],
            agents_changes=[
                FileChangeInfo(
                    path=Path("agent/"),
                    change_type=FileChangeType.ADDED,
                    source_path=Path("s/agent/"),
                ),
            ],
        )
        assert result.added_count == 2

    def test_updated_count_includes_agents_changes(self) -> None:
        """Test updated_count includes agents_changes (T072)."""
        result = UpdateResult(
            skills_changes=[
                FileChangeInfo(
                    path=Path("skill/"),
                    change_type=FileChangeType.UPDATED,
                    source_path=Path("s/skill/"),
                ),
            ],
            agents_changes=[
                FileChangeInfo(
                    path=Path("agent/"),
                    change_type=FileChangeType.UPDATED,
                    source_path=Path("s/agent/"),
                ),
            ],
        )
        assert result.updated_count == 2

    def test_has_changes_true_from_agents_only(self) -> None:
        """Test has_changes returns True when only agents_changes has changes."""
        result = UpdateResult(
            agents_changes=[
                FileChangeInfo(
                    path=Path("agent/"),
                    change_type=FileChangeType.ADDED,
                    source_path=Path("s/agent/"),
                ),
            ],
        )
        assert result.has_changes is True

    def test_agents_changes_unchanged_not_counted(self) -> None:
        """Test UNCHANGED agents_changes are not counted in added/updated."""
        result = UpdateResult(
            agents_changes=[
                FileChangeInfo(
                    path=Path("agent/"),
                    change_type=FileChangeType.UNCHANGED,
                ),
            ],
        )
        assert result.added_count == 0
        assert result.updated_count == 0
        assert result.has_changes is False


class TestUnmanagedFilesIgnored:
    """Tests for ignoring unmanaged files (#15).

    Issue: update command was displaying "not in toolkit, manual deletion required"
    for files that exist in target but not in source. These are user files or
    files from other tools and should be silently ignored.
    """

    def test_commands_ignores_unmanaged_files(self, tmp_path: Path) -> None:
        """Test that unmanaged command files are ignored."""
        # Setup empty source (no commands from toolkit)
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)

        # Setup target with user's custom command
        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)
        (commands_target / "my-custom-command.md").write_text("# My Custom Command")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            # Should NOT detect unmanaged files - no changes should be detected
            assert result.has_changes is False
        finally:
            template_module.get_commands_source_dir = original_func

    def test_skills_ignores_unmanaged_directories(self, tmp_path: Path) -> None:
        """Test that unmanaged skill directories are ignored."""
        # Setup empty source (no skills from toolkit)
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)

        # Setup target with user's custom skill (e.g., from speckit)
        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        (skills_target / "speckit.analyze").mkdir(parents=True)
        (skills_target / "speckit.analyze" / "skill.md").write_text("# Speckit Skill")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        try:
            result = service.update_skills(target_dir, dry_run=True)
            # Should NOT detect unmanaged directories - no changes should be detected
            assert result.has_changes is False
        finally:
            template_module.get_skills_source_dir = original_func

    def test_mixed_managed_and_unmanaged_files(self, tmp_path: Path) -> None:
        """Test that unmanaged files are ignored while managed files are detected."""
        # Setup source with one command
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "start-issue.md").write_text("# Start Issue")

        # Setup target with toolkit command (updated) and user's custom command
        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)
        (commands_target / "start-issue.md").write_text("# Old Start Issue")
        (commands_target / "speckit.analyze.md").write_text("# Speckit Command")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            # Should detect start-issue.md as updated
            assert result.updated_count == 1
            # Only one change (the update), unmanaged files are ignored
            assert len(result.commands_changes) == 1
            assert result.commands_changes[0].change_type == FileChangeType.UPDATED
        finally:
            template_module.get_commands_source_dir = original_func


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

    def test_ignores_unmanaged_files(self, tmp_path: Path) -> None:
        """Test that files in target but not in source are ignored (#15).

        Previously this test was 'test_detects_deleted_files' which expected
        deleted files to be detected. As of #15, unmanaged files are ignored.
        """
        # Setup empty source
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)

        # Setup target with extra file (unmanaged)
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
            # Unmanaged files are ignored - no changes detected
            assert len(result.commands_changes) == 0
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

    def test_ignores_unmanaged_directories(self, tmp_path: Path) -> None:
        """Test that directories in target but not in source are ignored (#15).

        Previously this test was 'test_detects_deleted_directories' which expected
        deleted files to be detected. As of #15, unmanaged directories are ignored.
        """
        # Setup empty source
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)

        # Setup target with extra directory (unmanaged)
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
            # Unmanaged directories are ignored - no changes detected
            assert len(result.skills_changes) == 0
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


class TestFileCmpErrorHandling:
    """Tests for filecmp.cmp() OSError handling (Critical #2)."""

    def test_filecmp_permission_error_records_error(self, tmp_path: Path) -> None:
        """Test that permission errors during file comparison are recorded."""
        from unittest.mock import patch

        # Setup source with file
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "test.md").write_text("# Test Content")

        # Setup target with file
        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)
        target_file = commands_target / "test.md"
        target_file.write_text("# Old Content")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        # Mock filecmp.cmp to raise OSError
        with patch("issue_workflow.services.template.filecmp.cmp") as mock_cmp:
            mock_cmp.side_effect = OSError("Permission denied")

            try:
                result = service.update_commands(target_dir, dry_run=True)
                # Should have recorded the error, not crashed
                assert result.has_errors
                assert any("Permission denied" in str(err) for _, err in result.errors)
            except OSError:
                # If we get an OSError here, the handling is missing
                pytest.fail("OSError should be caught and recorded, not raised")
            finally:
                template_module.get_commands_source_dir = original_func

    def test_copy_permission_error_records_error(self, tmp_path: Path) -> None:
        """Test that permission errors during file copy are recorded in errors."""
        from unittest.mock import patch

        # Setup source with new file
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "new.md").write_text("# New Content")

        # Setup target
        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        # Mock shutil.copy2 to raise OSError
        with patch("issue_workflow.services.template.shutil.copy2") as mock_copy:
            mock_copy.side_effect = OSError("Permission denied")

            try:
                result = service.update_commands(target_dir, dry_run=False)
                # Should have recorded the error, not crashed
                assert result.has_errors
                assert any("Permission denied" in str(err) for _, err in result.errors)
            except OSError:
                pytest.fail("OSError should be caught and recorded, not raised")
            finally:
                template_module.get_commands_source_dir = original_func

    def test_skills_copy_permission_error_records_error(self, tmp_path: Path) -> None:
        """Test that permission errors during skills directory copy are recorded."""
        from unittest.mock import patch

        # Setup source with new skill
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)
        (source_dir / "new-skill").mkdir()
        (source_dir / "new-skill" / "skill.md").write_text("# New Skill")

        # Setup target
        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        skills_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        # Mock shutil.copytree to raise OSError
        with patch("issue_workflow.services.template.shutil.copytree") as mock_copytree:
            mock_copytree.side_effect = OSError("Permission denied")

            try:
                result = service.update_skills(target_dir, dry_run=False)
                # Should have recorded the error, not crashed
                assert result.has_errors
                assert any("Permission denied" in str(err) for _, err in result.errors)
            except OSError:
                pytest.fail("OSError should be caught and recorded, not raised")
            finally:
                template_module.get_skills_source_dir = original_func

    def test_skills_update_rmtree_copytree_failure_shows_data_loss_warning(
        self, tmp_path: Path
    ) -> None:
        """Test that copytree failure after rmtree warns about data loss (Important #1)."""
        from unittest.mock import patch

        # Setup source with updated skill
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)
        (source_dir / "existing-skill").mkdir()
        (source_dir / "existing-skill" / "skill.md").write_text("# Updated Skill")

        # Setup target with existing skill
        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        (skills_target / "existing-skill").mkdir(parents=True)
        (skills_target / "existing-skill" / "skill.md").write_text("# Old Skill")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        def mock_copytree_fail(_src: Path, _dst: Path) -> None:
            raise OSError("Permission denied during copytree")

        with patch(
            "issue_workflow.services.template.shutil.copytree",
            side_effect=mock_copytree_fail,
        ):
            try:
                result = service.update_skills(target_dir, dry_run=False)
                # Should have recorded the error with data loss warning
                assert result.has_errors
                error_messages = [str(err) for _, err in result.errors]
                # Should mention that original directory was removed (data loss warning)
                assert any("removed" in msg.lower() for msg in error_messages)
            finally:
                template_module.get_skills_source_dir = original_func


class TestDircmpRecursive:
    """Tests for recursive directory change detection (Important #3)."""

    def test_detects_nested_subdirectory_changes(self, tmp_path: Path) -> None:
        """Test that changes in nested subdirectories are detected."""
        # Setup source with nested structure
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)
        skill_dir = source_dir / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "skill.md").write_text("# Skill")
        nested_dir = skill_dir / "templates"
        nested_dir.mkdir()
        (nested_dir / "template.md").write_text("# Updated Template")

        # Setup target with same structure but different nested file
        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        target_skill = skills_target / "my-skill"
        target_skill.mkdir(parents=True)
        (target_skill / "skill.md").write_text("# Skill")
        target_nested = target_skill / "templates"
        target_nested.mkdir()
        (target_nested / "template.md").write_text("# Original Template")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        try:
            result = service.update_skills(target_dir, dry_run=True)
            # Should detect that the skill directory has changes
            assert result.updated_count == 1
        finally:
            template_module.get_skills_source_dir = original_func

    def test_detects_deeply_nested_changes(self, tmp_path: Path) -> None:
        """Test that changes in deeply nested subdirectories are detected."""
        # Setup source with deeply nested structure
        source_dir = tmp_path / "source_package" / "skills"
        source_dir.mkdir(parents=True)
        skill_dir = source_dir / "my-skill"
        level1 = skill_dir / "level1"
        level2 = level1 / "level2"
        level2.mkdir(parents=True)
        (skill_dir / "skill.md").write_text("# Skill")
        (level2 / "deep.md").write_text("# Updated Deep File")

        # Setup target with same structure but different deeply nested file
        target_dir = tmp_path / ".claude"
        skills_target = target_dir / "skills"
        target_skill = skills_target / "my-skill"
        target_level1 = target_skill / "level1"
        target_level2 = target_level1 / "level2"
        target_level2.mkdir(parents=True)
        (target_skill / "skill.md").write_text("# Skill")
        (target_level2 / "deep.md").write_text("# Original Deep File")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: source_dir

        try:
            result = service.update_skills(target_dir, dry_run=True)
            # Should detect that the skill directory has changes
            assert result.updated_count == 1
        finally:
            template_module.get_skills_source_dir = original_func


class TestUpdateAgents:
    """Tests for TemplateService.update_agents method (T076)."""

    def test_detects_added_files(self, tmp_path: Path) -> None:
        """Test detecting newly added agent files."""
        source_dir = tmp_path / "source_package" / "agents"
        source_dir.mkdir(parents=True)
        (source_dir / "new-agent.md").write_text("# New Agent")

        target_dir = tmp_path / ".claude"
        agents_target = target_dir / "agents"
        agents_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_agents_source_dir
        template_module.get_agents_source_dir = lambda: source_dir

        try:
            result = service.update_agents(target_dir, dry_run=True)
            assert result.added_count == 1
            assert result.agents_changes[0].change_type == FileChangeType.ADDED
        finally:
            template_module.get_agents_source_dir = original_func

    def test_detects_updated_files(self, tmp_path: Path) -> None:
        """Test detecting updated agent files."""
        source_dir = tmp_path / "source_package" / "agents"
        source_dir.mkdir(parents=True)
        (source_dir / "existing.md").write_text("# Updated Content")

        target_dir = tmp_path / ".claude"
        agents_target = target_dir / "agents"
        agents_target.mkdir(parents=True)
        (agents_target / "existing.md").write_text("# Old Content")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_agents_source_dir
        template_module.get_agents_source_dir = lambda: source_dir

        try:
            result = service.update_agents(target_dir, dry_run=True)
            assert result.updated_count == 1
            assert result.agents_changes[0].change_type == FileChangeType.UPDATED
        finally:
            template_module.get_agents_source_dir = original_func

    def test_dry_run_does_not_create_files(self, tmp_path: Path) -> None:
        """Test dry-run does not create agent files."""
        source_dir = tmp_path / "source_package" / "agents"
        source_dir.mkdir(parents=True)
        (source_dir / "new-agent.md").write_text("# New Agent")

        target_dir = tmp_path / ".claude"
        agents_target = target_dir / "agents"
        agents_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_agents_source_dir
        template_module.get_agents_source_dir = lambda: source_dir

        try:
            result = service.update_agents(target_dir, dry_run=True)
            assert result.added_count == 1
            assert result.dry_run is True
            assert not (agents_target / "new-agent.md").exists()
        finally:
            template_module.get_agents_source_dir = original_func

    def test_applies_changes_when_not_dry_run(self, tmp_path: Path) -> None:
        """Test agent files are actually updated when dry_run=False."""
        source_dir = tmp_path / "source_package" / "agents"
        source_dir.mkdir(parents=True)
        (source_dir / "new-agent.md").write_text("# New Agent Content")

        target_dir = tmp_path / ".claude"
        agents_target = target_dir / "agents"
        agents_target.mkdir(parents=True)

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_agents_source_dir
        template_module.get_agents_source_dir = lambda: source_dir

        try:
            result = service.update_agents(target_dir, dry_run=False)
            assert result.added_count == 1
            assert (agents_target / "new-agent.md").exists()
            assert (agents_target / "new-agent.md").read_text() == "# New Agent Content"
        finally:
            template_module.get_agents_source_dir = original_func

    def test_ignores_unmanaged_files(self, tmp_path: Path) -> None:
        """Test that unmanaged agent files in target are ignored."""
        source_dir = tmp_path / "source_package" / "agents"
        source_dir.mkdir(parents=True)

        target_dir = tmp_path / ".claude"
        agents_target = target_dir / "agents"
        agents_target.mkdir(parents=True)
        (agents_target / "user-agent.md").write_text("# User Agent")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_agents_source_dir
        template_module.get_agents_source_dir = lambda: source_dir

        try:
            result = service.update_agents(target_dir, dry_run=True)
            assert result.has_changes is False
        finally:
            template_module.get_agents_source_dir = original_func

    def test_source_directory_not_found(self, tmp_path: Path) -> None:
        """Test error when agents source directory does not exist."""
        from issue_workflow.services.template import SourceDirectoryNotFoundError

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_agents_source_dir
        template_module.get_agents_source_dir = lambda: tmp_path / "nonexistent"

        try:
            with pytest.raises(SourceDirectoryNotFoundError):
                service.update_agents(tmp_path / ".claude")
        finally:
            template_module.get_agents_source_dir = original_func

    def test_no_changes_when_identical(self, tmp_path: Path) -> None:
        """Test no changes detected when agent files are identical."""
        source_dir = tmp_path / "source_package" / "agents"
        source_dir.mkdir(parents=True)
        (source_dir / "same.md").write_text("# Same Content")

        target_dir = tmp_path / ".claude"
        agents_target = target_dir / "agents"
        agents_target.mkdir(parents=True)
        (agents_target / "same.md").write_text("# Same Content")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_agents_source_dir
        template_module.get_agents_source_dir = lambda: source_dir

        try:
            result = service.update_agents(target_dir, dry_run=True)
            assert result.added_count == 0
            assert result.updated_count == 0
            assert result.has_changes is False
        finally:
            template_module.get_agents_source_dir = original_func


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
        """Test result correctly combines multiple change types.

        Note: As of #15, unmanaged files are ignored.
        """
        source_dir = tmp_path / "source_package" / "commands"
        source_dir.mkdir(parents=True)
        (source_dir / "new.md").write_text("# New")
        (source_dir / "updated.md").write_text("# Updated Content")

        target_dir = tmp_path / ".claude"
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True)
        (commands_target / "updated.md").write_text("# Old Content")
        (commands_target / "unmanaged.md").write_text("# Unmanaged")

        service = TemplateService()
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: source_dir

        try:
            result = service.update_commands(target_dir, dry_run=True)
            assert result.added_count == 1
            assert result.updated_count == 1
            # Unmanaged files are ignored (#15)
            assert result.has_changes is True
        finally:
            template_module.get_commands_source_dir = original_func
