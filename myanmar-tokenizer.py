#!/usr/bin/env python
# -*- coding=utf-8 -*-

import codecs
from python_utils import utils, task
import sys
import re
import os
import time


'''
缅甸语：Myanmar
参考《A Rule-based Syllable Segmentation of Myanmar Text 》里的规则进行实现
参考文献：http://www.aclweb.org/anthology/I08-3010
http://www.nlpresearch-ucsy.edu.mm/NLP_UCSY/wsandpos.html  # 在线切分
Myanmar Script共计12类，有75个字符组成
其中：
辅音组（Consonants group）：34个辅音字母
中间字符组（Medials group）：4个中间字符
依赖元音组（Dependent Vowels group）：8个元音
Myanmar Sign Virama： is used for stacking consonant letters and it does not have a glyph
用来堆叠辅音字母，他不具有字形
Myanmar Sign Asat： is used in devowelising process (e.g. ဆင်)

There are three dependent various signs in Group F.
F： three dependent various signs 3个依赖多样化的字符

The Group I consists of three independent vowels (ဤ, ဧ, ဪ) and three independent various signs (၌, ၍, ၏).
I： three independent vowels (ဤ, ဧ, ဪ) and three independent various signs (၌, ၍, ၏).The characters in Group I can act as stand-alone syllables.
    独立音节，3个独立元音和3个独立多样化字符

Group E consists of four independent vowels (ဣ, ဥ, ဦ, ဩ) and Myanmar Symbol Aforementioned (၎).
由4个独立元音和1个前导字符

Each of the independent vowels in group E has its own syllable but they can also combine with other signs to form a syllable (e.g. ဥက3⁄4 ာ).
E里的每个独立元音可以有它自己的音节，也可和其他字符组成音节

Myanmar Symbol Aforementioned in Group E can never stand alone and it is always written as ၄င်း as a short form of လည်းေကာင်း .
E里的前导符号永远不能独立，它总是写成4င်း作为လည်းေကာင်း缩写形式。

Myanmar Letter Great Sa is always preceded by a consonant and is never written alone (e.g. မနုဿ ).
Letter Great Sa总是以辅音，从不单独写（如မနုဿ）。

There are ten Myanmar digits in the Digits group.
数字组有10个数字

The group P consists of two Myanmar punctuation marks.
P：2个标点符号

Myanmar script uses white space between phrases, which is taken into account in this study
短语使用空白字符

Category Name   Name                            Glyph                               Unicode Code Point
C               Consonants                      ကခဂဃငစဆဇဈဉညဋဌဍဎဏတ            U+1000...U+1021
                                                ထဒဓနပဖဗဘမယရလဝသဟဠအ
M               Medials                          ျ     ြ     ွ        ှ                 U+103B...U+103E
V               Dependent Vowel Signs            ါ ာ ိ ီ ု ူ ေ ဲ                         U+102B...U+1032
S               Myanmar Sign Virama              ◌                                  U+1039
A               Myanmar Sign Asat                 ်                                  U+103A
F               Dependent Various Signs           ံ ့ း                                U+1036...U+1038
I               Independent Vowels,             ဤ ဧ ဪ                           U+1024; U+1027; U+102A; U+104C;
                Independent Various Signs       ၌ ၍ ၏                               U+104D; U+104F;
E               Independent Vowels,             ဣ ဥ ဦ ဩ                             U+1023; U+1025;U+1026; U+1029;
                Myanmar Symbol Aforementioned   ၎                                   U+104E;
G               Myanmar Letter Great Sa         ဿ                                   U+103F
D               Myanmar Digits                  ၀ ၁ ၂ ၃ ၄ ၅ ၆ ၇ ၈ ၉                 U+1040...U+1049
P               Punctuation Marks               ၊ ။                                     U+104A...U+104B
W               White space                                                         U+0020


Syllable Structure:
音节结构:
A Myanmar syllable consists of one initial consonant, zero or more medials,
一个缅甸音节由一个声母，零个或多个medials，
zero or more vowels and optional dependent various signs.
零个或多个元音和可选的依赖变形字符。
Independent vowels, independent various signs and digits can act as stand-alone syllables.
独立元音，独立各种标志和数字可以作为独立的音节。根据Unicode标准，元音后辅音存储。因此，缅甸元音符号E（U + 1031）之后的辅音存储虽然是摆在辅音渲染（如ေန）。 Medials可以在一个音节中最多出现三次（如ြမôာ）。元音可以在一个音节（如ေစာ）出现两次。在一个音节，第二个辅音可能会与一个AST的devowelising（如ဇင်）。每个在E组独立元音都有自己的音节，但它们也可以与其他标志（辅音，元音依赖，依赖各种标牌）相结合，形成一个音节（如ဣေòန研发，ဥက3/4ာ，ဦး，ေ ïသာင်း）。缅甸脚本的音节结构可以写成BNF（巴科斯范式）如下：
According to the Unicode standard, vowels are stored after the consonant.
Therefore, Myanmar vowel sign E (U+1031) is stored after the consonant
although it is placed before the consonant in rendering (e.g. ေန).
Medials may appear at most three times in a syllable (e.g. ြမôာ).
Medials可以在一个音节中最多出现三次（如ြမôာ）。
Vowels may appear twice in a syllable (e.g. ေစာ).
元音可以在一个音节（如ေစာ）出现两次。
In a syllable, a second consonant may come together with an Asat for devowelising (e.g. ဇင်) .
音节中，第二个辅音可能会与一个Asat的devowelising（如ဇင်）
Each of the independent vowels in group E has its own syllable but they
can also combine with other signs (consonants, dependent vowels, dependent various signs)
to form a syllable (e.g. ဣေòနÐ, ဥက3⁄4 ာ, ဦး, ေïသာင်း ).
E中的每个独立元音都有自己的音节，但他们也可以和其他字符（辅音，依赖元音，依赖变形字符）相结合形成一个音节(e.g. ဣေòနÐ, ဥက3⁄4 ာ, ဦး, ေïသာင်း ).
The syllable structure of Myanmar script can be written in BNF (Backus-Naur Form) as follows:
缅甸脚本的音节结构可以写成BNF（Backus-Naur Form）如下：
Syllable ::= C{M}{V}{F} | C{M}V+ A | C{M}{V}CA[F] | E{V}[CA][F]  | I | D

{} the item may appear zero or more times  {}出现次数>=0
+ the item may appear one or more times    +出现次数>=1
[] the item may appear zero or one time    []出现次数==0 or ==1

A finite state machine or finite state automaton (FSA) can be employed to
demonstrate the syllable structure of Myanmar script.
A finite state machine is a model of behavior composed of a finite number of states,
transitions between those states, and actions.
The starting state is shown by a bold circle and double circles indicate final or accepting states.
The above figure shows a finite state automaton that can realize a Myanmar syllable.
Examples of Myanmar syllables and their equivalent Unicode code points are shown in Table 2.



Syllable Segmentation Rules：
Syllable Segmentation Rules Typically, a syllable boundary can be determined
by comparing pairs of characters to find whether a break is possible or not between them.
通常情况下，一个音节边界可以通过比较字符对来确定是否可以分割或者不在他们之间
However, in some cases it is not sufficient to determine a syllable boundary
by just comparing two characters.
然而某些情况下，由两个字符确定音节边界不够充分

The following sections explain these cases and give examples.
1.Devowelising（去元音读音）：
In one syllable, a consonant may appear twice but the second consonant is
used for the devowelising process in conjunction with an Asat (U+103A MYANMAR SIGN ASAT).
一个音节中，一个辅音可能出现两次，但是第二个辅音用于devowelising过程中，与Asat接合使用

Therefore the character after the second consonant should be further checked for an Asat.
因此，第二个辅音后的字符应该进一步检查Asat。
If the character after the second consonant is an Asat, there should be no syllable break
before the second consonant.
如果第二个辅音后面的字符是Asat，那么第二个辅音之前不能分割

eg: ဆင် =》 ဆ င  ်  (elephant) 前两个都为辅音（C），最后一个为A
            C C A


2.Syllable Chaining：
Subjoined characters are shown by using an invisible Virama sign (U+1039 MYANMAR SIGN VIRAMA)
to indicate that the following character is subjoined and should take a subjoined form.
In this case, if the character after the second consonant is an invisible Virama sign,
there should be no syllable break before the second and third consonant.
在这种情况下，如果第二个辅音后的字符是Virama，那么第二个音节和第三个音节之前不能分隔。
Although there are two syllables in a subjoined form, it is not possible to separate
them in written form and they are therefore treated as one syllable.
eg: ဝတÏု  =>   ဝ တ ◌ ထ ု        (novel)
                C C S C V

3.Kinzi
Kinzi is a special form of devowelised Nga (U+1004 MYANMAR LETTER NGA) with the following
letter underneath, i.e., subjoined.
In this case, if the character after the second consonant is an Asat and the next character
after Asat is an invisible Virama sign (U+1039 MYANMAR SIGN VIRAMA) then there should be no
syllable break before the second and third consonant. Kinzi also consists of two syllables
but it is treated as one syllable in written form.
在这种情况下，如果第二个字符后面是Asat和Asat之后的下一个字符是Virama，那么第二个辅音和
第三个辅音没有分隔，Kinzi同样包含两个音节，但是在书面形式中视为一个音节

eg:မဂüလာ =>  မ င ် ◌ ဂ - လ ာ        (blessing)
              C C A S C - C V

4.Loan Words：外来词
Usage of loan words can be found in Myanmar text.
Although loan words do not follow the Myanmar syllable structure,
虽然外来词不按缅甸语的音节切分规则，
their usage is common and the segmentation rules for these words are considered in this study.
eg：မားစ်ðဂိုဟ်  =>   မ ာ း စ ် - ဂ ြ ိ ု ဟ ် (Mars)
                    C V F C A - C M V V C A

5.Great Sa
There should be no syllable break before great Sa (U+103F MYANMAR LETTER GREAT SA)
as great Sa acts like a stacked သÛ and devowelises the preceding consonant.
eg:  မနုဿ =>  မ - န ု ဿ  (human)
               C - C V G

6.Contractions
There are usages of double-acting consonants in Myanmar text.
The double-acting consonant acts as both the final consonant of one syllable and the
initial consonant of the following syllable. There are two syllables in a contracted
form but they cannot be segmented in written form and there should be no syllable break
between them.
eg:  ေယာက်ျား   =>   ယ ေ  ာ က ်  ျ ာ း  (man)
                     C  V  V C A M V F

Table 3. Syllable Break Status and Definition
Break Status        Definition
-1                  Illegal spelling order
 0                  No break after 1st character
 1                  Break after 1st character
 2                  Break after 2nd character
 3                  Break after 3rd character
 4                  Break after 4th character

Implementation 实现:
Syllable segmentation rules are presented in the form of letter sequence tables (Tables 4-6).
音节切分规则呈现在字母序列表（表4-6）的形式。
The tables were created by comparing each pair of character categories.
通过比较字符对类别来创建表。
However, it is not sufficient to determine all syllable breaks by comparing only two characters.
然而，通过比较仅两个字符是不足以确定所有音节的。
In some cases, a maximum of four consecutive characters need to be considered to determine
a possible syllable boundary.
在一些情况下，最多需要连续考虑四个字符，以确定一个可能的音节分隔
Two additional letter sequence tables were created for this purpose (Tables 5 and 6).
为此目的创建（表5和6）两个附加的字母顺序表。
Table 4 defines the break status for each pair of two consecutive characters.
表4定义了每对的两个连续的字符的分隔状态。
Table 5 and 6 define the break status for each pair of three and four consecutive characters, respectively.
表5和6限定​​为每一对分别考虑三个和四个连续字符来确定分隔状态。
The symbol U in the Table 4 and 5 stands for undefined cases.
符号U在表4和5代表不确定的情况。
Cases undefined in Table 4 are defined in the Table 5, and those undefined in Table 5 are then defined in Table 6.
表4中未定义的在表5中定义，和那些在表5中未定义的在表6中定义。
The syllable segmentation program obtains the break status for each pair of characters by
comparing the input character sequence with the letter sequence tables.
音节分词程序通过与字母顺序表比较输入字符序列获得用于每对字符的分隔状态。
The syllable break status and definitions are shown in Table 3.
音节分隔状态和定义见表3。
The break status -1 indicates a breach of canonical spelling order and a question mark is appended after the ambiguous character pair.
分隔状态-1表示违反规范的拼写顺序和模糊的字符对后一个问号被追加。
The status 0 means there should be no syllable break after the first character.
状态0表示应该是第一个字符后无音节的分隔。
For break cases, a syllable breaking symbol (i.e. B in the flowchart) is inserted at each syllable boundary of the input string.
对于分隔的情况，一个音节分隔符号（i.e. 流程图里的B）作为每一个音节的边界
The syllable segmentation process is shown in the flowchart in Figure 2.


Method and Results：
A syllable segmentation program was developed to evaluate the algorithm and segmentation rules.


The program accepts the Myanmar text string and shows the output string in a segmented form.


The program converts the input text string into equivalent sequence of category form
(e.g. CMCACV for ြမန်မာ) and compares the converted character sequence with the letter
sequence tables to determine syllable boundaries.
程序中的输入文本串转换成类形式的等效序列（如CMCACV为ြမန်မာ），并比较以字母顺序表的
转换的字符序列，以确定音节边界。

A syllable segmented Myanmar text string is shown as the output of the program.
The symbol "|" is used to represent the syllable breaking point.
符号“|”用于表示音节分隔符。
In order to evaluate the accuracy of the algorithm, a training corpus was developed
by extracting 11,732 headwords from Myanmar Orthography (Myanmar Language Commission, 2003).
The corpus contains a total of 32,238 Myanmar syllables.
为了评估算法的准确性，训练语料是由来自缅甸正字（缅甸语言文字工作委员会，2003）
抽取11732词条开发。该语料库共收录了32238缅甸音节。
These syllables were tested in the program and the segmented results were manually checked.
这些音节均在程序测试和分割结果进行人工检查。
The results showed 12 errors of incorrectly segmented syllables, thus achieving
accuracy of 99.96% for segmentation.
结果显示，不正确地分割音节12错误，从而实现了99.96％的准确度进行分割。
The few errors occur with the Myanmar Letter Great Sa ‘ဿ’ and the Independent Vowel ‘ဥ’.
缅甸字符Great Sa‘ဿ’和独立元音‘ဥ’出现了一些错误。
The errors can be fixed by updating the segmentation rules of these two characters in letter sequence tables.
这些错误可以固定通过更新这两个字符的分割规则字母序列表。

'''

# 缅甸语字符集范围：Unicode 8.0
MyanmarCharacterCode = [(u'\u1000', u'\u109F'),  # Myanmar
                        (u'\uAA60', u'\uAA7F'),  # Myanmar Extended-A
                        (u'\uA9E0', u'\uA9FF'),  # Myanmar Extended-B
                        ]


class MyanmarTokenizer:
    # Category name
    _CATEGORY_NAMES = ['C', 'M', 'V', 'S', 'A', 'F', 'I', 'E', 'G', 'D', 'P', 'W']
    # Category's Unicode Code Point
    _CATEGORY_RANGE = [
        ['C', range(0x1000, 0x1021 + 1)],  # Consonants
        ['M', range(0x103B, 0x103E + 1)],  # Medials
        ['V', range(0x102B, 0x1032 + 1)],  # Dependent Vowel Signs
        ['S', [0x1039]],  # Myanmar Sign Virama
        ['A', [0x103A]],  # Myanmar Sign Asat
        ['F', range(0x1036, 0x1038 + 1)],  # Dependent Various Signs
        ['I', [0x1024, 0x1027, 0x102A, 0x104C, 0x104D, 0x104F]],  # Independent Vowels,Independent Various Signs
        ['E', [0x1023, 0x1025, 0x1026, 0x1029, 0x104E]],  # Independent Vowels,Myanmar Symbol Aforementioned
        ['G', [0x103F]],  # Myanmar Letter Great Sa
        ['D', range(0x1040, 0x1049 + 1)],  # Myanmar Digits
        ['P', range(0x104A, 0x104B + 1)],  # Punctuation Marks
        ['W', [0x0020]],  # White space
    ]
    # Myanmar codes
    _MYANMAR_CODES_START = 0x1000
    _MYANMAR_CODES_END = 0x109f
    _MYANMAR_CODES = [unichr(n) for n in range(_MYANMAR_CODES_START, _MYANMAR_CODES_END + 1)]
    _PATTERN_MYANMAR_CODES = re.compile(u'([%s-%s]+)' % (unichr(_MYANMAR_CODES_START), unichr(_MYANMAR_CODES_END)),
                                        re.U)

    # Syllable Break Status and Definition
    _BREAK_STATUS_UNDEFINED = -2  # undefined cases
    _BREAK_STATUS_ILLEGAL_SPELLING_ORDER = -1  # Illegal spelling order
    _BREAK_STATUS_NO_BREAK_AFTER_1ST_CHARACTER = 0  # No break after 1 st character
    _BREAK_STATUS_BREAK_AFTER_1ST_CHARACTER = 1  # Break after 1 st character
    _BREAK_STATUS_BREAK_AFTER_2ND_CHARACTER = 2  # Break after 2 nd character
    _BREAK_STATUS_BREAK_AFTER_3RD_CHARACTER = 3  # Break after 3 rd character
    _BREAK_STATUS_BREAK_AFTER_4TH_CHARACTER = 4  # Break after 4 th character

    # Letter Sequence Table: 2nd, 3rd, 4th character
    _LETTER_SEQUENCE_TABLE_INDEX = {c: i for i, c in enumerate('A C D E F G I M P S V W'.split())}
    _LETTER_SEQUENCE_TABLE_2ND_CHARACTER = {
        # A C D E F G I M P S V W
        'A': (-1, -2, 1, 1, 0, -1, 1, 0, 1, 0, 0, 1),
        'C': (0, -2, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1),
        'D': (-1, 1, 0, 1, -1, -1, 1, -1, 1, -1, -1, 1),
        'E': (-1, -2, 1, 1, 2, 0, 1, -1, 1, -1, 0, 1),
        'F': (-1, -2, 1, 1, 2, -1, 1, -1, 1, -1, -1, 1),
        'G': (-1, 1, 1, 1, 0, -1, 1, -1, 1, -1, 0, 1),
        'I': (-1, 1, 1, 1, -1, -1, 1, -1, 1, -1, -1, 1),
        'M': (2, -2, 1, 1, 0, 0, 1, 0, 1, -1, 0, 1),
        'P': (-1, 1, 1, 1, -1, -1, 1, -1, 1, -1, -1, 1),
        'S': (-1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1),
        'V': (2, -2, 1, 1, 0, 0, 1, -1, 1, -1, 0, 1),
        'W': (-1, 1, 1, 1, -1, -1, 1, -1, 1, -1, -1, 0),
    }
    _LETTER_SEQUENCE_TABLE_3RD_CHARACTER = {
        # A C D E F G I M P S V W
        'AC': (3, 1, 1, 1, 1, 1, 1, -2, 1, 1, 1, 1),
        'CC': (0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1),
        'EC': (0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1),
        'FC': (3, 1, 1, 1, 1, 1, 1, -2, 1, 1, 1, 1),
        'MC': (0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1),
        'VC': (0, 1, 1, 1, 1, 1, 1, -2, 1, 0, 1, 1),
    }
    _LETTER_SEQUENCE_TABLE_4TH_CHARACTER = {
        # A C D E F G I M P S V W
        'ACM': (4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        'FCM': (4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        'VCM': (4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    }

    separator = property(lambda self: '|')

    def __init__(self, separator='|'):
        self.separator = separator
        for name in MyanmarTokenizer._CATEGORY_NAMES:
            setattr(MyanmarTokenizer, 'Category' + name, name)
        # 每个缅甸语字符对应的Category
        self.codeCategory = {unichr(_code): _name
                             for _name, _range in MyanmarTokenizer._CATEGORY_RANGE
                             for _code in _range}

    def code2Category(self, sentence):
        sentence = utils.toUnicode(sentence)
        return ''.join([self.codeCategory[c] if c in MyanmarTokenizer._MYANMAR_CODES else '?' for c in sentence])

    def _getSyllableBreakStatus(self, categorys, categorysLen):
        if categorysLen == 2:
            letterSequenceTable = MyanmarTokenizer._LETTER_SEQUENCE_TABLE_2ND_CHARACTER
        elif categorysLen == 3:
            letterSequenceTable = MyanmarTokenizer._LETTER_SEQUENCE_TABLE_3RD_CHARACTER
        elif categorysLen == 4:
            letterSequenceTable = MyanmarTokenizer._LETTER_SEQUENCE_TABLE_4TH_CHARACTER
        else:
            letterSequenceTable = None
        if not letterSequenceTable is None:
            status = letterSequenceTable.get(categorys[:categorysLen - 1])
            if not status is None:
                index = MyanmarTokenizer._LETTER_SEQUENCE_TABLE_INDEX.get(categorys[categorysLen - 1])
                if not index is None:
                    return status[index]
        return MyanmarTokenizer._BREAK_STATUS_UNDEFINED

    def cutRecursively(self, sentence):
        sentence = utils.toUnicode(sentence)
        result = ''
        for i, s in enumerate(self._split(sentence)):
            if ord(s[0]) < MyanmarTokenizer._MYANMAR_CODES_START \
                    or ord(s[0]) > MyanmarTokenizer._MYANMAR_CODES_END:
                if i != 0: result += self.separator
                result += s + self.separator
                continue
            categorys = self.code2Category(s)
            result += self._syllableSegmentationRecursively('', categorys, '', s)[1]
        return result

    def _split(self, sentence):
        for s in MyanmarTokenizer._PATTERN_MYANMAR_CODES.split(sentence):
            if s is u'':
                continue
            yield s

    def cut(self, sentence):
        sentence = utils.toUnicode(sentence)
        result = ''
        for i, s in enumerate(self._split(sentence)):
            if ord(s[0]) < MyanmarTokenizer._MYANMAR_CODES_START \
                    or ord(s[0]) > MyanmarTokenizer._MYANMAR_CODES_END:
                if i != 0: result += self.separator
                result += s + self.separator
                continue
            categorys = self.code2Category(s)
            result += self._syllableSegmentation(categorys, s)[1]
        return result

    def cutStd(self, stdin, stdout):
        for line in stdin:
            result = self.cut(line.strip())
            stdout.write(result+os.linesep)

    def cutCategory(self, categorys):
        result = self._syllableSegmentationRecursively('', categorys, '', categorys)
        return result[0]

    def _syllableSegmentation(self, categorys, sentence):
        ''' 对Myanmar分词
        :param categorys: sentence通过code2Category转换后的结果
        :param sentence: Myanmar sentence...
        :return : [categorys segmentations, sentence segmentations]
        '''
        result = ["", ""]
        residueLen = sentenceLen = len(categorys)
        start = 0
        while not residueLen is 0:
            if residueLen is 1:
                return [result[0] + categorys[-1], result[1] + sentence[-1]]
            # if categorys[start] is '?':
            #     # invalid categorys
            #     categorysLeft = categorys[start]
            #     sentenceLeft = sentence[start]
            #     start += 1
            #     result[0] += categorysLeft
            #     result[1] += sentenceLeft
            #     residueLen = sentenceLen - start
            #     continue

            # 先2nd
            breakStatus = self._getSyllableBreakStatus(categorys[start:start + 2], 2)
            if breakStatus == MyanmarTokenizer._BREAK_STATUS_UNDEFINED and residueLen >= 3:  # undefined cases
                breakStatus = self._getSyllableBreakStatus(categorys[start:start + 3], 3)
            if breakStatus == MyanmarTokenizer._BREAK_STATUS_UNDEFINED and residueLen >= 4:
                breakStatus = self._getSyllableBreakStatus(categorys[start:start + 4], 4)

            if breakStatus == MyanmarTokenizer._BREAK_STATUS_UNDEFINED:
                categorysLeft = categorys[start] + self.separator
                sentenceLeft = sentence[start] + self.separator
                start += 1
            elif breakStatus == MyanmarTokenizer._BREAK_STATUS_ILLEGAL_SPELLING_ORDER:
                # L = L + X1X2?;    R = X3X4...Xn ;
                categorysLeft = categorys[start:start + 2] + '?'
                sentenceLeft = sentence[start:start + 2] + '?'
                start += 2
            elif breakStatus == MyanmarTokenizer._BREAK_STATUS_NO_BREAK_AFTER_1ST_CHARACTER:
                # L = L + X1 ;   R = X2X3 ...Xn ;
                categorysLeft = categorys[start]
                sentenceLeft = sentence[start]
                start += 1
            elif breakStatus == MyanmarTokenizer._BREAK_STATUS_BREAK_AFTER_1ST_CHARACTER:  # Break after 1 st character
                # L = L + X1B;   R = X2X3 ...Xn ;
                categorysLeft = categorys[start] + self.separator
                sentenceLeft = sentence[start] + self.separator
                start += 1
            elif breakStatus == MyanmarTokenizer._BREAK_STATUS_BREAK_AFTER_2ND_CHARACTER:  # Break after 2 nd character
                # L = L + X1X2B;   R = X3X4 ...Xn ;
                categorysLeft = categorys[start:start + 2] + self.separator
                sentenceLeft = sentence[start:start + 2] + self.separator
                start += 2
            elif breakStatus == MyanmarTokenizer._BREAK_STATUS_BREAK_AFTER_3RD_CHARACTER:  # Break after 3 rd character
                # L = L + X1X2X3B;   R = X4X5 ...Xn ;
                categorysLeft = categorys[start:start + 3] + self.separator
                sentenceLeft = sentence[start:start + 3] + self.separator
                start += 3
            elif breakStatus == MyanmarTokenizer._BREAK_STATUS_BREAK_AFTER_4TH_CHARACTER:  # Break after 4 th character
                # L = L + X1X2X3X4B;  R = X5X6 ...Xn ;
                categorysLeft = categorys[start:start + 4] + self.separator
                sentenceLeft = sentence[start:start + 4] + self.separator
                start += 4
            result[0] += categorysLeft
            result[1] += sentenceLeft
            residueLen = sentenceLen - start

        return (result[0].rstrip(self.separator), result[1].rstrip(self.separator))

    def _syllableSegmentationRecursively(self, categorysLeft, categorysRight, sentenceLeft, sentenceRight):
        ''' 同_syllableSegmentation， 以递归方式运行
        :param categorysLeft: categorys返回结果
        :param categorysRight: categorys未处理字符串
        :param sentenceLeft: sentenceLeft返回结果
        :param sentenceRight: sentenceRight未处理字符串
        :return: [categorys segmentations, sentence segmentations]
        '''
        rightLen = len(categorysRight)
        if rightLen is 0:
            return (categorysLeft, sentenceLeft)
        if rightLen is 1:
            return (categorysLeft + categorysRight, sentenceLeft + sentenceRight)
        # 先2nd
        breakStatus = self._getSyllableBreakStatus(categorysRight[:2], 2)
        if breakStatus == MyanmarTokenizer._BREAK_STATUS_UNDEFINED and rightLen >= 3:  # undefined cases
            breakStatus = self._getSyllableBreakStatus(categorysRight[:3], 3)
        if breakStatus == MyanmarTokenizer._BREAK_STATUS_UNDEFINED and rightLen >= 4:
            breakStatus = self._getSyllableBreakStatus(categorysRight[:4], 4)
        if breakStatus == MyanmarTokenizer._BREAK_STATUS_UNDEFINED:
            return self._syllableSegmentationRecursively(categorysLeft + categorysRight[0] + self.separator,
                                                         categorysRight[1:],
                                                         sentenceLeft + sentenceRight[0] + self.separator,
                                                         sentenceRight[1:])

        if breakStatus == MyanmarTokenizer._BREAK_STATUS_ILLEGAL_SPELLING_ORDER:
            # L = L + X1X2?;    R = X3X4...Xn ;
            return self._syllableSegmentationRecursively(categorysLeft + categorysRight[:2] + '?', categorysRight[2:],
                                                         sentenceLeft + sentenceRight[:2] + '?', sentenceRight[2:])
        elif breakStatus == MyanmarTokenizer._BREAK_STATUS_NO_BREAK_AFTER_1ST_CHARACTER:
            # L = L + X1 ;   R = X2X3 ...Xn ;
            return self._syllableSegmentationRecursively(categorysLeft + categorysRight[0], categorysRight[1:],
                                                         sentenceLeft + sentenceRight[0], sentenceRight[1:])
        elif breakStatus == MyanmarTokenizer._BREAK_STATUS_BREAK_AFTER_1ST_CHARACTER:  # Break after 1 st character
            # L = L + X1B;   R = X2X3 ...Xn ;
            return self._syllableSegmentationRecursively(categorysLeft + categorysRight[0] + self.separator,
                                                         categorysRight[1:],
                                                         sentenceLeft + sentenceRight[0] + self.separator,
                                                         sentenceRight[1:])
        elif breakStatus == MyanmarTokenizer._BREAK_STATUS_BREAK_AFTER_2ND_CHARACTER:  # Break after 2 nd character
            # L = L + X1X2B;   R = X3X4 ...Xn ;
            return self._syllableSegmentationRecursively(categorysLeft + categorysRight[:2] + self.separator,
                                                         categorysRight[2:],
                                                         sentenceLeft + sentenceRight[:2] + self.separator,
                                                         sentenceRight[2:])
        elif breakStatus == MyanmarTokenizer._BREAK_STATUS_BREAK_AFTER_3RD_CHARACTER:  # Break after 3 rd character
            # L = L + X1X2X3B;   R = X4X5 ...Xn ;
            return self._syllableSegmentationRecursively(categorysLeft + categorysRight[:3] + self.separator,
                                                         categorysRight[3:],
                                                         sentenceLeft + sentenceRight[:3] + self.separator,
                                                         sentenceRight[3:])
        elif breakStatus == MyanmarTokenizer._BREAK_STATUS_BREAK_AFTER_4TH_CHARACTER:  # Break after 4 th character
            # L = L + X1X2X3X4B;  R = X5X6 ...Xn ;
            return self._syllableSegmentationRecursively(categorysLeft + categorysRight[:4] + self.separator,
                                                         categorysRight[4:],
                                                         sentenceLeft + sentenceRight[:4] + self.separator,
                                                         sentenceRight[4:])


def test():
    cases = [('CCSCCSCCCCCA', '|CCSCCSC|C|C|CCA|'),
             ('ECSCCCCACMCAFCCAF', '|ECSC|C|CCA|CMCAF|CCAF|'),
             ('ECSCVCC', '|ECSCV|C|C|'),
             ('ICCVCA', '|I|C|CVCA|'),
             ('CCASCCSCCVCA', '|CCASCCSC|CVCA|'),
             ('CVFCACMVVCA', '|CVFCA|CMVVCA|'),
             ('CCVGVC', '|C|CVGV|C|'),
             ('CVCCVFCV', '|CV|C|CVF|CV|'),
             ('CMMCAVCAICAF', '|CMMCAVCA|I|CAF|'),
             ('CCACMACVFCVF', '|CCACMA|CVF|CVF|'),
             ('CSCCACCACVVCA', '|CSCCA|CCA|CVVCA|'),
             ]
    tokenizer = MyanmarTokenizer()
    for case in cases:
        result = tokenizer.cutCategory(case[0])
        # if '|'+result+'|' != case[1]:
        #     print case, result
        print case, result, '|' + result + '|' == case[1]

    lines = codecs.open('samples.txt', 'r', 'utf16').readlines()
    tokenizer.separator = '@@'
    for lineno, line in enumerate(lines):
        case = line.strip().split('!!!')
        if len(case) == 1:
            case = [case[0], case[0]]
        result = tokenizer.cut(case[0])
        print u'%3d\t%s\t%s\t=>\t%s\t==\t%s' % (lineno+1, result == case[1], case[0], case[1], result)

    # tokenizer = MyanmarTokenizer()
    # seg = "ကမ္ဘာ့ဘဏ်အုပ်စု၏အဖွဲ့ဝင်"
    # seg = "ဆင်"
    # seg = "ကမ္ဘာ့ဘဏ်အုပ်abcdefgစု၏အဖွဲ့ဝင်"
    # seg = "ဆabcင်"
    # seg = 'ကော်'
    seg = 'စာကြည့်တိုက်'
    print tokenizer.code2Category(seg)
    # result = tokenizer.cutRecursively(seg)
    # print result
    result = tokenizer.cut(seg)
    print result
    # tokenizer.cutCategory('ECSCVCC')
    # test();


def analyzeParams(args):
    from optparse import OptionParser
    parser = OptionParser(usage="%prog -s -i FILE or [< FILE] -o FILE or [> FILE]", version="%prog 1.0")

    # add_option用来加入选项，action是有store，store_true，store_false等，dest是存储的变量，default是缺省值，help是帮助提示
    parser.set_description(u'Syllable Segmentation Program of Myanmar\n');

    parser.add_option("-s", "--separator", dest="separator", metavar="string"
                      , help=u'Syllable breaking symbol, default use |', default='|')
    parser.add_option("-c", "--coding", dest="coding", metavar="string"
                      , help=u'Input file coding, default use utf8', default='utf8')

    parser.add_option("-i", "--input", dest="input", metavar="FILE", action="store"
                      , help=u'Input file(dir) path， or < FILE')
    parser.add_option("-o", "--output", dest="output", metavar="FILE", action="store"
                      , help=u'Output file(dir) path, or > FILE')

#     if len(args) <= 1:
#         parser.print_help(sys.stderr)
#         eg = '''eg:
# python myanmar-tokenizer.py
# python myanmar-tokenizer.py -s "@" -i file -o file
# python myanmar-tokenizer.py -s "@" < inputfile > outputfile
#
#         \n'''
#         sys.stderr.write(eg)
#         return

    (opt, args) = parser.parse_args(args)

    tokenizer = MyanmarTokenizer(opt.separator)

    if opt.input == None or os.path.isfile(opt.input):
        stdin = sys.stdin
        stdout = sys.stdout
        if opt.input != None and os.path.exists(opt.input):
            stdin = codecs.open(opt.input, 'r', opt.coding)
        if opt.output != None:
            stdout = codecs.open(opt.output, 'w', 'utf8')
        tokenizer.cutStd(stdin, stdout)
        stdin.close()
        stdout.close()
    elif os.path.isdir(opt.input):
        inputpathLen = len(opt.input.rstrip(os.path.sep))
        stdout = sys.stdout
        isdir = opt.output != None and os.path.isdir(opt.output)

        processes = 10 if isdir else 1
        tokenizerTask = task.Task(processes)
        def work(tokenizer, stdin, stdout, closeOut):
            tokenizer.cutStd(stdin, stdout)
            stdin.close()
            if closeOut: stdout.close()
            return stdin.name

        if opt.output != None and not os.path.isdir(opt.output):
            stdout = codecs.open(opt.output, 'w', 'utf8')

        filecount = 0

        def callback(value):
            #print filecount, '\r',
            pass

        for path in utils.getFiles(opt.input, recursive=True):
            filecount += 1
            print 'run:%8d\r' % filecount,
            stdin = codecs.open(path, 'r', opt.coding)
            if isdir:
                op = os.path.join(opt.output, path[inputpathLen + 1:])
                try:
                    os.makedirs(os.path.split(op)[0])
                except:
                    pass
                stdout = codecs.open(op, 'w', 'utf8')
            tokenizerTask.add_async(work, (tokenizer, stdin, stdout, isdir), callback=callback)
        tokenizerTask.join()

if __name__ == "__main__":
    argv = sys.argv

    # argv = ['-s', '|',
    #         '-c', 'utf16',
    #         '-i', u'/home/zhaokun/IME/DicTools/myanmar/myanmar-tokenizer/data',
    #         '-o', u'/home/zhaokun/IME/DicTools/myanmar/myanmar-tokenizer/data1'
    #         ]
    ts = time.time()
    analyzeParams(argv)
    sys.stderr.write('run time: %f\n'%(time.time()-ts))
    #
    # test()
    pass

