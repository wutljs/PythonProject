# -*- coding: utf-8 -*-
# @Author  : LouJingshuo
# @E-mail  : 3480339804@qq.com
# @Time    : 2023/9/25 15:03
# @Function: Infringement must be investigated, please indicate the source of reproduction!

from Poker import Poker
from Player import Player
from Settings import POKER_WEIGHT


class Client:
    pokers = []
    players = []

    def init_game(self):
        # 初始化扑克牌
        for poker_key in list(POKER_WEIGHT.keys()):
            if poker_key in ['black_10', 'red_10']:
                self.pokers += [Poker(poker_key) for _ in range(2)]
            elif poker_key in ['small_joker', 'big_joker', 'red_peach_6', 'red_square_6']:
                self.pokers += [Poker(poker_key)]
            else:
                self.pokers += [Poker(poker_key) for _ in range(4)]

        # 初始化玩家
        self.players = [Player() for _ in range(4)]

    def deal_pokers(self):
        pass

    def playing(self):
        pass

    def close_pokers(self):
        pass
