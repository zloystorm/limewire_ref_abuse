from fake_useragent import UserAgent
import time
import tls_client
import imaplib
import email
import re
import json
import itertools
import logging



good = open('registred.txt', 'a')
bad = open('unregistred.txt', 'a')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_with_ref_code = open('file_with_ref_core.txt', 'a')

imap_host = 'imap.rambler.ru'
refka = '2SD5F9'
proxy = 'http://gaunter123:2a8a9d@51.77.79.248:11435'

def main():
    with open('emails.txt', 'r') as file_to_emails, open('file_with_ref_core.txt', 'r') as file_with_ref:
        while True:
            refka_list = [line.strip().split(':')[2] for line in file_with_ref]
            login1 = [line.strip().split(':')[0] for line in file_with_ref]
            refka_cycle = itertools.cycle(refka_list)
            for refka in refka_cycle:
                logger.info(f'Working on: {login1}')
                for _ in range(86):
                    time.sleep(1)
                    UAgent = UserAgent().random
                    jopech = file_to_emails.readline()
                    email_login = jopech.split(":")[0]
                    email_pass = jopech.split(":")[1]
                    sess = tls_client.Session(client_identifier=UAgent)
                    sess.proxies = {
                        'http': proxy,
                        'https': proxy
                    }
                    headers = {
                        'Accept': '*/*',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Host': 'api.kickofflabs.com',
                        'origin': 'https://lmwr.com',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'cross-site',
                        'User-Agent': UAgent
                        }

                    headers_confirm = {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Connection': 'keep-alive',
                        'Host': 'u33202342.ct.sendgrid.net',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'site',
                        'User-Agent': UAgent
                        }

                    sess.headers = headers

                    url = 'https://api.kickofflabs.com/v1/171250/subscribe'
                    data = {
                        'email': email_login,
                        'social_id': refka
                    }
                    try:
                        r = sess.post(url=url, headers=headers, data=data)
                    except Exception as ex:
                        print(ex)
                        continue
                    if r.status_code == 200:
                        print(f'\nmain sent: {email_login}')  
                        ref_code = json.loads(r.text)          
                    else:
                        print('хуйня, нихуя не отрправилось, ну и похуй')
                        time.sleep(1)
                        continue

                    target_subject = 'LimeWire Token Sale: Please confirm your e-mail address'
                    try:
                        max_wait_time = 10
                        start_time = time.time()
                        imap = imaplib.IMAP4_SSL(imap_host)
                        imap.login(email_login, email_pass)
                        imap.select('INBOX')
                        _, inbox_data = imap.search(None, 'HEADER', 'Subject', '"LimeWire Token Sale: Please confirm your e-mail address"')
                        inbox_msg_ids = inbox_data[0].split()
                        all_msg_ids = inbox_msg_ids
                        relevant_msg_ids = []
                        while True:
                            if time.time() - start_time >= max_wait_time:
                                print(f'\rWaiting mail: {remaining_time:.1f} сек.', end='', flush=True)
                                break
                            remaining_time = max_wait_time - (time.time() - start_time)
                            print(f'Waiting mail: {remaining_time:.1f} сек.', end='\r')
                            _, all_msg_ids = imap.search(None, 'ALL')
                            for msg_id in all_msg_ids[0].split():
                                _, msg_data_content = imap.fetch(msg_id, '(RFC822)')
                                email_body = msg_data_content[0][1].decode('utf-8')
                                email_message = email.message_from_string(email_body)
                                if email_message['Subject'] == target_subject:
                                    relevant_msg_ids.append(msg_id)
                                    break
                            else:
                                continue
                            break
                        if len(relevant_msg_ids) == 0:
                            print(f'\nNo relevant emails found in account in 10 sec {email_login}.')
                            bad.write(f'\n{email_login}:{email_pass}')
                            imap.close()
                            imap.logout()
                            continue
                        elif len(relevant_msg_ids) > 1:
                            print(f'Dva pisma nachel {email_login}. bery poslednee')
                            msg_id = relevant_msg_ids[-1]
                        else:
                            msg_id = relevant_msg_ids[0]
                        _, msg_data_content = imap.fetch(msg_id, '(RFC822)')
                        email_body = msg_data_content[0][1].decode('utf-8')
                        email_message = email.message_from_string(email_body)
                        links = []
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                try:
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    pass
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    for match in re.findall(r'(https?://[^\s]+)', body):
                                        links.append(match)
                        else:
                            body = email_message.get_payload(decode=True).decode()
                            for match in re.findall(r'(https?://[^\s]+)', body):
                                links.append(match)
                        print(f'Found {len(links)} links in email {msg_id} of account {email_login}')
                        if len(links) > 0:
                            link_end = links[1][:-8]
                        imap.close()
                        imap.logout()
                    except imaplib.IMAP4.error as e:
                        if str(e) == 'b\'Invalid login or password\'':
                            print(f"Login failed for email account {jopech.strip()}")
                            bad.write(f'\n{email_login}:{email_pass}')
                        else:
                            print(f"An error occurred while processing email account {jopech.strip()}: {str(e)}")
                            bad.write(f'\n{email_login}:{email_pass}')
                        continue
                    except Exception as e:
                        print(f"An error occurred while processing email account {jopech.strip()}: {str(e)}")
                        bad.write(f'\n{email_login}:{email_pass}')
                        continue
                    try:
                        r = sess.get(link_end, headers=headers_confirm)
                        print(link_end)
                    except Exception as ex:
                        print(ex)
                        continue
                    if r.status_code == 302:
                        print(f'SUCCESS registred:{email_login}\n')
                        good.write(f'\n{email_login}:{email_pass}:{link_end}')
                        file_with_ref_code.write(f'\n{email_login}:{email_pass}:{ref_code["social_id"]}')
                    else:
                        print(f'UNSUCCESS registred:{email_login}\n')
                        time.sleep(1)
                        bad.write(f'\n{email_login}:{email_pass}')
                        continue    


if __name__ == '__main__':
    main()
