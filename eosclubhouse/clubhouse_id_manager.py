#!/usr/bin/env python3
#
# Copyright © 2024 Endless OS Foundation LLC.
#
# This file is part of clubhouse
# (see https://github.com/endlessm/clubhouse).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import gi
gi.require_version('GObject', '2.0')
gi.require_version('Json', '1.0')

import json
import logging
import os
import sqlite3
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from gi.repository import GObject, Json
from eosclubhouse import config, utils
from eosclubhouse.utils import ClubhouseState

logger = logging.getLogger(__name__)


class ClubhouseIdToken:
    """Represents a clubhouse ID token for user identification and following."""
    
    def __init__(self, token: str, user_id: str, clubhouse_id: str, 
                 expires_at: Optional[datetime] = None, metadata: Optional[Dict] = None):
        self.token = token
        self.user_id = user_id
        self.clubhouse_id = clubhouse_id
        self.expires_at = expires_at or (datetime.now() + timedelta(days=30))
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.last_used = datetime.now()
    
    def is_valid(self) -> bool:
        """Check if the token is still valid."""
        return datetime.now() < self.expires_at
    
    def refresh(self, days: int = 30) -> None:
        """Refresh the token expiration."""
        self.expires_at = datetime.now() + timedelta(days=days)
        self.last_used = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary for storage."""
        return {
            'token': self.token,
            'user_id': self.user_id,
            'clubhouse_id': self.clubhouse_id,
            'expires_at': self.expires_at.isoformat(),
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClubhouseIdToken':
        """Create token from dictionary."""
        token = cls(
            token=data['token'],
            user_id=data['user_id'],
            clubhouse_id=data['clubhouse_id'],
            expires_at=datetime.fromisoformat(data['expires_at']),
            metadata=data.get('metadata', {})
        )
        token.created_at = datetime.fromisoformat(data['created_at'])
        token.last_used = datetime.fromisoformat(data['last_used'])
        return token


class ClubhouseFollowRelationship:
    """Represents a following relationship between clubhouse users."""
    
    def __init__(self, follower_id: str, following_id: str, 
                 followed_via_token: str, status: str = 'active'):
        self.follower_id = follower_id
        self.following_id = following_id
        self.followed_via_token = followed_via_token
        self.status = status  # active, pending, blocked
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary."""
        return {
            'follower_id': self.follower_id,
            'following_id': self.following_id,
            'followed_via_token': self.followed_via_token,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClubhouseFollowRelationship':
        """Create relationship from dictionary."""
        rel = cls(
            follower_id=data['follower_id'],
            following_id=data['following_id'],
            followed_via_token=data['followed_via_token'],
            status=data.get('status', 'active')
        )
        rel.created_at = datetime.fromisoformat(data['created_at'])
        rel.updated_at = datetime.fromisoformat(data['updated_at'])
        return rel


class ClubhouseIdManager(GObject.GObject):
    """Manages clubhouse IDs and token-based following relationships."""
    
    __gsignals__ = {
        'token-created': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str)
        ),
        'token-used': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str)
        ),
        'follow-relationship-created': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str, str)
        ),
        'follow-relationship-updated': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str, str)
        ),
    }
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__()
        self.db_path = db_path or os.path.join(config.USER_DIR, 'clubhouse_ids.db')
        self._ensure_db_exists()
        self._tokens_cache: Dict[str, ClubhouseIdToken] = {}
        self._relationships_cache: Dict[str, List[ClubhouseFollowRelationship]] = {}
        self._load_cache()
    
    def _ensure_db_exists(self) -> None:
        """Ensure the database and tables exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS clubhouse_tokens (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    clubhouse_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    last_used TEXT NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS follow_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    follower_id TEXT NOT NULL,
                    following_id TEXT NOT NULL,
                    followed_via_token TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(follower_id, following_id)
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_tokens_user_id 
                ON clubhouse_tokens(user_id)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_tokens_clubhouse_id 
                ON clubhouse_tokens(clubhouse_id)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_relationships_follower 
                ON follow_relationships(follower_id)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_relationships_following 
                ON follow_relationships(following_id)
            ''')
    
    def _load_cache(self) -> None:
        """Load tokens and relationships into cache."""
        with sqlite3.connect(self.db_path) as conn:
            # Load tokens
            cursor = conn.execute('''
                SELECT token, user_id, clubhouse_id, expires_at, metadata, created_at, last_used
                FROM clubhouse_tokens
                WHERE expires_at > datetime('now')
            ''')
            
            for row in cursor.fetchall():
                token_data = {
                    'token': row[0],
                    'user_id': row[1],
                    'clubhouse_id': row[2],
                    'expires_at': row[3],
                    'metadata': json.loads(row[4]) if row[4] else {},
                    'created_at': row[5],
                    'last_used': row[6]
                }
                token = ClubhouseIdToken.from_dict(token_data)
                self._tokens_cache[token.token] = token
            
            # Load relationships
            cursor = conn.execute('''
                SELECT follower_id, following_id, followed_via_token, status, created_at, updated_at
                FROM follow_relationships
                WHERE status = 'active'
            ''')
            
            for row in cursor.fetchall():
                rel_data = {
                    'follower_id': row[0],
                    'following_id': row[1],
                    'followed_via_token': row[2],
                    'status': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                }
                relationship = ClubhouseFollowRelationship.from_dict(rel_data)
                
                if relationship.follower_id not in self._relationships_cache:
                    self._relationships_cache[relationship.follower_id] = []
                self._relationships_cache[relationship.follower_id].append(relationship)
    
    def generate_token(self, user_id: str, clubhouse_id: str, 
                      expires_days: int = 30, metadata: Optional[Dict] = None) -> str:
        """Generate a new token for a user."""
        token = str(uuid.uuid4())
        
        # Check if token already exists (extremely unlikely)
        while token in self._tokens_cache:
            token = str(uuid.uuid4())
        
        token_obj = ClubhouseIdToken(
            token=token,
            user_id=user_id,
            clubhouse_id=clubhouse_id,
            expires_at=datetime.now() + timedelta(days=expires_days),
            metadata=metadata or {}
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO clubhouse_tokens 
                (token, user_id, clubhouse_id, expires_at, metadata, created_at, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                token_obj.token,
                token_obj.user_id,
                token_obj.clubhouse_id,
                token_obj.expires_at.isoformat(),
                json.dumps(token_obj.metadata),
                token_obj.created_at.isoformat(),
                token_obj.last_used.isoformat()
            ))
        
        # Update cache
        self._tokens_cache[token] = token_obj
        
        self.emit('token-created', user_id, token)
        logger.info(f"Generated token {token} for user {user_id} with clubhouse ID {clubhouse_id}")
        
        return token
    
    def validate_token(self, token: str) -> Optional[ClubhouseIdToken]:
        """Validate a token and return the token object if valid."""
        if token not in self._tokens_cache:
            return None
        
        token_obj = self._tokens_cache[token]
        if not token_obj.is_valid():
            # Remove expired token
            del self._tokens_cache[token]
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM clubhouse_tokens WHERE token = ?', (token,))
            return None
        
        # Update last used
        token_obj.last_used = datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE clubhouse_tokens SET last_used = ? WHERE token = ?
            ''', (token_obj.last_used.isoformat(), token))
        
        self.emit('token-used', token_obj.user_id, token)
        return token_obj
    
    def get_user_tokens(self, user_id: str) -> List[ClubhouseIdToken]:
        """Get all valid tokens for a user."""
        tokens = []
        for token_obj in self._tokens_cache.values():
            if token_obj.user_id == user_id and token_obj.is_valid():
                tokens.append(token_obj)
        return tokens
    
    def get_tokens_by_clubhouse_id(self, clubhouse_id: str) -> List[ClubhouseIdToken]:
        """Get all valid tokens for a clubhouse ID."""
        tokens = []
        for token_obj in self._tokens_cache.values():
            if token_obj.clubhouse_id == clubhouse_id and token_obj.is_valid():
                tokens.append(token_obj)
        return tokens
    
    def follow_via_token(self, follower_id: str, token: str) -> bool:
        """Create a follow relationship using a token."""
        token_obj = self.validate_token(token)
        if not token_obj:
            logger.warning(f"Invalid token {token} used for following")
            return False
        
        if follower_id == token_obj.user_id:
            logger.warning(f"User {follower_id} cannot follow themselves")
            return False
        
        # Check if relationship already exists
        existing_rel = self.get_follow_relationship(follower_id, token_obj.user_id)
        if existing_rel:
            logger.info(f"Follow relationship already exists between {follower_id} and {token_obj.user_id}")
            return True
        
        # Create new relationship
        relationship = ClubhouseFollowRelationship(
            follower_id=follower_id,
            following_id=token_obj.user_id,
            followed_via_token=token,
            status='active'
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO follow_relationships 
                (follower_id, following_id, followed_via_token, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                relationship.follower_id,
                relationship.following_id,
                relationship.followed_via_token,
                relationship.status,
                relationship.created_at.isoformat(),
                relationship.updated_at.isoformat()
            ))
        
        # Update cache
        if follower_id not in self._relationships_cache:
            self._relationships_cache[follower_id] = []
        self._relationships_cache[follower_id].append(relationship)
        
        self.emit('follow-relationship-created', follower_id, token_obj.user_id, token)
        logger.info(f"Created follow relationship: {follower_id} -> {token_obj.user_id} via token {token}")
        
        return True
    
    def get_follow_relationship(self, follower_id: str, following_id: str) -> Optional[ClubhouseFollowRelationship]:
        """Get a specific follow relationship."""
        if follower_id not in self._relationships_cache:
            return None
        
        for rel in self._relationships_cache[follower_id]:
            if rel.following_id == following_id and rel.status == 'active':
                return rel
        
        return None
    
    def get_following_list(self, user_id: str) -> List[ClubhouseFollowRelationship]:
        """Get list of users that a user is following."""
        return self._relationships_cache.get(user_id, [])
    
    def get_followers_list(self, user_id: str) -> List[ClubhouseFollowRelationship]:
        """Get list of users that are following a user."""
        followers = []
        for relationships in self._relationships_cache.values():
            for rel in relationships:
                if rel.following_id == user_id and rel.status == 'active':
                    followers.append(rel)
        return followers
    
    def unfollow(self, follower_id: str, following_id: str) -> bool:
        """Remove a follow relationship."""
        relationship = self.get_follow_relationship(follower_id, following_id)
        if not relationship:
            return False
        
        # Update status in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE follow_relationships 
                SET status = 'inactive', updated_at = ?
                WHERE follower_id = ? AND following_id = ?
            ''', (datetime.now().isoformat(), follower_id, following_id))
        
        # Remove from cache
        if follower_id in self._relationships_cache:
            self._relationships_cache[follower_id] = [
                rel for rel in self._relationships_cache[follower_id]
                if not (rel.following_id == following_id and rel.status == 'active')
            ]
        
        self.emit('follow-relationship-updated', follower_id, following_id, 'inactive')
        logger.info(f"Removed follow relationship: {follower_id} -> {following_id}")
        
        return True
    
    def get_clubhouse_id_info(self, clubhouse_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a clubhouse ID."""
        tokens = self.get_tokens_by_clubhouse_id(clubhouse_id)
        if not tokens:
            return None
        
        # Get the most recent token
        latest_token = max(tokens, key=lambda t: t.created_at)
        
        followers = self.get_followers_list(latest_token.user_id)
        following = self.get_following_list(latest_token.user_id)
        
        return {
            'clubhouse_id': clubhouse_id,
            'user_id': latest_token.user_id,
            'active_tokens': len(tokens),
            'followers_count': len(followers),
            'following_count': len(following),
            'created_at': latest_token.created_at.isoformat(),
            'last_used': latest_token.last_used.isoformat(),
            'metadata': latest_token.metadata
        }
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a specific token."""
        if token not in self._tokens_cache:
            return False
        
        # Remove from database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM clubhouse_tokens WHERE token = ?', (token,))
        
        # Remove from cache
        del self._tokens_cache[token]
        
        logger.info(f"Revoked token {token}")
        return True
    
    def revoke_user_tokens(self, user_id: str) -> int:
        """Revoke all tokens for a user."""
        tokens_to_revoke = [token for token, obj in self._tokens_cache.items() if obj.user_id == user_id]
        
        if not tokens_to_revoke:
            return 0
        
        # Remove from database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM clubhouse_tokens WHERE user_id = ?', (user_id,))
        
        # Remove from cache
        for token in tokens_to_revoke:
            del self._tokens_cache[token]
        
        logger.info(f"Revoked {len(tokens_to_revoke)} tokens for user {user_id}")
        return len(tokens_to_revoke)
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from database and cache."""
        expired_tokens = []
        
        for token, token_obj in self._tokens_cache.items():
            if not token_obj.is_valid():
                expired_tokens.append(token)
        
        if not expired_tokens:
            return 0
        
        # Remove from database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                DELETE FROM clubhouse_tokens 
                WHERE expires_at <= datetime('now')
            ''')
        
        # Remove from cache
        for token in expired_tokens:
            del self._tokens_cache[token]
        
        logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
        return len(expired_tokens)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the token and following system."""
        active_tokens = len(self._tokens_cache)
        total_relationships = sum(len(rels) for rels in self._relationships_cache.values())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM clubhouse_tokens')
            total_tokens = cursor.fetchone()[0]
            
            cursor = conn.execute('SELECT COUNT(*) FROM follow_relationships')
            total_all_relationships = cursor.fetchone()[0]
        
        return {
            'active_tokens': active_tokens,
            'total_tokens': total_tokens,
            'active_relationships': total_relationships,
            'total_relationships': total_all_relationships,
            'unique_users': len(set(token.user_id for token in self._tokens_cache.values()))
        }


# Global instance
_clubhouse_id_manager = None


def get_clubhouse_id_manager() -> ClubhouseIdManager:
    """Get the global clubhouse ID manager instance."""
    global _clubhouse_id_manager
    if _clubhouse_id_manager is None:
        _clubhouse_id_manager = ClubhouseIdManager()
    return _clubhouse_id_manager