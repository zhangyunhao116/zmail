<div align=center>
<img src="https://raw.githubusercontent.com/ZYunH/zmail/master/zmail_logo.png"/>
</div>

[![PyPI](https://img.shields.io/pypi/v/yagmail.svg?style=flat-square)]()
[![platform](https://img.shields.io/badge/python-3.5-green.svg)]()
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)]()

[中文介绍请戳这里](https://github.com/ZYunH/zmail/blob/master/README-cn.md)

## Introduction

Zmail makes it easier to send and retrieve emails in python3. There's no need to manually add—server address, port, suitable protocol, and so on—Zmail will do it for you. Besides, use a python dict as a mail is also more intuitive.

> WARNING: This project is no longer maintained. The original goal of `zmail` was to provide a simple way to send e-mail in python3. 
Unfortunately I am no longer have the time to continue to maintain this project. Feel free to fork if you want some features.


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
server = zmail.server('yourmail@example.com', 'yourpassword')

# Send mail
server.send_mail('yourfriend@example.com',{'subject':'Hello!','content_text':'By zmail.'})
# Or to a list of friends.
server.send_mail(['friend1@example.com','friend2@example.com'],{'subject':'Hello!','content_text':'By zmail.'})

# Retrieve mail
latest_mail = server.get_latest()
zmail.show(latest_mail)

```



## Demos

see [zmail_demos](https://github.com/ZYunH/zmail_demos)



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

If SMTP and POP are working correctly, the function will return True, else return Fasle.

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

You can define sender's name by add `'from':'Boss <mymail@foo.com>'`  in your mail.

- ##### To a list of recipients

```python
server.send_mail(['yourfriend@example.com','12345@example.com'], mail)
```

you can also name them (use tuple, first is its name, next is its address).

```
server.send_mail([('Boss','yourfriend@example.com'),'12345@example.com'], mail)
```

- ##### Send HTML content

```python
mail = {
    'subject': 'Success!',  # Anything you want.
    'content_html': ['HTML CONTENT'], 
    'attachments': '/Users/zyh/Documents/example.zip',  # Absolute path will be better.
}
server.send_mail('yourfriend@example.com',mail)
```

or

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

- ##### Use carbon copy

```
server.send_mail(['foo@163.com','foo@126.com'],mail,cc=['bar@163.com'])
```

Again, you can also name them (use tuple, first is its name, next is its address).

```
server.send_mail(['foo@163.com','foo@126.com'],mail,cc=[('Boss','bar@163.com'),'bar@126.com'])
```

- ##### Customize your server

If zmail is not working correctly, you can customize your server config yourself.

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

In this example, if 'GitHub' in mail's subject, it will be matched, as in '[GitHub] Your password has changed'

Sender is the same way.

You can also assign the range of mails.

```
mail = server.get_mails(subject='GitHub',start_time='2018-1-1',sender='github',start_index=1,end_index=10)
```

- ##### Get mailbox info.

```
mailbox_info = server.stat()
```

The result is a tuple of 2 integers: `(message count, mailbox size)`.

### Parse your mail

In zmail, each mail will be mapped to a python dictionary, you can access your mail by

```
subject = mail['subject']
```

Show your mail's base information, use **zmail.show()**

```python
import zmail
server = zmail.server('yourmail@example.com’, 'yourpassword')
mail = server.get_latest()
zmail.show(mail)
```

See all contents in mail.

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

If set any arguments which starts with `pop` or `smtp`, it will replace inner auto-generate argument (the arguments depend on the `username` or `config` you provide).

***config*** Shortcut for use enterprise mail,if specified, enterprise mail configs will replace all inner auto-generate configs.

***timeout*** can either be a float or int number of seconds to wait for.

***debug*** If is True, server will open debug model and display debug information.

***log*** The log can be None or instance of logging.logger,if is None, the zmail default logger is used, you can access it by logging.getLogger('zmail')

***auto_add_to*** If set to True, when the key 'to' (case-insensitive) not in mail(For send), the default 'to' will automatically added to mail.

***auto_add_from***  If set to True, when the key ' 'from' (case-insensitive) not in mail(For send), the default 'from' will automatically added to mail.

 

### MailServer.send_mail(recipients, mail, timeout=None,auto_add_from=False, auto_add_to=False)

Return True if success.

***recipients*** can either be str or a list of str.

***mail*** can either be dict or CaseInsensitiveDict(**Mail**).mail structure see below.

***timeout*** if is not None, it will replace server's timeout.

***auto_add_from*** if is not None, it will replace server's auto_add_from.

***auto_add_to*** if is not None, it will replace server's auto_add_to.

 

### MailServer.stat() 

Get mailbox status. The result is a tuple of 2 integers: (message count, mailbox size).

 

### MailServer.get_mail(which)

Return **Mail**

***which*** is a int number that represent mail's position in mailbox.The which must between 1 and message count(return from MailServer.stat())

Also set mail's seen flag.

 

### MailServer.get_mails(subject=None,start_time=None,end_time=None,sender=None,start_index=None,end_index=None)

Return a list of **Mail** 

***subject*** can either be None or str, if is not None, the subject of every mail must contains ***subject***

***start_time*** can either be None or string or datetime object, if is string,the format is "YYYY-MM-DD HH:MM:SS"(e.g. "2018-1-1 10:10:20").If is not None,the date of every mail must greater than start_time.

***end_time*** is similar to start_time.If is not None,the date of every mail must smaller than end_time.

***sender*** can either be None or str, if is not None, the from(header) of every mail must contains ***sender***.

***start_index*** can either be None or int, if is None or smaller than 1, it is set to 1. if greater than message_count(From MailServer.stat()), it is set to message_count.

***end_index*** similar to start_index.The selected range limited from **start_index** to **end_index**.

lso set mail's seen flag.

 

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

  Save mail's attachments to target_path.If not specified, target_path is current directory.If overwrite is True,the write process will overwrite exists file if possible.

- #### zmail.save(mail,name=None,target_path=None,overwrite=False)

  Save mail.

- #### zmail.read(file_path,SEP=b'\r\n')

  Read mail.



## Mail Structures

 

### Mail (Used for send)

Can either be dict or CaseInsensitiveDict(Usually from get_mail or get_mails)

***subject*** The subject of mail.

***from*** The 'from' header, represent the mail's source.

***to*** **(Not used)**.You can use tuple (name,address) to define the name of recipient.(Used for To and Cc)

***content_text*** The text content.Can either be str or a list of str.

***content_html*** The html content.Can either be str or a list of str.

***attachments*** Include all attachments.It can either be str or a list of str or a list of tuple.(e.g. '/User/apple/1.txt' or ['/User/apple/1.txt','2.txt'] or [('1.txt',b'...'),('2.txt',b'...')] )

***headers*** If you want to add extra headers,you can specified on it.Must be dict.

 

### Mail(From get_mail or get_mails)

***subject*** The subject of mail.

***from*** The 'from' header, represent the mail's source.

***to*** The 'to' header, represent the mail's destination.

***content_text*** A list of text content.

***content_html*** A list of html content.

***attachments*** Include all attachments.(e.g. ['1.txt',b'...'])

***raw_headers*** Include all  raw header pairs.

***headers*** Include all parsed headers.(CaseInsensitiveDict)

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

| Name                    | Usage                                          |
| ----------------------- | ---------------------------------------------- |
| Tencent enterprise mail | zmail.server('username','psw',config='qq')     |
| Ali enterprise mail     | zmail.server('username','psw',config='ali')    |
| Netease enterprise mail | zmail.server('username','psw',config='163')    |
| Google enterprise mail  | zmail.server('username','psw',config='google') |



## Q&A

- Can not send or retrieve
  - Ensure your smtp&pop3 function is open
  - Use smtp or pop protocol settings provided by your mail server to config zmail.server, like following
  - SMTP：server = zmail.server('user','psw',smtp_host = 'xxx',smtp_port = 'yyyyy',smtp_ssl=True)
  - POP3：server = zmail.server('user','psw',pop_host = 'xxx',pop_port = 'yyyyy',pop_ssl=True)
