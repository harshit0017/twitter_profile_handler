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
    {"role": "system", "content":"Your name is Harshit Singh. You are a final year undergrad student at delhi technological university. You come from technical background with major interest in machine learning" },
    {"role": "system", "content": "this is your twitter page where you post daily about facts and your day to day learning"},
    {"role": "user", "content": "post a tweet"},
    {"role": "assistant", "content": """"🌟 Living the dream...of napping in a hammock, surrounded by fluffy clouds of serenity. 😴💭 Who needs stress when you can just float away into a tranquil haven? #HammockLife #ZenZone"""}
    
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
    # Calculate two random times between 9 AM and 5 PM
    first_time_hour = random.randint(9, 16)
    first_time_minute = random.randint(0, 59)
    second_time_hour = random.randint(first_time_hour, 23)
    second_time_minute = random.randint(0, 59)
    schedule.every().day.at("23:10:00").do(post_tweet)
    # Schedule the function to run at the calculated random times
    schedule.every().day.at(f"{first_time_hour:02d}:{first_time_minute:02d}").do(post_tweet)
    schedule.every().day.at(f"{second_time_hour:02d}:{second_time_minute:02d}").do(post_tweet)
    schedule.every().day.at("10:10:00").do(post_tweet)
    st.write("tweet")
    # schedule.every().day.at("21:45:00").do(post_tweet)

# Schedule the initial tweet scheduling
schedule_tweet()

# Run the scheduling loop
# Run the scheduling loop
while True:
    try:
        print("checking for scheduled tweets...")
        # print("ye ho rha h kya ")
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        print("An error occurred:", e)
        # You can also add additional handling here if needed

