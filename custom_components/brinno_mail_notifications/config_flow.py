import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN

@callback
def configured_instances(hass):
    return [
        entry.title for entry in hass.config_entries.async_entries(DOMAIN)
    ]

class BrinnoMailNotificationsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            if user_input["mailbox_name"] not in configured_instances(self.hass):
                return self.async_create_entry(title=user_input["mailbox_name"], data=user_input)
            else:
                errors["base"] = "name_exists"
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("mailbox_name"): str,
                vol.Required("imap_server"): str,
                vol.Required("imap_port", default=993): int,
                vol.Required("use_ssl", default=True): bool,
                vol.Required("email"): str,
                vol.Required("password"): str,
                vol.Optional("mark_as_read", default=False): bool,
                vol.Optional("delete_after_download", default=False): bool,
            }),
            errors=errors,
        )
