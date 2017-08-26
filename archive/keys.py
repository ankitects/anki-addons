from ankiqt import mw

mw.mainWin.actionUndo.setShortcut("9")
mw.mainWin.actionMarkCard.setShortcut("8")

def newEventHandler(evt):
    key = unicode(evt.text())
    if mw.state == "showQuestion" and key == "0":
        evt.accept()
        return mw.mainWin.showAnswerButton.click()
    elif mw.state == "showAnswer" and key == "0":
        evt.accept()
        return getattr(mw.mainWin, "easeButton%d" %
                       mw.defaultEaseButton()).animateClick()
    return oldEventHandler(evt)

oldEventHandler = mw.keyPressEvent
mw.keyPressEvent = newEventHandler
