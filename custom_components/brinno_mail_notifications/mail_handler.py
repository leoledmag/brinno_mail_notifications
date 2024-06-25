import imapclient
import email
import os
import logging
from email.utils import parsedate_to_datetime
from imapclient import SEEN
import asyncio
import imageio
from PIL import Image
import json
from datetime import datetime

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
        self.info_file = os.path.join(self.media_path, "info.json")
        os.makedirs(self.media_path, exist_ok=True)

    async def check_mail(self, mail_id=None):
        try:
            await asyncio.to_thread(self._check_mail, mail_id)
        except Exception as e:
            _LOGGER.error("Error checking mail: %s", e)

    def _check_mail(self, mail_id):
        try:
            with imapclient.IMAPClient(self.imap_server, port=self.imap_port, ssl=self.use_ssl) as client:
                _LOGGER.info("Connected to IMAP server")
                client.login(self.email_address, self.password)
                _LOGGER.info("Logged in as %s", self.email_address)
                client.select_folder('INBOX', readonly=not self.mark_as_read)

                if mail_id:
                    messages = [int(mail_id)]
                else:
                    last_processed_info = self._get_last_processed_info()
                    search_criteria = ['FROM', 'noreplies@cameras.brinno.info', 'SUBJECT', "Your Brinno Duo door camera noticed some activity"]
                    if last_processed_info:
                        last_processed_date_str = last_processed_info['date'].strftime('%d-%b-%Y') if last_processed_info['date'] else None
                        last_processed_uid = last_processed_info['uid']
                        _LOGGER.debug(f"Last processed date: {last_processed_date_str}, Last processed UID: {last_processed_uid}")
                        
                        if last_processed_uid:
                            search_criteria.extend(['UID', f'{last_processed_uid + 1}:*'])
                        elif last_processed_date_str:
                            search_criteria.extend(['SINCE', last_processed_date_str])

                    _LOGGER.debug(f"Search criteria: {search_criteria}")
                    messages = client.search(search_criteria)
                    messages.sort()

                _LOGGER.info(f"Found {len(messages)} messages")
                if not messages:
                    _LOGGER.info("No messages found")
                    return

                for uid in messages:
                    message_data = client.fetch(uid, ['RFC822', 'INTERNALDATE'])
                    for msgid, data in message_data.items():
                        internal_date = data[b'INTERNALDATE']
                        _LOGGER.debug(f"INTERNALDATE before conversion: {internal_date}")
                        msg_date = internal_date
                        _LOGGER.debug(f"Message date: {msg_date}")

                        msg = email.message_from_bytes(data[b'RFC822'])
                        if msg.is_multipart():
                            image_files = []
                            for part in msg.walk():
                                if part.get_content_type() == 'image/jpeg':
                                    filename = part.get_filename()
                                    if filename:
                                        image_dir = os.path.join(self.media_path, 'images')
                                        os.makedirs(image_dir, exist_ok=True)
                                        filepath = os.path.join(image_dir, filename)
                                        with open(filepath, 'wb') as f:
                                            f.write(part.get_payload(decode=True))
                                        _LOGGER.info(f"Saved image {filename}")
                                        image_files.append(filepath)

                            self._create_media_files(image_files)
                            
                            # Guardar la fecha y UID del correo procesado
                            if not mail_id:
                                self._save_last_processed_info(msg_date, uid)

                            # Opcional: marcar como leído o eliminar
                            if self.mark_as_read:
                                client.add_flags(uid, [SEEN])
                            if self.delete_after_download:
                                client.delete_messages(uid)
                client.logout()
            _LOGGER.info("Logged out from IMAP server")
        except Exception as e:
            _LOGGER.error(f"Exception during mail check: {e}")

    def _create_media_files(self, image_files):
        image_files.sort()  # Ensure alphabetical order
        if len(image_files) >= 3:
            base_filename = os.path.splitext(os.path.basename(image_files[0]))[0]

            gif_path = self.media_path
            mp4_path = self.media_path
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
            _LOGGER.info(f"Created GIF and MP4 files at {gif_output_path} and {mp4_output_path}")

    def _get_last_processed_info(self):
        try:
            if os.path.exists(self.info_file):
                with open(self.info_file, 'r') as f:
                    data = json.load(f)
                    date = datetime.fromisoformat(data['date']) if 'date' in data else None
                    uid = data['uid'] if 'uid' in data else None
                    _LOGGER.debug(f"Loaded last processed info: {date}, {uid}")
                    return {'date': date, 'uid': uid}
            _LOGGER.debug("No last processed info found")
            return {'date': None, 'uid': None}
        except Exception as e:
            _LOGGER.error(f"Error loading last processed info: {e}")
            return {'date': None, 'uid': None}

    def _save_last_processed_info(self, date, uid):
        try:
            with open(self.info_file, 'w') as f:
                json.dump({'date': date.isoformat(), 'uid': uid}, f)
            _LOGGER.debug(f"Saved last processed info: {date}, {uid}")
        except Exception as e:
            _LOGGER.error(f"Error saving last processed info: {e}")
