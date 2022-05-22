# -*- coding: utf-8 -*-

import os
import time
import csv
import json
import requests
import pandas as pd
from tqdm import tqdm
from openpyxl  import load_workbook
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

option = webdriver.ChromeOptions()
option.add_argument('--disable-gpu')
option.add_argument("--disable-software-rasterizer")
option.add_experimental_option('useAutomationExtension', False)
option.add_experimental_option("excludeSwitches", ["enable-logging"])
option.add_experimental_option('excludeSwitches', ['enable-automation'])

local_version = 'v1.1.0'
url = "https://api.github.com/repos/DinforML/workingTools/releases/latest"
download_url = "https://github.com/DinforML/workingTools/releases/download/%s/default.zip"

def check_version():
	response = requests.get(url)
	online_version = response.json()['tag_name']

	if local_version == online_version:
		print(f"当前版本为最新版本[ {local_version} ] ！")
	else:
		name = 'WorkingTools ' + online_version.replace('/','_') + '.zip'
		with open(name,'wb') as f:
			print("当前版本已过期，下载新版本中...")
			response = requests.get(download_url % online_version, stream=True)
			total_length = response.headers.get('content-length')

			if total_length is None: # no content length header
				f.write(response.content)
			else:
				dl = 0
				total_length = int(total_length)
				for data in response.iter_content(chunk_size=4096):
					dl += len(data)
					f.write(data)
					done = int(50 * dl / total_length)
					sys.stdout.write("\r[%s%s]" % ('#' * done, ' ' * (50-done)) )	
					sys.stdout.flush()
			print("下载完毕。")
			input(f'请使用新版本 {name}\n点击Enter关闭视窗...')
			exit()


def clean():
	clear = lambda: os.system('cls')
	clear()

def login(driver):
	while True:
		account = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.ID, "login_username")))
		password = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.ID, "login_password")))
		code = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.ID, "login_code")))
		submit = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div/form/div[4]/div/div/span/button')))
		time.sleep(1)
		clean()
		acc = input("Account: ")
		account.clear()
		account.send_keys(acc)
		password.clear()
		pwd = getpass()
		password.send_keys(pwd)
		code.clear()
		v_code = input("Code: ")
		code.send_keys(v_code)
		submit.click()
		try:
			tex = WebDriverWait(driver, 1.5, 0.5).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[2]/div/span/div/div/div/span')))
			print(tex.text)
			account.clear()
			password.clear()
			code.clear()
		except:
			print("登入成功!")
			break
			
def Game_inquiry(driver):
	go_system = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/ul/li/a')))
	go_system.click()
	#report_page = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//span[text()="报表查询"]')))
	#report_page.click()
	game_list = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//a[text()="游戏注单查询"]')))
	game_list.click()

def sport_search(driver):
	df = pd.read_excel("account.xlsx")
	temp_list = []
	before_username = ""
	flow = ""
	user_count = df.last_valid_index() + 1
	for i in tqdm(range(user_count)):
		username = str(df.iat[i,0])
		username_input = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="create-form_username"]')))
		username_input.clear()
		username_input.send_keys(username)
		username_input.send_keys(Keys.ENTER)
		#searchButton = WebDriverWait(driver, 20, 0.5).until(EC.element_to_be_clickable((By.NAME, '查询')))
		#searchButton.click()
		before = flow
		while True:
			time.sleep(1)
			#bet_amount = WebDriverWait(driver, 15, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/section/section/div/main/div/div[1]/div[1]/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/table/tbody/tr/td[8]/p/text()[1]')))
			#bet_flow = WebDriverWait(driver, 15, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/section/section/div/main/div/div[1]/div[1]/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/table/tbody/tr/td[9]/p/text()[1]')))
			try:
				winlose = WebDriverWait(driver, 3, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/section/section/div/main/div/div[1]/div/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/table/tbody/tr/td[10]/p'))).text
				valid_flow = WebDriverWait(driver, 3, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/section/section/div/main/div/div[1]/div/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/table/tbody/tr/td[9]/p'))).text
				flow = valid_flow.split('\n')[1].replace(",","")
				winlose = winlose.split('\n')[0].replace(",","")
				lose = float(winlose) * -1
			except:
				flow = None
				lose = None
			if before_username != username:
				before_username == username
				break
		temp = {
			'会员账号':username,
			'体育流水': float(flow) if flow else "",
			'体育输赢': lose if lose else ""
			}
		temp_list.append(temp)
		time.sleep(0.5)
	end = pd.DataFrame(temp_list)
	end.to_csv("流水.csv",encoding="utf_8_sig")
	print("体育流水完成。")

def Nsport_search(driver):
	df = pd.read_csv("流水.csv")
	a = df.last_valid_index()
	temp_list = []
	before_username = ""
	flow = ""
	user_count = df.last_valid_index() + 1
	for i in tqdm(range(user_count)):
		username = str(df.iat[i,1])
		sport = float(df.iat[i,2]) if df.iat[i,2] != "" else ""
		sport_win = float(df.iat[i,3]) if df.iat[i,3] != "" else ""
		username_input = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="create-form_username"]')))
		username_input.clear()
		username_input.send_keys(username)
		username_input.send_keys(Keys.ENTER)
		#searchButton = WebDriverWait(driver, 20, 0.5).until(EC.element_to_be_clickable((By.NAME, '查询')))
		#searchButton.click()
		before = flow
		while True:
			time.sleep(1)
			#bet_amount = WebDriverWait(driver, 15, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/section/section/div/main/div/div[1]/div[1]/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/table/tbody/tr/td[8]/p/text()[1]')))
			#bet_flow = WebDriverWait(driver, 15, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/section/section/div/main/div/div[1]/div[1]/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/table/tbody/tr/td[9]/p/text()[1]')))
			try:
				winlose = WebDriverWait(driver, 3, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/section/section/div/main/div/div[1]/div/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/table/tbody/tr/td[10]/p'))).text
				valid_flow = WebDriverWait(driver, 3, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/section/section/div/main/div/div[1]/div/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/table/tbody/tr/td[9]/p'))).text
				flow = valid_flow.split('\n')[1].replace(",","")
				winlose = winlose.split('\n')[0].replace(",","")
				lose = float(winlose) * -1
			except:
				flow = None
				lose = None
			if before_username != username:
				before_username == username
				break
		temp = {
			'会员账号':username,
			'体育流水': sport,
			'体育输赢': sport_win,
			'娱乐流水': float(flow) if flow else "",
			'娱乐输赢': lose if lose else ""
			}
		temp_list.append(temp)
		time.sleep(0.5)
	end = pd.DataFrame(temp_list)
	end.to_csv("流水.csv",encoding="utf_8_sig")
	print("娱乐流水完成。")
	
def get_list(driver):
	print("start")
	r = 1
	templist = []
	page = 1
	page_str = (WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="root"]/div/section/section/div/main/div/div[1]/div[1]/div/div[3]/div/div/div[2]/div[1]/div/ul/li[1]')))).text
	total_page = (int(page_str.split(" ")[1]) // 500) + 1
	while True:
		try:
			username = driver.find_element(by=By.XPATH,value=f'//*[@id="root"]/div/section/section/div/main/div/div[1]/div[1]/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[2]/table/tbody/tr[{r}]/td[3]/div/p').text
			playground = driver.find_element(by=By.XPATH,value=f'//*[@id="root"]/div/section/section/div/main/div/div[1]/div[1]/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[2]/table/tbody/tr[{r}]/td[4]/div/p').text
			amount = driver.find_element(by=By.XPATH,value=f'//*[@id="root"]/div/section/section/div/main/div/div[1]/div[1]/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[2]/table/tbody/tr[{r}]/td[8]/div/p[1]/span').text
			two_amount = driver.find_element(by=By.XPATH,value=f'//*[@id="root"]/div/section/section/div/main/div/div[1]/div/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[2]/table/tbody/tr[{r}]/td[9]/p').text
			amount_list = (str(two_amount)).split("\n")
			bet_amount = amount_list[0]
			vali_amount = amount_list[1]
			parentName = driver.find_element(by=By.XPATH,value=f'//*[@id="root"]/div/section/section/div/main/div/div[1]/div[1]/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[2]/table/tbody/tr[{r}]/td[12]').text
			Table_dict={
				'会员账号':str(username),
				'游戏平台':str(playground),
				'下注金额':str(amount),
				'投注金额':str(bet_amount),
				'有效投注':str(vali_amount),
				'代理':str(parentName)
				}
			templist.append(Table_dict) 
			r+=1
		except NoSuchElementException: 
			print(f"完成 第{page}页")
			df = pd.DataFrame(templist)
			try:
				if page < total_page:
					next_page = driver.find_element(by=By.XPATH,value='//li[@title="下一页"]')
					driver.execute_script("arguments[0].click();", next_page)
					page += 1
					r = 1
					print("next")
					time.sleep(10)
				else:
					print(page)
					break
			except NoSuchElementException:
				print("break")
				break
	print("ok")
	df.to_csv("result2.csv",encoding="utf_8_sig")
	print("数据")
	
	
	
if __name__ == "__main__":
	check_version()
	while True:
		version = input("平台是(bb/ml)?: ")
		if version.lower() == 'bb':
			domain = "http://fundmng.aballbet.com/login"
			break
		if version.lower() == 'ml':
			domain = "http://fundmng.m6admin.com/login"
			break
	driver = webdriver.Chrome("chromedriver.exe",options=option)
	driver.get(domain)
	login(driver)
	Game_inquiry(driver)
	input("請先點進 篩選時間&體育場館 -> 篩選完後小黑窗按Enter #不需要點擊查詢")
	#get_list(driver)
	sport_search(driver)
	input("請篩選娱乐場館 -> 篩選完後小黑窗按Enter #不需要點擊查詢")
	Nsport_search(driver)
	input("流水已导出'流水.csv',可以关闭了")

