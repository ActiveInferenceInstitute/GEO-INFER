"""Tests for CollaborationManager session lifecycle (GS-227).

Covers session creation with host registration, join/leave flows
including idempotent rejoin and capacity limits, permission-checked
session ending, shared workspace messages/documents, and session
querying/statistics.
"""

import pytest

from geo_infer_comms.core.collaboration import CollaborationManager
from geo_infer_comms.models.message import CollaborationSessionRequest


@pytest.fixture()
def manager():
    return CollaborationManager()


def _request(name="Field planning", session_type=None):
    kwargs = {
        "name": name,
        "description": "Session under test",
        "participants": ["creator-1"],
    }
    if session_type is not None:
        kwargs["session_type"] = session_type
    return CollaborationSessionRequest(**kwargs)


def _activate(manager: CollaborationManager, session_id: str) -> None:
    """Fresh sessions are created as ``scheduled``; joining requires active."""
    manager.sessions[session_id].status = "active"


class TestSessionCreation:
    def test_create_session_registers_creator_as_host(self, manager):
        session = manager.create_session(_request(), "creator-1")

        assert session.session_id in manager.sessions
        assert len(session.participants) == 1
        assert session.participants[0].user_id == "creator-1"
        assert session.participants[0].role.value == "host"
        assert manager.participant_sessions["creator-1"] == {session.session_id}
        assert manager.metrics.sessions_created == 1

    def test_invalid_session_configuration_rejected(self, manager):
        with pytest.raises(ValueError, match="Invalid collaboration session"):
            manager.create_session(_request(name="   "), "creator-1")
        assert manager.metrics.sessions_created == 0

    def test_session_limit_enforced(self):
        manager = CollaborationManager(max_sessions=1)
        manager.create_session(_request(), "creator-1")
        with pytest.raises(ValueError, match="Maximum number of sessions"):
            manager.create_session(_request(), "other-creator")


class TestJoinLeave:
    def test_join_unknown_session_raises(self, manager):
        with pytest.raises(ValueError, match="Session not found"):
            manager.join_session("missing-session", "user-1")

    def test_join_scheduled_session_rejected(self, manager):
        session = manager.create_session(_request(), "creator-1")
        assert session.status == "scheduled"
        with pytest.raises(ValueError, match="Session is not active"):
            manager.join_session(session.session_id, "user-1")

    def test_join_active_session_adds_participant(self, manager):
        session = manager.create_session(_request(), "creator-1")
        _activate(manager, session.session_id)

        response = manager.join_session(session.session_id, "user-1")

        assert response.join_status == "joined"
        assert response.participant_id == "user-1"
        assert len(session.participants) == 2
        assert (
            manager.session_participants[session.session_id]["user-1"].role.value
            == "participant"
        )
        assert manager.metrics.participants_joined == 1

    def test_rejoin_is_idempotent(self, manager):
        session = manager.create_session(_request(), "creator-1")
        _activate(manager, session.session_id)

        first = manager.join_session(session.session_id, "creator-1")
        second = manager.join_session(session.session_id, "creator-1")

        assert first.join_status == second.join_status == "joined"
        assert len(session.participants) == 1
        assert manager.metrics.participants_joined == 0

    def test_join_full_session_raises(self):
        manager = CollaborationManager(max_participants_per_session=1)
        session = manager.create_session(_request(), "creator-1")
        _activate(manager, session.session_id)

        with pytest.raises(ValueError, match="Session is full"):
            manager.join_session(session.session_id, "user-1")

    def test_leave_flow(self, manager):
        session = manager.create_session(_request(), "creator-1")
        _activate(manager, session.session_id)
        manager.join_session(session.session_id, "user-1")

        assert manager.leave_session(session.session_id, "user-1") is True
        assert "user-1" not in manager.session_participants[session.session_id]
        assert session.session_id not in manager.participant_sessions["user-1"]
        assert manager.metrics.participants_left == 1
        # Leaving twice reports nothing left to do.
        assert manager.leave_session(session.session_id, "user-1") is False

    def test_leave_unknown_session_or_nonmember_returns_false(self, manager):
        session = manager.create_session(_request(), "creator-1")
        assert manager.leave_session("missing-session", "creator-1") is False
        assert manager.leave_session(session.session_id, "stranger") is False


class TestSessionEnding:
    def test_host_can_end_session(self, manager):
        session = manager.create_session(_request(), "creator-1")
        _activate(manager, session.session_id)

        assert manager.end_session(session.session_id, "creator-1") is True
        assert session.status == "ended"
        assert session.ended_at is not None
        assert all(p.status.value == "offline" for p in session.participants)
        assert manager.metrics.sessions_ended == 1

    def test_non_host_cannot_end_session(self, manager):
        session = manager.create_session(_request(), "creator-1")
        _activate(manager, session.session_id)
        manager.join_session(session.session_id, "user-1")

        assert manager.end_session(session.session_id, "user-1") is False
        assert session.status == "active"

    def test_end_unknown_session_returns_false(self, manager):
        assert manager.end_session("missing-session", "creator-1") is False


class TestSharedWorkspace:
    def test_message_flow(self, manager):
        session = manager.create_session(_request(), "creator-1")
        _activate(manager, session.session_id)
        manager.join_session(session.session_id, "user-1")

        assert (
            manager.add_session_message(session.session_id, "user-1", {"text": "hello"})
            is True
        )
        messages = manager.get_session_messages(session.session_id)
        assert len(messages) == 1
        assert messages[0]["text"] == "hello"
        assert messages[0]["user_id"] == "user-1"
        assert "timestamp" in messages[0]

    def test_message_rejected_for_non_participant_or_unknown_session(self, manager):
        session = manager.create_session(_request(), "creator-1")
        assert manager.add_session_message(session.session_id, "stranger", {}) is False
        assert manager.add_session_message("missing-session", "creator-1", {}) is False

    def test_shared_document_versioning(self, manager):
        session = manager.create_session(_request(), "creator-1")

        assert (
            manager.update_shared_document(
                session.session_id, "doc-1", "creator-1", {"title": "Plan"}
            )
            is True
        )
        assert (
            manager.update_shared_document(
                session.session_id, "doc-1", "creator-1", {"status": "draft"}
            )
            is True
        )

        document = manager.get_shared_document(session.session_id, "doc-1")
        assert document["version"] == 3
        assert document["content"] == {"title": "Plan", "status": "draft"}
        assert document["last_modified_by"] == "creator-1"
        assert manager.get_shared_document(session.session_id, "doc-missing") is None

    def test_document_update_rejected_for_non_participant(self, manager):
        session = manager.create_session(_request(), "creator-1")
        assert (
            manager.update_shared_document(session.session_id, "doc-1", "stranger", {})
            is False
        )


class TestSessionQueries:
    def test_get_participant_sessions_filters_by_membership(self, manager):
        session_a = manager.create_session(_request(), "creator-1")
        manager.create_session(_request(name="Other"), "creator-2")

        sessions = manager.get_participant_sessions("creator-1")
        assert [s.session_id for s in sessions] == [session_a.session_id]
        assert manager.get_participant_sessions("nobody") == []

    def test_get_sessions_filters_by_participant_and_status(self, manager):
        session = manager.create_session(_request(), "creator-1")
        manager.create_session(_request(name="Other"), "creator-2")

        active = manager.get_sessions(participant_id="creator-1")
        assert len(active) == 1

        # Only the first session was activated.
        _activate(manager, session.session_id)
        assert [s.session_id for s in manager.get_sessions(status="active")] == [
            session.session_id
        ]

    def test_statistics_counts(self, manager):
        session = manager.create_session(_request(), "creator-1")
        _activate(manager, session.session_id)
        manager.join_session(session.session_id, "user-1")

        stats = manager.get_session_statistics()
        assert stats["total_sessions"] == 1
        assert stats["active_sessions"] == 1
        assert stats["total_participants"] == 2
