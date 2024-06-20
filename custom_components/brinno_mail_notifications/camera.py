import os
from homeassistant.components.camera import Camera

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = config_entry.data
    async_add_entities([BrinnoMailCamera(hass, config)], True)

class BrinnoMailCamera(Camera):
    def __init__(self, hass, config):
        super().__init__()
        self.hass = hass
        self.config = config
        self._media_path = hass.config.path("Brinno", config["mailbox_name"], 'mp4')
        self._unique_id = f"brinno_mail_camera_{config['mailbox_name']}"
        self._name = f"Brinno Mail Camera {self.config['mailbox_name']}"
        os.makedirs(self._media_path, exist_ok=True)  # Crear el directorio si no existe
        self._update_video_path()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    async def async_camera_image(self, width=None, height=None):
        """Return bytes of the latest camera video."""
        self._update_video_path()
        if not self._video_path or not os.path.exists(self._video_path):
            return None
        return await self.hass.async_add_executor_job(self._read_video)

    def _update_video_path(self):
        """Update the path to the latest video file."""
        mp4_files = [f for f in os.listdir(self._media_path) if f.endswith('.mp4')]
        if mp4_files:
            latest_mp4 = max(mp4_files, key=lambda x: os.path.getctime(os.path.join(self._media_path, x)))
            self._video_path = os.path.join(self._media_path, latest_mp4)
        else:
            self._video_path = None

    def _read_video(self):
        with open(self._video_path, 'rb') as f:
            return f.read()

    @property
    def should_poll(self):
        return False
