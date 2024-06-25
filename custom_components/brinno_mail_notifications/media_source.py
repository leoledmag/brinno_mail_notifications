import os
from homeassistant.components.media_source import MediaSource, BrowseMediaSource, MediaSourceItem, PlayMedia
from homeassistant.core import HomeAssistant

DOMAIN = "brinno_mail_notifications"

class BrinnoMediaSource(MediaSource):

    name = "Brinno"

    def __init__(self, hass: HomeAssistant, media_path: str):
        super().__init__(DOMAIN)
        self.hass = hass
        self.media_path = media_path
        
    async def async_get_media(self, item: MediaSourceItem) -> PlayMedia:
        try:
            media_url = self._get_media_url(item.identifier)
            return PlayMedia(media_url, "video/mp4")
        except Exception as e:
            # Log any error that occurs
            self.hass.components.logger.error(f"Error in async_get_media: {str(e)}")
            raise

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        try:
            media_url = self._get_media_url(item.identifier)
            return PlayMedia(media_url, "video/mp4")
        except Exception as e:
            # Log any error that occurs
            self.hass.components.logger.error(f"Error in async_resolve_media: {str(e)}")
            raise

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
                    can_expand=False,
                    #thumbnail=self._get_thumbnail_url(media_content_id),
                ))

        # Añadir la imagen de vista previa
        #thumbnail_url = self._get_media_url(media_content_id)
        #if os.path.exists(thumbnail_path):
        #    children.insert(0, BrowseMediaSource(
        #        domain=DOMAIN,
        #        identifier='thumbnail.jpg',
        #        media_class='image',
        #        media_content_type='image/jpeg',
        #        title='Brinno Thumbnail',
        #        can_play=True,
        #        can_expand=False
        #    ))

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
        
    def _get_media_url(self, media_id):
        url = get_url(self.hass, require_ssl=True)
        relative_path = os.path.relpath(os.path.join(self.media_path, media_id), self.media_path)
        return f"{url}/media/local/{relative_path.replace(os.sep, '/')}"
       
    def _get_media_path(self, media_id):
        # Obtener la ruta del archivo de video a partir del media_id
        # Por ejemplo, si media_id es "local/videos/favourites/Epic Sax Guy 10 Hours.mp4"
        # la ruta del archivo de video sería "/media/videos/favourites/Epic Sax Guy 10 Hours.mp4"
        #media_dir = self._media_dirs.get('local')
        #media_path = os.path.join(media_dir, media_id)
        return self.media_path
       
    def _generate_thumbnail(self, media_path):
        # Generar un thumbnail para el archivo de video
        # Por ejemplo, utilizando ffmpeg para extraer un frame del video
        thumbnail_path = f"{media_path}.thumb.jpg"
        if not os.path.exists(thumbnail_path):
            cmd = f"ffmpeg -i {media_path} -vf scale=320:180 -vframes 1 {thumbnail_path}"
            os.system(cmd)
        return thumbnail_path

async def async_get_media_source(hass: HomeAssistant) -> BrinnoMediaSource:
    media_path = hass.config.path("brinno")
    return BrinnoMediaSource(hass, media_path)
