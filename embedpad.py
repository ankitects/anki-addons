# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# This plugin inserts a canvas in your deck for use with AnkiMobile. The
# canvas code is copyright the Tegaki project, and its integration with
# AnkiMobile copyright Shawn Moore - I just wrote a plugin to make using it
# easier.
#
# Shawn's work on this is at http://github.com/sartak/ankimobile-canvas
#
# This code will clobber mobileJS and mobileCSS deck variables, so if you've
# customized them, back up your local content first.
#
# changes by HS 2010-10-26:
#
# Starting with the Embed scratchpad plugin I removed everything that
# is not needed, in my oppion.  So, now you can only draw and clear.
# You cannot redraw you strokes, undo single strokes and so an.  I
# think it is much more responsive now.
#
# changed by Damien 2011-02-05:
#
# - work around serious webkit memory leaks, so using this won't cause lowmem
# crashes after 60-100 cards anymore
# - resize to 90% of width and 40% of screen size and remove retina
# display-specific code
# - don't setup new handlers each time a deck is opened, which lead to slower
# and slower performance
# - add a margin to the clear link to make it difficult to accidentally show
# the answer
# - support the iPad as well
#
# 2011-02-09:
#
# - patch from HS to improve appearance or retina display and display as a
# square
# - modified by Damien to default to the old rectangle which fits on the
# screen in both orientations and isn't biased towards kanji. If you want a
# square display, search for (0) and change it to (1)
#
# 2011-02-16:
#
# - patch from Shawn to remove code for IE and mouse support since this is iOS
# specific
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ankiqt import mw, ui
import os,re

def onEdit():
    mw.deck.setVar("mobileJS", JS)
    mw.deck.setVar("mobileCSS", CSS)
    mw.deck.setModified()
    if not mw.currentCard:
        ui.utils.showInfo("Please run this when a card is shown")
        return
    if not "canvas" in mw.currentCard.cardModel.qformat:
        mw.currentCard.cardModel.qformat += '\n<br><div id="canvas"></div>'
        mw.deck.updateCardsFromModel(mw.currentCard.fact.model)
    mw.syncDeck()
    ui.utils.showInfo("Updated deck sent to server. "+
                      "Sync on AnkiMobile to finish.")

# Setup menu entries
menu1 = QAction(mw)
menu1.setText("Embed Scratchpad")
mw.connect(menu1, SIGNAL("triggered()"), onEdit)
mw.mainWin.menuTools.addSeparator()
mw.mainWin.menuTools.addAction(menu1)

#
# 3rd party code below
#
CSS = """
canvas {
    border: 2px solid black;
}
.cvlink {
    padding: 0.3em 1em;
    border: 1px solid #000;
    background: #aaa;
    border-radius: 5px;
    text-decoration: none;
    color: #000;
}
"""

JS = r'''
/* webcanvas.js */
WebCanvas = function(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");

    this.buttonPressed = false;

    this.adjustSize();
    this._initListeners();
}

WebCanvas.prototype.adjustSize = function() {
    this.w = 1.0*this.canvas.getAttribute('width');
    this.h = 1.0*this.canvas.getAttribute('height');

    this.lw = 2 // linewidth
    this.scale = 1;

    if( window.devicePixelRatio == 2 ) {  // double size for iPhone4
         this.w     *= 2;
         this.h     *= 2;
         this.lw    *= 2;
         this.scale *= 2;
         this.canvas.setAttribute('width',  this.w);
         this.canvas.setAttribute('height', this.h);
         this.ctx.scale(2, 2);
    }
}

WebCanvas.prototype._withHandwritingLine = function() {
    this.ctx.strokeStyle = "rgb(0, 0, 0)";
    this.ctx.lineWidth = this.lw;
    this.ctx.lineCap = "round";
    this.ctx.lineJoin = "round";
}


WebCanvas.prototype._withAxisLine = function() {
    this.ctx.strokeStyle = "rgba(0, 0, 0, 0.1)";
    this.ctx.lineWidth = this.lw;
    this.ctx.lineCap = "butt";
}

WebCanvas.prototype._clear = function() {
    this.canvas.width = this.canvas.width; // clears the canvas
}

WebCanvas.prototype._drawAxis = function() {
    this._withAxisLine();

    this.ctx.beginPath();
    this.ctx.moveTo(this.w/2, 0);
    this.ctx.lineTo(this.w/2, this.h);
    this.ctx.moveTo(0, this.h/2);
    this.ctx.lineTo(this.w, this.h/2);

    this.ctx.stroke();
}

WebCanvas.prototype._initListeners = function() {

    function callback(webcanvas, func) {
        /* Without this trick, "this" in the callback refers to the canvas HTML object.
                          With this trick, "this" refers to the WebCanvas object! */
        return function(event) {
            func.apply(webcanvas, [event]);
        }
    }

    // iPhone/iTouch events
    this.canvas.addEventListener("touchstart",  callback(this, this._onButtonPressed),  false);
    this.canvas.addEventListener("touchend",    callback(this, this._onButtonReleased), false);
    this.canvas.addEventListener("touchcancel", callback(this, this._onButtonReleased), false);
    this.canvas.addEventListener("touchmove",   callback(this, this._onMove),           false);

    // Disable page scrolling via dragging inside the canvas
    this.canvas.addEventListener("touchmove", function(e){e.preventDefault();}, false);
}

WebCanvas.prototype._onButtonPressed = function(event) {
    window.event.stopPropagation();
    // this can occur with an iPhone/iTouch when we try to drag two fingers
    // on the canvas, causing a second smaller canvas to appear
    if (this.buttonPressed) return;

    this.buttonPressed = true;

    this.ctx.beginPath();
    this._withHandwritingLine();

    var position = this._getRelativePosition(event);
    this.ctx.moveTo(position.x, position.y);
}

WebCanvas.prototype._onMove = function(event) {

    if (this.buttonPressed) {
        var position = this._getRelativePosition(event);
        this.ctx.lineTo(position.x, position.y);
        this.ctx.stroke();
    }
}

WebCanvas.prototype._onButtonReleased = function(event) {
    window.event.stopPropagation();
    if (this.buttonPressed) {
        this.buttonPressed = false;
    }
}

WebCanvas.prototype._getRelativePosition = function(event) {
    var t = this.canvas;

    var e = event.targetTouches[0];
    var x = e.pageX;
    var y = e.pageY;

    do
        x -= t.offsetLeft + parseInt(t.style.borderLeftWidth || 0),
        y -= t.offsetTop + parseInt(t.style.borderTopWidth || 0);
    while (t = t.offsetParent);

    x *= this.scale;
    y *= this.scale;

    return {"x":x,"y":y};
}

WebCanvas.prototype.clear = function() {
    this._clear();
    this._drawAxis();
}

/* ankimobile.js */
function setupCanvas () {
    var cv;
    // create a reusable canvas to avoid webkit leaks
    if (!document.webcanvas) {
        cv = document.createElement("canvas");
        document.webcanvas = new WebCanvas(cv);
    } else {
        cv = document.webcanvas.canvas;
    }
    var w = window.innerWidth;
    var h = window.innerHeight;
    if (0) {
        // square
        h = w = Math.min(w,h) * 0.8;
    } else {
        // rectangle
        w *= 0.9;
        h *= 0.4;
    }
    cv.setAttribute("width" , w);
    cv.setAttribute("height", h);
    cv.style.width = w;             // set CSS width  (important for Retina display)
    cv.style.height = h;            // set CSS height (important for Retina display)
    document.webcanvas.adjustSize();
    document.webcanvas.clear();
    // put the canvas in the holder
    var holder = document.getElementById("canvas");
    if (!holder) {
        return;
    }
    holder.appendChild(cv);
    // and the clear link
    holder.appendChild(document.createElement("br"));
    var clear = document.createElement("a");
    clear.className = "cvlink";
    clear.appendChild(document.createTextNode("Clear"));
    clear.setAttribute("href", "#");
    clear.ontouchstart = function () { document.webcanvas.clear(); window.event.stopPropagation();}
    holder.appendChild(clear);
}

if (!document.webcanvas) {
    Ti.App.addEventListener("showQuestion1", setupCanvas);
    Ti.App.addEventListener("showQuestion2", setupCanvas);
}
'''
