import os
import json
import requests
import webbrowser
from dotenv import load_dotenv

# Location of the local file to save Imgur tokens
IMGUR_TOKEN_FILE = "../imgur_tokens.json"
load_dotenv()

def get_tokens_from_file():
    if os.path.exists(IMGUR_TOKEN_FILE):
        with open(IMGUR_TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def save_tokens(tokens):
    with open(IMGUR_TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=4)

def authenticate():
    client_id = os.environ["IMGUR_CLIENT_ID"]
    client_secret = os.environ["IMGUR_CLIENT_SECRET"]

    # Construct Imgur PIN-based authorization URL
    auth_url = f"https://api.imgur.com/oauth2/authorize?client_id={client_id}&response_type=pin"

    # Open the authorization URL in the default web browser
    print("Opening browser for Imgur authorization...")
    webbrowser.open(auth_url)
    print("If the browser didn’t open, use this URL:")
    print(auth_url)

    # User must paste the PIN shown by Imgur
    pin = input("Enter the PIN from Imgur: ").strip()

    # Exchange the PIN for access + refresh tokens
    response = requests.post("https://api.imgur.com/oauth2/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "pin",
        "pin": pin
    })
    response.raise_for_status()

    tokens = response.json()
    save_tokens(tokens)
    return tokens

def refresh_token(tokens):
    client_id = os.environ["IMGUR_CLIENT_ID"]
    client_secret = os.environ["IMGUR_CLIENT_SECRET"]
    refresh_token = tokens["refresh_token"]

    response = requests.post("https://api.imgur.com/oauth2/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    })
    response.raise_for_status()

    new_tokens = response.json()
    save_tokens(new_tokens)
    return new_tokens

def get_valid_tokens():
    tokens = get_tokens_from_file()
    if tokens is None:
        tokens = authenticate()
    else:
        try:
            tokens = refresh_token(tokens)
        except Exception as e:
            print("Failed to refresh token:", e)
            print("Re-authenticating with PIN...")
            tokens = authenticate()
    return tokens

if __name__ == "__main__":
    tokens = get_valid_tokens()
    print("Access token:", tokens["access_token"])