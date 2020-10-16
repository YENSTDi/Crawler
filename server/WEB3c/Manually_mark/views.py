from django.shortcuts import render
from pymongo import MongoClient
import pandas as pd


def load_data(max_d=50):
    print("DB GET data")
    client = MongoClient()
    db = client.crawler
    coll = db.main3c
    data = coll.find({}).limit(max_d)
    df = pd.DataFrame(list(data))
    df['r_name'] = df['name'].apply(lambda x: [g for g in x.replace("*", "-").replace(" ", "-").split("-") if g != ""])
    dt = df.to_dict("row")
    return dt


# Create your views here.
def index(request):
    if request.POST:
        print(request.POST)

    data = load_data()

    return render(request, 'load_data.html', {"data": data})



