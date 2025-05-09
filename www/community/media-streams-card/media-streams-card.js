class MediaStreamsCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      // Initialize card
      this.innerHTML = `
        <ha-card>
          <div class="card-header">
            <div class="name">Media Streams</div>
          </div>
          <div class="card-content">
            <div id="streams-container"></div>
          </div>
        </ha-card>
      `;
      
      this.card = this.querySelector('ha-card');
      this.content = this.querySelector('#streams-container');
      
      // Add styling
      const style = document.createElement('style');
      style.textContent = `
        .server-container {
          margin-bottom: 16px;
        }
        .server-header {
          display: flex;
          align-items: center;
          margin-bottom: 8px;
        }
        .server-icon {
          margin-right: 8px;
        }
        .server-name {
          font-weight: bold;
          font-size: 16px;
        }
        .stream-count {
          margin-left: auto;
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-radius: 14px;
          padding: 4px 8px;
          font-size: 12px;
          font-weight: bold;
        }
        .stream-item {
          display: flex;
          padding: 8px;
          margin-bottom: 4px;
          border-radius: 4px;
          background: var(--card-background-color);
          border-left: 3px solid var(--primary-color);
        }
        .stream-info {
          flex-grow: 1;
        }
        .stream-title {
          font-weight: 500;
        }
        .stream-details {
          font-size: 12px;
          color: var(--secondary-text-color);
        }
        .stream-user {
          display: flex;
          align-items: center;
        }
        .user-icon {
          margin-right: 4px;
        }
        .no-streams {
          color: var(--secondary-text-color);
          font-style: italic;
        }
      `;
      this.appendChild(style);
    }

    // Get config
    const config = this.config || {};
    const jellyfin_entity = config.jellyfin_entity;
    const plex_entity = config.plex_entity;

    // Clear content
    this.content.innerHTML = '';

    // Helper to create stream blocks for each server
    const createServerBlock = (entityId, serverType) => {
      if (!entityId || !hass.states[entityId]) return;
      
      const state = hass.states[entityId];
      const streamCount = parseInt(state.state) || 0;
      const streams = state.attributes.streams || [];
      
      const serverContainer = document.createElement('div');
      serverContainer.className = 'server-container';
      
      // Server header with icon and count
      const serverHeader = document.createElement('div');
      serverHeader.className = 'server-header';
      
      const serverIcon = document.createElement('ha-icon');
      serverIcon.className = 'server-icon';
      serverIcon.icon = serverType === 'jellyfin' ? 'mdi:play-network' : 'mdi:plex';
      
      const serverName = document.createElement('div');
      serverName.className = 'server-name';
      serverName.textContent = serverType === 'jellyfin' ? 'Jellyfin' : 'Plex';
      
      const streamCountEl = document.createElement('div');
      streamCountEl.className = 'stream-count';
      streamCountEl.textContent = `${streamCount} active`;
      
      serverHeader.appendChild(serverIcon);
      serverHeader.appendChild(serverName);
      serverHeader.appendChild(streamCountEl);
      serverContainer.appendChild(serverHeader);
      
      // Stream list
      if (streamCount > 0) {
        streams.forEach(stream => {
          const streamItem = document.createElement('div');
          streamItem.className = 'stream-item';
          
          const streamInfo = document.createElement('div');
          streamInfo.className = 'stream-info';
          
          const streamTitle = document.createElement('div');
          streamTitle.className = 'stream-title';
          streamTitle.textContent = stream.title;
          
          const streamDetails = document.createElement('div');
          streamDetails.className = 'stream-details';
          
          // Type and method
          const streamType = document.createElement('div');
          streamType.textContent = `${stream.type} • ${stream.method}`;
          
          // User info
          const streamUser = document.createElement('div');
          streamUser.className = 'stream-user';
          
          const userIcon = document.createElement('ha-icon');
          userIcon.className = 'user-icon';
          userIcon.icon = 'mdi:account';
          userIcon.style.width = '12px';
          userIcon.style.height = '12px';
          
          const userName = document.createElement('span');
          userName.textContent = stream.user;
          
          streamUser.appendChild(userIcon);
          streamUser.appendChild(userName);
          
          streamDetails.appendChild(streamType);
          streamDetails.appendChild(streamUser);
          
          streamInfo.appendChild(streamTitle);
          streamInfo.appendChild(streamDetails);
          
          streamItem.appendChild(streamInfo);
          serverContainer.appendChild(streamItem);
        });
      } else {
        const noStreams = document.createElement('div');
        noStreams.className = 'no-streams';
        noStreams.textContent = 'No active streams';
        serverContainer.appendChild(noStreams);
      }
      
      this.content.appendChild(serverContainer);
    };

    // Create blocks for each configured server
    if (jellyfin_entity) createServerBlock(jellyfin_entity, 'jellyfin');
    if (plex_entity) createServerBlock(plex_entity, 'plex');
    
    // If no entities configured, show message
    if (!jellyfin_entity && !plex_entity) {
      this.content.innerHTML = `
        <div style="color: var(--error-color);">
          Please configure media server entities in the card settings.
        </div>
      `;
    }
  }

  setConfig(config) {
    if (!config.jellyfin_entity && !config.plex_entity) {
      throw new Error('Please define at least one media server entity (jellyfin_entity or plex_entity)');
    }
    this.config = config;
    this.title = config.title || 'Media Streams';
  }

  getCardSize() {
    return 3;
  }

  static getConfigElement() {
    return document.createElement('media-streams-card-editor');
  }

  static getStubConfig() {
    return {
      jellyfin_entity: 'sensor.media_streams_jellyfin',
      plex_entity: 'sensor.media_streams_plex'
    };
  }
}

// Card editor (simplified for now)
class MediaStreamsCardEditor extends HTMLElement {
  setConfig(config) {
    this.config = config;
  }

  get _jellyfin_entity() {
    return this.config.jellyfin_entity || '';
  }

  get _plex_entity() {
    return this.config.plex_entity || '';
  }

  render() {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
    }

    this.shadowRoot.innerHTML = `
      <form class="row">
        <ha-selector-entity
          .hass=${this.hass}
          .label=${"Jellyfin Entity"}
          .value=${this._jellyfin_entity}
          .configValue=${"jellyfin_entity"}
          include-domains='["sensor"]'
          @value-changed=${this._valueChanged}
        ></ha-selector-entity>
        <ha-selector-entity
          .hass=${this.hass}
          .label=${"Plex Entity"}
          .value=${this._plex_entity}
          .configValue=${"plex_entity"}
          include-domains='["sensor"]'
          @value-changed=${this._valueChanged}
        ></ha-selector-entity>
      </form>
    `;
  }

  _valueChanged(ev) {
    if (!this.config || !this.hass) return;
    
    const target = ev.target;
    if (!target.configValue) return;

    const newConfig = {
      ...this.config,
      [target.configValue]: ev.detail.value,
    };
    
    this.config = newConfig;
    
    const event = new CustomEvent('config-changed', {
      detail: { config: newConfig },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }
}

customElements.define('media-streams-card', MediaStreamsCard);
customElements.define('media-streams-card-editor', MediaStreamsCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'media-streams-card',
  name: 'Media Streams Card',
  description: 'A card that displays active streams from your media servers',
});
