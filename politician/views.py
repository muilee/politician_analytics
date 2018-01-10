from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from datetime import datetime
from pymongo import MongoClient

politicin_dict = {"136845026417486": "柯文哲", "46251501064": "蔡英文", "360151611020961": "李錫錕", 
                  "449664581882455": "黃國昌", "261813197541354": "侯友宜", "109391162488374": "盧秀燕",
                  "191690867518507": "江啟臣", "122936517768637": "陳其邁", "333058400178329": "鄭文燦",
                  "118250504903757": "馬英九", "152472278103133": "賴清德", "852926604746233": "洪慈庸",
                  "10150145806225128": "朱立倫", "365320250345879": "林昶佐", "232716627404": "陳菊",
                  "600540963315152": "丁守中", "153819538009272": "林佳龍", "805460986214082": "蔣萬安",
                  "1380211668909443": "姚文智", "184799244894343": "蔡正元"}

class MongoConnection(object):
	client = None

	@staticmethod
	def getConnection():
		if MongoConnection.client is None:
			MongoConnection.client = MongoClient("mongodb://127.0.0.1:27017")
			return MongoConnection.client
		else:
			return MongoConnection.client


# @login_required(login_url="login/")
def index(request):
	return render(request, "politician/index.html", locals())

# @login_required(login_url="login/")
def politician(request, id):
	id = str(id)
	politician_image = "images/" + id
	politician_name = politicin_dict.get(id)

	start = datetime.strptime("2017-10-01", "%Y-%m-%d")
	end = datetime.strptime("2018-01-01", "%Y-%m-%d")


	if request.POST:
		start = datetime.strptime(request.POST["start"], "%Y-%m-%d")
		end = datetime.strptime(request.POST["end"], "%Y-%m-%d")

	client = MongoConnection.getConnection()
	db = client["project"]
	comment_collection = db["comments"]

	hot = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end} })

	negative_comments_number = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score": {"$lt": 0}})
	central_comments_number = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score": {"$lte": 0.1, "$gte": 0}})
	positive_comments_number = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score": {"$gt": 0.1}})

	negative_woman_percent = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score": {"$lt": 0}, "gender": 1}) / comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score": {"$lt": 0}, "gender": {"$nin": [None]}})
	negative_man_percent = 1 - negative_woman_percent
	central_woman_percent = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score": {"$lte": 0.1, "$gte": 0}, "gender": 1}) / comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score": {"$lte": 0.1, "$gte": 0}, "gender": {"$nin": [None]}})
	central_man_percent = 1 - central_woman_percent
	positive_woman_percent = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score": {"$gt": 0.1}, "gender": 1}) / comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score": {"$gt": 0.1}, "gender": {"$nin": [None]}})
	positive_man_percent = 1 - positive_woman_percent


	keyword_collection = db["keywords"]

	keywords = keyword_collection.find({"politician_id": id, "created_time": {"$gte": start, "$lte": end}}, {"_id": 0}).sort([("tfidf", -1)]).limit(10)



	return render(request, "politician/chart.html", locals())

def model_prediction(request, id):
	id = str(id)





# def login(request):
# 	if request.POST:
# 		username = ""
# 		username = request.POST.get("username")
# 		password = request.POST.get("password")
# 		user = authenticate(username=username, password=password)
		
# 		if user is not None and user.is_active:
# 			login(request, user)
# 			return redirect("/politician/")
# 	else:
# 		return render(reauest, "account/login.html", {})

# def logout(request):
# 	logout(request)
# 	return render(request, "account/login.html", {})