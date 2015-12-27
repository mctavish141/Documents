import pymongo
from pymongo import MongoClient

client = MongoClient()

def doesCollectionExists (collectionName, db):
    collections = db.collection_names()
    return collectionName in collections

def createStartUsers ():
    db = client.NewsDB
    if not doesCollectionExists('users', db):
        user1 = {'name': 'Serhii',
                 'surname': 'Kopach',
                 'login': 'serega',
                 'password': '123',
                 'admin': 1}
        db.users.insert_one(user1)

def getCollections():
    db = client.NewsDB
    collections = db.getCollectionNames()
    return collections

def getAllUsers():
    db = client.NewsDB
    usersCollection = db.users
    cursor = usersCollection.find()
    users = []
    for user in cursor:
        users.append(user)
    return users

def getAllUsersRemoved():
    db = client.NewsDB
    cursor = db.usersRemoved.find().sort('datetime', pymongo.DESCENDING)
    users = []
    for user in cursor:
        users.append(user)
    return users

def getAllArticles():
    db = client.NewsDB
    articlesCollection = db.articles
    cursor = articlesCollection.find().sort('datetime', pymongo.DESCENDING)
    articles = []
    for article in cursor:
        articles.append(article)
    return articles

class ArticleInfo(object):
    title = ''
    description = ''
    author = ''
class CommentInfo(object):
    description = ''
    author = ''
class UserInfo(object):
    name = ''
    surname = ''
    login = ''
    password = ''
    admin = False
def fillUserInfo (user):
    userInfo = UserInfo()
    userInfo.name = user['name']
    userInfo.surname = user['surname']
    userInfo.login = user['login']
    userInfo.password = user['password']
    userInfo.admin = user['admin']
    return userInfo

def doesUserExist(login):
    db = client.NewsDB
    user = db.users.find_one({
        'login': login,
    })
    return user is not None

def addUser(userInfo):
    db = client.NewsDB
    user = {
        'login': userInfo.login,
        'password': userInfo.password,
        'name': userInfo.name,
        'surname': userInfo.surname,
        'admin': 0
    }
    db.users.insert_one(user)

def removeUser(userLogin):
    if doesUserExist(userLogin):
        db = client.NewsDB
        db.users.delete_one({
        'login': userLogin
        })
        db.usersRemoved.insert_one({
            'login': userLogin,
            'datetime': datetime.now()
        })

def findUserRemoved(userLogin):
    db = client.NewsDB
    user = db.usersRemoved.find_one({
        'login': userLogin
    })
    return user

def getUserWithLogin(login):
    db = client.NewsDB
    user = db.users.find_one({
        'login': login,
    })
    return user

def getUser(login, password):
    db = client.NewsDB
    user = db.users.find_one({
        'login': login,
        'password': password
    })
    #return user
    if user is None:
        return None
    else:
        return fillUserInfo(user)

def getUserCommentsCount(userLogin):
    db = client.NewsDB
    user = db.users.find_one({
        'login': userLogin,
    })
    if user is None:
        return 0

    articles = db.articles.find({
        'comments.author': userLogin
    })
    if articles is None:
        return 0

    commentsList = []
    for article in articles:
        if 'comments' in article:
            for comment in article['comments']:
                if comment['author'] == userLogin:
                    commentsList.append(comment)

    return len(commentsList)

def getUserArticlesCount(userLogin):
    db = client.NewsDB
    articles = db.articles.find({
        'author': userLogin
    })
    arts = list(articles)
    return len(arts)

def getUserLastArticle(userLogin):
    db = client.NewsDB
    articles = db.articles.find({
        'author': userLogin
    }).sort('datetime', pymongo.DESCENDING)
    if articles is not None:
        return articles[0]
    else:
        return None

def removeUserComments(userLogin):
    db = client.NewsDB
    if getUserWithLogin(userLogin) is None:
        if findUserRemoved(userLogin) is None:
            return

    articles = db.articles.find({
        'comments.author': userLogin
    })

    for article in articles:
        new_comments = list(article['comments'])
        for comment in article['comments']:
            if comment['author'] == userLogin:
                new_comments.remove(comment)

        db.articles.update_one(
            {'_id': article['_id']},
            {'$set': {'comments': new_comments}}
        )

from datetime import datetime
def addArticle(articleInfo):
    db = client.NewsDB
    articleID = db.seqs.find_and_modify(
        query={'collection': 'articles'},
        update={'$inc': {'id': 1}},
        fields={'id': 1, '_id': 0},
        new=True
    ).get('id')

    article = {
        '_id': str(int(articleID)),
        'title': articleInfo.title,
        'description': articleInfo.description,
        'author': articleInfo.author,
        'comments_seq': 0,
        'datetime': datetime.now(),
        'views': 0
    }

    db.articles.insert_one(article)

def editArticle(articleInfo, articleID):
    db = client.NewsDB
    db.articles.update_one(
        {'_id': articleID},
        {'$set': {
            'title': articleInfo.title,
            'description': articleInfo.description
            }
        }
    )

def getArticle(articleID):
    db = client.NewsDB
    article = db.articles.find_one({
        '_id': articleID
    })
    return article

def updateArticleCounter(articleID):
    db = client.NewsDB
    db.articles.update_one(
        {'_id': articleID},
        {
            '$inc': {
                'views': 1
            }
        }
    )

def removeArticle(articleID):
    db = client.NewsDB
    db.articles.delete_one({
        '_id': articleID
    })

def addComment(commentInfo, articleID):
    db = client.NewsDB
    article = getArticle(articleID)
    if article is None:
        pass
    else:
        comment = {
            'id': article['comments_seq'] + 1,
            'description': commentInfo.description,
            'author': commentInfo.author
        }
        comments = []
        if 'comments' in article:
            comments = article['comments']

        comments.append(comment)
        db.articles.update_one(
            {'_id': articleID},
            {
                '$set': {
                    'comments': comments
                },
                '$inc': {
                    'comments_seq': 1
                }
            }
        )

def removeComments(commentsList, articleID):
    db = client.NewsDB
    article = db.articles.find_one({
        '_id': articleID
    })
    if article is not None:
        new_comments = list(article['comments'])
        for commentID in commentsList:
            for comment in article['comments']:
                if comment['id'] == int(commentID):
                    new_comments.remove(comment)

        db.articles.update_one(
            {'_id': articleID},
            {'$set': {'comments': new_comments}}
        )

def getMinYear():
    db = client.NewsDB
    articlesCollection = db.articles
    cursor = articlesCollection.find().sort('datetime', pymongo.ASCENDING)
    if cursor.count() == 0:
        return datetime.now().year
    else:
        article = cursor[0]
        return article['datetime'].year

def searchArticles(date_from, date_to, title):
    datetime_from = datetime.min.replace(year=date_from.year,
                                         month=date_from.month,day=date_from.day)
    datetime_to = datetime.max.replace(year=date_to.year,
                                       month=date_to.month,day=date_to.day)

    db = client.NewsDB
    cursor = db.articles.find({
        'title': {'$regex': '.*{0}.*'.format(title), '$options': 'i'},
        'datetime': {
            '$gte': datetime_from,
            '$lte': datetime_to
        }
    }).sort('datetime', pymongo.DESCENDING)
    articles = []
    for article in cursor:
        articles.append(article)
    return articles

###################################
# Statistics

def getMostViewedArticles():
    db = client.NewsDB
    cursor = db.articles.find({
        'views': {'$gt': 0}
    }).sort('views', pymongo.DESCENDING)
    articles = []
    for article in cursor:
        articles.append(article)

    return articles[:10]

def compareCommentedArticlesDesc(a, b):
    return b['comments_count'] - a['comments_count']

def comparePublishedUsersDesc(a, b):
    return b['articles_count'] - a['articles_count']

def compareCommentedUsersDesc(a, b):
    return b['comments_count'] - a['comments_count']

def getMostCommentedArticles():
    db = client.NewsDB
    cursor = db.articles.find()
    articles = []
    for article in cursor:
        if 'comments' in article:
            article['comments_count'] = len(article['comments'])
            articles.append(article)

    articles.sort(compareCommentedArticlesDesc)

    return articles[:10]

def getMostPublishedUsers():
    db = client.NewsDB
    cursorUsers = db.users.find({
        'admin': 1
    })
    usersDict = {}
    for user in cursorUsers:
        usersDict[user['login']] = 0

    cursorArt = db.articles.find()
    for article in cursorArt:
        usersDict[article['author']] += 1

    cursorUsers = db.users.find({
        'admin': 1
    })
    users = []
    for user in cursorUsers:
        user['articles_count'] = usersDict[user['login']]
        if user['articles_count'] > 0:
            users.append(user)

    users.sort(comparePublishedUsersDesc)

    return users[:10]

def getMostCommentedUsers():
    db = client.NewsDB
    cursorUsers = db.users.find()
    usersDict = {}
    for user in cursorUsers:
        usersDict[user['login']] = 0

    cursorArt = db.articles.find()
    for article in cursorArt:
        if 'comments' in article:
            for comment in article['comments']:
                usersDict[comment['author']] += 1

    cursorUsers = db.users.find()
    users = []
    for user in cursorUsers:
        user['comments_count'] = usersDict[user['login']]
        if user['comments_count'] > 0:
            users.append(user)

    users.sort(compareCommentedUsersDesc)

    return users[:10]

###################################
# Backup

def copyDB(fromDB,toDB):
    if fromDB in client.database_names():
        client.drop_database(toDB)
        client.admin.command('copydb',
                         fromdb=fromDB,
                         todb=toDB)
        return True
    else:
        return False

def backupDB():
    return copyDB('NewsDB', 'NewsDB-2')

def restoreDB():
    return copyDB('NewsDB-2', 'NewsDB')

def backupToCustomDB(todb):
    return copyDB('NewsDB', todb)
def restoreFromCustomDB(fromdb):
    return copyDB(fromdb, 'NewsDB')

###################################
# Testing

def testing():
    time1 = datetime.now()
    for i in xrange(1, 50000):
        doub = 2 * i
    time2 = datetime.now()
    print time1
    print time2
    print (time2 - time1).microseconds
