# Anzen Finance USDz Dashboard & Twitter Bot

This Python script fetches data from the Flipside API and posts weekly statistics about USDz stablecoin metrics to Twitter using the Tweepy library. The bot generates a Twitter thread with key information such as USDz supply, staking data, net minted amounts, staking rewards, and APY across multiple chains (Ethereum, Base, Blast, Arbitrum).

## Features

- **Fetch USDz Supply Data**: Queries weekly USDz minted/burned amounts across multiple chains (Ethereum, Base, Blast, Arbitrum) using the Flipside API.
- **Staking Data**: Retrieves USDz staking volume, net staked amounts, and calculates APY from Flipside’s blockchain data.
- **Weekly Stats**: Tracks weekly percentage changes for USDz supply, staking data, and chain dominance.
- **Automated Twitter Thread**: Posts a multi-tweet thread to Twitter with the fetched data, highlighting USDz supply, staking changes, and more.

## Prerequisites

1. **Python 3.x**: Ensure you have Python 3.x installed.
2. **API Keys**:
   - **Twitter API Keys**: Required to authenticate and post to Twitter via the Tweepy library.
   - **Flipside API Key**: Required to query blockchain data from the Flipside API.

### Required Python Libraries:

Install the following Python packages by running:

```bash
pip install tweepy pandas flipside
