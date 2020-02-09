import requests
from django.shortcuts import render, redirect
from .models import City
from .forms import CityForm


def index(request):
    """main page view for showing the list of added cities and their weather,
       cities can be deleted using delete view"""

    url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=c21fd6a23974cd59957ab440e5174fc5"

    # empty messages for manipulation, see below
    message = ""
    err_msg = ""
    message_class = ""

    if request.method == "POST":
        """all the activity with post requests for adding cities to the list"""
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data["name"]
            count_city = City.objects.filter(name=new_city).count()
            if count_city == 0:
                r = requests.get(url.format(new_city)).json()  # api-call
                if r["cod"] == 200:
                    form.save()
                else:
                    err_msg = "The city does not exist"
            else:
                err_msg = "The city already exists in database"

        # message manipulation + css classes
        if err_msg:
            message = err_msg
            message_class = "is-danger"
        else:
            message = "City added sucessfully!"
            message_class = "is-success"

    form = CityForm()

    cities = City.objects.all()  # main query

    weather_cities_list = []  # a list from the query

    for city in cities:
        r = requests.get(url.format(city)).json()

        city_weather = {
            "city": city.name,
            "temperature": int(r["main"]["temp"]),
            "description": r["weather"][0]["description"],
            "icon": r["weather"][0]["icon"],
        }
        weather_cities_list.append(city_weather)

    context = {
        "weather_cities_list": weather_cities_list,
        "form": form,
        "message": message,
        "message_class": message_class,
    }

    return render(request, "weather.html", context)


def delete_city(request, city_name):
    City.objects.filter(name=city_name).delete()

    return redirect("home")
