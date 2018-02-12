# zmail

[![PyPI](https://img.shields.io/pypi/v/yagmail.svg?style=flat-square)]()
[![platform](https://img.shields.io/badge/python-3.5-green.svg)]()
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)]()

Zmail allows you to send and get emails as possible as it can be in python.There is no need to check server address or make your own MIME string.With zmail, you only need to care about your mail content.

## Installation 

Zmail only running in python3 without third-party modules required. **Do not support python2**.

### Option 1:Install via pip（Better）

```
$ pip3 install zmail
```

or

```
$ pip install zmail
```

If that,means your pip is also work for python3.

### Option 2:Download from Github

You can download the master branch of zmail,unzip it ,and do

```
$ python3 setup.py install
```

## Features

- Automatic look for server address and it's port.
- Automatic convert a python dict to MIME object(with attachments).
- Automatic add mail header and local name to avoid server reject your mail.
- Easily custom your mail header.
- Only require python >= 3.5 ,you can embed it in your project without other module required.

## Usage

Before using it, please ensure:

- Using python3
- Open SMTP/POP3 function in your mail (For **@163.com** and **@gmail.com** you need to set your app private password)

Then,all you need to do is just import zmail.

## Examples

- ### Send your mail

```python
import zmail
mail_content = {
    'subject': 'Success!',  # Anything you want.
    'content': 'This message from zmail!',  # Anything you want.
    'attachments': '/Users/zyh/Documents/example.zip',  # Absolute path will be better.
}

mail = zmail.encode_mail(mail_content)

server = zmail.server('yourmail@example.com, 'yourpassword')

server.send_mail('yourfriend@example.com', mail)
```

## Supported mail server

The mail server in this list have been tested and approved.

**If your mail server not in it , don't worry , zmail will handle it automatically.If there any problems in use, pls tell me in the github.**  



| Server address | Send mail | Pull mail | Remarks                   |
| -------------- | --------- | --------- | ------------------------- |
| @163.com       | ✓         |           | Need app private password |
| @qq.com        | ✓         |           |                           |
| @126.com       | ✓         |           |                           |
| @yeah.net      | ✓         |           |                           |
| @gmail.com     | ✓         |           | Need app private password |
| @sina.com      | ✓         |           |                           |
|                |           |           |                           |



## To do

- [ ] Make get function using IMAP or POP3.