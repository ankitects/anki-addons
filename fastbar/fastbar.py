# -*- coding: utf-8 -*-
# Fastbar: an Anki 2.1 add-on adds a toolbar and toggle the sidebar
# in the Card Browser of Anki 2.1.
# Version: 0.1.1
# GitHub: https://github.com/luminousspice/anki-addons/
#
# Copyright: 2017 Luminous Spice <luminous.spice@gmail.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/agpl.html
#
# Third party softwares used with Fastbar.
# QtAwesome. Copyright 2015 The Spyder development team.
# Released under the MIT License.
# https://github.com/spyder-ide/qtawesome/blob/master/LICENSE
# The Font Awesome is licensed under the SIL Open Font License.
# Six. Copyright 2010-2015 Benjamin Peterson
# Released under the MIT License.
# https://bitbucket.org/gutworth/six/src/LICENSE

from aqt.qt import *
from PyQt5 import QtWidgets, QtCore
from aqt.forms.browser import Ui_Dialog
from aqt.browser import Browser
from anki.sched import Scheduler
from anki.utils import ids2str, intTime
from anki.hooks import addHook, wrap

from . import qtawesome as qta
from . import six

class Fastbar:
    def addToolBar(self):
        tb = QToolBar("Fastbar")
        tb.setObjectName("Fastbar")
        tb.setIconSize(QtCore.QSize(20, 20))
        tb.setToolButtonStyle(3)

        self.form.actionToggle_Sidebar.triggered.connect(lambda: self.sidebarDockWidget.toggleViewAction().trigger())
        self.form.actionToggle_Bury.triggered.connect(self.onBury)
        self.form.actionToggle_Fastbar.triggered.connect(lambda: tb.toggleViewAction().trigger())

        self.form.actionDelete.setText(_("Delete Note"))

        icon_fastbar = qta.icon('ei.remove-sign')
        icon_sidebar = qta.icon('fa.exchange')
        icon_add = qta.icon('fa.plus-square')
        icon_info = qta.icon('fa.info-circle')
        icon_mark = qta.icon('fa.star')
        icon_suspend = qta.icon('fa.pause-circle')
        icon_bury = qta.icon('fa.step-backward')
        icon_deck = qta.icon('fa.inbox')
        icon_note = qta.icon('fa.leanpub')
        icon_tag = qta.icon('fa.tag')
        icon_untag = qta.icon('fa.eraser')
        icon_tag_unused = qta.icon('fa.magic')
        icon_delete = qta.icon('fa.trash-o')
        self.form.actionToggle_Fastbar.setIcon(icon_fastbar)
        self.form.actionToggle_Sidebar.setIcon(icon_sidebar)
        self.form.actionAdd.setIcon(icon_add)
        self.form.action_Info.setIcon(icon_info)
        self.form.actionToggle_Mark.setIcon(icon_mark)
        self.form.actionToggle_Suspend.setIcon(icon_suspend)
        self.form.actionToggle_Bury.setIcon(icon_bury)
        self.form.actionChange_Deck.setIcon(icon_deck)
        self.form.actionChangeModel.setIcon(icon_note)
        self.form.actionAdd_Tags.setIcon(icon_tag)
        self.form.actionRemove_Tags.setIcon(icon_untag)
        self.form.actionClear_Unused_Tags.setIcon(icon_tag_unused)
        self.form.actionDelete.setIcon(icon_delete)

        tb.addAction(self.form.actionToggle_Fastbar)
        tb.addSeparator()
        tb.addAction(self.form.actionToggle_Sidebar)
        tb.addSeparator()
        tb.addAction(self.form.actionAdd)
        tb.addSeparator()
        tb.addAction(self.form.action_Info)
        tb.addSeparator()
        tb.addAction(self.form.actionToggle_Mark)
        tb.addSeparator()
        tb.addAction(self.form.actionToggle_Suspend)
        tb.addSeparator()
        tb.addAction(self.form.actionToggle_Bury)
        tb.addSeparator()
        tb.addAction(self.form.actionChange_Deck)
        tb.addSeparator()
        tb.addAction(self.form.actionChangeModel)
        tb.addSeparator()
        tb.addAction(self.form.actionAdd_Tags)
        tb.addSeparator()
        tb.addAction(self.form.actionRemove_Tags)
        tb.addSeparator()
        tb.addAction(self.form.actionClear_Unused_Tags)
        tb.addSeparator()
        tb.addAction(self.form.actionDelete)
        tb.addSeparator()
        self.addToolBar(tb)

    def isBuried(self):
        return not not (self.card and self.card.queue == -2)

    def onBury(self):
        self.editor.saveNow(self._onBury)

    def _onBury(self):
        bur = not self.isBuried()
        c = self.selectedCards()
        if bur:
            self.col.sched.buryCards(c)
        else:
            self.col.sched.unburiedCards(c)
        self.model.reset()
        self.mw.requireReset()

    def unburiedCards(self, ids):
        "Unburied cards."
        self.col.log(ids)
        self.col.db.execute(
            "update cards set queue=type,mod=?,usn=? "
            "where queue = -2 and id in "+ ids2str(ids),
            intTime(), self.col.usn())

    def setupUi(self, Dialog):
        self.actionToggle_Sidebar = QtWidgets.QAction(Dialog)
        self.actionToggle_Sidebar.setObjectName("toggleSidebar")
        self.actionToggle_Sidebar.setText(_("Toggle Sidebar"))
        self.actionToggle_Bury = QtWidgets.QAction(Dialog)
        self.actionToggle_Bury.setText(_("Toggle Bury"))
        self.actionToggle_Bury.setText(_("Toggle Bury"))
        self.actionToggle_Fastbar = QtWidgets.QAction(Dialog)
        self.actionToggle_Fastbar.setObjectName("toggleFastbar")
        self.actionToggle_Fastbar.setText(_("Toggle Fastbar"))
        self.menuJump.addSeparator()
        self.menuJump.addAction(self.actionToggle_Sidebar)
        self.menuJump.addAction(self.actionToggle_Fastbar)
        self.menu_Cards.addSeparator()
        self.menu_Cards.addAction(self.actionToggle_Bury)

addHook("browser.setupMenus", Fastbar.addToolBar)
Browser.isBuried = Fastbar.isBuried
Browser.onBury = Fastbar.onBury
Browser._onBury = Fastbar._onBury
Scheduler.unburiedCards = Fastbar.unburiedCards

Ui_Dialog.setupUi = wrap(Ui_Dialog.setupUi, Fastbar.setupUi)
