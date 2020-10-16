from django.shortcuts import render
from .models import *
from .forms import *
import  numpy as np
rep = 'home.html'
# Create your views here.
def home(request):
    if request.POST:
        test1 = {"A": 1, "B": 2, "D": request.POST['inp']}
    else:
        test1 = {"A": 1, "B": 2}

    # return render(request, rep, {"test": test1})
    return render(request, rep, test1)


def get_value(request):
    s = request.POST
    # with open("r.txt", "a+") as f:
    #     f.write("123")
    print(s)
    return render(request, rep)


def file(request):
    print(request.POST)

    form = upf(request.POST, request.FILES)
    if form.is_valid():
        f = document(file= request.FILES['filex'])
        f.save()

    if request.POST:
        print("files")
        img = request.FILES['filex']
        with open("abc.txt", "wb+") as f:
            f.write(np.array(img))
        print(img)
    return render(request, "file.html")
