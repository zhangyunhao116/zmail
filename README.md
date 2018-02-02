# zmail

[![PyPI](https://img.shields.io/pypi/v/yagmail.svg?style=flat-square)]()
[![platform](https://img.shields.io/badge/python-3.5-green.svg)]()
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)]()

Zmail allows you to send and get email as possible as it can be.There is no need to check server address or make your own MIME string.With zmail, you only need to care about your mail's content.

## Installation 

```
$ pip3 install zmail
```

## Examples

- ### Send your mail

```
import zmail
mail_content = {
    'subject': 'Success!',  # Anything you want.
    'from': '',  # Better be '' as default, zmail will handle it automatically.
    'to': 'zmail_user',  # Anything you want.
    'content': 'This message from zmail!',  # Anything you want.
    'attachments': '/Users/zyh/Documents/GitHub/zmail/test/t.zip',  # Absolute path will be better.
}

mail = zmail.encode_mail(mail_content)

server = zmail.server(user='yourmail@example.com', password='yourpassword')

server.send_mail('yourfriend@example.com', mail)
```

## Supported mail server

The mail server you are using must be in this list, or you provide the server address and it's port.

| Server address | Send | Get  |
| -------------- | ---- | ---- |
| @163.com       | ✓    |      |
| @qq.com        | ✓    |      |

## To do

- [ ] Make get function using IMAP or POP3.