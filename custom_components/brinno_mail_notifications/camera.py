from homeassistant.components.camera import Camera

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = config_entry.data
    async_add_entities([BrinnoMailCamera(hass, config)], True)

class BrinnoMailCamera(Camera):
    def __init__(self, hass, config):
        super().__init__()
        self.hass = hass
        self.config = config
        self._media_path = hass.config.path("media/Brinno", config["mailbox_name"], 'mp4')
        self._video_path = os.path.join(self._media_path, 'activity.mp4')

    @property
    def name(self):
        return f"Brinno Mail Camera {self.config['mailbox_name']}"

    def camera_image(self):
        with open(self._video_path, 'rb') as f:
            return f.read()

    @property
    def should_poll(self):
        return False
