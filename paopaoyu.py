#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  FileName    : test.py  
#  Created     : Sun Nov 15 21:02:04 2009  
#  Description : paopaoyu amf test 
#  Time-stamp: <2009-12-08 21:44:57 > 

import socket
socket.setdefaulttimeout(8)
import httplib
# httplib.HTTPConnection.debuglevel = 1
from pyamf.remoting.client import RemotingService
import time
import tempfile
#import Image
from PIL import GifImagePlugin
from PIL import JpegImagePlugin
import urllib2
import random
#import ImageFilter
import re
from hashlib import md5
import os
import base64
import sys
from ctypes import *
from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, ETA
from utils import print_tank, print_fish, fish_str, print_tank_detail, \
     worth_shock, print_userinfo, pr, get_cookie, worth_feed, \
     worth_delete, family_dict, safe_decode, now, worth_decompose, \
     second_str, __VERSION__, ask_captcha, ask_basic_info, cal_captcha, ask_register
#sleepbar

user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.256.0 Safari/532.5"
refer = "http://xnimg.cn/xcube/app/25049/media/swf/v15/game.swf"


CODEC = 'utf-8'
if os.name== 'nt':
    reload(sys)
    sys.setdefaultencoding('gb18030')   # codec fixed
    CODEC = 'gb18030'
    
print u"杯具渔民 %s 版 By 莔MM et Feather" % __VERSION__
print u"\n春哥保佑你们. \n游戏而已, 说到底就一堆随机数据. 该散就散吧."
            
formula_id = 8                          # 红珍珠虎
main_level = None
minor_level = 5 # default 5
username = ''
password = ''

config_item = ["auto-captcha", "long-time", "auto-filter",
               "catch-fish", "visit-tank", "delete-fish", "decompose-fish", 'compose-fish']
config = dict(zip( config_item, [True, False, False, True, True, False, False, True]))

# 登录部分TODO: add more
if len(sys.argv)== 4:
    username = sys.argv[1]
    password = sys.argv[2]
    main_level = int(sys.argv[3])

if username== '':
    username, password, main_level, minor_level, config = ask_basic_info()     # UI
    config = dict(zip(config_item, config))

if not username or not password:
    sys.exit(1)

for _ in xrange(6):
    try:
        cookie, uid = get_cookie(username, password)
        break
    except:
        print u"登录失败, 重试."
        continue
else:
    print u"你比渔民杯具, 谢谢."
    sys.exit(-1)

print u"获得 Uid:", uid

# AMF 连接设置
client = RemotingService("http://xiaonei.paopaoyu.cn/gateway/")
client.addHTTPHeader('Referer',  refer)
client.addHTTPHeader('Connection', "close")
client.addHTTPHeader('Cookie', cookie)
client.user_agent = user_agent 
#"Mozilla/5.0 (X11; Linux mips; U; zh-cn) Gecko/20091010 BeiJu/0.0.1"

membersService = client.getService("membersService")
productsService = client.getService("productsService") # // 鱼市
gameService = client.getService("gameService")  # // 抓鱼
faqsService = client.getService("faqsService") # // FAQ, 暂时没用
spacesService = client.getService("spacesService") # //
almanacService = client.getService("almanacService") # // 图鉴
inviteService = client.getService("inviteService") # // 邀请
pubseaService = client.getService("pubseaService") # //
syntheticService = client.getService("syntheticService") # //Fuck it

# 杯具, 连接封装, 搞定泡泡鱼卡的问题

def req_safe(servicename, methodname, *args):
    tries = 0
    res = "NO DATA!"
    while True:
        try:
            res =  servicename.__getattr__(methodname)(*args)
            assert (isinstance(res, dict) or isinstance(res, list))
            return res
        except AssertionError:
            tries+= 1
            print u"服务器返回异常. 重试. 若重复出现, 请联系GM."
            print res
            if tries>= 5:
                return None
            req_fail(spacesService, "getNewMsgAMF", uid, uid)
            time.sleep(0.1)
            continue
        except:
            print u'%s 请求失败, 重试!' % methodname
            client.connection.close()
            req_fail(membersService, "getUserInfoAMF", uid, uid)
            req_fail(gameService, "getCatchFishUserInfoAMF", uid)
            req_fail(spacesService, "getNewMsgAMF", uid, uid)
            time.sleep(0.1)
            continue

def req_fail(servicename, methodname, *args):
    while True:
        try:
            return servicename.__getattr__(methodname)(*args)
        except:
            # print u'%s 请求失败, 放弃!' % methodname # make quiet
            client.connection.close()
            time.sleep(0.3)
            break                           # do nothing
    

last_visit = 0
time_line = dict()
def do_time_line():
    global time_line, res, petst        # dummy
    events = filter(lambda k: k< now(), time_line.keys())
    for keys in events:
        if key not in time_line:
            continue  # fix
        dowhat, parms = time_line[keys]
        print dowhat, parms, 
        if dowhat== 'STEAL':
            print u"[偷鱼]:",
            while True:
                petst = req_safe(gameService, "getPetStatusAMF", uid, *parms)
                if petst['status']== u'b' and (not petst['is_stolen']):
                    res = req_safe(gameService, "stealAMF", uid, *parms)
                    if res.get('fish', 0):
                        print_fish(res['fish'])
                        break
                    else:
                        print u"失败"
                        break
                elif petst['status']== u'c' and ((petst['rest_time'] or 1)<= 120):
                    print '.',
                    sys.stdout.flush()
                    time.sleep(0.8)
                    continue
                else:
                    print u"失败"
                    break
        elif dowhat== 'SHOCK':
            tank = req_safe(productsService, "getMyFishTankObjectListAMF", uid, *parms) # f['id']. tk['id']
            is_worth_shock, is_need_feed =  worth_shock(tank)
            if is_worth_shock:
                print u"[电鱼]:",  #{'error': u'no remain time error'}
                if is_need_feed:
                    print u"(喂食2)",
                    req_fail(productsService, "feedAMF", uid, *(list(parms)+[2]))
                    time.sleep(0.1)
                while True:
                    res = req_safe(productsService, "shockAMF", uid, *parms)
                    if res.get('get_shells', 0):
                        print u"获得", res['get_shells'], u"贝壳",
                        time_line[now()+240*60-random.randint(0, 3)-20] = ('SHOCK', parms) # need fix
                        print "[EVENT Registered]"
                        break
                    else:
                        if res.get('remain_time', 1000)<= 2:
                            print ".",
                            sys.stdout.flush()
                            if parms[0]== 16: # 本句代码送给可爱的管理员
                                time.sleep(0.1)
                            else:
                                time.sleep(5)
                            continue
                        print u"失败", res
                        time_line[now()+ res.get('remain_time', 240)*60 - 60] = ('SHOCK', parms)
                        break
        elif dowhat== 'HARVEST':
            pet_dispath()
        elif dowhat== 'SYNTH':
            print u"[合成]:",
            # here can't assert always right, but bug
            res = req_safe(syntheticService, "getSynthesizeInfoAMF", uid) # dummy?
            res = syntheticService.compeleteSynthesizeAMF(uid, *parms)
            if res.get('error', False):
                print u"某错误发生. 重设所有合成鱼事件."
                for k in [i for i in time_line if time_line[i][0]== 'SYNTH']:
                    del time_line[k]
                res = req_safe(syntheticService, "getSynthesizeInfoAMF", uid)
                process_synthetic_info(res)
                continue                # noneed to go on and del
            elif res['result']:           # success
                print u"获得%s %d经验" % (res['fish_name'], res['get_exp'])
            else:
                print u"合成失败, 渔民杯具了"
            res = req_safe(syntheticService, "addSynthesizeAMF", uid,  formula_id) 
            tl = [e for e in time_line if time_line[e][0]== 'SYNTH'] # bad, but Works
            t = max(tl) if tl else now()
            res = req_safe(syntheticService, "getSynthesizeInfoAMF", uid) # 上条多次重试时会导致出错,故加入
            if res.get('synth_list', []):
                time_line[t+5+res['synth_list'][-1]['need_time']] = ('SYNTH', (res['synth_list'][-1]['synth_id'],))
                print u"[EVENT Registered]"
            else:
                print u"自动合成出错, 可能是材料不足"
        else:
            print u"错误"
        del time_line[keys]

# sleep function
def sleepbar(tm=50, txt=''):
    # Bar(widgets=[marker=RotatingMarker()...]
    pbar = ProgressBar(widgets=[txt, Percentage(), Bar(marker=RotatingMarker(), \
           left='[', right=']'), ' ', ETA()], maxval=600).start()
    for i in range(600):
        if i%6== 0:
            do_time_line()
        time.sleep(tm/600.0)
        pbar.update(i+1)
    pbar.finish()

def wait(sec=70, txt=''):
    t = random.randint(-1, 7) + sec
    if t< 45:
        t = 46
    sleepbar(t, txt)


newmsg = req_safe(spacesService, "getNewMsgAMF", uid, uid)
userinfo = req_safe(membersService, "getUserInfoAMF", uid, uid)
req_fail(pubseaService, "getPubSeaInfoAMF", uid)
fishinfo = req_safe(gameService, "getCatchFishUserInfoAMF", uid)

if newmsg:
    print u"有 %d 条新信息." % newmsg.get('new_msg_num', 0)
if userinfo:
    # print userinfo
    print_userinfo(userinfo)
if (not main_level) or (main_level not in [2,3]):
    print u"自动根据等级设置抓鱼区域."
    main_level = fishinfo.get('tempo', 2)

# 好友 #############################
print u"= 好友信息 ="
friends = req_safe(spacesService, "getFriendListAMF", uid) # or refreshFriendListAMF
for f in friends.get('friend_list', []):
    print u"%s 等级%d Id#%d" % (safe_decode(f['nickname']), f['almanac_level'], f['id'])
print u"共 %d 好友" % len( friends.get('friend_list', []))

#membersService.getUserInfoByXiaoneiIdAMF(uid,  xxxxxxxxx)
#spacesService.getDynamicMessageListAMF(uid, 1)


# 收鱼部分 ########################################
print u"= 潜艇鱼 ="
def pet_dispath():
    global petst
    petst = req_safe(gameService, "getPetStatusAMF", uid, uid)
    if petst:
        if petst['status']== u'c':
            print u"抓鱼剩余时间 %d 秒." % (petst['rest_time'] or 0)
            time_line[now()+(petst['rest_time'] or 1000)] = ('HARVEST', ())
        elif petst['status']== u'w':
            print u"派遣抓鱼."
            # petst = gameService.dispatchAMF(uid, 2) # 雌雄双煞
            # petst = gameService.dispatchAMF(uid, 3) # 杜姆之巢
            petst = req_safe(gameService, "dispatchAMF", uid, main_level)
        elif petst['status']== u'b':
            print u"收获鱼列表:"
            map(print_fish, petst['fish_list'])
            if petst['fish_list']!= [] or (not petst['rest_time']):  # status=u'b'
                petst = req_safe(gameService, "harvestAMF", uid)
                print u"派遣抓鱼."
                time_line[now()+10*60*60] = ('HARVEST', ())
            petst = req_safe(gameService, "dispatchAMF", uid, main_level)
pet_dispath()

# 合成鱼部分 ########################################
def print_formulary(f):
    print u'Id#%d' % f['id'],
    print u' + '.join([u'%sx%s(%d星)' % (e['essence_num'],
                                         e['name'], e['star']) for e in f['essence']]),
    print u'+ %dBK =  %s' % (f['shells'], f['name']),
    print u'+ %d经验' % f['get_exp'],
    print u'(基础成功率%d%% 耗时%s)' % (f['base_rate'], second_str(f['total_time']))
    print u'[可合成]' if (f['is_essence_enough'] and f.get('is_level_enough', True)) else u'[不可合成]'
def print_synth_item(f):
    print_formulary(f['formulary'])
    print u"剩余时间%d/%d秒 已被帮助%d次 成功率%d%% Id#%d" % \
          ((f['rest_time'] or 0), f['need_time'], f['helper_num'], f['success_rate'], f['synth_id'])
def process_synthetic_info(i):
    if 'error' in i:
        return
    print u"合成等级%d 经验%d/%d 队列最大长度%d" % (i['synth_level'], i['remain_exp'], i['next_exp'],
                                                    i['max_queue'])
    t = 0                               # some_time ^_^
    tmax = 0                            # calculate all time here
    for f in i.get('synth_list', []):
        if f['synth_status']== 1:
            tmax += f['rest_time']
        elif f['synth_status']== 0:
            tmax += f['need_time']
        else:
            pass
    for num, f in enumerate(i.get('synth_list', [])):
#        print f
        print_synth_item(f)
        if f['synth_status']== 2: # 2=完成 1=正在抓 0=队列
            res = syntheticService.compeleteSynthesizeAMF(uid, f['synth_id'])
            if res['result']:           # success
                print u"获得%s %d经验" % (res['fish_name'], res['get_exp'])
            else:
                print u"合成失败, 渔民杯具了"
            print u"设置合成 公式#3:",
            res = req_safe(syntheticService, "addSynthesizeAMF", uid,  formula_id)
            if res.get('synth_list', []):
                fid = res['synth_list'][-1]['synth_id'] # must be new
                time_line[now()+tmax+res['synth_list'][-1]['need_time']+10] = ('SYNTH', (fid,)) # maybe fixed
                print u"成功 [EVENT Registered]"
            else:
                print u"失败", res
        elif f['synth_status']== 1:
            t+= f['rest_time']+ 10
            time_line[now()+t] = ('SYNTH', (f['synth_id'],)) # later is not problem
            print "[EVENT Registered]"
        elif f['synth_status']== 0:
            t+= f['need_time']+ 10
            time_line[now()+t] = ('SYNTH', (f['synth_id'],)) # later is not problem
            print "[EVENT Registered]"
        else:
            # noting
            pass

if config['compose-fish']:
    print u"= 合成鱼 ="
    types = [2, 3, 5, 7, 11, 13] # current no X-> , 1]
    for t in types:
        print u"== 合成公式:%s ==" % family_dict.get(t, str(t))
        res = req_safe(syntheticService, "getFormularyListAMF", uid, t)
        map(print_formulary, res['objList'])
    res = req_safe(syntheticService, "getSynthesizeInfoAMF", uid)
    process_synthetic_info(res)


# 塑料袋部分 ########################################
def print_decompose_result(r):
    #{'color': u'r', 'style': u'e_e10_h1', 'star': 2, 'id': 11, 'name': u'\u7ea2\u4e09\u4f53\u7cbe\u534e'}
    print u"%s(%s星)" % (r.get('name', "????"), r.get('star', '?')),

print u"= 塑料袋 ="
types = [2, 3, 5, 7, 11, 13, 1]
all_fishes = []
for t in types:
    print u"== %s ==" % family_dict.get(t, str(t))
    fishes = []                         #                 family, type, is_change_family, page
    res = req_safe(productsService, "getMyBagObjectListAMF", uid, t, u'f', True) # 11.30 modified
    # print res
    if res: # some maybe None
        print u"共%d条" % res['total_num']
        fishes.extend( res['objList'] )
        all_fishes.extend( fishes )
        for f in fishes:
            print fish_str(f['style']),
            if (config["delete-fish"] and worth_delete(f)):
                print u"[卖鱼",
                res = req_safe(productsService, "deleteObjectAMF", uid, f['id'], u'f')
                if res.get('get_food', 0):
                    print u'%d鱼食]' % res['get_food'] ,
            if config["decompose-fish"] and worth_decompose(f):
                print u"[Decompose]",
                res = req_safe(syntheticService, "decomposeFishAMF", uid, f['id'])
                print_decompose_result(res)
    print

# TODO: some function definition
# TODO: Refactor using OOP

# 好友杯具部分 ########################################
def random_order(s):
    return random.sample(s, len(s))
if config["visit-tank"]:
    print u"= 遍历好友鱼缸 ="
    flist = random_order(friends.get('friend_list', []))
else:
    flist = list()
for f in flist:
    info = req_safe(membersService, "getUserInfoAMF", uid, f['id'])
    ftanks = req_safe(productsService, "getMyFishTankListAMF", uid, f['id'])
    userinfo = req_safe(membersService, "getUserInfoAMF", uid, uid)
    petst = req_safe(gameService, "getPetStatusAMF", uid, f['id'])
    synthinfo = req_safe(syntheticService, "getMemberSyntheizeAMF", uid, f['id'])
    #print req_safe(syntheticService, "addRateFriendAMF", uid, f['id'])
    if info['user_info']['almanac_level']<= 2:
        continue
    print '==',
    print_userinfo(info)
    if not synthinfo.get('error', False):
        print_synth_item(synthinfo)
        # 帮助好友提高成功率 ^_^
        if synthinfo['helper_num']< 10:
            print u"帮助好友提高成功率:",
            res = req_safe(syntheticService, "addRateFriendAMF", uid, f['id'], synthinfo['synth_id'])
            print res.get('success_rate', res.get('error', "ERRPR"))
    # 偷鱼
    if petst['status']== u'b' and (not petst['is_stolen']):
        print u"偷鱼:",
        res = gameService.stealAMF(uid, f['id'])
        if res['fish']:
            print_fish(res['fish'])
        else:
            print u"失败"
    elif petst['status']== u'c':
        print u"偷鱼:",
        print "[EVENT Registered]"
        time_line[now()+petst['rest_time']-12] = ('STEAL', (f['id'],))
    req_fail(pubseaService, "getPubSeaInfoAMF", uid)
    userinfo = req_safe(membersService, "getUserInfoAMF", uid, uid)
    req_fail(productsService, "getMyFishTankListAMF", uid, uid)
    time.sleep(0.1)
    for tk in random_order(ftanks):
        userinfo = req_safe(membersService, "getUserInfoAMF", uid, uid)
        if random.randint(0,2)== 0:                    # dummy req
            req_fail(pubseaService, "getPubSeaInfoAMF", uid)
            req_fail(productsService, "getMyFishTankListAMF", uid, f['id'])
            time.sleep(0.3)
        print u"[%s]" % tk['name'], 
        tank = req_safe(productsService, "getMyFishTankObjectListAMF", uid, f['id'], tk['id'])
        if userinfo['user_info']['fish_food']< 2:
            print u"-> 鱼食不足"
            continue
        if userinfo['user_info']['remain_shock_times']< 1:
            print u"-> 电鱼机会不足"
            continue
        # 喂鱼
        if f['id'] in ['your_feedee']:
            is_worth_feed, how_many_need = worth_feed(tank)
            if is_worth_feed:
                print u"喂鱼: 喂食%d" % int(how_many_need/2),
                for _ in xrange(int(how_many_need/2)):
                    res = req_safe(productsService, "feedAMF", uid, f['id'], tk['id'], how_many_need)
                    if res:
                        userinfo['user_info'] = res['user_info']['user_info']
                        tank.update(res['obj_list']) # update here
                        if res.get('get_food', 0):
                            print "*",
        # 电鱼
        is_worth_shock, is_need_feed =  worth_shock(tank)
        if is_worth_shock:
            print u"电鱼:",
            if tank['fish_tank']['is_shocked']:
                res = req_safe(productsService, "shockAMF", uid, f['id'], tk['id'])
                time_line[now()+ res.get('remain_time', 240)*60] = ('SHOCK', (f['id'], tk['id']))
                print '[EVENT Registered]'
                continue                # fixed
            if is_need_feed:
                print u"(喂食2)",
                req_fail(productsService, "feedAMF", uid, f['id'], tk['id'], 2)
            time.sleep(0.1)
            res = req_safe(productsService, "shockAMF", uid, f['id'], tk['id'])
            if res.get('get_shells', 0):
                print u"获得", res['get_shells'], u"贝壳",
                print '[EVENT Registered]',
                time_line[now()+ 4*60*60 - 20] = ('SHOCK', (f['id'], tk['id']))
            else:
                print u"失败", res,
            userinfo = req_safe(membersService, "getUserInfoAMF", uid, uid) # update at last
        print

# 鱼缸信息 ########################################
print u"= 我的鱼缸 ="
ftanks = req_safe(productsService, "getMyFishTankListAMF", uid, uid)
for t in ftanks:
    tank = req_safe(productsService, "getMyFishTankObjectListAMF", uid, uid, t['id'])
    for f in filter(lambda o:o['type']== u'f', tank['objList']):
        if f[style][-1]== '1':
            req_fail(productsService, "deleteObjectAMF", uid, f['id'], u'f')
        else:
            req_fail(productsService, "sellObjectAMF", uid, f['id'], u'f')

    print_tank_detail(tank)

# 抓鱼部分 ########################################          # ^_^

anti_cheating = 90 if config['long-time'] else 35

def catch_fish():
    socket.setdefaulttimeout(None)
    def get_captcha():
        while True:
            try:
                req = urllib2.Request("http://xiaonei.paopaoyu.cn/getCaptcha/?nocache=%d.987654321" % \
                        int(time.time()*1000),
                        headers = {"Cookie": cookie, 
                                   "User-Agent": user_agent,
                                   "Referer": refer})
                break
            except:
                print u"获取验证码失败, 渔民杯具了"
                continue
        fname = tempfile.mktemp(".jpg")
        with open(fname, "wb") as fp:
            fp.write( urllib2.urlopen(req).read() )
        if config['auto-captcha']:
            return cal_captcha(fname) or get_captcha() # recur
        else:
            return ask_captcha(fname)
        #im = Image.open(fname)
        #im = im.filter(ImageFilter.ModeFilter()).filter(ImageFilter.MinFilter())
        #im.show()
        #return int(raw_input("You See:").strip()) 
    def parseJS(js, code):
        if len(code)== 1:
            code = code[0]              # 12.2 modified, useless maybe
        delim = re.findall(r"\d+", js)
        parms = map(int, delim)         # 11.30 modified
        if len(parms)== 2:
            a, b = map(int, delim)
            return str( code[a:b] )
        else:                            # before 11.30, now useless
            a, b, c, d = map(int, delim)        # fixed
            return str( code[a:b] + code[c:d] )

    # def catch_fish begins
    global res, anti_cheating
    max_level = minor_level if minor_level!= 0 else random.choice([1,3,5]) # a random seq
    for i in xrange(1, max_level+1): #
        catched = False
        lv = "%d%d" % (main_level, i)
        level = gameService.catchFishStartLevelAMF(uid, lv, main_level) if i== 1 \
                else gameService.catchFishStartLevelAMF(uid, lv)
        # print level
        if level.get('fish', []):
            print u"此次可抓到:", fish_str( level['fish']['style'] )
            catched = True
            fstr = level['fish']['style']
            if minor_level== 5 and config["auto-filter"]:
                if 'nn' in fstr or 'll' in fstr or 'adl' in fstr or 'z' in fstr or 'fh' in fstr:
                    catched = True
                else:
                    catched = False
                    if i== 5:
                        print u"没好鱼, 杯具不抓了"
                        return
                    else:
                        print u"烂鱼! 跳过"
        socket.setdefaulttimeout(10)    # set
        wait(42+ i*anti_cheating + main_level*7, u"第%d关 ".encode(CODEC) % i)
        socket.setdefaulttimeout(None)  # release
        js = gameService.catchFishCompleteLevelAMF(uid, lv, catched) # odd level you'll get fish
        # print js
        if not js.get('js_script', False):
            print u"出错", js
            if js.get('error','asdf')== u'are you cheating?':
                print u"尝试修改时间参数,重试中..."
                anti_cheating+= 6
                time.sleep(10)
                js = gameService.catchFishCompleteLevelAMF(uid, lv, catched) # try again
                if 'js_script' not in js:
                    return
            else:
                return
        varify_code = level['varify_code']
        code = parseJS(js['js_script'], varify_code)
    for _ in xrange(3):
        captcha_code = int(get_captcha()) # int() is needless
        res = gameService.catchFishGiveUpLevelAMF(uid, lv, code, captcha_code)
        if res and res.get('success', None): # bug here, banned?
            print u"成功捉鱼"
            break
        else:
            print u"失败", res
    req_fail(pubseaService, "getPubSeaInfoAMF", uid)
    socket.setdefaulttimeout(10)

# dummy req
req_fail(pubseaService, "getPubSeaInfoAMF", uid)
req_fail(gameService, "getCatchFishUserInfoAMF", uid)

if __name__ == '__main__':
    while True:
        if config['catch-fish']:
            try:
                catch_fish()
            except:
                print u"捉鱼过程出错, 请确认使用最新版本"
                pass
        else:
            do_time_line()
            a = int(sorted(time_line.keys())[0]-now() + 1)
            if a>= 0:
                print "[EVENTS=%d]" % len(time_line), "Latest:",
                print time.ctime( sorted(time_line.keys())[0] )
                time.sleep(a)
               
        req_fail(pubseaService, "getPubSeaInfoAMF", uid)
        req_fail(gameService, "getCatchFishUserInfoAMF", uid)        
        req_fail(gameService, "getCatchFishUserInfoAMF", uid)
