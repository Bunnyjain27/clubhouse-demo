#!/usr/bin/env python3
"""
Example script demonstrating the Clubhouse ID and Token system.

This script shows how to:
1. Create clubhouse IDs of different types
2. Link IDs together using tokens
3. Verify token-based relationships
4. Manage ID relationships and metadata
"""

import sys
import os
import time

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eosclubhouse.id_manager import (
    IDManager, ClubhouseID, TokenID, IDType, TokenStatus,
    get_id_manager, create_clubhouse_id, create_token_link, verify_token_link
)


def demonstrate_basic_usage():
    """Demonstrate basic clubhouse ID creation and management."""
    print("=== Basic Clubhouse ID Usage ===")
    
    # Create different types of IDs
    clubhouse_id = create_clubhouse_id(
        id_type=IDType.CLUBHOUSE,
        metadata={"name": "Main Clubhouse", "location": "virtual"}
    )
    
    user_id = create_clubhouse_id(
        id_type=IDType.USER,
        metadata={"username": "alice_explorer", "level": 5}
    )
    
    quest_id = create_clubhouse_id(
        id_type=IDType.QUEST,
        metadata={"name": "Web Adventure", "difficulty": "medium"}
    )
    
    print(f"Created clubhouse ID: {clubhouse_id}")
    print(f"Created user ID: {user_id}")
    print(f"Created quest ID: {quest_id}")
    
    # Access ID metadata
    print(f"User level: {user_id.get_metadata('level')}")
    print(f"Quest difficulty: {quest_id.get_metadata('difficulty')}")
    
    return clubhouse_id, user_id, quest_id


def demonstrate_token_linking():
    """Demonstrate token-based ID linking."""
    print("\n=== Token-Based ID Linking ===")
    
    # Create some IDs first
    clubhouse_id, user_id, quest_id = demonstrate_basic_usage()
    
    # Create a token linking user to clubhouse (membership)
    membership_token = create_token_link(
        source_id=user_id.id_value,
        target_id=clubhouse_id.id_value,
        expires_in=3600,  # 1 hour
        relationship_type="membership",
        metadata={"joined_at": time.time(), "role": "member"}
    )
    
    # Create a token linking user to quest (enrollment)
    enrollment_token = create_token_link(
        source_id=user_id.id_value,
        target_id=quest_id.id_value,
        expires_in=7200,  # 2 hours
        relationship_type="enrollment",
        metadata={"started_at": time.time(), "progress": 0}
    )
    
    print(f"Created membership token: {membership_token.token_value}")
    print(f"Created enrollment token: {enrollment_token.token_value}")
    
    # Verify the token links
    print(f"Membership token valid: {verify_token_link(membership_token.token_value)}")
    print(f"Enrollment token valid: {verify_token_link(enrollment_token.token_value)}")
    
    # Check with specific source/target validation
    print(f"User->Clubhouse link valid: {verify_token_link(membership_token.token_value, user_id.id_value, clubhouse_id.id_value)}")
    print(f"User->Quest link valid: {verify_token_link(enrollment_token.token_value, user_id.id_value, quest_id.id_value)}")
    
    return membership_token, enrollment_token, user_id, clubhouse_id, quest_id


def demonstrate_relationship_queries():
    """Demonstrate querying relationships between IDs."""
    print("\n=== Relationship Queries ===")
    
    membership_token, enrollment_token, user_id, clubhouse_id, quest_id = demonstrate_token_linking()
    
    manager = get_id_manager()
    
    # Get all IDs linked from the user
    linked_ids = manager.get_linked_ids(user_id.id_value)
    print(f"IDs linked from user {user_id.id_value}: {linked_ids}")
    
    # Get all IDs that link to the clubhouse
    reverse_linked = manager.get_reverse_linked_ids(clubhouse_id.id_value)
    print(f"IDs linking to clubhouse {clubhouse_id.id_value}: {reverse_linked}")
    
    # Get relationships by type
    memberships = manager.get_relationships(relationship_type="membership")
    enrollments = manager.get_relationships(relationship_type="enrollment")
    
    print(f"Found {len(memberships)} membership relationships")
    print(f"Found {len(enrollments)} enrollment relationships")
    
    # Get relationships for a specific user
    user_relationships = manager.get_relationships(source_id=user_id.id_value)
    print(f"User has {len(user_relationships)} outgoing relationships")
    
    for rel in user_relationships:
        print(f"  - {rel.relationship_type}: {rel.source_id} -> {rel.target_id}")


def demonstrate_token_management():
    """Demonstrate token lifecycle management."""
    print("\n=== Token Management ===")
    
    manager = get_id_manager()
    
    # Create a short-lived token for demonstration
    temp_id1 = create_clubhouse_id(IDType.CUSTOM, metadata={"temp": True})
    temp_id2 = create_clubhouse_id(IDType.CUSTOM, metadata={"temp": True})
    
    # Create a token that expires in 1 second
    short_token = create_token_link(
        source_id=temp_id1.id_value,
        target_id=temp_id2.id_value,
        expires_in=1,  # 1 second
        relationship_type="temporary"
    )
    
    print(f"Created short-lived token: {short_token.token_value}")
    print(f"Token status: {short_token.status.value}")
    print(f"Token expires at: {short_token.expires_at}")
    
    # Verify it works initially
    print(f"Token valid initially: {verify_token_link(short_token.token_value)}")
    
    # Wait for it to expire
    print("Waiting for token to expire...")
    time.sleep(2)
    
    # Try to verify after expiration
    print(f"Token valid after expiration: {verify_token_link(short_token.token_value)}")
    print(f"Token status after expiration: {short_token.status.value}")
    
    # Demonstrate token revocation
    another_token = create_token_link(
        source_id=temp_id1.id_value,
        target_id=temp_id2.id_value,
        relationship_type="revocation_demo"
    )
    
    print(f"Created revocation demo token: {another_token.token_value}")
    print(f"Token valid before revocation: {verify_token_link(another_token.token_value)}")
    
    # Revoke the token
    manager.revoke_token(another_token.token_value)
    print(f"Token valid after revocation: {verify_token_link(another_token.token_value)}")
    print(f"Token status after revocation: {another_token.status.value}")
    
    # Cleanup expired tokens
    cleanup_count = manager.cleanup_expired_tokens()
    print(f"Cleaned up {cleanup_count} expired tokens")


def demonstrate_advanced_features():
    """Demonstrate advanced features like statistics and data export."""
    print("\n=== Advanced Features ===")
    
    manager = get_id_manager()
    
    # Get statistics
    stats = manager.get_statistics()
    print("Current ID Manager Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Demonstrate data export
    print("\nExporting data...")
    exported_data = manager.export_data()
    print(f"Exported {len(exported_data['ids'])} IDs")
    print(f"Exported {len(exported_data['tokens'])} tokens")
    print(f"Exported {len(exported_data['relationships'])} relationships")
    
    # Show some sample exported data
    if exported_data['ids']:
        first_id = list(exported_data['ids'].keys())[0]
        print(f"Sample exported ID: {exported_data['ids'][first_id]}")


def demonstrate_practical_scenario():
    """Demonstrate a practical scenario: User joining a clubhouse and starting quests."""
    print("\n=== Practical Scenario: User Journey ===")
    
    # Create a clubhouse
    clubhouse = create_clubhouse_id(
        id_type=IDType.CLUBHOUSE,
        metadata={
            "name": "Adventure Academy",
            "description": "A place for digital explorers",
            "capacity": 100,
            "created_by": "admin"
        }
    )
    
    # Create a user
    user = create_clubhouse_id(
        id_type=IDType.USER,
        metadata={
            "username": "brave_explorer",
            "email": "explorer@example.com",
            "join_date": time.time(),
            "preferences": {"theme": "dark", "notifications": True}
        }
    )
    
    # Create some quests
    quest1 = create_clubhouse_id(
        id_type=IDType.QUEST,
        metadata={
            "name": "Python Basics",
            "difficulty": "beginner",
            "estimated_time": 60,
            "prerequisites": []
        }
    )
    
    quest2 = create_clubhouse_id(
        id_type=IDType.QUEST,
        metadata={
            "name": "Web Development",
            "difficulty": "intermediate",
            "estimated_time": 120,
            "prerequisites": ["Python Basics"]
        }
    )
    
    print(f"Created clubhouse: {clubhouse.get_metadata('name')}")
    print(f"Created user: {user.get_metadata('username')}")
    print(f"Created quest 1: {quest1.get_metadata('name')}")
    print(f"Created quest 2: {quest2.get_metadata('name')}")
    
    # User joins the clubhouse
    membership_token = create_token_link(
        source_id=user.id_value,
        target_id=clubhouse.id_value,
        expires_in=86400,  # 24 hours
        relationship_type="membership",
        metadata={
            "membership_type": "basic",
            "joined_at": time.time(),
            "referred_by": None
        }
    )
    
    print(f"User joined clubhouse with token: {membership_token.token_value}")
    
    # User starts first quest
    quest1_token = create_token_link(
        source_id=user.id_value,
        target_id=quest1.id_value,
        expires_in=7200,  # 2 hours
        relationship_type="enrollment",
        metadata={
            "started_at": time.time(),
            "progress": 0,
            "status": "active"
        }
    )
    
    print(f"User started quest 1 with token: {quest1_token.token_value}")
    
    # Simulate quest progress
    time.sleep(1)  # Simulate some time passing
    
    # Update quest progress (metadata update)
    manager = get_id_manager()
    relationships = manager.get_relationships(
        source_id=user.id_value,
        target_id=quest1.id_value,
        relationship_type="enrollment"
    )
    
    if relationships:
        rel = relationships[0]
        print(f"Quest 1 progress: {rel.metadata.get('progress', 0)}%")
        
        # Simulate quest completion
        # In a real scenario, this would be updated through quest completion events
        print("Quest 1 completed!")
        
        # User can now start quest 2
        quest2_token = create_token_link(
            source_id=user.id_value,
            target_id=quest2.id_value,
            expires_in=7200,
            relationship_type="enrollment",
            metadata={
                "started_at": time.time(),
                "progress": 0,
                "status": "active",
                "prerequisite_completed": quest1.id_value
            }
        )
        
        print(f"User started quest 2 with token: {quest2_token.token_value}")
    
    # Show final user connections
    manager = get_id_manager()
    user_connections = manager.get_linked_ids(user.id_value)
    print(f"User is connected to {len(user_connections)} entities")
    
    user_relationships = manager.get_relationships(source_id=user.id_value)
    print("User relationships:")
    for rel in user_relationships:
        target_id_obj = manager.get_id(rel.target_id)
        target_name = target_id_obj.get_metadata('name') if target_id_obj else rel.target_id
        print(f"  - {rel.relationship_type}: {target_name}")


def main():
    """Main function to run all demonstrations."""
    print("Clubhouse ID System Demonstration")
    print("=" * 50)
    
    try:
        demonstrate_basic_usage()
        demonstrate_token_linking()
        demonstrate_relationship_queries()
        demonstrate_token_management()
        demonstrate_advanced_features()
        demonstrate_practical_scenario()
        
        print("\n" + "=" * 50)
        print("All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()