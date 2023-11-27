# -*- coding: utf-8 -*-
# @Author  : LouJingshuo
# @E-mail  : 3480339804@qq.com
# @Time    : 2023/9/24 13:59
# @Function: Infringement must be investigated, please indicate the source of reproduction!

from Settings import POKER_WEIGHT


class Poker:
    poker_kind = None
    poker_weight = None

    def __init__(self, poker_kind):
        self.poker_kind = poker_kind
        self.poker_weight = POKER_WEIGHT[poker_kind]
