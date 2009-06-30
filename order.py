from ankiqt import mw
from operator import attrgetter
import re

def numericSort(a, b):
    vals = []
    for question in (a, b):
        # get int from start of string
        m = re.match("^(\d+). ", question)
        if m:
            vals.append(int(m.group(1)))
        else:
            vals.append(0)
    return cmp(*vals)

def sortDeck():
    # sort based on number
    mw.currentDeck.sort(cmp=numericSort, key=attrgetter("question"))
    # print the new order for confirmation
    for card in mw.currentDeck:
        print card.question
    mw.currentDeck.setModified()

mw.addHook("init", sortDeck)
