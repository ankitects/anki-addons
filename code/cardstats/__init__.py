# Copyright: Ankitects Pty Ltd and contributors
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Show statistics about the current and previous card while reviewing.
# Activate from the tools menu.
#

from __future__ import annotations

from anki.cards import Card
from aqt import mw
from aqt.main import AnkiQt
from aqt.mediasrv import PageContext
from aqt.qt import *
from aqt.webview import AnkiWebView, AnkiWebViewKind


class DockableWithClose(QDockWidget):
    closed = pyqtSignal()

    def closeEvent(self, evt: QCloseEvent) -> None:
        self.closed.emit()
        QDockWidget.closeEvent(self, evt)


class CardStats:
    def __init__(self, mw: AnkiQt):
        self.mw = mw
        self.shown: DockableWithClose | None = None
        from aqt import gui_hooks

        gui_hooks.reviewer_did_show_question.append(self._update)
        gui_hooks.reviewer_will_end.append(self.hide)

    def _addDockable(self, title: str, w: AnkiWebView) -> DockableWithClose:
        dock = DockableWithClose(title, mw)
        dock.setObjectName(title)
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        dock.setWidget(w)
        if mw.width() < 600:
            mw.resize(QSize(600, mw.height()))
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        return dock

    def _remDockable(self, dock: QDockWidget) -> None:
        mw.removeDockWidget(dock)

    def show(self) -> None:
        if not self.shown:

            class ThinAnkiWebView(AnkiWebView):
                def sizeHint(self) -> QSize:
                    return QSize(200, 100)

            self.web = ThinAnkiWebView(kind=AnkiWebViewKind.BROWSER_CARD_INFO)
            self.shown = self._addDockable(("Card Info"), self.web)
            self.shown.closed.connect(self._onClosed)
            self._load_html()
        self._update(None)

    def hide(self) -> None:
        if self.shown:
            self._remDockable(self.shown)
            self.shown = None

    def toggle(self) -> None:
        if self.shown:
            self.hide()
        else:
            self.show()

    def _onClosed(self) -> None:
        # schedule removal for after evt has finished
        self.mw.progress.single_shot(100, self.hide, False)

    def _update(self, card: Card | None) -> None:
        if not self.shown:
            return
        self.web.eval(f"anki.updateCardInfos('{self._get_ids()}');")

    def _get_ids(self) -> str:
        r = self.mw.reviewer
        current_id = r.card.id if r.card else "null"
        previous = r.lastCard()
        previous_id = previous.id if previous else "null"
        return f"{current_id}/{previous_id}"

    def _revlog_as_number(self) -> str:
        config = mw.addonManager.getConfig(__name__)
        return "1" if config.get("revlog") else "0"

    def _load_html(self) -> None:
        self.web.load_sveltekit_page(
            f"card-info/{self._get_ids()}?revlog={self._revlog_as_number()}"
        )


_cs = CardStats(mw)


def cardStats(on: bool) -> None:
    _cs.toggle()


action = QAction(mw)
action.setText("Card Stats")
action.setCheckable(True)
action.setShortcut(QKeySequence("Ctrl+Alt+C"))
mw.form.menuTools.addAction(action)
action.toggled.connect(cardStats)  # type: ignore
