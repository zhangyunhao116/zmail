from zmail.parser import recursive_decode, remove_line_feed_and_whitespace


def test_recursive_decode():
    test_as_str = 'zmail测试信息'
    assert recursive_decode(test_as_str.encode('utf-8'), ('utf-8',)) == test_as_str
    assert recursive_decode(test_as_str.encode('gbk'), ('gbk', 'utf-8')) == test_as_str
    assert recursive_decode(test_as_str.encode('gbk'), ('utf-8', 'gbk')) == test_as_str
    assert recursive_decode(test_as_str.encode('gbk'), ('utf-8', 'gb2312', 'gbk')) == test_as_str

    assert recursive_decode(test_as_str.encode('utf-8'), tuple()) is None
    assert recursive_decode(test_as_str.encode('gbk'), ('utf-8',)) is None

    assert recursive_decode(test_as_str.encode('utf-8'), ('gbk',)) == 'zmail娴嬭瘯淇℃伅'


def test_remove_line_feed_and_whitespace():
    assert remove_line_feed_and_whitespace('gb2312') == 'gb2312'
    assert remove_line_feed_and_whitespace('nr123rn') == 'nr123rn'

    assert remove_line_feed_and_whitespace(' gb2312 ') == 'gb2312'
    assert remove_line_feed_and_whitespace('r gb2312 n') == 'r gb2312 n'

    assert remove_line_feed_and_whitespace('\r\ngb2312\r\n') == 'gb2312'
    assert remove_line_feed_and_whitespace('\r\n \r\ngb2312\r\n \r\n') == 'gb2312'

    assert remove_line_feed_and_whitespace(r' \r\ngb2312\r\n ') == 'gb2312'
    assert remove_line_feed_and_whitespace(' \r\n\\r\\ngb2312\\r\\n\r\n ') == 'gb2312'

    assert remove_line_feed_and_whitespace(r' \r\n\r\ngb2312\r\n\r\n ') == 'gb2312'
    assert remove_line_feed_and_whitespace('\r\n \r\n\r\ngb2312\r\n\r\n \r\n') == 'gb2312'
