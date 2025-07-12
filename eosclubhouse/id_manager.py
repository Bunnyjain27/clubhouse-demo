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
from gi.repository import GObject

import uuid
import time
import hashlib
import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IDType(Enum):
    """Types of IDs that can be managed."""
    CLUBHOUSE = "clubhouse"
    USER = "user"
    SESSION = "session"
    QUEST = "quest"
    ACHIEVEMENT = "achievement"
    CUSTOM = "custom"


class TokenStatus(Enum):
    """Status of a token."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class IDRelationship:
    """Represents a relationship between two IDs via a token."""
    source_id: str
    target_id: str
    token_id: str
    relationship_type: str
    created_at: float
    expires_at: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def is_expired(self) -> bool:
        """Check if the relationship has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


class ClubhouseID(GObject.GObject):
    """Represents a clubhouse ID with metadata and validation."""
    
    __gtype_name__ = 'ClubhouseID'
    
    def __init__(self, id_value: str = None, id_type: IDType = IDType.CLUBHOUSE, 
                 metadata: Dict[str, Any] = None):
        super().__init__()
        
        self._id_value = id_value if id_value is not None else self._generate_id()
        self._id_type = id_type
        self._metadata = metadata or {}
        self._created_at = time.time()
        self._last_accessed = time.time()
        self._access_count = 0
        
        # Validate ID format
        if not self._validate_id():
            raise ValueError(f"Invalid ID format: {self._id_value}")
    
    def _generate_id(self) -> str:
        """Generate a unique ID using UUID4."""
        return str(uuid.uuid4())
    
    def _validate_id(self) -> bool:
        """Validate the ID format."""
        if not self._id_value or len(self._id_value.strip()) == 0:
            return False
        
        # Check if it's a valid UUID
        try:
            uuid.UUID(self._id_value)
            return True
        except ValueError:
            # Allow custom ID formats (alphanumeric with hyphens and underscores)
            # But ensure it's not empty and has valid characters
            if len(self._id_value) == 0:
                return False
            return all(c.isalnum() or c in '-_' for c in self._id_value)
    
    def access(self) -> None:
        """Update access tracking."""
        self._last_accessed = time.time()
        self._access_count += 1
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update metadata for this ID."""
        self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value for this ID."""
        return self._metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ID to dictionary representation."""
        return {
            'id': self._id_value,
            'type': self._id_type.value,
            'metadata': self._metadata,
            'created_at': self._created_at,
            'last_accessed': self._last_accessed,
            'access_count': self._access_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClubhouseID':
        """Create ClubhouseID from dictionary."""
        clubhouse_id = cls(
            id_value=data['id'],
            id_type=IDType(data['type']),
            metadata=data.get('metadata', {})
        )
        clubhouse_id._created_at = data.get('created_at', time.time())
        clubhouse_id._last_accessed = data.get('last_accessed', time.time())
        clubhouse_id._access_count = data.get('access_count', 0)
        return clubhouse_id
    
    @property
    def id_value(self) -> str:
        """Get the ID value."""
        self.access()
        return self._id_value
    
    @property
    def id_type(self) -> IDType:
        """Get the ID type."""
        return self._id_type
    
    @property
    def created_at(self) -> float:
        """Get creation timestamp."""
        return self._created_at
    
    @property
    def last_accessed(self) -> float:
        """Get last access timestamp."""
        return self._last_accessed
    
    @property
    def access_count(self) -> int:
        """Get access count."""
        return self._access_count
    
    def __str__(self) -> str:
        return f"ClubhouseID({self._id_value}, {self._id_type.value})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, ClubhouseID):
            return False
        return self._id_value == other._id_value and self._id_type == other._id_type


class TokenID(GObject.GObject):
    """Represents a token that links two IDs together."""
    
    __gtype_name__ = 'TokenID'
    
    def __init__(self, source_id: str, target_id: str, token_value: str = None,
                 expires_in: Optional[int] = None, metadata: Dict[str, Any] = None):
        super().__init__()
        
        self._source_id = source_id
        self._target_id = target_id
        self._token_value = token_value or self._generate_token()
        self._created_at = time.time()
        self._expires_at = (time.time() + expires_in) if expires_in else None
        self._status = TokenStatus.ACTIVE
        self._metadata = metadata or {}
        self._usage_count = 0
        
        # Generate token hash for security
        self._token_hash = self._hash_token(self._token_value)
    
    def _generate_token(self) -> str:
        """Generate a secure token."""
        return str(uuid.uuid4()) + "-" + str(int(time.time()))
    
    def _hash_token(self, token: str) -> str:
        """Generate SHA256 hash of the token."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def verify_token(self, token: str) -> bool:
        """Verify if the provided token matches this TokenID."""
        if self._status != TokenStatus.ACTIVE:
            return False
        
        if self.is_expired():
            self._status = TokenStatus.EXPIRED
            return False
        
        token_hash = self._hash_token(token)
        if token_hash == self._token_hash:
            self._usage_count += 1
            return True
        
        return False
    
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        if self._expires_at is None:
            return False
        return time.time() > self._expires_at
    
    def revoke(self) -> None:
        """Revoke the token."""
        self._status = TokenStatus.REVOKED
    
    def extend_expiry(self, additional_seconds: int) -> None:
        """Extend token expiry time."""
        if self._expires_at:
            self._expires_at += additional_seconds
        else:
            self._expires_at = time.time() + additional_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary representation."""
        return {
            'source_id': self._source_id,
            'target_id': self._target_id,
            'token_hash': self._token_hash,
            'created_at': self._created_at,
            'expires_at': self._expires_at,
            'status': self._status.value,
            'metadata': self._metadata,
            'usage_count': self._usage_count
        }
    
    @property
    def source_id(self) -> str:
        """Get source ID."""
        return self._source_id
    
    @property
    def target_id(self) -> str:
        """Get target ID."""
        return self._target_id
    
    @property
    def token_value(self) -> str:
        """Get token value (should be used carefully)."""
        return self._token_value
    
    @property
    def status(self) -> TokenStatus:
        """Get token status."""
        return self._status
    
    @property
    def created_at(self) -> float:
        """Get creation timestamp."""
        return self._created_at
    
    @property
    def expires_at(self) -> Optional[float]:
        """Get expiry timestamp."""
        return self._expires_at
    
    @property
    def usage_count(self) -> int:
        """Get usage count."""
        return self._usage_count
    
    def __str__(self) -> str:
        return f"TokenID({self._source_id} -> {self._target_id}, {self._status.value})"
    
    def __repr__(self) -> str:
        return self.__str__()


class IDManager(GObject.GObject):
    """Manages clubhouse IDs and their relationships via tokens."""
    
    __gtype_name__ = 'IDManager'
    
    def __init__(self):
        super().__init__()
        
        self._ids: Dict[str, ClubhouseID] = {}
        self._tokens: Dict[str, TokenID] = {}
        self._relationships: List[IDRelationship] = []
        
        # Index for quick lookups
        self._id_by_type: Dict[IDType, List[str]] = {id_type: [] for id_type in IDType}
        self._tokens_by_source: Dict[str, List[str]] = {}
        self._tokens_by_target: Dict[str, List[str]] = {}
    
    def create_id(self, id_type: IDType = IDType.CLUBHOUSE, 
                  id_value: str = None, metadata: Dict[str, Any] = None) -> ClubhouseID:
        """Create a new clubhouse ID."""
        clubhouse_id = ClubhouseID(id_value, id_type, metadata)
        
        # Store the ID
        self._ids[clubhouse_id.id_value] = clubhouse_id
        
        # Update index
        if clubhouse_id.id_value not in self._id_by_type[id_type]:
            self._id_by_type[id_type].append(clubhouse_id.id_value)
        
        logger.info(f"Created new ID: {clubhouse_id}")
        return clubhouse_id
    
    def get_id(self, id_value: str) -> Optional[ClubhouseID]:
        """Get a clubhouse ID by its value."""
        return self._ids.get(id_value)
    
    def get_ids_by_type(self, id_type: IDType) -> List[ClubhouseID]:
        """Get all IDs of a specific type."""
        id_values = self._id_by_type.get(id_type, [])
        return [self._ids[id_val] for id_val in id_values if id_val in self._ids]
    
    def create_token_link(self, source_id: str, target_id: str, 
                         expires_in: Optional[int] = None,
                         relationship_type: str = "linked",
                         metadata: Dict[str, Any] = None) -> TokenID:
        """Create a token that links two IDs."""
        # Validate that both IDs exist
        if source_id not in self._ids:
            raise ValueError(f"Source ID {source_id} does not exist")
        if target_id not in self._ids:
            raise ValueError(f"Target ID {target_id} does not exist")
        
        # Create the token
        token = TokenID(source_id, target_id, expires_in=expires_in, metadata=metadata)
        
        # Store the token
        self._tokens[token.token_value] = token
        
        # Update indices
        if source_id not in self._tokens_by_source:
            self._tokens_by_source[source_id] = []
        self._tokens_by_source[source_id].append(token.token_value)
        
        if target_id not in self._tokens_by_target:
            self._tokens_by_target[target_id] = []
        self._tokens_by_target[target_id].append(token.token_value)
        
        # Create relationship
        relationship = IDRelationship(
            source_id=source_id,
            target_id=target_id,
            token_id=token.token_value,
            relationship_type=relationship_type,
            created_at=time.time(),
            expires_at=token.expires_at,
            metadata=metadata
        )
        self._relationships.append(relationship)
        
        logger.info(f"Created token link: {source_id} -> {target_id} via {token.token_value}")
        return token
    
    def verify_token_link(self, token_value: str, source_id: str = None, 
                         target_id: str = None) -> bool:
        """Verify a token link between IDs."""
        token = self._tokens.get(token_value)
        if not token:
            return False
        
        # Verify the token itself
        if not token.verify_token(token_value):
            return False
        
        # Verify source and target if provided
        if source_id and token.source_id != source_id:
            return False
        if target_id and token.target_id != target_id:
            return False
        
        return True
    
    def get_linked_ids(self, source_id: str, active_only: bool = True) -> List[str]:
        """Get all IDs linked to a source ID."""
        token_values = self._tokens_by_source.get(source_id, [])
        linked_ids = []
        
        for token_value in token_values:
            token = self._tokens.get(token_value)
            if token:
                if active_only and (token.status != TokenStatus.ACTIVE or token.is_expired()):
                    continue
                linked_ids.append(token.target_id)
        
        return linked_ids
    
    def get_reverse_linked_ids(self, target_id: str, active_only: bool = True) -> List[str]:
        """Get all IDs that link to a target ID."""
        token_values = self._tokens_by_target.get(target_id, [])
        linked_ids = []
        
        for token_value in token_values:
            token = self._tokens.get(token_value)
            if token:
                if active_only and (token.status != TokenStatus.ACTIVE or token.is_expired()):
                    continue
                linked_ids.append(token.source_id)
        
        return linked_ids
    
    def get_relationships(self, source_id: str = None, target_id: str = None,
                         relationship_type: str = None, active_only: bool = True) -> List[IDRelationship]:
        """Get relationships based on criteria."""
        relationships = []
        
        for rel in self._relationships:
            if source_id and rel.source_id != source_id:
                continue
            if target_id and rel.target_id != target_id:
                continue
            if relationship_type and rel.relationship_type != relationship_type:
                continue
            if active_only and rel.is_expired():
                continue
            
            relationships.append(rel)
        
        return relationships
    
    def revoke_token(self, token_value: str) -> bool:
        """Revoke a token."""
        token = self._tokens.get(token_value)
        if token:
            token.revoke()
            logger.info(f"Revoked token: {token_value}")
            return True
        return False
    
    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens and return count of cleaned tokens."""
        expired_count = 0
        
        for token_value, token in list(self._tokens.items()):
            if token.is_expired():
                token.revoke()
                expired_count += 1
        
        # Remove expired relationships
        active_relationships = [rel for rel in self._relationships if not rel.is_expired()]
        removed_count = len(self._relationships) - len(active_relationships)
        self._relationships = active_relationships
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired tokens and {removed_count} relationships")
        
        return expired_count
    
    def export_data(self) -> Dict[str, Any]:
        """Export all data to a dictionary."""
        return {
            'ids': {id_val: cid.to_dict() for id_val, cid in self._ids.items()},
            'tokens': {token_val: token.to_dict() for token_val, token in self._tokens.items()},
            'relationships': [
                {
                    'source_id': rel.source_id,
                    'target_id': rel.target_id,
                    'token_id': rel.token_id,
                    'relationship_type': rel.relationship_type,
                    'created_at': rel.created_at,
                    'expires_at': rel.expires_at,
                    'metadata': rel.metadata
                }
                for rel in self._relationships
            ]
        }
    
    def import_data(self, data: Dict[str, Any]) -> None:
        """Import data from a dictionary."""
        # Clear existing data
        self._ids.clear()
        self._tokens.clear()
        self._relationships.clear()
        
        # Reset indices
        self._id_by_type = {id_type: [] for id_type in IDType}
        self._tokens_by_source.clear()
        self._tokens_by_target.clear()
        
        # Import IDs
        for id_val, id_data in data.get('ids', {}).items():
            clubhouse_id = ClubhouseID.from_dict(id_data)
            self._ids[id_val] = clubhouse_id
            self._id_by_type[clubhouse_id.id_type].append(id_val)
        
        # Import tokens (Note: actual token values are not stored for security)
        for token_val, token_data in data.get('tokens', {}).items():
            # We can't restore actual tokens from export due to security hashing
            logger.warning(f"Cannot restore token {token_val} from export - tokens must be recreated")
        
        # Import relationships
        for rel_data in data.get('relationships', []):
            relationship = IDRelationship(
                source_id=rel_data['source_id'],
                target_id=rel_data['target_id'],
                token_id=rel_data['token_id'],
                relationship_type=rel_data['relationship_type'],
                created_at=rel_data['created_at'],
                expires_at=rel_data.get('expires_at'),
                metadata=rel_data.get('metadata')
            )
            self._relationships.append(relationship)
        
        logger.info("Data imported successfully")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the ID manager."""
        stats = {
            'total_ids': len(self._ids),
            'total_tokens': len(self._tokens),
            'total_relationships': len(self._relationships),
            'ids_by_type': {id_type.value: len(ids) for id_type, ids in self._id_by_type.items()},
            'active_tokens': sum(1 for token in self._tokens.values() 
                               if token.status == TokenStatus.ACTIVE and not token.is_expired()),
            'expired_tokens': sum(1 for token in self._tokens.values() if token.is_expired()),
            'revoked_tokens': sum(1 for token in self._tokens.values() 
                                if token.status == TokenStatus.REVOKED),
            'active_relationships': len([rel for rel in self._relationships if not rel.is_expired()])
        }
        
        return stats
    
    def __str__(self) -> str:
        stats = self.get_statistics()
        return f"IDManager(IDs: {stats['total_ids']}, Tokens: {stats['total_tokens']}, Relations: {stats['total_relationships']})"
    
    def __repr__(self) -> str:
        return self.__str__()


# Global instance for easy access
_id_manager_instance = None


def get_id_manager() -> IDManager:
    """Get the global ID manager instance."""
    global _id_manager_instance
    if _id_manager_instance is None:
        _id_manager_instance = IDManager()
    return _id_manager_instance


def create_clubhouse_id(id_type: IDType = IDType.CLUBHOUSE, 
                       id_value: str = None, metadata: Dict[str, Any] = None) -> ClubhouseID:
    """Convenience function to create a clubhouse ID."""
    return get_id_manager().create_id(id_type, id_value, metadata)


def create_token_link(source_id: str, target_id: str, 
                     expires_in: Optional[int] = None,
                     relationship_type: str = "linked",
                     metadata: Dict[str, Any] = None) -> TokenID:
    """Convenience function to create a token link."""
    return get_id_manager().create_token_link(source_id, target_id, expires_in, 
                                            relationship_type, metadata)


def verify_token_link(token_value: str, source_id: str = None, 
                     target_id: str = None) -> bool:
    """Convenience function to verify a token link."""
    return get_id_manager().verify_token_link(token_value, source_id, target_id)