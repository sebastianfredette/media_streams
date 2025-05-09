"""Media Streams sensor for Home Assistant."""
import logging
from datetime import timedelta
import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_HOST, 
    CONF_PORT, 
    CONF_API_KEY, 
    CONF_USERNAME, 
    CONF_PASSWORD,
    CONF_SSL,
    CONF_NAME
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

# Define available server types
CONF_SERVER_TYPE = "server_type"
SERVER_TYPE_JELLYFIN = "jellyfin"
SERVER_TYPE_PLEX = "plex"

DEFAULT_NAME = "Media Streams"
DEFAULT_PORT_JELLYFIN = 8096
DEFAULT_PORT_PLEX = 32400
DEFAULT_SSL = False

# Configuration schema
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SERVER_TYPE): vol.In([SERVER_TYPE_JELLYFIN, SERVER_TYPE_PLEX]),
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT): cv.port,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
    vol.Exclusive(CONF_API_KEY, "auth"): cv.string,
    vol.Exclusive(CONF_USERNAME, "auth"): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    server_type = config.get(CONF_SERVER_TYPE)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    name = config.get(CONF_NAME)
    use_ssl = config.get(CONF_SSL)
    api_key = config.get(CONF_API_KEY)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    # Set default port based on server type if not provided
    if port is None:
        if server_type == SERVER_TYPE_JELLYFIN:
            port = DEFAULT_PORT_JELLYFIN
        else:  # PLEX
            port = DEFAULT_PORT_PLEX

    protocol = "https" if use_ssl else "http"
    base_url = f"{protocol}://{host}:{port}"

    if server_type == SERVER_TYPE_JELLYFIN:
        sensor = JellyfinStreamsSensor(base_url, api_key, name)
    else:  # PLEX
        sensor = PlexStreamsSensor(base_url, api_key, username, password, name)

    add_entities([sensor], True)


class JellyfinStreamsSensor(SensorEntity):
    """Representation of a Jellyfin streams sensor."""

    def __init__(self, base_url, api_key, name):
        """Initialize the sensor."""
        self._base_url = base_url
        self._api_key = api_key
        self._name = f"{name} Jellyfin"
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:play-network"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "streams"

    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # Get sessions from Jellyfin API
            headers = {"X-MediaBrowser-Token": self._api_key} if self._api_key else {}
            response = requests.get(
                f"{self._base_url}/Sessions", 
                headers=headers, 
                timeout=10
            )
            response.raise_for_status()
            
            sessions = response.json()
            
            # Filter for active sessions that are actually playing content
            active_streams = [
                s for s in sessions 
                if s.get("NowPlayingItem") and s.get("PlayState", {}).get("PlayMethod") in ["DirectPlay", "DirectStream", "Transcode"]
            ]
            
            self._state = len(active_streams)
            
            # Add extra details about streams
            stream_details = []
            for stream in active_streams:
                user = stream.get("UserName", "Unknown")
                item = stream.get("NowPlayingItem", {})
                title = item.get("Name", "Unknown")
                media_type = item.get("Type", "Unknown")
                play_method = stream.get("PlayState", {}).get("PlayMethod", "Unknown")
                
                stream_details.append({
                    "user": user,
                    "title": title,
                    "type": media_type,
                    "method": play_method
                })
            
            self._attributes["streams"] = stream_details
            self._attributes["last_updated"] = response.headers.get("Date")
            
        except requests.RequestException as err:
            _LOGGER.error("Error fetching Jellyfin stream data: %s", err)
            self._state = None


class PlexStreamsSensor(SensorEntity):
    """Representation of a Plex streams sensor."""

    def __init__(self, base_url, api_key, username, password, name):
        """Initialize the sensor."""
        self._base_url = base_url
        self._api_key = api_key  # X-Plex-Token
        self._username = username
        self._password = password
        self._name = f"{name} Plex"
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:plex"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "streams"

    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # If we don't have an API key but have username/password, get a token first
            headers = {}
            if not self._api_key and self._username and self._password:
                # This is simplified - in a real implementation you'd need to handle getting
                # a proper auth token which is more complex with Plex
                _LOGGER.warning("Username/password auth for Plex not fully implemented")
            
            if self._api_key:
                headers["X-Plex-Token"] = self._api_key
            
            # Get sessions from Plex API
            response = requests.get(
                f"{self._base_url}/status/sessions", 
                headers=headers, 
                timeout=10
            )
            response.raise_for_status()
            
            # Parse XML response - simplified for this example
            # In a real implementation, use proper XML parsing
            # For now we're just counting the MediaContainer size attribute
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            # Get the 'size' attribute which represents the number of active sessions
            self._state = int(root.get('size', 0))
            
            # Parse stream details
            stream_details = []
            for video in root.findall('.//Video'):
                user_tag = video.find('.//User')
                user = user_tag.get('title', 'Unknown') if user_tag is not None else 'Unknown'
                
                title = video.get('title', 'Unknown')
                media_type = video.get('type', 'Unknown')
                
                # Get transcoding info
                transcoding = "DirectPlay"
                for stream in video.findall('.//Stream'):
                    if stream.get('decision') == 'transcode':
                        transcoding = "Transcode"
                        break
                
                stream_details.append({
                    "user": user,
                    "title": title,
                    "type": media_type,
                    "method": transcoding
                })
            
            self._attributes["streams"] = stream_details
            self._attributes["last_updated"] = response.headers.get("Date")
            
        except requests.RequestException as err:
            _LOGGER.error("Error fetching Plex stream data: %s", err)
            self._state = None
