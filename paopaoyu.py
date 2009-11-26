#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  FileName    : test.py 
#  Author      : Feather.et.ELF <andelf@gmail.com> 
#  Created     : Sun Nov 15 21:02:04 2009 by Feather.et.ELF 
#  Copyright   : Feather Workshop (c) 2009 
#  Description : paopaoyu amf test 
#  Time-stamp: <2009-11-26 20:17:34 andelf> 

import socket
socket.setdefaulttimeout(8)
import httplib
# httplib.HTTPConnection.debuglevel = 1
from pyamf.remoting.client import RemotingService
import time
import Image
import urllib2
import random
import ImageFilter
import re
import os
import sys
from utils import print_tank, print_fish, fish_str, print_tank_detail, \
     worth_shock, print_userinfo, pr, get_cookie, sleepbar, worth_feed, \
     worth_delete, family_dict, safe_decode, __VERSION__

CODEC = 'utf-8'
if os.name== 'nt':
    reload(sys)
    sys.setdefaultencoding('gb18030')   # codec fixed
    CODEC = 'gb18030'

print u"悲剧渔民 %s 版 By xxx" % __VERSION__

main_level = None
username = 'username'
password = 'password'

# 登录部分TODO: add more
if len(sys.argv)== 4:
    username = sys.argv[1]
    password = sys.argv[2]
    main_level = int(sys.argv[3])

while True:
    try:
        cookie, uid = get_cookie(username, password)
        break
    except:
        print u"登录失败, 重试."
        continue

print u"获得 Uid:", uid

# AMF 连接设置
client = RemotingService("http://xiaonei.paopaoyu.cn/gateway/")
client.addHTTPHeader('Referer', "http://xnimg.cn/xcube/app/25049/media/swf/v10/game.swf")
client.addHTTPHeader('Connection', "close")
client.addHTTPHeader('Cookie', cookie)
client.user_agent = "Mozilla/5.0 (X11; Linux mips; U; zh-cn) Gecko/20091010 BeiJu/0.0.1"

membersService = client.getService("membersService")
productsService = client.getService("productsService") # // 鱼市
gameService = client.getService("gameService")  # // 抓鱼
faqsService = client.getService("faqsService") # // FAQ, 暂时没用
spacesService = client.getService("spacesService") # //
almanacService = client.getService("almanacService") # // 图鉴
inviteService = client.getService("inviteService") # // 邀请
pubseaService = client.getService("pubseaService") # //

# 杯具, 连接封装, 搞定泡泡鱼卡的问题
def req_safe(servicename, methodname, *args):
    while True:
        try:
            return servicename.__getattr__(methodname)(*args)
        except:
            print u'%s 请求失败, 重试!' % methodname
            client.connection.close()
            time.sleep(0.3)
            continue

def req_fail(servicename, methodname, *args):
    while True:
        try:
            return servicename.__getattr__(methodname)(*args)
        except:
            print u'%s 请求失败, 放弃!' % methodname
            client.connection.close()
            break                           # do nothing
    
def wait(sec=70, txt=''):
    t = random.randint(-7, 2) + sec
    sleepbar(t, txt)
    # while time.time() - t < sec+random.randint(-5, 1):
    #     gameService.getCatchFishUserInfoAMF(uid) if int(time.time()) % 3== 0 else ()
    #     spacesService.getFriendListAMF(uid) if int(time.time()) % 3== 1 else ()
    #     productsService.getMyFishTankListAMF(uid, uid) if int(time.time()) % 3== 2 else ()
    #     time.sleep(2.2)

newmsg = req_safe(spacesService, "getNewMsgAMF", uid, uid)
userinfo = req_safe(membersService, "getUserInfoAMF", uid, uid)
seainfo = req_safe(pubseaService, "getPubSeaInfoAMF", uid)
fishinfo = req_safe(gameService, "getCatchFishUserInfoAMF", uid)

if newmsg:
    print u"有 %d 条新信息." % newmsg.get('new_msg_num', 0)
if userinfo:
    print_userinfo(userinfo)
# print seainfo                           # 公告等
if (not main_level) or (main_level not in [2,3]):
    print u"自动根据等级设置抓鱼区域."
    main_level = fishinfo.get('tempo', 2)

# 好友 #############################
print u"= 好友信息 ="
friends = req_safe(spacesService, "getFriendListAMF", uid) # or refreshFriendListAMF
for f in friends.get('friend_list', []):
    print u"%s 等级%d Id#%d" % (safe_decode(f['nickname']), f['almanac_level'], f['id'])
print u"共 %d 好友" % len( friends.get('friend_list', []))

# 收鱼部分 ########################################
print u"= 潜艇鱼 ="
petst = req_safe(gameService, "getPetStatusAMF", uid, uid)
if petst:
    if petst['status']== u'c':
        print u"抓鱼剩余时间 %d 秒." % (petst['rest_time'] or 0)
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
            petst = req_safe(gameService, "dispatchAMF", uid, main_level)


# 塑料袋部分 ########################################
print u"= 塑料袋 ="
types = [2, 3, 5, 7, 11, 13, 17]
for t in types:
    print u"== %s ==" % family_dict.get(t, str(t))
    fishes = []
    for i in xrange(1, 100):            # big enough
        res = req_safe(productsService, "getMyBagObjectListAMF", uid, t, u'f', i)
        if not res['objList']:
            print u"共%d条" % res['total_num']
            break
        fishes.extend( res['objList'] )
    for f in fishes:
        print fish_str(f['style']),
        if 0: # worth_delete(f):
            print u"[卖鱼",
            res = req_safe(productsService, "deleteObjectAMF", uid, f['id'], u'f')
            if res.get('get_food', 0):
                print u'%d鱼食]' % res['get_food'] ,
    print 

# TODO: some function definition
def shock():
    pass

def feed():
    pass

def steal():
    pass

# 好友杯具部分 ########################################
print u"= 遍历好友鱼缸 ="
for f in friends.get('friend_list', []):    
    info = req_safe(membersService, "getUserInfoAMF", uid, f['id'])
    ftanks = req_safe(productsService, "getMyFishTankListAMF", uid, f['id'])
    petst = req_safe(gameService, "getPetStatusAMF", uid, f['id'])
    print '====',
    print_userinfo(info)    
    # 偷鱼
    if petst['status']== u'b' and (not petst['is_stolen']):
        print u"偷鱼:",
        res = gameService.stealAMF(uid, f['id'])
        if res['fish']:
            print_fish(res['fish'])
        else:
            print u"失败"
    req_fail(pubseaService, "getPubSeaInfoAMF", uid)
    userinfo = req_safe(membersService, "getUserInfoAMF", uid, uid)
    req_fail(productsService, "getMyFishTankListAMF", uid, uid)
    time.sleep(0.1)
    for i, tk in enumerate(ftanks):
        if userinfo['user_info']['fish_food']< 2:
            print u"-> 鱼食不足, 放弃遍历"
            break
        if userinfo['user_info']['remain_shock_times']< 1:
            print u"-> 电鱼机会不足, 放弃遍历"
            break
        if i% 2== 0:                    # dummy req
            req_fail(pubseaService, "getPubSeaInfoAMF", uid)
            req_fail(productsService, "getMyFishTankListAMF", uid, f['id'])
            time.sleep(0.3)
        print u"[%s]" % tk['name'], 
        tank = req_safe(productsService, "getMyFishTankObjectListAMF", uid, f['id'], tk['id'])
        # 喂鱼
        if f['id'] in []:# [844206]: # [590851]:
            print worth_feed(tank),
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
            if is_need_feed:
                print u"(喂食2)",
                req_fail(productsService, "feedAMF", uid, f['id'], tk['id'], 2)
            time.sleep(0.1)
            res = req_safe(productsService, "shockAMF", uid, f['id'], tk['id'])
            if res.get('get_shells', 0):
                print u"获得", res['get_shells'], u"贝壳",
            else:
                print u"失败", res,
            userinfo = req_safe(membersService, "getUserInfoAMF", uid, uid) # update at last
        print

# 鱼缸信息 ########################################
print u"= 我的鱼缸 ="
ftanks = req_safe(productsService, "getMyFishTankListAMF", uid, uid)
for t in ftanks:
    # print_tank(t) 
    tank = req_safe(productsService, "getMyFishTankObjectListAMF", uid, uid, t['id'])
    print_tank_detail(tank)

# 抓鱼部分 ########################################
socket.setdefaulttimeout(None)          # ^_^

def catch_fish():
    def get_captcha():
        req = urllib2.Request("http://xiaonei.paopaoyu.cn/getCaptcha/?nocache=%d.a_test_only" % int(time.time()),
                              headers = {"Cookie": cookie})
        with open("tmp.gif", "wb") as fp:
            fp.write( urllib2.urlopen(req).read() )
        im = Image.open("tmp.gif")
        # im = im.filter(ImageFilter.ModeFilter()).filter(ImageFilter.MinFilter())
        im.show()
        return raw_input("You See:").strip()
    def parseJS(js, code):
        if len(code)== 1:
            code = code[0]
        else:
            return 
        delim = re.findall(r"\d+", js)
        a, b, c, d = map(int, delim)        # fixed
        return str( code[a:b] + code[c:d] )

    # def catch_fish begins
    for i in xrange(1, 5+1):
        lv = "%d%d" % (main_level, i)
        level = gameService.catchFishStartLevelAMF(uid, lv, main_level) if i== 1 \
                else gameService.catchFishStartLevelAMF(uid, lv)
        if level['fish']:
            print u"此次可抓到:", fish_str( level['fish']['style'] )
        wait(40+ i*4, u"第%d关 ".encode(CODEC) % i)
        js = gameService.catchFishCompleteLevelAMF(uid, lv, i%2== 1) # odd level you'll get fish
        if not js.get('js_script', False):
            print u"出错", js
            return
        varify_code = level['varify_code'], 
        code = parseJS(js['js_script'], varify_code)
    res = 0
    while not res:
        captcha_code = get_captcha()
        os.system('killall xv')         # for linux only
        res = gameService.catchFishGiveUpLevelAMF(uid, lv, code, captcha_code)
        if res and res.get('success', None):
            print u"成功捉鱼"
        else:
            print res
            res = None
    pubseaService.getPubSeaInfoAMF(uid)

# dummy req
req_fail(pubseaService, "getPubSeaInfoAMF", uid)
req_fail(gameService, "getCatchFishUserInfoAMF", uid)

if __name__ == '__main__':
    while True:
        catch_fish()
        req_fail(pubseaService, "getPubSeaInfoAMF", uid)
        req_fail(gameService, "getCatchFishUserInfoAMF", uid)
        time.sleep(1.1)
        req_fail(gameService, "getCatchFishUserInfoAMF", uid)
