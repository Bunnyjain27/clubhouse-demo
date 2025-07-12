#!/usr/bin/env python3
#
# Copyright © 2024 Endless OS Foundation LLC.
#
# This file is part of clubhouse
# (see https://github.com/endlessm/clubhouse).
#
# UI widgets for clubhouse ID management and token-based following
#

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")

import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from gi.repository import Gtk, GdkPixbuf, GObject, Gdk, Gio
from eosclubhouse.clubhouse_id_manager import (
    get_clubhouse_id_manager, 
    ClubhouseIdToken, 
    ClubhouseFollowRelationship
)
from eosclubhouse.widgets import gtk_widget_add_custom_css_provider

logger = logging.getLogger(__name__)


class TokenDisplayWidget(Gtk.Box):
    """Widget to display token information."""
    
    def __init__(self, token: ClubhouseIdToken):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.token = token
        
        # Add CSS styling
        self.get_style_context().add_class('token-display')
        
        # Token icon
        self.token_icon = Gtk.Image()
        self.token_icon.set_from_icon_name('dialog-password', Gtk.IconSize.BUTTON)
        self.pack_start(self.token_icon, False, False, 0)
        
        # Token info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        # Token ID (truncated)
        token_label = Gtk.Label()
        token_label.set_markup(f"<b>Token:</b> {token.token[:8]}...")
        token_label.set_halign(Gtk.Align.START)
        info_box.pack_start(token_label, False, False, 0)
        
        # Clubhouse ID
        clubhouse_label = Gtk.Label()
        clubhouse_label.set_markup(f"<b>Clubhouse ID:</b> {token.clubhouse_id}")
        clubhouse_label.set_halign(Gtk.Align.START)
        info_box.pack_start(clubhouse_label, False, False, 0)
        
        # Expiration status
        status_label = Gtk.Label()
        if token.is_valid():
            days_left = (token.expires_at - datetime.now()).days
            status_label.set_markup(f"<span color='green'>Valid (expires in {days_left} days)</span>")
        else:
            status_label.set_markup(f"<span color='red'>Expired</span>")
        status_label.set_halign(Gtk.Align.START)
        info_box.pack_start(status_label, False, False, 0)
        
        self.pack_start(info_box, True, True, 0)
        
        # Actions
        actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        # Copy button
        copy_button = Gtk.Button()
        copy_button.set_image(Gtk.Image.new_from_icon_name('edit-copy', Gtk.IconSize.BUTTON))
        copy_button.set_tooltip_text("Copy token to clipboard")
        copy_button.connect('clicked', self._on_copy_clicked)
        actions_box.pack_start(copy_button, False, False, 0)
        
        # Revoke button
        revoke_button = Gtk.Button()
        revoke_button.set_image(Gtk.Image.new_from_icon_name('edit-delete', Gtk.IconSize.BUTTON))
        revoke_button.set_tooltip_text("Revoke token")
        revoke_button.connect('clicked', self._on_revoke_clicked)
        actions_box.pack_start(revoke_button, False, False, 0)
        
        self.pack_start(actions_box, False, False, 0)
        
        self.show_all()
    
    def _on_copy_clicked(self, button):
        """Copy token to clipboard."""
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.token.token, -1)
        logger.info(f"Token {self.token.token[:8]}... copied to clipboard")
    
    def _on_revoke_clicked(self, button):
        """Revoke the token."""
        manager = get_clubhouse_id_manager()
        success = manager.revoke_token(self.token.token)
        if success:
            logger.info(f"Token {self.token.token[:8]}... revoked")
            self.set_sensitive(False)


class FollowRelationshipWidget(Gtk.Box):
    """Widget to display follow relationship information."""
    
    def __init__(self, relationship: ClubhouseFollowRelationship, show_follower: bool = True):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.relationship = relationship
        self.show_follower = show_follower
        
        # Add CSS styling
        self.get_style_context().add_class('follow-relationship')
        
        # User icon
        user_icon = Gtk.Image()
        user_icon.set_from_icon_name('avatar-default', Gtk.IconSize.BUTTON)
        self.pack_start(user_icon, False, False, 0)
        
        # User info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        # User ID
        user_id = relationship.follower_id if show_follower else relationship.following_id
        user_label = Gtk.Label()
        user_label.set_markup(f"<b>{user_id}</b>")
        user_label.set_halign(Gtk.Align.START)
        info_box.pack_start(user_label, False, False, 0)
        
        # Relationship info
        rel_info = "Following you" if show_follower else "You are following"
        rel_label = Gtk.Label()
        rel_label.set_markup(f"<small>{rel_info}</small>")
        rel_label.set_halign(Gtk.Align.START)
        info_box.pack_start(rel_label, False, False, 0)
        
        # Date
        date_label = Gtk.Label()
        date_str = relationship.created_at.strftime("%Y-%m-%d")
        date_label.set_markup(f"<small>Since {date_str}</small>")
        date_label.set_halign(Gtk.Align.START)
        info_box.pack_start(date_label, False, False, 0)
        
        self.pack_start(info_box, True, True, 0)
        
        # Unfollow button (only for following, not followers)
        if not show_follower:
            unfollow_button = Gtk.Button()
            unfollow_button.set_image(Gtk.Image.new_from_icon_name('list-remove', Gtk.IconSize.BUTTON))
            unfollow_button.set_tooltip_text("Unfollow")
            unfollow_button.connect('clicked', self._on_unfollow_clicked)
            self.pack_start(unfollow_button, False, False, 0)
        
        self.show_all()
    
    def _on_unfollow_clicked(self, button):
        """Unfollow the user."""
        manager = get_clubhouse_id_manager()
        success = manager.unfollow(self.relationship.follower_id, self.relationship.following_id)
        if success:
            logger.info(f"Unfollowed {self.relationship.following_id}")
            self.set_sensitive(False)


class TokenGeneratorDialog(Gtk.Dialog):
    """Dialog for generating new tokens."""
    
    def __init__(self, parent_window, user_id: str, clubhouse_id: str):
        super().__init__(title="Generate New Token", parent=parent_window, modal=True)
        self.user_id = user_id
        self.clubhouse_id = clubhouse_id
        
        self.set_default_size(400, 300)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Generate", Gtk.ResponseType.OK
        )
        
        content_area = self.get_content_area()
        content_area.set_spacing(12)
        content_area.set_border_width(12)
        
        # Header
        header_label = Gtk.Label()
        header_label.set_markup(f"<b>Generate Token for {clubhouse_id}</b>")
        content_area.pack_start(header_label, False, False, 0)
        
        # Expiration days
        exp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        exp_label = Gtk.Label("Expires in:")
        exp_box.pack_start(exp_label, False, False, 0)
        
        self.exp_spin = Gtk.SpinButton.new_with_range(1, 365, 1)
        self.exp_spin.set_value(30)
        exp_box.pack_start(self.exp_spin, False, False, 0)
        
        exp_days_label = Gtk.Label("days")
        exp_box.pack_start(exp_days_label, False, False, 0)
        
        content_area.pack_start(exp_box, False, False, 0)
        
        # Metadata
        metadata_label = Gtk.Label("Metadata (JSON):")
        metadata_label.set_halign(Gtk.Align.START)
        content_area.pack_start(metadata_label, False, False, 0)
        
        self.metadata_textview = Gtk.TextView()
        self.metadata_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.metadata_textview)
        scrolled.set_size_request(-1, 100)
        content_area.pack_start(scrolled, True, True, 0)
        
        # Set default metadata
        buffer = self.metadata_textview.get_buffer()
        default_metadata = {
            "generated_by": "clubhouse_ui",
            "purpose": "user_following"
        }
        buffer.set_text(json.dumps(default_metadata, indent=2))
        
        self.show_all()
    
    def get_token_params(self):
        """Get the token generation parameters."""
        expires_days = int(self.exp_spin.get_value())
        
        # Get metadata
        buffer = self.metadata_textview.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        metadata_text = buffer.get_text(start_iter, end_iter, False)
        
        try:
            metadata = json.loads(metadata_text) if metadata_text.strip() else {}
        except json.JSONDecodeError:
            metadata = {}
        
        return expires_days, metadata


class FollowViaTokenDialog(Gtk.Dialog):
    """Dialog for following a user via token."""
    
    def __init__(self, parent_window, user_id: str):
        super().__init__(title="Follow via Token", parent=parent_window, modal=True)
        self.user_id = user_id
        
        self.set_default_size(400, 200)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Follow", Gtk.ResponseType.OK
        )
        
        content_area = self.get_content_area()
        content_area.set_spacing(12)
        content_area.set_border_width(12)
        
        # Header
        header_label = Gtk.Label()
        header_label.set_markup("<b>Follow a User via Token</b>")
        content_area.pack_start(header_label, False, False, 0)
        
        # Instructions
        instructions_label = Gtk.Label()
        instructions_label.set_markup(
            "Enter the token of the user you want to follow.\n"
            "The token should be shared by the user you want to follow."
        )
        instructions_label.set_line_wrap(True)
        content_area.pack_start(instructions_label, False, False, 0)
        
        # Token entry
        token_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        token_label = Gtk.Label("Token:")
        token_box.pack_start(token_label, False, False, 0)
        
        self.token_entry = Gtk.Entry()
        self.token_entry.set_placeholder_text("Enter token here...")
        self.token_entry.set_activates_default(True)
        token_box.pack_start(self.token_entry, True, True, 0)
        
        content_area.pack_start(token_box, False, False, 0)
        
        # Set default button
        self.set_default_response(Gtk.ResponseType.OK)
        
        self.show_all()
    
    def get_token(self):
        """Get the entered token."""
        return self.token_entry.get_text().strip()


class ClubhouseIdManagerView(Gtk.Box):
    """Main view for clubhouse ID management."""
    
    def __init__(self, user_id: str, clubhouse_id: str):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.user_id = user_id
        self.clubhouse_id = clubhouse_id
        self.manager = get_clubhouse_id_manager()
        
        self.set_border_width(12)
        
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        header_label = Gtk.Label()
        header_label.set_markup(f"<b>Clubhouse ID Manager</b> - {clubhouse_id}")
        header_label.set_halign(Gtk.Align.START)
        header_box.pack_start(header_label, True, True, 0)
        
        # Refresh button
        refresh_button = Gtk.Button()
        refresh_button.set_image(Gtk.Image.new_from_icon_name('view-refresh', Gtk.IconSize.BUTTON))
        refresh_button.set_tooltip_text("Refresh")
        refresh_button.connect('clicked', self._on_refresh_clicked)
        header_box.pack_start(refresh_button, False, False, 0)
        
        self.pack_start(header_box, False, False, 0)
        
        # Create notebook for tabs
        self.notebook = Gtk.Notebook()
        self.pack_start(self.notebook, True, True, 0)
        
        # Tokens tab
        self.tokens_page = self._create_tokens_page()
        self.notebook.append_page(self.tokens_page, Gtk.Label("My Tokens"))
        
        # Following tab
        self.following_page = self._create_following_page()
        self.notebook.append_page(self.following_page, Gtk.Label("Following"))
        
        # Followers tab
        self.followers_page = self._create_followers_page()
        self.notebook.append_page(self.followers_page, Gtk.Label("Followers"))
        
        # Statistics tab
        self.stats_page = self._create_stats_page()
        self.notebook.append_page(self.stats_page, Gtk.Label("Statistics"))
        
        # Connect to manager signals
        self.manager.connect('token-created', self._on_token_created)
        self.manager.connect('follow-relationship-created', self._on_relationship_created)
        self.manager.connect('follow-relationship-updated', self._on_relationship_updated)
        
        self.show_all()
        self._refresh_all()
    
    def _create_tokens_page(self):
        """Create the tokens management page."""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.set_border_width(12)
        
        # Header with action buttons
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        tokens_label = Gtk.Label("My Tokens")
        tokens_label.set_halign(Gtk.Align.START)
        header_box.pack_start(tokens_label, True, True, 0)
        
        # Generate token button
        generate_button = Gtk.Button("Generate New Token")
        generate_button.set_image(Gtk.Image.new_from_icon_name('list-add', Gtk.IconSize.BUTTON))
        generate_button.connect('clicked', self._on_generate_token_clicked)
        header_box.pack_start(generate_button, False, False, 0)
        
        page.pack_start(header_box, False, False, 0)
        
        # Tokens list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.tokens_listbox = Gtk.ListBox()
        self.tokens_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.tokens_listbox)
        
        page.pack_start(scrolled, True, True, 0)
        
        return page
    
    def _create_following_page(self):
        """Create the following management page."""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.set_border_width(12)
        
        # Header with action buttons
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        following_label = Gtk.Label("Following")
        following_label.set_halign(Gtk.Align.START)
        header_box.pack_start(following_label, True, True, 0)
        
        # Follow via token button
        follow_button = Gtk.Button("Follow via Token")
        follow_button.set_image(Gtk.Image.new_from_icon_name('list-add', Gtk.IconSize.BUTTON))
        follow_button.connect('clicked', self._on_follow_via_token_clicked)
        header_box.pack_start(follow_button, False, False, 0)
        
        page.pack_start(header_box, False, False, 0)
        
        # Following list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.following_listbox = Gtk.ListBox()
        self.following_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.following_listbox)
        
        page.pack_start(scrolled, True, True, 0)
        
        return page
    
    def _create_followers_page(self):
        """Create the followers page."""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.set_border_width(12)
        
        # Header
        followers_label = Gtk.Label("Followers")
        followers_label.set_halign(Gtk.Align.START)
        page.pack_start(followers_label, False, False, 0)
        
        # Followers list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.followers_listbox = Gtk.ListBox()
        self.followers_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.followers_listbox)
        
        page.pack_start(scrolled, True, True, 0)
        
        return page
    
    def _create_stats_page(self):
        """Create the statistics page."""
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.set_border_width(12)
        
        # Header
        stats_label = Gtk.Label("Statistics")
        stats_label.set_halign(Gtk.Align.START)
        page.pack_start(stats_label, False, False, 0)
        
        # Stats display
        self.stats_textview = Gtk.TextView()
        self.stats_textview.set_editable(False)
        self.stats_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.stats_textview)
        
        page.pack_start(scrolled, True, True, 0)
        
        return page
    
    def _on_refresh_clicked(self, button):
        """Refresh all data."""
        self._refresh_all()
    
    def _on_generate_token_clicked(self, button):
        """Show generate token dialog."""
        dialog = TokenGeneratorDialog(self.get_toplevel(), self.user_id, self.clubhouse_id)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            expires_days, metadata = dialog.get_token_params()
            token = self.manager.generate_token(
                user_id=self.user_id,
                clubhouse_id=self.clubhouse_id,
                expires_days=expires_days,
                metadata=metadata
            )
            logger.info(f"Generated new token: {token}")
            self._refresh_tokens()
        
        dialog.destroy()
    
    def _on_follow_via_token_clicked(self, button):
        """Show follow via token dialog."""
        dialog = FollowViaTokenDialog(self.get_toplevel(), self.user_id)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            token = dialog.get_token()
            if token:
                success = self.manager.follow_via_token(self.user_id, token)
                if success:
                    logger.info(f"Successfully followed user via token {token[:8]}...")
                    self._refresh_following()
                else:
                    logger.warning(f"Failed to follow user via token {token[:8]}...")
        
        dialog.destroy()
    
    def _on_token_created(self, manager, user_id, token):
        """Handle token created signal."""
        if user_id == self.user_id:
            self._refresh_tokens()
    
    def _on_relationship_created(self, manager, follower_id, following_id, token):
        """Handle relationship created signal."""
        if follower_id == self.user_id:
            self._refresh_following()
        # Check if someone followed us
        user_tokens = self.manager.get_user_tokens(self.user_id)
        for user_token in user_tokens:
            if user_token.token == token:
                self._refresh_followers()
                break
    
    def _on_relationship_updated(self, manager, follower_id, following_id, status):
        """Handle relationship updated signal."""
        if follower_id == self.user_id:
            self._refresh_following()
        if following_id == self.user_id:
            self._refresh_followers()
    
    def _refresh_all(self):
        """Refresh all data."""
        self._refresh_tokens()
        self._refresh_following()
        self._refresh_followers()
        self._refresh_stats()
    
    def _refresh_tokens(self):
        """Refresh tokens list."""
        # Clear existing tokens
        for child in self.tokens_listbox.get_children():
            self.tokens_listbox.remove(child)
        
        # Add current tokens
        tokens = self.manager.get_user_tokens(self.user_id)
        for token in tokens:
            token_widget = TokenDisplayWidget(token)
            self.tokens_listbox.add(token_widget)
        
        if not tokens:
            no_tokens_label = Gtk.Label("No tokens found")
            no_tokens_label.set_halign(Gtk.Align.CENTER)
            self.tokens_listbox.add(no_tokens_label)
        
        self.tokens_listbox.show_all()
    
    def _refresh_following(self):
        """Refresh following list."""
        # Clear existing following
        for child in self.following_listbox.get_children():
            self.following_listbox.remove(child)
        
        # Add current following
        following = self.manager.get_following_list(self.user_id)
        for rel in following:
            follow_widget = FollowRelationshipWidget(rel, show_follower=False)
            self.following_listbox.add(follow_widget)
        
        if not following:
            no_following_label = Gtk.Label("Not following anyone")
            no_following_label.set_halign(Gtk.Align.CENTER)
            self.following_listbox.add(no_following_label)
        
        self.following_listbox.show_all()
    
    def _refresh_followers(self):
        """Refresh followers list."""
        # Clear existing followers
        for child in self.followers_listbox.get_children():
            self.followers_listbox.remove(child)
        
        # Add current followers
        followers = self.manager.get_followers_list(self.user_id)
        for rel in followers:
            follower_widget = FollowRelationshipWidget(rel, show_follower=True)
            self.followers_listbox.add(follower_widget)
        
        if not followers:
            no_followers_label = Gtk.Label("No followers")
            no_followers_label.set_halign(Gtk.Align.CENTER)
            self.followers_listbox.add(no_followers_label)
        
        self.followers_listbox.show_all()
    
    def _refresh_stats(self):
        """Refresh statistics."""
        stats = self.manager.get_statistics()
        clubhouse_info = self.manager.get_clubhouse_id_info(self.clubhouse_id)
        
        stats_text = "System Statistics:\n"
        stats_text += f"• Active Tokens: {stats['active_tokens']}\n"
        stats_text += f"• Total Tokens: {stats['total_tokens']}\n"
        stats_text += f"• Active Relationships: {stats['active_relationships']}\n"
        stats_text += f"• Total Relationships: {stats['total_relationships']}\n"
        stats_text += f"• Unique Users: {stats['unique_users']}\n\n"
        
        if clubhouse_info:
            stats_text += f"Your Clubhouse ({self.clubhouse_id}) Statistics:\n"
            stats_text += f"• Your Followers: {clubhouse_info['followers_count']}\n"
            stats_text += f"• You're Following: {clubhouse_info['following_count']}\n"
            stats_text += f"• Your Active Tokens: {clubhouse_info['active_tokens']}\n"
        
        buffer = self.stats_textview.get_buffer()
        buffer.set_text(stats_text)


def show_clubhouse_id_manager(parent_window, user_id: str, clubhouse_id: str):
    """Show the clubhouse ID manager window."""
    window = Gtk.Window()
    window.set_title("Clubhouse ID Manager")
    window.set_default_size(600, 500)
    window.set_transient_for(parent_window)
    
    manager_view = ClubhouseIdManagerView(user_id, clubhouse_id)
    window.add(manager_view)
    
    window.show_all()
    return window