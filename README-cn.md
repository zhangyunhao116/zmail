# zmail

[![PyPI](https://img.shields.io/pypi/v/yagmail.svg?style=flat-square)]()
[![platform](https://img.shields.io/badge/python-3.5-green.svg)]()
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)]()

[English Introduction click here](https://github.com/ZYunH/zmail/blob/master/README.md)

## 介绍

Zmail 允许你发送和接受邮件尽可能的简单。你不需要去检查你的服务器地址、端口以及自己构造MIME对象，使用Zmail，你只需要关注你的邮件内容即可。

## 安装

Zmail仅支持python3，不需要任何其他外部依赖. **不支持python2**.

### 选项一：通过pip安装（推荐）

```
$ pip3 install zmail
```

或者

```
$ pip install zmail
```

这样做也意味着此pip版本是支持python3的。

### 选项二： 从GitHub下载安装

你可以下载Zmail的master分支，将其解压，切换到相应目录，然后

```
$ python3 setup.py install
```

## 特性

- 自动寻找服务器地址以及端口
- 自动使用可靠的链接协议
- 自动将一个python字典映射成MIME对象（带有附件的）
- 自动添加头文件以及localhostname来避免服务器拒收你的邮件
- 轻松自定义你的头文件
- 支持使用HTML作为邮件内容
- 仅需python>=3.5，你可以将其嵌入你的项目而无需其他的依赖

## 使用须知

使用它之前，请保证

- 使用Python3
- 确保打开了邮箱的POP3和SMTP功能 (对于 **@163.com** 和 **@gmail.com** 你需要设置你的应用专用密码)

然后，剩下你需要做的就是import zmail即可

## 使用示例

### 测试SMTP和POP功能是否正常

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

以上功能正常时，返回True，否则返回False，logger会打印相应错误信息。

### 发送你的邮件

```python
import zmail
mail = {
    'subject': 'Success!',  # Anything you want.
    'content': 'This message from zmail!',  # Anything you want.
    'attachments': '/Users/zyh/Documents/example.zip',  # Absolute path will be better.
}

server = zmail.server('yourmail@example.com’, 'yourpassword')

server.send_mail('yourfriend@example.com', mail)
```

- ##### 给一个列表的收件人发件

```
server.send_mail(['yourfriend@example.com','12345@example.com'], mail)
```

- ##### **发送HTML作为邮件内容**

```python
mail = {
    'subject': 'Success!',  # Anything you want.
    'content_html': zmail.get_html('/Users/example.html'), # Absolute path will be better.
    'attachments': '/Users/zyh/Documents/example.zip',  # Absolute path will be better.
}
server.send_mail('yourfriend@example.com',mail)
```

或者

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



### 取回你的邮件

- ##### 取得最新的邮件

```python
import zmail
server = zmail.server('yourmail@example.com', 'yourpassword')
mail = server.get_latest()
```

- ##### 依据id取回邮件

```python
mail = server.get_mail(2)
```

- ##### 依据 (subject,after,before,sender)取回一个列表的邮件

```
mail = server.get_mails(subject='GitHub',after='2018-1-1',sender='github')
```

示例中， 如果 'GitHub' 在邮件的主题中，这封邮件将会被匹配, 例如'  [GitHub] Your password has changed'

sender亦是如此

- ##### 得到所有邮件的头文件信息.一个由字典组成的列表,每个字典包含了所有能够提取的头文件.

```
mail_info = server.get_info()
```

- ##### 得到邮箱的信息

```
mailbox_info = server.stat()
```

结果为包含两个整型的元组: `(邮件的数量, 邮箱的大小)`.

### 解析你的邮件

在zmail中，接收到的邮件被映射为一个字典，你可以通过访问python字典的形式来访问你的邮件，例如

```
subject = mail['subject']
```

展示你的邮件，使用 **zmail.show()**

```
import zmail
server = zmail.server('yourmail@example.com‘, 'yourpassword')
mail = server.get_latest()
zmail.show(mail)
```

输出 :

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

#### **邮件的结构**

- content-type: 邮件内容的类型
- subject: 邮件主题
- to：收件人
- from：寄件人
- date: 年-月-日 时间 时区
- boundary: 如果邮件为multiple parts，你可以得到其分界线
- content: 邮件的文本内容（仅在text/plain时可以被解析）
- content_html:邮件的网页内容（仅在text/html时可以被解析）
- raw: 邮件的原始数据
- attachments: None 或者 [['附件名称;编码方式','附件的二进制内容']...]
- id: 在邮箱中的id

#### **获得附件**

```python
import zmail
server = zmail.server('yourmail@example.com‘, 'yourpassword')
mail = server.get_latest()
zmail.get_attachment(mail)
```

你可以重命名你的附件，使用

```
zmail.get_attachment(mail,'example.zip')
```

#### 保存邮件

```
import zmail
server = zmail.server('yourmail@example.com‘, 'yourpassword')
mail = server.get_latest()
zmail.save_eml(mail)
```

你可以重命名或者指定路径，使用

```
zmail.save_eml(mail,name='hello.eml',path='/usr/home')
```

#### 读取磁盘上的邮件

```
import zmail
mail_as_raw = zmail.read_eml('/usr/home/hello.eml') # Abspath will be better
```

你可以将读取到的原始邮件解析成zmail格式的邮件

```
mail = zmail.decode(mail_as_raw)
```



## 支持的邮件服务商

列表中的邮件服务商已经被测试可正常使用

**如果你的邮箱不在此列，请不要担心，目前尚未发现不支持的邮箱.如果你发现任何问题，请在GitHub上告知于我**  

| 服务商地址      | 发送邮件 | 取回邮件 | 备注            |
| ---------- | ---- | ---- | ------------- |
| @163.com   | ✓    | ✓    | 需要应用专用密码      |
| @qq.com    | ✓    | ✓    | POP3 需要应用专用密码 |
| @126.com   | ✓    | ✓    |               |
| @yeah.net  | ✓    | ✓    |               |
| @gmail.com | ✓    | ✓    | 需要应用专用密码      |
| @sina.com  | ✓    | ✓    |               |
| @outlook   | ✓    | ✓    |               |

## 问题索引

- ##### 发送或者接受失败

  - 检查是否开启了SMTP和POP3功能
  - 根据服务器SMTP或者POP3地址的端口填写server（没有填写的将会为默认值）
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