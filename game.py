#coding=utf-8
import re
import threading
import random

class Trap:
    center=(0,0)
    r=0
    damage=0
    def __init__(self,_center,_r,_damage,_owner):
        self.center=_center
        self.r=_r
        self.damage=_damage
        self.owner=_owner
    
class Player:
    id=0
    name=""
    character = 0
    occu=["苦工食尸鬼","翌·邪魔","单·我不胖","迪·遁隐","金·破尘","叶·黑爪",'超·纵魂','赵·太二']
    location = (0, 0)
    alive=True
    
    #       cur  max  re
    health=(0,   0,   0)
    magic=(0,    0,   5)

    #    ATK    range       cd          enable
    atk=(0,     2,          5,          True)
    
    #    cd     magic consumption       enable
    skl=(0,     0,                      True)
    
    #   cd      magic consumption       enable
    mov=(3,     2,                      True)
    
    #          cur      max     获得一个标记所需的（伤害等）量
    mark_thin=(0,       7,      10)
    mark_cool=(0,       5)
    
    #      暴击几率      暴击效果
    crit=(0.2,          3)
    locked=False
    
    def __init__(self, _id, _name):
        self.id=_id
        self.name = _name
        self.character = random.randint(7, 7)
        if self.character==1:
            self.health=(80,80,0)
            self.magic=(100,100,4)
            self.atk=(10,2,5,True)
            self.skl=(40,40,True)
            
        elif self.character==2:
            self.health=(100,100,0)
            self.magic=(100,100,2)
            self.atk=(5,2,5,True)
            self.skl=(40,50,True)

        elif self.character==3:
            self.health=(70,70,2)
            self.magic=(100,100,2)
            self.atk=(10,2,5,True)
            self.skl=(30,40,True)
            
        elif self.character==4:
            self.health=(70,70,0)
            self.magic=(100,100,2)
            self.atk=(5,4,5,True)
            self.skl=(30,40,True)
        
        elif self.character==5:
            self.health=(60,60,0)
            self.magic=(100,100,2)
            self.atk=(20,2,10,True)
            self.skl=(50,40,True)
            
        elif self.character==6:
            self.health=(60,60,0)
            self.magic=(100,100,2)
            self.atk=(10,2,5,True)
            self.skl=(60,50,True)
            
        elif self.character==7:
            self.health=(60,60,0)
            self.magic=(100,100,2)
            self.atk=(10,2,3,True)
            self.skl=(60,50,True)
    
    def unlock(self):
        self.locked=False
           
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
    
    def set_mark_thin(self,m):
        mm=min(m,self.mark_thin[1])
        
        self.mark_thin=(mm,self.mark_thin[1],self.mark_thin[2])
        self.atk=(5+mm,self.atk[1],self.atk[2],self.atk[3])
        #print("---------------------------标记："+str(self.mark_thin))
        
    def set_mark_cool(self,m):
        mm=min(m,self.mark_cool[1])
        self.mark_cool=(mm,self.mark_cool[1])
        self.crit=(0.2+0.02*mm,self.crit[1])
        
    def re_mov(self):
        self.mov=(self.mov[0],self.mov[1],True)  
    
    def re_atk(self):
        self.atk=(self.atk[0],self.atk[1],self.atk[2],True)
        
    def re_skl(self):
        self.skl=(self.skl[0],self.skl[1],True)
        
    def takeoff_taticalvisor(self):
        self.atk=(self.atk[0],2,self.atk[2],self.atk[3])
                    
class Map:
    width = 12
    map = {}
    players = {}
    names={}
    blank = []
    event_death=[]
    traps=[]

    def __init__(self):
        self.map = {}
        self.players = {}
        for i in range(self.width):
            for j in range(self.width):
                self.blank.append((i, j))
    def dis(self,a,b):
        return max( abs(a[0]-b[0]),abs(a[1]-b[1])   ) 
    def addplayer(self, p):
        if p.name in self.names.keys():
            self.names[p.name].append(p.id)
        else:
            self.names[p.name]=[p.id]
        self.players[p.id] = p
        p.location = random.choice(self.blank)
        self.map[p.location] = p
        self.blank.remove(p.location)
        p.re_magic()
        if p.health[2]>0:
            p.re_health()
        
        if p.character==6:
            self.selfseparate(p.id)
    
    def cause_dmg(self,er,p,dmg):
        p.health=(p.health[0]-dmg,p.health[1],p.health[2])
        if p.character==2:
            p.set_mark_thin(p.mark_thin[0]+round(dmg/p.mark_thin[2]))
        if er.character==7:
            er.set_mark_cool(er.mark_cool[0]+1)
    def get_neighbor_blank(self, p):
        neighbor=[]
        for i in range(p.location[0]-p.atk[1],p.location[0]+p.atk[1]+1):
            if (i>=0) and (i<self.width):
                for j in range(p.location[1]-p.atk[1],p.location[1]+p.atk[1]+1):
                     if (j>=0) and (j<self.width):
                         if not((i,j) in self.map.keys()):
                             neighbor.append((i,j))
        return neighbor
    
    def trapfade(self,t):
        if t in self.traps:
            self.traps.remove(t)
    def suicide(self,p):
        if p.alive==True:
            del self.map[p.location]
            self.blank.append(p.location)
            del self.players[p.id]
            if len(self.names[p.name])>1:
                self.names[p.name].remove(p.id)
            else:
                del self.names[p.name]
             
    def death(self, corpse, killer, means, ifshow):
        corpse.alive=False
        if ifshow==True:
            self.event_death.append((corpse,killer,means))
        del self.map[corpse.location]
        self.blank.append(corpse.location)
        del self.players[corpse.id]
        if len(self.names[corpse.name])>1:
            self.names[corpse.name].remove(corpse.id)
        else:
            del self.names[corpse.name]
     
    def getsight(self,p):
        map_str=""
        for i in range(p.location[1]-p.atk[1],p.location[1]+p.atk[1]+1)[::-1]:
            if (i>=0) and (i<self.width):
                row=""
                for j in range(p.location[0]-p.atk[1],p.location[0]+p.atk[1]+1):
                     if (j>=0) and (j<self.width):
                         if (j,i) in self.map.keys():
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
            if p.skl[2]==True and p.skl[1]<=p.magic[0]:
                msg_ski=u"可用"
            else:
                msg_ski=u"不可用"
                
            msg_special=''
            if p.character==2:
                msg_special=u'\n标记数量：'+str(p.mark_thin[0])+u'\n攻击力：'+str(p.atk[0])
            if p.character==7:
                msg_special=u'\n标记数量：'+str(p.mark_cool[0])+u'\n暴击率：'+str(p.crit[0])
            return u"职业=" + p.occu[p.character] + u"\n" + u"位置=(" + str(p.location[0]) + u',' + str(p.location[1]) + ')\n' \
                    +u"血量=" + str(p.health[0]) + '\n' + u"蓝量=" + str(p.magic[0]) + '\n' + u"技能"+msg_ski+'\n'+self.getsight(p)+msg_special
        return ""
    
    def attackplayer(self, _id, p_id):
        if not(_id in self.players):
            return (u"玩家不存在！",'','')
        if not(p_id in self.players):
            return (u"emmm你攻击了旁观者，可恶！",'','')
        p = self.players[_id]
        pp = self.players[p_id]
        if p.atk[3]==False:
            p.magic=(p.magic[0]-5,p.magic[1],p.magic[2])
            if p.health[0]<=0:
                self.death(p,p,u'自杀致死！',True)
                return ("叫你乱A，把自己搞死了哈哈哈",'','')
            else:
                return (u"A太快了！掉5蓝",'','')
            
        if p.alive==False:
            return (u"你死了！别操作了！",'','')
        if pp.alive==False:
            return (u"你居然鞭尸！",'','')
        
        if max(abs(pp.location[0]-p.location[0]),abs(pp.location[1]-p.location[1]))>p.atk[1]:
            return (u"你又不是金狗，手没这么长！",'','')
        else:
            p.atk=(p.atk[0],p.atk[1],p.atk[2],False)
            threading.Timer(p.atk[2],p.re_atk).start()
            
            dmg=p.atk[0]
            lucky=False
            if p.character==7:
                if random.random()<p.crit[0]:
                    lucky=True
                    dmg=dmg*p.crit[1]           #Crit!!
                    
            atk_msg='A'
            if lucky==True:
                atk_msg=u'暴击A'
                
            actual_name=pp.name    
            if pp.character==0:
                actual_name='苦工食尸鬼'   
            if pp.health[0]-dmg<=0:
                self.death(pp,p,atk_msg+u'死了！',False)
                if p.character==5:
                    p.health=(p.health[1],p.health[1],p.health[2])
                return (u"恭喜你！击杀了"+actual_name,   u"很遗憾！你出局了！凶手："+p.name,   u'死亡通告：'+actual_name+u'被'+p.name+atk_msg+u'死了')
            else:
                self.cause_dmg(p,pp,dmg)
                return (u'你成功'+atk_msg+u'了'+actual_name+u'一下，还剩'+str(pp.health[0])+'血',u'警告：你被'+p.name+atk_msg+u'一下，还剩'+str(pp.health[0])+'血',u'实时：'+p.name+atk_msg+u'了'+actual_name+u'一下，还剩'+str(pp.health[0])+'血')
    #如果踩到陷阱则立即处理    
    def check_if_trapped_and_dead(self,p):
        istrapped=False
        trapped=[]
        murderer=None
        for trap in self.traps:
            if self.dis(p.location,trap.center)<=trap.r:
                istrapped=True
                self.cause_dmg(None,p,trap.damage)
                trapped.append(trap)
                if p.health[0]<=0:
                    murderer=trap.owner
                    break
                    
        for trap in trapped:
            self.traps.remove(trap)
        if istrapped==True:
            p.locked=True
            threading.Timer(15,p.unlock).start()
            if p.health[0]<=0:
                self.death(p,murderer,u'用虚空陷阱秀了一波，死于虫洞的吞噬之下！',True)
                return (True,True)
            else:
                return (True,False)
        else:
            return (False,False)
        
    def moveplayer(self, _id, spec):
        if not(_id in self.players):
            return u"玩家不存在！"
        p = self.players[_id]
        if p.alive==False:
            return u"你死了！别操作了！"
        if p.mov[2]==False:
            return u"冷却时间内不可移动！"
        if p.locked==True:
            return u"你正在被禁锢中！爽飞了！"
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
                
            status=self.check_if_trapped_and_dead(p)
            
            if status==(True,True):
                return u"天算不如人算！你被虚空陷阱吞噬而死！"
            else:
                del self.map[p.location]
                self.blank.append(p.location)
                p.location=des2
                self.map[des2]=p
                self.blank.remove(des2)
                p.magic = (p.magic[0]-p.mov[1]*dis*dis,p.magic[1],p.magic[2])
                p.mov=(p.mov[0],p.mov[1],False)
                threading.Timer(p.mov[0],p.re_mov).start()
                
                trapmsg=''
                if status[0]==True:
                    trapmsg='\n你踩到了虚空陷阱，被禁锢住了！小心行事！'
                return u"新位置：("+str(p.location[0])+','+str(p.location[1])+')\n'+self.getsight(p)+trapmsg
                
    def castskill(self, _id, p_id):
        if not( _id in self.players):
            return (u"玩家不存在！",(),'')
        p=self.players[_id]
        if p.character==1: 
            return self.vacanttrap(_id) 
        elif p.character==2:
            return self.eatalot(_id)
        elif p.character==3:
            return self.lifesteal(_id,p_id)
        elif p.character==4:
            return self.magicsteal(_id)
        elif p.character==5:
            return self.terminate(_id)
        elif p.character==6:
            return self.earthquake(_id)
        elif p.character==7:
            return self.overwatch(_id)
        return None
    
    def terminate(self,_id):
        p = self.players[_id]
        if p.skl[2]==False:
            return (u"技能还没准备好！",(),'')
        if p.magic[0]<p.skl[1]:
            return (u"蓝量不够！",(),'')
        
        termprop=0.3
        pid_set=[]
        for i in range(p.location[1]-p.atk[1],p.location[1]+p.atk[1]+1)[::-1]:
            if (i>=0) and (i<self.width):
                for j in range(p.location[0]-p.atk[1],p.location[0]+p.atk[1]+1):
                     if (j>=0) and (j<self.width):
                         if (j,i) in self.map.keys():
                             if self.map[(j,i)].id!=p.id:
                                 pp=self.map[(j,i)]
                                 self.cause_dmg(p,pp,0.3*(pp.health[1]-pp.health[0]))
                                 pid_set.append(pp.id)
                                 if (pp.health[0]<=0):
                                     self.death(pp,p,u'使用技能“终结”杀死了！\n'+p.name+u'恢复至满血！',True)
                                     p.health=(p.health[1],p.health[1],p.health[2])

        p.skl=(p.skl[0],p.skl[1],False)
        p.magic = (p.magic[0]-p.skl[1],p.magic[1],p.magic[2])
        threading.Timer(p.skl[0],p.re_skl).start()
        return (u'你成功使用了技能“终结”！',(u'严重警告：你被'+p.name+u'使用了技能！',pid_set),u"实时：\n"+p.name+"成功使用了技能！")
    def overwatch(self, _id):
        p = self.players[_id]
        if p.skl[2]==False:
            return (u"技能还没准备好！",(),'')
        if p.magic[0]<p.skl[1]:
            return (u"蓝量不够！",(),'')
        if p.mark_cool[0]!=5:
            return (u"标记不足！",(),'')
        
        p.atk=(p.atk[0],self.width,p.atk[2],p.atk[3])       #overwatch!!
        threading.Timer(12,p.takeoff_taticalvisor).start()
        
        p.skl=(p.skl[0],p.skl[1],False)
        p.magic = (p.magic[0]-p.skl[1],p.magic[1],p.magic[2])
        threading.Timer(p.skl[0],p.re_skl).start()
        return (u'战术目镜启动！',(),u"实时：\n"+p.name+"成功使用了技能！")
        
    def eatalot(self, _id):
        p = self.players[_id]
        if p.skl[2]==False:
            return (u"技能还没准备好！",(),'')
        if p.magic[0]<p.skl[1]:
            return (u"蓝量不够！",(),'')
        if p.mark_thin[0]<=0:
            return (u"没有标记！",(),'')
        
        heal=p.mark_thin[0]*8
        p.set_mark_thin(0)
        p.health=(min(p.health[0]+heal,p.health[1]),p.health[1],p.health[2])
        p.skl=(p.skl[0],p.skl[1],False)
        p.magic = (p.magic[0]-p.skl[1],p.magic[1],p.magic[2])
        threading.Timer(p.skl[0],p.re_skl).start()
        return (u'胡吃海喝！瞬间恢复了'+str(heal)+u'点生命！',(),u"实时：\n"+p.name+"成功使用了技能！")
    def earthquake(self, _id):
        p = self.players[_id]
        if p.skl[2]==False:
            return (u"技能还没准备好！",(),'')
        if p.magic[0]<p.skl[1]:
            return (u"蓝量不够！",(),'')
        
        dmg=20
        pid_set=[]
        for i in range(p.location[1]-p.atk[1],p.location[1]+p.atk[1]+1)[::-1]:
            if (i>=0) and (i<self.width):
                for j in range(p.location[0]-p.atk[1],p.location[0]+p.atk[1]+1):
                     if (j>=0) and (j<self.width):
                         if (j,i) in self.map.keys():
                             if self.map[(j,i)].id!=p.id:
                                 pp=self.map[(j,i)]
                                 self.cause_dmg(p,pp,dmg)
                                 pid_set.append(pp.id)
                                 if (pp.health[0]<=0):
                                     self.death(pp,p,u'用霜之哀伤捅死了，心疼~',True)
                                 else:
                                     pp.locked=True
                                     threading.Timer(10,pp.unlock).start()
        
        p.skl=(p.skl[0],p.skl[1],False)
        p.magic = (p.magic[0]-p.skl[1],p.magic[1],p.magic[2])
        threading.Timer(p.skl[0],p.re_skl).start()
        return (u'你成功发动了技能“地震”！',(u'警告：你受到了技能：“地震”的影响！',pid_set),u"实时：\n"+p.name+"成功使用了技能！")
        
    def magicsteal(self,_id):
        p = self.players[_id]
        if p.skl[2]==False:
            return (u"技能还没准备好！",(),'')
        if p.magic[0]<p.skl[1]:
            return (u"蓝量不够！",(),'')
        
        p.magic = (p.magic[0]-p.skl[1],p.magic[1],p.magic[2])
        stealprop=0.4
        pid_set=[]
        for i in range(p.location[1]-p.atk[1],p.location[1]+p.atk[1]+1)[::-1]:
            if (i>=0) and (i<self.width):
                for j in range(p.location[0]-p.atk[1],p.location[0]+p.atk[1]+1):
                     if (j>=0) and (j<self.width):
                         if (j,i) in self.map.keys():
                             if self.map[(j,i)].id!=p.id:
                                 pp=self.map[(j,i)]
                                 pid_set.append(pp.id)
                                 p.magic=(min(p.magic[1],p.magic[0]+int(stealprop*pp.magic[0])),p.magic[1],p.magic[2])
                                 pp.magic=(int((1-stealprop)*pp.magic[0]),pp.magic[1],pp.magic[2])

        p.skl=(p.skl[0],p.skl[1],False)
        threading.Timer(p.skl[0],p.re_skl).start()
        return (u'你成功发动了技能“吸精！”',(u"糟糕！你被偷取了蓝量！",pid_set),u"实时：\n"+p.name+"成功使用了技能！")
    def lifesteal(self,_id,p_id):
        if p_id==None:
            return (u"技能释放对象不存在！",(),'')
        p = self.players[_id]
        pp = self.players[p_id]
        if p.skl[2]==False:
            return (u"技能还没准备好！",(),'')
        if p.magic[0]<p.skl[1]:
            return (u"蓝量不够！",(),'')
        if _id==p_id:
            return (u'不能对自己施放技能！',(),'')
        p.magic = (p.magic[0]-p.skl[1],p.magic[1],p.magic[2])
        stealprop=0.3
        p.health=(p.health[0]+int(stealprop*pp.health[0]),p.health[1],p.health[2])
        pp.health=(round((1-stealprop)*pp.health[0]),pp.health[1],pp.health[2])
        p.skl=(p.skl[0],p.skl[1],False)
        threading.Timer(p.skl[0],p.re_skl).start()
        return (u'你成功偷取了'+pp.name+u'的生命！',(p.name+u"很狡猾！偷取了你的生命！",[pp.id]),u"实时：\n"+p.name+"成功使用了技能！")
        
    def vacanttrap(self, _id):
        p = self.players[_id]
        if p.skl[2]==False:
            return (u"技能还没准备好！",(),'')
        if p.magic[0]<p.skl[1]:
            return (u"蓝量不够！",(),'')
        
        trap=Trap(p.location,1,30,p)
        self.traps.append(trap)
        
        threading.Timer(120,self.trapfade,(trap,))
        p.magic = (p.magic[0]-p.skl[1],p.magic[1],p.magic[2]) 
        p.skl=(p.skl[0],p.skl[1],False)
        threading.Timer(p.skl[0],p.re_skl).start()
        return ('你成功布下了一个虚空陷阱，愉快地蹲人吧！',(),u"实时：\n"+p.name+"成功使用了技能！")
        
    def selfseparate(self, _id):
        if not(_id in self.players):
            return None
        p = self.players[_id]
        
        new_id=_id+'ghost'
        pghost=Player(new_id,p.name)
        pghost.character=0
        pghost.health=(50,50,0)
        pghost.magic=(0,0,0)
        pghost.atk=(0,1,5,False)
        pghost.skl=(10,0,False)
        
        if p.name in self.names.keys():
            self.names[p.name].append(new_id)
        else:
            self.names[p.name]=[new_id]
        self.players[new_id] = pghost
        pghost.location = random.choice(self.get_neighbor_blank(p))
        self.map[pghost.location] = pghost
        self.blank.remove(pghost.location)
        threading.Timer(30,self.suicide,(pghost,)).start()
        
        global selfseparate_t
        selfseparate_t = threading.Timer(60,self.selfseparate,(_id,))
        selfseparate_t.start()
        
        