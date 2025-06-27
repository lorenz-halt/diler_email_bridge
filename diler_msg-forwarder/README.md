# DILER Message Forwarder

This project is designed to log into the DILER website, scrape unread messages, forward them via email, and mark them as read. 

## Project Structure

```
stuttgart-message-forwarder
├── src
│   ├── main.py            # Entry point of the application
│   ├── email_utils.py     # Utility functions for sending emails
│   ├── message_scraper.py  # Handles message scraping and processing
│   └── attachments         # Directory for storing downloaded attachments
├── .env                    # Environment variables for sensitive credentials
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd stuttgart-message-forwarder
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
python src/main.py
```

This will log into the Stuttgart Element-i Schule website, check for unread messages, forward them to the specified email address, and mark them as read.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes. 

## License

This project is licensed under the MIT License.