import re
from anki.hooks import addHook

r = r' ?([^ ]+?)\[(.+?)\]'
# based on old japanese plugin, which was based on
# http://welkin.s60.xrea.com/css_labo/Ruby-CSS_DEMO3.html
ruby = r'<span style="display: inline-block; text-align: center; line-height: 1; white-space: nowrap; vertical-align: baseline; margin: 0; padding: 0"><span style="display: block; text-decoration: none; line-height: 1.2; font-weight: normal; font-size: 0.64em">\2</span>\1</span>'

def kanjionly(txt, *args):
    return re.sub(r, r'\1', txt)

def readingonly(txt, *args):
    return re.sub(r, r'\2', txt)

def furigana(txt, *args):
    return re.sub(r, ruby, txt)

addHook('fieldModifier_kanjionly', kanjionly);
addHook('fieldModifier_readingonly', readingonly);
addHook('fieldModifier_furigana', furigana);
