from django.shortcuts import render
import os
import tweepy
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

load_dotenv()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

df = pd.read_csv('models/hate_speech_model.csv')
x = df['text']
y = df['is_toxic']
vectorizer = CountVectorizer()
x = vectorizer.fit_transform(x)
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42)
model = LogisticRegression()
model.fit(x_train, y_train)


def toxicity_score(tweet_text):
    tweet_text = vectorizer.transform([tweet_text])
    return round((model.predict_proba(tweet_text)[0][1] * 100), 2)


def search_tweets(username, count):
    tweets = api.user_timeline(screen_name=username, count=count)

    tweet_list = []
    for tweet in tweets:
        tweet_dict = {}
        tweet_dict['user'] = tweet.user.screen_name
        tweet_dict['text'] = tweet.text
        tweet_dict['is_toxic'] = model.predict([vectorizer.transform([tweet.text])])[0]
        tweet_dict['toxicity_score'] = toxicity_score(tweet.text)
        tweet_list.append(tweet_dict)

    return tweet_list


def search(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        count = int(request.POST.get('count'))
        tweets = search_tweets(username, count)

        # Pie chart of toxicity distribution
        labels = ['Non-Toxic', 'Toxic']
        sizes = [sum(not tweet['is_toxic'] for tweet in tweets),
                 sum(tweet['is_toxic'] for tweet in tweets)]
        colors = ['#1E88E5', '#FF5252']
        explode = (0, 0.1)

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90)
        ax.axis('equal')
        chart1 = plt.savefig('static/chart1.png')

        # Bar chart of male/female interaction ratio
        genders = []
        for tweet in tweets:
            if tweet['user'].gender == 'male':
                genders.append('Male')
            elif tweet['user'].gender == 'female':
                genders.append('Female')
            else:
                genders.append('Unknown')
        df_genders = pd.DataFrame(genders, columns=['Gender'])
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.countplot(x='Gender', data=df_genders, ax=ax, palette='Blues')
        chart2 = plt.savefig('static/chart2.png')

        context = {
            'tweets': tweets,
            'chart1': chart1,
            'chart2': chart2
        }
        return render(request, 'results.html', context)

    return render(request, 'search.html')
