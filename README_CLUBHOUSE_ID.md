# Clubhouse ID System

This system provides a comprehensive ID management solution for the Clubhouse application, allowing you to create unique IDs and link them together using secure tokens.

## Features

- **Multiple ID Types**: Support for different types of IDs (clubhouse, user, session, quest, achievement, custom)
- **Token-Based Linking**: Securely link IDs together using cryptographic tokens
- **Expiration Management**: Tokens can have expiration times and be automatically cleaned up
- **Relationship Tracking**: Track relationships between IDs with metadata
- **Access Tracking**: Monitor ID usage with access counts and timestamps
- **Data Export/Import**: Serialize and deserialize ID data for persistence
- **Comprehensive Validation**: Ensure ID format integrity and security

## Core Components

### ClubhouseID
Represents a unique identifier with metadata and access tracking.

```python
from eosclubhouse.id_manager import create_clubhouse_id, IDType

# Create a user ID
user_id = create_clubhouse_id(
    id_type=IDType.USER,
    metadata={"username": "alice", "level": 5}
)

# Access metadata
username = user_id.get_metadata("username")
print(f"User: {username}, Level: {user_id.get_metadata('level')}")
```

### TokenID
Represents a secure token that links two IDs together.

```python
from eosclubhouse.id_manager import create_token_link

# Create a token linking user to quest
token = create_token_link(
    source_id=user_id.id_value,
    target_id=quest_id.id_value,
    expires_in=3600,  # 1 hour
    relationship_type="enrollment",
    metadata={"started_at": time.time()}
)
```

### IDManager
Central manager for all ID operations and relationships.

```python
from eosclubhouse.id_manager import get_id_manager

manager = get_id_manager()

# Get all IDs of a specific type
users = manager.get_ids_by_type(IDType.USER)

# Get relationships
relationships = manager.get_relationships(relationship_type="enrollment")
```

## Usage Examples

### Basic ID Creation

```python
from eosclubhouse.id_manager import create_clubhouse_id, IDType

# Create different types of IDs
clubhouse_id = create_clubhouse_id(
    id_type=IDType.CLUBHOUSE,
    metadata={"name": "Main Clubhouse", "capacity": 100}
)

user_id = create_clubhouse_id(
    id_type=IDType.USER,
    metadata={"username": "explorer", "email": "explorer@example.com"}
)

quest_id = create_clubhouse_id(
    id_type=IDType.QUEST,
    metadata={"title": "Python Adventure", "difficulty": "beginner"}
)
```

### Token-Based Linking

```python
from eosclubhouse.id_manager import create_token_link, verify_token_link

# User joins clubhouse
membership_token = create_token_link(
    source_id=user_id.id_value,
    target_id=clubhouse_id.id_value,
    expires_in=86400,  # 24 hours
    relationship_type="membership"
)

# User starts quest
quest_token = create_token_link(
    source_id=user_id.id_value,
    target_id=quest_id.id_value,
    expires_in=3600,  # 1 hour
    relationship_type="enrollment"
)

# Verify tokens
is_member = verify_token_link(membership_token.token_value)
is_enrolled = verify_token_link(quest_token.token_value)
```

### Relationship Queries

```python
from eosclubhouse.id_manager import get_id_manager

manager = get_id_manager()

# Get all IDs linked from a user
linked_ids = manager.get_linked_ids(user_id.id_value)

# Get all users linked to a clubhouse
members = manager.get_reverse_linked_ids(clubhouse_id.id_value)

# Get specific relationship types
enrollments = manager.get_relationships(relationship_type="enrollment")
```

### Token Management

```python
# Revoke a token
manager.revoke_token(token.token_value)

# Extend token expiry
token.extend_expiry(3600)  # Add 1 hour

# Clean up expired tokens
expired_count = manager.cleanup_expired_tokens()
```

## ID Types

- **CLUBHOUSE**: Main clubhouse entities
- **USER**: User accounts and profiles
- **SESSION**: User sessions and temporary states
- **QUEST**: Learning quests and activities
- **ACHIEVEMENT**: Unlocked achievements and badges
- **CUSTOM**: Custom application-specific IDs

## Token Status

- **ACTIVE**: Token is valid and can be used
- **EXPIRED**: Token has passed its expiration time
- **REVOKED**: Token has been manually revoked
- **PENDING**: Token is created but not yet active

## Security Features

- **Token Hashing**: Tokens are stored as SHA256 hashes for security
- **Validation**: All IDs must pass format validation
- **Expiration**: Automatic token expiration prevents stale access
- **Revocation**: Manual token revocation for security incidents

## Example: Complete User Journey

```python
from eosclubhouse.id_manager import *
import time

# Create entities
clubhouse = create_clubhouse_id(
    id_type=IDType.CLUBHOUSE,
    metadata={"name": "Adventure Academy", "capacity": 100}
)

user = create_clubhouse_id(
    id_type=IDType.USER,
    metadata={"username": "brave_explorer", "email": "user@example.com"}
)

quest = create_clubhouse_id(
    id_type=IDType.QUEST,
    metadata={"title": "Python Basics", "difficulty": "beginner"}
)

# User joins clubhouse
membership = create_token_link(
    source_id=user.id_value,
    target_id=clubhouse.id_value,
    expires_in=86400,  # 24 hours
    relationship_type="membership"
)

# User starts quest
enrollment = create_token_link(
    source_id=user.id_value,
    target_id=quest.id_value,
    expires_in=3600,  # 1 hour
    relationship_type="enrollment"
)

# Check user's connections
manager = get_id_manager()
connections = manager.get_linked_ids(user.id_value)
print(f"User is connected to {len(connections)} entities")

# Get statistics
stats = manager.get_statistics()
print(f"Total IDs: {stats['total_ids']}")
print(f"Active tokens: {stats['active_tokens']}")
```

## Testing

Run the unit tests to verify functionality:

```bash
python3 tests/test_id_manager.py
```

Run the example script to see the system in action:

```bash
python3 examples/clubhouse_id_example.py
```

## Files

- `eosclubhouse/id_manager.py`: Core ID management system
- `examples/clubhouse_id_example.py`: Comprehensive usage examples
- `tests/test_id_manager.py`: Unit tests for all functionality

## Integration

The ID system is designed to integrate seamlessly with the existing Clubhouse application. It uses GObject for compatibility with the GTK-based UI and provides both object-oriented and functional interfaces for ease of use.

## Performance

- Fast lookups using indexed data structures
- Efficient token verification using cryptographic hashing
- Automatic cleanup of expired tokens and relationships
- Minimal memory footprint with lazy loading

## Future Enhancements

- Database backend for persistent storage
- Token refresh mechanisms
- Role-based access control
- Audit logging for security events
- Integration with external authentication systems