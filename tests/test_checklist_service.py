"""
Tests for ChecklistService: subtask management and completion progress.
"""
import pytest

from src.services.checklist_service import ChecklistService


def test_checklist_lifecycle(db_session, sample_task):
    service = ChecklistService()

    # Initial progress should be 0/0
    done, total = service.get_progress(sample_task.id)
    assert done == 0
    assert total == 0

    # Add 2 items
    item1, err1 = service.add_item(sample_task.id, "Read Chapter 5")
    assert err1 == ""
    assert item1 is not None

    item2, err2 = service.add_item(sample_task.id, "Complete Exercises 1-10")
    assert err2 == ""
    assert item2 is not None

    # Check progress
    done, total = service.get_progress(sample_task.id)
    assert done == 0
    assert total == 2

    # Toggle first item
    ok, _ = service.toggle_item(item1.id)
    assert ok is True

    done, total = service.get_progress(sample_task.id)
    assert done == 1
    assert total == 2

    # Delete second item
    ok_del, _ = service.delete_item(item2.id)
    assert ok_del is True

    done, total = service.get_progress(sample_task.id)
    assert done == 1
    assert total == 1
