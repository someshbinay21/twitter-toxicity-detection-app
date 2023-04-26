# Project: Hate Speech Detector
# Author: Somesh Binay
# Date: 18/12/2022

import os
import pickle
import tkinter as tk
from tkinter import ttk
import tweepy
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from dotenv import load_dotenv

# load the environment variables
load_dotenv()

# --------------APIs & auth--------------- # DO NOT UNCOMMENT THIS SECTION
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret =os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
# --------------APIs & auth END--------------- # DO NOT UNCOMMENT THIS SECTION

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# load the data into a pandas dataframe
df = pd.read_csv('models/hate_speech_model.csv')

# split the data into feature and target variables
x = df['text']
y = df['is_toxic']

# convert the text data into numerical vectors using a CountVectorizer
vectorizer = CountVectorizer()
x = vectorizer.fit_transform(x)

# split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42)

# train a logistic regression model on the training data
model = LogisticRegression()
model.fit(x_train, y_train)

# use the model to make predictions on the test data
predictions = model.predict(x_test)

# calculate the accuracy of the model by comparing the predicted labels to the true labels
accuracy = sum(predictions == y_test) / len(y_test)
print("Model Accuracy(from models/hate_speech_model.csv):", accuracy * 100, "%\n")

# function to search for tweets
def search_tweets():
    # get the username from the entry widget
    username = username_entry.get()

    # get the number of tweets to retrieve
    count = int(count_entry.get())

    # retrieve the tweets using the API object
    tweets = api.user_timeline(screen_name=username, count=count)

    # clear any existing tweet widgets
    for widget in tweet_frame.winfo_children():
        widget.destroy()

    # create a canvas widget to hold the tweet frame and scrollbar
    canvas = tk.Canvas(tweet_frame)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(
        tweet_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.config(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda event: canvas.configure(
        scrollregion=canvas.bbox("all")))
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(
        int(-1 * (event.delta / 120)), "units"))

    # create a frame inside the canvas to hold the tweets
    canvas_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=canvas_frame, anchor="nw")
    canvas_frame.columnconfigure(0, weight=1)

    # create a widget for each tweet
    for tweet in tweets:
        tweet_widget = ttk.Frame(canvas_frame, padding=10, relief="groove")
        tweet_widget.grid(sticky="ew", pady=10)
        tweet_widget.columnconfigure(1, weight=1)
        user_label = ttk.Label(
            tweet_widget, text=f"{tweet.user.name} (@{tweet.user.screen_name})")
        user_label.grid(row=0, column=0, sticky="w")
        text_label = ttk.Label(tweet_widget, text=tweet.text,
                               wraplength=400, justify="left")
        text_label.grid(row=1, column=0, columnspan=2, sticky="w")
        created_label = ttk.Label(
            tweet_widget, text=tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        created_label.grid(row=2, column=0, sticky="w")
        favorite_label = ttk.Label(
            tweet_widget, text=f"❤ {tweet.favorite_count}")
        favorite_label.grid(row=2, column=1, sticky="e")
        retweet_label = ttk.Label(
            tweet_widget, text=f"♺ {tweet.retweet_count}")
        retweet_label.grid(row=2, column=1, sticky="w")

        # check if the tweet is toxic
        tweet_text = tweet.text
        tweet_text = vectorizer.transform([tweet_text])
        prediction = model.predict(tweet_text)

        percentage = round((model.predict_proba(tweet_text)[0][1] * 100), 2)

        if percentage >= 65.00:
            print("Toxic Tweet")
            text_label.config(foreground="red")
            percentage_label = ttk.Label(
                tweet_widget, text=f"{percentage}% Toxic", foreground="red", font="bold")
            percentage_label.grid(row=3, column=0, sticky="w")
        else:
            print("Non-Toxic Tweet")
            text_label.config(foreground="green")
            percentage_label = ttk.Label(
                tweet_widget, text=f"{percentage}% Toxic", foreground="green", font="bold")
            percentage_label.grid(row=3, column=0, sticky="w")

    # save the model
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)

    # update the canvas to reflect the changes
    canvas_frame.update_idletasks()
    canvas.config(scrollregion=canvas_frame.bbox("all"))

root = tk.Tk()
root.geometry("490x700")
root.title("Hate Speech Detection - By Somesh Binay")

search_frame = ttk.Frame(root, padding=10)
search_frame.pack(fill="x")
search_frame.columnconfigure(0, weight=1)
username_label = ttk.Label(search_frame, text="Username:")
username_label.grid(row=0, column=0, sticky="w")
username_entry = ttk.Entry(search_frame)
username_entry.grid(row=0, column=1, sticky="ew")
username_entry.focus()
count_label = ttk.Label(search_frame, text="Count:")
count_label.grid(row=0, column=2, sticky="w")
count_entry = ttk.Entry(search_frame, width=5)
count_entry.grid(row=0, column=3, sticky="w")
count_entry.insert(0, "10")
search_button = ttk.Button(search_frame, text="Search", command=search_tweets)
search_button.grid(row=0, column=4, sticky="e")

tweet_frame = ttk.Frame(root, padding=10)
tweet_frame.pack(fill="both", expand=True)

root.mainloop()
