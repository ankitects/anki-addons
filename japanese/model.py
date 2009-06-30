# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Standard Japanese model.
#

from anki.models import Model, CardModel, FieldModel
import anki.stdmodels

def JapaneseModel():
    m = Model(_("Japanese"))
    # expression
    f = FieldModel(u'Expression', True, True)
    font = u"Mincho"
    f.quizFontSize = 50
    f.quizFontFamily = font
    f.editFontFamily = font
    m.addFieldModel(f)
    # meaning
    m.addFieldModel(FieldModel(u'Meaning', False, False))
    # reading
    f = FieldModel(u'Reading', False, False)
    font = u"Arial"
    f.quizFontSize = 50
    f.quizFontFamily = font
    f.editFontFamily = font
    m.addFieldModel(f)
    m.addCardModel(CardModel(u"Recognition",
                   u"%(Expression)s",
                   u"%(Reading)s<br>%(Meaning)s"))
    m.addCardModel(CardModel(u"Recall",
                             u"%(Meaning)s",
                             u"%(Reading)s",
                             active=False))
    m.tags = u"Japanese"
    return m

anki.stdmodels.models['Japanese'] = JapaneseModel
