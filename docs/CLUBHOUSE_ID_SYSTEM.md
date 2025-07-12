# Clubhouse ID and Token-Based Following System

## Overview

The Clubhouse ID and Token-Based Following System is a comprehensive solution for managing user identities and social connections within the Endless OS Clubhouse application. This system enables users to:

- Generate unique tokens for their clubhouse IDs
- Follow other users via token numbers
- Manage following relationships
- Track social connections and statistics

## Features

### 🔑 Token Management
- **Unique Token Generation**: Each user can generate UUID-based tokens for their clubhouse ID
- **Token Expiration**: Configurable expiration dates (default: 30 days)
- **Token Validation**: Real-time validation and automatic cleanup of expired tokens
- **Token Revocation**: Users can revoke tokens individually or in bulk
- **Metadata Support**: Attach custom metadata to tokens for enhanced functionality

### 👥 Following System
- **Token-Based Following**: Users follow each other using tokens instead of direct usernames
- **Privacy Protection**: Tokens can be shared selectively without exposing user details
- **Relationship Management**: Create, query, and remove following relationships
- **Bidirectional Tracking**: Track both followers and following lists
- **Status Management**: Support for active, inactive, and other relationship states

### 📊 Statistics and Analytics
- **System Statistics**: Track active tokens, relationships, and users
- **User Analytics**: Individual user statistics (followers, following, tokens)
- **Performance Metrics**: Monitor system performance and usage patterns
- **Clubhouse Information**: Detailed information about specific clubhouse IDs

### 🔒 Security and Privacy
- **Token-Based Authentication**: No direct exposure of user IDs or personal information
- **Configurable Expiration**: Tokens expire automatically for enhanced security
- **Relationship Control**: Users have full control over their following relationships
- **Data Isolation**: Each user's data is properly isolated and secured

## Architecture

### Core Components

#### 1. ClubhouseIdToken
Represents a token for user identification and following.

```python
class ClubhouseIdToken:
    def __init__(self, token, user_id, clubhouse_id, expires_at, metadata):
        self.token = token              # UUID-based token
        self.user_id = user_id          # Internal user ID
        self.clubhouse_id = clubhouse_id # Public clubhouse ID
        self.expires_at = expires_at    # Expiration datetime
        self.metadata = metadata        # Custom metadata
```

#### 2. ClubhouseFollowRelationship
Represents a following relationship between users.

```python
class ClubhouseFollowRelationship:
    def __init__(self, follower_id, following_id, followed_via_token, status):
        self.follower_id = follower_id           # User who follows
        self.following_id = following_id         # User being followed
        self.followed_via_token = followed_via_token  # Token used to follow
        self.status = status                     # Relationship status
```

#### 3. ClubhouseIdManager
Main management class for the entire system.

```python
class ClubhouseIdManager(GObject.GObject):
    # Core functionality
    def generate_token(self, user_id, clubhouse_id, expires_days=30, metadata=None)
    def validate_token(self, token)
    def follow_via_token(self, follower_id, token)
    def get_following_list(self, user_id)
    def get_followers_list(self, user_id)
    # ... and many more methods
```

### Database Schema

The system uses SQLite for persistent storage with the following tables:

#### clubhouse_tokens
```sql
CREATE TABLE clubhouse_tokens (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    clubhouse_id TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT NOT NULL,
    last_used TEXT NOT NULL
);
```

#### follow_relationships
```sql
CREATE TABLE follow_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    follower_id TEXT NOT NULL,
    following_id TEXT NOT NULL,
    followed_via_token TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(follower_id, following_id)
);
```

## Installation and Setup

### 1. Dependencies

The system requires the following Python packages:
- `gi` (GObject Introspection)
- `sqlite3` (built-in)
- `uuid` (built-in)
- `json` (built-in)
- `datetime` (built-in)

### 2. Integration with Existing Clubhouse

Add the following import to your clubhouse code:

```python
from eosclubhouse.clubhouse_id_manager import get_clubhouse_id_manager
```

### 3. Database Initialization

The database is automatically created when the manager is first instantiated:

```python
manager = get_clubhouse_id_manager()
# Database is created at ~/.local/share/eos-clubhouse/clubhouse_ids.db
```

## Usage Examples

### Basic Usage

```python
from eosclubhouse.clubhouse_id_manager import get_clubhouse_id_manager

# Get the manager
manager = get_clubhouse_id_manager()

# Generate a token
token = manager.generate_token(
    user_id="alice123",
    clubhouse_id="alice_art_studio",
    expires_days=30,
    metadata={"name": "Alice", "pathway": "art"}
)

# Follow someone using their token
success = manager.follow_via_token("bob456", token)

# Get following list
following = manager.get_following_list("alice123")
```

### Advanced Features

```python
# Get all tokens for a user
tokens = manager.get_user_tokens("alice123")

# Get followers
followers = manager.get_followers_list("alice123")

# Get clubhouse information
info = manager.get_clubhouse_id_info("alice_art_studio")

# System statistics
stats = manager.get_statistics()
```

### Error Handling

```python
# Validate token before use
token_obj = manager.validate_token(token)
if token_obj:
    print(f"Token is valid, expires in {(token_obj.expires_at - datetime.now()).days} days")
else:
    print("Token is invalid or expired")

# Handle following errors
success = manager.follow_via_token("user1", "invalid_token")
if not success:
    print("Failed to follow user - invalid token or other error")
```

## Command Line Interface

A comprehensive CLI tool is provided for managing the system:

### Installation

```bash
# Make the CLI tool executable
chmod +x tools/clubhouse_id_cli.py
```

### Usage

```bash
# Generate a token
python3 tools/clubhouse_id_cli.py generate alice123 alice_art_studio --expires-days 30

# Follow someone via token
python3 tools/clubhouse_id_cli.py follow bob456 <token>

# List tokens
python3 tools/clubhouse_id_cli.py list-tokens --user-id alice123

# Get system statistics
python3 tools/clubhouse_id_cli.py stats

# Run demonstration
python3 tools/clubhouse_id_cli.py demo
```

### Available Commands

| Command | Description |
|---------|-------------|
| `generate` | Generate a new token |
| `validate` | Validate a token |
| `follow` | Follow a user via token |
| `unfollow` | Unfollow a user |
| `list-tokens` | List tokens for a user |
| `list-following` | List users being followed |
| `list-followers` | List followers |
| `info` | Get clubhouse ID information |
| `revoke-token` | Revoke a specific token |
| `revoke-user` | Revoke all tokens for a user |
| `cleanup` | Clean up expired tokens |
| `stats` | Show system statistics |
| `demo` | Run a demonstration |

## GUI Integration

### Widgets

The system includes comprehensive GTK widgets for GUI integration:

#### ClubhouseIdManagerView
Main view for managing clubhouse IDs and relationships.

```python
from eosclubhouse.clubhouse_id_widgets import show_clubhouse_id_manager

# Show the manager window
window = show_clubhouse_id_manager(parent_window, user_id, clubhouse_id)
```

#### TokenDisplayWidget
Display individual tokens with copy and revoke functionality.

#### FollowRelationshipWidget
Display following relationships with unfollow options.

### Features

- **Tabbed Interface**: Separate tabs for tokens, following, followers, and statistics
- **Real-time Updates**: Automatic refresh when relationships change
- **Token Management**: Generate, copy, and revoke tokens
- **Following Management**: Follow users via tokens and manage relationships
- **Statistics Display**: Visual representation of system statistics

## Integration with Existing Clubhouse Components

### Character System Integration

```python
# Generate tokens for existing characters
character_info = CharacterInfo()
for char_id, info in character_info.items():
    token = manager.generate_token(
        user_id=info['username'],
        clubhouse_id=f"{char_id}_clubhouse",
        metadata={
            "character_id": char_id,
            "pathway": info['pathway'],
            "pathway_title": info['pathway_title']
        }
    )
```

### Quest System Integration

```python
# Create following relationships as part of quests
def quest_follow_character(follower_id, character_token):
    success = manager.follow_via_token(follower_id, character_token)
    if success:
        # Award quest points or achievements
        pass
```

### Achievement System Integration

```python
# Check for social achievements
def check_social_achievements(user_id):
    following = manager.get_following_list(user_id)
    followers = manager.get_followers_list(user_id)
    
    if len(following) >= 5:
        award_achievement("social_butterfly")
    
    if len(followers) >= 10:
        award_achievement("popular_clubhouse")
```

## Performance Considerations

### Caching Strategy

The system implements intelligent caching:
- **Token Cache**: Active tokens are cached in memory
- **Relationship Cache**: Active relationships are cached by user
- **Automatic Cleanup**: Expired tokens are automatically removed

### Database Optimization

- **Indexes**: Proper indexes on frequently queried columns
- **Prepared Statements**: Use of prepared statements for security and performance
- **Connection Pooling**: Efficient database connection management

### Scalability

- **Batch Operations**: Support for bulk token generation and relationship creation
- **Pagination**: Large result sets can be paginated (future enhancement)
- **Async Support**: Designed for future asynchronous operation support

## Security Best Practices

### Token Security

- **UUID-based**: Tokens use UUID4 for cryptographic randomness
- **Expiration**: All tokens have configurable expiration dates
- **Revocation**: Tokens can be revoked immediately when compromised
- **Metadata Validation**: Input validation for all metadata fields

### Privacy Protection

- **Token-based Following**: No direct exposure of user IDs
- **Controlled Sharing**: Users decide which tokens to share
- **Data Isolation**: Each user's data is properly isolated
- **Audit Trail**: Complete audit trail of all operations

### Database Security

- **SQLite Security**: Proper file permissions on database
- **SQL Injection Prevention**: All queries use parameterized statements
- **Data Encryption**: Sensitive data can be encrypted (future enhancement)

## Troubleshooting

### Common Issues

#### Token Validation Failures
```python
# Check if token exists and is valid
token_obj = manager.validate_token(token)
if not token_obj:
    print("Token is invalid or expired")
    # Generate new token or handle error
```

#### Following Relationship Errors
```python
# Check if relationship already exists
existing = manager.get_follow_relationship(follower_id, following_id)
if existing:
    print("Already following this user")
```

#### Database Connection Issues
```python
# The manager handles database connections automatically
# If issues persist, check file permissions and disk space
```

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

Monitor system statistics:

```python
stats = manager.get_statistics()
print(f"Active tokens: {stats['active_tokens']}")
print(f"Active relationships: {stats['active_relationships']}")

# Clean up expired tokens
cleaned = manager.cleanup_expired_tokens()
print(f"Cleaned up {cleaned} expired tokens")
```

## API Reference

### ClubhouseIdManager Methods

#### Token Management
- `generate_token(user_id, clubhouse_id, expires_days=30, metadata=None) -> str`
- `validate_token(token) -> Optional[ClubhouseIdToken]`
- `get_user_tokens(user_id) -> List[ClubhouseIdToken]`
- `get_tokens_by_clubhouse_id(clubhouse_id) -> List[ClubhouseIdToken]`
- `revoke_token(token) -> bool`
- `revoke_user_tokens(user_id) -> int`
- `cleanup_expired_tokens() -> int`

#### Relationship Management
- `follow_via_token(follower_id, token) -> bool`
- `unfollow(follower_id, following_id) -> bool`
- `get_follow_relationship(follower_id, following_id) -> Optional[ClubhouseFollowRelationship]`
- `get_following_list(user_id) -> List[ClubhouseFollowRelationship]`
- `get_followers_list(user_id) -> List[ClubhouseFollowRelationship]`

#### Information and Statistics
- `get_clubhouse_id_info(clubhouse_id) -> Optional[Dict[str, Any]]`
- `get_statistics() -> Dict[str, Any]`

### Signals

The ClubhouseIdManager emits GObject signals:

- `token-created(user_id, token)`: Emitted when a token is created
- `token-used(user_id, token)`: Emitted when a token is validated
- `follow-relationship-created(follower_id, following_id, token)`: Emitted when a relationship is created
- `follow-relationship-updated(follower_id, following_id, status)`: Emitted when a relationship is updated

## Future Enhancements

### Planned Features

1. **Social Graph Analysis**: Advanced analytics on following patterns
2. **Recommendation System**: Suggest users to follow based on interests
3. **Privacy Controls**: Fine-grained privacy settings for tokens and relationships
4. **Token Sharing**: Built-in mechanisms for secure token sharing
5. **Backup and Sync**: Cloud backup and multi-device synchronization
6. **Real-time Notifications**: Push notifications for new followers
7. **Bulk Operations**: Enhanced bulk import/export functionality
8. **API Endpoints**: REST API for external integrations

### Technical Improvements

1. **Performance Optimization**: Further database and caching optimizations
2. **Async Support**: Full asynchronous operation support
3. **Encryption**: End-to-end encryption for sensitive data
4. **Monitoring**: Built-in monitoring and alerting
5. **Testing**: Comprehensive test suite with 100% coverage

## Contributing

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m pytest tests/`
4. Run examples: `python examples/clubhouse_id_example.py`

### Code Style

- Follow PEP 8 for Python code style
- Use type hints for all public methods
- Write comprehensive docstrings
- Add unit tests for new features

### Submitting Changes

1. Create a feature branch
2. Make your changes
3. Add tests
4. Update documentation
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v2.0 - see the [COPYING](../COPYING) file for details.

## Support

For support and questions:
- File an issue on GitHub
- Check the troubleshooting section
- Run the diagnostic tools

---

*This documentation covers the complete Clubhouse ID and Token-Based Following System. For the most up-to-date information, please refer to the source code and inline documentation.*