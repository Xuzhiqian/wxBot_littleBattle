#coding=utf-8
import re
import threading
import random

class Player:
    id=0
    name=""
    character = 0
    occu=["None","翌·邪魔","单·嗜血者","迪·遁隐","金·破尘"]
    location = (0, 0)
    alive=True
    
    #       cur  max  re
    health=(0,   0,   0)
    magic=(0,    0,   5)

    #    ATK    range       cd          enable
    atk=(0,     1,          5,          True)
    
    #    cd     magic consumption       enable
    skl=(0,     0,                      True)
    
    #   cd      magic consumption       enbale
    #see=(3,     3,                      True)
    
    
    #   cd      magic consumption       enable
    mov=(3,     2,                      True)

    def __init__(self, _id, _name, _info):
        self.id=_id
        self.name = _name
        self.info = _info
        self.character = random.randint(1, 4)
        if self.character==1:
            self.health=(100,100,0)
            self.magic=(100,100,4)
            self.atk=(10,1,3,True)
            self.skl=(30,50,True)
            
        elif self.character==2:
            self.health=(120,120,0)
            self.magic=(80,80,2)
            self.atk=(15,1,3,True)
            self.skl=(45,60,True)

        elif self.character==3:
            self.health=(60,60,2)
            self.magic=(100,100,2)
            self.atk=(10,1,3,True)
            self.skl=(25,40,True)
            
        elif self.character==4:
            self.health=(50,50,0)
            self.magic=(100,100,2)
            self.atk=(10,3,3,True)
            self.skl=(70,80,True)
     
    def re_magic(self):
        if self.alive==True:
            self.magic=(min(self.magic[1],self.magic[0]+self.magic[2]),self.magic[1],self.magic[2])
            global re_magic_t
            re_magic_t = threading.Timer(5,self.re_magic)
            re_magic_t.start()
            
    def re_health(self):
        if self.alive==True:
            self.health=(min(self.health[1],self.health[0]+self.health[2]),self.health[1],self.health[2])
            global re_health_t
            re_health_t = threading.Timer(5,self.re_health)
            re_health_t.start()       
      
    def re_mov(self):
        self.mov=(self.mov[0],self.mov[1],True)  
    
    def re_atk(self):
        self.atk=(self.atk[0],self.atk[1],self.atk[2],True)
        
    def re_skl(self):
        self.skl=(self.skl[0],self.skl[1],True)
        
    def atk_recover(self):
        self.atk=(self.atk[0]-10,self.atk[1],self.atk[2],self.atk[3])
            
class Map:
    width = 10
    map = {}
    players = {}
    blank = []
    event_death=[]

    def __init__(self):
        self.map = {}
        self.players = {}
        for i in range(self.width):
            for j in range(self.width):
                self.blank.append((i, j))
       
    def addplayer(self, p):
        self.players[p.id] = p
        p.location = random.choice(self.blank)
        self.map[p.location] = p
        self.blank.remove(p.location)
        p.re_magic()
        p.re_health()
        
    
    def death(self, corpse, killer, means):
        self.event_death.append((corpse.name,killer.name,means))
        del self.map[corpse.location]
        self.blank.append(corpse.location)
        del self.players[corpse.id]
     
    def getsight(self,p):
        map_str=""
        for i in range(p.location[1]-p.atk[1],p.location[1]+p.atk[1]+1)[::-1]:
            if (i>=0) and (i<self.width):
                row=""
                for j in range(p.location[0]-p.atk[1],p.location[0]+p.atk[1]+1):
                     if (j>=0) and (j<self.width):
                         if (j,i) in self.map:
                             if self.map[(j,i)].id==p.id:
                                 row=row+'  I  '
                             else:
                                 row=row+' '+self.map[(j,i)].name+' '
                         else:
                             row=row+'  · '
                if row!="":
                    map_str=map_str+row+'\n'
        return map_str

    def getplayerinfo(self, _id):
        if _id in self.players:
            p = self.players[_id]
            if p.alive==False:
                return u"你死了！别操作了！"
            if p.skl[2]==True:
                msg_ski=u"可用"
            else:
                msg_ski=u"不可用"
            return u"职业=" + p.occu[p.character] + u"\n" + u"位置=(" + str(p.location[0]) + u',' + str(p.location[1]) + ')\n' \
                    +u"血量=" + str(p.health[0]) + '\n' + u"蓝量=" + str(p.magic[0]) + '\n' + u"技能"+msg_ski+'\n'+self.getsight(p)
        return ""
    
    def attackplayer(self, _id, p_id):
        if not(_id in self.players):
            return (0,u"玩家不存在！")
        if not(p_id in self.players):
            return (0,u"emmm你攻击了旁观者，可恶！")
        p = self.players[_id]
        pp = self.players[p_id]
        if p.atk[3]==False:
            p.health=(p.health[0]-5,p.health[1],p.health[2])
            if p.health[0]<=0:
                self.death(p,p,u'自杀致死！')
                return (0,"叫你乱A，你把自己搞死了哈哈哈")
            else:
                return (0,u"A太快了！扣5血")
            
        if p.alive==False:
            return (0,u"你死了！别操作了！")
        if pp.alive==False:
            return (0,u"你居然鞭尸！")
        
        if max(abs(pp.location[0]-p.location[0]),abs(pp.location[1]-p.location[1]))>p.atk[1]:
            return (0,u"你又不是金狗，手没这么长！")
        else:
            p.atk=(p.atk[0],p.atk[1],p.atk[2],False)
            threading.Timer(p.atk[2],p.re_atk).start()
            
            if p.character==2:
                p.health=(min(p.health[0]+p.atk[0],p.health[1]),p.health[1],p.health[2])
            if pp.health[0]-p.atk[0]<=0:
                self.death(pp,p,u'A死了！')
                return (0,u"恭喜你！击杀了"+pp.name)
            else:
                pp.health=(pp.health[0]-p.atk[0],pp.health[1],pp.health[2])
                return (1,u"实时：\n"+p.name+u'A了'+pp.name+u'一下，现在'+pp.name+'只剩'+str(pp.health[0])+'血了')        
        
    def moveplayer(self, _id, spec):
        if not(_id in self.players):
            return u"玩家不存在！"
        p = self.players[_id]
        if p.alive==False:
            return u"你死了！别操作了！"
        if p.mov[2]==False:
            return u"冷却时间内不可移动！"
        des=(0,0)
        direct = re.search(r"([udlr])([0-9]+)",spec).group(1)
        distance = re.search(r"([udlr])([0-9]+)",spec).group(2)
        if (direct==None) or (distance==None):
            return u"异常操作！"
        else:
            
            dis=int(distance)
            if (dis<=0):
                return u"距离为0！"
            if p.magic[0]<p.mov[1]*dis*dis:
                return u"蓝量不够！"
            if direct=='u':
                des=(des[0],des[1]+dis)
            elif direct=='l':
                des=(des[0]-dis,des[1])
            elif direct=='d':
                des=(des[0],des[1]-dis)
            elif direct=='r':
                des=(des[0]+dis,des[1])
            des2=(des[0]+p.location[0],des[1]+p.location[1])
            if (des2[0]<0) or (des2[0]>=self.width) or (des2[1]<0) or (des2[1]>=self.width):
                return u"移动操作越界！"
            if des2 in self.map:
                return u"移动到另一名玩家上了！"
            del self.map[p.location]
            self.blank.append(p.location)
            p.location=des2
            self.map[des2]=p
            self.blank.remove(des2)
            p.magic = (p.magic[0]-p.mov[1]*dis*dis,p.magic[1],p.magic[2])
            
            
            p.mov=(p.mov[0],p.mov[1],False)
            threading.Timer(p.mov[0],p.re_mov).start()
            return u"新位置：("+str(p.location[0])+','+str(p.location[1])+')\n'+self.getsight(p)
    def castskill(self, _id, p_id):
        if not( _id in self.players):
            return (0,u"玩家不存在！")
        p=self.players[_id]
        if p.character==1: 
            return self.godstransport(_id,p_id) 
        elif p.character==2:
            return self.suckblood(_id,p_id)
        elif p.character==3:
            return self.lifesteal(_id,p_id)
        elif p.character==4:
            return self.magicsteal(_id,p_id)
        return None 
    def suckblood(self, _id, p_id):
        p=self.players[_id]
        if p.skl[2]==False:
            return (0,u"技能还没准备好！")
        if p.alive==False:
            return (0,u"你死了！别操作了！")
        if p.magic[0]<p.skl[1]:
            return (0,u"蓝量不够！")
        
        p.atk=(p.atk[0]+10,p.atk[1],p.atk[2],p.True)
        threading.Timer(30,p.atk_recover).start()
        p.magic = (p.magic[0]-p.skl[1],p.magic[1],p.magic[2]) 
        p.skl=(p.skl[0],p.skl[1],False)
        threading.Timer(p.skl[0],p.re_skl).start()
        return (1,u"实时：\n"+p.name+"成功使用了技能！")
    
    def magicsteal(self,_id,p_id):
        p = self.players[_id]
        if p.skl[2]==False:
            return (0,u"技能还没准备好！")
        if p.alive==False:
            return (0,u"你死了！别操作了！")
        if p.magic[0]<p.skl[1]:
            return (0,u"蓝量不够！")
        
        stealprop=0.4
        for i in range(p.location[1]-p.atk[1],p.location[1]+p.atk[1]+1)[::-1]:
            if (i>=0) and (i<self.width):
                for j in range(p.location[0]-p.atk[1],p.location[0]+p.atk[1]+1):
                     if (j>=0) and (j<self.width):
                         if (j,i) in self.map:
                             if self.map[(j,i)].id!=p.id:
                                 pp=self.map[(j,i)]
                                 p.magic=(min(p.magic[1],p.magic[0]+int(stealprop*pp.magic[0])),p.magic[1],p.magic[2])
                                 pp.magic=(int((1-stealprop)*pp.magic[0]),pp.magic[1],pp.magic[2])

        p.skl=(p.skl[0],p.skl[1],False)
        threading.Timer(p.skl[0],p.re_skl).start()
        return (1,u"实时：\n"+p.name+"成功使用了技能！")
    def lifesteal(self,_id,p_id):
        p = self.players[_id]
        pp = self.players[p_id]
        if p.skl[2]==False:
            return (0,u"技能还没准备好！")
        if p.alive==False:
            return (0,u"你死了！别操作了！")
        if pp.alive==False:
            return (0,u"你居然鞭尸！")
        if p.magic[0]<p.skl[1]:
            return (0,u"蓝量不够！")
        
        stealprop=0.3
        p.health=(p.health[0]+int(stealprop*pp.health[0]),p.health[1],p.health[2])
        pp.health=(int((1-stealprop)*pp.health[0]),pp.health[1],pp.health[2])
        p.skl=(p.skl[0],p.skl[1],False)
        threading.Timer(p.skl[0],p.re_skl).start()
        return (1,u"实时：\n"+p.name+"成功使用了技能！")
        
    def godstransport(self, _id, p_id):
        p = self.players[_id]
        pp = self.players[p_id]
        if p.skl[2]==False:
            return (0,u"技能还没准备好！")
        if p.alive==False:
            return (0,u"你死了！别操作了！")
        if pp.alive==False:
            return (0,u"你居然鞭尸！")
        if p.magic[0]<p.skl[1]:
            return (0,u"蓝量不够！")
        
        self.map[p.location]=pp
        self.map[pp.location]=p
        target_pos=pp.location
        pp.location=p.location
        p.location=target_pos
        p.magic = (p.magic[0]-p.skl[1],p.magic[1],p.magic[2]) 
        p.skl=(p.skl[0],p.skl[1],False)
        threading.Timer(p.skl[0],p.re_skl).start()
        return (1,u"实时：\n"+p.name+"成功使用了技能！")