import logging
import os
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.integration_platform import async_process_integration_platforms

from .const import DOMAIN
from .media_source import async_get_media_source, BrinnoMediaSource
from .mail_handler import MailHandler

_LOGGER = logging.getLogger(__name__)

SERVICE_CHECK_MAIL = 'check_mail'

SERVICE_CHECK_MAIL_SCHEMA = vol.Schema({
    vol.Required('mailbox_name'): cv.string,
    vol.Optional('mail_uuid'): cv.string,
})

async def async_setup(hass: HomeAssistant, config: dict):
    async def handle_check_mail(call: ServiceCall):
        mailbox_name = call.data['mailbox_name']
        mail_uuid = call.data.get('mail_uuid')
        _LOGGER.debug("Service called to get mail with mailbox_name: %s, mail_uuid: %s", mailbox_name, mail_uuid)
        
        # Find the correct config entry based on the mailbox_name
        config_entry = next(
            (entry for entry in hass.config_entries.async_entries(DOMAIN) if entry.data['mailbox_name'] == mailbox_name), 
            None
        )

        if config_entry is None:
            _LOGGER.error("No configuration found for mailbox_name: %s", mailbox_name)
            return

        # Initialize MailHandler with appropriate configuration
        mail_handler = MailHandler(
            imap_server=config_entry.data.get('imap_server'),
            imap_port=config_entry.data.get('imap_port', 993),
            use_ssl=config_entry.data.get('use_ssl', True),
            email_address=config_entry.data.get('email'),
            password=config_entry.data.get('password'),
            mailbox_name=config_entry.data.get('mailbox_name'),
            mark_as_read=config_entry.data.get('mark_as_read', False),
            delete_after_download=config_entry.data.get('delete_after_download', False),
            media_path=hass.config.path("config", "brinno")
        )

        await mail_handler.check_mail(mail_uuid)

    hass.services.async_register(DOMAIN, SERVICE_CHECK_MAIL, handle_check_mail, schema=SERVICE_CHECK_MAIL_SCHEMA)

    return True

#async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
#    """Set up the Brinno camera sensor platform."""
#    entities = []
#    camera_sensor = BrinnoMailCamera(config)
#    entities.append(camera_sensor)
#    async_add_entities(entities, True)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    media_path = hass.config.path("brinno")
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
    #await hass.helpers.integration_platform.async_process_integration_platforms(DOMAIN, media_source_instance)
    #await async_process_integration_platforms(hass, DOMAIN, async_setup_platform, entry)
    await async_process_integration_platforms(hass, DOMAIN, media_source_instance)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "camera")
    return True
