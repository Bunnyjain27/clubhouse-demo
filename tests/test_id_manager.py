#!/usr/bin/env python3
"""
Unit tests for the Clubhouse ID and Token system.
"""

import sys
import os
import time
import unittest
from unittest.mock import patch

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eosclubhouse.id_manager import (
    IDManager, ClubhouseID, TokenID, IDType, TokenStatus, IDRelationship,
    get_id_manager, create_clubhouse_id, create_token_link, verify_token_link
)


class TestClubhouseID(unittest.TestCase):
    """Test cases for ClubhouseID class."""

    def test_create_default_id(self):
        """Test creating a default clubhouse ID."""
        cid = ClubhouseID()
        self.assertIsNotNone(cid.id_value)
        self.assertEqual(cid.id_type, IDType.CLUBHOUSE)
        self.assertEqual(cid.access_count, 1)  # Accessing id_value increments counter

    def test_create_custom_id(self):
        """Test creating a custom clubhouse ID."""
        custom_id = "custom-123"
        metadata = {"test": "value"}
        cid = ClubhouseID(custom_id, IDType.USER, metadata)
        
        self.assertEqual(cid.id_value, custom_id)
        self.assertEqual(cid.id_type, IDType.USER)
        self.assertEqual(cid.get_metadata("test"), "value")

    def test_invalid_id_raises_error(self):
        """Test that invalid ID formats raise ValueError."""
        with self.assertRaises(ValueError):
            ClubhouseID("")
        
        with self.assertRaises(ValueError):
            ClubhouseID("invalid@id#format")

    def test_metadata_operations(self):
        """Test metadata operations."""
        cid = ClubhouseID()
        
        # Test setting and getting metadata
        cid.update_metadata("key1", "value1")
        self.assertEqual(cid.get_metadata("key1"), "value1")
        
        # Test default value
        self.assertEqual(cid.get_metadata("nonexistent", "default"), "default")
        
        # Test updating existing metadata
        cid.update_metadata("key1", "new_value")
        self.assertEqual(cid.get_metadata("key1"), "new_value")

    def test_access_tracking(self):
        """Test access tracking functionality."""
        cid = ClubhouseID()
        initial_count = cid.access_count
        initial_time = cid.last_accessed
        
        # Access the ID
        time.sleep(0.1)  # Small delay to ensure timestamp difference
        _ = cid.id_value
        
        self.assertEqual(cid.access_count, initial_count + 1)
        self.assertGreater(cid.last_accessed, initial_time)

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        original = ClubhouseID("test-id", IDType.QUEST, {"name": "Test Quest"})
        
        # Convert to dict
        data = original.to_dict()
        self.assertEqual(data['id'], "test-id")
        self.assertEqual(data['type'], "quest")
        self.assertEqual(data['metadata']['name'], "Test Quest")
        
        # Convert back from dict
        restored = ClubhouseID.from_dict(data)
        self.assertEqual(restored.id_value, original.id_value)
        self.assertEqual(restored.id_type, original.id_type)
        self.assertEqual(restored.get_metadata("name"), original.get_metadata("name"))

    def test_equality(self):
        """Test ID equality comparison."""
        id1 = ClubhouseID("same-id", IDType.USER)
        id2 = ClubhouseID("same-id", IDType.USER)
        id3 = ClubhouseID("different-id", IDType.USER)
        id4 = ClubhouseID("same-id", IDType.QUEST)
        
        self.assertEqual(id1, id2)
        self.assertNotEqual(id1, id3)
        self.assertNotEqual(id1, id4)
        self.assertNotEqual(id1, "not-a-clubhouse-id")


class TestTokenID(unittest.TestCase):
    """Test cases for TokenID class."""

    def test_create_basic_token(self):
        """Test creating a basic token."""
        token = TokenID("source-id", "target-id")
        
        self.assertEqual(token.source_id, "source-id")
        self.assertEqual(token.target_id, "target-id")
        self.assertEqual(token.status, TokenStatus.ACTIVE)
        self.assertIsNotNone(token.token_value)
        self.assertEqual(token.usage_count, 0)

    def test_create_expiring_token(self):
        """Test creating a token with expiration."""
        token = TokenID("source-id", "target-id", expires_in=3600)
        
        self.assertIsNotNone(token.expires_at)
        self.assertFalse(token.is_expired())
        self.assertGreater(token.expires_at, time.time())

    def test_token_verification(self):
        """Test token verification."""
        token = TokenID("source-id", "target-id")
        
        # Verify correct token
        self.assertTrue(token.verify_token(token.token_value))
        self.assertEqual(token.usage_count, 1)
        
        # Verify wrong token
        self.assertFalse(token.verify_token("wrong-token"))
        self.assertEqual(token.usage_count, 1)  # Should not increment

    def test_token_expiration(self):
        """Test token expiration."""
        token = TokenID("source-id", "target-id", expires_in=1)
        
        # Should work initially
        self.assertTrue(token.verify_token(token.token_value))
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired now
        self.assertTrue(token.is_expired())
        self.assertFalse(token.verify_token(token.token_value))
        self.assertEqual(token.status, TokenStatus.EXPIRED)

    def test_token_revocation(self):
        """Test token revocation."""
        token = TokenID("source-id", "target-id")
        
        # Should work initially
        self.assertTrue(token.verify_token(token.token_value))
        
        # Revoke the token
        token.revoke()
        self.assertEqual(token.status, TokenStatus.REVOKED)
        
        # Should not work after revocation
        self.assertFalse(token.verify_token(token.token_value))

    def test_extend_expiry(self):
        """Test extending token expiry."""
        token = TokenID("source-id", "target-id", expires_in=1)
        original_expiry = token.expires_at
        
        # Extend expiry
        token.extend_expiry(3600)
        
        self.assertGreater(token.expires_at, original_expiry)
        self.assertFalse(token.is_expired())

    def test_token_metadata(self):
        """Test token metadata."""
        metadata = {"purpose": "test", "priority": "high"}
        token = TokenID("source-id", "target-id", metadata=metadata)
        
        token_dict = token.to_dict()
        self.assertEqual(token_dict['metadata'], metadata)


class TestIDRelationship(unittest.TestCase):
    """Test cases for IDRelationship class."""

    def test_create_relationship(self):
        """Test creating a relationship."""
        rel = IDRelationship(
            source_id="source-id",
            target_id="target-id",
            token_id="token-id",
            relationship_type="test",
            created_at=time.time()
        )
        
        self.assertEqual(rel.source_id, "source-id")
        self.assertEqual(rel.target_id, "target-id")
        self.assertEqual(rel.token_id, "token-id")
        self.assertEqual(rel.relationship_type, "test")

    def test_relationship_expiration(self):
        """Test relationship expiration."""
        # Non-expiring relationship
        rel1 = IDRelationship(
            source_id="source-id",
            target_id="target-id",
            token_id="token-id",
            relationship_type="test",
            created_at=time.time()
        )
        self.assertFalse(rel1.is_expired())
        
        # Expired relationship
        rel2 = IDRelationship(
            source_id="source-id",
            target_id="target-id",
            token_id="token-id",
            relationship_type="test",
            created_at=time.time(),
            expires_at=time.time() - 1  # Expired 1 second ago
        )
        self.assertTrue(rel2.is_expired())


class TestIDManager(unittest.TestCase):
    """Test cases for IDManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = IDManager()

    def test_create_and_get_id(self):
        """Test creating and retrieving IDs."""
        # Create an ID
        cid = self.manager.create_id(IDType.USER, metadata={"name": "Test User"})
        
        # Retrieve it
        retrieved = self.manager.get_id(cid.id_value)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id_value, cid.id_value)
        self.assertEqual(retrieved.get_metadata("name"), "Test User")

    def test_get_ids_by_type(self):
        """Test getting IDs by type."""
        # Create IDs of different types
        user_id = self.manager.create_id(IDType.USER)
        quest_id = self.manager.create_id(IDType.QUEST)
        another_user_id = self.manager.create_id(IDType.USER)
        
        # Get users
        users = self.manager.get_ids_by_type(IDType.USER)
        self.assertEqual(len(users), 2)
        
        # Get quests
        quests = self.manager.get_ids_by_type(IDType.QUEST)
        self.assertEqual(len(quests), 1)
        
        # Get empty type
        achievements = self.manager.get_ids_by_type(IDType.ACHIEVEMENT)
        self.assertEqual(len(achievements), 0)

    def test_create_token_link(self):
        """Test creating token links."""
        # Create source and target IDs
        source_id = self.manager.create_id(IDType.USER)
        target_id = self.manager.create_id(IDType.QUEST)
        
        # Create token link
        token = self.manager.create_token_link(
            source_id.id_value,
            target_id.id_value,
            expires_in=3600,
            relationship_type="enrollment",
            metadata={"started_at": time.time()}
        )
        
        self.assertIsNotNone(token)
        self.assertEqual(token.source_id, source_id.id_value)
        self.assertEqual(token.target_id, target_id.id_value)

    def test_create_token_link_invalid_ids(self):
        """Test creating token links with invalid IDs."""
        source_id = self.manager.create_id(IDType.USER)
        
        # Try to link to non-existent target
        with self.assertRaises(ValueError):
            self.manager.create_token_link(
                source_id.id_value,
                "non-existent-id"
            )
        
        # Try to link from non-existent source
        target_id = self.manager.create_id(IDType.QUEST)
        with self.assertRaises(ValueError):
            self.manager.create_token_link(
                "non-existent-id",
                target_id.id_value
            )

    def test_verify_token_link(self):
        """Test verifying token links."""
        # Create IDs and token
        source_id = self.manager.create_id(IDType.USER)
        target_id = self.manager.create_id(IDType.QUEST)
        token = self.manager.create_token_link(source_id.id_value, target_id.id_value)
        
        # Verify token
        self.assertTrue(self.manager.verify_token_link(token.token_value))
        
        # Verify with source/target validation
        self.assertTrue(self.manager.verify_token_link(
            token.token_value, source_id.id_value, target_id.id_value
        ))
        
        # Verify with wrong source/target
        self.assertFalse(self.manager.verify_token_link(
            token.token_value, "wrong-source", target_id.id_value
        ))

    def test_get_linked_ids(self):
        """Test getting linked IDs."""
        # Create IDs
        source_id = self.manager.create_id(IDType.USER)
        target1_id = self.manager.create_id(IDType.QUEST)
        target2_id = self.manager.create_id(IDType.CLUBHOUSE)
        
        # Create links
        self.manager.create_token_link(source_id.id_value, target1_id.id_value)
        self.manager.create_token_link(source_id.id_value, target2_id.id_value)
        
        # Get linked IDs
        linked = self.manager.get_linked_ids(source_id.id_value)
        self.assertEqual(len(linked), 2)
        self.assertIn(target1_id.id_value, linked)
        self.assertIn(target2_id.id_value, linked)

    def test_get_reverse_linked_ids(self):
        """Test getting reverse linked IDs."""
        # Create IDs
        source1_id = self.manager.create_id(IDType.USER)
        source2_id = self.manager.create_id(IDType.USER)
        target_id = self.manager.create_id(IDType.QUEST)
        
        # Create links
        self.manager.create_token_link(source1_id.id_value, target_id.id_value)
        self.manager.create_token_link(source2_id.id_value, target_id.id_value)
        
        # Get reverse linked IDs
        reverse_linked = self.manager.get_reverse_linked_ids(target_id.id_value)
        self.assertEqual(len(reverse_linked), 2)
        self.assertIn(source1_id.id_value, reverse_linked)
        self.assertIn(source2_id.id_value, reverse_linked)

    def test_get_relationships(self):
        """Test getting relationships."""
        # Create IDs
        source_id = self.manager.create_id(IDType.USER)
        target_id = self.manager.create_id(IDType.QUEST)
        
        # Create relationships
        self.manager.create_token_link(
            source_id.id_value, target_id.id_value, relationship_type="enrollment"
        )
        
        # Get relationships by type
        enrollments = self.manager.get_relationships(relationship_type="enrollment")
        self.assertEqual(len(enrollments), 1)
        self.assertEqual(enrollments[0].relationship_type, "enrollment")
        
        # Get relationships by source
        source_rels = self.manager.get_relationships(source_id=source_id.id_value)
        self.assertEqual(len(source_rels), 1)
        
        # Get relationships by target
        target_rels = self.manager.get_relationships(target_id=target_id.id_value)
        self.assertEqual(len(target_rels), 1)

    def test_revoke_token(self):
        """Test revoking tokens."""
        # Create IDs and token
        source_id = self.manager.create_id(IDType.USER)
        target_id = self.manager.create_id(IDType.QUEST)
        token = self.manager.create_token_link(source_id.id_value, target_id.id_value)
        
        # Verify token works
        self.assertTrue(self.manager.verify_token_link(token.token_value))
        
        # Revoke token
        self.assertTrue(self.manager.revoke_token(token.token_value))
        
        # Verify token no longer works
        self.assertFalse(self.manager.verify_token_link(token.token_value))
        
        # Try to revoke non-existent token
        self.assertFalse(self.manager.revoke_token("non-existent-token"))

    def test_cleanup_expired_tokens(self):
        """Test cleaning up expired tokens."""
        # Create IDs
        source_id = self.manager.create_id(IDType.USER)
        target_id = self.manager.create_id(IDType.QUEST)
        
        # Create expired token
        self.manager.create_token_link(
            source_id.id_value, target_id.id_value, expires_in=1
        )
        
        # Wait for expiration
        time.sleep(2)
        
        # Clean up
        expired_count = self.manager.cleanup_expired_tokens()
        self.assertEqual(expired_count, 1)

    def test_statistics(self):
        """Test getting statistics."""
        # Create some data
        user_id = self.manager.create_id(IDType.USER)
        quest_id = self.manager.create_id(IDType.QUEST)
        self.manager.create_token_link(user_id.id_value, quest_id.id_value)
        
        # Get statistics
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats['total_ids'], 2)
        self.assertEqual(stats['total_tokens'], 1)
        self.assertEqual(stats['total_relationships'], 1)
        self.assertEqual(stats['ids_by_type']['user'], 1)
        self.assertEqual(stats['ids_by_type']['quest'], 1)
        self.assertEqual(stats['active_tokens'], 1)

    def test_export_import_data(self):
        """Test exporting and importing data."""
        # Create some data
        user_id = self.manager.create_id(IDType.USER, metadata={"name": "Test User"})
        quest_id = self.manager.create_id(IDType.QUEST, metadata={"name": "Test Quest"})
        
        # Export data
        exported = self.manager.export_data()
        
        # Verify export structure
        self.assertIn('ids', exported)
        self.assertIn('tokens', exported)
        self.assertIn('relationships', exported)
        self.assertEqual(len(exported['ids']), 2)
        
        # Import data into new manager
        new_manager = IDManager()
        new_manager.import_data(exported)
        
        # Verify import
        imported_user = new_manager.get_id(user_id.id_value)
        self.assertIsNotNone(imported_user)
        self.assertEqual(imported_user.get_metadata("name"), "Test User")


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""

    def test_create_clubhouse_id(self):
        """Test convenience function for creating clubhouse IDs."""
        cid = create_clubhouse_id(IDType.USER, metadata={"name": "Test"})
        self.assertEqual(cid.id_type, IDType.USER)
        self.assertEqual(cid.get_metadata("name"), "Test")

    def test_create_token_link(self):
        """Test convenience function for creating token links."""
        # Create IDs first
        source_id = create_clubhouse_id(IDType.USER)
        target_id = create_clubhouse_id(IDType.QUEST)
        
        # Create token link
        token = create_token_link(source_id.id_value, target_id.id_value)
        
        self.assertIsNotNone(token)
        self.assertEqual(token.source_id, source_id.id_value)
        self.assertEqual(token.target_id, target_id.id_value)

    def test_verify_token_link(self):
        """Test convenience function for verifying token links."""
        # Create IDs and token
        source_id = create_clubhouse_id(IDType.USER)
        target_id = create_clubhouse_id(IDType.QUEST)
        token = create_token_link(source_id.id_value, target_id.id_value)
        
        # Verify token
        self.assertTrue(verify_token_link(token.token_value))
        self.assertTrue(verify_token_link(
            token.token_value, source_id.id_value, target_id.id_value
        ))

    def test_get_id_manager_singleton(self):
        """Test that get_id_manager returns the same instance."""
        manager1 = get_id_manager()
        manager2 = get_id_manager()
        
        self.assertIs(manager1, manager2)


if __name__ == '__main__':
    unittest.main()