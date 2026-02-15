import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns

rcParams['font.family'] = 'Segoe UI Emoji'

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    #st.text(data)
    df = preprocessor.preprocess(data)

    st.dataframe(df)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")
    selected_user = st.sidebar.selectbox("Show Analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        # Stats Analysiis

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Monthly Timeline
        st.title("Monthly TimeLine")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color = 'green')
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

        # Daily TimeLine
        st.title("Daily TimeLine")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color = 'orange')
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

        # activity map
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color = 'purple')
            #plt.xticks(rotation = 'vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)


        # Finding the busiest users in the group(Group Level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            
            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color = 'red')
                plt.xticks(rotation = 'vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("WordCloud")
        df_wc = helper.create_wordcloud(selected_user,df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # MOst Common Words
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df.iloc[:,0], most_common_df.iloc[:,1])
        plt.xticks(rotation = 'vertical')

        st.title('Most Common Words')
        st.pyplot(fig)
        #st.dataframe(most_common_df)

        # Emoji Analysis
        st.title("Emoji Analysis")

        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            if not emoji_df.empty:
                fig, ax = plt.subplots(figsize=(6,6))

                # Take only top 10 emojis for clean graph
                top_emoji = emoji_df.head(10)

                total = top_emoji['Count'].sum()
                percentages = (top_emoji['Count'] / total) * 100

                ax.barh(
                    top_emoji['Emoji'],
                    percentages,
                    color=plt.cm.tab20.colors
                )

                ax.set_xlabel("Percentage (%)")
                ax.set_title("Top Emojis Used")

                # Show percentage text beside bars
                for i, v in enumerate(percentages):
                    ax.text(v + 0.5, i, f"{v:.1f}%", va='center')

                st.pyplot(fig)




        st.title("Toxicity / Abusive Language Detection")

        total_messages, toxic_messages, non_toxic_messages, toxicity_percentage, toxic_users_df = helper.toxicity_analysis(selected_user, df)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Messages", total_messages)

        with col2:
            st.metric("Toxic Messages", toxic_messages)

        with col3:
            st.metric("Toxicity %", f"{toxicity_percentage}%")

        # Toxic vs Non Toxic Bar Graph
        fig1, ax1 = plt.subplots()
        ax1.bar(['Toxic', 'Non-Toxic'], [toxic_messages, non_toxic_messages], color=['red', 'green'])
        ax1.set_title("Toxic vs Non-Toxic Messages")
        st.pyplot(fig1)


        # Most Toxic Users Bar Graph
        if not toxic_users_df.empty:
            st.subheader("Most Toxic Users")
        
            fig2, ax2 = plt.subplots()
            ax2.barh(toxic_users_df['User'], toxic_users_df['Toxic Messages'], color='orange')
            ax2.set_xlabel("Number of Toxic Messages")
            ax2.set_title("User Toxicity Ranking")

            st.pyplot(fig2)

            st.dataframe(toxic_users_df)
        else:
            st.success("No abusive language detected ")






        # 🎉 FUN SECTION
        st.title("Fun Chat Insights")

        fun_data = helper.fun_section(selected_user, df)

        if fun_data:

            col1, col2 = st.columns(2)

            with col1:
                st.info(f"Most Active Day: {fun_data['most_active_day']}")
                st.info(f"Most Active Hour: {fun_data['most_active_hour']}:00")
                st.info(f"Most Emoji User: {fun_data['most_emoji_user']}")
                st.info(f"Fastest Replier: {fun_data['fastest_replier']} ({fun_data['avg_reply_time']} mins)")

            with col2:
                st.warning(f"Most Ignoring User: {fun_data['most_ignorer']}")
                st.success(f"Longest Message By: {fun_data['longest_message_user']}")
                st.write(fun_data['longest_message'][:200] + "...")
