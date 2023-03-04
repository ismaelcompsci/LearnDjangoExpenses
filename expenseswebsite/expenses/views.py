import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages


from .models import Category, Expense


def search_expenses(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get("searchText")

        expenses = (
            Expense.objects.filter(
                amount__istartswith=search_str,
                owner=request.user,
            )
            | Expense.objects.filter(
                date__istartswith=search_str,
                owner=request.user,
            )
            | Expense.objects.filter(
                description__icontains=search_str,
                owner=request.user,
            )
            | Expense.objects.filter(
                category__icontains=search_str,
                owner=request.user,
            )
        )
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


# Create your views here.
@login_required(login_url="authentication/login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    expeneses = Expense.objects.filter(owner=request.user)

    context = {"expenses": expeneses}

    return render(request, "expenses/index.html", context)


def add_expense(request):
    categories = Category.objects.all()
    context = {"categories": categories, "values": request.POST}

    if request.method == "GET":
        return render(request, "expenses/add_expense.html", context=context)

    if request.method == "POST":
        amount = request.POST["amount"]
        description = request.POST["description"]
        category = request.POST["category"]
        date = request.POST["expense_date"]

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "expenses/add_expense.html", context=context)

        if not description:
            messages.error(request, "Description is required")
            return render(request, "expenses/add_expense.html", context=context)

        Expense.objects.create(
            amount=amount,
            date=date,
            category=category,
            description=description,
            owner=request.user,
        )
        messages.success(request, "Expense saved succesfully")

        return redirect("expenses")


def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()

    context = {"expense": expense, "values": expense, "categories": categories}

    if request.method == "GET":
        return render(request, "expenses/edit-expense.html", context)

    if request.method == "POST":
        amount = request.POST["amount"]
        description = request.POST["description"]
        category = request.POST["category"]
        date = request.POST["expense_date"]

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "expenses/edit-expense.html", context=context)

        if not description:
            messages.error(request, "Description is required")
            return render(request, "expenses/edit-expense.html", context=context)

        expense.owner = request.user
        expense.date = date
        expense.amount = amount
        expense.category = category
        expense.description = description

        expense.save()

        messages.success(request, "Expense Updated succesfully")

        return redirect("expenses")


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense removed")

    return redirect("expenses")
