import streamlit as st
import os
import instaloader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Function to log in to Instagram using Selenium
def instagram_login(username, password):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Uncomment this to run in headless mode
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)

    # Locate and input username and password
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    
    username_input.send_keys(username)
    password_input.send_keys(password)
    
    # Submit login form
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)  # Adjust sleep time as needed
    
    return driver

# Function to get posts, followers, and following using Instaloader
def get_instagram_data(username, password, folder_name):
    # Log in to Instagram with Selenium
    driver = instagram_login(username, password)

    # Set up Instaloader
    L = instaloader.Instaloader(dirname_pattern=folder_name + "/{target}")
    L.login(username, password)

    # Fetch profile data
    profile = instaloader.Profile.from_username(L.context, username)

    # Create directory if not exists
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Get posts data
    posts_data = []
    for post in profile.get_posts():
        post_data = {
            'caption': post.caption,
            'likes': post.likes,
            'comments': post.comments,
            'date': post.date,
            'url': post.url,
            'video': post.is_video
        }
        posts_data.append(post_data)
        # Download post image/video
        L.download_post(post, target=username)
    
    # Get followers
    followers = [follower.username for follower in profile.get_followers()]
    
    # Get following
    following = [followee.username for followee in profile.get_followees()]

    # Save posts data, followers, and following into text files
    with open(os.path.join(folder_name, 'posts_data.txt'), 'w') as file:
        for i, post in enumerate(posts_data, 1):
            file.write(f"Post {i}\n")
            for key, value in post.items():
                file.write(f"{key.capitalize()}: {value}\n")
            file.write("\n")

    with open(os.path.join(folder_name, 'followers.txt'), 'w') as file:
        for follower in followers:
            file.write(f"{follower}\n")

    with open(os.path.join(folder_name, 'following.txt'), 'w') as file:
        for followee in following:
            file.write(f"{followee}\n")

    driver.quit()

    return {
        "posts_data": len(posts_data),
        "followers": len(followers),
        "following": len(following)
    }

# Streamlit App
def main():
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            margin-top: 2rem;
            font-size: 4rem;
        }
        .subtitle {
            text-align: center;
            font-size: 2rem;
            margin-top: 0.5rem;
        }
        </style>
        <h1 class="title">Snap Crawler</h1>
        <h2 class="subtitle">Instagram</h2>
        """,
        unsafe_allow_html=True
    )
    
    # Get user input
    username = st.text_input("Instagram Username")
    password = st.text_input("Instagram Password", type="password")
    folder_name = st.text_input("Folder Name to Save Data", value="instagram_data")
    
    if st.button("Start Extraction"):
        if username and password:
            with st.spinner("Extracting data..."):
                result = get_instagram_data(username, password, folder_name)
                st.success("Data Extraction Completed")
                
                st.write(f"Data saved in folder: `{folder_name}`")
                st.write(f"Number of posts downloaded: {result['posts_data']}")
                st.write(f"Number of followers: {result['followers']}")
                st.write(f"Number of following: {result['following']}")
        else:
            st.error("Please enter both username and password.")

if __name__ == "__main__":
    main()
