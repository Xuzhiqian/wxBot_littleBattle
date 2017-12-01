#!/usr/bin/env python
# coding: utf-8

import threading
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
from game import Map,Player
            
                   
def main():
    src_id=msg['content']['user']['id']
    src_name=msg['content']['user']['name']
    src_info=self.get_group_member_name(msg['user']['id'],src_id)
    if msg['content']['type'] == 0:  # text message
        mm=msg['content']['desc']
        if mm == 'join':
            if src_id in self.m.players:
                self.send_msg_by_uid("@"+src_name+'\n'+"已经加入！", msg['user']['id'])
            else:
                p = Player(src_id,src_name,src_info)
                
                
                whole_name=""
                if 'remark_name' in src_info:
                    whole_name = whole_name+src_info['remark_name']+'\n'
                else:
                    whole_name=whole_name+'None\n'
                if 'nickname' in src_info:
                    whole_name = whole_name+src_info['nickname']+'\n'
                else:
                    whole_name=whole__name+'None\n'

                if 'display_name' in src_info:
                    whole_name = whole_name+src_info['display_name']+'\n'
                else:
                    whole_name=whole_name+'None\n'
                                       
                self.m.addplayer(p)
                self.send_msg_by_uid("@"+src_name+'\n'+"加入成功！"+'\n'+whole_name, msg['user']['id'])
        elif mm == 's':
            if src_id in self.m.players:
                self.send_msg_by_uid(self.m.getplayerinfo(src_id), src_id)
            
        elif re.search(r"([udlr])([0-9]+)",mm)!=None:
            if src_id in self.m.players:
                self.send_msg_by_uid(self.m.moveplayer(src_id,mm), src_id)
            
        elif re.search(r"a",mm)!=None:
            pid= self.get_at_user_id(msg)
            if not(pid in self.m.players):
                self.send_msg_by_uid("无效攻击！",msg['user']['id'])
                return None
                
            msgg=self.m.attackplayer(src_id,pid)
            if msgg[0]==0:
                self.send_msg_by_uid(msgg[1],src_id)
            else:
                self.send_msg_by_uid(msgg[1],msg['user']['id'])
                self.send_msg_by_uid(msgg[1],pid)
                
        elif re.search(r"k",mm)!=None:
            pid = self.get_at_user_id(msg)
            msgk=self.m.castskill(src_id,pid)
            if msgk[0]==0:
                self.send_msg_by_uid(msgk[1],src_id)
            else:
                self.send_msg_by_uid(msgk[1],msg['user']['id'])
                
        if self.m.event_death!=[]:
            for event in self.m.event_death:
                self.send_msg_by_uid(u"竞争就是这么残酷，杀手永远无情，唯有活到最后，才是真的王者！\n\n"+event[0]+u'被'+event[1]+event[2],msg['user']['id'])
            self.m.event_death=[]
            if len(self.m.players)<=1:
                for winner in self.m.players.values():
                    self.send_msg_by_uid(u"Winner Winner, Chicken Dinner!\n恭喜"+winner.name+u'!',msg['user']['id'])
                self.robot_switch = False
    


if __name__ == '__main__':
    main()
