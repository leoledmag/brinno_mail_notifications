import imapclient
import email
import os
from email.header import decode_header

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

    def check_mail(self):
        with imapclient.IMAPClient(self.imap_server, port=self.imap_port, ssl=self.use_ssl) as client:
            client.login(self.email_address, self.password)
            client.select_folder('INBOX', readonly=not self.mark_as_read)
            
            messages = client.search(['FROM', 'noreplies@cameras.brinno.info', 'SUBJECT', "Your Brinno Duo door camera noticed some activity"])
            for uid in messages:
                message_data = client.fetch(uid, ['RFC822'])
                for msgid, data in message_data.items():
                    msg = email.message_from_bytes(data[b'RFC822'])
                    if msg.is_multipart():
                        image_count = 0
                        for part in msg.walk():
                            if part.get_content_type() == 'image/jpeg' and image_count < 3:
                                filename = f"image_{image_count + 1}.jpg"
                                filepath = os.path.join(self.media_path, filename)
                                with open(filepath, 'wb') as f:
                                    f.write(part.get_payload(decode=True))
                                image_count += 1

                        # Optional: mark as read or delete
                        if self.mark_as_read:
                            client.add_flags(uid, [imapclient.SEEN])
                        if self.delete_after_download:
                            client.delete_messages(uid)
            client.logout()
        
        self.create_media_files()
    
    def create_media_files(self):
        import imageio
        from PIL import Image
        
        images = [os.path.join(self.media_path, f) for f in os.listdir(self.media_path) if f.endswith('.jpg')]
        images.sort()
        
        if len(images) >= 3:
            gif_path = os.path.join(self.media_path, 'gif')
            mp4_path = os.path.join(self.media_path, 'mp4')
            os.makedirs(gif_path, exist_ok=True)
            os.makedirs(mp4_path, exist_ok=True)
            
            gif_images = [Image.open(img) for img in images[:3]]
            gif_output_path = os.path.join(gif_path, 'activity.gif')
            gif_images[0].save(gif_output_path, save_all=True, append_images=gif_images[1:], duration=500, loop=0)
            
            mp4_output_path = os.path.join(mp4_path, 'activity.mp4')
            writer = imageio.get_writer(mp4_output_path, fps=2)
            for img in images[:3]:
                writer.append_data(imageio.imread(img))
            writer.close()
