<div align=center>
<img src="https://raw.githubusercontent.com/ZYunH/zmail/master/zmail_logo.png"/>
</div>

[![PyPI](https://img.shields.io/pypi/v/yagmail.svg?style=flat-square)]()
[![platform](https://img.shields.io/badge/python-3.5-green.svg)]()
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)]()

[中文介绍请戳这里(中文新版本介绍尚未更新完成)](https://github.com/ZYunH/zmail/blob/master/README-cn.md)

## Introduction

Zmail allows you to send and get emails as possible as it can be in python.There is no need to check server address or make your own MIME object.With zmail, you only need to care about your mail content.

## Installation 

Zmail only running in python3 without third-party modules required. **Do not support python2**.

```
$ pip3 install zmail
```



## Features

- Automatic looks for server address and it's port.
- Automatic uses suitable protocol to login.
- Automatic converts a python dictionary to MIME object(with attachments).
- Automatic add mail header and local name to avoid server reject your mail.
- Easily custom your mail header.
- Support HTML as mail content.
- Only require python >= 3.5 , you can embed it in your project without other module required.



## Usage

Before using it, please ensure:

- Using python3
- Open SMTP/POP3 functions in your mail (For **@163.com** and **@gmail.com** you need to set your app private password)

Then, all you need to do is just import zmail.



## QuickStart

```python
import zmail
server = zmail.server('yourmail@example.com’, 'yourpassword')

# Send mail
server.send_mail('yourfriend@example.com',{'subject':'Hello!','content_text':'By zmail.'})
# Or to a list of friends.
server.send_mail(['friend1@example.com','friend2@example.com'],{'subject':'Hello!','content_text':'By zmail.'})

# Retrieve mail
latest_mail = server.get_latest()
zmail.show(latest_mail)

```



## Examples



### Send your mail

```python
import zmail
mail = {
    'subject': 'Success!',  # Anything you want.
    'content_text': 'This message from zmail!',  # Anything you want.
    'attachments': ['/Users/zyh/Documents/example.zip','/root/1.jpg'],  # Absolute path will be better.
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
    'content-html': ['HTML CONTENT'], # Absolute path will be better.
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
    'content-html': content_html, 
    'attachments': '/Users/zyh/Documents/example.zip',  # Absolute path will be better.
}
server.send_mail('yourfriend@example.com',mail)
```

- ##### Customize your server

If zmail not working correctly, you can customize your server config by yourself.

```
server = zmail.server('username','password',smtp_host='smtp.163.com',smtp_port=994,smtp_ssl=True,pop_host='pop.163.com',pop_port=995,pop_tls=True)
```

### Get your mails

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
mail = server.get_mails(subject='GitHub',start_time='2018-1-1',sender='github')
```

In the example, if 'GitHub' is in mail's subject, it will be matched, such as '  [GitHub] Your password has changed'

sender is the same way.

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

OR

```python
import zmail
server = zmail.server('yourmail@example.com’, 'yourpassword')
mail = server.get_latest()
for k,v in mail.items():
	print(k,v)
```



## API Reference

### zmail.server(username,password,smtp_host,smtp_port,smtp_ssl,smtp_tls,pop_host,pop_port,pop_ssl,pop_tls,config,timeout=60, debug=False, log=None,auto_add_from=True, auto_add_to=True)

Return **MailServer** instance, it implements all SMTP and POP functions.

If define any parameters start with `pop` or `smtp`, it wiil replace inner auto-generate config(The config depends on the `username` or `config` you provided).

***config*** Shortcut for use enterprise mail,if specified, it will replace all inner auto-generate configs.

***timeout*** can either be a float or int number of seconds to wait for.

***debug*** If is True, server will open debug model and display debug information.

***log*** The log can be None or instance of logging.logger,if is None, the zmail default logeer is used, you can access it by logging.getLogger('zmail')

***auto_add_to*** If set to True, when the key 'to' (case-insensitive) not in mail-as-dict, the default 'to' will automatically added to mail.

***auto_add_from***  If set to True, when the key ' 'from' (case-insensitive) not in mail-as-dict, the default 'from' will automatically added to mail.

 

### MailServer.send_mail(recipients, mail, timeout=None,auto_add_from=False, auto_add_to=False)

Return True if success.

***recipients*** can either be str or a list of str.

***mail*** can either be dict or CaseInsensitiveDict(**Mail**).see below for more info.

***timeout*** if is not None, it will replace server's timeout.

***auto_add_from*** if is not None, it will replace server's auto_add_from.

***auto_add_to*** if is not None, it will replace server's auto_add_to.

 

### MailServer.stat() 

Get mailbox status. The result is a tuple of 2 integers: (message count, mailbox size).

 

### MailServer.get_mail(which)

Return **Mail**

***which*** is a int number that represent mail's position in maibox.The which must between 1 and message count(return from MailServer.stat())

also set mail's seen flag.

 

### MailServer.get_mails(subject=None,start_time=None,end_time=None,sender=None,start_index=None,end_index=None)

Return a list of **Mail** 

***subject*** can either be None or str, if is not None, the subject of every mail must contains ***subject***

***start_time*** can either be None or string or datetime object, if is string,the format is "YYYY-MM-DD HH:MM:SS"(e.g. "2018-1-1 10:10:20").If is not None,the date of every mail must after start_time.

***end_time*** is same as start_time.If is not None,the date of every mail must before end_time.

***sender*** can either be None or str, if is not None, the from(header) of every mail must contains ***sender***.

***start_index*** can either be None or int, if is None or smaller than 1, it is set to 1. if greater than message_count(From MailServer.stat()), it is set to message_count.

***end_index*** same as start_time.The selected range limited from **start_index** to **end_index**.

also set mail's seen flag.

 

### MailServer.get_latest()

Return **Mail**

Return latest mail.Equal to MailServer.get_mail(message_count).The message count is return from MailServer.stat()

also set mail's seen flag.

 

### MailServer.~~get_info()~~

Return a list of raw_headers

Use MailServer.get_headers() instead.

Removed in version 0.2.0

 

### MailServer.get_headers(start_index=None,end_index=None)

Return a list of headers.(A list of CaseInsensitiveDict)

The range of headers is limited from start_index to end_index.same as that of MailServer.get_mails()

New in version 0.2.0

 

### MailServer.delete(which)

***which*** flag message number which for deletion. 

New in version 0.2.0

 

### MailServer.smtp_able()

Return True if SMTP working correctly else False.

 

### MailServer.pop_able()

Return True if POP working correctly else False.

 

### Utils

- #### zmail.show(mails)

  You can use this function to show one or list of mail.

- #### zmail.save_attachment(mail,target_path=None,overwrite=False)

  Save mail attachments to target_path.If not specified, target_path is current directory.If overwrite is True,the write process will overwrite exists file if possible.

- #### zmail.save(mail,name=None,target_path=None,overwrite=False)

  Save mail.

- #### zmail.read(file_path,SEP=b'\r\n')

  Read mail.



## Mail Stuctures

 

### Mail (Used for send)

Can either be dict or CaseInsensitiveDict(Usually from get_mail or get_mails)

***subject*** The subject of mail.

***from*** The 'from' header, represent the source or name.

***to*** The 'to' header, represent the destination or name.

***content_text*** The text content.Can either be str or list.

***content_text*** The html content.Can either be str or list.

***attachments*** Include all attachments.It can either be str or a list of str or a list of tuple.Like '/User/apple/1.txt' or ['/User/apple/1.txt','2.txt'] or [('1.txt',b'...'),('2.txt',b'...')]

***headers*** If you want to add extra headers,you can specified on it.Must be dict.

 

### Mail(From get_mail or get_mails)

***subject*** The subject of mail.

***from*** The 'from' header, represent the source or name.

***to*** The 'to' header, represent the destination or name.

***content_text*** A list of text content.

***content_text*** A list of html content.

***attachments*** Include all attachments.Like['1.txt',b'...']

***headers*** If you want to add extra headers,you can specified on it.Must be dict.

***raw_headers*** Include all  raw header pairs.

***headers*** Include all parsed headers.

***charsets*** Include all charsets.

***date*** Mail date.

***id*** Mail id.Used to locate mail position in mail-box.

***raw*** raw mail.As a list of bytes.

​    

## Supported mail server

The mail server in this list has been tested and approved.

**If your mail server not in it, don't worry, zmail will handle it automatically.If any problems in use, please tell me in the Github.**  

| Server address | Send mail | Retrieve mail | Remarks                        |
| -------------- | --------- | ------------- | ------------------------------ |
| @163.com       | ✓         | ✓             | Need app private password      |
| @qq.com        | ✓         | ✓             | POP3 need app private password |
| @126.com       | ✓         | ✓             |                                |
| @yeah.net      | ✓         | ✓             |                                |
| @gmail.com     | ✓         | ✓             | Need app private password      |
| @sina.com      | ✓         | ✓             |                                |
| @outlook       | ✓         | ✓             | Need app private password      |
| @hotmail       | ✓         | ✓             | Require extra setup            |



## Supported enterprise mail server

| Name                    | Usage                                       |
| ----------------------- | ------------------------------------------- |
| Tencent enterprise mail | zmail.server('username','psw',config='qq')  |
| Ali enterprise mail     | zmail.server('username','psw',config='ali') |
| Netease enterprise mail | zmail.server('username','psw',config='163') |



## Q&A

- Can not send or retrieve
  - ensure your smtp&pop3 function is open
  - according to smtp or pop protocol provided by your mail server to define zmail.server 
  - SMTP：server = zmail.server('user','psw',smtp_host = 'xxx',smtp_port = 'yyyyy',smtp_ssl=True)
  - POP3：server = zmail.server('user','psw',pop_host = 'xxx',pop_port = 'yyyyy',pop_ssl=True)
