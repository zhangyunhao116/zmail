import json
from zmail.message import Mail

mail_suites = {
    'mail_base': {
        'subject': 'test',
        'content': 'content',
    },

    'mail_with_list_of_content': {
        'subject': 'test',
        'content': ['content_part_1', 'content_part_2'],
    },

    'mail_with_utf8_char': {
        'subject': 'test测试邮件',
        'content': ['content_part_1_测试部分1', 'content_part_2_测试部分2'],
    },

    'mail_with_attachments': {
        'subject': 'test',
        'content': 'content',
        'attachments': ['favicon.ico', '图标.ico']
    },

    'mail_with_customized_from': {
        'subject': 'test',
        'content': 'content',
        'from': 'WORLD奥特曼',
        'to': 'DEAR怪兽',
    }
}


def test_as_string():
    res = {}
    for k, v in mail_suites.items():
        res[k] = Mail(v).set_boundary('==============ZYunH==').as_string()

    with open('mail_suites_result', 'r') as f:
        mail_suites_result = json.loads(f.read())

    for k, v in mail_suites_result.items():
        assert res[k] == v
