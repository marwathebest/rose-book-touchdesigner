# build_rose_book.py
# يشغّل book_body.py (اللي يبني الكتاب) ويكتب أي خطأ في build_log.txt
import traceback

_DIR = 'C:/Users/MarwahSabei/Desktop/roses_animation'
_LOG = _DIR + '/build_log.txt'

_g = dict(globals())
_g['me'] = me
try:
    _src = open(_DIR + '/book_body.py', encoding='utf-8').read()
    exec(compile(_src, _DIR + '/book_body.py', 'exec'), _g)
    _msg = 'OK'
except Exception:
    _msg = traceback.format_exc()
with open(_LOG, 'w', encoding='utf-8') as f:
    f.write(_msg)
print(_msg)
