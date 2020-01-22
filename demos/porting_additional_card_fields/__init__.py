"""
Add-on for Anki 2.1: Additional Card Fields for the reviewer

Copyright: (c) 2018- ijgnd
           (c) 2017 https://www.reddit.com/user/Dayjaby/
           (c) 2012- HSSM (Advanced Browser)
           (c) 2016 Dmitry Mikheev, http://finpapa.ucoz.net/
           (c) Damien Elmes <anki@ichi2.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


This addon is a modification of "Additional Card Fields",
https://ankiweb.net/shared/info/441235634

"Additional Card Fields" also contains code from the add-on
"_Young_Mature_Card_Fields" which from
  https://ankiweb.net/shared/info/1751807495
  https://github.com/ankitest/anki-musthave-addons-by-ankitest
"""

import collections
import copy
import re
import time

from anki import version as ankiversion
from anki.collection import _Collection
from anki.hooks import wrap
from anki.stats import CardStats
from anki.template.template import *
from anki.utils import fmtTimeSpan, isWin, stripHTML
from aqt import mw
from aqt.utils import tooltip


def gc(arg, fail=False):
    return mw.addonManager.getConfig(__name__).get(arg, fail)


# this is function timefn is from anki from anki/stats.py which is at
# https://github.com/dae/anki/blob/master/anki/stats.py#L77 and
def timefn(tm):
    str = ""
    if tm >= 60:
        str = fmtTimeSpan((tm / 60) * 60, short=True, point=-1, unit=1)
    if tm % 60 != 0 or not str:
        str += fmtTimeSpan(tm % 60, point=2 if not str else -1, short=True)
    return str


# from Advanced Browser - overdue_days
# https://github.com/hssm/advanced-browser/blob/master/advancedbrowser/advancedbrowser/custom_fields.py#L225
def valueForOverdue(odid, queue, type, due, d):
    if odid or queue == 1:
        return
    elif queue == 0 or type == 0:
        return
    elif queue in (2, 3) or (type == 2 and queue < 0):
        diff = due - d.sched.today
        if diff < 0:
            return diff * -1
        else:
            return


def external_file_link(card, model):
    field_for_filename = ""
    field_for_page = ""
    # import user settings for field names from other add-on
    try:
        field_for_filename = __import__(
            "1994996371"
        ).open_in_external.field_for_filename
        field_for_page = __import__("1994996371").open_in_external.field_for_page
    except:
        return ""
    if all([field_for_filename, field_for_page]):
        note = mw.col.getNote(card.nid)
        for i, f in enumerate(note.model()["flds"]):
            if f["name"] == field_for_filename:
                file = note.fields[i]
            if f["name"] == field_for_page:
                page = note.fields[i]
        try:
            file
            page
        except:
            return ""
        f = stripHTML(file)
        p = stripHTML(page)
        pycmd = f"open_external_filesüöäüöä{f}üöäüöä{p}"
        if p:
            text = f"{f} , {p}"
        else:
            text = f"{f}"
        out = f"""<a href='javascript:pycmd("{pycmd}");'>{text}</a>"""
        return out


# this is a modification of a function from anki/collection.py
def _renderQA(self, data, qfmt=None, afmt=None, _old=None):
    """
    this function overwrites a function from collection.py
    The beginning of this function reads:
        "Returns hash of id, question, answer."
        # data is [cid, nid, mid, did, ord, tags, flds]
        # unpack fields and create dict
    """
    data = list(data)
    origFieldMap = self.models.fieldMap
    model = self.models.get(data[2])
    if data[0] is None:
        card = None
    elif data[0] == 1:
        card = None
    else:
        try:
            card = self.getCard(data[0])
        except:
            card = None

    origdata = copy.copy(data)
    data[6] += "\x1f"

    addInfo = collections.OrderedDict()

    if card is not None:
        r = mw.reviewer
        d = mw.col
        cs = CardStats(d, r.card)

        if card.odid:
            conf = d.decks.confForDid(card.odid)
        else:
            conf = d.decks.confForDid(card.did)

        (first, last, cnt, total) = self.db.first(
            "select min(id), max(id), count(), sum(time)/1000 from revlog where cid = :id",
            id=card.id,
        )

        if cnt:
            addInfo["FirstReview"] = time.strftime(
                "%a, %d %b %Y %H:%M:%S", time.localtime(first / 1000)
            )
            addInfo["LastReview"] = time.strftime(
                "%a, %d %b %Y %H:%M:%S", time.localtime(last / 1000)
            )

            # https://docs.python.org/2/library/datetime.html  #todo
            addInfo["TimeAvg"] = timefn(total / float(cnt))
            addInfo["TimeTotal"] = timefn(total)

            cOverdueIvl = valueForOverdue(card.odid, card.queue, card.type, card.due, d)
            if cOverdueIvl:
                addInfo["overdue_fmt"] = (
                    str(cOverdueIvl) + " day" + ("s" if cOverdueIvl > 1 else "")
                )
                addInfo["overdue_days"] = str(cOverdueIvl)

        model = self.models.get(data[2])
        addInfo["external_file_link"] = external_file_link(card, model)

        addInfo["Ord"] = data[4]
        addInfo["Did"] = card.did
        addInfo["Due"] = card.due
        addInfo["Id"] = card.id
        addInfo["Ivl"] = card.ivl
        addInfo["Queue"] = card.queue
        addInfo["Reviews"] = card.reps
        addInfo["Lapses"] = card.lapses
        addInfo["Type"] = card.type
        addInfo["Nid"] = card.nid
        addInfo["Mod"] = time.strftime("%Y-%m-%d", time.localtime(card.mod))
        addInfo["Usn"] = card.usn
        addInfo["Factor"] = card.factor
        addInfo["Ease"] = int(card.factor / 10)

        addInfo["Review?"] = "Review" if card.type == 2 else ""
        addInfo["New?"] = "New" if card.type == 0 else ""
        addInfo["Learning?"] = "Learning" if card.type == 1 else ""
        addInfo["TodayLearning?"] = (
            "Learning" if card.type == 1 and card.queue == 1 else ""
        )
        addInfo["DayLearning?"] = (
            "Learning" if card.type == 1 and card.queue == 3 else ""
        )

        addInfo["Young"] = "Young" if card.type == 2 and card.ivl < 21 else ""
        addInfo["Mature"] = "Mature" if card.type == 2 and card.ivl > 20 else ""

        if gc("make_deck_options_available", False):
            addInfo["Options_Group_ID"] = conf["id"]
            addInfo["Options_Group_Name"] = conf["name"]
            addInfo["Ignore_answer_times_longer_than"] = conf["maxTaken"]
            addInfo["Show_answer_time"] = conf["timer"]
            addInfo["Auto_play_audio"] = conf["autoplay"]
            addInfo["When_answer_shown_replay_q"] = conf["replayq"]
            addInfo["is_filtered_deck"] = conf["dyn"]
            addInfo["deck_usn"] = conf["usn"]
            addInfo["deck_mod_time"] = conf["mod"]
            addInfo["new__steps_in_minutes"] = conf["new"]["delays"]
            addInfo["new__order_of_new_cards"] = conf["new"]["order"]
            addInfo["new__cards_per_day"] = conf["new"]["perDay"]
            addInfo["graduating_interval"] = conf["new"]["ints"][0]
            addInfo["easy_interval"] = conf["new"]["ints"][1]
            addInfo["Starting_ease"] = int(conf["new"]["initialFactor"] / 10)
            addInfo["bury_related_new_cards"] = conf["new"]["bury"]
            addInfo["MaxiumReviewsPerDay"] = conf["rev"]["perDay"]
            addInfo["EasyBonus"] = int(100 * conf["rev"]["ease4"])
            addInfo["IntervalModifier"] = int(100 * conf["rev"]["ivlFct"])
            addInfo["MaximumInterval"] = conf["rev"]["maxIvl"]
            addInfo["bur_related_reviews_until_next_day"] = conf["rev"]["bury"]
            addInfo["lapse_learning_steps"] = conf["lapse"]["delays"]
            addInfo["lapse_new_ivl"] = int(100 * conf["lapse"]["mult"])
            addInfo["lapse_min_ivl"] = conf["lapse"]["minInt"]
            addInfo["lapse_leech_threshold"] = conf["lapse"]["leechFails"]
            addInfo["lapse_leech_action"] = conf["lapse"]["leechAction"]
            addInfo["Date_Created"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(card.nid / 1000)
            )

        # add your additional fields here

    # for debugging quickly add all values to template
    tt = " <table>" + "\n"
    for k in addInfo.keys():
        tt += (
            '<tr><td align="left">%s </td><td align="left">  {{info::%s}}  </td></tr> +\n'
            % (k, k)
        )
    tt += " </table>" + "\n"
    addInfo["allfields"] = tt

    additionalFields = [""] * len(addInfo)

    for i, v in enumerate(addInfo.values()):
        additionalFields[i] = str(v)

    data[6] += "\x1f".join(additionalFields)  # \x1f is used as a field separator

    def tmpFieldMap(m):
        "Mapping of field name -> (ord, field)."
        d = dict((f["name"], (f["ord"], f)) for f in m["flds"])

        newFields = []
        for k in addInfo.keys():
            newFields.append("info::" + k)

        for i, f in enumerate(newFields):
            d[f] = (len(m["flds"]) + i, 0)
        return d

    self.models.fieldMap = tmpFieldMap

    data = tuple(data)
    result = _old(self, data, qfmt, afmt)
    data = origdata
    self.models.fieldMap = origFieldMap
    return result


# this is a modification of a function from anki/collection.py
def previewCards(self, note, type=0, did=None):
    existingTemplates = {c.template()["name"]: c for c in note.cards()}
    if type == 0:
        cms = self.findTemplates(note)
    elif type == 1:
        cms = [c.template().name() for c in note.cards()]
    else:
        cms = note.model()["tmpls"]
    if not cms:
        return []
    cards = []
    for template in cms:
        if template["name"] in existingTemplates:
            card = existingTemplates[template["name"]]
        else:
            # compatibility for 2.1.9+, see https://github.com/ijgnd/anki21__additional_card_fields_during_review/pull/1
            # because of https://github.com/dae/anki/commit/d8f059b570a8f2e99348a8b6c2b521f46bf141ef
            if ankiversion in ["2.1.%d " % d for d in range(0, 9)]:
                card = self._newCard(note, template, 1, flush=False, did=did)
            else:
                card = self._newCard(note, template, 1, flush=False)
        cards.append(card)
    return cards


# maybe need to increase repCount?
# this function is from anki/template/template.py
def render_tags(self, template, context):
    """Renders all the tags in a template for a context."""
    repCount = 0
    while 1:
        if repCount > 200:  # mod
            print("too many replacements")
            break
        repCount += 1

        match = self.tag_re.search(template)
        if match is None:
            break

        tag, tag_type, tag_name = match.group(0, 1, 2)
        tag_name = tag_name.strip()
        try:
            func = modifiers[tag_type]
            replacement = func(self, tag_name, context)
            template = template.replace(tag, replacement)
        except (SyntaxError, KeyError):
            return "{{invalid template}}"

    return template


if gc("increase_repCount", False):
    Template.render_tags = render_tags
_Collection._renderQA = wrap(_Collection._renderQA, _renderQA, "around")
_Collection.previewCards = previewCards
