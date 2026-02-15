import re
import pandas as pd

f = open("WhatsApp Chat with Papa Ji.txt", 'r', encoding='utf-8')
data = f.read()
print(data)
print(type(data))
pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
#messages = re.split(pattern, data)
#print(messages)
messages = re.split(pattern, data)[1:]
print(len(messages))
dates = re.findall(pattern, data)
print(dates[:5])
print(len(dates))
df = pd.DataFrame({'user_message': messages, 'message_date': dates})
#covert message_date type
df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M - ')
df.rename(columns={'message_date': 'date'}, inplace=True)
print(df.head())
print(df.head())
# Separate users and Messages
users = []
messages = []
for message in df['user_message']:
    entry = re.split('([\w\W]+?):\s', message)
    if entry[1:]: #user name
        users.append(entry[1])
        messages.append(entry[2])
    else:
        users.append('group_notification')
        messages.append(entry[0])

df['user'] = users
df['message'] = messages
df.drop(columns=['user_message'], inplace=True)
print(df.head())
df['year'] = df['date'].dt.year
print(df.head())
df['month'] = (df['date'].dt.month_name())
print(df['month'])
df['day'] = (df['date'].dt.day)
print(df['day'])
df['hour'] = df['date'].dt.hour
df['minute'] = df['date'].dt.minute
print(df.head())

print(df[df['user'] == 'Papa Ji'])
print(df[df['user'] == 'Papa Ji'].shape)

words = []
for message in df['message']:
    (words.extend((message)))
    print(len(words))

X = (df['user'].value_counts().head())
print(X)
import matplotlib.pyplot as plt
name = X.index
count = X.values
plt.bar(name, count)
plt.xticks(rotation = 'vertical')
plt.show()

temp = (df[df['user'] != 'group_notification'])
temp[temp['message'] != 'Media omitted\n']
f = open('stop_hinglish.txt', 'r')
stop_words = f.read()
print(stop_words)
words = []
for message in temp['message']:
    for word in message.lower().split():
        if word not in stop_words:
            words.append(word)
    words.extend(message.split())

from collections import Counter
pd.DataFrame(Counter(words).most_common(20))

