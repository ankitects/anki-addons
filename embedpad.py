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
        mw.currentCard.cardModel.qformat += '\n<br><div id="canvas" />'
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
#ianki_webcanvas {
    border: 2px solid black;
}
.canvas_links {
    list-style-type: none;
    padding: 0;
    margin: 0;
    font-size: .6em;
}
.canvas_links li {
    display: inline;
}
.canvas_links a {
    color: #0000FF;
}"""

JS = r'''
/* character.js */
/*
* Copyright (C) 2008 The Tegaki project contributors
*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License along
* with this program; if not, write to the Free Software Foundation, Inc.,
* 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*/

/*
* Contributors to this file:
*  - Mathieu Blondel
*/

DEFAULT_WIDTH = 1000;
DEFAULT_HEIGHT = 1000;

/* Point */

var Point = function(x, y, pressure, xtilt, ytilt, timestamp) {
    this.x = x;
    this.y = y;
    this.pressure = pressure || null;
    this.xtilt = xtilt || null;
    this.ytilt = ytilt || null;
    this.timestamp = timestamp || null;
}

Point.prototype.copy_from = function(point) {
    var keys = ["x", "y", "pressure", "xtilt", "ytilt", "timestamp"];

    for (var i = 0; i < keys.length; i++) {
        var key = keys[i];

        if (point[key] != null)
            this[key] = point[key];
    }
}

Point.prototype.copy = function() {
    var c = new Point();
    c.copy_from(this);
    return c;
}

Point.prototype.toXML = function() {
    var values = [];
    var keys = ["x", "y", "pressure", "xtilt", "ytilt", "timestamp"];

    for (var i = 0; i < keys.length; i++) {
        var key = keys[i];
        if (this[key] != null)
            values.push(key + "=\"" + this[key] + "\"");
    }

    return "<point " + values.join(" ") + " />";
}

Point.prototype.toSexp = function() {
    return "(" + this["x"] + " "+ this["y"] + ")";
}

/* Stroke */

var Stroke = function() {
    this.points = [];
    this.is_smoothed = false;
}

Stroke.prototype.copy_from = function(stroke) {
    for(var i = 0; i < stroke.points.length; i++) {
        var point = new Point();
        point.copy_from(stroke.points[i]);
        this.points[i] = point;
    }
    this.points.length = stroke.points.length;
}

Stroke.prototype.copy = function() {
    var c = new Stroke();
    c.copy_from(this);
    return c;
}

Stroke.prototype.getPoints = function() {
    return this.points;
}

Stroke.prototype.getNPoints = function() {
    return this.points.length;
}

Stroke.prototype.getDuration = function() {
    if (this.points.length > 0) {
        last = this.points.length - 1;

        if (this.points[last].timestamp != null && this.points[0].timestamp !=
null)
            return (this.points[last].timestamp - this.points[0].timestamp);
    }
    return null;
}

Stroke.prototype.appendPoint = function(point) {
    this.points.push(point);
}

Stroke.prototype.toXML = function() {
    var s = "<stroke>\n";

    for (var i=0; i < this.points.length; i++)
        s += "  " + this.points[i].toXML() + "\n";

    s += "</stroke>";

    return s;
}

Stroke.prototype.toSexp = function() {
    var s = "(";

    for (var i=0; i < this.points.length; i++)
        s += "  " + this.points[i].toSexp() + "\n";

    s += ")";

    return s;
}

Stroke.prototype.smooth = function() {
    /* Smoothing method based on a (simple) moving average algorithm.
     *
     * Let p = p(0), ..., p(N) be the set points of this stroke,
     *     w = w(-M), ..., w(0), ..., w(M) be a set of weights.
     *
     * This algorithm aims at replacing p with a set p' such as
     *
     *    p'(i) = (w(-M)*p(i-M) + ... + w(0)*p(i) + ... + w(M)*p(i+M)) / S
     *
     * and where S = w(-M) + ... + w(0) + ... w(M). End points are not
     * affected.
     */

    if (this.is_smoothed)
        return;

    var weights = [1, 1, 2, 1, 1]; // Weights to be used
    var times = 3;                 // Number of times to apply the algorithm

    if (this.points.length >= weights.length) {
        var offset = Math.floor(weights.length / 2);
        var sum = 0;

        for (var j = 0; j < weights.length; j++) {
            sum += weights[j];
        }

        for (var n = 1; n <= times; n++) {
            var s = this.copy();

            for (var i = offset; i < this.points.length - offset; i++) {
                this.points[i].x = 0;
                this.points[i].y = 0;

                for (var j = 0; j < weights.length; j++) {
                    this.points[i].x += weights[j] * s.points[i + j - offset].x;
                    this.points[i].y += weights[j] * s.points[i + j - offset].y;
                }

                this.points[i].x = Math.round(this.points[i].x / sum);
                this.points[i].y = Math.round(this.points[i].y / sum);
            }
        }
    }
    this.is_smoothed = true;
}

/* Writing */

var Writing = function() {
    this.strokes = [];
    this.width = DEFAULT_WIDTH;
    this.height = DEFAULT_HEIGHT;
}

Writing.prototype.copy_from = function(writing) {
    for(var i = 0; i < writing.strokes.length; i++) {
        var stroke = new Stroke();
        stroke.copy_from(writing.strokes[i]);
        this.strokes[i] = stroke;
    }
    this.strokes.length = writing.strokes.length;
}

Writing.prototype.copy = function() {
    var c = new Writing();
    c.copy_from(this);
    return c;
}

Writing.prototype.getDuration = function() {
    var last = this.strokes.length - 1;
    var lastp = this.strokes[last].getPoints().length - 1;
    if (this.strokes.length > 0)
        if (this.strokes[0].getPoints()[0].timestamp != null &&
            this.strokes[last].getPoints()[lastp].timestamp != null)
            return (this.strokes[last].getPoints()[lastp].timestamp -
                    this.strokes[0].getPoints()[0].timestamp);
    return null;
}

Writing.prototype.getNStrokes = function() {
    return this.strokes.length;
}

Writing.prototype.getStrokes = function() {
    return this.strokes;
}

Writing.prototype.moveToPoint = function(point) {
    var stroke = new Stroke();
    stroke.appendPoint(point);
    this.appendStroke(stroke);
}

Writing.prototype.lineToPoint = function(point) {
    this.strokes[this.strokes.length - 1].appendPoint(point);
}

Writing.prototype.appendStroke = function(stroke) {
    this.strokes.push(stroke);
}

Writing.prototype.removeLastStroke = function() {
    if (this.strokes.length > 0)
        this.strokes.pop();
}

Writing.prototype.clear = function() {
    this.strokes = [];
}

Writing.prototype.toXML = function() {
    var s = "<width>" + this.width + "</width>\n"
    s += "<height>" + this.height + "</height>\n"

    s += "<strokes>\n";

    for (var i = 0; i < this.strokes.length; i++) {
        var lines = this.strokes[i].toXML().split("\n");

        for (var j = 0; j < lines.length; j++)
            s += "  " + lines[j] + "\n";
    }

    s += "</strokes>";

    return s;
}

Writing.prototype.toSexp = function() {
    var s = "(width " + this.width + ") "
    s += "(height " + this.height + ")\n"

    s += "(strokes ";

    for (var i = 0; i < this.strokes.length; i++) {
        var lines = this.strokes[i].toSexp().split("\n");

        for (var j = 0; j < lines.length; j++)
            s += " " + lines[j] + "";
    }

    s += ")";

    return s;
}

Writing.prototype.smooth = function() {
    for (var i = 0; i < this.strokes.length; i++) {
        this.strokes[i].smooth();
    }
}

/* Character */

var Character = function() {
    this.writing = new Writing();
    this.utf8 = null;
}

Character.prototype.copy_from = function(character) {
    this.setUTF8(character.utf8);

    var writing = new Writing();
    writing.copy_from(character.writing);

    this.setWriting(writing);
}

Character.prototype.copy = function() {
    var c = new Character();
    c.copy_from(this);
    return c;
}

Character.prototype.getUTF8 = function() {
    return this.utf8;
}

Character.prototype.setUTF8 = function(utf8) {
    this.utf8 = utf8;
}

Character.prototype.getWriting = function() {
    return this.writing;
}

Character.prototype.setWriting = function(writing) {
    this.writing = writing;
}

Character.prototype.toSexp = function() {
    var s = "(character";

    var lines = this.writing.toSexp().split("\n");

    for (var i = 0; i < lines.length; i++)
        s += " " + lines[i] + " ";

    s += ")";

    return s;
}

Character.prototype.toXML = function() {
    var s = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";

    s += "<character>\n";
    s += "  <utf8>" + this.utf8 + "</utf8>\n";

    var lines = this.writing.toXML().split("\n");

    for (var i = 0; i < lines.length; i++)
        s += "  " + lines[i] + "\n";

    s += "</character>";

    return s;
}

/* webcanvas.js */
/*
* Copyright (C) 2008 The Tegaki project contributors
*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License along
* with this program; if not, write to the Free Software Foundation, Inc.,
* 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*/

/*
* Contributors to this file:
*  - Mathieu Blondel
*  - Shawn M Moore
*/

/* Internal canvas size */
CANVAS_WIDTH = 1000;
CANVAS_HEIGHT = 1000;

WebCanvas = function(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");

    if (document.all) {
        /* For Internet Explorer */
        this.canvas.unselectable = "on";
        this.canvas.onselectstart = function() { return false };
        this.canvas.style.cursor = "default";
    }

    this.internal2real_scalex = canvas.width * 1.0 / CANVAS_WIDTH;
    this.internal2real_scaley = canvas.height * 1.0 / CANVAS_HEIGHT;

    this.real2internal_scalex = 1.0 / this.internal2real_scalex;
    this.real2internal_scaley = 1.0 / this.internal2real_scaley;

    this.writing = new Writing();
    this.buttonPressed = false;
    this.first_point_time = null;
    this.locked = false;

    this._initListeners();
}

WebCanvas.prototype._withHandwritingLine = function() {
    this.ctx.strokeStyle = "rgb(0, 0, 0)";
    this.ctx.lineWidth = 8;
    this.ctx.lineCap = "round";
    this.ctx.lineJoin = "round";
}

WebCanvas.prototype._withStrokeLine = function() {
    this.ctx.strokeStyle = "rgba(255, 0, 0, 0.7)";
    this.ctx.lineWidth = 8;
    this.ctx.lineCap = "round";
    this.ctx.lineJoin = "round";
}

WebCanvas.prototype._withAxisLine = function() {
    this.ctx.strokeStyle = "rgba(0, 0, 0, 0.1)";
    this.ctx.lineWidth = 4;
    //this.ctx.set_dash ([8, 8], 2);
    this.ctx.lineCap = "butt";
    this.ctx.lineJoin = "round";
}

WebCanvas.prototype._drawBackground = function() {
    this.ctx.beginPath();
    this.ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    this.ctx.closePath();
}

WebCanvas.prototype._drawAxis = function() {
    this.ctx.save();

    this._withAxisLine();

    this.ctx.beginPath();

    this.ctx.moveTo(CANVAS_WIDTH / 2, 0);
    this.ctx.lineTo(CANVAS_WIDTH / 2, CANVAS_HEIGHT);
    this.ctx.moveTo(0, CANVAS_HEIGHT / 2);
    this.ctx.lineTo(CANVAS_WIDTH, CANVAS_HEIGHT / 2);

    this.ctx.stroke();
    this.ctx.restore();
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
        this.canvas.attachEvent("onmousemove",
                                callback(this, this._onMove));
        this.canvas.attachEvent("onmousedown",
                                callback(this, this._onButtonPressed));
        this.canvas.attachEvent("onmouseup",
                                callback(this, this._onButtonReleased));
        this.canvas.attachEvent("onmouseout",
                                callback(this, this._onButtonReleased));
    }
    else if (this.canvas.addEventListener) {
        // Browser sniffing is evil, but I can't figure out a good way to ask in
        // advance if this browser will send touch or mouse events.
        // If we generate both touch and mouse events, the canvas gets confused
        // on iPhone/iTouch with the "revert stroke" command
        if (navigator.userAgent.toLowerCase().indexOf('iphone')!=-1 || navigator.userAgent.toLowerCase().indexOf('ipad')!=-1) {
            // iPhone/iTouch events
            this.canvas.addEventListener("touchstart",
                                        callback(this, this._onButtonPressed),
                                                false);
            this.canvas.addEventListener("touchend",
                                        callback(this, this._onButtonReleased),
                                        false);
            this.canvas.addEventListener("touchcancel",
                                        callback(this, this._onButtonReleased),
                                        false);
            this.canvas.addEventListener("touchmove",
                                        callback(this, this._onMove), false);

            // Disable page scrolling via dragging inside the canvas
            this.canvas.addEventListener("touchmove", function(e){e.preventDefault();}, false);
        }
        else {
            this.canvas.addEventListener("mousemove",
                                        callback(this, this._onMove), false);
            this.canvas.addEventListener("mousedown",
                                        callback(this, this._onButtonPressed),
                                                false);
            this.canvas.addEventListener("mouseup",
                                        callback(this, this._onButtonReleased),
                                        false);
            this.canvas.addEventListener("mouseout",
                                        callback(this, this._onButtonReleased),
                                        false);
        }
    }
    else
        alert("Your browser does not support interaction.");
}

WebCanvas.prototype._onButtonPressed = function(event) {
    if (this.locked) return;

    // this can occur with an iPhone/iTouch when we try to drag two fingers
    // on the canvas, causing a second smaller canvas to appear
    if (this.buttonPressed) return;

    this.buttonPressed = true;

    var position = this._getRelativePosition(event);

    var point = new Point();
    point.x = Math.round(position.x * this.real2internal_scalex);
    point.y = Math.round(position.y * this.real2internal_scaley);

    this.ctx.save();
    this.ctx.scale(this.internal2real_scalex, this.internal2real_scaley);
    this._withHandwritingLine();
    this.ctx.beginPath();
    this.ctx.moveTo(point.x, point.y);

    var now = new Date();

    if (this.writing.getNStrokes() == 0) {
        this.first_point_time = now.getTime();
        point.timestamp = 0;
    }
    else {
        if (this.first_point_time == null) {
            /* in the case we add strokes to an imported character */
            this.first_point_time = now.getTime() -
                                    this.writing.getDuration() - 50;
        }

        point.timestamp = now.getTime() - this.first_point_time;
    }

    this.writing.moveToPoint(point);
}

WebCanvas.prototype._onButtonReleased = function(event) {
    if (this.locked) return;

    if (this.buttonPressed) {
        this.buttonPressed = false;
        this.ctx.restore();

        /* Added for tests only. Smoothing should be performed on a copy. */
        if (this.writing.getNStrokes() > 0){
            this.writing.getStrokes()[this.writing.getNStrokes() - 1].smooth();
            this.draw();
        }
    }
}

WebCanvas.prototype._onMove = function(event) {
    if (this.locked) return;

    if (this.buttonPressed) {
        var position = this._getRelativePosition(event);

        var point = new Point();
        point.x = Math.round(position.x * this.real2internal_scalex);
        point.y = Math.round(position.y * this.real2internal_scaley);

        this.ctx.lineTo(point.x, point.y);
        this.ctx.stroke();

        var now = new Date();

        point.timestamp = now.getTime() - this.first_point_time;

        this.writing.lineToPoint(point);
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

    return {"x":x,"y":y};
}

WebCanvas.prototype._drawWriting = function(length) {
    var nstrokes = this.writing.getNStrokes();

    if (!length) length = nstrokes;

    if (nstrokes > 0) {
        var strokes = this.writing.getStrokes();

        this.ctx.save();

        this._withHandwritingLine();

        for(var i = 0; i < length; i++) {
            var stroke = strokes[i];

            var first_point = stroke.getPoints()[0];

            this.ctx.beginPath();

            this.ctx.moveTo(first_point.x, first_point.y);

            for (var j = 1; j < stroke.getNPoints(); j++) {
                var point = stroke.getPoints()[j];

                this.ctx.lineTo(point.x, point.y);
            }

            this.ctx.stroke();
        }

        this.ctx.restore();

    }
}

WebCanvas.prototype._drawWritingAnimation = function(default_speed) {
    var nstrokes = this.writing.getNStrokes();

    if (nstrokes > 0) {
        var strokes = this.writing.getStrokes();

        this.ctx.save();
        this.ctx.scale(this.internal2real_scalex, this.internal2real_scaley);
        this._withStrokeLine();

        var currstroke = 0;
        var currpoint = 0;
        var state = this.getLocked();
        this.setLocked(true);
        var webcanvas = this; // this inside _onAnimate doesn't refer to the web canvas

        _onAnimate = function() {

            var point = strokes[currstroke].getPoints()[currpoint];

            if (currpoint == 0) {
                webcanvas.ctx.beginPath();
                webcanvas.ctx.moveTo(point.x, point.y);
            }
            else {
                webcanvas.ctx.lineTo(point.x, point.y);
                webcanvas.ctx.stroke();
            }

            if (strokes[currstroke].getNPoints() == currpoint + 1) {
                // if we reach the stroke last point

                currpoint = 0;
                currstroke += 1;

                // redraw completely the strokes we have
                webcanvas._drawBackground();
                webcanvas._drawAxis();
                webcanvas._drawWriting(currstroke);

                if (strokes.length == currstroke) {
                    // if we reach the last stroke
                    webcanvas.ctx.restore();
                    webcanvas.setLocked(state);
                    return;
                }
                else {
                    // there are still strokes to go...
                }

            }
            else {
                currpoint += 1;
            }

            var delay;

            if (default_speed == null &&
                strokes[0].getPoints()[0].timestamp != null) {

                if (currpoint == 0 && currstroke == 0) {
                    // very first point
                    delay = 0;
                }
                else if (currstroke > 0 && currpoint == 0) {
                    // interstroke duration
                    var t2 = strokes[currstroke].getPoints()[0].timestamp;
                    var last_stroke = strokes[currstroke - 1].getPoints();
                    var t1 = last_stroke[last_stroke.length - 1].timestamp;
                    delay = (t2 - t1);
                }
                else {
                    var pts = strokes[currstroke].getPoints()
                    delay = pts[currpoint].timestamp -
                            pts[currpoint-1].timestamp;
                }
            }
            else
                delay = default_speed;

            setTimeout(_onAnimate, delay);
        }

        _onAnimate.call();
    }
}

WebCanvas.prototype.getWriting = function() {
    return this.writing;
}

WebCanvas.prototype.setWriting = function(w) {
    if (this.locked) return;

    this.writing = w;
    this.draw();
}

WebCanvas.prototype.clear = function() {
    if (this.locked) return;

    this.setWriting(new Writing());
}

WebCanvas.prototype.draw = function() {
    this.ctx.save();

    this.ctx.scale(this.internal2real_scalex, this.internal2real_scaley);

    this._drawBackground();
    this._drawAxis();

    this._drawWriting();

    this.ctx.restore();
}

WebCanvas.prototype.replay = function(speed) {
    if (this.locked) return;

    this.ctx.save();

    this.ctx.scale(this.internal2real_scalex, this.internal2real_scaley);

    this._drawBackground();
    this._drawAxis();

    this.ctx.restore();

    this._drawWritingAnimation(speed);
}

WebCanvas.prototype.revertStroke = function() {
    if (this.locked) return;

    if (this.writing.getNStrokes() > 0) {
        this.writing.removeLastStroke();
        this.draw();
    }
}

WebCanvas.prototype.getLocked = function() {
    return this.locked;
}

WebCanvas.prototype.setLocked = function(locked) {
    this.locked = locked;
}

WebCanvas.prototype.toDataURL = function(contentType) {
    if (this.locked) return;

    if (this.canvas.toDataURL) {
        return this.canvas.toDataURL(contentType);
    }
    else
        return null;
}

WebCanvas.prototype.toPNG = function() {
    return this.toDataURL("image/png");
}

WebCanvas.prototype.smooth = function() {
    if (this.locked) return;

    if (this.writing.getNStrokes() > 0) {
        this.writing.smooth();
        this.draw();
    }
}

/* ankimobile.js */
function add_canvas (id) {
    var parent_element = document.getElementById(id);
    if (!parent_element) {
        return;
    }

    parent_element.innerHTML = '<canvas id="ianki_webcanvas" height="250" width="250">canvas</canvas><ul class="canvas_links"> <li><a href="#" onclick="document.webcanvas.clear();">clear</a></li> <li><a href="#" onclick="document.webcanvas.revertStroke();">undo stroke</a></li> <li><a href="#" onclick="document.webcanvas.replay();">replay</a></li></ul>';

    /* stop bubbling the click events up to AnkiMobile's tap handlers */
    parent_element.onclick = function () {
        window.event.stopPropagation();
    };

    document.webcanvas = null;
    var canvas = document.getElementById("ianki_webcanvas");
    if (canvas.getContext) {
        document.webcanvas = new WebCanvas(canvas);
        document.webcanvas.draw();
    }
}

Ti.App.addEventListener("showQuestion1", function () { add_canvas("canvas") })
Ti.App.addEventListener("showQuestion2", function () { add_canvas("canvas") })
'''
