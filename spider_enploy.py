# -*- coding = utf-8 -*-
# @Time : 2020/11/21 19:24
from bs4 import BeautifulSoup
from urllib import parse
import multiprocessing
from selenium import webdriver
import re
import xlwt
import time
import requests
import variables

def main():
    variables.keyword=input("请输入你要搜索的岗位关键字：")
    variables.Keyword = parse.quote(parse.quote(variables.keyword))
    variables.pagenum = int(input("请输入你要爬取的数据页数（一页五十条数据）："))
    for i in range(0, variables.pagenum):
        variables.list_baseurl.append(
            "https://search.51job.com/list/000000,000000,0000,00,9,99," +variables.Keyword + ",2," + str(
                i + 1) + ".html")
    spider_1()
    spider_2()
    spider_3()
    savedata()

def askURL(url):
    head = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit "
                      "/ 537.36(KHTML, likeGecko) Chrome / "
                      "87.0.4280.66Safari / 537.36"
    }
    if url=="暂未填写":
        return 0
    res=requests.get(url,headers=head)
    str=res.apparent_encoding
    if re.search('GB.*',str):
        str='GBK'
    html = ""
    res.encoding=str
    html=res.text
    return html

def askURL_base(baseurl):
    opt = webdriver.ChromeOptions()
    opt.add_argument('headless')
    driver = webdriver.Chrome(executable_path=r'chromedriver', options=opt)
    driver.get(baseurl)
    element = driver.page_source
    driver.quit()
    return element

def getData_1(element):

    bs = BeautifulSoup(element, "html.parser")
    resultList_a = bs.select("div.j_joblist > div.e > a.el")
    resultList_name = bs.select("div.j_joblist > div.e > a.el > p.t >span.jname.at")
    resultList_time = bs.select("div.j_joblist > div.e > a.el > p.t >span.time")
    resultList_salary = bs.select("div.j_joblist > div.e > a.el > p.info >span.sal")
    resultList_position = bs.select("div.j_joblist > div.e > a.el > p.info >span.d.at")
    resultList_subsidy= bs.select("div.j_joblist > div.e > a.el ")
    resultList_company = bs.select("div.j_joblist > div.e > div.er >a")
    resultList_type_num = bs.select("div.j_joblist > div.e > div.er >p.dc.at")
    resultList_company_project = bs.select("div.j_joblist > div.e > div.er >p.int.at")

    for i in resultList_a:
        variables.list_a.append(i["href"])
    for item in resultList_name:
        item = str(item)
        variables.list_title.append(re.findall(re.compile(r'<span class="jname at" title=".*">(.*)</span>'), item))
    for item in resultList_time:
        item = str(item)
        variables.list_time.append(re.findall(re.compile(r'<span class="time">(.*)</span>'), item))
    for item in resultList_salary:
        item = str(item)
        variables.list_salary.append(re.findall(re.compile(r'<span class="sal">(.*)</span>'), item))
    for item in resultList_position:
        item = str(item)
        variables.list_positon.append(re.findall(re.compile(r'<span class="d at">(.*)</span>'), item))
    for item in resultList_subsidy:
        item = str(item)
        m = re.findall(re.compile(r'<p class="tags" title="(.*)"><span>'), item)
        if (0!= len(m)):
            variables.list_subsidy.append(m)
        else:
            variables.list_subsidy.append("暂未填写")
    for item in resultList_company:
        item = str(item)
        variables.list_company_a.append(re.findall(re.compile(r'a class="cname at" href="(.*)" target'), item))
    for item in resultList_company:
        item = str(item)
        variables.list_company_name.append(re.findall(re.compile(r'title="(.*)">'), item))
    for item in resultList_type_num:
        item = str(item)
        variables.list_type_num.append(re.findall(re.compile(r'<p class="dc at">(.*)</p>'), item))
    for item in resultList_company_project:
        item = str(item)
        variables.list_company_project.append(re.findall(re.compile(r'<p class="int at">(.*)</p>'), item))


def getData_2(html):
    bs = BeautifulSoup(html, "html.parser")
    resultList_require=bs.select("div.bmsg.job_msg.inbox")
    if(len(resultList_require)!=0):
        for item in resultList_require:
            item=filter_tag(str(item))
            variables.list_require.append(item)
    else:
        variables.list_require.append("暂未填写")
    resultList_address = bs.select("div.bmsg.inbox>p.fp")
    if(len(resultList_address)!=0):
        for item in resultList_address:
            item = filter_tag(str(item))
            variables.list_address.append(item)
    else:
        variables.list_address.append("暂未填写")
    resultList_a_2 = bs.select("div.tHeader.tHjob > div.in > div.cn > p.cname >a.catn")
    m=0
    for item in resultList_a_2:
        m=m+1
    if(m==0):
        variables.list_a_2.append("暂未填写")
        variables.list_company_address.append('暂未填写')
        variables.list_company_web.append('暂未填写')
    else:
        for i in resultList_a_2:
            variables.list_a_2.append(i["href"])

def getData_3(html):
    if html==0:
        return 0
    bs = BeautifulSoup(html, "html.parser")
    resultList_company_message=bs.select("div.tBorderTop_box.bmsg > div.inbox >p.fp ")
    if(len(resultList_company_message))==0:
        variables.list_company_address.append("暂未填写")
        variables.list_company_web.append("暂未填写")
    elif(len(resultList_company_message))==1:
        variables.list_company_address.append(filter_tag(str(resultList_company_message[0])))
        variables.list_company_web.append("暂未填写")
    else:
        variables.list_company_address.append(filter_tag(str(resultList_company_message[0])))
        variables.list_company_web.append(filter_tag(str(resultList_company_message[1])))

def spider_1():
    print("------------------------第一层爬取-------------------------")
    time_1 = time.time()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    list = pool.map(askURL_base, variables.list_baseurl)
    for i in range(0, len(list)):
        print("----------------------第一层解析第" + str(i + 1) + "次----------------------")
        getData_1(list[i])
    pool.close()
    pool.join()
    print("------------------------爬取成功！-------------------------")
    print("第一层数据爬取耗时：", time.time() - time_1, "秒")


def spider_2():
    print("------------------------第二层爬取-------------------------")
    time_2 = time.time()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    list1 = pool.map(askURL, variables.list_a)
    pool.close()
    pool.join()
    for i in range(0, len(list1)):
        print("----------------------第二层解析第" + str(i + 1) + "次----------------------")
        getData_2(list1[i])
    print("------------------------爬取成功！-------------------------")
    print("第二层数据爬取耗时：", time.time() - time_2, "秒")


def spider_3():
    print("------------------------第三层爬取-------------------------")
    time_3 = time.time()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    list2 = pool.map(askURL, variables.list_a_2)
    pool.close()
    pool.join()
    for i in range(0, len(list2)):
        print("----------------------第三层解析第" + str(i + 1) + "次----------------------")
        getData_3(list2[i])
    print("------------------------爬取成功！-------------------------")
    print("第三层数据爬取耗时：", time.time() - time_3, "秒")

def savedata():
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheet = book.add_sheet(variables.keyword+"招聘信息", cell_overwrite_ok=True)
    print("-------------------------写入数据-------------------------")
    col = ("招聘链接", "招聘职位", "发布时间", "工资", "工作地点", "补贴", "公司信息链接",
           "公司名称", "公司类型、规模", "主营","工作要求","工作地址","公司地址","公司官网")
    for i in range(0,13):
        if(i==0 or i==4 or i==5 or i==6 or i==7 or i==11 or i==12 or i==13):
            sheet.col(i).width = 10000
        if (i == 1 or i == 8 or i == 9):
            sheet.col(i).width = 6000
        if (i == 2 or i == 3):
            sheet.col(i).width = 3000
        if (i == 10):
            sheet.col(i).width = 65535
    for i in range(0, 14):
        sheet.write(0, i, col[i])
    for i in range(0, variables.pagenum*50):
        sheet.write(i + 1, 0, variables.list_a[i])
        sheet.write(i + 1, 1, variables.list_title[i])
        sheet.write(i + 1, 2, variables.list_time[i])
        sheet.write(i + 1, 3, variables.list_salary[i])
        sheet.write(i + 1, 4, variables.list_positon[i])
        sheet.write(i + 1, 5, variables.list_subsidy[i])
        sheet.write(i + 1, 6, variables.list_company_a[i])
        sheet.write(i + 1, 7, variables.list_company_name[i])
        sheet.write(i + 1, 8, variables.list_type_num[i])
        sheet.write(i + 1, 9, variables.list_company_project[i])
        sheet.write(i + 1, 10, variables.list_require[i])
        sheet.write(i + 1, 11, variables.list_address[i])
        sheet.write(i + 1, 12, variables.list_company_address[i])
        sheet.write(i + 1, 13, variables.list_company_web[i])
        print("正在写入第", i+1, "条信息")
    book.save(str(variables.keyword+'招聘信息.xls'))
    print("爬取完毕！")

def filter_tag(htmlstr):
    re_cdata = re.compile('<!DOCTYPE HTML PUBLIC[^>]*>', re.I)
    re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  #过滤脚本
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  #过滤style
    re_br = re.compile('<br\s*?/?>')
    re_h = re.compile('</?\w+[^>]*>')
    re_comment = re.compile('<!--[\s\S]*-->')
    s = re_cdata.sub('', htmlstr)
    s = re_script.sub('', s)
    s=re_style.sub('',s)
    s=re_br.sub('\n',s)
    s=re_h.sub(' ',s)
    s=re_comment.sub('',s)
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=re.sub('\s+',' ',s)
    s=replaceCharEntity(s)
    return s
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':'','160':'',
                    'lt':'<','60':'<',
                    'gt':'>','62':'>',
                    'amp':'&','38':'&',
                    'quot':'"''"','34':'"'}
    re_charEntity=re.compile(r'&#?(?P<name>\w+);') #命名组,把 匹配字段中\w+的部分命名为name,可以用group函数获取
    sz=re_charEntity.search(htmlstr)
    while sz:
        key=sz.group('name') #命名组的获取
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1) #1表示替换第一个匹配
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

if __name__ == "__main__":
    time_begin = time.time()
    main()
    print("总耗时：", time.time() - time_begin, "秒")
