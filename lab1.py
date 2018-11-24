import random
import time
import numpy as np
from itertools import product

class Game():
    """docstring for ClassName"""
    def __init__(self, player, enemy, time=2):
        self.time = time
        self.player = player
        self.enemy = enemy
        self.exit_pos = [4,4]
        self.S_dim = self.time*5*6*5*6 # state dimension
        self.init_v = np.zeros(self.S_dim) # initial state values
        self.init_p = np.ones((self.S_dim,len(self.player.actions))) * \
                      1.0/len(self.player.actions) # initial policy
        self.r_not_escaped = -1.0
        self.r_eaten = -1000.0
        self.r_escaped = 0.0
        self.pij = self.calc_pij()
        self.rewards = self.calc_rewards()

    def tostate(self, t, pos_p, pos_e):
        return 900*t + 30*(pos_p[0]*6 + pos_p[1]) + pos_e[0]*6 + pos_e[1]

    def fromstate(self, s):
        T = s // 900
        rem = s % 900
        pos_p = rem // 30
        y_p = pos_p // 6
        x_p = pos_p % 6
        rem2 = rem % 30
        y_e = rem2 // 6
        x_e = rem2 % 6
        return T, [y_p, x_p], [y_e, x_e]
    
    def calc_pij(self):
        pij = np.zeros((self.S_dim,self.S_dim,len(self.player.actions)))
        ''' Iterates through time, player_pos, enemy_pos and new_enemy_pos, because we know that new_time = time + 1 and we know new_player_pos from player.transition function.'''
        iters = [self.time, 5, 6, 5, 6, 5, 6]
        ranges = [range(x) for x in iters]
        for t, y_p, x_p, y_e, x_e, yn_e, xn_e in product(*ranges):
            for idx, action in enumerate(self.player.actions):
                S = self.tostate(t,[y_p,x_p],[y_e,x_e])
                if t < self.time-1:
                    posn_p = self.player.transition([y_p,x_p], action)
                    prob = self.enemy.transition([y_e,x_e],[yn_e,xn_e])
                    Sn = self.tostate(t+1, posn_p, [yn_e,xn_e])
                    pij[S,Sn,idx] = prob
                ''' terminal states are recursive: final time step, minotaur kills player, player escapes maze '''
                if t == self.time-1 or \
                   y_p == y_e and x_p == x_e or \
                   [y_p, x_p] == self.exit_pos:
                    pij[S,S,idx] = 1.0
        return pij

    def test_pij(self):
        pass

    def calc_rewards(self):
        rewards = np.ones(self.S_dim)*self.r_not_escaped
        iters = [self.time, 5, 6, 5, 6]
        ranges = [range(x) for x in iters]
        for t, y_p, x_p, y_e, x_e in product(*ranges):
            S = self.tostate(t,[y_p,x_p],[y_e,x_e])
            if t == self.time-1 or \
               y_p == y_e and x_p == x_e:
                rewards[S] = self.r_eaten
            if [y_p, x_p] == self.exit_pos:
                rewards[S] = self.r_escaped
        return rewards

    def test_rewards(self):
        iters = [self.time, 5, 6, 5, 6]
        ranges = [range(x) for x in iters]
        for t, y_p, x_p, y_e, x_e in product(*ranges):
            S = self.tostate(t,[y_p,x_p],[y_e,x_e])
            print('t = {}, player = [{},{}], minotaur = [{},{}], reward = {}'.format(t, y_p, x_p, y_e, x_e, self.rewards[S]))

    def find_optimal(self):
        pass

    def display_board(self):
        vis_board = np.empty((5,6), dtype='str')
        vis_board[:] = ' '
        if self.player.pos == self.enemy.pos:
            vis_board[tuple(self.player.pos)] = 'B' # Both in same position
        else:
            vis_board[tuple(self.player.pos)] = 'P' # Player
            vis_board[tuple(self.enemy.pos)] = 'M' # Minotaur
        print(' ' + '_'*8 + ' ')
        print('|{}{}|{}{} {}{}|'.format(*vis_board[0,:]))
        print('|{}{}|{}{}|{}{}|'.format(*vis_board[1,:]))
        print('|{}{}|{}{}|{}\u0305{}\u0305|'.format(*vis_board[2,:]))
        print('|{}{} {}{} {}{}|'.format(*vis_board[3,:]))
        print('|{}{}\u203e{}\u0305{}\u0305|\u0305{}\u0305{}\u0305|'.format(
            *vis_board[4,:]))
        print(' ' + '\u203e'*8 + ' ')
        time.sleep(0.3)


class Player():
    """docstring for ClassName"""
    def __init__(self):
        self.pos = [0,0]
        self.actions = ['U','D','L','R','S']
        self.actdict = {'U': (-1,0),
                        'D': (1,0),
                        'L': (0,-1),
                        'R': (0,1),
                        'S': (0,0)}

    def transition(self, pos, action):
        # ACCEPTS: old position, action
        # RETURNS: new position
        # NOTE: assumes invalid action returns same position!
        y, x = pos[0], pos[1]
        # edge proximity actions
        if (y == 0 and action == 'U') or \
           (y == 4 and action == 'D') or \
           (x == 0 and action == 'L') or \
           (x == 5 and action == 'R'):
           pos_new = [y,x]
        # wall proximity actions going left to right, top to bottom
        elif (x == 1 and y < 3 and action == 'R') or \
             (x == 2 and y < 3 and action == 'L') or \
             (x == 3 and y > 0 and y < 3 and action == 'R') or \
             (x == 4 and y > 0 and y < 3 and action == 'L') or \
             (y == 1 and x > 3 and action == 'D') or \
             (y == 2 and x > 3 and action == 'U') or \
             (y == 3 and x > 0 and x < 5 and action == 'D') or \
             (y == 4 and x > 0 and x < 5 and action == 'U') or \
             (y == 4 and x == 3 and action == 'R') or \
             (y == 4 and x == 4 and action == 'L'):
             pos_new = [y,x]
        else:
            pos_new = [y + x for y, x in zip(pos, self.actdict[action])]
        return pos_new

    def test_transition(self):
        for y in range(5):
            for x in range(6):
                for action in self.actions:
                    yn, xn = Gary.transition([y, x], action)
                    print('[{},{}] > [{},{}] via {}'.format(y,x,yn,xn,action))


class Enemy():
    """docstring  for ClassName"""
    def __init__(self, can_same=False):
        self.pos = [4,4]
        self.can_same = can_same # Can it remain in same place, see transition

    def transition(self, oldpos, newpos):
        # ACCEPTS: old position, new position
        # RETURNS: probability of transition
        # NOTE: assumes invalid action results in same position!
        y, x = oldpos[0], oldpos[1]
        yn, xn = newpos[0], newpos[1]
        # CENTRAL RECTANGLE POSITIONS
        if y > 0 and y < 4 and x > 0 and x < 5:
            if (yn == (y + 1) and xn == x) or \
               (yn == (y - 1) and xn == x) or \
               (yn == y and xn == (x + 1)) or \
               (yn == y and xn == (x - 1)):
                prob = 1.0/(4 + self.can_same)
            elif (yn == y and xn == x):
                prob = 1 - (4.0/(4 + self.can_same))
            else:
                prob = 0.0
        # EDGE POSITIONS
        elif x == 0 and y > 0 and y < 4:
            if (yn == (y + 1) and xn == x) or \
               (yn == (y - 1) and xn == x) or \
               (yn == y and xn == (x + 1)):
                prob = 1.0/(4 + self.can_same)
            elif (yn == y and xn == x):
                prob = (1.0 + self.can_same)/(4 + self.can_same)
            else:
                prob = 0.0
        elif x == 5 and y > 0 and y < 4:
            if (yn == (y + 1) and xn == x) or \
               (yn == (y - 1) and xn == x) or \
               (yn == y and xn == (x - 1)):
                prob = 1.0/(4 + self.can_same)
            elif (yn == y and xn == x):
                prob = (1.0 + self.can_same)/(4 + self.can_same)
            else:
                prob = 0.0
        elif y == 0 and x > 0 and x < 5:
            if (yn == (y + 1) and xn == x) or \
               (yn == y and xn == (x - 1)) or \
               (yn == y and xn == (x + 1)):
                prob = 1.0/(4 + self.can_same)
            elif (yn == y and xn == x):
                prob = (1.0 + self.can_same)/(4 + self.can_same)
            else:
                prob = 0.0
        elif y == 4 and x > 0 and x < 5:
            if (yn == (y - 1) and xn == x) or \
               (yn == y and xn == (x - 1)) or \
               (yn == y and xn == (x + 1)):
                prob = 1.0/(4 + self.can_same)
            elif (yn == y and xn == x):
                prob = (1.0 + self.can_same)/(4 + self.can_same)
            else:
                prob = 0.0
        # CORNER POSITIONS
        elif y==0 and x==0:
            if (yn == (y + 1) and xn == x) or \
               (yn == y and xn == (x + 1)):
                prob = 1.0/(4 + self.can_same)
            elif (yn == y and xn == x):
                prob = (2.0 + self.can_same)/(4 + self.can_same)
            else:
                prob = 0.0
        elif y==4 and x==0:
            if (yn == (y - 1) and xn == x) or \
               (yn == y and xn == (x + 1)):
                prob = 1.0/(4 + self.can_same)
            elif (yn == y and xn == x):
                prob = (2.0 + self.can_same)/(4 + self.can_same)
            else:
                prob = 0.0
        elif y==0 and x==5:
            if (yn == (y + 1) and xn == x) or \
               (yn == y and xn == (x - 1)):
                prob = 1.0/(4 + self.can_same)
            elif (yn == y and xn == x):
                prob = (2.0 + self.can_same)/(4 + self.can_same)
            else:
                prob = 0.0
        elif y==4 and x==5:
            if (yn == (y - 1) and xn == x) or \
               (yn == y and xn == (x - 1)):
                prob = 1.0/(4 + self.can_same)
            elif (yn == y and xn == x):
                prob = (2.0 + self.can_same)/(4 + self.can_same)
            else:
                prob = 0.0
        return prob

    def test_transition(self):
        iters = [5, 6, 5, 6]
        ranges = [range(x) for x in iters]
        for y, x, yn, xn in product(*ranges):
            prob = self.transition([y,x],[yn,xn])
            print('p{{({},{})|({},{})}} = {}'.format(yn,xn,y,x,prob))

Gary = Player()
Minotaur = Enemy()
TheGame = Game(Gary, Minotaur)