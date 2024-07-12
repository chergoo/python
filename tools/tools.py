#!/usr/bin/env python3
# encoding: utf-8

import tkinter as tk
from tkinter import colorchooser,font,messagebox,filedialog,font
import tkinter.ttk as ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import sys
import datetime
import random
from geopy.geocoders import Nominatim  
from random import uniform  
import folium
import requests
import webbrowser
import json
from dotenv import load_dotenv
import os
import io
import tkinter.font as tkFont
import matplotlib.font_manager as fm
import imageio
import numpy as np



kaomojis = {
    "欢乐":[
            "(* ^ ω ^)",
           "(´ ∀ ` *)",
           "٩(◕‿◕｡)۶",
           "☆*:.｡.o(≧▽≦)o.｡.:*☆",
           "(o^▽^o)","(⌒▽⌒)☆",
           "<(￣︶￣)>",
           "。.:☆*:･'(*⌒―⌒*)))",
           "ヽ(・∀・)ﾉ",
           "(´｡• ω •｡`)	(￣ω￣)",
           "｀;:゛;｀;･(°ε° )",
           "(o･ω･o)",
           "	(＠＾◡＾)",
           "ヽ(*・ω・)ﾉ",
           "	(o_ _)ﾉ彡☆",
           "(^人^)",
            "(o´▽`o)",
            "(*´▽`*)",
            "｡ﾟ( ﾟ^∀^ﾟ)ﾟ｡",
            "( ´ ω ` )",
            "(((o(*°▽°*)o)))",
            "(≧◡≦)",
            "(o´∀`o)",
            "(´• ω •`)",
            "(＾▽＾)",
            "(⌒ω⌒)",
            "∑d(°∀°d)",
            "╰(▔∀▔)╯",
            "(─‿‿─)",
            "(*^‿^*)",
            "ヽ(o^ ^o)ﾉ",
            "(✯◡✯)",
            "(◕‿◕)",
            "(*≧ω≦*)",
            "(☆▽☆)",
            "(⌒‿⌒)",
            "＼(≧▽≦)／",
            "ヽ(o＾▽＾o)ノ",
            "☆ ～('▽^人)",
            "ヽ(*⌒▽⌒*)ﾉ",
            "(✧ω✧)",
            "٩(｡•́‿•̀｡)۶",
            "(*°▽°*)",
            "(´｡• ᵕ •｡`)",
            "( ´ ▽ ` )",
            "(￣▽￣)",
            "╰(*´︶`*)╯",
            "(っ˘ω˘ς )",
            "(☆ω☆)",
            "o(≧▽≦)o",
            "ヽ(>∀<☆)ノ",
            "＼(￣▽￣)／",
            "(*¯︶¯*)",
            "＼(＾▽＾)／",
            "٩(◕‿◕)۶",
            "(〃＾▽＾〃)",
            r"\(^ヮ^)/",
            r"\(★ω★)/",
            "(o˘◡˘o)",
            "(╯✧▽✧)╯",
            "o(>ω<)o",
            "o( ❛ᴗ❛ )o",
            "｡ﾟ(TヮT)ﾟ｡",
            "( ‾́ ◡ ‾́ )",
            "(ﾉ´ヮ`)ﾉ*: ･ﾟ",
            "(b ᵔ▽ᵔ)b",
            "(๑˃ᴗ˂)ﻭ",
            "°˖✧◝(⁰▿⁰)◜✧˖°",
            "(*꒦ິ꒳꒦ີ)",
            "( ˙꒳​˙ )",
            "(๑˘︶˘๑)",
            "(´･ᴗ･ ` )",
            "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
            "(„• ֊ •„)",
            "(.❛ ᴗ ❛.)",
            "(*￣▽￣)b",
            "(¬‿¬ )",
            "(￢‿￢ )",
            "(⁀ᗢ⁀)",
            "( ˙▿˙ )",
            "(¯▿¯)",
            "( ◕▿◕ )",
            "＼(٥⁀▽⁀ )／",
            "(๑>◡<๑)",
            "( ´ ▿ ` )",
            "(ᵔ◡ᵔ)",
            "(„• ᴗ •„)",
            "( = ⩊ = )",
            "( ´ ꒳ ` )",
            "⸜( ´ ꒳ ` )⸝",
            "⸜(⸝⸝⸝´꒳`⸝⸝⸝)⸝",
            "⸜(*ˊᗜˋ*)⸝",
            "⸜( *ˊᵕˋ* )⸝",
            ],

    "love": [
        "(ﾉ´ з `)ノ",
        "(♡μ_μ)",
        "(*^^*)♡",
        "☆⌒ヽ(*'､^*)",
        "(♡-_-♡)",
        "(￣ε￣＠)",
        "ヽ(♡‿♡)ノ",
        "( ´ ∀ `)ノ～ ♡",
        "(｡・//ε//・｡)",
        "(*♡∀♡)",
        "(´｡• ᵕ •｡`) ♡",
        "(─‿‿─)♡",
        "(´ ω `♡)",
        "♡( ◡‿◡ )",
        "(◕‿◕)♡",
        "(/▽＼*)｡o○♡",
        "♡ ～('▽^人)",
        "♡(｡- ω -)",
        "(♡°▽°♡)",
        "(ღ˘⌣˘ღ)",
        "(´• ω •`) ♡",
        "(´ ε ` )♡",
        "(´｡• ω •｡`) ♡",
        "( ´ ▽ ` ).｡ｏ♡",
        "♡＼(￣▽￣)／♡",
        "(♡˙︶˙♡)",
        "(*˘︶˘*).｡.:*♡",
        "╰(*´︶`*)╯♡",
        "(≧◡≦) ♡",
        "(⌒▽⌒)♡",
        "(*¯ ³¯*)♡",
        "(っ˘з(˘⌣˘ ) ♡",
        "٩(♡ε♡)۶",
        "(/^-^(^ ^*)/ ♡",
        "( ˘⌣˘)♡(˘⌣˘ )",
        "♡ (˘▽˘>ԅ( ˘⌣˘)",
        "σ(≧ε≦σ) ♡",
        "♡ (⇀ 3 ↼)",
        "♡ (￣З￣)",
        "(❤ω❤)",
        "(°◡°♡)",
        "(´♡‿♡`)",
        "❤ (ɔˆз(ˆ⌣ˆc)",
        "(˘∀˘)/(μ‿μ) ❤",
        "Σ>―(〃°ω°〃)♡→",
        "(´,,•ω•,,)♡",
        "(´꒳`)♡",
        "♡(>ᴗ•)"

    ],

    "尴尬": [
        "(⌒_⌒;)",
        "(o^ ^o)",
        "(*/ω＼)",
        "(*/。＼)",
        "(*μ_μ)",
        "(o-_-o)",
        "(*ﾉωﾉ)",
        "(*/_＼)",
        "( ◡‿◡ *)",
        "(ᵔ.ᵔ)",
        "(*ﾉ∀`*)",
        "(//▽//)",
        "(*ﾉ▽ﾉ)",
        "(*^.^*)",
        "(ノ*°▽°*)",
        "(//ω//)",
        "(￣▽￣*)ゞ",
        "(⁄ ⁄•⁄ω⁄•⁄ ⁄)",
        "(*/▽＼*)",
        "(⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
        "(/▿＼ )",
        "( 〃▽〃)",
        "(ง ื▿ ื)ว",
        "(„ಡωಡ„)",
        "(///￣ ￣///)",
        "(◕‿◕✿)",
        "ଘ(੭ˊᵕˋ)੭* ੈ✩‧₊˚",
        "ଘ(੭ˊ꒳​ˋ)੭✧"

    ],

    "同情": [
        "(ノ_<。)ヾ(´ ▽ ` )",
        "｡･ﾟ･(ﾉД`)ヽ(￣ω￣ )",
        "ρ(- ω -、)ヾ(￣ω￣; )",
        "ヽ(~_~(・_・ )ゝ",
        "(*´ I `)ﾉﾟ(ﾉД｀ﾟ)ﾟ｡",
        "ヽ(￣ω￣(。。 )ゝ",
        "(ﾉ_；)ヾ(´ ∀ ` )",
        "(; ω ; )ヾ(´∀`* )",
        "(*´ー)ﾉ(ノд`)",
        "(ｏ・_・)ノ”(ノ_<、)",
        "(っ´ω`)ﾉ(╥ω╥)",
        "(´-ω-`( _ _ )",
        "(ಠ_ಠ)"
    ],
    "不满": [
        "(＃＞＜)",
        "(；⌣̀_⌣́)",
        "☆ｏ(＞＜；)○",
        "(￣ ￣|||)",
        "(＃￣ω￣)",
        "(＃￣0￣)",
        "(￣□￣」)",
        "(；￣Д￣)",
        "(￢_￢;)",
        "(＞ｍ＜)",
        "(」°ロ°)」",
        "(〃＞＿＜;〃)",
        "<(￣ ﹌ ￣)>",
        "凸(￣ヘ￣)",
        "(」＞＜)」",
        "(￣ヘ￣)",
        "(--_--)",
        "o(>< )o",
        "(︶︹︺)",
        "(＞﹏＜)",
        "(⇀‸↼‶)",
        "(눈_눈)",
        "(＾＾＃)",
        "(￣︿￣)",
        "ヾ( ￣O￣)ツ",
        "(ᗒᗣᗕ)՞"

    ],
    "生气": [
        "(＃`Д´)",
        "(`皿´＃)",
        "( ` ω ´ )",
        "ヽ( `д´*)ノ",
        "凸(`△´＃)",
        "ヽ(`⌒´メ)ノ",
        "(`ー´)",
        "(・`ω´・)",
        "( `ε´ )",
        "ψ( ` ∇ ´ )ψ",
        "ヾ(`ヘ´)ﾉﾞ",
        "ヽ(‵﹏´)ノ",
        "凸( ` ﾛ ´ )凸",
        "┌∩┐(◣_◢)┌∩┐",
        "(╬`益´)",
        "(ﾒ` ﾛ ´)",
        "Σ(▼□▼メ)",
        "(°ㅂ°╬)",
        "ψ(▼へ▼メ)～→",
        "(ノ°益°)ノ",
        "((╬◣﹏◢))",
        "(҂` ﾛ ´)凸",
        "(‡▼益▼)",
        "(҂ `з´ )",
        "٩(╬ʘ益ʘ╬)۶",
        "(╬ Ò﹏Ó)",
        "＼＼٩(๑`^´๑)۶／／",
        "(凸ಠ益ಠ)凸",
        "٩(ఠ益ఠ)۶",
        "୧((#Φ益Φ#))୨",
        "←~(Ψ▼ｰ▼)∈",
        "↑_(ΦwΦ)Ψ",
        "(ﾉಥ益ಥ)ﾉ",
        "(≖､≖╬)",
        "(╯°益°)╯彡┻━┻",
        "(╮°-°)╮┳━━┳ ( ╯°□°)╯ ┻━━┻"

    ],
    "悲伤":[
        "(ノ_<。)",
        "(-_-)",
        "(´-ω-`)",
        ".･ﾟﾟ･(／ω＼)･ﾟﾟ･.",
        "。゜゜(´Ｏ`) ゜゜。",
        "(-ω-、)",
        "(ﾉД`)",
        "(μ_μ)",
        "o(TヘTo)",
        "( ; ω ; )",
        "(｡╯︵╰｡)",
        "｡･ﾟﾟ*(>д<)*ﾟﾟ･｡",
        "｡･ﾟ(ﾟ><ﾟ)ﾟ･｡",
        "(╯︵╰,)",
        "(个_个)",
        "( ﾟ，_ゝ｀)",
        "( ╥ω╥ )",
        "(╯_╰)",
        "(╥_╥)",
        ".｡･ﾟﾟ･(＞_＜)･ﾟﾟ･｡.",
        "｡ﾟ(｡ﾉωヽ｡)ﾟ｡",
        "(╥﹏╥)",
        "(ノ_<、)",
        "(／ˍ・、)",
        "(つω`｡)",
        "(｡T ω T｡)",
        "(ﾉω･､)",
        "･ﾟ･(｡>ω<｡)･ﾟ･",
        "｡ﾟ･ (>﹏<) ･ﾟ｡",
        "(っ˘̩╭╮˘̩)っ",
        "(>_<)",
        "(T_T)",
        "o(〒﹏〒)o",
        "(｡•́︿•̀｡)",
        "(ಥ﹏ಥ)",
        "(ಡ‸ಡ)"
    ],
    "疼痛":[
        "~(>_<~)",
        "☆⌒(> _ <)",
        "☆⌒(>。<)",
        "(☆_@)",
        "(x_x)⌒☆",
        "(×_×)⌒☆",
        "(x_x)",
        "(×_×)",
        "(×﹏×)",
        "☆(＃××)",
        "(＋_＋)",
        "[ ± _ ± ]",
        "(ﾒ﹏ﾒ)",
        "_:(´ཀ`」 ∠):_",
        "٩(× ×)۶"

    ],
    "害怕":[
        "(ノωヽ)",
        "(／。＼)",
        "(ﾉ_ヽ)",
        "..・ヾ(。＞＜)シ",
        "＼(〇_ｏ)／",
        "(・人・)",
        "(;;;*_*)",
        "(″ロ゛)",
        "(/ω＼)",
        "(/_＼)",
        "〜(＞＜)〜",
        "Σ(°△°|||)︴",
        "〣( ºΔº )〣",
        "＼(º □ º l|l)/",
        "{{ (>_<) }}",
        "(((＞＜)))",
        "▓▒░(°◡°)░▒▓"

    ],
    "冷漠":[
        "ヽ(ー_ー )ノ",
        "ヽ(´ー` )┌",
        "┐(‘～` )┌",
        "ヽ(　￣д￣)ノ",
        "┐(￣ヘ￣)┌",
        "ヽ(￣～￣　)ノ",
        "╮(￣_￣)╭",
        "ヽ(ˇヘˇ)ノ",
        r"¯\_(ツ)_/¯",
        "╮(￣～￣)╭",
        "┐(︶▽︶)┌",
        "┐(￣～￣)┌",
        "┐( ´ д ` )┌",
        "╮(︶︿︶)╭",
        "┐(￣∀￣)┌",
        "┐( ˘ ､ ˘ )┌",
        "╮( ˘_˘ )╭",
        "┐( ˘_˘ )┌",
        "╮( ˘ ､ ˘ )╭",
        "╮(︶▽︶)╭",
        "┐(￣ヮ￣)┌",
        "ᕕ( ᐛ )ᕗ",
        "┐(シ)┌"

    ],
    "困惑":[
        "(￣ω￣;)",
        "σ(￣、￣〃)",
        "(￣～￣;)",
        "(-_-;)・・・",
        "┐(￣ヘ￣;)┌",
        "(〃￣ω￣〃ゞ",
        "(・_・ヾ",
        "┐('～`;)┌",
        "(・_・;)",
        "(￣_￣)・・・",
        "╮(￣ω￣;)╭",
        "(¯ . ¯;)",
        "(・・ ) ?",
        "(・・;)ゞ",
        "(＠_＠)",
        "(•ิ_•ิ)?",
        "(◎ ◎)ゞ",
        "(ーー;)",
        "ლ(ಠ_ಠ ლ)",
        "(¯ ¯٥)",
        "(¯ . ¯٥)",
        'ლ(¯ロ¯"ლ)'
    ],
    "怀疑":[
        "(￢_￢)",
        "(→_→)",
        "(￢ ￢)",
        "(￢‿￢ )",
        "(¬‿¬ )",
        "(¬ ¬ )",
        "(←_←)",
        "(¬_¬ )",
        "(↼_↼)",
        "(⇀_⇀)",
        "(ᓀ ᓀ)"
    ],
    "惊讶":[
        "w(°ｏ°)w",
        "ヽ(°〇°)ﾉ",
        "Σ(O_O)",
        "Σ(°ロ°)",
        "(⊙_⊙)",
        "(o_O)",
        "(O_O;)",
        "(O.O)",
        "Σ(□_□)",
        "(□_□)",
        "(o_O) !",
        "(°ロ°) !",
        "∑(O_O;)",
        "( : ౦ ‸ ౦ : )"

    ],
    "问候":[
        "(*・ω・)ﾉ",
        "(￣▽￣)ノ",
        "(°▽°)/",
        "( ´ ∀ ` )ﾉ",
        "( ° ∀ ° )ﾉﾞ",
        "(´• ω •`)ﾉ",
        "(＠´ー`)ﾉﾞ",
        "(^-^*)/",
        "ヾ(*'▽'*)",
        "＼(⌒▽⌒)",
        "ヾ(☆▽☆)",
        "( ´ ▽ ` )ﾉ",
        "ヾ(・ω・*)",
        "(・∀・)ノ",
        "~ヾ(・ω・)",
        "(^０^)ノ",
        "(*°ｰ°)ﾉ",
        "(・_・)ノ",
        "(o´ω`o)ﾉ",
        "( ´ ▽ ` )/",
        "(o^ ^o)/",
        "(⌒ω⌒)ﾉ",
        "( ´ ω ` )ノﾞ",
        "(￣ω￣)/",
        "(≧▽≦)/",
        "(✧∀✧)/",
        "(o´▽`o)ﾉ",
        "(￣▽￣)/"

    ],
    "拥抱":[
        "(づ￣ ³￣)づ",
        "(つ≧▽≦)つ",
        "(つ✧ω✧)つ",
        "(づ ◕‿◕ )づ",
        "(づ◡﹏◡)づ",
        "(っಠ‿ಠ)っ",
        "(つ . •́ _ʖ •̀ .)つ",
        "(⊃｡•́‿•̀｡)⊃",
        "⊂(´• ω •`⊂)",
        "⊂(･ω･*⊂)",
        "⊂(￣▽￣)⊃",
        "⊂( ´ ▽ ` )⊃",
        "(っ╹ᆺ╹)っ",
        "(っ ᵔ◡ᵔ)っ",
        "(ノ= ⩊ = )ノ",
        "( ~*-*)~"
    ],
    "wink":[
        "(^_~)",
        "( ﾟｏ⌒)",
        "(^_-)≡☆",
        "(^ω~)",
        "( -_・)",
        "(^_-)",
        "(~人^)",
        "(>ω^)",
        "(^_<)〜☆",
        "(^人<)〜☆",
        "☆⌒(≧▽​° )",
        "☆⌒(ゝ。∂)",
        "(^.~)☆",
        "(･ω<)☆",
        "(^_−)☆",
        "(^_<)",
        "(^.~)",
        "(｡•̀ᴗ-)✧",
        "(>ᴗ•)"

    ],
    "道歉":[
        "(*￣ii￣)",
        "(￣ﾊ￣*)",
        r"\(￣ﾊ￣)",
        "(＾་།＾)",
        "(￣ ;;￣)",
        "(￣ ;￣)",
        "(￣ ¨ヽ￣)",
        "(＾〃＾)"

    ],
    "流鼻血":[
        "(*￣ii￣)",
        "(￣ﾊ￣*)",
        r"\(￣ﾊ￣)",
        "(＾་།＾)",
        "(￣ ;;￣)",
        "(￣ ;￣)",
        "(￣ ¨ヽ￣)",
        "(＾〃＾)"
    ],
    "隐藏":[
        "ﾍ(･_|",
        "|ω･)ﾉ",
        "ヾ(･|",
        "|д･)",
        "|_￣))",
        "|▽//)",
        "┬┴┬┴┤(･_├┬┴┬┴",
        "|_・)",
        "┬┴┬┴┤(･_├┬┴┬┴",
        "┬┴┬┴┤( ͡° ͜ʖ├┬┴┬┴",
        "┬┴┬┴┤･ω･)ﾉ",
        "|･д･)ﾉ",
        "|ʘ‿ʘ)╯"
    ],
    "写":[
        "( ￣ー￣)φ__",
        "__φ(。。)",
        "__φ(．．;)",
        "ヾ( `ー´)シφ__",
        "__〆(￣ー￣ )",
        "....φ(・∀・*)",
        "___〆(・∀・)",
        "__φ(◎◎ヘ)",
        "( . .)φ__",
        "....φ(︶▽︶)φ....",
        "( ^▽^)ψ__"

    ],
    "跑":[
        "☆ﾐ(o*･ω･)ﾉ",
        "C= C= C= C= C=┌(;・ω・)┘",
        "─=≡Σ((( つ＞＜)つ",
        "C= C= C= C=┌( `ー´)┘",
        "ε=ε=┌( >_<)┘",
        "ε=ε=ε=ε=┌(;￣▽￣)┘",
        "ε===(っ≧ω≦)っ",
        "ヽ(￣д￣;)ノ=3=3=3",
        "。。。ミヽ(。＞＜)ノ"
    ],
    "睡觉":[        
        "(－_－) zzZ",
        "(∪｡∪)｡｡｡zzZ",
        "(－ω－) zzZ",
        "(－.－)...zzz",
        "(￣ρ￣)..zzZZ",
        "(( _ _ ))..zzzZZ",
        "(￣o￣) zzZZzzZZ",
        "(＿ ＿*) Z z z",
        "(x . x) ~~zzZ"
    ],
    "猫":[
        "(=^･ω･^=)",
        "(=^･ｪ･^=)",
        "(=①ω①=)",
        "( =ω=)..nyaa",
        "( =ノωヽ=)",
        "(=^‥^=)",
        "(=`ω´=)",
        "(= ; ｪ ; =)",
        "(=⌒‿‿⌒=)",
        "(=^ ◡ ^=)",
        "(=^-ω-^=)",
        "ヾ(=`ω´=)ノ”",
        "ฅ(• ɪ •)ฅ",
        "ฅ(•ㅅ•❀)ฅ",
        "(/ =ω=)/",
        "(＾• ω •＾)",
        "ଲ(ⓛ ω ⓛ)ଲ",
        "(^=◕ᴥ◕=^)",
        "( =ω= )",
        "(^˵◕ω◕˵^)",
        "( Φ ω Φ )",
        "ต(=ω=)ต",
        "(^◕ᴥ◕^)",
        "(^◔ᴥ◔^)",
        "ฅ(^◕ᴥ◕^)ฅ"

    ],
    "熊":[
        "( ´(ｴ)ˋ )",
        "(*￣(ｴ)￣*)",
        "ヽ(￣(ｴ)￣)ﾉ",
        "(／￣(ｴ)￣)／",
        "(／(ｴ)＼)",
        "⊂(￣(ｴ)￣)⊃",
        "ヽ( ˋ(ｴ)´ )ﾉ",
        "(￣(ｴ)￣)",
        "⊂(´(ェ)ˋ)⊃",
        "(/-(ｴ)-＼)",
        "(/°(ｴ)°)/",
        "ʕ ᵔᴥᵔ ʔ",
        "ʕಠᴥಠʔ",
        "ʕ •̀ o •́ ʔ",
        "ʕ •̀ ω •́ ʔ",
        "ʕ •ᴥ• ʔ"

    ],
    "狗":[
        "∪･ω･∪",
        "∪￣-￣∪",
        "∪･ｪ･∪",
        "V●ᴥ●V",
        "U^ｪ^U",
        "ＵＴｪＴＵ",
        "Ｕ^皿^Ｕ",
        "U・ᴥ・U"
    ],
    "蜘蛛":[
        r"/╲/\╭(ఠఠ益ఠఠ)╮/\/\ ",
        r"/╲/\╭(ರರ⌓ರರ)╮/\╱\ ",
        r"/╲/\╭༼ ººل͟ºº ༽╮/\╱\ ",
        r"/╲/\╭( ͡°͡° ͜ʖ ͡°͡°)╮/\╱\ ",
        r"/╲/\╭[☉﹏☉]╮/\╱\ ",
        r"/╲/\( •̀ ω •́ )/\╱\ ",
        r"/╲/\╭[ ᴼᴼ ౪ ᴼᴼ]╮/\╱\ ",
    ],
    "朋友":[
        "ヾ(・ω・)メ(・ω・)ノ",
        "ヽ(∀° )人( °∀)ノ",
        "ヽ( ⌒o⌒)人(⌒-⌒ )ﾉ",
        "ヾ(￣ー￣(≧ω≦*)ゝ",
        "＼(＾∀＾)メ(＾∀＾)ノ",
        "(*^ω^)八(⌒▽⌒)八(-‿‿- )ヽ",
        "ヽ( ⌒ω⌒)人(=^‥^= )ﾉ",
        "ヽ(≧◡≦)八(o^ ^o)ノ",
        "(*・∀・)爻(・∀・*)",
        "(((￣(￣(￣▽￣)￣)￣)))",
        "o(^^o)(o^^o)(o^^o)(o^^)o",
        "｡*:☆(・ω・人・ω・)｡:゜☆｡",
        "(°(°ω(°ω°(☆ω☆)°ω°)ω°)°)",
        "ヾ(・ω・`)ノヾ(´・ω・)ノ゛",
        "Ψ( `∀)(∀´ )Ψ",
        "☆ヾ(*´・∀・)ﾉヾ(・∀・`*)ﾉ☆",
        "(((*°▽°*)八(*°▽°*)))",
        "(っ˘▽˘)(˘▽˘)˘▽˘ς)",
        "(*＾ω＾)人(＾ω＾*)",
        "٩(๑･ิᴗ･ิ)۶٩(･ิᴗ･ิ๑)۶",
        "(☞°ヮ°)☞ ☜(°ヮ°☜)",
        r"\( ˙▿˙ )/\( ˙▿˙ )/",
        r"＼(▽￣ \ (￣▽￣) / ￣▽)／"
    ],
    "敌人":[
        "ヽ( ･∀･)ﾉ_θ彡☆Σ(ノ `Д´)ノ",
        "(*´∇`)┌θ☆(ﾉ>_<)ﾉ",
        "( ￣ω￣)ノﾞ⌒☆ﾐ(o _ _)o",
        "(╬￣皿￣)=○＃(￣#)３￣)",
        "(o¬‿¬o )...☆ﾐ(*x_x)",
        "(*`0´)θ☆(メ°皿°)ﾉ",
        "(; -_-)――――――C<―_-)",
        "＜( ￣︿￣)︵θ︵θ︵☆(＞口＜－)",
        "(￣ε(#￣)☆╰╮o(￣▽￣///)",
        ",,((( ￣□)_／ ＼_(○￣ ))),,",
        "ヘ(>_<ヘ) ￢o(￣‿￣ﾒ)",
        "ヽ(>_<ヽ) ―⊂|=0ヘ(^‿^ )",
        "(҂` ﾛ ´)︻デ═一 ＼(º □ º l|l)/",
        "(╯°Д°)╯︵ /(.□ . ＼)",
        "(¬_¬'')ԅ(￣ε￣ԅ)",
        "!!(ﾒ￣ ￣)_θ☆°0°)/",
        "(ﾉ-.-)ﾉ….((((((((((((●~* ( >_<)",
        "/( .□.)＼ ︵╰(°益°)╯︵ /(.□. /)",
        "(`⌒*)O-(`⌒´Q)",
        "(((ง’ω’)و三 ง’ω’)ڡ≡　☆⌒ﾐ((x_x)",
        "(งಠ_ಠ)ง　σ( •̀ ω •́ σ)",
        r"( °ᴗ°)~ð (/❛o❛\)",
        "(｢• ω •)｢ (⌒ω⌒`)",
        "(っ•﹏•)っ ✴==≡눈٩(`皿´҂)ง"
    ],
    "武器":[
        "( ・∀・)・・・--------☆",
        "(/-_・)/D・・・・・------ →",
        "(^ω^)ノﾞ(((((((((●～*",
        "―⊂|=0ヘ(^^ )",
        "(/・・)ノ　　 (( く ((へ",
        "( -ω-)／占~~~~~",
        "○∞∞∞∞ヽ(^ー^ )",
        "(; ・_・)――――C",
        "(ಠ o ಠ)¤=[]:::::>",
        "―(T_T)→",
        "￢o(￣-￣ﾒ)",
        "(*＾＾)/~~~~~~~~~~◎",
        "((( ￣□)_／",
        "(ﾒ` ﾛ ´)︻デ═一",
        "( ´-ω･)︻┻┳══━一",
        "Q(`⌒´Q)",
        "✴==≡눈٩(`皿´҂)ง",
        "(ﾒ￣▽￣)︻┳═一"

    ],
    "魔法":[
        "(ノ ˘_˘)ノ　ζ|||ζ　ζ|||ζ　ζ|||ζ",
        "(ﾉ≧∀≦)ﾉ ‥…━━━★",
        "(ﾉ>ω<)ﾉ :｡･:*:･ﾟ’★,｡･:*:･ﾟ’☆",
        "(＃￣□￣)o━∈・・━━━━☆",
        "╰( ͡° ͜ʖ ͡° )つ──☆*:・ﾟ",
        "(ノ°∀°)ノ⌒･*:.｡. .｡.:*･゜ﾟ･*☆",
        "(⊃｡•́‿•̀｡)⊃━✿✿✿✿✿✿",
        "(∩ᄑ_ᄑ)⊃━☆ﾟ*･｡*･:≡( ε:)",
        "(/￣ー￣)/~~☆’.･.･:★’.･.･:☆",
        "(∩` ﾛ ´)⊃━炎炎炎炎炎"

    ],
    "食物":[
        "(っ˘ڡ˘ς)",
        "( o˘◡˘o) ┌iii┐",
        "(　’ω’)旦~~",
        "( ・ω・)o-{{[〃]}}",
        "♨o(>_<)o♨",
        "( ˘▽˘)っ♨",
        "(　・ω・)⊃-[二二]",
        "( ・・)つ―{}@{}@{}-",
        "( ・・)つ-●●●",
        "( o^ ^o)且 且(´ω`*)",
        "(*´з`)口ﾟ｡ﾟ口(・∀・ )",
        "(*´ー`)旦 旦(￣ω￣*)",
        "( ￣▽￣)[] [](≧▽≦ )",
        "( *^^)o∀*∀o(^^* )",
        "( ^^)_旦~~　 ~~U_(^^ )",
        "( ・・)つ―●○◎-",
        "-●●●-ｃ(・・ )",
        "(*￣▽￣)旦 且(´∀`*)"

    ],
    "音乐":[
        "ヾ(´〇`)ﾉ♪♪♪",
        "ヘ(￣ω￣ヘ)",
        "(〜￣▽￣)〜",
        "〜(￣▽￣〜)",
        "♪(/_ _ )/♪",
        "♪ヽ(^^ヽ)♪",
        "(ﾉ≧∀≦)ﾉ",
        "ヽ(o´∀`)ﾉ♪♬",
        "♪♬((d⌒ω⌒b))♬♪",
        "└(￣-￣└))",
        "((┘￣ω￣)┘",
        "√(￣‥￣√)",
        "／(￣▽￣)／",
        "＼(￣▽￣)＼",
        "┌(＾＾)┘",
        "└(＾＾)┐",
        "(￣▽￣)/♫•*¨*•.¸¸♪",
        "(^_^♪)",
        "(~˘▽˘)~",
        "~(˘▽˘~)",
        "~(˘▽˘)~",
        "(~‾▽‾)~",
        "(〜￣△￣)〜",
        "ヾ(⌐■_■)ノ♪",
        "乁( • ω •乁)",
        "(｢• ω •)｢",
        "⁽⁽◝( • ω • )◜⁾⁾",
        "✺◟( • ω • )◞✺",
        "(ˇ▽ˇ)ノ♪♬♫",
        "♪♪♪ ヽ(ˇ∀ˇ )ゞ",
        "( ˘ ɜ˘) ♬♪♫",
        "♬♫♪◖(● o ●)◗♪♫♬"
    ],
    "游戏":[
        "( ^^)p_____|_o____q(^^ )",
        "(／o^)/ °⊥ ＼(^o＼)",
        "!(;ﾟoﾟ)o/￣￣￣￣￣￣￣~ >ﾟ))))彡",
        "(／_^)／　　●　＼(^_＼)",
        "ヽ(^o^)ρ┳┻┳°σ(^o^)ノ",
        "( ノ-_-)ノﾞ_□ VS □_ヾ(^-^ヽ)",
        "ヽ(；^ ^)ノﾞ ．．．...___〇",
        "(=O*_*)=O Q(*_*Q)",
        "(˙ω˙)🎮(˙∀˙)🎮",
        "Ю　○三　＼(￣^￣＼)"

    ],
    "脸":[
        "( ͡° ͜ʖ ͡°)",
        "( ͡° ʖ̯ ͡°)",
        "( ͠° ͟ʖ ͡°)",
        "( ͡ᵔ ͜ʖ ͡ᵔ)",
        "( ಠ ʖ̯ ಠ)",
        "( ͡ಠ ʖ̯ ͡ಠ)",
        "( ఠ ͟ʖ ఠ)",
        "( . •́ _ʖ •̀ .)",
        "( ಠ ͜ʖ ಠ)",
        "( ಥ ʖ̯ ಥ)",
        "( ͡• ͜ʖ ͡• )",
        "( ･ิ ͜ʖ ･ิ)",
        "(ʘ ͟ʖ ʘ)",
        "(ʘ ʖ̯ ʘ)",
        "(≖ ͜ʖ≖)",
        "( ͡ ͜ʖ ͡ )",
        "(ʘ ͜ʖ ʘ)",
        "(;´༎ຶٹ༎ຶ`)"
    ]



}

def choose_color():
    # 创建一个新的顶级窗口来显示字体列表
        color_window = tk.Toplevel(root)
        color_window.geometry("300x150+150+250")  # 设置窗口大小为300x200，并将左上角定位在屏幕坐标（150，250）
        color_window.title("颜色参数")

        # 使用Entry组件来代替Label，并设置为只读
        entry_rgb = tk.Entry(color_window, width=20, state='readonly')
        entry_hex = tk.Entry(color_window, width=20, state='readonly')
        entry_rgb.pack(pady=10)
        entry_hex.pack()

        color_code = colorchooser.askcolor(title="选择颜色")
        if color_code:
            rgb, hex_color = color_code
            entry_rgb.config(state='normal')  # 设置为可编辑状态
            entry_rgb.delete(0, tk.END)  # 清空之前的内容
            entry_rgb.insert(0, f"RGB: {rgb}")  # 插入新的内容
            entry_rgb.config(state='readonly')  # 设置为只读状态

            entry_hex.config(state='normal')  # 设置为可编辑状态
            entry_hex.delete(0, tk.END)  # 清空之前的内容
            entry_hex.insert(0, f"Hex: {hex_color}")  # 插入新的内容
            entry_hex.config(state='readonly')  # 设置为只读状态

    # # 标签用于显示选择的颜色的RGB和16进制格式
    #     label_rgb = tk.Label(color_window, text="RGB: ")
    #     label_rgb.pack(pady=10)

    #     label_hex = tk.Label(color_window, text="16进制: ")
    #     label_hex.pack(pady=10)

    # # 弹出颜色选择器
    #     color_code = colorchooser.askcolor(title="选择颜色")
    #     print("yansss",color_code)
    #     if color_code:
    #         rgb, hex_color = color_code
    #         label_rgb.config(text=f"RGB: {rgb}")
    #         label_hex.config(text=f"16进制: {hex_color}")

def get_font_list():
    # 获取系统中可用的字体列表
    system_fonts = font.families()
    return system_fonts

def copy_font_name(event):
    # 复制选中的字体名
    widget = event.widget
    selected_index = widget.curselection()
    if selected_index:
        font_name = widget.get(selected_index[0])
        root.clipboard_clear()
        root.clipboard_append(font_name)
        # messagebox.showinfo("复制成功", f"已复制字体名 '{font_name}'")
        # 创建顶层窗口
        top = tk.Toplevel(root)
        top.title("字体选择与预览")
        top.geometry("300x150")
                
        # 创建 Label 小部件并设置字体
        message = ("复制成功", f"已复制字体名 '{font_name}'")
        msg_label = tk.Label(top, text=message)
        msg_label.pack(pady=10)
        Font_Preview = tk.Label(top, text="字体预览--Font Preview", font=(font_name, 12))
        Font_Preview.pack(pady=10)
    
        # 创建 Button 小部件关闭消息框
        ok_button = tk.Button(top, text="确定", command=top.destroy)
        ok_button.pack(pady=5)

       

def show_font_list():
    # 创建一个新的顶级窗口来显示字体列表
    font_list_window = tk.Toplevel(root)
    font_list_window.title("可用字体列表")

    # Frame 用于放置字体列表和滚动条
    frame_font_list = tk.Frame(font_list_window)
    frame_font_list.pack(padx=20, pady=20)

    # 创建滚动条
    scrollbar = tk.Scrollbar(frame_font_list)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 创建 Listbox 用于显示字体列表
    font_listbox = tk.Listbox(frame_font_list, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, width=40, height=10)
    scrollbar.config(command=font_listbox.yview)
    
    # 获取并显示字体列表
    fonts = get_font_list()
    for font_name in fonts:
        font_listbox.insert(tk.END, font_name)
    # 
    font_listbox.pack(side=tk.LEFT)

    # 定义鼠标移动事件处理函数
    def on_mouse_move(event):
        widget = event.widget
        index = widget.nearest(event.y)
        if index >= 0:
            font_name = widget.get(index)
            preview_label.config(font=(font_name, 16), text=font_name) 

    # 绑定双击事件，复制选中的字体名
    font_listbox.bind("<Double-Button-1>", copy_font_name)
    
    # 绑定鼠标移动事件
    font_listbox.bind("<Motion>", on_mouse_move)

    preview_label = tk.Label(font_list_window, text="Preview Text", font=("Arial", 20))
    preview_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    

    

def gif_to_jpg_converter():
    # 创建一个Tkinter根窗口并隐藏它
    root = tk.Tk()
    root.withdraw()

    # 弹出文件选择对话框，选择GIF文件
    gif_path = filedialog.askopenfilename(title="选择一个GIF文件", filetypes=[("GIF files", "*.gif")])
    print(gif_path)
    # 如果选择了文件，执行拆解操作
    if gif_path:
        output_folder = os.getcwd()  # 使用当前工作目录
        # 打开GIF图像
        with Image.open(gif_path) as im:
            # 遍历每一帧
            for frame in range(im.n_frames):
                im.seek(frame)
                frame_image = im.convert('RGB')  # 将图像转换为RGB模式
                frame_path = os.path.join(output_folder, f"frame_{frame}.jpg")
                frame_image.save(frame_path, format="JPEG")
                print(f"Saved {frame_path}")
        print(f"所有帧已保存到 {output_folder}")
    else:
        print("未选择任何文件")

def create_gif_from_images():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
        

    # 弹出文件选择对话框让用户选择图片
    filetypes = [("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    image_files = filedialog.askopenfilenames(title="Select Images", filetypes=filetypes)
    
    if not image_files:
        print("No images selected")
        return
    
    # 打开所有选中的图片
    images = [Image.open(img) for img in image_files]
    
    # 弹出保存对话框让用户选择保存GIF文件的位置和名称
    gif_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])
    
    if not gif_path:
        print("Save cancelled")
        return
    
    # 保存为GIF图
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=100,  # 每帧显示时间（毫秒）
        loop=0  # 循环次数，0表示无限循环
    )
    
    print(f"GIF saved at {gif_path}")

def time_change():
    # root = tk.Tk()
    # root.withdraw()  # 隐藏主窗口
    root_ = tk.Toplevel(root)  # 创建新的顶级窗口
    label = tk.Label(root_, text="新窗口")
    label.pack

    # 将时间戳转换为datetime对象
    def change_():
     # 清空 Entry 输入框
     entry__time.delete(0, tk.END)
     timestamp = int(entry_time.get())
     
     dt = datetime.datetime.fromtimestamp(timestamp)
    
    # 格式化datetime对象为字符串
     formatted_time = dt.strftime("%m/%d/%y %H:%M:%S")
     entry__time.insert(0, str(formatted_time))
    
    def change():
        entry_time.delete(0, tk.END)
        timestamp_ = entry__time.get()
        # 定义日期时间字符串的格式
        date_format = "%m/%d/%y %H:%M:%S"
        # 将字符串转换为datetime对象
        dt = datetime.datetime.strptime(timestamp_, date_format)
        # 将datetime对象转换为时间戳
        timestamp = int(dt.timestamp())
        entry_time.insert(0, str(timestamp))

    # 第一行：创建标签和输入框
    top_frame = tk.Frame(root_)
    top_frame.pack(pady=10)

    label_time = tk.Label(top_frame, text="时间_数值 ")
    label_time.pack(side=tk.LEFT,padx=10,pady=20)

    # 创建 Entry 小部件，并设置默认值
    entry_time = tk.Entry(top_frame)
    default_value = "1719822360"
    entry_time.insert(0, default_value)
    entry_time.pack(side=tk.LEFT,padx=10,pady=20)

    btn_time = tk.Button(top_frame, text="时间——数值转换", command=change_)
    btn_time.pack(side=tk.LEFT,padx=10,pady=20) 


    # 第二行：创建结果显示的标签和输入框
    middle_frame = tk.Frame(root_)
    middle_frame.pack(pady=10)

    label__time = tk.Label(middle_frame,text="时间_通用")
    label__time.pack(side=tk.LEFT,padx=10,pady=20)
    # 创建 Entry 小部件，并设置默认
    entry__time = tk.Entry(middle_frame)
    default_value = "07/01/24 16:26:00"
    entry__time.insert(0, default_value)
    entry__time.pack(side=tk.LEFT,padx=10,pady=20)
    
    btn__time = tk.Button(middle_frame, text="时间——通用转换", command=change)
    btn__time.pack(side=tk.LEFT,padx=10,pady=20) 

def kaomoji_choose():
    # root = tk.Tk()
    # root.withdraw()  # 隐藏主窗口
    root_moji = tk.Toplevel(root)  # 创建新的顶级窗口
    root_moji.geometry("300x300")
    label = tk.Label(root_moji, text="kaomoji")
    label.pack

   # 标签
    label = ttk.Label(root_moji, text="Select a district:")
    label.pack(pady=10)

    # 下拉框
    selected_district = tk.StringVar(value=list(kaomojis.keys())[0])  # 设置默认值为第一个键
    combobox = ttk.Combobox(root_moji, textvariable=selected_district)
    combobox['values'] = list(kaomojis.keys())
    combobox.pack(pady=10)

    # 输出结果的Entry
    result_entry = ttk.Entry(root_moji, state='readonly')
    result_entry.pack(pady=10)

    # 输出结果的标签
    result_label = ttk.Label(root_moji, text="")
    result_label.pack(pady=10)

    # 按钮点击事件
    def show_random_value():
        district = selected_district.get()
        if district in kaomojis:
            random_value = random.choice(kaomojis[district])
            result_entry.config(state='normal')
            result_entry.delete(0, tk.END)
            result_entry.insert(0, f" {random_value}") 
            result_entry.config(state='readonly')

    def copy_to_clipboard():
        root_moji.clipboard_clear()
        root_moji.clipboard_append(result_entry.get())
        root_moji.update()  # 更新剪贴板
    # 按钮
    button = ttk.Button(root_moji, text="Show", command=show_random_value)
    button.pack(pady=10) 

    copy_button = ttk.Button(root_moji, text="Copy", command=copy_to_clipboard)
    copy_button.pack(pady=10)

def random_map():  
    def generate_random_location():  
        # 生成随机经纬度（这里只是示例，实际范围可能需要根据需要调整）  
        # 中国的经纬度范围大致是从东经73°33′至135°05′，纬度从3°51′N至53°33′N。
        lat = round(uniform(18.16, 53.33) ,6) # 纬度范围：-90到90  
        lon = round(uniform(73.33, 135.05),6)  # 经度范围：-180到180  
        # 高德API Key
        load_dotenv()
        
        YOUR_AMAP_API_KEY = os.getenv('API_KEY')
        
        # 经纬度
        YOUR_LATITUDE = lat
        YOUR_LONGITUDE = lon
        
        # 构建请求URL
        # url = f'https://restapi.amap.com/v3/geocode/regeo?key={YOUR_AMAP_API_KEY}&location={YOUR_LATITUDE},{YOUR_LONGITUDE}'
        url = f'https://restapi.amap.com/v3/geocode/regeo?location={YOUR_LONGITUDE},{YOUR_LATITUDE}&key={YOUR_AMAP_API_KEY}&extensions=base' 
        static_map_url = f"https://restapi.amap.com/v3/staticmap?location={YOUR_LONGITUDE},{YOUR_LATITUDE}&zoom=2&size=750*300&markers=mid,,A:{YOUR_LONGITUDE},{YOUR_LATITUDE}&key={YOUR_AMAP_API_KEY}"
        # 发送请求
        response = requests.get(url)
        print("高德返回的地址",response.text)
        
        response1 = requests.get(static_map_url)
        binary_data = response1.content

        # 将二进制数据转换为PIL图像
        image = Image.open(io.BytesIO(binary_data))

        # 解析JSON响应
        data = response.json()
        # 检查状态码，确保请求成功
        if data['status'] == '1':
                # 打印详细地址
                formatted_address = data['regeocode']['formatted_address']
                print(formatted_address)
        else:
                print('请求失败，错误码：', data['infocode'])
        return formatted_address,lat,lon,image,response1,data

    def check():
        formatted_address,lat,lon,image,response1,data =generate_random_location()
        
        while not formatted_address:
            print("地址为查询到，正在重试...")
            formatted_address,lat,lon,image,response1,data =generate_random_location()
        
        return formatted_address,lat,lon,image,response1,data
        
    formatted_address,lat,lon,image ,response1,data=check()
    
    # Create a map using Folium  
    map = folium.Map(location=[lat, lon], zoom_start=12)  
            
    # Add a marker for the geocoded location  
    folium.Marker([lat, lon], popup=formatted_address).add_to(map)  
            
    # Save the map to an HTML file for visualization  
    # 保存地图到 map.html 文件
    file_path = 'map.html'
    map.save(file_path)
    # 将图片保存到本地
    with open('go_map.png', 'wb') as f:
        f.write(response1.content)
        print("go_map.png已保存")        
    # Display the map  
 
    print("地图已经生成")
    print(f"Random Latitude: {lat}, Longitude: {lon}")  
    # 自动在默认浏览器中打开 map.html 文件
    root_map = tk.Toplevel(root)  # 创建新的顶级窗口
    # label_m = ttk.Label(root_map, text=(f"经度: {lat}, 纬度: {lon}"))
    # label_m.pack()
    # 创建一个 Text 部件
    text = tk.Text(root_map, height=2, width=40)
    text.tag_configure("center", justify='center')
    # 设置字体格式
    text.tag_configure("font", font=('黑体', 12))
    text.pack()
    text.insert(tk.END,f"经度: {lat}, 纬度: {lon}",("center","font")) 

    # 初始颜色和闪烁状态
    def cho_color():
        color_=random.choice(["red","blue","green","#ff8080","#ff00ff"])
        label_test.config(foreground=color_)  # 更新Label的文本颜色
        root_map.after(1000,cho_color)
        return color_   
    
    custom_font = ('Arial', 14, 'bold')
    label_test = ttk.Label(root_map, text="Goooooo", font=custom_font, justify='center',foreground="blue")
    label_test.pack()

    
    cho_color()

    formatted_address1 = data['regeocode']['formatted_address']
    print("输出地址为",formatted_address1)

    # label1 = ttk.Label(root_map, text=formatted_address1)
    # label1.pack()
    
    text1 = tk.Text(root_map, height=2, width=60)
    text1.tag_configure("center", justify='center')
    # 设置字体格式
    text1.tag_configure("font", font=('黑体', 12))
    # 设置居中格式
    text1.pack()
    text1.insert(tk.END,formatted_address1,("center","font")) 

    # 将PIL图像转换为Tkinter兼容的图像
    tk_image = ImageTk.PhotoImage(image)
    print("已经转化",tk_image)
    # 创建一个标签用于显示图像
    label2 = tk.Label(root_map, image=tk_image)
    label2.pack()
    # 保持对tk_image的引用，以防止其被垃圾回收
    label2.image = tk_image
    def show_map():
        webbrowser.open(file_path)
     # 按钮
    button = tk.Button(root_map, text="Show Map", command=show_map)
    button.pack(pady=10) 

def install_fonts():
    # root = tk.Tk()
    # root.withdraw()  # 隐藏主窗口
    root_fonts = tk.Toplevel(root)  # 创建新的顶级窗口

    # Function to retrieve all installed fonts
    def get_installed_fonts():
        return fm.findSystemFonts()

   
    # Create a Canvas widget to hold the Text widgets
    canvas = tk.Canvas(root_fonts)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar to the canvas
    scrollbar = ttk.Scrollbar(root_fonts, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the Text widgets
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    # Get all installed fonts
    font_list = get_installed_fonts()

    # Function to create a new text widget for each font
    def create_font_example(font_name, parent):
        text_widget = tk.Text(parent, width=50, height=2, wrap=tk.WORD)
        text_widget.pack(padx=10, pady=5)
        text_widget.tag_configure("font", font=(font_name, 12))
        text_widget.insert(tk.END, f"{font_name}---示例---", "font")

    # Create a text widget for each font example
    for font_path in font_list:
        font_name = fm.FontProperties(fname=font_path).get_name()
        create_font_example(font_name, frame)

    # Configure the canvas to resize with the frame
    frame.update_idletasks()  # Update frame size
    canvas.config(scrollregion=canvas.bbox(tk.ALL))  # Set scroll region   

def pixel_art():
    # def generate_char_pixel_art(char, font_path, font_size=100, image_size=(200, 200), pixel_size=20, color=None):
    #     # 创建一个高分辨率的空白图像
    #     image = Image.new('RGB', image_size, 'white')
    #     draw = ImageDraw.Draw(image)
    #     font = ImageFont.truetype(font_path, font_size)

    #     # 获取文字边界框并计算大小
    #     bbox = draw.textbbox((0, 0), char, font=font)
    #     text_width = bbox[2] - bbox[0]
    #     text_height = bbox[3] - bbox[1]
    #     position = ((image_size[0] - text_width) // 2, (image_size[1] - text_height) // 2)
        
    #     # 在图像上绘制文字
    #     if color is None:
    #         color = (0, 0, 0)  # 默认黑色
    #     draw.text(position, char, fill=color, font=font)
        
    #     # 将图像缩放为像素艺术效果
    #     small_image_size = (image_size[0] // pixel_size, image_size[1] // pixel_size)
    #     pixel_image = image.resize(small_image_size, Image.NEAREST)
    #     pixel_image = pixel_image.resize(image_size, Image.NEAREST)
    #     return pixel_image

    # def generate_sentence_pixel_art_animation(sentence, font_path, output_path='animation.gif', font_size=100, image_size=(200, 200), pixel_size=20):
    #     colors = [
    #         (255, 0, 0),    # 红色
    #         (0, 255, 0),    # 绿色
    #         (0, 0, 255),    # 蓝色
    #         (255, 255, 0),  # 黄色
    #         (255, 0, 255),  # 紫色
    #         (0, 255, 255)   # 青色
    #     ]
        
    #     frames = []
    #     for char in sentence:
    #         color = random.choice(colors)
    #         char_image = generate_char_pixel_art(char, font_path, font_size, image_size, pixel_size, color)
    #         frames.append(char_image)
        
    #     # 保存为GIF动画
    #     frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=500, loop=0)
    #     print("animation.gif已经输出至:",output_path)
    #     messagebox.showinfo("提示","animation.gif已输出")



    # # 创建主窗口
    # root_pixart = tk.Toplevel(root)  # 创建新的顶级窗口

    # font__path = ttk.Entry(root_pixart)
    # default_value = "simhei"
    # #  "STXingkai" "LiSu"  "HarmonyOS Sans SC" "STHupo"    "STXinwei"  "FZShuTi"
    # font__path.insert(0, default_value)
    # font__path.pack(side=tk.LEFT,padx=10,pady=20)
    # # font_path = font__path.get()

    # font__word = ttk.Entry(root_pixart)
    # default_value = "你好，世界！"
    # #  "STXingkai" "LiSu"  "HarmonyOS Sans SC" "STHupo"    "STXinwei"  "FZShuTi"
    # font__word.insert(0, default_value)
    # font__word.pack(side=tk.LEFT,padx=10,pady=20)
    # # font_word = font__word.get()
    # # print(font_word)

    # # 使用下载的字体文件路径
    # # font_path = 'simhei'  # 请确保字体文件在当前工作目录中
    # #  "STXingkai" "LiSu"  "HarmonyOS Sans SC" "STHupo"    "STXinwei"  "FZShuTi"

    # # 生成一句话的像素图动画，使用下载的黑体字体文件和随机颜色
    # def start_wordani():
    #     font_word = font__word.get()
    #     print(font_word)
    #     font_path = font__path.get()
    #     print(font_path)

    #     generate_sentence_pixel_art_animation(font_word, font_path, font_size=500, image_size=(600, 600), pixel_size=5)


    # btn_show_font_list = tk.Button(root_pixart, text="开始生成", command=start_wordani)
    # btn_show_font_list.pack(side=tk.LEFT,padx=20,pady=20)
    root_pixart = tk.Toplevel(root)  # 创建新的顶级窗口
    font__word = ttk.Entry(root_pixart)
    default_value = "你好，世界！"
    #  "STXingkai" "LiSu"  "HarmonyOS Sans SC" "STHupo"    "STXinwei"  "FZShuTi"
    font__word.insert(0, default_value)
    font__word.pack(side=tk.LEFT,padx=10,pady=20)
    def creat():
    # 准备数据
        # 准备数据
        text = font__word.get()
        font_path = "simhei"  # 使用思源黑体字体
        font_size = 100
        output_gif = "output.gif"
        frame_duration = 500  # 每秒播放几帧

        # 创建字体对象
        font = ImageFont.truetype(font_path, font_size)

        # 创建随机颜色
        def generate_random_colors(n):
            
            return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n)]

        # 创建像素风格的字体图像
        def create_pixel_font_image(char, font, colors, scale=2, image_size=(500, 500)):   #像素点大小设置
            bbox = font.getbbox(char)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            
            # 确保宽度和高度大于零
            if text_width <= 0 or text_height <= 0:
                return Image.new('RGB', image_size, (255, 255, 255))
            
            image = Image.new('RGB', (text_width, text_height), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            draw.text((-bbox[0], -bbox[1]), char, font=font, fill=(0, 0, 0))
            
            # 缩小到像素风格
            small_width, small_height = max(1, text_width // scale), max(1, text_height // scale)
            pixel_image = image.resize((small_width, small_height), Image.NEAREST)
            pixel_data = np.array(pixel_image)
            
            # 给每个像素点着不同的颜色
            for x in range(pixel_data.shape[1]):
                for y in range(pixel_data.shape[0]):
                    if pixel_data[y, x, 0] < 128:  # 如果像素是黑色（字符的一部分）
                        pixel_data[y, x] = colors[(x + y) % len(colors)]
            
            pixel_image = Image.fromarray(pixel_data)
            pixel_image = pixel_image.resize(image_size, Image.NEAREST)
            
            return pixel_image

        # 设置统一图像尺寸
        image_size = (200, 200)

        # 创建每一帧
        frames = []
        for i in range(len(text)):
            char = text[i]
            
            # 创建一个新的图像
            image = Image.new('RGB', image_size, (255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # 生成随机颜色
            colors = generate_random_colors(image_size[0] * image_size[1])
            
            # 创建字符的像素风格图像
            char_image = create_pixel_font_image(char, font, colors, image_size=image_size)
            image.paste(char_image, (0, 0))
            
            # 将图像转换为数组并加入帧列表
            frames.append(np.array(image))
            
        # 保存为GIF
        imageio.mimsave(output_gif, frames, "gif",duration=frame_duration ,loop =0)#loop=0 标识循环播放
        messagebox.showinfo("提示","output_gif 已输出")
        print("okkkkkkkkkkkkkkkkkkkkkkk")



    btn_show_font_list = tk.Button(root_pixart, text="开始生成", command=creat)
    btn_show_font_list.pack(side=tk.LEFT,padx=20,pady=20) 
       

def pixel_art1():

    root_pix1 = tk.Toplevel(root)  # 创建新的顶级窗口

    pix_text = ttk.Entry(root_pix1)
    default_value = "你好，世界！"
    #  "STXingkai" "LiSu"  "HarmonyOS Sans SC" "STHupo"    "STXinwei"  "FZShuTi"
    pix_text.insert(0, default_value)
    pix_text.pack(side=tk.LEFT,padx=10,pady=20)

    # 准备数据
    
    font_path = "simhei"  # 替换为实际的字体文件路径
    font_size = 100
    output_gif = "output.gif"
    frame_duration = 500  # 每帧持续时间，单位为秒

    def creat_gif():
        text = pix_text.get()
        # 创建字体对象
        font = ImageFont.truetype(font_path, font_size)

        # 创建随机颜色
        def generate_random_colors(n):
            return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n)]


        # 创建像素风格的字体图像
        def create_pixel_font_image(char, font, colors, scale=3):
            bbox = font.getbbox(char)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            
            # 确保宽度和高度大于零
            if text_width <= 0 or text_height <= 0:
                return Image.new('RGB', (scale, scale), (255, 255, 255))
            
            image = Image.new('RGB', (text_width, text_height), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            draw.text((-bbox[0], -bbox[1]), char, font=font, fill=(0, 0, 0))
            
            # 缩小到像素风格
            small_width, small_height = max(1, text_width // scale), max(1, text_height // scale)
            pixel_image = image.resize((small_width, small_height), Image.NEAREST)
            pixel_data = np.array(pixel_image)
            
            # 给每个像素点着不同的颜色
            for x in range(pixel_data.shape[1]):
                for y in range(pixel_data.shape[0]):
                    if pixel_data[y, x, 0] < 128:  # 如果像素是黑色（字符的一部分）
                        pixel_data[y, x] = colors[(x + y) % len(colors)]
            
            pixel_image = Image.fromarray(pixel_data)
            return pixel_image.resize((text_width, text_height), Image.NEAREST)

        # 计算图像尺寸
        bbox = font.getbbox(text)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        image_size = (text_width, text_height)

        # 创建每一帧
        frames = []
        for i in range(len(text)):
            # 创建一个新的图像
            image = Image.new('RGB', image_size, (255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # 逐个字符绘制
            x_offset = 0
            for j in range(i + 1):
                char = text[j]
                colors = generate_random_colors(text_width * text_height)  # 为每个字符生成随机颜色
                char_image = create_pixel_font_image(char, font, colors)
                image.paste(char_image, (x_offset, 0))
                x_offset += char_image.width
            
            # 将图像转换为数组并加入帧列表
            frames.append(np.array(image))

        # 保存为GIF
        imageio.mimsave(output_gif, frames, duration=frame_duration)
        

        messagebox.showinfo("提示","GIF图已经输出")
        

    btn_show_font_list = tk.Button(root_pix1, text="开始生成", command=creat_gif)
    btn_show_font_list.pack(side=tk.LEFT,padx=20,pady=20)

# 创建主窗口
root = tk.Tk()
root.title("TOOl")

# 当窗口关闭时，调用关闭函数
def on_closing():
    root.quit()
    root.destroy()
    sys.exit()

# 绑定关闭事件
root.protocol("WM_DELETE_WINDOW", on_closing)

# # 创建按钮框架
# frame = tk.Frame(root)
# frame.pack(padx=10, pady=10)

# 第一行：创建标签和输入框
top__frame = tk.Frame(root)
top__frame.pack(pady=10)

# 添加按钮用于打开颜色选择器
btn_choose_color = tk.Button(top__frame, text="选择颜色", command=choose_color)
btn_choose_color.pack(side=tk.LEFT,padx=10,pady=20) 


# 添加按钮用于显示字体列表
btn_show_font_list = tk.Button(top__frame, text="显示字体列表", command=show_font_list)
btn_show_font_list.pack(side=tk.LEFT,padx=10,pady=20)

# 添加按钮用于显示字体列表
btn_show_font_list = tk.Button(top__frame, text="GIF拆解", command=gif_to_jpg_converter)
btn_show_font_list.pack(side=tk.LEFT,padx=20,pady=20)

# 添加按钮用于显示字体列表
btn_show_font_list = tk.Button(top__frame, text="GIF合成", command=create_gif_from_images)
btn_show_font_list.pack(side=tk.LEFT,padx=20,pady=20)

btn_show_font_list = tk.Button(top__frame, text="时间格式转换", command=time_change)
btn_show_font_list.pack(side=tk.LEFT,padx=10,pady=20) 

btn_show_font_list = tk.Button(top__frame, text="颜文字选择", command=kaomoji_choose)
btn_show_font_list.pack(side=tk.LEFT,padx=10,pady=20) 

# 第二行：创建标签和输入框
mid__frame = tk.Frame(root)
mid__frame.pack(pady=10)

btn_show_font_list = tk.Button(mid__frame, text="？GO！", command=random_map)
btn_show_font_list.pack(side=tk.LEFT,padx=10,pady=20) 

btn_show_font_list = tk.Button(mid__frame, text="查询已安装字体", command=install_fonts)
btn_show_font_list.pack(side=tk.LEFT,padx=10,pady=20) 

btn_show_font_list = tk.Button(mid__frame, text="像素字体动图", command=pixel_art)
btn_show_font_list.pack(side=tk.LEFT,padx=10,pady=20) 

btn_show_font_list = tk.Button(mid__frame, text="像素字体动图1", command=pixel_art1)
btn_show_font_list.pack(side=tk.LEFT,padx=10,pady=20) 


root.quit()

# 运行主循环
root.mainloop()
