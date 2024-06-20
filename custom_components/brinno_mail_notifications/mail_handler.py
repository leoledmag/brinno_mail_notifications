import imapclient
import email
import os
import logging
from email.header import decode_header
from imapclient import SEEN
import asyncio
import imageio
from PIL import Image

_LOGGER = logging.getLogger(__name__)

class MailHandler:
    def __init__(self, imap_server, imap_port, use_ssl, email_address, password, mailbox_name, mark_as_read, delete_after_download, media_path):
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.use_ssl = use_ssl
        self.email_address = email_address
        self.password = password
        self.mailbox_name = mailbox_name
        self.mark_as_read = mark_as_read
        self.delete_after_download = delete_after_download
        self.media_path = os.path.join(media_path, mailbox_name)
        os.makedirs(self.media_path, exist_ok=True)

    async def check_mail(self):
        try:
            await asyncio.to_thread(self._check_mail)
        except Exception as e:
            _LOGGER.error("Error checking mail: %s", e)

    def _check_mail(self):
        with imapclient.IMAPClient(self.imap_server, port=self.imap_port, ssl=self.use_ssl) as client:
            _LOGGER.info("Connected to IMAP server")
            client.login(self.email_address, self.password)
            _LOGGER.info("Logged in as %s", self.email_address)
            client.select_folder('INBOX', readonly=not self.mark_as_read)

            messages = client.search(['FROM', 'noreplies@cameras.brinno.info', 'SUBJECT', "Your Brinno Duo door camera noticed some activity"])
            _LOGGER.info("Found %d messages", len(messages))
            for uid in messages:
                message_data = client.fetch(uid, ['RFC822'])
                image_files = []
                for msgid, data in message_data.items():
                    msg = email.message_from_bytes(data[b'RFC822'])
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'image/jpeg':
                                filename = part.get_filename()
                                if filename:
                                    filepath = os.path.join(self.media_path, filename)
                                    with open(filepath, 'wb') as f:
                                        f.write(part.get_payload(decode=True))
                                    _LOGGER.info("Saved image %s", filename)
                                    image_files.append(filepath)

                        # Opcional: marcar como leído o eliminar
                        if self.mark_as_read:
                            client.add_flags(uid, [SEEN])
                        if self.delete_after_download:
                            client.delete_messages(uid)
            client.logout()
        _LOGGER.info("Logged out from IMAP server")
        self._create_media_files(image_files)

    def _create_media_files(self, image_files):
        image_files.sort()  # Ensure alphabetical order
        if len(image_files) >= 3:
            base_filename = os.path.splitext(os.path.basename(image_files[0]))[0]
            
            gif_path = os.path.join(self.media_path, 'gif')
            mp4_path = os.path.join(self.media_path, 'mp4')
            os.makedirs(gif_path, exist_ok=True)
            os.makedirs(mp4_path, exist_ok=True)

            gif_images = [Image.open(img) for img in image_files[:3]]
            gif_output_path = os.path.join(gif_path, f'{base_filename}.gif')
            gif_images[0].save(gif_output_path, save_all=True, append_images=gif_images[1:], duration=500, loop=0)

            mp4_output_path = os.path.join(mp4_path, f'{base_filename}.mp4')
            writer = imageio.get_writer(mp4_output_path, fps=2, codec='libx264')
            for img in image_files[:3]:
                writer.append_data(imageio.imread(img))
            writer.close()
            _LOGGER.info("Created GIF and MP4 files")
