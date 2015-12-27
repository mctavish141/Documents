# Create your views here.

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
import db
from db import ArticleInfo,UserInfo,CommentInfo

def index(request):
    #return HttpResponse("<h1>News Application! :)</h1>")
    return HttpResponseRedirect('/home')

#def users(request):
#    usersList = db.getAllUsers()
#    return render(request, 'users.html', {'users': usersList})

def makeUsersCommentsCounts(usersList):
    for user in usersList:
        user['commentsCount'] = db.getUserCommentsCount(user['login'])

def users(request):
    if userSession.flag == True:
        if userSession.user.admin == True:
            usersList = db.getAllUsers()
            makeUsersCommentsCounts(usersList)
            return render(request, 'users.html', {'users': usersList})

    return HttpResponseRedirect('/')

def usersRemoved(request):
    if userSession.flag == True:
        if userSession.user.admin == True:
            usersList = db.getAllUsersRemoved()
            return render(request, 'usersRemoved.html', {'users': usersList})

    return HttpResponseRedirect('/')

def showUser(request, userLogin):
    if userSession.flag == False:
        return HttpResponseRedirect('/')

    user = db.getUserWithLogin(userLogin)
    if user is None:
        user = db.findUserRemoved(userLogin)
        if user is not None:
            #return HttpResponse("<h1>This account has been removed.</h1>")
            return render(request, 'user.html', {'user': None, 'userRemoved': user, 'user_whose_session': userSession.user})
        else:
            return HttpResponseRedirect('/')

    user['commentsCount'] = db.getUserCommentsCount(user['login'])
    if user['admin']:
        user['articlesCount'] = db.getUserArticlesCount(user['login'])
        lastArticle = db.getUserLastArticle(user['login'])
        if lastArticle is not None:
            lastArticle['link'] = getArticleLink(lastArticle)
        user['lastArticle'] = lastArticle

    return render(request, 'user.html', {'user': user, 'user_whose_session': userSession.user})

def removeUser(request, userLogin):
    #######################################
    if userLogin == 'serega':
        return HttpResponseRedirect('/')
    #######################################

    if userSession.flag == True:
        if (userSession.user.admin == True) or (userSession.user.login == userLogin):
            db.removeUser(userLogin)

    #if userSession.flag == True:
    #    if userSession.user.admin == True:
    #        db.removeUser(userLogin)

    return HttpResponseRedirect('/')

def removeUserComments(request, userLogin):
    if userSession.flag == False:
        return HttpResponseRedirect('/')
    if userSession.user.admin == False:
        return HttpResponseRedirect('/')

    db.removeUserComments(userLogin)
    return HttpResponseRedirect('/users/{0}/'.format(userLogin))

from forms import AddArticleForm,LoginForm,AddCommentForm,RegisterForm,ManageCommentsForm,SearchArticlesForm

class UserSession (object):
    flag = False
    user = None

userSession = UserSession()

def addArticle(request):
    if request.method == 'POST':
        form = AddArticleForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']

            articleInfo = ArticleInfo()
            articleInfo.title = title
            articleInfo.description = description
            articleInfo.author = userSession.user.login

            db.addArticle(articleInfo)
            return HttpResponseRedirect('/')
    else:
        form = AddArticleForm()

    if userSession.flag == True:
        if userSession.user.admin == True:
            return render(request, 'addArticle.html', {'form': form})

    return HttpResponseRedirect('/')

def editArticle(request, articleID):
    if userSession.flag == False:
        return HttpResponseRedirect('/')
    if userSession.user.admin == False:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = AddArticleForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']

            articleInfo = ArticleInfo()
            articleInfo.title = title
            articleInfo.description = description

            db.editArticle(articleInfo, articleID)
            return HttpResponseRedirect(getArticleLinkID(articleID))
    else:
        #form = AddArticleForm()
        article = db.getArticle(articleID)
        if article is None:
            return HttpResponseRedirect('/')
        else:
            form = AddArticleForm(initial={'title': article['title'], 'description': article['description']})

    return render(request, 'editArticle.html', {'form': form, 'articleID': articleID})

def getArticleLink(article):
    return '/articles/{0}/'.format(article['_id'])
def getArticleLinkID(articleID):
    return '/articles/{0}/'.format(articleID)

def showArticle (request, articleID):
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']

            commentInfo = CommentInfo()
            commentInfo.description = description
            commentInfo.author = userSession.user.login

            db.addComment(commentInfo, articleID)
            return HttpResponseRedirect(request.path)
            #return HttpResponseRedirect('/')
    else:
        form = AddCommentForm()
        db.updateArticleCounter(articleID)

    article = db.getArticle(articleID)
    if article is None:
        return HttpResponseRedirect('/')
    else:
        #article['link'] = getArticleLink(article)
        article['ID'] = articleID
        return render(request, 'article.html', {'article': article, 'form': form, 'user': userSession.user})

def removeArticle(request, articleID):
    if userSession.flag == True:
        if userSession.user.admin == True:
            db.removeArticle(articleID)

    return HttpResponseRedirect('/')

def manageComments(request, articleID):
    if userSession.flag == False:
        return HttpResponseRedirect('/')
    if userSession.user.admin == False:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = ManageCommentsForm(request.POST)
        if form.is_valid():
            commentsToDelete = request.POST.getlist('comments_list')
            str = db.removeComments(commentsToDelete, articleID)

            return HttpResponseRedirect(getArticleLinkID(articleID))
    else:
        article = db.getArticle(articleID)
        if article is None:
            return HttpResponseRedirect('/')
        else:
            if 'comments' in article:
                form = ManageCommentsForm(comments=article['comments'])
            else:
                return HttpResponseRedirect('/')

    return render(request, 'manageComments.html', {'form': form, 'articleID': articleID})

def makeArticlesLinks(articlesList):
    for article in articlesList:
        article['link'] = '/articles/{0}/'.format(article['_id'])

def makeArticlesTimes(articlesList):
    for article in articlesList:
        if 'datetime' in article:
            article['time24'] = str(article['datetime'].time())[:5]

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']

            if db.doesUserExist(login):
                return render(request, 'register.html', {'form': form, 'login_exists': True})
            else:
                userInfo = UserInfo()
                userInfo.login = login
                userInfo.password = password
                userInfo.name = name
                userInfo.surname = surname
                db.addUser(userInfo)
                userSession.flag = True
                userSession.user = db.getUser(login,password)
                return HttpResponseRedirect('/')
    else:
        form = RegisterForm()

    if userSession.flag == True:
        return HttpResponseRedirect('/')
    else:
        return render(request, 'register.html', {'form': form})

def searchArticles(request):
    if request.method == 'POST':
        form = SearchArticlesForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            title = form.cleaned_data['title']

            articlesList = db.searchArticles(date_from,date_to,title)
            makeArticlesLinks(articlesList)
            makeArticlesTimes(articlesList)
            return render(request, 'searchArticles.html', {'form': form, 'articles': articlesList})
    else:
        form = SearchArticlesForm()

    return render(request, 'searchArticles.html', {'form': form})

def home(request):
    if request.method == 'POST':
        # if logoff posted
        if 'submitButton1' in request.POST:
            #currentUser = None
            userSession.flag = False
            userSession.user = None
            return HttpResponseRedirect('/home/')

        # if login posted
        if 'submitButton2' in request.POST:
            form = LoginForm(request.POST)
            if form.is_valid():
                login = form.cleaned_data['login']
                password = form.cleaned_data['password']

                #currentUser = db.getUser(login,password)
                user = db.getUser(login,password)
                if user is not None:
                    userSession.flag = True
                    userSession.user = user
                    return HttpResponseRedirect('/home/')
                else:
                    articlesList = db.getAllArticles()
                    makeArticlesLinks(articlesList)
                    makeArticlesTimes(articlesList)
                    return render(request, 'home.html', {'no_login_password': True, 'user': None, 'guest': True,
                                                         'form': form, 'articles': articlesList})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    articlesList = db.getAllArticles()
    makeArticlesLinks(articlesList)
    makeArticlesTimes(articlesList)
    if userSession.flag is True:
        text = "You are logged in as " + userSession.user.login + '.'
        return render(request, 'home.html', {'user': userSession.user, 'form': form, 'text': text, 'articles': articlesList})
    else:
        return render(request, 'home.html', {'user': None, 'guest': True, 'form': form, 'articles': articlesList})

    #articlesList = db.getAllArticles()
    #return render(request, 'home.html', {'articles': articlesList})

def statistics(request):
    if userSession.flag == False:
        return HttpResponseRedirect('/')
    if userSession.user.admin == False:
        return HttpResponseRedirect('/')

    #ARTICLES
    #The most viewed
    articles_viewed = db.getMostViewedArticles()
    makeArticlesLinks(articles_viewed)

    #The most commented
    articles_commented = db.getMostCommentedArticles()
    makeArticlesLinks(articles_commented)

    #USERS
    #The most published
    users_published = db.getMostPublishedUsers()

    #The most commented
    users_commented = db.getMostCommentedUsers()

    return render(request, 'statistics.html', {'articles_viewed': articles_viewed, 'articles_commented': articles_commented,
                                               'users_published': users_published, 'users_commented': users_commented})

def backupDatabase(request):
    if userSession.flag == False:
        return HttpResponseRedirect('/')
    if userSession.user.admin == False:
        return HttpResponseRedirect('/')

    db.backupDB()
    #return render(request, 'copyDatabase.html', {'backup': True})
    return HttpResponseRedirect('/')

def restoreDatabase(request):
    if userSession.flag == False:
        return HttpResponseRedirect('/')
    if userSession.user.admin == False:
        return HttpResponseRedirect('/')

    status = db.restoreDB()
    #return render(request, 'copyDatabase.html', {'backup': False, 'status': status})
    return HttpResponseRedirect('/')

def createTestArticle():
    articleInfo = ArticleInfo()
    articleInfo.title = 'Test Article Title'
    articleInfo.description = 'Test Article Description'
    articleInfo.author = 'serega'
    db.addArticle(articleInfo)
    return db.getUserLastArticle('serega')

from datetime import datetime
def testing(request):
    #if userSession.flag == False:
    #    return HttpResponseRedirect('/')
    #if userSession.user.admin == False:
    #    return HttpResponseRedirect('/')

    range1 = 10000  #articles - insert
    range2 = 100  #comments
    range3 = 10000  #articles - get

    dict = {}
    dict['range1'] = range1
    dict['range2'] = range2
    dict['range3'] = range3

    test_backup_db = 'test_backup'
    db.backupToCustomDB(test_backup_db)

    ############# 1

    time1 = datetime.now()
    for i in xrange(0, range1):
        articleInfo = ArticleInfo()
        articleInfo.title = 'Test Article {0} Title'.format(i)
        articleInfo.description = 'Test Article {0} Description'.format(i)
        articleInfo.author = 'serega'
        db.addArticle(articleInfo)
    time2 = datetime.now()
    dict['timeDelta1'] = time2 - time1

    try:
        milliseconds = float((time2 - time1).seconds) * 1000 + float((time2 - time1).microseconds) / 1000
        dict['speed1'] = int((float(dict['range1'] / milliseconds) * 1000))
    except ZeroDivisionError:
        #dict['speed1'] = 'Too small amount of data.'
        dict['speed1'] = 0

    ############# 2

    article = createTestArticle()
    time1 = datetime.now()
    for i in xrange(0, range2):
        commentInfo = CommentInfo()
        commentInfo.description = 'Test Comment {0} Description'.format(i)
        commentInfo.author = 'serega'
        db.addComment(commentInfo, article['_id'])
    time2 = datetime.now()
    dict['timeDelta2'] = time2 - time1
    db.removeArticle(article['_id'])

    try:
        milliseconds = float((time2 - time1).seconds) * 1000 + float((time2 - time1).microseconds) / 1000
        dict['speed2'] = int((float(dict['range2'] / milliseconds) * 1000))
    except ZeroDivisionError:
        dict['speed2'] = 0

    ############# 3

    article = createTestArticle()
    articleID = article['_id']
    time1 = datetime.now()
    for i in xrange(0, range3):
        db.getArticle(articleID)
    time2 = datetime.now()
    dict['timeDelta3'] = time2 - time1
    db.removeArticle(article['_id'])

    try:
        milliseconds = float((time2 - time1).seconds) * 1000 + float((time2 - time1).microseconds) / 1000
        dict['speed3'] = int((float(dict['range3'] / milliseconds) * 1000))
    except ZeroDivisionError:
        dict['speed3'] = 0

    ####################################################

    db.restoreFromCustomDB(test_backup_db)

    return render(request, 'testing.html', {'dict': dict})
