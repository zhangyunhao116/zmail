<div align=center>
<img src="https://raw.githubusercontent.com/ZYunH/zmail/master/zmail_logo.png"/>
</div>

[![PyPI](https://img.shields.io/pypi/v/yagmail.svg?style=flat-square)]()
[![platform](https://img.shields.io/badge/python-3.5-green.svg)]()
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)]()

[English Introduction click here](https://github.com/ZYunH/zmail/blob/master/README.md)

## 介绍

Zmail 使得在python3中发送和接受邮件变得更简单。你不需要手动添加服务器地址、端口以及适合的协议，zmail会帮你完成。此外，使用一个python字典来代表邮件内容也更符合直觉。

## 安装

Zmail仅支持python3，不需要任何外部依赖. **不支持python2**.

```
$ pip3 install zmail
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



## 快速入门

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



## 应用示例

请看 [zmail_demos](https://github.com/ZYunH/zmail_demos)



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
    'content_text': 'This message from zmail!',  # Anything you want.
    'attachments': ['/Users/zyh/Documents/example.zip','/root/1.jpg'],  # Absolute path will be better.
}

server = zmail.server('yourmail@example.com’, 'yourpassword')

server.send_mail('yourfriend@example.com', mail)
```

你也可以自定义发送者的名字，具体的做法是在在mail中加入`'from':'Boss <mymail@foo.com>'`

- ##### 给一个列表的收件人发件

```
server.send_mail(['yourfriend@example.com','12345@example.com'], mail)
```

你还可以为收件人定义名字(使用元组，第一个为其命名，第二个为其地址)

```
server.send_mail([('Boss','yourfriend@example.com'),'12345@example.com'], mail)
```

- ##### 发送HTML作为邮件内容

```python
mail = {
    'subject': 'Success!',  # Anything you want.
    'content_html': ['HTML CONTENT'], 
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

- ##### 使用抄送

```
server.send_mail(['foo@163.com','foo@126.com'],mail,cc=['bar@163.com'])
```

同样，你也可以为他们命名(使用元组，第一个为其命名，第二个为其地址)

```
server.send_mail(['foo@163.com','foo@126.com'],mail,cc=[('Boss','bar@163.com'),'bar@126.com'])
```

- ##### 自定义你的server

如果zmail不能正常工作，你可以自定义server的配置

```
server = zmail.server('username','password',smtp_host='smtp.163.com',smtp_port=994,smtp_ssl=True,pop_host='pop.163.com',pop_port=995,pop_tls=True)
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

你也可以指定一个范围的邮件

```
mail = server.get_mails(subject='GitHub',start_time='2018-1-1',sender='github',start_index=1,end_index=10)
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

打印你的邮件，使用 **zmail.show()**

```
import zmail
server = zmail.server('yourmail@example.com‘, 'yourpassword')
mail = server.get_latest()
zmail.show(mail)
```
查看邮件的所有内容

```python
import zmail
server = zmail.server('yourmail@example.com’, 'yourpassword')
mail = server.get_latest()
for k,v in mail.items():
	print(k,v)
```




## API索引

### zmail.server(username,password,smtp_host,smtp_port,smtp_ssl,smtp_tls,pop_host,pop_port,pop_ssl,pop_tls,config,timeout=60, debug=False, log=None,auto_add_from=True, auto_add_to=True)

返回 **MailServer** 实例, 它实现了所有SMTP和POP的功能

如果设置了任何以 `pop` 或 `smtp` 开头的参数，它将会取代内部自动生成的参数（自动生成的参数取决于你的 `username` 或 `config` 参数）

***config*** 使用企业邮箱的便捷方法，如果被指定，企业邮箱的配置将会取代所有自动生成的配置

***timeout*** 可为整型或者浮点型，指定了最长的等待时长(秒)

***debug*** 如果为True，server将会打开调试模式，并且显示调试信息

***log*** 可为None或者logging.logger的实例，如果为None，将会使用zmail默认的日志记录器，你可以通过logging.getLogger('zmail')来访问默认的日志记录器

***auto_add_to*** 如果为True，当键'to'（不区分大小写）不在发送的邮件中时，默认的'to'将会自动添加到邮件中

***auto_add_from*** 如果为True，当键'from'（不区分大小写）不在发送的邮件中时，默认的'from'将会自动添加到邮件中



### MailServer.send_mail(recipients, mail, timeout=None,auto_add_from=False, auto_add_to=False)

成功发送时返回True

***recipients*** 可以是字符串或者字符串组成的列表

***mail*** 可以是字典或者 CaseInsensitiveDict(通常是接收到的邮件).邮件的接口位于下方说明

***timeout*** 如果不为None，它将会取代server的超时时间

***auto_add_from*** 如果不为None，它将会取代server的auto_add_from

***auto_add_to*** 如果不为None，它将会取代server的auto_add_to



### MailServer.stat()

获取邮箱状态. 返回值是两个整型组成的元组: (邮件数量, 邮件大小).



### MailServer.get_mail(which)

返回 **Mail**

***which*** 是一个整型，代表了邮件在邮箱中的位置。必须位于1至邮件数量（从MailServer.stat()返回）的范围内

同样将邮件设置为已读



### MailServer.get_mails(subject=None,start_time=None,end_time=None,sender=None,start_index=None,end_index=None)

返回 一个由**Mail**组成的列表

***subject*** 可为None或整型，如果不为None，每个邮件的subject都必须包含***subject***

***start_time*** 可为None或字符串或datetime对象，如果为字符串，它的结构为"年-月-日 时:分:秒"(例如 "2018-1-1 10:10:20") ，如果不为None，每个邮件的时间必须大于start_time

***end_time*** 和start_time类似，如果不为None，每个邮件的时间必须小于end_time

***sender*** 可为None或字符串，如果不为None，每个邮件的'from'头部必须包含***sender***

***start_index*** 可为None或整型，如果为None或者小于1，将会被置为1。如果大于邮件数量（从MailServer.stat()返回），将会被置为邮件数量。

***end_index*** 和start_index类似。选择的邮件范围将会被设置为start_index到end_index之间

同时会将所有取出的邮件置为已读



### MailServer.get_latest()

返回 **Mail**

返回最新的邮件。等同于MailServer.get_mail(message_count)。message_count从MailServer.stat()中可得到。

同时会将邮件置为已读



### MailServer.~~get_info()~~

返回有原始头部组成的列表

使用MailServer.get_headers代替它

在0.2.0版本被移除



### MailServer.get_headers(start_index=None,end_index=None)

返回一个由邮件头部组成的列表（一个CaseInsensitiveDict组成的列表）

取回邮件头的范围将会被限制在start_index至end_index。和它们在MailServer.get_mails()中的表现形式相同

在0.2.0版本中新增



### MailServer.delete(which)

***which*** 表明了那封邮件应该被删除

在0.2.0版本中新增



### MailServer.smtp_able()

返回True如果SMTP工作正常否则返回False



### MailServer.pop_able()

返回True如果POP工作正常否则返回False



### Utils

- #### zmail.show(mails)

  你可以是用这个函数来打印一个或多个邮件

- #### zmail.save_attachment(mail,target_path=None,overwrite=False)

  将邮件的附件存储到target_path。如果不指定，target_path将会是当前目录。如果overwrite为True，写入过程将会覆盖可能存在的同名文件

- #### zmail.save(mail,name=None,target_path=None,overwrite=False)

  保存邮件

- #### zmail.read(file_path,SEP=b'\r\n')

  读取邮件



## Mail 结构



### Mail (用于发送)

可为dict或者CaseInsensitiveDict(一般从get_mail or get_mails获得)

***subject*** 邮件的标题

***from*** 'from'头部，表明了邮件的来源

***to*** **(不在使用)** 你可以使用一个元组(name,address)来指定接收人的名字，适用于抄送和发送。

***content_text*** 邮件的文本内容，可为字符串或者一个由字符串组成的列表

***content_html*** 邮件的HTML内容，可为字符串或者一个由字符串组成的列表

***attachments*** 包含了所有附件。可为 字符串 或者 一个由字符串组成的列表 或者 一个由元组组成的列表。(例如 '/User/apple/1.txt' or ['/User/apple/1.txt','2.txt'] or [('1.txt',b'...'),('2.txt',b'...')] )

***headers*** 如果你想要为邮件添加额外的头文件，你可以在这指定。必须为dict。



### Mail(从 get_mail 或 get_mails获得)

***subject*** 邮件的标题

***from*** 'from'头部，表明了邮件的来源

***to*** 'to'头部，表明了邮件的目的地

***content_text*** 邮件的文本内容，可为字符串或者一个由字符串组成的列表

***content_html*** 邮件的HTML内容，可为字符串或者一个由字符串组成的列表

***attachments*** 包含了所有附件。(例如['1.txt',b'...'])

***raw_headers*** 包含了所有原生头部键值对

***headers*** 包含了所有解析过的头部（为大小写不敏感字典）

***charsets*** 包含了所有编码类型

***date*** 邮件时间

***id*** 邮件的id。用于定位在邮箱中位置

***raw*** 原始的邮件信息。由bytes组成的列表

​    

## 支持的邮件服务商

列表中的邮件服务商已经被测试可正常使用

**如果你的邮箱不在此列，请不要担心，目前尚未发现不支持的邮箱.如果你发现任何问题，请在GitHub上告知于我**  

| 服务商地址 | 发送邮件 | 取回邮件 | 备注                  |
| ---------- | -------- | -------- | --------------------- |
| @163.com   | ✓        | ✓        | 需要应用专用密码      |
| @qq.com    | ✓        | ✓        | POP3 需要应用专用密码 |
| @126.com   | ✓        | ✓        |                       |
| @yeah.net  | ✓        | ✓        |                       |
| @gmail.com | ✓        | ✓        | 需要应用专用密码      |
| @sina.com  | ✓        | ✓        |                       |
| @outlook   | ✓        | ✓        | 需要应用专用密码      |
| @hotmail   | ✓        | ✓        | 需要额外设置          |



## 支持的企业邮箱

| 名称         | 使用示例                                       |
| ------------ | ---------------------------------------------- |
| 腾讯企业邮箱 | zmail.server('username','psw',config='qq')     |
| 阿里企业邮箱 | zmail.server('username','psw',config='ali')    |
| 网易企业邮箱 | zmail.server('username','psw',config='163')    |
| 谷歌企业邮箱 | zmail.server('username','psw',config='google') |



## 问题索引

- ##### 发送或者接受失败

  - 检查是否开启了SMTP和POP3功能
  - 根据服务器SMTP或者POP3地址的端口填写server（没有填写的将会为默认值）
  - SMTP：server = zmail.server('user','psw',smtp_host = 'xxx',smtp_port = 'yyyyy',smtp_ssl=True)
  - POP3：server = zmail.server('user','psw',pop_host = 'xxx',pop_port = 'yyyyy',pop_ssl=True)

