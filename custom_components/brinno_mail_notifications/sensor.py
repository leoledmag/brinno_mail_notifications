from homeassistant.helpers.entity import Entity
from .const import DOMAIN
from .mail_handler import MailHandler

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = config_entry.data
    async_add_entities([BrinnoMailSensor(hass, config)], True)

class BrinnoMailSensor(Entity):
    def __init__(self, hass, config):
        self.hass = hass
        self.config = config
        self._state = None
        self._media_path = hass.config.path("brinno")
        self.mail_handler = MailHandler(
            imap_server=config["imap_server"],
            imap_port=config["imap_port"],
            use_ssl=config["use_ssl"],
            email_address=config["email"],
            password=config["password"],
            mailbox_name=config["mailbox_name"],
            mark_as_read=config["mark_as_read"],
            delete_after_download=config["delete_after_download"],
            media_path=self._media_path
        )
        self._unique_id = f"brinno_mail_sensor_{config['mailbox_name']}"
        self._name = f"Brinno Mail Sensor {self.config['mailbox_name']}"

    async def async_added_to_hass(self):
        await self.mail_handler.check_mail()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        return self._state

    async def async_update(self):
        await self.mail_handler.check_mail()
        self._state = "Mail Checked"
