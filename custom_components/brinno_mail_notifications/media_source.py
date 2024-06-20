import os
from homeassistant.components.media_source import MediaSource, BrowseMediaSource, MediaSourceItem
from homeassistant.core import HomeAssistant

DOMAIN = "brinno_mail_notifications"

class BrinnoMediaSource(MediaSource):

    name = "Brinno"

    def __init__(self, hass: HomeAssistant, media_path: str):
        super().__init__(DOMAIN)
        self.hass = hass
        self.media_path = media_path

    async def async_resolve_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        return item

    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        if item.identifier:
            dir_path = os.path.join(self.media_path, item.identifier)
        else:
            dir_path = self.media_path

        if not os.path.isdir(dir_path):
            return None

        children = []
        for entry in os.listdir(dir_path):
            full_path = os.path.join(dir_path, entry)
            if os.path.isdir(full_path):
                children.append(BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=entry,
                    media_class='directory',
                    media_content_type='',
                    title=entry,
                    can_play=False,
                    can_expand=True,
                ))
            else:
                media_class = 'video' if entry.endswith('.mp4') else 'image'
                media_content_type = 'video/mp4' if entry.endswith('.mp4') else 'image/jpeg'
                children.append(BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=entry,
                    media_class=media_class,
                    media_content_type=media_content_type,
                    title=entry,
                    can_play=True,
                    can_expand=False
                ))

        # Añadir la imagen de vista previa
        thumbnail_path = os.path.join(self.media_path, 'thumbnail.jpg')
        if os.path.exists(thumbnail_path):
            children.insert(0, BrowseMediaSource(
                domain=DOMAIN,
                identifier='thumbnail.jpg',
                media_class='image',
                media_content_type='image/jpeg',
                title='Brinno Thumbnail',
                can_play=True,
                can_expand=False
            ))

        return BrowseMediaSource(
            domain=DOMAIN,
            identifier='',
            media_class='directory',
            media_content_type='',
            title='Brinno',
            can_play=False,
            can_expand=True,
            children=children
        )

async def async_get_media_source(hass: HomeAssistant) -> BrinnoMediaSource:
    media_path = hass.config.path("Brinno")
    return BrinnoMediaSource(hass, media_path)
