# Media Streams for Home Assistant

This custom integration allows you to monitor active streams from your Jellyfin and/or Plex media servers in Home Assistant.

## Installation

### Method 1: HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed.
2. Add this repository as a custom repository in HACS:
   - Go to HACS > Integrations
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add the URL to your repository
   - Select "Integration" as the category
   - Click "Add"
3. Install the "Media Streams" integration from HACS.
4. Restart Home Assistant.

### Method 2: Manual Installation

1. Create the following folder structure in your Home Assistant configuration directory:
   ```
   custom_components/media_streams/
   ```
2. Copy all the files from this repository's `custom_components/media_streams/` folder to your newly created folder.
3. Restart Home Assistant.

## Configuration

### Step 1: Configure the Sensors

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: media_streams
    name: Media Streams  # Optional, default is "Media Streams"
    server_type: jellyfin
    host: YOUR_JELLYFIN_SERVER_IP
    port: 8096  # Optional, default is 8096
    ssl: false  # Optional, default is false
    api_key: YOUR_JELLYFIN_API_KEY  # Recommended authentication method

  - platform: media_streams
    name: Media Streams  # Optional, default is "Media Streams"
    server_type: plex
    host: YOUR_PLEX_SERVER_IP
    port: 32400  # Optional, default is 32400
    ssl: false  # Optional, default is false
    api_key: YOUR_PLEX_TOKEN  # Recommended authentication method
    # Alternative authentication:
    # username: YOUR_PLEX_USERNAME
    # password: YOUR_PLEX_PASSWORD
```

### Step 2: Install the Custom Card

1. Create the following folder structure:
   ```
   www/community/media-streams-card/
   ```
2. Copy the `media-streams-card.js` file to this folder.

3. Add the card resource in your Lovelace configuration:
   - Go to Configuration > Lovelace Dashboards > Resources
   - Click "Add Resource"
   - URL: `/local/community/media-streams-card/media-streams-card.js`
   - Resource type: "JavaScript Module"

### Step 3: Add the Card to Your Dashboard

1. Go to your dashboard
2. Click the "Edit" button
3. Click "Add Card"
4. Scroll down and select "Custom: Media Streams Card"
5. Configure the card:
   ```yaml
   type: 'custom:media-streams-card'
   jellyfin_entity: sensor.media_streams_jellyfin
   plex_entity: sensor.media_streams_plex
   ```
6. Click "Save"

## Getting API Keys

### Jellyfin

1. In Jellyfin, go to Dashboard > Administration > API Keys
2. Create a new API key
3. Copy the API key and use it in your configuration

### Plex

To get your Plex token:

1. Log in to Plex Web App
2. Play any video
3. Open your browser's developer tools (F12)
4. Go to Network tab
5. Look for a request to the Plex server
6. Find the `X-Plex-Token` parameter in the URL
7. Copy this token and use it as your `api_key` in the configuration

## Troubleshooting

If you encounter issues:

1. Check your Home Assistant logs for errors related to the `media_streams` component
2. Verify that your media server is reachable from Home Assistant
3. Confirm that your API key or credentials are correct
4. Make sure your user has sufficient privileges on the media server

## Advanced Customization

The card and sensors can be further customized:

- Use template sensors to create alerts when stream count exceeds a threshold
- Create automations based on specific users streaming content
- Customize the card appearance using your own CSS in card-mod
