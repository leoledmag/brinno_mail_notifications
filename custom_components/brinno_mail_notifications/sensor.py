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
        self._media_path = hass.config.path("media/Brinno")
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
        self.check_mail()

    def check_mail(self):
        self.mail_handler.check_mail()
        self._state = "Mail Checked"

    @property
    def name(self):
        return f"Brinno Mail Sensor {self.config['mailbox_name']}"

    @property
    def state(self):
        return self._state
        
    @property
    def icon(self):
        return "mdi:doorbell-video" 

    def update(self):
        self.check_mail()
