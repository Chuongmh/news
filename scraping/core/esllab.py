from urlparse import urlparse, urljoin
from urllib import urlopen, urlretrieve
from bs4 import BeautifulSoup
import sys
import os
import time


url = "http://www.esl-lab.com/index.htm"

"""
easy = set(["A Day at School", 'Acting School and Movie Stars', 'Answering Machine', 'Apartments for Rent',
            'Bookstore Shopping', 'Camping Under the Stars', 'Christmas is Coming!', 'Class Reunion', 'Clothing Styles',
            'Business Communications', 'College Life', 'Daily Schedule', 'Dating Game', 'DVD Movie Rentals',
            'Eye Glasses for You', 'A Fun Day', 'Family Activities', 'Family Relationships', 'First Date',
            'Getting Around Tokyo', 'Good Old Blues', 'Happy Birthday!', 'Health Club', 'Heavenly Pies Restaurant',
            'Holiday Traditions', 'Homestay in the USA', 'Hotel Reservations', 'Immigration and Customs',
            'Lost in the Crowd', 'Meeting Singles', 'Nice to Meet You', 'Party Invitations', 'Party Time!',
            'Phone Message', 'Picnic Preparations', 'Private Language Tutor', 'Reading Time', 'Rental Shop (Version B)',
            "Saturday's Chores", 'Shopping for the Day', 'Sightseeing in Town', 'Snack Time', "So, what's the matter?",
            "Social Media Web Sites", 'Spending Money', 'Tell me about yourself', 'Train Tickets',
            'Travel Arrangements', 'Travel on Sky Airlines', 'What a Busy Day!', 'Where are you from?'])

easy = set(['A Student Credit Card', 'A Healthy Lifestyle', 'A Hiking Family', 'A Story to Remember', 'Airline Safety',
            'Back to School Supplies', 'Baking Cookies', 'Breakfast Recipes', 'Budget Hotel Rooms', 'Bus Trip',
            'Car Rental', 'Career Search', 'College Majors', 'College Roommates', 'College Textbooks', 'Computer Sales',
            'Cyberbullying', 'Dinner Time', "Driver's License", 'Emergency Call', 'Exercise Program',
            'English Language Center', 'Great Apartment Living', 'Grocery Shopping', "Haven't We Met Before?",
            'Japanese Public Bath', 'Just a Haircut, Please!', 'Leisure Activities', 'Marriage Preparation',
            'Martial Arts', 'Medical Advice', 'Moving Company', 'New York Travel', 'Our Family Roots', 'Parenting',
            'Personal Security', 'Pizza Delivery', 'Radio Advertising', 'Running Shoes', 'Show Times', 'Smart Phones',
            'Smoking: Kicking the Habit', 'Snacks and Candy', 'Snow Skiing', 'Street Market', 'Suicide Prevention',
            'Taxi Ride (Medium)', 'Texting and Driving', 'Traffic Ticket', 'TV Guide', 'Vacation Plans',
            'Weekly Activities', 'World Cup Soccer', 'World of Computers'])
"""
easy = set(['72-Hour Emergency Kit', 'A Free Cell Phone!', 'A Great Car Deal', 'A University Degree',
            'ABCs of Money Matters', 'Adsense: Making Money', 'Alcoholics Anonymous', 'Car Accident', 'Car Repairs',
            'Dating Violence', 'Dating Woes', 'Diet Plan', 'Divorce Lawyers', 'Driving Road Test', 'Drug Addiction',
            'Enjoying the Zoo', 'Easy Pet Care', 'Flower Shop', 'First Mountain Bank', 'Friday Night Mishaps',
            'Friendly Dental Care', 'Funerals: Expressing Condolences', 'Furniture Store Ad', 'Gardening Show',
            'Hamburger Restaurant', 'Home Repairs', 'Home Security', 'Honey. Are you listening?', 'Hotel Check-In',
            'Housing Complaints', 'Hunting Trip', "It's a Home Run!", 'Job Hunting', 'Job Interview',
            'Landscaping Secrets', 'Movie Review', 'Personal Problems', 'Professional Babysitting',
            'Rental Shop (Version A)', 'School Report', 'Security Systems', 'Store Returns', 'Summer Camp',
            'Taxi Ride (Difficult)', 'Telemarketing',  'The Ideal Woman', 'Towing Service', 'Trivia Game Show',
            'Utah Travel Ad', 'Video Game Systems', 'Wedding Anniversary', 'Wedding Plans',
            "Where's the movie theater?"])


nexturl = set([])
mp3links = set([])


def getLinks():
    try:
        html = urlopen(url)
    except:
        print("urlopen error: {0}".format(sys.exc_info()))

    try:
        bsObj = BeautifulSoup(html)
        links = bsObj.find_all("a")
        #print(len(links))
        for link in links:
            if link.string in easy:
                new_url = urljoin(url, link.attrs['href'])
                nexturl.add(new_url)
    except:
        print("Error: {0}".format(sys.exc_info()))


def getmp3(mp3url):
    try:
        html = urlopen(mp3url)
    except:
        print("MP3 urlopen error: {0}".format(sys.exc_info()))

    try:
        bsObj = BeautifulSoup(html)
        scripts = bsObj.find_all("script")
        for script in scripts:
            if script.string is not None:
                if script.string.find("jwplayer") != -1:
                    for line in script.string.splitlines():
                        if line.find("file:") != -1:
                            mp3links.add(urljoin(mp3url, line[7:len(line)-2]))
                            #print urljoin(mp3url, line[7:len(line)-2])
                            #urlretrieve(urljoin(mp3url, line[7:len(line)-2]), '/home/chuong/Downloads/mp3')
                            #print urljoin(mp3url, line[7:len(line)-2])
    except:
        print("MP3 Error: {0}".format(sys.exc_info()))


getLinks()
for n in nexturl:
    getmp3(n)
for m in mp3links:
    cmd = 'wget --directory-prefix=/home/chuong/Downloads/mp3/hard ' + m
    # print cmd
    os.system(cmd)
    time.sleep(1)