# -*- coding: utf-8 -*-

import os
import time
import csv
import json
import zipfile
import requests
import pandas as pd
from tqdm import tqdm
from openpyxl  import load_workbook
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


option = webdriver.ChromeOptions()
option.add_argument('--disable-gpu')
option.add_argument("--disable-software-rasterizer")
option.add_experimental_option('useAutomationExtension', False)
option.add_experimental_option("excludeSwitches", ["enable-logging"])
option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_experimental_option("prefs", {"credentials_enable_service": False,"profile.password_manager_enabled": False})
capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

local_version = 'v1.3.0'
url = "https://api.github.com/repos/DinforML/workingTools/releases/latest"
download_url = "https://github.com/DinforML/workingTools/releases/download/%s/default.zip"

def check_version():
	response = requests.get(url)
	online_version = response.json()['tag_name']

	if local_version == online_version:
		print(f"当前版本为最新版本[ {local_version} ] ！")
	else:
		name = 'WorkingTools ' + online_version.replace('/','_') + '.zip'
		print(f"当前版本[{local_version}]已过期，下载新版本[{online_version}]中...")
		response = requests.get(download_url % online_version, stream=True)
		total_size_in_bytes= int(response.headers.get('content-length', 0))
		block_size = 1024 #1 Kibibyte
		progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
		with open(name, 'wb') as file:
			for data in response.iter_content(block_size):
				progress_bar.update(len(data))
				file.write(data)
		progress_bar.close()
		if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
			print("下载失败，请重新尝试。")
		print("下载完毕。")
		if os.path.getsize(name) != 0:
			with zipfile.ZipFile(name,"r") as zip_ref:
				zip_ref.extractall()
			#os.rename('default',f'WorkingTools-{online_version}')
			os.remove(name)
		input(f'请使用新版本 {online_version}\npress ENTER to quit...')
		os.start('getFlow.exe')
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
			go_system = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/ul/li/a')))
			go_system.click()
			break

def timeStamp(timeNum):
	timeStamp = float(timeNum/1000)
	timeArray = time.localtime(timeStamp)
	timeStyle = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
	return timeStyle

def get_responce_Info():
	logs_raw = driver.get_log("performance")
	logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
	def log_filter(log_):
			return (log_["method"] == "Network.responseReceived" and "json" in log_["params"]["response"]["mimeType"])
	for log in filter(log_filter, logs):
		request_id = log["params"]["requestId"]
		resp_url = log["params"]["response"]["url"]
		if resp_url == "http://fundmng.m6admin.com/api/manage/data/user/detail/by/username":
			data = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})['body']
			data = json.loads(data)
			if data['message'].lower() == 'success':
				lastBetTime = str(timeStamp(data['data']['lastBettingTime'])) if data['data']['lastBettingTime'] else "无投注"
			else:
				return '账号错误' , '账号错误' , '账号错误'
		if resp_url == "http://fundmng.m6admin.com/api/manage/data/trend/userFund":
			data = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})['body']
			data = json.loads(data)
			if data['message'].lower() == 'success':
				rechargeTimes = str(data['data']['rechargeNum'])
				upAmountTimes = str(data['data']['upAmountTimes'])
			else:
				rechargeTimes = upAmountTimes = '-'
	return lastBetTime, rechargeTimes , upAmountTimes


def Game_inquiry(driver):
	game_list = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//a[text()="游戏注单查询"]')))
	game_list.click()

def sport_search(driver,temp_list):
	df = pd.read_excel("account.xlsx")
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
	end.to_csv("数据.csv",encoding="utf_8_sig")
	print("体育流水完成。")
	return temp_list

def Nsport_search(driver,temp_list,sportCheck):
	df = pd.read_excel("account.xlsx")
	a = df.last_valid_index()
	before_username = ""
	flow = ""
	user_count = df.last_valid_index() + 1
	for i in tqdm(range(user_count)):
		username = str(df.iat[i,0])
		#sport = float(df.iat[i,2]) if df.iat[i,2] != "" else ""
		#sport_win = float(df.iat[i,3]) if df.iat[i,3] != "" else ""
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
		if temp_list != []:
			if sportCheck:
				userList = []
				for UserDict in temp_list:
					if UserDict['会员账号'] == username:
						UserDict['娱乐流水'] = float(flow) if flow else ""
						UserDict['娱乐输赢'] = lose if lose else ""
			else:
				temp = {
					'会员账号':username,
					'娱乐流水': float(flow) if flow else "",
					'娱乐输赢': lose if lose else ""
					}
				temp_list.append(temp)
		else:
			temp = {
				'会员账号':username,
				'娱乐流水': float(flow) if flow else "",
				'娱乐输赢': lose if lose else ""
				}
			temp_list.append(temp)

		time.sleep(0.5)
	end = pd.DataFrame(temp_list)
	end.to_csv("数据.csv",encoding="utf_8_sig")
	print("娱乐流水完成。")
	return temp_list

def user_info_search(driver,temp_list,sportCheck,NsportCheck):
	df = pd.read_excel("account.xlsx")
	a = df.last_valid_index()
	before_username = ""
	flow = ""
	user_count = df.last_valid_index() + 1
	counting = 0
	error_acc = []
	for i in tqdm(range(user_count)):
		while True:
			try:
				username = str(df.iat[i,0])
				input_username = WebDriverWait(driver, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="root"]/div/section/section/header[2]/div/div[2]/span/span/span[1]/input')))
				input_username.clear()
				input_username.send_keys(username)
				input_username.send_keys(Keys.ENTER)
				time.sleep(0.5)
				lastBet , rechargeTimes , upAmountTimes = get_responce_Info()
				break
			except:
				driver.refresh()
		error_acc.append(username) if lastBet == '账号错误' else error_acc
		if temp_list != []:
			if sportCheck or NsportCheck:
				userList = []
				for UserDict in temp_list:
					if UserDict['会员账号'] == username:
						if lastBetTime:
							UserDict['最后投注时间'] = str(lastBet) if lastBet else '账号错误'
						if chargeTimes:
							UserDict['存款次数'] = str(rechargeTimes) if rechargeTimes else ''
							UserDict['代充次数'] = str(upAmountTimes) if upAmountTimes else ''
			else:
				temp = {
					'会员账号': username
					}
				if lastBetTime:
					temp['最后投注时间'] = str(lastBet) if lastBet else ""
				if chargeTimes:
					temp['存款次数'] = str(rechargeTimes) if rechargeTimes else ''
					temp['代充次数'] = str(upAmountTimes) if upAmountTimes else ''
				temp_list.append(temp)
		else:
			temp = {
				'会员账号': username
				}
			if lastBetTime:
				temp['最后投注时间'] = str(lastBet) if lastBet else ""
			if chargeTimes:
				temp['存款次数'] = str(rechargeTimes) if rechargeTimes else ''
				temp['代充次数'] = str(upAmountTimes) if upAmountTimes else ''
			temp_list.append(temp)

	end = pd.DataFrame(temp_list)
	end.to_csv("数据.csv",encoding="utf_8_sig")
	if error_acc:
		print('以下为 错误账号\n')
		for i in error_acc:
			print(i)
		print('-'*30)
	print("会员数据完成。")
	return temp_list
	
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
	

def checkTrueFalse(check):
	if check == 'y':
		return True
	elif check == 'n':
		return False
	
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
	driver = webdriver.Chrome(desired_capabilities=capabilities,executable_path="chromedriver.exe",options=option)
	driver.get(domain)
	login(driver)
	while True:
		while True:
			sportCheck = input('是否需要查询体育流水(y/n)?：').lower()
			if sportCheck in ['y','n']:
				sportCheck = checkTrueFalse(sportCheck)
				break
		while True:
			NsportCheck = input('是否需要查询娱乐流水(y/n)?：').lower()
			if NsportCheck in ['y','n']:
				NsportCheck = checkTrueFalse(NsportCheck)
				break
		while True:
			lastBetTime = input('是否需要查询最后投注时间(y/n)?：').lower()
			if lastBetTime in ['y','n']:
				lastBetTime = checkTrueFalse(lastBetTime)
				break
		while True:
			chargeTimes = input('是否需要查询(代)充值次数(y/n)?：').lower()
			if chargeTimes in ['y','n']:
				chargeTimes = checkTrueFalse(chargeTimes)
				break
		clean()
		print(f'True => 是 \nFalse => 否\n\n体育流水查询：{sportCheck}\n娱乐流水查询：{NsportCheck}\n最后投注时间查询：{lastBetTime}\n(代)充值次数查询：{chargeTimes}')
		doubleCheck = input('上述正确(y/n)?：').lower()
		if doubleCheck == 'y':
			break
		else:
			clean()
	temp_list = []
	if sportCheck:
		Game_inquiry(driver)
		input("請先篩選時間&體育場館 -> 篩選完後小黑窗按Enter #不需要點擊查詢")
		temp_list = sport_search(driver,temp_list)
	if NsportCheck:
		if sportCheck != True:
			Game_inquiry(driver)
		input("請先篩選娱乐場館 -> 篩選完後小黑窗按Enter #不需要點擊查詢")
		temp_list = Nsport_search(driver,temp_list,sportCheck)
	if lastBetTime or chargeTimes:
		temp_list = user_info_search(driver,temp_list,sportCheck,NsportCheck)
	input("数据已导出'数据.csv',可以关闭了")

