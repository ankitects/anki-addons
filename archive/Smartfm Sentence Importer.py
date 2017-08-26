# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin lets you import smart.fm material into Anki.
#
# Many thanks to smart.fm for the material and the generous sharing policies.
#
# To use, create a new deck, then run Tools > Smart.fm Import
#
# Enter a list URL like:
# http://www.iknow.co.jp/lists/19055-japanese-core-2000-step-2
#
# Once it's finished downloading, you can add more contents, or click cancel
# to finish.
#

includeImages = False
includeSounds = True

import re, urllib, urllib2, simplejson

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw
from ankiqt.ui.utils import getOnlyText
from anki.models import Model, FieldModel, CardModel
from anki.features.japanese import kakasi

def doImport():
    # add an iknow model
    if not [m for m in mw.deck.models if m.name == 'Smart.fm']:
        m = Model(u'Smart.fm')
        m.addFieldModel(FieldModel(u'Expression', False, False))
        m.addFieldModel(FieldModel(u'Meaning', False, False))
        m.addFieldModel(FieldModel(u'Reading', False, False))
        m.addFieldModel(FieldModel(u'Audio', False, False))
        m.addFieldModel(FieldModel(u'Image', False, False))
        m.addCardModel(CardModel(
            u'Listening',
            u'Listen.%(Audio)s',
            u'%(Expression)s<br>%(Reading)s<br>%(Meaning)s<br>%(Image)s'))
        mw.deck.addModel(m)
    while 1:
        mw.reset()
        url = getOnlyText("Enter list URL:")
        if not url:
            return
        id = re.search("/lists/(\d+)", url).group(1)
        # get sentences
        f = urllib2.urlopen(
            "http://api.smart.fm/lists/%s/sentences.json" % id)
        d = simplejson.load(f)
        # add facts
        diag = QProgressDialog(_("Importing..."), "", 0, 0, mw)
        diag.setCancelButton(None)
        diag.setMaximum(len(d))
        diag.setMinimumDuration(0)
        for i, sen in enumerate(d):
            diag.setValue(i)
            diag.setLabelText(sen['text'])
            mw.app.processEvents()
            f = mw.deck.newFact()
            f['Expression'] = sen['text']
            f['Meaning'] = sen['translations'] and sen['translations'][0]['text'] or u""
            try:
                f['Reading'] = sen['transliterations']['Hrkt'] or u""
                # reading is sometimes missing
                if not f['Reading'] and kakasi:
                    f['Reading'] = kakasi.toFurigana(f['Expression'])
            except KeyError:
                f['Reading'] = u""
            if includeSounds and sen['sound']:
                (file, headers) = urllib.urlretrieve(sen['sound'])
                path = mw.deck.addMedia(file)
                f['Audio'] = u'[sound:%s]' % path
            else:
                f['Audio'] = u""
            if includeImages and sen['image']:
                (file, headers) = urllib.urlretrieve(sen['image'])
                path = mw.deck.addMedia(file)
                f['Image'] = u'<img src="%s">' % path
            else:
                f['Image'] = u""
            mw.deck.addFact(f)
        diag.cancel()
        mw.deck.save()

act = QAction(mw)
act.setText("Smart.fm Import")
mw.connect(act, SIGNAL("triggered()"),
           doImport)

mw.mainWin.menuTools.addSeparator()
mw.mainWin.menuTools.addAction(act)

mw.registerPlugin("Smart.fm Sentence Importer", 1)
