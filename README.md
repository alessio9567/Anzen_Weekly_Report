Anzen Finance USDz Dashboard & Twitter Bot
This Python script fetches data from the Flipside API and posts weekly statistics about USDz stablecoin metrics to Twitter using the Tweepy library. The bot generates a Twitter thread with key information such as USDz supply, staking data, net minted amounts, staking rewards, and APY across multiple chains (Ethereum, Base, Blast, Arbitrum).

Features
Fetch USDz Supply Data: Queries weekly USDz minted/burned amounts across multiple chains (Ethereum, Base, Blast, Arbitrum) using the Flipside API.
Staking Data: Retrieves USDz staking volume, net staked amounts, and calculates APY from Flipside’s blockchain data.
Weekly Stats: Tracks weekly percentage changes for USDz supply, staking data, and chain dominance.
Automated Twitter Thread: Posts a multi-tweet thread to Twitter with the fetched data, highlighting USDz supply, staking changes, and more.
Prerequisites
Python 3.x: Ensure you have Python 3.x installed.
API Keys:
Twitter API Keys: Required to authenticate and post to Twitter via the Tweepy library.
Flipside API Key: Required to query blockchain data from the Flipside API.
Required Python Libraries:
Install the following Python packages by running:

bash
Copia codice
pip install tweepy pandas flipside
Configuration
Twitter API Keys: Store your Twitter API keys in a file called x_api_keys.txt in the format below:

makefile
Copia codice
CONSUMER_KEY="your_consumer_key"
CONSUMER_SECRET="your_consumer_secret"
ACCESS_TOKEN="your_access_token"
ACCESS_TOKEN_SECRET="your_access_token_secret"
Flipside API Key: Store your Flipside API key in a file called flipside_api.txt as a single line:

Copia codice
your_flipside_api_key
How It Works
1. Fetch Weekly USDz Data
Supply Data: The script uses an SQL query to retrieve weekly net minted USDz amounts and total supply for each chain (Ethereum, Base, Blast, Arbitrum).
Staking Data: It fetches weekly staking data, including total staked USDz, net staking amounts, and calculates the weekly and annualized APY based on rewards distributed.
2. Prepare Twitter Thread
The script formats the fetched data into readable and informative Twitter threads. The thread contains:

Total USDz supply and its distribution across chains.
Weekly supply change and net minted amounts per chain.
Total USDz staked and weekly staking percentage changes.
Staking rewards and APY.
3. Post to Twitter
Once the data is processed, the script uses the Tweepy library to automatically post the thread on Twitter.

Functions Breakdown
read_api_keys(file_path): Reads API keys from a specified file and returns them as a dictionary.
create_thread_content(): Generates the content for the Twitter thread by processing USDz supply and staking data.
post_thread(content_list): Posts a series of tweets (thread) on Twitter, starting with the first tweet and replying with subsequent ones.
beautify_number(num, is_percentage=False): Formats large numbers and percentages into more readable formats (e.g., 1.2M, 3.5%).
Queries
The script uses two main SQL queries against the Flipside API:

USDz Supply Query: Fetches USDz supply and net minted data across multiple chains.
Staking Query: Fetches USDz staking data, rewards, and calculates weekly and annual APY.
Both queries are defined as strings within the script and executed using the Flipside API client.

Usage
Configure API Keys: Add your Twitter and Flipside API keys to the respective files.

Run the Script:

bash
Copia codice
python script_name.py
The script will fetch the latest weekly USDz data and automatically post a Twitter thread.

Customization
Modify Queries: If you want to adjust the SQL queries for fetching different metrics, you can edit the sql_query and staking_query strings in the script.
Thread Formatting: You can adjust the format of the Twitter thread by editing the create_thread_content() function to add/remove specific metrics or change the text.
License
This project is open-source and available under the MIT License.
