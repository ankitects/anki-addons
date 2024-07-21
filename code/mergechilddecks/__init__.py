# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

from anki.decks import DeckId
from anki.utils import ids2str, int_time
from aqt import mw
from aqt.qt import *
from aqt.qt import sip


class Wizard(QWizard):
    changes: list[Change] = []

    def __init__(self) -> None:
        QWizard.__init__(self)
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)
        self.setWindowTitle("Merge Child Decks")
        self.addPage(OptionsPage())
        self.addPage(PreviewPage())
        self.addPage(CommitPage())


class OptionsPage(QWizardPage):
    def __init__(self) -> None:
        QWizardPage.__init__(self)

    def initializePage(self) -> None:
        self.setTitle("Options")

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Depth"))
        depth = QSpinBox()
        depth.setRange(1, 10)
        depth.setValue(2)
        self.registerField("depth", depth)
        hbox.addWidget(depth)
        hbox.addStretch()
        vbox.addLayout(hbox)

        l = QLabel(
            "For example, if you set this to 2, cards from 'One::Two::Three' will be moved into 'One::Two'"
        )
        l.setWordWrap(True)
        vbox.addWidget(l)

        vbox.addSpacing(30)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Deck Prefix"))
        deck = QLineEdit()
        deck.setPlaceholderText("optional prefix")
        self.registerField("deckprefix", deck)
        hbox.addWidget(deck)
        vbox.addLayout(hbox)
        l = QLabel(
            "Specifying a deck here will ignore any decks that don't start with the prefix."
        )
        l.setWordWrap(True)
        vbox.addWidget(l)

        vbox.addSpacing(30)

        tag = QCheckBox("Tag Notes")
        tag.setChecked(True)
        self.registerField("tag", tag)
        vbox.addWidget(tag)
        l = QLabel(
            "When enabled, a tag based on the original child deck name will be added to notes."
        )
        l.setWordWrap(True)
        vbox.addWidget(l)

        vbox.addStretch()

        self.setLayout(vbox)


class PreviewPage(QWizardPage):
    def __init__(self) -> None:
        QWizardPage.__init__(self)

    def initializePage(self) -> None:
        self.setCommitPage(True)
        self.setTitle("Preview")

        vbox = QVBoxLayout()

        edit = QPlainTextEdit()
        edit.setReadOnly(True)
        f = QFont("Courier")
        f.setStyleHint(QFont.StyleHint.Monospace)
        edit.setFont(f)
        vbox.addWidget(edit)

        changes = buildChanges(
            self.field("depth"), self.field("deckprefix"), self.field("tag")
        )

        self.get_wizard().changes = changes

        if not changes:
            edit.setPlainText("No changes to perform.")
        else:
            buf = "Cards will be removed from any filtered decks, then moved in the following decks:\n\n"
            buf += "\n\n".join(self._renderChange(x) for x in changes)
            edit.setPlainText(buf)

        if self.layout():
            sip.delete(self.layout())
        self.setLayout(vbox)

    def isComplete(self) -> bool:
        return bool(self.get_wizard().changes)

    def _renderChange(self, change: Change) -> str:
        return """\
From: %s
  To: %s
 Tag: %s  
""" % (
            change.oldname,
            change.newname,
            change.tag or "[no tag added]",
        )

    def get_wizard(self) -> Wizard:
        return self.wizard()  # type: ignore


class CommitPage(QWizardPage):
    def __init__(self) -> None:
        QWizardPage.__init__(self)

    def initializePage(self) -> None:
        self.changeDecks()

        self.setTitle("Done!")

        vbox = QVBoxLayout()

        vbox.addWidget(QLabel("Decks have been updated."))

        vbox.addStretch()

        self.setLayout(vbox)
        print("done!")

    def changeDecks(self) -> None:
        changes = self.get_wizard().changes
        performDeckChange(changes)

    def get_wizard(self) -> Wizard:
        return self.wizard()  # type: ignore


@dataclass
class Change:
    oldname: str
    newname: str
    tag: str


def buildChanges(depth: int, deckprefix: str, tag: str) -> list[Change]:
    changes = []
    for deck in sorted(mw.col.decks.all(), key=lambda x: x["name"].lower()):
        # ignore if prefix doesn't match
        if not deck["name"].lower().startswith(deckprefix.lower()):
            continue

        # ignore if it's already short enough
        components = deck["name"].split("::")
        if len(components) <= depth:
            continue

        # ignore if it's a filtered deck
        if deck.get("dyn"):
            continue

        newcomponents = components[0:depth]
        if tag:
            rest = components[depth:]
            tag = "-".join(rest)
            tag = re.sub(r"[\s,]", "-", tag)
        else:
            tag = ""

        changes.append(
            Change(
                oldname=deck["name"], newname="::".join(newcomponents), tag=tag.lower()
            )
        )

    return changes


def performDeckChange(changes: list[Change]) -> None:
    # process in reverse order, leaves first
    changes2 = reversed(changes)
    nameMap = {d.name: DeckId(d.id) for d in mw.col.decks.all_names_and_ids()}

    mw.progress.start(immediate=True)
    try:
        for change in changes2:
            changeDeck(nameMap, change)
            mw.progress.update()
    finally:
        mw.progress.finish()


def changeDeck(nameMap: dict[str, DeckId], change: Change) -> None:
    oldDid = nameMap[change.oldname]
    newDid = nameMap[change.newname]

    # remove cards from any filtered decks
    cids = mw.col.db.list("select id from cards where odid=?", oldDid)
    if cids:
        mw.col.sched.remFromDyn(cids)

    # tag the notes
    if change.tag:
        nids = mw.col.db.list("select distinct nid from cards where did=?", oldDid)
        if nids:
            mw.col.tags.bulk_add(nids, change.tag)

    # move cards
    mod = int_time()
    usn = mw.col.usn()
    mw.col.db.execute(
        """
update cards set did=?, usn=?, mod=? where did=?""",
        newDid,
        usn,
        mod,
        oldDid,
    )

    # remove the deck
    mw.col.decks.remove([oldDid])


def setupMenu() -> None:
    action = QAction("Merge Child Decks...", mw)

    def onMergeAction() -> None:
        w = Wizard()
        w.exec()
        mw.reset()

    action.triggered.connect(onMergeAction)
    mw.form.menuTools.addAction(action)


setupMenu()
