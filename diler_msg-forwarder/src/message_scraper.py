import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import email_utils
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

load_dotenv()

class MessageScraper:
    def __init__(self, url=None, username=None, password=None):
        self.session = requests.Session()
        self.base_url = url
        self.username = username
        self.password = password
        self.driver = None

    def __enter__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Delete all files in the attachments folder on exit
        attachments_dir = os.path.join(os.path.dirname(__file__), 'attachments')
        if os.path.exists(attachments_dir):
            for filename in os.listdir(attachments_dir):
                file_path = os.path.join(attachments_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_unread_messages(self):
        driver = self.driver
        wait = WebDriverWait(driver, 20)
        messages = []
        driver.get(self.base_url)
        wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        driver.find_element(By.NAME, 'username').send_keys(self.username)
        driver.find_element(By.NAME, 'password').send_keys(self.password)
        # Try multiple selectors for the login button
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        except Exception:
            try:
                login_btn = driver.find_element(By.XPATH, '//input[@type="submit"]')
            except Exception:
                try:
                    login_btn = driver.find_element(By.NAME, 'Submit')
                except Exception:
                    print(driver.page_source)
                    raise Exception('Login button not found. See page source above.')
        login_btn.click()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        # Switch to messages inbox 
        driver.get(f'{self.base_url}/messages/inbox')
        wait.until(EC.presence_of_element_located((By.ID, 'texterMessages')))
        
        # Select '365 Tage' (all messages)
        try:
            btn_365 = driver.find_element(By.XPATH, '//label[@for="ts4"]')
            btn_365.click()
            time.sleep(1)
        except Exception:
            print("365 Tage button not found, skipping.")
        
        # Select 'Ungelesene' (unread)
        try:
            btn_unread = driver.find_element(By.XPATH, '//label[@for="mt_read_status_unread"]')
            btn_unread.click()
            time.sleep(2)
        except Exception:
            print("Ungelesene button not found, skipping.")

        # Work on the messages table
        messages_table = driver.find_element(By.ID, 'texterMessages')
        unread_ids = []
        for elem in messages_table.find_elements(By.CSS_SELECTOR, 'tr'):
            row_class = elem.get_attribute('class') or ''
            is_unread = 'unread' in row_class
            if not is_unread:
                try:
                    mid = elem.get_attribute('id')
                    read_btn = elem.find_element(By.XPATH, f'.//button[contains(@id, "read{mid}")]')
                    icon = read_btn.find_element(By.TAG_NAME, 'i')
                    if 'fa-eye-slash' in icon.get_attribute('class'):
                        is_unread = True
                except Exception:
                    pass
            if is_unread:
                message_id = elem.get_attribute('id')
                unread_ids.append(message_id)

        # Now process each unread message by id, always re-locating the row
        for message_id in unread_ids:
            try:
                elem = driver.find_element(By.ID, message_id)
                sender = elem.find_element(By.CSS_SELECTOR, '.sender').text
                message_html = elem.find_element(By.CSS_SELECTOR, '.message-text .texterMessage').get_attribute('innerHTML')
                try:
                    subject = elem.find_element(By.CSS_SELECTOR, '.subject').text
                except Exception:
                    subject = ''
                attachments = []
                download_failures = []
                soup = BeautifulSoup(message_html, 'html.parser')
                # Now find all download links in the message
                for a in soup.find_all('a'):
                    url = a.get('rel') or a.get('href')
                    if isinstance(url, list):
                        url = url[0] if url else None
                    if url and isinstance(url, str) and url.startswith('index.php?option=com_diler'):
                        match = re.search(r'search=id:(\d+)', url)
                        if not match:
                            continue
                        media_id = match.group(1)
                        cloud_url = f'{self.base_url}/{url}'
                        inbox_url = driver.current_url
                        # Add download link to email body (absolute URL)
                        a.attrs = {}
                        a['href']=cloud_url
                        # Download link for the email body
                        driver.get(cloud_url)
                        time.sleep(2)
                        try:
                            tr = driver.find_element(By.XPATH, f'//tr[@data-media-id="{media_id}"]')
                            download_a = tr.find_element(By.CSS_SELECTOR, 'a.fileDownload')
                            download_url = download_a.get_attribute('href')
                            filename = download_a.get_attribute('data-filename')
                            if not filename:
                                try:
                                    filename = tr.find_element(By.CSS_SELECTOR, '.fileName.mediaDisplay').get_attribute('title')
                                except Exception:
                                    filename = download_a.text or f'file_{media_id}'
                            local_path = os.path.join(os.path.dirname(__file__), 'attachments', filename)
                            os.makedirs(os.path.dirname(local_path), exist_ok=True)
                            selenium_cookies = driver.get_cookies()
                            cookies_dict = {c['name']: c['value'] for c in selenium_cookies}
                            user_agent = driver.execute_script("return navigator.userAgent;")
                            headers = {'User-Agent': user_agent}
                            r = requests.get(download_url, cookies=cookies_dict, headers=headers, stream=True)
                            try:
                                with open(local_path, 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                attachments.append(local_path)
                            except Exception as e:
                                print(f"Error downloading attachment {filename}: {e}")
                                download_failures.append(filename)
                        except Exception as e:
                            print(f"Could not download attachment for media_id {media_id}: {e}")
                            download_failures.append(f"media_id {media_id}")
                        driver.get(inbox_url)
                        time.sleep(1)
                # Convert soup back to HTML for message_html
                message_html = str(soup)
                # If any download failed, add a comment to the email
                if download_failures:
                    message_html += (
                        "<br><br><br><b>Achtung:</b> "
                        "Der Download der folgenden Datei(en) ist fehlgeschlagen: "
                        f"{', '.join(download_failures)}. "
                        "Sie können die Datei(en) evtl. manuell über den Link oben im Browser herunterladen."
                    )
                messages.append({
                    'id': message_id,
                    'subject': subject or f'DILER Nachricht von {sender}',
                    'body': message_html,
                    'attachments': attachments,
                })
            except Exception as e:
                print(f"Error processing message {message_id}: {e}")
        return messages

    def mark_message_as_read(self, message_id):
        driver = self.driver
        wait = WebDriverWait(driver, 20)
        
        # Switch to messages inbox 
        driver.get(f'{self.base_url}/messages/inbox')
        wait.until(EC.presence_of_element_located((By.ID, 'texterMessages')))
        
        # Select '365 Tage' (all messages)
        try:
            btn_365 = driver.find_element(By.XPATH, '//label[@for="ts4"]')
            btn_365.click()
            time.sleep(1)
        except Exception:
            print("365 Tage button not found, skipping.")
        
        # Select 'Ungelesene' (unread)
        try:
            btn_unread = driver.find_element(By.XPATH, '//label[@for="mt_read_status_unread"]')
            btn_unread.click()
            time.sleep(2)
        except Exception:
            print("Ungelesene button not found, skipping.")

        try:
            read_btn = driver.find_element(By.XPATH, f'//tr[@id="{message_id}"]//button[contains(@id, "read{message_id}")]')
            icon = read_btn.find_element(By.TAG_NAME, 'i')
            if 'fa-eye-slash' in icon.get_attribute('class') or 'fa-eye' in icon.get_attribute('class'):
                read_btn.click()
                time.sleep(1)
        except Exception as e:
            print(f"Could not mark message {message_id} as read: {e}")
