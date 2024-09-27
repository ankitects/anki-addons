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
from aqt.webview import AnkiWebView


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

            self.web = ThinAnkiWebView()
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
        self.mw.progress.timer(100, self.hide, False)

    def _update(self, card: Card | None) -> None:
        if not self.shown:
            return
        r = self.mw.reviewer
        id = r.card.id if r.card else "null"
        self.web.eval(f"current.then(s => s.updateStats({id}));")
        lc = r.lastCard()
        id = lc.id if lc else "null"
        self.web.eval(f"previous.then(s => s.updateStats({id}));")

    def _load_html(self) -> None:
        self.web.setHtml(
            """
<html><head>
<script src="js/vendor/bootstrap.bundle.min.js"></script>
<link href="pages/card-info-base.css" rel="stylesheet" />
<link href="pages/card-info.css" rel="stylesheet" />
</head><style>%s</style>
<body>
<script src="pages/card-info.js"></script>
<center>
<h3>Current</h3>
<div id=current></div>
<h3>Previous</h3>
<div id=previous></div>
<script>
const current = anki.setupCardInfo(document.getElementById("current"), {includeRevlog:false});
const previous = anki.setupCardInfo(document.getElementById("previous"), {includeRevlog:false});
</script>
</center></body></html>"""
            % self._style(),
            PageContext.ADDON_PAGE,
        )
        self.web.on_theme_did_change()

    def _style(self) -> str:
        return """
td { font-size: 80%; }
.card-info-placeholder { position: relative !important; }
"""


_cs = CardStats(mw)


def cardStats(on: bool) -> None:
    _cs.toggle()


action = QAction(mw)
action.setText("Card Stats")
action.setCheckable(True)
action.setShortcut(QKeySequence("Ctrl+Alt+C"))
mw.form.menuTools.addAction(action)
action.toggled.connect(cardStats)  # type: ignore
