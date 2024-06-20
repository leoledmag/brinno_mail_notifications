from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import os

from .const import DOMAIN
from .media_source import async_get_media_source, BrinnoMediaSource

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    media_path = hass.config.path("Brinno")
    os.makedirs(media_path, exist_ok=True)  # Crear el directorio si no existe

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "camera")
    )

    # Registrar media source
    hass.data.setdefault(DOMAIN, {})
    media_source_instance = await async_get_media_source(hass)
    hass.data[DOMAIN][entry.entry_id] = media_source_instance
    hass.helpers.integration_platform.async_register_integration_platform(
        DOMAIN, media_source_instance
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "camera")
    return True
