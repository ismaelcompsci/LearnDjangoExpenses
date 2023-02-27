from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control


# Create your views here.
@login_required(login_url="authentication/login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    return render(request, "expenses/index.html")


def add_expense(request):
    return render(request, "expenses/add_expense.html")
