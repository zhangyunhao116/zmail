# zmail

[![PyPI](https://img.shields.io/pypi/v/yagmail.svg?style=flat-square)]()
[![platform](https://img.shields.io/badge/python-3.5-green.svg)]()
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)]()

[中文介绍请戳这里](https://github.com/ZYunH/zmail/blob/master/README-cn.md)

## Introduction

Zmail allows you to send and get emails as possible as it can be in python.There is no need to check server address or make your own MIME object.With zmail, you only need to care about your mail content.

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

If that means your pip is also working for python3.

### Option 2:Download from Github

You can download the master branch of zmail,unzip it ,and do

```
$ python3 setup.py install
```

## Features

- Automatic looks for server address and it's port.
- Automatic use suitable protocol to login.
- Automatic converts a python dictionary to MIME object(with attachments).
- Automatic add mail header and local name to avoid server reject your mail.
- Easily custom your mail header.
- Support HTML as mail content.
- Only require python >= 3.5 , you can embed it in your project without other module required.

## Usage

Before using it, please ensure:

- Using python3
- Open SMTP/POP3 function in your mail (For **@163.com** and **@gmail.com** you need to set your app private password)

Then, all you need to do is just import zmail.

## Examples

### Verify SMTP and POP function working correctly

```python
import zmail
server = zmail.server('yourmail@example.com’, 'yourpassword')

if server.smtp_able():
    pass
    # SMTP function.
if server.pop_able():
    pass
    # POP function.
            
```

If SMTP and POP are working correctly,the function will return True,else return Fasle.

### Send your mail

```python
import zmail
mail = {
    'subject': 'Success!',  # Anything you want.
    'content': 'This message from zmail!',  # Anything you want.
    'attachments': '/Users/zyh/Documents/example.zip',  # Absolute path will be better.
}

server = zmail.server('yourmail@example.com‘, 'yourpassword')

server.send_mail('yourfriend@example.com', mail)
```

- ##### To a list of recipients

```python
server.send_mail(['yourfriend@example.com','12345@example.com'], mail)
```

- ##### **Send HTML content**

```python
mail = {
    'subject': 'Success!',  # Anything you want.
    'content_html': zmail.get_html('/Users/example.html'), # Absolute path will be better.
    'attachments': '/Users/zyh/Documents/example.zip',  # Absolute path will be better.
}
server.send_mail('yourfriend@example.com',mail)
```

OR

```python
with open('/Users/example.html','r') as f:
    content_html = f.read()
mail = {
    'subject': 'Success!',  # Anything you want.
    'content_html': content_html, 
    'attachments': '/Users/zyh/Documents/example.zip',  # Absolute path will be better.
}
server.send_mail('yourfriend@example.com',mail)
```



### Retrieve your mail

- ##### Get the latest mail.

```python
import zmail
server = zmail.server('yourmail@example.com‘, 'yourpassword')
mail = server.get_latest()
```

- ##### Retrieve mail by its id.

```python
mail = server.get_mail(2)
```

- ##### Get a list of mails by its (subject,after,before,sender)

```
mail = server.get_mails(subject='GitHub',after='2018-1-1',sender='github')
```

In the example, if 'GitHub' is in mail's subject, it will be matched, such as '  [GitHub] Your password has changed'

sender is the same way.

- ##### Get all mails' info, include each mail's header.A list of dictionary, each dictionary include all headers can be extracted.

```
mail_info = server.get_info()
```

- ##### Get mailbox info. 

```
mailbox_info = server.stat()
```

The result is a tuple of 2 integers: `(message count, mailbox size)`.

### Parse your mail

In zmail, all mails will be mapped to a python dictionary, you can access your mail by

```
subject = mail['subject']
```

Show you mail, use **zmail.show()**

```python
import zmail
server = zmail.server('yourmail@example.com’, 'yourpassword')
mail = server.get_latest()
zmail.show(mail)
```

Output, example :

```
content-type multipart/mixed
subject Success!
to zmail_user
from zmail<zmail@126.com>
date 2018-2-3 01:42:29 +0800
boundary ===============9196441298519098157==
content ['This message from zmail!']
content_html ['<HTML EXAMPLE>']
raw [[b'Content-Type: text/plain; charset="utf-8"', b'MIME-Version: 1.0', b'Content-Transfer-Encoding: base64', b'', b'VGhpcyBtZXNzYWdlIGZyb20gem1haWwh', b'']]
attachments None
id 5
```

#### **Mail structure**

- content-type: Mail content type
- subject: Mail subject
- to
- from
- date: year-month-day time TimeZone
- boundary: If mail is multiple parts, you can get the boundary
- content: Mail content as text/plain
- content_html: Mail content as text/html
- raw: raw mail as bytes
- attachments: None or [['attachment-name;Encoding','ATTACHMENT-DATA']...]
- id: Mailbox id

#### **Get attachment**

```python
import zmail
server = zmail.server('yourmail@example.com‘, 'yourpassword')
mail = server.get_latest()
zmail.get_attachment(mail)
```

you can rename your attachment file, by

```
zmail.get_attachment(mail,'example.zip')
```

#### Save email

```
import zmail
server = zmail.server('yourmail@example.com‘, 'yourpassword')
mail = server.get_latest()
zmail.save_eml(mail)
```

you can rename your mail or define the path,  by

```
zmail.save_eml(mail,name='hello.eml',path='/usr/home')
```

#### Read mail in disk

```
import zmail
mail_as_raw = zmail.read_eml('/usr/home/hello.eml') # Abspath will be better
```

you can convert the raw mail to zmail format

```
mail = zmail.decode(mail_as_raw)
```



## Supported mail server

The mail server in this list has been tested and approved.

**If your mail server not in it, don't worry, zmail will handle it automatically.If there any problems in use, pls tell me in the Github.**  



| Server address | Send mail | Retrieve mail | Remarks                        |
| -------------- | --------- | ------------- | ------------------------------ |
| @163.com       | ✓         | ✓             | Need app private password      |
| @qq.com        | ✓         | ✓             | POP3 need app private password |
| @126.com       | ✓         | ✓             |                                |
| @yeah.net      | ✓         | ✓             |                                |
| @gmail.com     | ✓         | ✓             | Need app private password      |
| @sina.com      | ✓         | ✓             |                                |
| @outlook       | ✓         | ✓             |                                |

## Q&A

- Can not send or retrieve
  - ensure your smtp&pop3 function is open
  - according to smtp or pop protocol provided by your mail server to define zmail.server 
  - SMTP：server = zmail.server('user','psw',smtp_host = 'xxx',smtp_port = 'yyyyy',smtp_ssl=True)
  - POP3：server = zmail.server('user','psw',pop_host = 'xxx',pop_port = 'yyyyy',pop_ssl=True)



## API

server = zmail.server('user@example','password')

#### SMTP

- server.smtp_able()

- server.send_mail([recipient,], mail)

#### POP3

- server.pop_able()

- server.get_mail(which)
- server.get_mails(subject, sender, after, before)
- server.get_latest()
- server.get_info()
- server.stat()

#### Parse mail

- server.get_attachment(mail)

### Mail(For send)

- subject
- content
- content_html
- from
- to

#### Other

- zmail.show()