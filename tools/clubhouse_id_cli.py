#!/usr/bin/env python3
#
# Copyright © 2024 Endless OS Foundation LLC.
#
# This file is part of clubhouse
# (see https://github.com/endlessm/clubhouse).
#
# Command-line interface for managing clubhouse IDs and token-based following
#

import argparse
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add the parent directory to path to import eosclubhouse modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eosclubhouse.clubhouse_id_manager import (
    ClubhouseIdManager, 
    get_clubhouse_id_manager,
    ClubhouseIdToken,
    ClubhouseFollowRelationship
)


def format_datetime(dt_str: str) -> str:
    """Format datetime string for display."""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str


def print_token_info(token: ClubhouseIdToken) -> None:
    """Print token information in a formatted way."""
    print(f"Token: {token.token}")
    print(f"  User ID: {token.user_id}")
    print(f"  Clubhouse ID: {token.clubhouse_id}")
    print(f"  Valid: {'Yes' if token.is_valid() else 'No'}")
    print(f"  Expires: {format_datetime(token.expires_at.isoformat())}")
    print(f"  Created: {format_datetime(token.created_at.isoformat())}")
    print(f"  Last Used: {format_datetime(token.last_used.isoformat())}")
    if token.metadata:
        print(f"  Metadata: {json.dumps(token.metadata, indent=2)}")
    print()


def print_relationship_info(rel: ClubhouseFollowRelationship) -> None:
    """Print relationship information in a formatted way."""
    print(f"Relationship: {rel.follower_id} -> {rel.following_id}")
    print(f"  Status: {rel.status}")
    print(f"  Via Token: {rel.followed_via_token}")
    print(f"  Created: {format_datetime(rel.created_at.isoformat())}")
    print(f"  Updated: {format_datetime(rel.updated_at.isoformat())}")
    print()


def cmd_generate_token(args) -> None:
    """Generate a new token for a user."""
    manager = get_clubhouse_id_manager()
    
    metadata = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print("Error: Invalid JSON metadata")
            return
    
    token = manager.generate_token(
        user_id=args.user_id,
        clubhouse_id=args.clubhouse_id,
        expires_days=args.expires_days,
        metadata=metadata
    )
    
    print(f"Generated token: {token}")
    print(f"Token will expire in {args.expires_days} days")


def cmd_validate_token(args) -> None:
    """Validate a token."""
    manager = get_clubhouse_id_manager()
    
    token_obj = manager.validate_token(args.token)
    if token_obj:
        print("Token is valid!")
        print_token_info(token_obj)
    else:
        print("Token is invalid or expired")


def cmd_follow(args) -> None:
    """Follow a user via token."""
    manager = get_clubhouse_id_manager()
    
    success = manager.follow_via_token(args.follower_id, args.token)
    if success:
        print(f"Successfully created follow relationship using token {args.token}")
    else:
        print("Failed to create follow relationship")


def cmd_unfollow(args) -> None:
    """Unfollow a user."""
    manager = get_clubhouse_id_manager()
    
    success = manager.unfollow(args.follower_id, args.following_id)
    if success:
        print(f"Successfully removed follow relationship: {args.follower_id} -> {args.following_id}")
    else:
        print("Follow relationship not found")


def cmd_list_tokens(args) -> None:
    """List tokens for a user."""
    manager = get_clubhouse_id_manager()
    
    if args.user_id:
        tokens = manager.get_user_tokens(args.user_id)
        print(f"Tokens for user {args.user_id}:")
    elif args.clubhouse_id:
        tokens = manager.get_tokens_by_clubhouse_id(args.clubhouse_id)
        print(f"Tokens for clubhouse ID {args.clubhouse_id}:")
    else:
        print("Error: Must specify either --user-id or --clubhouse-id")
        return
    
    if not tokens:
        print("No tokens found")
        return
    
    for token in tokens:
        print_token_info(token)


def cmd_list_following(args) -> None:
    """List users that a user is following."""
    manager = get_clubhouse_id_manager()
    
    relationships = manager.get_following_list(args.user_id)
    print(f"Users that {args.user_id} is following:")
    
    if not relationships:
        print("Not following anyone")
        return
    
    for rel in relationships:
        print_relationship_info(rel)


def cmd_list_followers(args) -> None:
    """List users that are following a user."""
    manager = get_clubhouse_id_manager()
    
    relationships = manager.get_followers_list(args.user_id)
    print(f"Users following {args.user_id}:")
    
    if not relationships:
        print("No followers")
        return
    
    for rel in relationships:
        print_relationship_info(rel)


def cmd_clubhouse_info(args) -> None:
    """Get information about a clubhouse ID."""
    manager = get_clubhouse_id_manager()
    
    info = manager.get_clubhouse_id_info(args.clubhouse_id)
    if not info:
        print(f"No information found for clubhouse ID {args.clubhouse_id}")
        return
    
    print(f"Clubhouse ID: {info['clubhouse_id']}")
    print(f"User ID: {info['user_id']}")
    print(f"Active Tokens: {info['active_tokens']}")
    print(f"Followers: {info['followers_count']}")
    print(f"Following: {info['following_count']}")
    print(f"Created: {format_datetime(info['created_at'])}")
    print(f"Last Used: {format_datetime(info['last_used'])}")
    if info['metadata']:
        print(f"Metadata: {json.dumps(info['metadata'], indent=2)}")


def cmd_revoke_token(args) -> None:
    """Revoke a specific token."""
    manager = get_clubhouse_id_manager()
    
    success = manager.revoke_token(args.token)
    if success:
        print(f"Successfully revoked token {args.token}")
    else:
        print("Token not found")


def cmd_revoke_user_tokens(args) -> None:
    """Revoke all tokens for a user."""
    manager = get_clubhouse_id_manager()
    
    count = manager.revoke_user_tokens(args.user_id)
    print(f"Revoked {count} tokens for user {args.user_id}")


def cmd_cleanup(args) -> None:
    """Clean up expired tokens."""
    manager = get_clubhouse_id_manager()
    
    count = manager.cleanup_expired_tokens()
    print(f"Cleaned up {count} expired tokens")


def cmd_statistics(args) -> None:
    """Show system statistics."""
    manager = get_clubhouse_id_manager()
    
    stats = manager.get_statistics()
    print("Clubhouse ID System Statistics:")
    print(f"  Active Tokens: {stats['active_tokens']}")
    print(f"  Total Tokens: {stats['total_tokens']}")
    print(f"  Active Relationships: {stats['active_relationships']}")
    print(f"  Total Relationships: {stats['total_relationships']}")
    print(f"  Unique Users: {stats['unique_users']}")


def cmd_demo(args) -> None:
    """Run a demonstration of the system."""
    manager = get_clubhouse_id_manager()
    
    print("=== Clubhouse ID Manager Demo ===\n")
    
    # Create some demo users
    print("1. Creating demo users and tokens...")
    
    # User 1: Alice
    alice_token = manager.generate_token(
        user_id="alice123",
        clubhouse_id="alice_clubhouse",
        metadata={"name": "Alice", "pathway": "art"}
    )
    print(f"   Generated token for Alice: {alice_token}")
    
    # User 2: Bob
    bob_token = manager.generate_token(
        user_id="bob456",
        clubhouse_id="bob_clubhouse",
        metadata={"name": "Bob", "pathway": "games"}
    )
    print(f"   Generated token for Bob: {bob_token}")
    
    # User 3: Charlie
    charlie_token = manager.generate_token(
        user_id="charlie789",
        clubhouse_id="charlie_clubhouse",
        metadata={"name": "Charlie", "pathway": "web"}
    )
    print(f"   Generated token for Charlie: {charlie_token}")
    
    print("\n2. Creating follow relationships...")
    
    # Alice follows Bob using Bob's token
    success = manager.follow_via_token("alice123", bob_token)
    print(f"   Alice follows Bob: {'Success' if success else 'Failed'}")
    
    # Charlie follows Alice using Alice's token
    success = manager.follow_via_token("charlie789", alice_token)
    print(f"   Charlie follows Alice: {'Success' if success else 'Failed'}")
    
    # Bob follows Charlie using Charlie's token
    success = manager.follow_via_token("bob456", charlie_token)
    print(f"   Bob follows Charlie: {'Success' if success else 'Failed'}")
    
    print("\n3. Displaying relationships...")
    
    # Show Alice's following list
    alice_following = manager.get_following_list("alice123")
    print(f"   Alice is following {len(alice_following)} users:")
    for rel in alice_following:
        print(f"     -> {rel.following_id} (via {rel.followed_via_token[:8]}...)")
    
    # Show Bob's followers
    bob_followers = manager.get_followers_list("bob456")
    print(f"   Bob has {len(bob_followers)} followers:")
    for rel in bob_followers:
        print(f"     <- {rel.follower_id} (via {rel.followed_via_token[:8]}...)")
    
    print("\n4. Getting clubhouse info...")
    
    # Get Alice's clubhouse info
    alice_info = manager.get_clubhouse_id_info("alice_clubhouse")
    if alice_info:
        print(f"   Alice's clubhouse info:")
        print(f"     Followers: {alice_info['followers_count']}")
        print(f"     Following: {alice_info['following_count']}")
        print(f"     Active tokens: {alice_info['active_tokens']}")
    
    print("\n5. System statistics...")
    stats = manager.get_statistics()
    print(f"   Active tokens: {stats['active_tokens']}")
    print(f"   Active relationships: {stats['active_relationships']}")
    print(f"   Unique users: {stats['unique_users']}")
    
    print("\n=== Demo Complete ===")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Clubhouse ID Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate token command
    gen_parser = subparsers.add_parser("generate", help="Generate a new token")
    gen_parser.add_argument("user_id", help="User ID")
    gen_parser.add_argument("clubhouse_id", help="Clubhouse ID")
    gen_parser.add_argument("--expires-days", type=int, default=30, help="Token expiration in days")
    gen_parser.add_argument("--metadata", help="JSON metadata")
    gen_parser.set_defaults(func=cmd_generate_token)
    
    # Validate token command
    val_parser = subparsers.add_parser("validate", help="Validate a token")
    val_parser.add_argument("token", help="Token to validate")
    val_parser.set_defaults(func=cmd_validate_token)
    
    # Follow command
    follow_parser = subparsers.add_parser("follow", help="Follow a user via token")
    follow_parser.add_argument("follower_id", help="Follower user ID")
    follow_parser.add_argument("token", help="Token of user to follow")
    follow_parser.set_defaults(func=cmd_follow)
    
    # Unfollow command
    unfollow_parser = subparsers.add_parser("unfollow", help="Unfollow a user")
    unfollow_parser.add_argument("follower_id", help="Follower user ID")
    unfollow_parser.add_argument("following_id", help="Following user ID")
    unfollow_parser.set_defaults(func=cmd_unfollow)
    
    # List tokens command
    list_tokens_parser = subparsers.add_parser("list-tokens", help="List tokens")
    list_tokens_group = list_tokens_parser.add_mutually_exclusive_group(required=True)
    list_tokens_group.add_argument("--user-id", help="User ID")
    list_tokens_group.add_argument("--clubhouse-id", help="Clubhouse ID")
    list_tokens_parser.set_defaults(func=cmd_list_tokens)
    
    # List following command
    following_parser = subparsers.add_parser("list-following", help="List users being followed")
    following_parser.add_argument("user_id", help="User ID")
    following_parser.set_defaults(func=cmd_list_following)
    
    # List followers command
    followers_parser = subparsers.add_parser("list-followers", help="List followers")
    followers_parser.add_argument("user_id", help="User ID")
    followers_parser.set_defaults(func=cmd_list_followers)
    
    # Clubhouse info command
    info_parser = subparsers.add_parser("info", help="Get clubhouse ID information")
    info_parser.add_argument("clubhouse_id", help="Clubhouse ID")
    info_parser.set_defaults(func=cmd_clubhouse_info)
    
    # Revoke token command
    revoke_parser = subparsers.add_parser("revoke-token", help="Revoke a specific token")
    revoke_parser.add_argument("token", help="Token to revoke")
    revoke_parser.set_defaults(func=cmd_revoke_token)
    
    # Revoke user tokens command
    revoke_user_parser = subparsers.add_parser("revoke-user", help="Revoke all tokens for a user")
    revoke_user_parser.add_argument("user_id", help="User ID")
    revoke_user_parser.set_defaults(func=cmd_revoke_user_tokens)
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up expired tokens")
    cleanup_parser.set_defaults(func=cmd_cleanup)
    
    # Statistics command
    stats_parser = subparsers.add_parser("stats", help="Show system statistics")
    stats_parser.set_defaults(func=cmd_statistics)
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run a demonstration")
    demo_parser.set_defaults(func=cmd_demo)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())