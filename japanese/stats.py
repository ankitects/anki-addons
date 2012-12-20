# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# Used/unused kanji list code originally by 'LaC'
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

import unicodedata
from anki.hooks import addHook
from anki.utils import ids2str, splitFields
from aqt import mw
from aqt.webview import AnkiWebView
from aqt.qt import *
from aqt.utils import restoreGeom, saveGeom

# look for kanji in these fields
srcFields = ["Expression", "Kanji"]

def isKanji(unichar):
    try:
        return unicodedata.name(unichar).find('CJK UNIFIED IDEOGRAPH') >= 0
    except ValueError:
        # a control character
        return False

class KanjiStats(object):

    def __init__(self, col, wholeCollection):
        self.col = col
        if wholeCollection:
            self.lim = ""
        else:
            self.lim = " and c.did in %s" % ids2str(self.col.decks.active())
        self._gradeHash = dict()
        for (name, chars), grade in zip(self.kanjiGrades,
                                        xrange(len(self.kanjiGrades))):
            for c in chars:
                self._gradeHash[c] = grade

    def kanjiGrade(self, unichar):
        return self._gradeHash.get(unichar, 0)

    # FIXME: as it's html, the width doesn't matter
    def kanjiCountStr(self, gradename, count, total=0, width=0):
        d = {'count': self.rjustfig(count, width), 'gradename': gradename}
        if total:
            d['total'] = self.rjustfig(total, width)
            d['percent'] = float(count)/total*100
            return _("%(gradename)s: %(count)s of %(total)s (%(percent)0.1f%%).") % d
        else:
            return _("%(count)s %(gradename)s kanji.") % d

    def rjustfig(self, n, width):
        n = unicode(n)
        return n + "&nbsp;" * (width - len(n))

    def genKanjiSets(self):
        self.kanjiSets = [set([]) for g in self.kanjiGrades]
        chars = set()
        for m in self.col.models.all():
            if "japanese" not in m['name'].lower():
                continue
            idxs = []
            for c, name in enumerate(self.col.models.fieldNames(m)):
                for f in srcFields:
                    if name == f:
                        idxs.append(c)
            for row in self.col.db.execute("""
select flds from notes where id in (
select n.id from cards c, notes n
where c.nid = n.id and mid = ? and c.queue > 0
%s) """ % self.lim, m['id']):
                flds = splitFields(row[0])
                for idx in idxs:
                    chars.update(flds[idx])
        for c in chars:
            if isKanji(c):
                self.kanjiSets[self.kanjiGrade(c)].add(c)

    def report(self):
        self.genKanjiSets()
        counts = [(name, len(found), len(all)) \
                  for (name, all), found in zip(self.kanjiGrades, self.kanjiSets)]
        out = ((_("<h1>Kanji statistics</h1>The seen cards in this %s "
                 "contain:") % (self.lim and "deck" or "collection")) +
               "<ul>" +
               # total kanji
               _("<li>%d total unique kanji.</li>") %
               sum([c[1] for c in counts]) +
               # total joyo
               "<li>%s</li>" % self.kanjiCountStr(
            u'Old jouyou',sum([c[1] for c in counts[1:8]]),
            sum([c[2] for c in counts[1:8]])) +
               # total new joyo
               "<li>%s</li>" % self.kanjiCountStr(*counts[8]) +
               # total jinmei (reg)
               "<li>%s</li>" % self.kanjiCountStr(*counts[9]) +
               # total jinmei (var)
               "<li>%s</li>" % self.kanjiCountStr(*counts[10]) +
               # total non-joyo
               "<li>%s</li>" % self.kanjiCountStr(*counts[0]))

        out += "</ul><p/>" + _(u"Jouyou levels:") + "<p/><ul>"
        L = ["<li>" + self.kanjiCountStr(c[0],c[1],c[2], width=3) + "</li>"
             for c in counts[1:8]]
        out += "".join(L)
        out += "</ul>"
        return out

    def missingReport(self, check=None):
        if not check:
            check = lambda x, y: x not in y
            out = _("<h1>Missing</h1>")
        else:
            out = _("<h1>Seen</h1>")
        for grade in range(1, len(self.kanjiGrades)):
            missing = "".join(self.missingInGrade(grade, check))
            if not missing:
                continue
            out += "<h2>" + self.kanjiGrades[grade][0] + "</h2>"
            out += "<font size=+2>"
            out += self.mkEdict(missing)
            out += "</font>"
        return out + "<br/>"

    def mkEdict(self, kanji):
        out = "<font size=+2>"
        while 1:
            if not kanji:
                out += "</font>"
                return out
            # edict will take up to about 10 kanji at once
            out += self.edictKanjiLink(kanji[0:10])
            kanji = kanji[10:]

    def seenReport(self):
        return self.missingReport(lambda x, y: x in y)

    def nonJouyouReport(self):
        out = _("<h1>Non-Jouyou</h1>")
        out += self.mkEdict("".join(self.kanjiSets[0]))
        return out + "<br/>"

    def edictKanjiLink(self, kanji):
        base="http://www.csse.monash.edu.au/~jwb/cgi-bin/wwwjdic.cgi?1MMJ"
        url=base + kanji
        return '<a href="%s">%s</a>' % (url, kanji)

    def missingInGrade(self, gradeNum, check):
        existingKanji = self.kanjiSets[gradeNum]
        totalKanji = self.kanjiGrades[gradeNum][1]
        return [k for k in totalKanji if check(k, existingKanji)]

    kanjiGrades = [
        (u'non-jouyou', ''),
        (u'Grade 1', u'一右雨円王音下火花貝学気休玉金九空月犬見五口校左三山四子糸字耳七車手十出女小上森人水正生青石赤先千川早草足村大男竹中虫町天田土二日入年白八百文本名木目夕立力林六'),
        (u'Grade 2', u'引羽雲園遠黄何夏家科歌画会回海絵外角楽活間丸岩顔帰汽記弓牛魚京強教近兄形計元原言古戸午後語交光公工広考行高合国黒今才細作算姉市思止紙寺時自室社弱首秋週春書少場色食心新親図数星晴声西切雪線船前組走多太体台谷知地池茶昼朝長鳥直通弟店点電冬刀東当答頭同道読内南肉馬買売麦半番父風分聞米歩母方北妹毎万明鳴毛門夜野矢友曜用来理里話'),
        (u'Grade 3', u'悪安暗委意医育員飲院運泳駅央横屋温化荷界開階寒感漢館岸期起客宮急球究級去橋業局曲銀区苦具君係軽決血研県庫湖向幸港号根祭坂皿仕使始指死詩歯事持次式実写者主取守酒受州拾終習集住重宿所暑助勝商昭消章乗植深申真神身進世整昔全想相送息速族他打対待代第題炭短談着柱注丁帳調追定庭笛鉄転登都度島投湯等豆動童農波配倍箱畑発反板悲皮美鼻筆氷表病秒品負部服福物平返勉放味命面問役薬油有由遊予様洋羊葉陽落流旅両緑礼列練路和'),
        (u'Grade 4', u'愛案以位囲胃衣印栄英塩億加果課貨芽改械害街各覚完官管観関願喜器希旗機季紀議救求泣給挙漁競共協鏡極訓軍郡型径景芸欠結健建験固候功好康航告差最菜材昨刷察札殺参散産残司史士氏試児治辞失借種周祝順初唱松焼照省笑象賞信臣成清静席積折節説戦浅選然倉巣争側束続卒孫帯隊達単置仲貯兆腸低停底的典伝徒努灯働堂得特毒熱念敗梅博飯費飛必標票不付夫府副粉兵別変辺便包法望牧末満未脈民無約勇要養浴利陸料良量輪類令例冷歴連労老録'),
        (u'Grade 5', u'圧易移因営永衛液益演往応恩仮価可河過賀解快格確額刊幹慣眼基寄規技義逆久旧居許境興均禁句群経潔件券検険減現限個故護効厚構耕講鉱混査再妻採災際在罪財桜雑賛酸師志支枝資飼似示識質舎謝授修術述準序承招証常情条状織職制勢性政精製税績責接設絶舌銭祖素総像増造則測属損態貸退団断築張提程敵適統導銅徳独任燃能破判版犯比肥非備俵評貧婦富布武復複仏編弁保墓報豊暴貿防務夢迷綿輸余預容率略留領'),
        (u'Grade 6', u'異遺域宇映延沿我灰拡閣革割株巻干看簡危揮机貴疑吸供胸郷勤筋敬系警劇激穴憲権絹厳源呼己誤后孝皇紅鋼降刻穀骨困砂座済裁策冊蚕姿私至視詞誌磁射捨尺若樹収宗就衆従縦縮熟純処署諸除傷将障城蒸針仁垂推寸盛聖誠宣専泉洗染善創奏層操窓装臓蔵存尊宅担探誕暖段値宙忠著庁潮頂賃痛展党糖討届難乳認納脳派俳拝背肺班晩否批秘腹奮並閉陛片補暮宝訪亡忘棒枚幕密盟模訳優郵幼欲翌乱卵覧裏律臨朗論'),
        (u'JuniorHS', u'亜哀握扱依偉威尉慰為維緯違井壱逸稲芋姻陰隠韻渦浦影詠鋭疫悦謁越閲宴援炎煙猿縁鉛汚凹奥押欧殴翁沖憶乙卸穏佳嫁寡暇架禍稼箇華菓蚊雅餓介塊壊怪悔懐戒拐皆劾慨概涯該垣嚇核殻獲穫較郭隔岳掛潟喝括渇滑褐轄且刈乾冠勘勧喚堪寛患憾換敢棺款歓汗環甘監緩缶肝艦貫還鑑閑陥含頑企奇岐幾忌既棋棄祈軌輝飢騎鬼偽儀宜戯擬欺犠菊吉喫詰却脚虐丘及朽窮糾巨拒拠虚距享凶叫峡恐恭挟況狂狭矯脅響驚仰凝暁斤琴緊菌襟謹吟駆愚虞偶遇隅屈掘靴繰桑勲薫傾刑啓契恵慶憩掲携渓継茎蛍鶏迎鯨撃傑倹兼剣圏堅嫌懸献肩謙賢軒遣顕幻弦玄孤弧枯誇雇顧鼓互呉娯御悟碁侯坑孔巧恒慌抗拘控攻更江洪溝甲硬稿絞綱肯荒衡貢購郊酵項香剛拷豪克酷獄腰込墾婚恨懇昆紺魂佐唆詐鎖債催宰彩栽歳砕斎載剤咲崎削搾索錯撮擦傘惨桟暫伺刺嗣施旨祉紫肢脂諮賜雌侍慈滋璽軸執湿漆疾芝赦斜煮遮蛇邪爵酌釈寂朱殊狩珠趣儒寿需囚愁秀臭舟襲酬醜充柔汁渋獣銃叔淑粛塾俊瞬准循旬殉潤盾巡遵庶緒叙徐償匠升召奨宵尚床彰抄掌昇晶沼渉焦症硝礁祥称粧紹肖衝訟詔詳鐘丈冗剰壌嬢浄畳譲醸錠嘱飾殖触辱伸侵唇娠寝審慎振浸紳薪診辛震刃尋甚尽迅陣酢吹帥炊睡粋衰遂酔随髄崇枢据杉澄瀬畝是姓征牲誓請逝斉隻惜斥析籍跡拙摂窃仙占扇栓潜旋繊薦践遷鮮漸禅繕塑措疎礎租粗訴阻僧双喪壮捜掃挿曹槽燥荘葬藻遭霜騒憎贈促即俗賊堕妥惰駄耐怠替泰滞胎袋逮滝卓択拓沢濯託濁諾但奪脱棚丹嘆淡端胆鍛壇弾恥痴稚致遅畜蓄逐秩窒嫡抽衷鋳駐弔彫徴懲挑眺聴超跳勅朕沈珍鎮陳津墜塚漬坪釣亭偵貞呈堤帝廷抵締艇訂逓邸泥摘滴哲徹撤迭添殿吐塗斗渡途奴怒倒凍唐塔悼搭桃棟盗痘筒到謄踏逃透陶騰闘洞胴峠匿督篤凸突屯豚曇鈍縄軟尼弐如尿妊忍寧猫粘悩濃把覇婆廃排杯輩培媒賠陪伯拍泊舶薄迫漠爆縛肌鉢髪伐罰抜閥伴帆搬畔繁般藩販範煩頒盤蛮卑妃彼扉披泌疲碑罷被避尾微匹姫漂描苗浜賓頻敏瓶怖扶敷普浮符腐膚譜賦赴附侮舞封伏幅覆払沸噴墳憤紛雰丙併塀幣弊柄壁癖偏遍舗捕穂募慕簿倣俸奉峰崩抱泡砲縫胞芳褒邦飽乏傍剖坊妨帽忙房某冒紡肪膨謀僕墨撲朴没堀奔翻凡盆摩磨魔麻埋膜又抹繭慢漫魅岬妙眠矛霧婿娘銘滅免茂妄猛盲網耗黙戻紋厄躍柳愉癒諭唯幽悠憂猶裕誘雄融与誉庸揚揺擁溶窯謡踊抑翼羅裸頼雷絡酪欄濫吏履痢離硫粒隆竜慮虜了僚寮涼猟療糧陵倫厘隣塁涙累励鈴隷零霊麗齢暦劣烈裂廉恋錬炉露廊楼浪漏郎賄惑枠湾腕'),
        (u'New jouyou', u'挨宛闇椅畏萎茨咽淫臼唄餌怨艶旺岡臆俺苛牙崖蓋骸柿顎葛釜鎌瓦韓玩伎畿亀僅巾錦駒串窟熊稽詣隙桁拳鍵舷股虎乞勾喉梗頃痕沙挫塞采阪埼柵拶斬鹿叱嫉腫呪蹴拭尻芯腎須裾凄醒戚脊煎羨腺詮膳曽狙遡爽痩捉袖遜汰唾堆戴誰旦綻酎捗椎潰爪鶴諦溺填貼妬賭藤憧瞳栃頓奈那謎鍋匂虹捻罵剥箸斑氾汎眉膝肘媛阜蔽蔑蜂貌頬睦勃昧枕蜜冥麺餅冶弥湧妖沃嵐藍梨璃侶瞭瑠呂賂弄麓脇丼傲刹哺喩嗅嘲毀彙恣惧慄憬拉摯曖楷鬱璧瘍箋籠緻羞訃諧貪踪辣錮'),
        (u'Jinmeiyou (regular)', u'丑丞乃之乎也云亘亙些亦亥亨亮仔伊伍伽佃佑伶侃侑俄俠俣俐倭俱倦倖偲傭儲允兎兜其冴凌凜凛凧凪凰凱函劉劫勁勿匡廿卜卯卿厨厩叉叡叢叶只吾吞吻哉啄哩喬喧喰喋嘩嘉嘗噌噂圃圭坐尭堯坦埴堰堺堵塙塡壕壬夷奄奎套娃姪姥娩嬉孟宏宋宕宥寅寓寵尖尤屑峨峻崚嵯嵩嶺巌巖已巳巴巷巽帖幌幡庄庇庚庵廟廻弘弛彌彗彦彪彬徠忽怜恢恰恕悌惟惚悉惇惹惺惣慧憐戊或戟托按挺挽掬捲捷捺捧掠揃摑摺撒撰撞播撫擢孜敦斐斡斧斯於旭昂昊昏昌昴晏晃晄晒晋晟晦晨智暉暢曙曝曳曾朋朔杏杖杜李杭杵杷枇柑柴柘柊柏柾柚桧檜栞桔桂栖桐栗梧梓梢梛梯桶梶椛梁棲椋椀楯楚楕椿楠楓椰楢楊榎樺榊榛槙槇槍槌樫槻樟樋橘樽橙檎檀櫂櫛櫓欣欽歎此殆毅毘毬汀汝汐汲沌沓沫洸洲洵洛浩浬淵淳渚淀淋渥湘湊湛溢滉溜漱漕漣澪濡瀕灘灸灼烏焰焚煌煤煉熙燕燎燦燭燿爾牒牟牡牽犀狼猪獅玖珂珈珊珀玲琢琉瑛琥琶琵琳瑚瑞瑶瑳瓜瓢甥甫畠畢疋疏瘦皐皓眸瞥矩砦砥砧硯碓碗碩碧磐磯祇祢禰祐禄祿禎禱禽禾秦秤稀稔稟稜穣穰穿窄窪窺竣竪竺竿笈笹笙笠筈筑箕箔篇篠簞簾籾粥粟糊紘紗紐絃紬絆絢綺綜綴緋綾綸縞徽繫繡纂纏羚翔翠耀而耶耽聡肇肋肴胤胡脩腔膏臥舜舵芥芹芭芙芦苑茄苔苺茅茉茸茜莞荻莫莉菅菫菖萄菩萌萠萊菱葦葵萱葺萩董葡蓑蒔蒐蒼蒲蒙蓉蓮蔭蔣蔦蓬蔓蕎蕨蕉蕃蕪薙蕾蕗藁薩蘇蘭蝦蝶螺蟬蟹蠟衿袈袴裡裟裳襖訊訣註詢詫誼諏諄諒謂諺讃豹貰賑赳跨蹄蹟輔輯輿轟辰辻迂迄辿迪迦這逞逗逢遥遙遁遼邑祁郁鄭酉醇醐醍醬釉釘釧鋒鋸錐錆錫鍬鎧閃閏閤阿陀隈隼雀雁雛雫霞靖鞄鞍鞘鞠鞭頁頌頗頰顚颯饗馨馴馳駕駿驍魁魯鮎鯉鯛鰯鱒鱗鳩鳶鳳鴨鴻鵜鵬鷗鷲鷺鷹麒麟麿黎黛鼎'),
        (u'Jinmeiyou (variant)', u'亞惡爲衞谒緣應櫻奧橫溫價祸壞懷樂渴卷陷寬氣僞戲虛峽狹曉勳薰惠揭鷄藝擊縣儉劍險圈檢顯驗嚴廣恆黃國黑碎雜兒濕壽收從澁獸縱緖敍將涉燒獎條狀乘淨剩疊孃讓釀眞寢愼盡粹醉穗瀨齊靜攝專戰纖禪壯爭莊搜巢裝騷增藏臟卽帶滯單團彈晝鑄廳徵聽鎭轉傳燈盜稻德拜賣髮拔晚祕拂佛步飜每默藥與搖樣謠來賴覽龍綠淚壘曆歷鍊郞錄')
        ]

def genKanjiStats():
    wholeCollection = mw.state == "deckBrowser"
    s = KanjiStats(mw.col, wholeCollection)
    rep = s.report()
    rep += s.seenReport()
    rep += s.missingReport()
    rep += s.nonJouyouReport()
    return rep

def onKanjiStats():
    mw.progress.start(immediate=True)
    rep = genKanjiStats()
    d = QDialog(mw)
    l = QVBoxLayout()
    l.setMargin(0)
    w = AnkiWebView()
    l.addWidget(w)
    w.stdHtml(rep)
    bb = QDialogButtonBox(QDialogButtonBox.Close)
    l.addWidget(bb)
    bb.connect(bb, SIGNAL("rejected()"), d, SLOT("reject()"))
    d.setLayout(l)
    d.resize(500, 400)
    restoreGeom(d, "kanjistats")
    mw.progress.finish()
    d.exec_()
    saveGeom(d, "kanjistats")

def createMenu():
    a = QAction(mw)
    a.setText("Kanji Stats")
    mw.form.menuTools.addAction(a)
    mw.connect(a, SIGNAL("triggered()"), onKanjiStats)

createMenu()
