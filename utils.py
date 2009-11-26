#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  FileName    : utils.py 
#  Author      : Feather.et.ELF <andelf@gmail.com> 
#  Created     : Tue Nov 17 21:26:12 2009 by Feather.et.ELF 
#  Copyright   : Feather Workshop (c) 2009 
#  Description : PaoPaoYu util funcs 
#  Time-stamp: <2009-11-26 17:20:05 andelf> 

import urllib2
import urllib
import re
import sys
from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, ETA
import time


__VERSION__ = '0.0.2'

pr = sys.stdout.write

# 使用素数
family_dict = {2:u'团团族', 3:u'迅风族', 5:u'三刀族', 7:u'豆花族', 11:u'巨角族', 13:u'暴米族', 30030:u'全族', \
               17:u'X族'}

def fish_str(s):
    _, kind, color, lv = s.split('_')
    kd = {'ly':u'鲤鱼', 'dd':u'点点', 'f7':u'印度神仙', 'wns':u'维纳斯', 'bmy':u'斑马鱼', 'pk':u'朋克',
          'dby':u'大宝鱼', 'f8':u'珍珠虎', 'yzm':u'一枝梅', 'f10':u'三间火箭', 'chy':u'彩虹鱼',
          'll':u'丽丽', 'nn':u'牛牛', 'f13':u'金鱼', 'cg':u'彩冠', 'df':u'刀锋', 'jc':u'吉彩',
          'f11':u'吊吊', 'adl':u'阿迪龙', 'f12':u'罗汉', 'f15':u'巴浪', 'f9':u'神仙'}
    cd = {'l':u'绿', 'h1':u'红', 'l1':u'蓝', 'h':u'黄', 'fh':u'粉红',
          'jh':u'橘红', 'qfh':u'浅粉红', 'z':u'紫'}
    k = kd.get(kind, kind)
    c = cd.get(color, color)
    return u"%s%s（%s级）" % (c, k, lv)

def print_fish(f):
    # {'status': u'NM', 'is_highest_level': False, 'strength': 5, 'star': 2, 'name': u'\u7d2b\u7ef4\u7eb3\u65af\uff081\u7ea7\uff09', 'family': 7, 'level': 0, 'max_exp': 400, 'endurance': 9, 'max_life': 720, 'life': 720, 'hungry': 95.544444444444451, 'price': 0, 'agility': 9, 'style': u'f_wns_z_1', 'fishtank_id': 8382994, 'exp': 5.5694444444444446, 'can_be_potion': True, 'type': u'f', 'id': 164829662}
    if not f.has_key('hungry'):
        print fish_str(f['style'])
        return 
    print f['name'], family_dict.get(f['family'], f['family']), u'饥饿%d%%' % int(f['hungry']), \
          u"经验%d/%d" % (int(f['exp']), f['max_exp']), "Id#%d" % f['id']

def print_tank(t):
    # {'style': u't_pool', 'is_first': 1, 'star': 2, 'name': u'\u9c7c\u5858', 'family': 30030, 'price': 2483, 'is_shocked': False, 'extra_growth_speed': 0, 'troll_times': 0, 'pool_bg': u'poolBg_1', 'troll_price': 0, 'is_pool': 1, 'capacity': 8, 'can_be_trolled': 0, 'type': u't', 'id': 870225}
    print u"[%s] %d星 %s %d格 Id#%d" % (t['name'], t['star'], family_dict.get(t['family'], str(t['family'])),
                                      t['capacity'], t['id']),
    print u"钓鱼%dBK/%d次" % (t['troll_price'], t['troll_times']) if t['can_be_trolled'] else "",
    print u"已被电" if t['is_shocked'] else u"未被电"

def print_userinfo(userinfo):
    print u"昵称 %s, Id#%d, 图鉴等级 %d, 剩余鱼食 %d, 电鱼机会剩余 %d, 贝壳 %d, 珍珠 %d, 经验 %d/%d" % \
          (userinfo['user_info']['nickname'],
           userinfo['user_info']['id'],
           userinfo['user_info']['almanac_level'],
           userinfo['user_info']['fish_food'],
           userinfo['user_info']['remain_shock_times'],
           userinfo['user_info']['shells'],
           userinfo['user_info']['pearls'],
           userinfo['user_info']['exp'],
           userinfo['user_info']['next_exp'],
           )

def print_tank_detail(td):
    print_tank(td['fish_tank'])
    fishes = filter(lambda o:o['type']== u'f', td['objList'])
    if fishes:
        print "="* 20
        map(print_fish, fishes)
        print "="* 20

def worth_shock(td):
    if td['fish_tank']['is_shocked']:
        return (False, False)
    bk = 0                              # how many you'll get
    need_feed = False
    for f in filter(lambda o:o['type']== u'f', td['objList']):
        bk += f.get('star', 0) * int( f.get('style', 'f_f7_l1_0').split('_')[-1] )
        if f.get('hungry', 0)< 1:
            need_feed = True
    return (bk> 20, need_feed)
    # return (bk> 10, True) #  force need feed here / need_feed) 
        
def worth_feed(td):
    star = td['fish_tank'].get('star', 1)
    family = td['fish_tank'].get('family', 30030)
    fishes = filter(lambda o:o['type']== u'f', td['objList'])
    how_many = []
    if len(td['objList'])!= td['fish_tank'].get('capacity', 0):
           return (False, 0)
    for f in fishes:
        if f['is_highest_level']:
            return (False, 0)
        elif f['star']> star:
            return (False, 0)
        elif family!= 30030 and f['family']!= family:
            return (False, 0)
        elif f['hungry']> 60:           # fuck
            return (False, 0)
        else:
            how_many.append( 70 - f['hungry'])
    return (True, int(min(how_many)))

def worth_delete(f):
    # {'status': u'NM', 'is_highest_level': False, 'strength': 5, 'star': 1, 'name': u'\u84dd\u70b9\u70b9\u9c7c\uff081\u7ea7\uff09 ', 'family': 11, 'level': 0, 'max_exp': 100, 'endurance': 5, 'max_life': 720, 'life': 719.34194444444449, 'hungry': 0, 'price': 0, 'agility': 3, 'style': u'f_dd_l1_1', 'fishtank_id': 0, 'exp': 0, 'can_be_potion': True, 'type': u'f', 'id': 190420645}
    cd = {'l':u'绿', 'l1':u'蓝', 'h':u'黄'}
    return f['family']< 14 and f['hungry']== 0 and \
           (f['style'].split('_')[2] in cd) and f['exp']== 0 and f['style'].split('_')[3]== '1'

def get_cookie(email, password):
    cookie_handler = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookie_handler)
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (X11; Linux mips; U; zh-cn) Gecko/20091010 BeiJu/%s' % (__VERSION__,) ),
        ('x-flash-version', '11,0,32,18') ] # flash 11 better?
    print u"模拟页面登陆... 用户: %s." % email
    url = "http://passport.renren.com/PLogin.do" # 9.22 modify
    data = {'email' : email,
            'password' :  password,
            'domain'   : 'renren.com',
            'origURL' : "http://apps.renren.com/paopaoyu/?origin=104" }
    dataEncoded = urllib.urlencode(data)
    req = urllib2.Request(url, data = dataEncoded)
    res = opener.open(req)
    url = re.findall(r'id="iframe_canvas" src="([^"]+)"', res.read())
    if not url:
        print u"用户名/密码错误!"
        sys.exit(-1)
    url = url[0]
    url = url.replace('amp;', '') # .replace('?', '/?')
    print u"获得转接Url", url
    res = opener.open(url) # 
    cookiejar = cookie_handler.cookiejar
    cookies = cookiejar._cookies_for_request(urllib2.Request('http://xiaonei.paopaoyu.cn/some_fack_url'))
    uid = re.findall(r'member_id=(\d+)&', res.read())
    uid = int(uid[0])
    return (''.join(["%s=%s;" % (ck.name, ck.value) for ck in cookies]), uid)

def sleepbar(tm=50, txt=''):
    pbar = ProgressBar(widgets=[txt, Percentage(), Bar(marker=RotatingMarker(), left='[', right=']'), ' ', ETA()], maxval=300).start()
    for i in range(300):
        time.sleep(tm/300.0)
        pbar.update(i+1)
    pbar.finish()

def test():
    print fish_str("f_ly_l_1")
    print fish_str("f_dd_h1_1")
    print fish_str("f_f7_l1_1")
    print fish_str("f_dby_l_1")

if __name__ == '__main__':
    test()
 
