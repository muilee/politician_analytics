from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from pymongo import MongoClient
import json
from django.contrib.auth.models import User

politicin_dict = {"136845026417486": "柯文哲", "46251501064": "蔡英文", "360151611020961": "李錫錕", 
                  "449664581882455": "黃國昌", "261813197541354": "侯友宜",
                  "191690867518507": "江啟臣", "122936517768637": "陳其邁", "333058400178329": "鄭文燦",
                  "152472278103133": "賴清德", "852926604746233": "洪慈庸",
                  "10150145806225128": "朱立倫", "365320250345879": "林昶佐", "805460986214082": "蔣萬安",
                  "1380211668909443": "姚文智", "184799244894343": "蔡正元"}


class MongoConnection(object):
	client = None

	@staticmethod
	def getConnection():
		if MongoConnection.client is None:
			MongoConnection.client = MongoClient("mongodb://10.120.37.108:27017")
			return MongoConnection.client
		else:
			return MongoConnection.client


def index(request):
	return render(request, "politician/index.html", locals())

@login_required(login_url="/accounts/login/")
def politician(request, id):
	id = str(id)
	politician_image = "images/" + id
	politician_name = politicin_dict.get(id)

	start = datetime.strptime("2017-10-01", "%Y-%m-%d")
	end = datetime.strptime("2018-01-01", "%Y-%m-%d")


	if request.GET:
		start = datetime.strptime(request.GET["start"], "%Y-%m-%d")
		end = datetime.strptime(request.GET["end"], "%Y-%m-%d")

	client = MongoConnection.getConnection()
	db = client["project"]
	comment_collection = db["comments"]

	hot = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end} })

	negative_comments_number = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score_NN": {"$lt": -0.2}})
	central_comments_number = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score_NN": {"$lte": 0.1, "$gte": -0.2}})
	positive_comments_number = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score_NN": {"$gt": 0.1}})

	negative_woman_percent = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score_NN": {"$lt": -0.2}, "gender": 1}) / comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score_NN": {"$lt": -0.2}, "gender": {"$nin": [None]}})
	negative_man_percent = 1 - negative_woman_percent
	central_woman_percent = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score_NN": {"$lte": 0.1, "$gte": -0.2}, "gender": 1}) / comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score_NN": {"$lte": 0.1, "$gte": -0.2}, "gender": {"$nin": [None]}})
	central_man_percent = 1 - central_woman_percent
	positive_woman_percent = comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score_NN": {"$gt": 0.1}, "gender": 1}) / comment_collection.count({"politician_id": id, "created_time": {"$gte": start, "$lte": end}, "score_NN": {"$gt": 0.1}, "gender": {"$nin": [None]}})
	positive_man_percent = 1 - positive_woman_percent

	negative_woman = str(round(negative_woman_percent * 100, 1)) + "%"
	negative_man = str(round(negative_man_percent * 100, 1)) + "%"
	central_woman = str(round(central_woman_percent * 100, 1)) + "%"
	central_man = str(round(central_man_percent * 100, 1)) + "%"
	positive_woman = str(round(positive_woman_percent * 100, 1)) + "%"
	positive_man = str(round(positive_man_percent * 100, 1)) + "%"


	keyword_collection = db["keywords"]
	keywords = keyword_collection.find({"politician_id": id, "created_time": {"$gte": start, "$lte": end}}, {"_id": 0}).sort([("tfidf", -1)]).limit(100)

	map_reduce_collection = db["mapReduce"]
	data = list(map_reduce_collection.find({"politician_id": id, "created_time": {"$gte": start, "$lte": end}}, {"_id": 0, "politician_id":0}).sort([("created_time", 1)]))
	for x in data:
		x['created_time'] = x['created_time'].strftime("%Y-%m-%d")
	data = json.dumps(data)
	politition_list = [(id, name) for id, name in politicin_dict.items()]


	return render(request, "politician/chart.html", locals())

def model_prediction(request, id):
	id = str(id)


def user_register(request):
	if request.method == 'POST' and request.POST:
		username = request.POST["username"]
		password = request.POST["password"]
		user = User.objects.create_user(username=username,password=password)
		return redirect("/politician")

	else:
		return render(request, "account/register.html", locals())


def user_login(request):
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		
		if user is not None:
			login(request, user)
			return redirect("/politician")
	else:
		return render(request, "account/login.html", locals())

@login_required(login_url="/accounts/login/")
def user_logout(request):
	logout(request)
	return redirect("/politician")