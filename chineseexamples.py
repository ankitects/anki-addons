#!/usr/bin/python
#-*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# author: aaron@lamelion.com
# tested on ubuntu linux and windows xp
# This file is a plugin for anki flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------

import codecs

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.latex import renderLatex
from anki.sound import playFromText, stripSounds
from ankiqt.ui.utils import mungeQA
from ankiqt import mw

import re
import os
import pickle
import urllib,urllib2


curIndex = 0
isOn = False
senFile = os.path.join(mw.config.configPath,'plugins', 'chineseSentences.pickle')
if os.path.exists(senFile):
    pickled = open(senFile,'rb')
    sentences = pickle.load(pickled)
    pickled.close()
else:
    errm = QErrorMessage(mw)
    errm.showMessage('ChineseExampleSentence plugin: you need to put the chinese examples data file into %s'%senFile)

#example sentence lookup & disp ######################################################################
def findChar(c):
    found = []
    for k,v in sentences.iteritems():
        if v[0].find(c)>-1:
            v.append(k)
            found.append(v)
    return found

def moveToStateCES(state):
    origMoveToState(state)
    if state=='showQuestion' or state=='getQuestion' or state=='showAnswer': buttStates(True)
    elif  state=='studyScreen' or state=='initial' or state=='noDeck': buttStates(False)
    else: buttStates(False)

def buttStates(on):
    global toggle,next
    if on:
        toggle.setEnabled(True)
        next.setEnabled(toggle.isChecked() and mw.state=='showAnswer')
    else:
        toggle.setEnabled(False)
        next.setEnabled(False)       

def cardAnsweredCES(quality):
    global curIndex
    curIndex = 0
    origCardAnswered(quality)

def drawAnswerCES():
    if not isOn:
        origDrawAnswer()
        return
    a = mw.currentCard.htmlAnswer()
    mainAns = mungeQA(mw.bodyView.main.deck, a)
    mw.bodyView.write('<span id=answer />'+mainAns)
    mw.bodyView.flush()
    currentCard = mw.currentCard
    word = currentCard.fact['Expression']
    exSens = findChar(' '+word.strip()+' ')
    displayableExSens = exSensFormat(exSens,word)
    mw.bodyView.write(displayableExSens)
    if mw.bodyView.state != mw.bodyView.oldState:
        playFromText(a)

def exSensFormat(exSens,word):
    exSens.sort(senLenCmp)
    max = 1
    hlStyle = '<span style="background-color:#FFDA44;">'
    exStyle = '<span style="font-size:15px">'
    if len(exSens)<max: max = len(exSens)
    offset = curIndex
    dif = len(exSens)-(offset+max)
    if dif<0: return "no more sentences"
    formated = ""
    if len(exSens)>0:
        for i in range(0+offset,max+offset):
            hl = exSens[i][0]
        trans = gTrans(hl)
        start = hl.find(word)
        end = len(word)+start
        numSpaces = hl[:start].count(' ')
        pySplit = exSens[i][1].split(' ')
        pySplit[numSpaces] = hlStyle.replace('44;','44;font-size:15px')+pySplit[numSpaces]+'</span>'
        hl = hl[:start]+hlStyle+hl[start:end]+'</span>'+hl[end:]
        formated += str(i+1)+') '+hl+'<br>'+exStyle+(' '.join(pySplit))+'</span><br>'+trans+'<br><br>'
    else:
        formated = "no examples found"
    return formated+"<span style='color:gray'>found "+str(len(exSens))+" examples out of "+str(len(sentences))+"</span>"

def senLenCmp(x,y):
    return cmp(len(x[0]),len(y[0]))



#gtrans ######################################################################
def gTrans(src):
    url="http://translate.google.com/translate_a/t?client=t&text=%s&sl=%s&tl=%s"%(urllib.quote(src.encode('utf-8')),'zh-CN','en')
    con=urllib2.Request(url, headers={'User-Agent':'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}, origin_req_host='http://translate.google.com')
    try:
        req=urllib2.urlopen(con)
    except urllib2.HTTPError, detail:
        return '<span style="color:gray">Could not get translation: '+str(detail)+'</span>'
    except urllib2.URLError, detail:
        return '<span style="color:gray">Could not get translation: '+str(detail)+'</span>'
    ret=U''
    for line in req:
        line = line.decode('utf-8').strip()
        break
    return re.match('.+?"(.+?)"', line).group(1)

#LOGO ######################################################################
logo = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00\x0f\x08\x06\x00\x00\x00\x85\x80\xcd\x17\x00\x00\x00\x04gAMA\x00\x00\xaf\xc87\x05\x8a\xe9\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<\x00\x00\x02\xe2IDATx\xdabd\xc0\x0f\x18\x81\x98\x15\x88\xd9\xa1\xf4? \xfe\t\xc4\xbf\x80\xf8/\x03\x15\x00@\x001\x12\x90\xe3\x06b\t V\x00bA\xa8\xe5\x8f\xa1\xf8\x03\x10\xff\xa1\xd4\x01\x00\x01\x04s\x00\x13\x10\xb3@13\x12_\x1a\x88M\x81\xd8\x15\x88\xd5\x80\xf8\x0b\x10\x1f\x05\xe2\x83@|\r\x88\xdf\x02\xf1\x7f\xa8ZV\xa8Y\xbf\xa0\xf8?\xd4,Fhh\xfd\x83\xca\xb3 \x89\xfd\x01\x08 Fh\xf0\n\x01\xb1\x14\x10\x8b\x021\x0f\xd4\x01 \x03U\x80\xd8\xcd\x85\x81\xc1\xca\x18\xaa\xbb\x13B\xad\x85:\xe2.\xd42PH\xf1A\x95\xbc\x85\xe2?P\xb3X\xa1j\xbeA\xcd\x85\x99\xff\t\x88\x9f\x01\x04\x10\xc8\x01\x92@\xac\x07\xc4\x8e@l\x08\xe5\xb3@\x15\xc9\x011g9\x90\xe8\xc0\x8c\xb3w@|\x15j0(z\xc4\xa0\xe2 G\xdd\x83\x8a\x83\xa2\x8f\x17\x1au\xef\xa0!"\n\xf5\xfd- \xde\x0b\x10@ \x8b\xc4\x81\xd8\x16hB\x811$4P\xc0\x1e4\xbe\x12\x10\x87B\x98B\xb3\x80\xfa\xde\x03\x19...\x0c\xc6\xc6\x900:{\xf6\xac\xc2\x9e={\x9c\x19\xa0\xe2 p\xef\xde=0F\x16{\xf0\xe0\xc1\xc7;w\xee|\x00\x08 \x10\xdb\n\x88\x17\x02\x85\xff\xff\xc7\x82AqY\x8e\xc4\x7f\x87\xc4^\x05\xc43g\xce\xfc\x8f\x0e@b`}\xe5\xe5`\xfe\xbbw\xef\xfe\x03\x1d\x88\xc2\x17\x14\x14\x04\xa9\xe9\x00\x08 \x06h"\x9b\r\x0c\x81\xff G\x84"Y2\x13\x8b\x03\xca\xa1\x16\x83\xf9..pK\x81>\x03c\x18\x00Y\x08\xd2\xbb{\xf7n0\xff\xcc\x993p\xb9\xd0\xd0\xd0\xff\xd0DY\n\x10@ \x07\xe8B\xd3\x16D\x03\xd4\xf0\xddP>\xba\x03P\xf8P\x1f\x81\x00\xc8"\x98e \x00\xf2-H-\xc8\xa7\xc8`\xd5\xaaU0sAi \x06 \x80@i\x80\x03\x88\x05@.\x99\t\x8a#P<\x02q\x18\x89\xf9\x19\x18\xef(40-\xa0\xc49\x0c\x80\xf8@G1\xbc\x7f\xff\x1e\x94\xf3\x04\x00\x02\x08\x94\xd2\xf9AY\x10\x94\xb0\xd2\xa0\x8a\xeeA\xd9\xe5\xd0D\x87\x13\xac^\x8d!\x04\xb3\x10\xe4\x00\x90E\xc0\xf4\x00\xe6WTT\x80\x1d\x87$&\x0c\xc4\xf2\x00\x01\xc4\x00-d6\x94\xe3H\x84.\xf8\xa2\x00\x88\xd3\xd2\xd20\x12!H\x0c\xa4\x0e\x14\xdc\xb0\xf8\x07\xf1\x95\x94\x94\xc0\t\x10)\x8af\x00\x04\x10([\xeb\x03\xb1/\x10\'\x00\xb129\xc5)\xc8WH\xd9\x10\x14\xbc\xc4h\xbb\x04\xca}\x00\x01\x04r\x80\x08\xb4\xc43\x00buhA\x01*\xbd~\x03\xf1Wh\x81\xc2\x80T\xd4\xfeF\xe2\x83\xca\r6h\x1a\x12\x80\x8a?\x05es \x06\xb9\x82\x13\x8aA)\xfe;T\x0f7\xb4\x94\xbc\x0f\xc4\x17\x01\x02\x88\x11Z\xeaqA\r\xe0\x87&Jfhi\xf5\x1b\xc9Bf(\xfd\x17\x89\xcf\x8c\xa4\x9f\x0b*\xfe\tj\xf9w\xa8<\xac\x16\xfd\x83T\xc4\xff\x87z\xee\x03@\x80\x01\x00Zh\x9a\x0e\x10\xa1\xc4l\x00\x00\x00\x00IEND\xaeB`\x82'
nextLogo='\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00\x0f\x08\x06\x00\x00\x00\x85\x80\xcd\x17\x00\x00\x00\x04gAMA\x00\x00\xaf\xc87\x05\x8a\xe9\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<\x00\x00\x02GIDATx\xdab\xfc\xff\xff?\x035\x00###\x13\x90b\x03b^ \xe6\x07b. \xfe\x0b\xc4\x9f\x80\xf8\x03\x10\x7f\x03\xda\xf5\x17]\x1f@\x00\xb1\x90h\tH=;\x10\xb3B\x85~\x02\xf1/ \xfe\x07\xc4\x9c@,\x05\xc4\x9a@\xac\re\x7f\x05\xe2\x9b@|\x16\x88\xef\x03\xf1gt3\x01\x02\x88\x85\x04\xcbA\x16\x88\x02\xb1<\x10\x8b\x00\xf1\x1f ~\n\xc4/\xa1>\x95\x03b+ \xf6\x03bG$\xad\xa7\x81x:\x10\xbf\xc7\xe6\x00\x80\x00b!\xc2bF\xa8\x8f%\x80\xd8\x08\x88=\xa0>\xfc\x01\xc4\xa7\x80\xf8\x02\x10\x83\xe2\xd1\x04\x88CA\x0e\xdc\xbd{7\x83\x8b\x8b\x0bL\xbf)\x90:\x04\xc4g\x80\xf81\xba\xf9\x00\x01\xc4\x00J\x03\xb80\x100\x03\xb1\x00\x10k\x01q2\x10oU\x02ZV\x0e\xc5P\x8b\x8fA\x1d\xf2_II\xe9\xff\xaaU\xab\xfe#\x03\xa8\x9a%@l\x8a\xcd\x0e\x80\x00"\xe4\x00P\x822\x06\xe2" >\x012\x0c\xe8/\x886\x84\x03\xc0x\xe6\xcc\x99\xff\xb1\x01\xa8\xfcJ \xb6\xc0f\x07@\x00\x11r\x80\x0c\x10\'\x82\x82\xd9\x05jy9\x92\x03`b\xc6 >\x10\xbc{\xf7\xee\x7fyy9I\x0e\x00\x08 B\x0eP\x05\xe2\x1a\x06$K\xb1\xe1\xdd@\x9c\x96\x96\xf6_PP\x10l!)\x0e\x00\x08 B\x89\x10\x94\xba\xbf\x81\xb2\xd3\x1e\x06\x06n\x90\x80 4N@`\x0f\x94\x06\xe5\xb1Y\xb3f\x91U~\x00\x04\x10\xa1\x10\x00e;o ^\n\x8bk\x1ci\x00\x94\xbd\xceA\xcb\x04\x92B\x00 \x80\x08\x85\x00\xc8\xe0\xab@\xbc\x02Z\x9a\xc5\x001\x1f\x9a\x9a[@\xbc\x18Z\xe2\x81\xca\x00g,\xe6\xfc\x86\x86&\x06\x00\x08 B\x0e\x00\xf9\xe8\x05\x10\x7f\x87Z\xf0\x1e\x18\xec\xd1\xc0\x82A\x01*\x7f\x03\x88\xe7Cc\x83\x03\x88\x95q8\xe0\x05\xb4\xdc\xc0\x00\x00\x01\xc4B z@E\xec\x0f`a\xf2\x13Z\xec~\x01\xe2\x07@\xac\x02\r\xda[H\xc5\xac\x00\xb4P:\r-|\x90K\xc2\xab\xd0\x10\xc4\x00\x00\x01\xc4Hle\x044\x94\x19Z\xc1\x08@\xcb\x07X\x14}\x80&T\x90\x9c"4\x8d\x82JJa ~\x0b\xb5\x1c\xecH\xa0]\x18E1@\x001R\xb16Dv\xa0\x00\xb4f\xfc\x05u \xce\xda\x10 \xc0\x00\xfd9\xc0iRg\xb6\x02\x00\x00\x00\x00IEND\xaeB`\x82'
def getLogoFile(name,data):
    logoFile = os.path.join(mw.config.configPath,'plugins',name)
    if not os.path.exists(logoFile):
        lf = open(logoFile,'wb')
        lf.write(data)
        lf.close()
    return logoFile

#anki ######################################################################
def doToggle():
    global isOn,curIndex,next
    curIndex = 0
    isOn = not isOn
    next.setEnabled(isOn and mw.state=='showAnswer')
    mw.bodyView.redisplay()

def doNext():
    global curIndex,isOn
    if isOn:
        curIndex += 1
        mw.bodyView.redisplay()
    
def initChineseExampleSentence():
    global origDrawAnswer,origCardAnswered,origMoveToState,toggle,next
    try: pickled
    except NameError: return
    origDrawAnswer = mw.bodyView.drawAnswer
    origCardAnswered = mw.cardAnswered
    origMoveToState = mw.moveToState
    mw.moveToState = moveToStateCES
    mw.cardAnswered = cardAnsweredCES
    mw.bodyView.drawAnswer = drawAnswerCES
    mw.mainWin.toolBar.addSeparator()
    toggle = QAction(mw)
    icon = QIcon()
    icon.addPixmap(QPixmap(getLogoFile('zhexsen_logo.png',logo)),QIcon.Normal,QIcon.Off)
    toggle.setIcon(icon)
    toggle.setIconText('zhex')
    toggle.setCheckable(True)
    toggle.setEnabled(False)
    mw.connect(toggle,SIGNAL("toggled(bool)"),doToggle)
    mw.mainWin.toolBar.addAction(toggle)
    next = QAction(mw)
    icon = QIcon()
    icon.addPixmap(QPixmap(getLogoFile('zhexsen_logo_next.png',nextLogo)),QIcon.Normal,QIcon.Off)
    next.setIcon(icon)
    next.setIconText('zhex:next')
    next.setEnabled(False)
    mw.connect(next,SIGNAL("triggered()"),doNext)
    mw.mainWin.toolBar.addAction(next)

mw.addHook("init", initChineseExampleSentence)




