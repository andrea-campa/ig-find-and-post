import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
from instabot import Bot
import urllib.request
import time
import confidential
from random import randrange

verbose=1

#driver= webdriver.Chrome("/home/campa/Documents/GitHub/instahashbot/chromedriver")
chrome_options = Options()
chrome_options.add_argument("--user-data-dir=chrome-data")
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome('./chromedriver',options=chrome_options)

def check_if_url_in_file(file_name, string_to_search):
    # Check if any line in the file contains given string
    with open(file_name, 'r') as read_obj:
        for line in read_obj:
            if string_to_search in line:
                read_obj.close()
                return True
    read_obj.close()
    return False

def top_post_hash(tag):

    urlhash = "https://www.instagram.com/explore/tags/" + tag + "/?__a=1"    
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'}
    max=0
    
    driver.get(urlhash)
    time.sleep(5)
    html = driver.find_elements_by_tag_name("pre")
    response=html[0].get_attribute('innerHTML')
    response=json.loads(response)
    data=response

    command = "mkdir /tmp/looter/" #make tmp dir
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print (proc_stdout)

    #print(data)
    #!!!!!!!!!!!   MAKE A CHECK IF SELENIUM ANSWERS 200
    #check if valid response
    # if (str(response)!="<Response [200]>"):
    #     print("Error, not a 200 response")
    #     quit()
    
    #print("Instagram responded with 200")

    #print(data["graphql"]["hashtag"]["edge_hashtag_to_top_posts"]["edges"]) #print top posts
    
    for i in data["graphql"]["hashtag"]["edge_hashtag_to_top_posts"]["edges"]: #perchè mettendo node qui nel for sbrocca? 
        
        link=i["node"]["display_url"].replace("amp;","")
        
        if (verbose): #verbose
            print("instagram.com/p/" + i["node"]["shortcode"])
            print(i["node"]["edge_liked_by"]["count"])
            print("\x1B[3m" + i["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"][:40].replace("\n"," ")+"..." + "\x1B[23m")
            print(link)
        
        if (i["node"]["edge_liked_by"]["count"]>max): #check if it has more likes

            if (check_if_url_in_file("download_log.txt",link)==False): #check if it has already been uploaded
                max=i["node"]["edge_liked_by"]["count"]
                code=i["node"]["shortcode"]
                userid=i["node"]["owner"]["id"]
                caption=i["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
                displayurl=link

            else:
                print("Most liked post was found in download_log.txt, skipping")
    
    print("Max number of likes: \"" + code + "\" has " + str(max))
    print(caption)

    #this gets the first tag in description
    #caption="empty" #to trigger the if
    if (caption.find("@")==-1):
        print("Using account name as username")
        #get username from userid
        #urluserid from https://commentpicker.com/instagram-username.php
        urluserid="https://www.instagram.com/graphql/query/?query_hash=c9100bf9110dd6361671f113dd02e7d6&variables={%22user_id%22:%22" + str(userid) + "%22,%22include_chaining%22:false,%22include_reel%22:true,%22include_suggested_users%22:false,%22include_logged_out_extras%22:false,%22include_highlight_reels%22:false,%22include_related_profiles%22:false}"
        driver.get(urluserid)
        time.sleep(3)
        html = driver.find_elements_by_tag_name("pre")
        response=html[0].get_attribute('innerHTML')
        response=json.loads(response)
        userdata=response
        postname=userdata["data"]["user"]["reel"]["user"]["username"]
        print(postname)

    else: 
        print("Using first @ found")
        caption=caption[caption.find("@") + len("@"):]
        postname=caption.replace("\n"," ").split(" ")[0]
        print("username="+postname)

    urllib.request.urlretrieve(displayurl, '/tmp/looter/toupload.jpg')

    #exit()
    bot = Bot()
    bot.login (username = confidential.username, password = confidential.password)

    #before using this you need to edit the module to delete that stupid ds_user
    
    print("Uploading")
    caption = "Shot by @" + postname + "\n" + confidential.desc
    #print(caption)
    bot.upload_photo("/tmp/looter/toupload.jpg", caption)
    print("Uploaded")

    file_obj=open("download_log.txt","a")
    file_obj.write(displayurl+"\n")
    file_obj.close()

    driver.quit()
    command = "rm /tmp/looter/*.REMOVE_ME; rm -r ./config/"
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print (proc_stdout)

choice=randrange(len(confidential.hashtags))
print("Using " + str(choice) + ": " + confidential.hashtags[choice])
top_post_hash(confidential.hashtags[choice])
