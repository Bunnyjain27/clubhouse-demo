#!/usr/bin/env python3
"""
Example usage of the Clubhouse ID Manager system.

This script demonstrates the complete functionality of the clubhouse ID and 
token-based following system, including:

1. Token generation and management
2. Following relationships via tokens
3. User management and statistics
4. Integration with the existing clubhouse system
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add the parent directory to path to import eosclubhouse modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eosclubhouse.clubhouse_id_manager import (
    ClubhouseIdManager,
    get_clubhouse_id_manager,
    ClubhouseIdToken,
    ClubhouseFollowRelationship
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Demonstrate basic usage of the clubhouse ID manager."""
    print("=== Basic Usage Example ===\n")
    
    # Get the manager instance
    manager = get_clubhouse_id_manager()
    
    # Create some users
    users = [
        {"user_id": "alice_2024", "clubhouse_id": "alice_art_studio", "name": "Alice", "pathway": "art"},
        {"user_id": "bob_games", "clubhouse_id": "bob_game_dev", "name": "Bob", "pathway": "games"},
        {"user_id": "charlie_web", "clubhouse_id": "charlie_web_design", "name": "Charlie", "pathway": "web"},
        {"user_id": "diana_os", "clubhouse_id": "diana_system_admin", "name": "Diana", "pathway": "os"},
    ]
    
    print("1. Creating users and generating tokens...")
    tokens = {}
    for user in users:
        metadata = {
            "name": user["name"],
            "pathway": user["pathway"],
            "created_via": "example_script"
        }
        token = manager.generate_token(
            user_id=user["user_id"],
            clubhouse_id=user["clubhouse_id"],
            expires_days=30,
            metadata=metadata
        )
        tokens[user["user_id"]] = token
        print(f"   {user['name']} ({user['user_id']}): {token[:8]}...")
    
    print("\n2. Creating follow relationships...")
    
    # Alice follows Bob
    success = manager.follow_via_token("alice_2024", tokens["bob_games"])
    print(f"   Alice follows Bob: {'Success' if success else 'Failed'}")
    
    # Bob follows Charlie
    success = manager.follow_via_token("bob_games", tokens["charlie_web"])
    print(f"   Bob follows Charlie: {'Success' if success else 'Failed'}")
    
    # Charlie follows Diana
    success = manager.follow_via_token("charlie_web", tokens["diana_os"])
    print(f"   Charlie follows Diana: {'Success' if success else 'Failed'}")
    
    # Diana follows Alice (creates a partial cycle)
    success = manager.follow_via_token("diana_os", tokens["alice_2024"])
    print(f"   Diana follows Alice: {'Success' if success else 'Failed'}")
    
    print("\n3. Querying relationships...")
    
    # Show who Alice is following
    alice_following = manager.get_following_list("alice_2024")
    print(f"   Alice is following {len(alice_following)} users:")
    for rel in alice_following:
        print(f"     -> {rel.following_id} (since {rel.created_at.strftime('%Y-%m-%d')})")
    
    # Show Alice's followers
    alice_followers = manager.get_followers_list("alice_2024")
    print(f"   Alice has {len(alice_followers)} followers:")
    for rel in alice_followers:
        print(f"     <- {rel.follower_id} (since {rel.created_at.strftime('%Y-%m-%d')})")
    
    print("\n4. Token validation...")
    
    # Validate Alice's token
    alice_token = tokens["alice_2024"]
    token_obj = manager.validate_token(alice_token)
    if token_obj:
        print(f"   Alice's token is valid, expires in {(token_obj.expires_at - datetime.now()).days} days")
    else:
        print("   Alice's token is invalid")
    
    print("\n5. Getting clubhouse information...")
    
    # Get Alice's clubhouse info
    alice_info = manager.get_clubhouse_id_info("alice_art_studio")
    if alice_info:
        print(f"   Alice's clubhouse info:")
        print(f"     Followers: {alice_info['followers_count']}")
        print(f"     Following: {alice_info['following_count']}")
        print(f"     Active tokens: {alice_info['active_tokens']}")
    
    return tokens


def example_advanced_features():
    """Demonstrate advanced features of the clubhouse ID manager."""
    print("\n=== Advanced Features Example ===\n")
    
    manager = get_clubhouse_id_manager()
    
    print("1. Token management...")
    
    # Generate a short-lived token
    short_token = manager.generate_token(
        user_id="temp_user",
        clubhouse_id="temp_clubhouse",
        expires_days=1,
        metadata={"type": "temporary", "purpose": "testing"}
    )
    print(f"   Generated temporary token: {short_token[:8]}...")
    
    # Get all tokens for a user
    user_tokens = manager.get_user_tokens("temp_user")
    print(f"   User has {len(user_tokens)} active tokens")
    
    # Revoke the token
    success = manager.revoke_token(short_token)
    print(f"   Token revocation: {'Success' if success else 'Failed'}")
    
    print("\n2. Relationship management...")
    
    # Try to follow yourself (should fail)
    alice_token = manager.get_user_tokens("alice_2024")[0].token
    success = manager.follow_via_token("alice_2024", alice_token)
    print(f"   Alice tries to follow herself: {'Success' if success else 'Failed (as expected)'}")
    
    # Unfollow someone
    success = manager.unfollow("alice_2024", "bob_games")
    print(f"   Alice unfollows Bob: {'Success' if success else 'Failed'}")
    
    print("\n3. System statistics...")
    
    stats = manager.get_statistics()
    print(f"   System statistics:")
    print(f"     Active tokens: {stats['active_tokens']}")
    print(f"     Total tokens: {stats['total_tokens']}")
    print(f"     Active relationships: {stats['active_relationships']}")
    print(f"     Total relationships: {stats['total_relationships']}")
    print(f"     Unique users: {stats['unique_users']}")
    
    print("\n4. Cleanup operations...")
    
    # Clean up expired tokens
    expired_count = manager.cleanup_expired_tokens()
    print(f"   Cleaned up {expired_count} expired tokens")


def example_integration_with_existing_system():
    """Demonstrate integration with existing clubhouse components."""
    print("\n=== Integration Example ===\n")
    
    # This would typically be integrated with the existing Character system
    # from the clubhouse.py file
    
    print("1. Integration with Character system...")
    
    # Simulate getting character information
    character_info = {
        'estelle': {
            'username': 'lightspeedgal',
            'pathway': 'art',
            'pathway_title': 'Art'
        },
        'ada': {
            'username': 'countesslovelace',
            'pathway': 'games',
            'pathway_title': 'Games'
        }
    }
    
    manager = get_clubhouse_id_manager()
    
    # Generate tokens for existing characters
    for char_id, char_info in character_info.items():
        metadata = {
            "character_id": char_id,
            "username": char_info["username"],
            "pathway": char_info["pathway"],
            "pathway_title": char_info["pathway_title"],
            "integrated_with": "clubhouse_character_system"
        }
        
        token = manager.generate_token(
            user_id=char_info["username"],
            clubhouse_id=f"{char_id}_clubhouse",
            expires_days=90,  # Longer expiration for established characters
            metadata=metadata
        )
        
        print(f"   Generated token for {char_info['username']} ({char_id}): {token[:8]}...")
    
    print("\n2. Integration with Quest system...")
    
    # Simulate a quest that creates following relationships
    quest_metadata = {
        "quest_name": "social_connections",
        "quest_type": "following_quest",
        "auto_generated": True
    }
    
    # Estelle follows Ada as part of a quest
    ada_tokens = manager.get_tokens_by_clubhouse_id("ada_clubhouse")
    if ada_tokens:
        success = manager.follow_via_token("lightspeedgal", ada_tokens[0].token)
        print(f"   Quest-based following (Estelle -> Ada): {'Success' if success else 'Failed'}")
    
    print("\n3. Integration with Achievements system...")
    
    # Simulate achievement unlocked for social connections
    lightspeedgal_followers = manager.get_followers_list("lightspeedgal")
    lightspeedgal_following = manager.get_following_list("lightspeedgal")
    
    total_connections = len(lightspeedgal_followers) + len(lightspeedgal_following)
    print(f"   Estelle has {total_connections} total social connections")
    
    if total_connections >= 1:
        print("   Achievement unlocked: 'Social Butterfly' - Made your first connection!")
    
    if len(lightspeedgal_followers) >= 1:
        print("   Achievement unlocked: 'Inspiring Leader' - Someone is following you!")


def example_error_handling():
    """Demonstrate error handling and edge cases."""
    print("\n=== Error Handling Example ===\n")
    
    manager = get_clubhouse_id_manager()
    
    print("1. Invalid token handling...")
    
    # Try to validate a non-existent token
    invalid_token = "invalid-token-12345"
    token_obj = manager.validate_token(invalid_token)
    print(f"   Validating invalid token: {'Valid' if token_obj else 'Invalid (as expected)'}")
    
    # Try to follow with invalid token
    success = manager.follow_via_token("alice_2024", invalid_token)
    print(f"   Following with invalid token: {'Success' if success else 'Failed (as expected)'}")
    
    print("\n2. Duplicate relationship handling...")
    
    # Try to create duplicate relationship
    alice_tokens = manager.get_user_tokens("alice_2024")
    bob_tokens = manager.get_user_tokens("bob_games")
    
    if alice_tokens and bob_tokens:
        # Create initial relationship
        success1 = manager.follow_via_token("alice_2024", bob_tokens[0].token)
        print(f"   First follow attempt: {'Success' if success1 else 'Failed'}")
        
        # Try to create duplicate
        success2 = manager.follow_via_token("alice_2024", bob_tokens[0].token)
        print(f"   Duplicate follow attempt: {'Success' if success2 else 'Failed'}")
    
    print("\n3. Non-existent user handling...")
    
    # Try to get relationships for non-existent user
    following = manager.get_following_list("non_existent_user")
    followers = manager.get_followers_list("non_existent_user")
    print(f"   Non-existent user following: {len(following)} (expected 0)")
    print(f"   Non-existent user followers: {len(followers)} (expected 0)")


def example_performance_and_scalability():
    """Demonstrate performance considerations and scalability."""
    print("\n=== Performance and Scalability Example ===\n")
    
    manager = get_clubhouse_id_manager()
    
    print("1. Bulk operations...")
    
    # Generate multiple tokens quickly
    start_time = datetime.now()
    bulk_tokens = []
    
    for i in range(10):
        token = manager.generate_token(
            user_id=f"bulk_user_{i}",
            clubhouse_id=f"bulk_clubhouse_{i}",
            expires_days=30,
            metadata={"bulk_generated": True, "index": i}
        )
        bulk_tokens.append(token)
    
    end_time = datetime.now()
    print(f"   Generated {len(bulk_tokens)} tokens in {(end_time - start_time).total_seconds():.2f} seconds")
    
    print("\n2. Bulk relationship creation...")
    
    # Create a following network
    start_time = datetime.now()
    relationship_count = 0
    
    for i in range(len(bulk_tokens)):
        for j in range(len(bulk_tokens)):
            if i != j:  # Don't follow yourself
                success = manager.follow_via_token(f"bulk_user_{i}", bulk_tokens[j])
                if success:
                    relationship_count += 1
    
    end_time = datetime.now()
    print(f"   Created {relationship_count} relationships in {(end_time - start_time).total_seconds():.2f} seconds")
    
    print("\n3. System performance statistics...")
    
    stats = manager.get_statistics()
    print(f"   Current system load:")
    print(f"     Active tokens: {stats['active_tokens']}")
    print(f"     Active relationships: {stats['active_relationships']}")
    print(f"     Memory usage: {len(manager._tokens_cache)} tokens in cache")
    print(f"     Relationship cache: {len(manager._relationships_cache)} users with relationships")


def main():
    """Main function to run all examples."""
    print("Clubhouse ID Manager - Comprehensive Example")
    print("=" * 50)
    
    try:
        # Run basic usage example
        tokens = example_basic_usage()
        
        # Run advanced features example
        example_advanced_features()
        
        # Run integration example
        example_integration_with_existing_system()
        
        # Run error handling example
        example_error_handling()
        
        # Run performance example
        example_performance_and_scalability()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
        # Final system statistics
        manager = get_clubhouse_id_manager()
        final_stats = manager.get_statistics()
        print(f"\nFinal system state:")
        print(f"  Active tokens: {final_stats['active_tokens']}")
        print(f"  Active relationships: {final_stats['active_relationships']}")
        print(f"  Unique users: {final_stats['unique_users']}")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())