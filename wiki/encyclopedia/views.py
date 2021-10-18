import random
from typing import ValuesView
from django import forms
from . import util
import markdown2
from django.shortcuts import render

class NewPageForm(forms.Form):
    Title = forms.CharField(label="Title")
    Text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 5}))


class EditPageForm(forms.Form):
    Title = forms.CharField(
        label="Title", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    Text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 5}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def page(requests, title):
    text = util.get_entry(title)
    if text is not None:
        md = markdown2.Markdown()
        result = md.convert(text)
        return render(requests, "encyclopedia/page.html", {
            "content": result,
            "title": title
        })
    else:
        return render(requests, "encyclopedia/page.html", {
            "content": "<h2> Page not found </h2>"
        })


def search(requests):
    enc_list = []
    if requests.method == "POST":
        form = requests.POST
    wiki_list = util.list_entries()
    wiki_list_lower = []
    for wiki in wiki_list:
        wiki_list_lower.append(wiki.lower())
    if form['q'].lower() in wiki_list_lower:
        return page(requests, form['q'])
    elif wiki in wiki_list:
        for wiki in wiki_list:
            wiki_lower = wiki.lower()
            if wiki_lower.find(form['q'].lower()) != -1:
                enc_list.append(wiki)
        return render(requests, "encyclopedia/search.html", {
            "contents": enc_list
        })

    else:
        return render(requests, "encyclopedia/search.html")


def create_page(requests):
    entries_list = util.list_entries()
    if requests.method == "POST":
        form = NewPageForm(requests.POST)
        if form.is_valid():
            Title = form.cleaned_data["Title"]
            Text = form.cleaned_data["Text"]
            if Title not in entries_list:
                util.save_entry(Title, f"#{Title} \n {Text}")
                return page(requests, Title)
            else:
                form.add_error(
                    'Title', 'Error. An article with the same name already exists!')
                return render(requests, "encyclopedia/create_new.html", {
                    "form": form
                })
    return render(requests, "encyclopedia/create_new.html", {
        "form": NewPageForm()
    })


def edit(requests):
    return render(requests, "encyclopedia/edit.html", {
        "form":  EditPageForm()
    })


def random_page(requests):
    return page(requests, random.choice(util.list_entries()))
