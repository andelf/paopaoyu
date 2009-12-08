#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  FileName    : utils.py 
#  Author      : Feather.et.ELF <andelf@gmail.com> 
#  Created     : Tue Nov 17 21:26:12 2009 by Feather.et.ELF 
#  Copyright   : Feather Workshop (c) 2009 
#  Description : PaoPaoYu util funcs 
#  Time-stamp: <2009-12-08 21:15:10 andelf> 

import urllib2
import urllib
import re
import sys
from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, ETA
import time
from Tkinter import Frame, TOP, Entry, BOTTOM, Label, \
     StringVar, Tk, X, RIGHT, LEFT, Button, IntVar, Radiobutton, W, Checkbutton, YES
from ImageTk import PhotoImage
import Image

__VERSION__ = '0.0.6'

pr = sys.stdout.write

family_dict = {2:u'团团族', 3:u'迅风族', 5:u'三刀族', 7:u'豆花族',
               11:u'巨角族', 13:u'暴米族', 30030:u'全族', 1:u'X族'}

def now():
    return time.time()

# code from www.java2s.com
class Checckbar(Frame):
    def __init__(self, parent=None, picks=[], side=LEFT, anchor=W, default=[]):
        Frame.__init__(self, parent)
        self.vars = []
        for i,pick in enumerate(picks):
            var = IntVar()
            chk = Checkbutton(self, text=pick, variable=var)
            chk.pack(side=side, anchor=anchor, expand=YES)
            if i< len(default):
                var.set(default[i])
            self.vars.append(var)
    def state(self):
        return map((lambda var: bool(var.get())), self.vars)


# 12.7 update
val = 0                                 # use as global
def cal_captcha(fname='./tmp.jpg'):
    global val
    im = Image.open(fname)
    def crop_box(pos):
        x, y = pos
        return im.crop((x, y, x+60, y+60))
    def like_fish(im): # fuck it
        result = []
        for x in range(37, 41) + range(18,22):
            for y in range(37,41):
                result.append( reduce(lambda x,y:x*y, im.getpixel((x,y)), 1) )
        return max(result) - min(result)
    def crop_test(im):
        result = []
        for y in xrange(3):
            for x in xrange(4):
                pos = (x*65, y*65)
                sub_im = crop_box(pos)
                match_val = like_fish(sub_im)
                if match_val< 13000000:
                    result.append( (match_val,  x+4*y+1) )
        if result:
            result.sort()
            return result[0][1]
        return 0
    val = crop_test(im)
    if val!= 0:
        print u"尝试自动识别成功. 位置%d发现匹配水草." % val
        return val
    else:
        print u"自动识别失败."
        return 5
    # return ask_captcha(fname)

def ask_captcha(fname='./tmp.jpg'):
    def on_click(event):
        global val
        if event.num== 1:
            cx, cy = (event.x, event.y)
            for y in xrange(3):
                for x in xrange(4):
                    if ((x*65+30-cx)**2+(y*65+30-cy)**2)**0.5< 25:
                        val = x+4*y+1
                        root.destroy()
    root = Tk()
    image = PhotoImage(file=fname)
    lbl = Label(root, image=image)
    lbl.bind("<Button-1>", on_click)
    lbl.pack()
    root.title(u"单击水草")
    root.mainloop()
    return val

# useless
def ask_captcha_old(fname='./tmp.jpg'):
    root = Tk()
    top = Frame(root)
    top.pack()
    image=PhotoImage(file=fname)
    Label(top, image=image).pack(side=TOP)
    var = StringVar()
    widget = Entry(top, textvariable=var)
    widget.focus_force()                # Put keyboard focus on Entry
    def set_code(event=None):
        captcha = var.get()
        if len(captcha)>= 2:
            var.set("")
        else:
            root.destroy()
    widget.bind("<Key-Return>", set_code)
    widget.pack(side=BOTTOM)
    root.title(u"验证码:")
    root.mainloop()
    return var.get()
    
def ask_basic_info():
    root = Tk()
    # username
    left_frame = Frame(root)
    user_frame = Frame(left_frame)
    user_frame.pack()
    Label(user_frame, text=u"用户名:").pack(side=LEFT, padx=5)
    username = StringVar()
    ue = Entry(user_frame, textvariable=username)
    ue.pack(side=RIGHT, padx=5)
    username.set("")
    ue.focus_force()
    user_frame.pack(expand=1, fill=X, pady=5,  padx=5)
    # passworkd
    pass_frame = Frame(left_frame)
    pass_frame.pack()
    Label(pass_frame, text=u"　密码:").pack(side=LEFT, padx=5)
    password = StringVar()
    pe = Entry(pass_frame, textvariable=password, show="*")
    pe.pack(side=RIGHT, padx=5)
    def ask(_=None):
        if len(username.get()) * len(password.get())== 0:
            pass
        else:
            root.destroy()
    pe.bind("<Key-Return>", ask)
    password.set("password")
    pass_frame.pack(expand=1, fill=X, pady=5,  padx=5)
    # dumu / cixun
    level_frame = Frame(left_frame)
    main_level = IntVar()
    Radiobutton(level_frame, text=u"雌雄双煞", value=2, variable=main_level).pack(side=LEFT)
    Radiobutton(level_frame, text=u"杜姆之巢", value=3, variable=main_level).pack(side=LEFT)
    main_level.set(2)
    level_frame.pack()
    # minor
    minor_level_frame = Frame(left_frame)
    minor_level = IntVar()
    Label(minor_level_frame, text=u"子关选择:").pack(side=LEFT, padx=5)
    Radiobutton(minor_level_frame, text=u"1", value=1, variable=minor_level).pack(side=LEFT)
    Radiobutton(minor_level_frame, text=u"3", value=3, variable=minor_level).pack(side=LEFT)
    Radiobutton(minor_level_frame, text=u"5", value=5, variable=minor_level).pack(side=LEFT)
    Radiobutton(minor_level_frame, text=u"随机", value=0, variable=minor_level).pack(side=LEFT)
    minor_level.set(5)
    minor_level_frame.pack()
    # misc
    misc_item = [u"使用自动验证码识别", u"提高时间参数(防封号)"]
    default_var = [1, 0]
    misc_bar = Checckbar(left_frame, misc_item, default=default_var, side=TOP)
    misc_bar.pack()
    #
    left_frame.pack(side=LEFT)
    # bool config
    config_item = [u"捉鱼", u"访问鱼缸", u"换鱼食", u"点化鱼", u"合成鱼"]
    default_var = [1, 1, 0, 0, 1]
    config_bar = Checckbar(root, config_item, default=default_var, side=TOP)
    config_bar.pack(side=LEFT)
    # login
    Button(root, text=u"登录", command=ask).pack(side=LEFT)
    root.title(u"欢迎使用杯具渔民 %s" % __VERSION__)
    root.mainloop()
    return (username.get(), password.get(), main_level.get(), minor_level.get(),
            misc_bar.state() + config_bar.state())

########################################

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

def second_str(s):
    minute = int(s/60)
    hour = int(minute/60)
    minute = minute % 60
    second = int(s % 60)
    return u"".join([u"%d小时" % hour if hour else "",
                     u"%d分" % minute if minute else "",
                     u"%d秒" % second if second else ""])

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

def safe_decode(s):
    return s.encode('gbk', 'ignore').decode('gbk')

def print_userinfo(userinfo):
    print u"昵称 %s, Id#%d, 等级 %d, 剩余鱼食 %d, 电鱼机会 %d, 贝壳 %d, 珍珠 %d, 经验 %d/%d" % \
          (safe_decode(userinfo['user_info']['nickname']),
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
    bk = 0                              # how many you'll get
    need_feed = False
    for f in filter(lambda o:o['type']== u'f', td['objList']):
        bk += f.get('star', 0) * int( f.get('style', 'f_f7_l1_0').split('_')[-1] )
        if f.get('hungry', 0)< 1:
            need_feed = True
    return (bk> 35, need_feed)
    #return (bk> 30, True) #  force need feed here / need_feed) 
        
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
    return f['family']> 1 and f['hungry']== 0 and f['star']== 1 and \
           (f['style'].split('_')[2] in cd) and f['exp']== 0 and f['style'].split('_')[3]== '1'

def worth_decompose(f):
    cd = {'l':u'绿', 'l1':u'蓝', 'h':u'黄', 'h1':u'红'}
    return f['family']> 1 and f['hungry']== 0 and f['star']<= 1 and \
           (f['style'].split('_')[2] in cd) and f['exp']== 0 and f['style'].split('_')[3]== '1'


def get_cookie(email, password):
    cookie_handler = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookie_handler)
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (X11; Linux mips; U; zh-cn) Gecko/20091010 BeiJu/%s' % (__VERSION__,) ),
        ('Referer', 'http://apps.renren.com/paopaoyu/?origin=104'),
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
    #print res.read()
    #return                              # test
    url = re.findall(r'id="iframe_canvas" src="([^"]+)"', res.read())
    if not url:
        print u"用户名/密码错误!"
        sys.exit(-1)
    url = url[0]
    url = url.replace('amp;', '') # .replace('?', '/?')
    print u"获得转接Url"# , url
    res = opener.open(url) #
    data = res.read()
    cookiejar = cookie_handler.cookiejar
    cookies = cookiejar._cookies_for_request(urllib2.Request('http://xiaonei.paopaoyu.cn/some_fack_url'))
    uid = re.findall(r'my_id=(\d+)&', data)
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
    #ask_captcha()
    #print ask_basic_info()


if __name__ == '__main__':
    test()
 
