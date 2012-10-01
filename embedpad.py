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
# 2012-10-01:
#
# - update for Anki 2.0
#

from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo
import os,re

def onEdit():
    if not mw.reviewer.card:
        return showInfo("Please run this when a card is shown")
    m = mw.reviewer.card.model()
    t = mw.reviewer.card.template()
    if "canvas" in t['qfmt']:
        return
    mw.checkpoint("Embed Scratchpad")
    t['qfmt'] += '\n<br><div id="canvas"></div>' + "\n<script>%s</script>" % JS
    m['css'] += CSS
    mw.col.models.save(m)
    mw.col.setMod()
    mw.reset()
    showInfo("Scratchpad embedded.")

# Setup menu entries
menu1 = QAction(mw)
menu1.setText("Embed Scratchpad")
mw.connect(menu1, SIGNAL("triggered()"), onEdit)
mw.form.menuTools.addSeparator()
mw.form.menuTools.addAction(menu1)

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

    if (document.all) {
        /* For Internet Explorer */
        this.canvas.unselectable = "on";
        this.canvas.onselectstart = function() { return false };
        this.canvas.style.cursor = "default";
    }

    this.buttonPressed = false;

    this.adjustSize();
    this._initListeners();
}

WebCanvas.prototype.adjustSize = function() {
    this.w = 1.0*this.canvas.getAttribute('width');
    this.h = 1.0*this.canvas.getAttribute('height');

    this.lw = 2 // linewidth
    this.scale = 1;
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
        if (navigator.userAgent.toLowerCase().indexOf('iphone')!=-1 ||
            navigator.userAgent.toLowerCase().indexOf('ipad')!=-1) {
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
    setupCanvas();
}
'''
