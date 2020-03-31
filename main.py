# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 16:25:35 2020

@author: Administrator
"""

import re
import os
import time
import datetime
import urllib.request
from pathlib import Path

url = 'http://ocg-card.com'
update_dt = datetime.date.today().strftime('%Y%m')
save_html = Path('./menu_%s.html' % update_dt)

if not save_html.exists():
    
    page = urllib.request.urlopen(url+'/list/').read()
    save_html.write_bytes(page).encode('utf-8')
else:
    page = save_html.read_bytes().decode('utf-8')


mark_star = 'page-template-default page'
mark_end = 'no-icon ad-content-bott'
body = page.split(mark_star)[1].split(mark_end)[0]

save_pack = Path('./pack')

def create_dir(path):
    if not path.exists():
        path.mkdir()
        
        
def update_html():
    html = Path('./html')
    
    for cgr in body.split('list-category">')[1:]:
        cgr_name = cgr.split('<')[0]
        print(cgr_name)
        
        cgr_dir = html / cgr_name
        create_dir(cgr_dir)
        
        for fld in cgr.split('listfolder-list mark"></a>')[1:]:
            fld_name = fld.split('<')[0]
            print(' └─', fld_name)
            
            fld_dir = cgr_dir / fld_name
            create_dir(fld_dir)
            
            for pk in re.findall(r'href="(.+?)">(.+?)</a>', fld):
                pk_url, pk_name = pk
                pack_url = url + pk_url
                pack_html = fld_dir / (pk_name.replace('/', '') + '.html')
                if not pack_html.exists():
                    print(pack_url)
                    page = urllib.request.urlopen(pack_url, timeout=60).read()
                    n = pack_html.write_bytes(page)
                    print('下载完成：', pk_name, n)
                    #time.sleep(30)
                print(' │   └─', pk_name)

update_html()

#
#base_html = Path('./html')
#base_pack = Path('./pack')
#
#create_dir(base_pack)
#
#for cgr in body.split('list-category">')[1:]:
#    cgr_name = cgr.split('<')[0]
#    create_dir(base_html / cgr_name)
#    create_dir(base_pack / cgr_name)
#    
#    for fld in cgr.split('listfolder-list mark"></a>')[1:]:
#        fld_name = fld.split('<')[0]
#        create_dir(base_html / cgr_name / fld_name)
#        create_dir(base_pack / cgr_name / fld_name)
#        
#        for pk in re.findall(r'href="(.+?)">(.+?)</a>', fld):
#            pk_url, pk_name = pk
#            
#            
#            html_path = base_html/cgr_name/fld_name/(pk_name.replace('/', '') + '.html')
#            page = html_path.read_bytes().decode('utf-8')
#            pack_path = base_pack/cgr_name/fld_name/(pk_name.replace('/', '') + '.csv')
#            
#            
##            pk_name = '20th ANNIVERSARY デュエルセット（オベリスクの巨神兵）'
##            html_path = base_html/'商品同梱'/'デュエルセット'/(pk_name.replace('/', '') + '.html')
##            page = html_path.read_bytes().decode('utf-8')
##            pack_path = base_html/'商品同梱'/'デュエルセット'/(pk_name.replace('/', '') + '.csv')
#            
#            
#            if not pack_path.exists():
#                
#                print(pack_path)
#                mark_star = '<header class="article-header entry-header">'
#                mark_end = '<div class="ad">'
#                body = page.split(mark_star)[1].split(mark_end)[0]
#            
#                hd, lt = body.split('<div id="list">')
#            
#                pack_update_dt = re.search('datetime="(.{10})', hd).group(1)
#                card_num = int(re.search('全([0-9]+)枚', hd).group(1))
#                
#                cds = lt.split('card-number')[1:]
#                
#                if card_num != len(cds):
#                    '《{}》卡包全{}枚，已公布{}枚。'.format(pk_name, card_num, len(cds))
#                    continue
#                
#                if pack_path.exists():
#                    os.remove(pack_path)
#                    
#                for cd in lt.split('card-number')[1:]:
#                    card_number = re.search('>(.+?)<', cd).group(1)
#                    m = re.search(r'(back-|mon|magic|trap).+?>(.+?)</td>', cd)
#                
#                    card_name_raw = m.group(2)
#                    card_name_raw = re.sub('<rt>.+?<.+?>', '', card_name_raw)
#                    card_name_raw = re.sub('limit-icon.+?<', '', card_name_raw)
#                    card_name = re.sub('<.+?>', '', card_name_raw)
#                    m = re.search(r'card-category.+?>(.+?)</td>', cd)
#                    if m:
#                        card_category = m.group(1)
#                    else:
#                        continue
#                    
#                    m = re.search(r'card-pass.+?>(.+?)</td>', cd)
#                    if m:
#                        card_pass = m.group(1)
#                    else:
#                        continue
#                    card_text_raw = re.search(r'card-text.+?>(.*?)</td>', cd).group(1)
#                    card_text = re.sub('<.*?>', '', card_text_raw)
#                    card_rare = re.findall('img/card.+?>(.+?)<', cd)
#                    if m.group(1) == 'mon':
#                        card_attr = re.search(r'card-attr.+?>(.+?)</td>', cd).group(1)
#                        card_type = re.search(r'card-type.+?>(.+?)</td>', cd).group(1)
#                        card_star = re.search(r'(card-star|non-stts).+?>(.+?)</td>', cd).group(2)
#                        card_force = re.findall(r'card-force.+?>(.+?)</td>', cd)
#                        if len(card_force) == 2:
#                            card_atk, card_def = card_force
#                        else:
#                            card_atk = card_force[0]
#                            card_def = '-'
#                    else:
#                        card_attr, card_type, card_star, card_atk, card_def = ['']*5
#                
#                    if 'リンク' in  card_category:
#                        card_link = re.search(r'card-link">LINK-([0-9]+)', cd).group(1)
#                        card_arrow = re.search(r'card-link.+?：(.+?)<', cd).group(1).replace(' ','')
#                    elif 'ペンデュラム' in  card_category:
#                        if card_name != 'EMクリボーダー':
#                            card_pscale = re.search(r'card-p-scale.+?>(.+?)</td>', cd).group(1)
#                            card_ptext = card_text
#                            card_text_raw = re.search(r'card-text.+?>(.*?)</td>', cd.split('card-text',1)[1]).group(1)
#                            card_text = re.sub('<.*?>', '', card_text_raw)
#                    else:
#                        card_link, card_arrow, card_pscale, card_ptext = ['']*4
#                    
#                    line = ','.join([card_number, card_name, card_pass, card_category, card_text])
#                    with open(pack_path, 'a', encoding='utf-8') as f:
#                        f.write(line+'\n')
#
#










