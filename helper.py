from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import emoji
from better_profanity import profanity

extract = URLExtract()


# Fteching STATS
def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]

    words = []
    for message in df['message']:
        words.extend(message.split())

    num_media_messages = df[df['message'].str.contains('Media omitted', na=False)].shape[0]

    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


# BUSY USERS
def most_busy_users(df):
    x = df['user'].value_counts().head()

    new_df = (
        round((df['user'].value_counts() / df.shape[0]) * 100, 2)
        .reset_index()
        .rename(columns={'index': 'name', 'user': 'percent'})
    )

    return x, new_df


# WORDCLOUD
def create_wordcloud(selected_user, df):

    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read().splitlines()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>']

    def remove_stop_words(message):
        return " ".join(
            word for word in message.lower().split()
            if word not in stop_words
        )

    df['message'] = df['message'].apply(remove_stop_words)

    wc = WordCloud(
        width=500,
        height=500,
        min_font_size=10,
        background_color='black'
    )

    return wc.generate(df['message'].str.cat(sep=" "))


# MOST COMMON WORDS
def most_common_words(selected_user, df):

    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read().splitlines()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>']

    words = []

    for message in df['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    return pd.DataFrame(
        Counter(words).most_common(20),
        columns=['Word', 'Count']
    )

# Emoji Analyze
def emoji_helper(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []

    for message in df['message']:
        for char in message:
            if emoji.is_emoji(char):
                emojis.append(char)

    emoji_df = pd.DataFrame(
        Counter(emojis).most_common(),
        columns=['Emoji', 'Count']
    )

    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_name', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)

    return user_heatmap


from better_profanity import profanity
import pandas as pd

def toxicity_analysis(selected_user, df):
    profanity.load_censor_words()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    total_messages = df.shape[0]

    toxic_messages = 0
    toxic_users = {}

    for index, row in df.iterrows():
        message = row['message']
        user = row['user']

        if profanity.contains_profanity(message):
            toxic_messages += 1

            toxic_users[user] = toxic_users.get(user, 0) + 1

    non_toxic_messages = total_messages - toxic_messages

    toxicity_percentage = 0
    if total_messages > 0:
        toxicity_percentage = round((toxic_messages / total_messages) * 100, 2)

    toxic_users_df = (
        pd.DataFrame(toxic_users.items(), columns=['User', 'Toxic Messages'])
        .sort_values(by='Toxic Messages', ascending=False)
    )

    return (
        total_messages,
        toxic_messages,
        non_toxic_messages,
        toxicity_percentage,
        toxic_users_df
    )

















def fun_section(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return None

    df = df.sort_values('date').copy()

    results = {}

    # Most Active Day
    results["most_active_day"] = df['date'].dt.day_name().value_counts().idxmax()

    # Most Active Hour
    results["most_active_hour"] = df['hour'].value_counts().idxmax()

    # Longest Message
    df["msg_length"] = df["message"].apply(len)
    longest_row = df.loc[df["msg_length"].idxmax()]

    results["longest_message_user"] = longest_row["user"]
    
    clean_message = longest_row["message"]
    if len(clean_message) > 200:
        clean_message = clean_message[:200] + "..."
    results["longest_message"] = clean_message


    # Most Emoji Useers
    emoji_count = {}

    for _, row in df.iterrows():
        user = row["user"]
        message = row["message"]

        count = sum(1 for char in message if emoji.is_emoji(char))

        if count > 0:
            emoji_count[user] = emoji_count.get(user, 0) + count

    if emoji_count:
        results["most_emoji_user"] = max(emoji_count, key=emoji_count.get)
    else:
        results["most_emoji_user"] = "No emojis used"

    #  Reply Time And Ignore Logic
    reply_times = {}
    ignore_counts = {}

    prev_user = None
    prev_time = None

    for _, row in df.iterrows():
        curr_user = row["user"]
        curr_time = row["date"]

        if prev_user:

            if curr_user != prev_user:
                diff = (curr_time - prev_time).total_seconds()

                reply_times.setdefault(curr_user, []).append(diff)
            else:
                ignore_counts[prev_user] = ignore_counts.get(prev_user, 0) + 1

        prev_user = curr_user
        prev_time = curr_time

    # Average reply time
    avg_reply = {}

    for user, times in reply_times.items():
        avg_reply[user] = sum(times) / len(times)

    if avg_reply:
        fastest_user = min(avg_reply, key=avg_reply.get)
        results["fastest_replier"] = fastest_user
        results["avg_reply_time"] = round(avg_reply[fastest_user] / 60, 2)
    else:
        results["fastest_replier"] = "N/A"
        results["avg_reply_time"] = 0

    # Most ignoring user
    if ignore_counts:
        results["most_ignorer"] = max(ignore_counts, key=ignore_counts.get)
    else:
        results["most_ignorer"] = "N/A"

    return results