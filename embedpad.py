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
menu1.setText("Embed Simple Scratchpad")
mw.connect(menu1, SIGNAL("triggered()"), onEdit)
mw.mainWin.menuTools.addSeparator()
mw.mainWin.menuTools.addAction(menu1)

#
# 3rd party code below
#
CSS = """
#ianki_webcanvas {
    border: 2px solid black;
    width: 250;
    height: 250;
}
.canvas_links {
    list-style-type: none;
    padding: 0;
    margin: 0;
    font-size: 1.6em;
}
.canvas_links a {
    color: #0000FF;
}

"""

JS = r'''
/* webcanvas.js */
WebCanvas = function(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");

    if (document.all) {
        /* For Internet Explorer */
        this.canvas.unselectable = "on";
        this.canvas.onselectstart = function() { return false };
        this.canvas.style.cursor = "default";
    }

    this.buttonPressed = false;

    this.w = 1.0*this.canvas.getAttribute('width');
    this.h = 1.0*this.canvas.getAttribute('height');

    this.lw = 2 // linewidth
    this.scale = 1;

    if(window.devicePixelRatio == 2) {  // double size for iPhone4
         this.w     *= 2;
         this.h     *= 2;
         this.lw    *= 2;
         this.scale *= 2; 
         this.canvas.setAttribute('width',  this.w);
         this.canvas.setAttribute('height', this.h);
         this.ctx.scale(2, 2);
    }

    this._initListeners();
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

    if (this.canvas.attachEvent) {
        this.canvas.attachEvent("onmousemove",      callback(this, this._onMove));
        this.canvas.attachEvent("onmousedown",      callback(this, this._onButtonPressed));
        this.canvas.attachEvent("onmouseup",        callback(this, this._onButtonReleased));
        this.canvas.attachEvent("onmouseout",       callback(this, this._onButtonReleased));
    }
    else if (this.canvas.addEventListener) {
        // Browser sniffing is evil, but I can't figure out a good way to ask in
        // advance if this browser will send touch or mouse events.
        // If we generate both touch and mouse events, the canvas gets confused
        // on iPhone/iTouch with the "revert stroke" command
        if (navigator.userAgent.toLowerCase().indexOf('iphone')!=-1) {
            // iPhone/iTouch events
            this.canvas.addEventListener("touchstart",  callback(this, this._onButtonPressed),  false);
            this.canvas.addEventListener("touchend",    callback(this, this._onButtonReleased), false);
            this.canvas.addEventListener("touchcancel", callback(this, this._onButtonReleased), false);
            this.canvas.addEventListener("touchmove",   callback(this, this._onMove),           false);

            // Disable page scrolling via dragging inside the canvas
            this.canvas.addEventListener("touchmove", function(e){e.preventDefault();}, false);
        }
        else {
            this.canvas.addEventListener("mousemove",  callback(this, this._onMove),           false);
            this.canvas.addEventListener("mousedown",  callback(this, this._onButtonPressed),  false);
            this.canvas.addEventListener("mouseup",    callback(this, this._onButtonReleased), false);
            this.canvas.addEventListener("mouseout",   callback(this, this._onButtonReleased), false);
        }
    }
    else alert("Your browser does not support interaction.");
}

WebCanvas.prototype._onButtonPressed = function(event) {

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

    if (this.buttonPressed) {
        this.buttonPressed = false;
    }
}

WebCanvas.prototype._getRelativePosition = function(event) {
    var t = this.canvas;

    var x, y;
    // targetTouches is iPhone/iTouch-specific; it's a list of finger drags
    if (event.targetTouches) {
       var e = event.targetTouches[0];

       x = e.pageX;
       y = e.pageY;
    }
    else {
        x = event.clientX + (window.pageXOffset || 0);
        y = event.clientY + (window.pageYOffset || 0);
    }

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
function add_canvas (id) {
    var parent_element = document.getElementById(id);
    if (!parent_element) {
        return;
    }

    parent_element.innerHTML = '<canvas id="ianki_webcanvas" width=250 height=250></canvas><div id="cl" class="canvas_links"><a href="#" onclick="document.webcanvas.clear();">clear</a></div>';

    /* stop bubbling the click events up to AnkiMobile's tap handlers */
// this is not needed for the canvas as there one should not click, but draw
//    parent_element.onclick = function () {window.event.stopPropagation();};
// but it is needed for the links
    var cl = document.getElementById("cl");
    if (cl) cl.onclick = function () {window.event.stopPropagation();};


    document.webcanvas = null;
    var canvas = document.getElementById("ianki_webcanvas");
    if (canvas.getContext) {
        document.webcanvas = new WebCanvas(canvas);
        document.webcanvas.clear();
    }
}

Ti.App.addEventListener("showQuestion1", function () { add_canvas("canvas") })
Ti.App.addEventListener("showQuestion2", function () { add_canvas("canvas") })

'''
