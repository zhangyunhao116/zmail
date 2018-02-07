# Zmail 

## 1.  Send mail API

### 1.1 zmail.ZMAIL

A standard mail content for zmail.it's a dict :

```python
ZMAIL = {
    'subject': 'From zmail server',  # Anything you want.
    'content': 'This message from zmail!',  # Anything you want.
    'attachments': '',  # Absolute path will be better.
}
```

you can make your mail use this standard mail ,but rewrite it's content and subject use 

```
mymail = zmail.ZMAIL
myail['subject'] = 'Hello zmail'
mymail['content'] = 'Hava a nice day.'
```

if you want to add some attachments, do 

```
mymail['attachments'] = '/Users/zyh/Documents/GitHub/zmail/setup.py'
```

or

```
mymail['attachments'] = ('/Users/zyh/Documents/GitHub/zmail/setup.py','/Users/zyh/Documents/GitHub/zmail/ok.mp3'
```

if the python program and attachment in a same directory, you can do as follow

```
mymail['attachments']= 'example.zip'
```

it is not recommended , but a shortcut.

### 1.2 zmail.encode_mail(mail_content)

Return a MIME multiple part object by convert a mail content dictionary, see python standard libary MIMEMultipart. you can also change your mail content using email.mime library after that.

**mail_content** is a dictionary includes 

### 1.3 zmail.server(user,password)

Return a ZmailServer object.see ZmailServer as follows.This class allows you to use mail server easily,user and password parameters used to login your server mail for send or get mails.



### class zmail.MailServer.ZmailServer(user,password)

This class represents a mail server.The user and password can be used to login mail server.

#### send_mail([recipients,], mail)

Send your mail using SMTP protocol.

**recipients** can be a string or a list or a tuple,this parameter define where your mail would be sent.

**mail** must be a MIME multiple part object,you can easily get it by using zmail.encode_mail(mail_content).





# TBD:



1.get_mail([which,])

get mail from server,from&subject is a filter for choose mail.

2.get_mails([which,],)

3.get_info(max_num)

get mail info from server

return ((index,subject,from,size,content?)......)

# MAILMESSAGE

1.decode(mail)

return dict

{

subject:

from:

content: text/plain

contents: 

attachements: ((attachment_name,attachment_content),)

}



