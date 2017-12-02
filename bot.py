#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import threading
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
from game import Map,Player
            


class TulingWXBot(WXBot):
    m=Map()
    group_id=''
    
    pattern_join=re.compile(r"^(join) ([a-zA-Z]{1,4})( [1-6])?$")
    pattern_atk=re.compile(r"^(a) ([a-zA-Z]{1,4})$")
    pattern_skl=re.compile(r"^(k)( [a-zA-Z]{1,4})?$")
    pattern_mov=re.compile(r"^([udlr])([0-9]+)$")
    
    def __init__(self):
        WXBot.__init__(self)

        self.robot_switch = True
    
    def get_id(self,pname):
        pid_ghost=''
        pid_real='' 
        if not(pname in self.m.names):
            return None 
        if self.m.names[pname]==[]:
            return None 
        for player_id in self.m.names[pname]:
            player=self.m.players[player_id]
            if player.character==0:
                pid_ghost=player_id
            else:
                pid_real=player_id
                
        if pid_ghost!='':
            return pid_ghost
        else:
            return pid_real
            
    def handle_msg_all(self, msg):
        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:
            if msg['content']['data']==u'game restart'
                self.m=Map()
                self.robot_switch=True
                
        if not self.robot_switch: # and msg['msg_type_id'] != 1
            return
        if msg['msg_type_id'] == 3 and msg['content']['type'] == 0:  # group text message
            if 'detail' in msg['content']:

                src_id=msg['content']['user']['id']
                self.group_id=msg['user']['id']
                if msg['content']['type'] == 0:  # text message
                    mm=msg['content']['desc']
                    result_join=re.match(self.pattern_join,mm)
                    if result_join!=None:
                        src_name=result_join.group(2)
                        if src_id in self.m.players:
                            self.send_msg_by_uid("@"+src_name+'\n'+"已经加入！",self.group_id)
                        else:
                            if src_name in self.m.names:
                                self.send_msg_by_uid("@"+src_name+'\n'+"名字已存在！",self.group_id)
                                return
                            p = Player(src_id,src_name)                 
                            self.m.addplayer(p)
                            self.send_msg_by_uid("@"+src_name+'\n'+"加入成功！",self.group_id)
                    #else:
                        #self.send_msg_by_uid("sorry，错误的名字格式不利于游戏平衡\n正确格式：1至4个英文字母",self.group_id)
       
                            
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 0:
            src_id=msg['user']['id']
            mm=msg['content']['data']
            result_atk=re.match(self.pattern_atk,mm)
            result_skl=re.match(self.pattern_skl,mm)
            result_mov=re.match(self.pattern_mov,mm)
            
            if mm == 's':
                if src_id in self.m.players:
                    self.send_msg_by_uid(self.m.getplayerinfo(src_id), src_id)
                        
            elif result_mov!=None:
                if src_id in self.m.players:
                    self.send_msg_by_uid(self.m.moveplayer(src_id,mm), src_id)
                        
            elif result_atk!=None:
                pid=self.get_id(result_atk.group(2))
                if pid==None or src_id==pid:
                    self.send_msg_by_uid("无效攻击！",src_id)
                    return
                msga=self.m.attackplayer(src_id,pid)
                self.send_msg_by_uid(msga[0],src_id)
                self.send_msg_by_uid(msga[1],pid)
                self.send_msg_by_uid(msga[2],self.group_id)
                            
            elif result_skl!=None:
                pid=self.get_id(result_skl.group(2))
                if pid!=None:
                    pid=pid[1:]
                if src_id in self.m.players==False:
                    return
                msgk=self.m.castskill(src_id,pid)
                self.send_msg_by_uid(msgk[0],src_id)
                if msgk[1]!=():
                    for victim in msgk[1][1]:
                        self.send_msg_by_uid(msgk[1][0],victim)
                self.send_msg_by_uid(msgk[2],self.group_id)
                            
            if self.m.event_death!=[]:
                for event in self.m.event_death:
                    if event[0].character!=0:
                        self.send_msg_by_uid(u"竞争就是这么残酷，杀手永远无情，唯有活到最后，才是真的王者！\n\n"+event[0].name+u'被'+event[1].name+event[2],self.group_id)
                        self.send_msg_by_uid(u"很遗憾！你出局了！凶手："+event[1].name,event[0].id)
                    
                self.m.event_death=[]
                if len(self.m.players)<=1:
                    for winner in self.m.players.values():
                        self.send_msg_by_uid(u"Winner Winner, Chicken Dinner!\n恭喜"+winner.name+u'!'+'\n\n等待造物主xzq授权重新开始游戏...',self.group_id)
                    self.robot_switch = False
            
                    
def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'
    
    
    bot.run()


if __name__ == '__main__':
    main()
