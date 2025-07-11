# DILER Message Forwarder

This project is designed to log into the DILER website, scrape unread messages, forward them via email, and mark them as read. 

## Project Structure

```
diler-msg-forwarder
├── src
│   ├── main.py            # Entry point of the application
│   ├── email_utils.py     # Utility functions for sending emails
│   ├── message_scraper.py  # Handles message scraping and processing
│   └── attachments         # Directory for storing downloaded attachments (will be created on-demand)
├── .env                    # Environment variables for sensitive credentials
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone https://github.com/lorenz-halt/diler_message_forwarder.git
   cd diler-msg-forwarder
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory and add your credentials:
   ```
   DILER_URL=https://schule.de
   DILER_USERNAME=user.name
   DILER_PASSWORD=xxx

   EMAIL_ADDRESS=email.sender@host.com
   EMAIL_PASSWORD=yyy
   SMTP_SERVER=mail.host.net
   SMTP_PORT=587

   TO_EMAIL_ADDRESS=user.name@host.de
   ```

## Usage

To run the application, execute the following command:
```
cd diler-msg-forwarder
python src/main.py
```

This will log into the DILER Schule website, check for unread messages, forward them to the specified email address, and mark them as read.

## Cronjob (Linux)

To run the application periodically on your device consider setting up cronjobs.

These two example cronjobs execute the script Mondays to Fridays during working hours every 30 minutes and Sundays afternoon once (for emergency messages):
```
crontab -e
```
Add to the end (replace __<path to your clone>__):
```
*/30 6-18 * * 1-5 /__<path to your clone>__/diler-msg-forwarder/venv/bin/python /__<path to your clone>__/diler-msg-forwarder/src/main.py >> /var/log/diler_msg.log 2>&1
0 16 * * 0 /__<path to your clone>__/diler-msg-forwarder/venv/bin/python /__<path to your clone>__/diler-msg-forwarder/src/main.py >> /var/log/diler_msg.log 2>&1
```

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes. 

## License

This project is licensed under the MIT License.
