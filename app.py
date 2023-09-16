from requests_oauthlib import OAuth1Session
import openai
import os
from dotenv import load_dotenv
import requests
import re
import json
from collections import Counter
import schedule  
import time
import random
import streamlit as st
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

st.title("hosting to post on my twitter")
api_key = os.getenv('api_key')
api_key_secret = os.getenv('api_key_secret')
api_access_token = os.getenv('api_access_token')
api_access_token_secret = os.getenv('api_access_token_secret')
print("chla")


def get_tweet():
    
    message = [
    { "role":"system","content":f""" You are final year student at DTU college. You love to tweet daily on twitter.
                                Follow the steps below to create a tweet.
                                1. Create a generalised tweet about life, science, machine learning, day to day life of engineering student and other interesting topics as well.
                                2. word limit is maximum 250 characters.
                                3. Include relevant hashtags.
                                4. Be Creative.
                            
                                
                                
                                """},
    {"role": "user", "content": "post a tweet"},
    {"role": "assistant", "content": """  "Living the dream...of napping in a hammock, surrounded by fluffy clouds of serenity. 😴 Who needs stress when you can just float away into a tranquil haven? #HammockLife" #ZenZone """}
    
]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        temperature=0.8,
        messages=message,
        max_tokens= 50
        
    )
    return response['choices'][0]['message']['content']

last_tweets = []  # List to store the last 5 tweets
def analyze_tweet_history(tweets, new_tweet):
    # Create a GPT-3 prompt to check if the new tweet was made before
    prompt = f"Previous tweets:\n{tweets}\nNew tweet: {new_tweet}\nWas this tweet made before? return true or false"
    
    response = openai.Completion.create(
        model="text-davinci-003",  # Use a text-based model for analysis
        prompt=prompt,
        temperature=0.2,
        max_tokens=1
    )
    
    return response.choices[0].text.strip().lower() 



def get_unique_tweet(command):
    max_attempts = 5  # Maximum attempts to find a unique tweet
    attempts = 0

    while attempts < max_attempts:
        tweet = get_tweet()
        print(tweet)
        # Analyze if the new tweet has been posted before
        if not analyze_tweet_history("\n".join(last_tweets), tweet):
            if len(last_tweets) >= 5:
                last_tweets.pop(0)  # Remove the oldest tweet
            last_tweets.append(tweet)
            return tweet

        attempts += 1

    raise Exception("Unable to find a unique tweet after multiple attempts")


def post_tweet():
    url = "https://api.twitter.com/2/tweets"
    print("chalu ho rha h")
    twitter = OAuth1Session(api_key,
                            client_secret=api_key_secret,
                            resource_owner_key=api_access_token,
                            resource_owner_secret=api_access_token_secret)

    headers = {
        "Content-Type": "application/json",
    }
    command= "Generate a new tweet "
    
    tweet = get_unique_tweet(command)
    
    data = {
        "text": tweet,
    }

    response = twitter.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 201:
        raise Exception(f"Request returned an error: {response.status_code}, {response.text}")

    print("Tweet posted successfully!")

def schedule_tweet():
    # Determine how many tweets to schedule (between 3 and 4)
    num_tweets = random.randint(3, 4)
    
    # Generate random times for tweets
    for _ in range(num_tweets):
        # Calculate a random time between 9 AM (09:00) and 5 PM (17:00)
        random_hour = random.randint(9, 16)
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)
        scheduled_time = f"{random_hour:02d}:{random_minute:02d}:{random_second:02d}"
        
        # Schedule the tweet
        schedule.every().day.at(scheduled_time).do(post_tweet)
    

# Schedule the initial tweet scheduling
schedule_tweet()

# Run the scheduling loop
while True:
    try:
        print("checking for scheduled tweets...")
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        print("An error occurred:", e)
        # You can also add additional error handling here if needed


