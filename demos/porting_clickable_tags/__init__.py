# Copyright 2013 Abdolmahdi Saravi <amsaravi@yahoo.com>
# Copyright 2019 Joseph Lorimer <joseph@lorimer.me>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from re import sub

from anki.cards import Card
from anki.hooks import wrap
from anki.template import Template
from aqt import dialogs
from aqt.qt import Qt
from aqt.reviewer import Reviewer


def linkHandler(self, url, _old):
    if url.startswith('ct_click_'):
        tag = url.replace('ct_click_', '')
        browser = dialogs.open('Browser', self.mw)
        browser.setFilter('"tag:%s"' % tag)
    elif url.startswith('ct_dblclick_'):
        tag, deck = url.replace('ct_dblclick_', '').split('|')
        browser = dialogs.open('Browser', self.mw)
        browser.setFilter('"tag:%s" "deck:%s"' % (tag, deck))
        browser.setWindowState(
            browser.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
        )
    else:
        return _old(self, url)


def css(self, _old):
    return (
        _old(self)
        + """
<style>
  kbd {
    box-shadow: inset 0 1px 0 0 white;
    background:
      gradient(
        linear,
        left top,
        left bottom,
        color-stop(0.05, #f9f9f9),
        color-stop(1, #e9e9e9)
      );
    background-color: #f9f9f9;
    border-radius: 4px;
    border: 1px solid gainsboro;
    display: inline-block;
    font-size: 15px;
    height: 15px;
    line-height: 15px;
    padding: 4px 4px;
    margin: 5px;
    text-align: center;
    text-shadow: 1px 1px 0 white;
    cursor: pointer;
    cursor: hand;
  }
</style>
"""
    )


def render(self, template, context, encoding, _old):
    js = """
<script type="text/javascript">
  function ct_click(tag) {
    pycmd("ct_click_" + tag)
  }
  function ct_dblclick(tag, deck) {
    pycmd("ct_dblclick_" + tag + "|" + deck)
  }
</script>
"""
    kbd = """
<kbd onclick="ct_click('{tag}')" ondblclick="ct_dblclick('{tag}', '{deck}')">
  {tag}
</kbd>
"""
    template = template or self.template
    context = context or self.context
    if context is not None:
        s = ''.join(
            [
                kbd.format(tag=tag, deck=context['Deck'])
                for tag in context['Tags'].split()
            ]
        )
        template = sub('{{Tags}}', s + js, template)
    return _old(self, template, context, encoding)


Card.css = wrap(Card.css, css, 'around')
Reviewer._linkHandler = wrap(Reviewer._linkHandler, linkHandler, 'around')
Template.render = wrap(Template.render, render, 'around')
