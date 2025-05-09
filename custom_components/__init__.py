"""The Media Streams integration."""

DOMAIN = "media_streams"

async def async_setup(hass, config):
    """Set up the Media Streams component."""
    return True

async def async_setup_entry(hass, entry):
    """Set up Media Streams from a config entry."""
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return True
