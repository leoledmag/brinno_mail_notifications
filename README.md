# Brinno Mail Notifications

This Home Assistant integration monitors emails from the Brinno Duo camera, automatically downloading attached images and generating GIFs and MP4 videos. It supports multiple mailboxes and offers configurable options to mark emails as read and delete them after downloading.

## Installation

1. Ensure you have HACS installed in your Home Assistant.
2. Add this repository to HACS as a custom repository.
3. Install the "Brinno Mail Notifications" integration from HACS.

## Configuration

1. Go to Configuration > Integrations.
2. Click on "Add Integration" and search for "Brinno Mail Notifications".
3. Follow the setup wizard to configure your email account and preferences:
    - **Mailbox Name**: A unique name for your mailbox.
    - **IMAP Server**: The IMAP server address for your email provider.
    - **IMAP Port**: The IMAP server port (default is 993).
    - **Use SSL**: Whether to use SSL for the IMAP connection (default is Yes).
    - **Email**: Your email address.
    - **Password**: Your email password.
    - **Mark Emails as Read**: Option to mark emails as read after downloading images (default is No).
    - **Delete Emails After Download**: Option to delete emails after downloading images (default is No).

## Features

- **Multiple Mailbox Support**: Monitor multiple email accounts simultaneously.
- **Automatic Image Download**: Automatically download images attached to specific emails from your Brinno Duo door camera.
- **GIF and MP4 Generation**: Generate a GIF and an MP4 video from the downloaded images.
- **Camera Entity**: Create a camera entity in Home Assistant to display the last generated MP4 video.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
