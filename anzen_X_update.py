import tweepy
from flipside import Flipside
import pandas as pd

# Function to read API keys from the file
def read_api_keys(file_path):
    api_keys = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=')
                api_keys[key.strip()] = value.strip().replace('"', '')
    return api_keys

# Load Twitter API keys from file
twitter_api_keys = read_api_keys('x_api_keys.txt')

# Load Flipside API key
with open('flipside_api.txt', 'r') as file:
    api_key = file.readline().strip()  # Read the first line for Flipside API key

# Set up authentication using Tweepy (Twitter API v2)
client = tweepy.Client(
    consumer_key=twitter_api_keys.get('CONSUMER_KEY'),
    consumer_secret=twitter_api_keys.get('CONSUMER_SECRET'),
    access_token=twitter_api_keys.get('ACCESS_TOKEN'),
    access_token_secret=twitter_api_keys.get('ACCESS_TOKEN_SECRET'),
)

# Initialize Flipside API
flipside = Flipside(api_key, "https://api-v2.flipsidecrypto.xyz")

# SQL Query for weekly USDz supply
sql_query = """
select
  chain,
  date_trunc('week', day) as week, 
  sum(usdz_minted_amount) as weekly_net_usdz_minted_amount,
  sum(weekly_net_usdz_minted_amount) over (
    partition by chain
    order by
      week
  ) as usdz_supply
from
  (
    -- mint
    SELECT
      '@ethereum' as chain,
      date_trunc('day', block_timestamp) as day,
      SUM(amount) as usdz_minted_amount
    from
      ethereum.core.ez_token_transfers
    where
      contract_address = '0xa469b7ee9ee773642b3e93e842e5d9b5baa10067'
      and from_address = '0x0000000000000000000000000000000000000000'
    GROUP by
      day
    union
    all -- reedem
    SELECT
      '@ethereum' as chain,
      date_trunc('day', block_timestamp) as day,
      - SUM(amount) as usdz_burned_amount
    from
      ethereum.core.ez_token_transfers
    where
      contract_address = '0xa469b7ee9ee773642b3e93e842e5d9b5baa10067'
      and to_address = '0x0000000000000000000000000000000000000000'
    GROUP by
      day
    union
    all -- mint
    SELECT
      '@base' as chain,
      date_trunc('day', block_timestamp) as day,
      SUM(amount) as usdz_minted_amount
    from
      base.core.ez_token_transfers
    where
      contract_address = lower('0x04D5ddf5f3a8939889F11E97f8c4BB48317F1938')
      and from_address = '0x0000000000000000000000000000000000000000'
    GROUP by
      day
    union
    all -- reedem
    SELECT
      '@base' as chain,
      date_trunc('day', block_timestamp) as day,
      - SUM(amount) as usdz_burned_amount
    from
      base.core.ez_token_transfers
    where
      contract_address = lower('0x04D5ddf5f3a8939889F11E97f8c4BB48317F1938')
      and to_address = '0x0000000000000000000000000000000000000000'
    GROUP by
      day
    union
    all -- mint
    SELECT
      '@blast' as chain,
      date_trunc('day', block_timestamp) as day,
      SUM(amount) as usdz_minted_amount
    from
      blast.core.ez_token_transfers
    where
      contract_address = lower('0x52056ED29Fe015f4Ba2e3b079D10C0B87f46e8c6')
      and from_address = '0x0000000000000000000000000000000000000000'
    GROUP by
      day
    union
    all -- reedem
    SELECT
      '@blast' as chain,
      date_trunc('day', block_timestamp) as day,
      - SUM(amount) as usdz_burned_amount
    from
      blast.core.ez_token_transfers
    where
      contract_address = lower('0x52056ED29Fe015f4Ba2e3b079D10C0B87f46e8c6')
      and to_address = '0x0000000000000000000000000000000000000000'
    GROUP by
      day
    union
    all -- mint
    SELECT
      '@arbitrum' as chain,
      date_trunc('day', block_timestamp) as day,
      SUM(amount) as usdz_minted_amount
    from
      arbitrum.core.ez_token_transfers
    where
      contract_address = lower('0x5018609AB477cC502e170A5aCcf5312B86a4b94f')
      and from_address = '0x0000000000000000000000000000000000000000'
    GROUP by
      day
    union
    all -- reedem
    SELECT
      '@arbitrum' as chain,
      date_trunc('day', block_timestamp),
      - SUM(amount) as usdz_burned_amount
    from
      arbitrum.core.ez_token_transfers
    where
      contract_address = lower('0x5018609AB477cC502e170A5aCcf5312B86a4b94f')
      and to_address = '0x0000000000000000000000000000000000000000'
    GROUP by
      2
  )
GROUP by
  1,
  2 
order by week desc
"""

# Staking query to get weekly staked data
staking_query = """
WITH weekly_staking_data AS (
  -- Calculate the cumulative staked amount at the start of each 7-day reward period
  SELECT
    week,
    SUM(daily_net_volume_usdz_staked) AS weekly_net_volume_usdz_staked,
    SUM(SUM(daily_net_volume_usdz_staked)) OVER (ORDER BY week) AS cumulative_usdz_staked
  FROM (
    SELECT
      date_trunc('week', block_timestamp) AS week,
      SUM(amount) AS daily_net_volume_usdz_staked
    FROM
      ethereum.core.ez_token_transfers
    WHERE
      contract_address = '0xa469b7ee9ee773642b3e93e842e5d9b5baa10067'
      AND to_address = '0x547213367cfb08ab418e7b54d7883b2c2aa27fd7'
      AND symbol = 'USDz'
    GROUP BY
      1
    UNION ALL
    SELECT
      date_trunc('week', block_timestamp) AS week,
      -SUM(amount) AS daily_net_volume_usdz_unstaked
    FROM
      ethereum.core.ez_token_transfers
    WHERE
      contract_address = '0xa469b7ee9ee773642b3e93e842e5d9b5baa10067'
      AND from_address = '0x5d74abb95e85cba124fb27df08994ef072b5d49b'
      AND symbol = 'USDz'
    GROUP BY
      1
  ) AS staking_data
  GROUP BY
    week
),

weekly_rewards AS (
  -- Calculate total rewards given out every 7 days
  SELECT
    date_trunc('week', block_timestamp) AS week,
    SUM(amount) AS weekly_usdz_rewards
  FROM
    ethereum.core.ez_token_transfers
  WHERE
    contract_address = '0xa469b7ee9ee773642b3e93e842e5d9b5baa10067'
    AND to_address = '0x547213367cfb08ab418e7b54d7883b2c2aa27fd7'
    AND from_address = '0x663de54432a1d74912c99e7929d2d58a75452170'
    AND symbol = 'USDz'
  GROUP BY
    1
)

-- Calculate the weekly yield and annualized APY
SELECT
  wsd.week,
  wsd.weekly_net_volume_usdz_staked as weekly_net_usdz_staked,
  wsd.cumulative_usdz_staked,
  wr.weekly_usdz_rewards,
  (wr.weekly_usdz_rewards / wsd.cumulative_usdz_staked) AS weekly_yield,
  (POW(1 + (wr.weekly_usdz_rewards / wsd.cumulative_usdz_staked), 52) - 1)*100 AS annualized_apy
FROM
  weekly_staking_data wsd
LEFT JOIN
  weekly_rewards wr
ON
  wsd.week = wr.week
WHERE
  wsd.cumulative_usdz_staked > 0
ORDER BY
  wsd.week DESC;

"""

# Run the query against Flipside's query engine
staking_result_set = flipside.query(staking_query)
staking_data = staking_result_set.records

# Convert query result to pandas DataFrame
staking_df = pd.DataFrame(staking_data)

# Convert 'week' to datetime for calculations
staking_df['week'] = pd.to_datetime(staking_df['week'])

# Calculate percentage change in staked USDz weekly
staking_df = staking_df.sort_values(by=[  'week'], ascending=[ True])
staking_df['weekly_staked_change_pct'] = staking_df['cumulative_usdz_staked'].pct_change() * 100

# Run the query against Flipside's query engine for USDz supply
query_result_set = flipside.query(sql_query)
data = query_result_set.records

# Convert query result to pandas DataFrame
df = pd.DataFrame(data)

# Convert 'week' to datetime for calculations
df['week'] = pd.to_datetime(df['week'])

# Calculate percentage change in supply by chain 
df = df.sort_values(by=['chain', 'week'], ascending=[True, True])
df['supply_change_pct'] = df.groupby('chain')['usdz_supply'].pct_change() * 100

# Calculate total supply by week
total_supply = df.groupby('week')['usdz_supply'].sum()

# Calculate weekly net minted by chain
net_minted = df.groupby(['chain', 'week'])['weekly_net_usdz_minted_amount'].sum()
 
# Prepare data for the Twitter thread
def create_thread_content():
    
    # Total USDz Staked
    latest_staking_week = staking_df['week'].max()
    latest_staking_data = staking_df[staking_df['week'] == latest_staking_week]
    latest_week_data = staking_df[staking_df['week'] < latest_staking_week]
    
    total_usdz_staked = beautify_number(latest_staking_data['cumulative_usdz_staked'].values[0])
    weekly_net_usdz_staked = beautify_number(latest_staking_data['weekly_net_usdz_staked'].values[0])
    staking_change_pct = beautify_number(latest_staking_data['weekly_staked_change_pct'].values[0], is_percentage=True)

    staking_change_text = staking_change_pct

    # Total USDz Supply
    latest_week = df['week'].max()
    latest_data = df[df['week'] == latest_week] 
    last_week_data = df[df['week'] < latest_week] 

    # Weekly Rewards and APY
    latest_weekly_rewards = beautify_number(latest_week_data['weekly_usdz_rewards'].values[0])
    latest_apy = beautify_number(latest_week_data['annualized_apy'].values[0], is_percentage=True)

    total_supply_value = beautify_number(total_supply[latest_week])
    chain_dominance = "\n".join([f"{row['chain']}: {beautify_number((row['usdz_supply'] / total_supply[latest_week]) * 100, is_percentage=True)}" 
                                 for index, row in latest_data.iterrows()])
    
    # Weekly percentage change
    weekly_changes = "\n".join([f"{row['chain']}: {beautify_number(row['supply_change_pct'], is_percentage=True)}" 
                                for index, row in last_week_data.iterrows()])
    
    staking_weekly_changes = "\n".join([f"Week {row['week'].strftime('%Y-%m-%d')}: {beautify_number(row['weekly_staked_change_pct'], is_percentage=True)}" 
                                for index, row in latest_week_data.iterrows()])

    # Net minted with error handling
    net_minted_values = "\n".join([f"{chain}: {beautify_number(net_minted.get((chain, latest_week), 0))} USDz" 
                                   for chain in net_minted.index.levels[0]])
    


    # Prepare tweet content
    thread_content = [
        f"💼 @AnzenFinance Weekly Stats: #USDz Stablecoin \n\n"
        f"1️⃣ Total USDz Supply: {total_supply_value} USDz\n{chain_dominance} \n\n"
              f"https://flipsidecrypto.xyz/alessio9567/anzen-usdz-rwa-backed-stablecoin-YDPmpQ ",
        f"2️⃣ Weekly Supply Change by Chain:\n{weekly_changes}",
        f"3️⃣ Weekly Net #USDz Minted by Chain:\n{net_minted_values}",
        f"4️⃣ Total USDz Staked: {total_usdz_staked} #USDz\n",
        f"5️⃣ Net Weekly USDz Staked: {weekly_net_usdz_staked} #USDz\n\n"
              f"Weekly Change :\n{staking_weekly_changes}",
        f"6️⃣ Weekly Staking Rewards: {latest_weekly_rewards} #USDz ",
        f"7️⃣ Annualized APY: {latest_apy}%\n"
    ]

    return thread_content

# Post a Twitter thread
def post_thread(content_list):
    # Post the first tweet
    response = client.create_tweet(text=content_list[0])
    thread_id = response.data["id"]
    
    # Post the subsequent tweets in the thread
    for content in content_list[1:]:
        response = client.create_tweet(text=content, in_reply_to_tweet_id=thread_id)
        thread_id = response.data["id"]


# Beautify numbers and percentages for better readability in the thread
def beautify_number(num, is_percentage=False):
    if is_percentage:
        # Handle percentages with two decimal precision
        return f"{round(num, 2)}%" if num >= 0 else f"-{abs(round(num, 2))}%"
    else:
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}k"
        else:
            return str(num)


# Create the thread content
thread_content = create_thread_content()

# Post the thread on Twitter
post_thread(thread_content)
