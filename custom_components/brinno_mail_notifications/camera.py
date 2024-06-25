import os
import aiofiles
import logging
from homeassistant.components.camera import Camera, CameraEntityFeature
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = config_entry.data
    _LOGGER.debug("Setting up BrinnoMailCamera with config: %s", config)
    async_add_entities([BrinnoMailCamera(hass, config)], True)

class BrinnoMailCamera(Camera):
    def __init__(self, hass, config):
        super().__init__()
        self.hass = hass
        self.config = config
        self._media_path = hass.config.path("brinno", config["mailbox_name"])
        self._unique_id = f"{config['mailbox_name']}"
        self._name = f"{self.config['mailbox_name']}"
        os.makedirs(self._media_path, exist_ok=True)  # Crear el directorio si no existe
        self._video_path = None
        self._gif_path = None
        _LOGGER.debug("Initializing BrinnoMailCamera: name=%s, media_path=%s", self._name, self._media_path)
        self._update_media_paths()

    @property
    def name(self):
        return self._name

    @property
    def brand(self):
        return "Brinno"

    @property
    def model(self):
        return "SHC1000W"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def stream_source(self):
        """Return the URL to the video stream."""
        self._update_media_paths()
        if self._video_path:
            _LOGGER.debug("Stream source for %s: %s", self._name, self._video_path)
            return f"file://{self._video_path}"
        _LOGGER.debug("No video path found for %s", self._name)
        return None

    async def async_camera_image(self):
        """Return the latest still image (GIF) from the camera."""
        self._update_media_paths()
        if not self._gif_path or not os.path.exists(self._gif_path):
            _LOGGER.debug("No GIF path found for %s", self._name)
            return None

        try:
            async with aiofiles.open(self._gif_path, 'rb') as f:
                _LOGGER.debug("Reading GIF for %s from %s", self._name, self._gif_path)
                return await f.read()
        except Exception as e:
            _LOGGER.error("Error reading GIF for %s: %s", self._name, e)
            return None

    def _update_media_paths(self):
        """Update the paths to the latest video and GIF files."""
        try:
            mp4_files = [f for f in os.listdir(self._media_path) if f.endswith('.mp4')]
            if mp4_files:
                latest_mp4 = max(mp4_files)
                self._video_path = os.path.join(self._media_path, latest_mp4)
                self._gif_path = os.path.splitext(self._video_path)[0] + '.gif'
                _LOGGER.debug("Updated media paths for %s: video_path=%s, gif_path=%s", self._name, self._video_path, self._gif_path)
            else:
                self._video_path = None
                self._gif_path = None
                _LOGGER.debug("No MP4 files found in %s for %s", self._media_path, self._name)
        except Exception as e:
            _LOGGER.error("Error updating media paths for %s: %s", self._name, e)

    @property
    def should_poll(self):
        return False

    @property
    def supported_features(self):
        return CameraEntityFeature(0)
