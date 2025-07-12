# Clubhouse API Documentation

This document provides comprehensive documentation for all public APIs, functions, and components in the Clubhouse application.

## Table of Contents

1. [Core Quest System](#core-quest-system)
2. [Utility Classes](#utility-classes)
3. [UI Components](#ui-components)
4. [App Integration](#app-integration)
5. [System Integration](#system-integration)
6. [Achievement System](#achievement-system)
7. [Animation System](#animation-system)
8. [Supporting Modules](#supporting-modules)

## Core Quest System

### Quest Class

The `Quest` class is the foundation for creating interactive educational quests in the Clubhouse.

#### Basic Quest Structure

```python
from eosclubhouse.libquest import Quest

class MyQuest(Quest):
    __app_id__ = 'com.example.MyApp'
    __tags__ = ['pathway:games', 'difficulty:normal']
    __pathway_order__ = 1
    __items_on_completion__ = {'my_item': {}}
    
    def setup(self):
        self.auto_offer = True
        self.skippable = False
    
    def step_begin(self):
        self.show_message('WELCOME')
        return self.step_launch_app
    
    def step_launch_app(self):
        return self.ask_for_app_launch()
    
    def step_complete_and_stop(self):
        self.give_item('my_item', 'Congratulations!')
        return super().step_complete_and_stop()
```

#### Quest Properties

- `__app_id__`: Application ID associated with the quest
- `__tags__`: List of tags for categorization and pathways
- `__pathway_order__`: Order within pathway (lower = earlier)
- `__items_on_completion__`: Items given when quest completes
- `__auto_offer_info__`: Configuration for auto-offering quests
- `auto_offer`: Boolean to auto-offer when available
- `available_since`/`available_until`: Date range for availability
- `skippable`: Whether quest should be hidden from UI

#### Message Methods

```python
# Show a simple message
self.show_message('MESSAGE_ID')

# Show message with choices
self.show_message('QUESTION', choices=[
    ('Yes', self.step_yes),
    ('No', self.step_no)
])

# Wait for user confirmation
self.wait_confirm('CONFIRMATION_MESSAGE')

# Show hints that cycle through multiple messages
self.show_hints_message('HINT_PREFIX')  # Shows HINT_PREFIX, HINT_PREFIX_HINT1, etc.
```

#### App Integration Methods

```python
# Launch and wait for app
self.ask_for_app_launch()

# Wait for app to be launched
self.wait_for_app_launch()

# Wait for app to be in foreground
self.wait_for_app_in_foreground()

# Wait for app properties to change
self.wait_for_app_js_props_changed(props=['level', 'score'])

# Connect to app property changes
action = self.connect_app_js_props_changes(props=['level'])
action.wait()
```

#### Highlighting Methods

```python
# Highlight screen regions
self.show_highlight_rect(x, y, width, height, 'Click here')
self.show_highlight_circle(x, y, radius, 'Target area')
self.show_highlight_widget('widget_name', 'Click this button')
self.show_highlight_icon('app_id', 'Launch this app')

# Wait for highlight interaction
self.wait_for_highlight_rect(x, y, width, height, 'Click here')
```

#### Utility Methods

```python
# Pause execution
self.pause(5)  # 5 seconds

# Save/load quest configuration
self.set_conf('key', 'value')
value = self.get_conf('key')
self.save_conf()

# Deploy files to user directories
self.deploy_file('source.txt', '~/Documents/', override=True)

# Open URLs and PDFs
self.open_url_in_browser('https://example.com')
self.open_pdf('guide.pdf')
```

### QuestSet Class

Groups related quests together and manages pathway progression.

```python
from eosclubhouse.libquest import QuestSet

class MyQuestSet(QuestSet):
    __pathway_name__ = 'My Pathway'
    __character_id__ = 'ada'
    __quests__ = ['Quest1', 'Quest2', 'Quest3']
    
    def get_empty_message(self):
        return "No quests available right now!"
```

### Registry Class

Manages quest loading and registration system-wide.

```python
from eosclubhouse.libquest import Registry

# Get quest by name
quest = Registry.get_quest_by_name('MyQuest')

# Get all quest sets
quest_sets = Registry.get_quest_sets()

# Get quests by tag
quests = Registry.get_matching_quests('pathway:games')

# Load episode
Registry.load_current_episode()
```

### AsyncAction Class

Handles asynchronous operations in quests.

```python
# Create async action
action = self.connect_app_js_props_changes(['level'])

# Wait for action to complete
result = action.wait(timeout=30)

# Check action state
if action.is_done():
    print("Action completed")
elif action.is_cancelled():
    print("Action was cancelled")
```

## Utility Classes

### QuestStringCatalog

Manages quest text and localization.

```python
from eosclubhouse.utils import QuestStringCatalog

# Get message text
text = QuestStringCatalog.get_string('MYQUEST_WELCOME')

# Get message info (includes character, mood, sounds)
info = QuestStringCatalog.get_info('MYQUEST_WELCOME')
# Returns: {'txt': 'Welcome!', 'character_id': 'ada', 'mood': 'talk', ...}

# Get hint keys
hints = QuestStringCatalog.get_hint_keys('MYQUEST_FLIP')
# Returns: ['MYQUEST_FLIP', 'MYQUEST_FLIP_HINT1', 'MYQUEST_FLIP_HINT2', ...]
```

### ClubhouseState

Manages global application state.

```python
from eosclubhouse.utils import ClubhouseState

state = ClubhouseState()

# Access state properties
state.current_page = ClubhouseState.Page.CLUBHOUSE
state.lights_on = True
state.characters_disabled = False
state.window_is_visible = True

# Connect to state changes
state.connect('notify::lights-on', self.on_lights_changed)
```

### Episode Management

```python
from eosclubhouse.utils import Episode, EpisodesDB

# Get episode information
episodes_db = EpisodesDB()
episode = episodes_db.get_episode('hack2')

# Episode properties
print(f"Episode: {episode.name}")
print(f"Description: {episode.description}")
print(f"Complete: {episode.is_complete()}")
print(f"Progress: {episode.percentage_complete}%")
```

### Performance Monitoring

```python
from eosclubhouse.utils import Performance

# Decorate functions for timing
@Performance.timeit
def slow_function():
    # Function implementation
    pass
```

## UI Components

### ClubhouseWindow

Main application window with navigation and quest management.

```python
from eosclubhouse.clubhouse import ClubhouseWindow

class MyClubhouseWindow(ClubhouseWindow):
    def __init__(self, app):
        super().__init__(app)
        self.connect('notify::visible', self.on_visibility_changed)
    
    def set_page(self, page_name):
        """Navigate to different pages"""
        # page_name can be 'clubhouse', 'pathways', 'news', 'character'
        super().set_page(page_name)
```

### Character

Manages character display and animations.

```python
from eosclubhouse.clubhouse import Character

# Get or create character
ada = Character.get_or_create('ada')

# Character properties
ada.mood = 'excited'
ada.body_animation = 'hi'

# Get character information
print(f"Username: {ada.username}")
print(f"Pathway: {ada.pathway}")
position = ada.get_position()  # (x, y) coordinates
```

### Message

Displays quest messages and character dialogs.

```python
from eosclubhouse.clubhouse import Message

# Create message
message = Message(scale=1.5)

# Configure message
message.set_text("Welcome to the quest!")
message.set_character('ada')
message.display_character(True)

# Add action buttons
message.add_button('Continue', self.continue_callback)
message.add_button('Skip', self.skip_callback)
```

### ActivityCard

Displays quest information in the UI.

```python
from eosclubhouse.clubhouse import ActivityCard

# Create activity card
card = ActivityCard(quest_set, quest)

# Card automatically shows:
# - Quest name and description
# - Difficulty indicators
# - Progress status
# - Background artwork
```

### InAppNotify

Shows in-app notifications for achievements and items.

```python
from eosclubhouse.clubhouse import InAppNotify

# Create notification for achievement
notification = InAppNotify.from_achievement(achievement)

# Create notification for item
notification = InAppNotify.from_item(item, "You got a new item!")

# Create custom message notification
notification = InAppNotify.from_message(message_info)
notification.slide_in()
```

## App Integration

### Base App Class

```python
from eosclubhouse.system import App

class MyApp(App):
    def __init__(self):
        super().__init__('com.example.MyApp')
    
    def is_feature_enabled(self):
        return self.get_js_property('featureEnabled', False)
    
    def set_level(self, level):
        return self.set_js_property('currentLevel', level)
```

### Fizzics App

Specialized physics game integration.

```python
from eosclubhouse.apps import Fizzics

app = Fizzics()

# Level management
app.set_current_level(5)
current_level = app.get_current_level()
effective_level = app.get_effective_level()  # Includes completion bonus

# Tool management
app.disable_tool('create', disabled=True)
app.disable_add_tool_for_ball_type(Fizzics.BallType.ENEMY)

# Physics properties
app.set_property_for_ball_type('gravity', Fizzics.BallType.PLAYER, 9.8)
app.enable_physics_for_ball_type(Fizzics.BallType.ROCK)
```

### LightSpeed App

Space game integration with powerups and upgrades.

```python
from eosclubhouse.apps import LightSpeed

app = LightSpeed()

# Level management
app.set_level(3)

# Powerup tracking
spawned = app.powerups_spawned('invulnerable', 'blowup')
picked = app.powerups_picked('upgrade')
active = app.powerups_active('invulnerable')

# Toolbox integration
app.reveal_topic('variables')
```

## System Integration

### Desktop Class

Manages desktop environment integration.

```python
from eosclubhouse.system import Desktop

# App management
Desktop.launch_app('com.example.MyApp')
Desktop.focus_app('com.example.MyApp')
is_running = Desktop.app_is_running('com.example.MyApp')

# App grid management
Desktop.add_app_to_grid('com.example.MyApp')
Desktop.remove_app_from_grid('com.example.MyApp')
in_grid = Desktop.is_app_in_grid('com.example.MyApp')

# Hack mode management
Desktop.set_hack_mode_shell(True)
Desktop.set_hack_icon_pulse(True)

# Window management
Desktop.minimize_all()
is_foreground = Desktop.is_app_in_foreground('com.example.MyApp')
```

### GameStateService

Persistent data storage for quest progress.

```python
from eosclubhouse.system import GameStateService

gss = GameStateService()

# Store data
gss.set('quest.MyQuest', {'complete': True, 'score': 100})

# Retrieve data
data = gss.get('quest.MyQuest', default_value={})

# Update existing data
gss.update('quest.MyQuest', {'score': 150})

# Reset all data
gss.reset()
```

### UserAccount

Access user profile information.

```python
from eosclubhouse.system import UserAccount

account = UserAccount()

# Get user information
real_name = account.get('RealName')
username = account.get('UserName')

# Set user information
account.set_real_name('John Doe')
```

## Achievement System

### AchievementsDB

Manages achievement tracking and rewards.

```python
from eosclubhouse.achievements import AchievementsDB

db = AchievementsDB()
manager = db.manager

# Add points to skillsets
manager.add_points('GAMES', 10, record_points=True)
manager.add_points('PATHWAY:ART', 5)

# Get achievements
achieved = manager.get_achievements_achieved()
for achievement in achieved:
    print(f"Achievement: {achievement.name}")
    print(f"Description: {achievement.description}")
```

### Achievement Integration in Quests

```python
class MyQuest(Quest):
    __tags__ = ['skillset:games:5', 'pathway:games']
    
    def step_complete_and_stop(self):
        # Points automatically awarded based on tags
        return super().step_complete_and_stop()
```

## Animation System

### AnimationImage

Displays animated character sprites.

```python
from eosclubhouse.animation import AnimationImage

# Create animated image
image = AnimationImage('ada/fullbody')
image.load(scale=1.0)

# Play animations
image.play('idle')
image.play('hi')
image.play('talk')

# Get animation anchor point
anchor = image.get_anchor()  # (x, y) offset
```

### Animation

Manages individual animation sequences.

```python
from eosclubhouse.animation import Animation

# Animation metadata format (JSON):
{
    "width": 147,
    "height": 306,
    "default-delay": 100,
    "frames": [
        "0 750",     # Frame 0 for 750ms
        1, 2, 3,     # Frames 1-3 with default delay
        "4 2000-3000" # Frame 4 with random delay
    ],
    "loop": true,
    "anchor": [73, 280]
}
```

### Custom Animation Directories

```python
# Place custom animations in:
# ~/.var/app/com.hack_computer.Clubhouse/data/characters/
# 
# Directory structure:
# characters/
#   ada/
#     fullbody/
#       idle.png
#       idle.json
#       hi.png
#       hi.json
```

## Supporting Modules

### Sound Integration

```python
from eosclubhouse.system import Sound

# Play sound effects
Sound.play('quests/quest-given')
Sound.play('clubhouse/dialog/open')

# Play with callback
def on_sound_finished(proxy, uuid, sound_id):
    print(f"Sound {sound_id} finished")

Sound.play('background/ambient', on_sound_finished, 'ambient')
```

### Network Management

```python
from eosclubhouse.network import NetworkManager

network = NetworkManager()

# Check connection
is_connected = network.is_connected()

# Get connection details
connection_info = network.get_connection_info()
```

### Metrics and Analytics

```python
from eosclubhouse import metrics

# Record events
metrics.record('QUEST_STARTED', {'quest_id': 'MyQuest'})
metrics.record('ACHIEVEMENT_EARNED', {'achievement_id': 'first_quest'})

# Record timed events
metrics.record_start('QUEST_DURATION', 'MyQuest')
# ... quest execution ...
metrics.record_stop('QUEST_DURATION', 'MyQuest')
```

## Common Patterns and Examples

### Complete Quest Example

```python
class TutorialQuest(Quest):
    __app_id__ = 'com.example.Tutorial'
    __tags__ = ['pathway:games', 'difficulty:easy']
    __pathway_order__ = 1
    __items_on_completion__ = {'tutorial_badge': {}}
    
    def setup(self):
        self.auto_offer = True
        
    def step_begin(self):
        self.show_message('TUTORIAL_WELCOME')
        return self.step_launch_app
        
    def step_launch_app(self):
        return self.ask_for_app_launch(
            pause_after_launch=2,
            give_app_icon=True
        )
        
    def step_wait_for_level(self):
        action = self.connect_app_js_props_changes(['level'])
        if action.wait(timeout=60):
            level = self.app.get_js_property('level', 0)
            if level >= 3:
                return self.step_congratulations
        return self.step_timeout
        
    def step_congratulations(self):
        self.show_message('TUTORIAL_COMPLETE')
        self.give_item('tutorial_badge', 'Well done!')
        return self.step_complete_and_stop
        
    def step_timeout(self):
        self.show_message('TUTORIAL_TIMEOUT')
        return self.step_complete_and_stop
```

### Message String Configuration

```csv
TUTORIAL_WELCOME,"Welcome to the tutorial!",ada,excited,quests/quest-given,
TUTORIAL_COMPLETE,"Congratulations! You completed the tutorial.",ada,happy,quests/quest-complete,
TUTORIAL_TIMEOUT,"Take your time and try again later.",ada,talk,,
```

### Custom App Integration

```python
class CustomApp(App):
    def __init__(self):
        super().__init__('com.custom.App')
        
    def wait_for_score(self, target_score):
        """Custom method to wait for specific score"""
        def check_score():
            current = self.get_js_property('score', 0)
            return current >= target_score
            
        return self.connect_props_change(
            self.APP_JS_PARAMS,
            ['score'],
            check_score
        )
```

## Best Practices

1. **Quest Design**:
   - Use descriptive message IDs
   - Implement proper error handling
   - Provide clear user feedback
   - Use appropriate timeouts

2. **Performance**:
   - Load animations asynchronously
   - Cache frequently accessed data
   - Use @Performance.timeit for optimization

3. **User Experience**:
   - Provide visual highlights for interactions
   - Use consistent messaging patterns
   - Handle app crashes gracefully

4. **Testing**:
   - Test quests in isolation
   - Verify app integration works
   - Test different user scenarios

This documentation covers the major public APIs and components of the Clubhouse system. Each component provides extensive functionality for creating educational interactive experiences.