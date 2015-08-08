import abc
import csv
import os
import argparse
import json
import gtk
import urllib2
import urllib
from random import randint
import requests
import sys
from time import sleep
from datetime import datetime
from PIL import Image
import cStringIO

# https://gist.github.com/rtt/10403467
# urllib.urlretrieve(urlloc, fileloc)

class Message():
    def __init__(self, data_dict):
            self.d = data_dict
        
    def get_to(self):
        return self.d['to']
    
    def get_from(self):
        return self.d['from']
    
    def get_match_id(self):
        return self.d['match_id']
    
    def get_message(self):
        return self.d['message']
            
    def get_message_time(self):
        return datetime.strptime(self.d['sent_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            
# base class which is returned when requesting a new user
class UserBase(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        return
    
    @abc.abstractmethod
    def get_user_name(self):
        return
    
    @abc.abstractmethod
    def get_name(self):
        return
    
    @abc.abstractmethod
    def get_age(self):
        return
    
    @abc.abstractmethod
    def get_images(self):
        return
    
    @abc.abstractmethod
    def get_profile(self):
        return
    
    @abc.abstractmethod
    def get_messages(self):
        return
    
    @abc.abstractmethod
    def save_data(self, directory):
        return
    
    @abc.abstractmethod
    def get_image_names(self):
        return
    
# user class used by the Tinder Data Wrapper
class TinderUser(UserBase):
    def __init__(self, data_dict, messages=[]):
        self.d = data_dict
        self.messages = messages

    def get_user_name(self):
        return self.d['_id']
    
    def get_match_id(self):
        return self.d['match_id']
    
    def get_name(self):
        return self.d['name']
    
    def get_age(self):
        raw = self.d.get('birth_date')
        if raw:
            d = datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S.%fZ')
            return datetime.now().year - int(d.strftime('%Y'))

        return None
    
    def get_profile(self):
        try:
            return self.d['bio'].encode('ascii', 'ignore').replace('\n', '').strip()
        except (UnicodeError, UnicodeEncodeError, UnicodeDecodeError):
            return '[garbled]'
        
    def get_images(self):
        images = []
        for photo in self.d['photos']:
            img_file = cStringIO.StringIO(urllib.urlopen(photo['processedFiles'][0]['url']).read())
            images.append(Image.open(img_file))
            
        return images

    def get_messages(self):
        msg_list = []
        for msg in self.messages:
            msg_list.append(Message(msg))
            
        return msg_list

    def save_data(self, directory):
        i=1
        for picture in self.get_images():
            picture.save(directory + self.get_user_name() + '_' + str(i) +'.jpg', "JPEG")
            i += 1
            
        f = open(directory + self.get_user_name() + '_profile.txt', 'w')
        f.write(self.get_profile())
        f.close()
        
    def get_image_names(self):
        names_list = []
        
        for i in range(1,len(self.get_images())+1):
            names_list.append(self.get_user_name() + '_' + str(i) +'.jpg')
            
        return names_list
    
    @property
    def ago(self):
        raw = self.d.get('ping_time')
        if raw:
            d = datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S.%fZ')
            secs_ago = int(datetime.now().strftime("%s")) - int(d.strftime("%s"))
            if secs_ago > 86400:
                return u'{days} days ago'.format(days=secs_ago / 86400)
            elif secs_ago < 3600:
                return u'{mins} mins ago'.format(mins=secs_ago / 60)
            else:
                return u'{hours} hours ago'.format(hours=secs_ago / 3600)

        return '[unknown]'
    
    def __unicode__(self):
        return u'{name} ({age}), {distance}km, {ago}'.format(
            name=self.d['name'],
            age=self.age,
            distance=self.d['distance_mi'],
            ago=self.ago
        )
   
# user class used by the LocalDataWrapper
class LocalUser(UserBase):

    def __init__(self, user_name, image):
        self.user_name = user_name
        self.profile = ""
        self.image = image
    
    def get_user_name(self):
        return self.user_name
    
    def get_name(self):
        return "her"
    
    def get_images(self):
        return [self.image]
    
    def get_age(self):
        return None
    
    def get_profile(self):
        return self.profile
    
    def get_messages(self):
        return []
    
    def save_data(self, directory):
        return

    def get_image_names(self):
        return [self.user_name + ".jpg",]
  
class AutoUser(UserBase):
   
    def __init__(self, user_name, images, profile):
        self.user_name = user_name
        self.profile = profile
        self.images = images
    
    def get_user_name(self):
        return self.user_name
    
    def get_name(self):
        return "her"
    
    def get_images(self):
        return self.images
    
    def get_age(self):
        return None
    
    def get_profile(self):
        return self.profile
    
    def get_messages(self):
        return []
    
    def save_data(self, directory):
        return

    def get_image_names(self):
        names_list = []
        
        for i in range(1,len(self.get_images())+1):
            names_list.append(self.get_user_name() + '_' + str(i) +'.jpg')
            
        return names_list
    
    
class imageInterfaceBase(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        return
        
    @abc.abstractmethod
    def yes(self, user_name):
        return
    
    @abc.abstractmethod
    def no(self, user_name):
        return
    
    @abc.abstractmethod
    def autoPredictionEnabled(self):
        return
    
    @abc.abstractmethod
    def getNextUser(self):
        return
    
    @abc.abstractmethod
    def getMatches(self):
        return
    
    @abc.abstractmethod
    def sendMessage(self, user, message):
        return
    
    def writeResult(self, fileLoc, row):
        fp = open(fileLoc, 'a') 
        writer = csv.writer(fp) 
        writer.writerow((row))

class TinderWrapper(imageInterfaceBase):
    headers = {
        'app-version': '123',
        'platform': 'ios',
        'User-agent': 'Tinder/4.0.9 (iPhone; iOS 8.0.2; Scale/2.00)',
        'content-type': 'application/json', 
    }
    post_headers = {
        'app-version': '123',
        'platform': 'ios',
        'User-agent': 'Tinder/4.0.9 (iPhone; iOS 8.0.2; Scale/2.00)',
    }
    
    def __init__(self, fb_id, fb_auth_token, directory, labels_location):
        self.auth_token = self.get_auth_token(fb_id, fb_auth_token)
        self.directory = directory
        self.labels_location = labels_location
        self.current_user_list = []
         
    # sends a "yes" for a user and saves the data
    # as local labeled training data
    def yes(self, user):
        try:
            d = self.send_yes(user)
            user.save_data(self.directory)
            
            super(TinderWrapper, self).writeResult(self.labels_location, [user.get_user_name(), 10])
        except KeyError:
            raise
        else:
            #return d['match']
            return 
      
    # sends a "no" for a user and saves the data
    # as local labeled training data
    def no(self, user):
        try:
            self.send_no(user)
            user.save_data(self.directory)
            
            super(TinderWrapper, self).writeResult(self.labels_location, [user.get_user_name(), 0])
        except KeyError:
            raise
    
    def autoPredictionEnabled(self):
        return True
    
    # requests some more user information
    def getNextUser(self):
        
        if len(self.current_user_list)>0:
            return_user = self.current_user_list[0]
            del self.current_user_list[0]
            return return_user
        
        h = self.headers
        h.update({'X-Auth-Token': self.auth_token})
        r = requests.get('https://api.gotinder.com/user/recs', headers=h)
        if r.status_code == 401 or r.status_code == 504:
            raise Exception('Invalid code')
            print r.content
        
        if r.status_code == 403:
            raise Exception('Authentication Failed')
            print r.content
            
        if not 'results' in r.json():
            print r.json()
    
        # add users to the user list
        for result in r.json()['results']:
            self.current_user_list.append(TinderUser(result))
    
        # if we have users then return the user
        if len(self.current_user_list)>0:
            return_user = self.current_user_list[0]
            del self.current_user_list[0]
            return return_user
        
    def getMatches(self):
        
        h = self.post_headers
        h.update({'X-Auth-Token': self.auth_token})
        r = requests.post('https://api.gotinder.com/updates',headers=h)
        if r.status_code == 401 or r.status_code == 504:
            raise Exception('Invalid code')
            print r.content
        
        if r.status_code == 403:
            raise Exception('Authentication Failed')
            print r.content
            
        if not 'matches' in r.json():
            print r.json()
            return []
        
        matching_users = []
        for match in r.json()['matches']:
            matching_users.append(TinderUser(match['person'],match['messages']))
        
        return matching_users
        
    def sendMessage(self, user, message):
        
        h = self.headers
        h.update({'X-Auth-Token': self.auth_token})
        data = {"message": message}
        #r = requests.post('https://api.gotinder.com/user/matches/' + user.get_match_id(),headers=h, params=data)
        r = requests.get('https://api.gotinder.com/user/matches/5502d6c994ffa52134a538ae550f3fedf2014e041a6146d4',headers=h, params=data)
        if r.status_code in (400, 401, 504):
            raise Exception('Invalid code')
            print r.content
        
        if r.status_code == 403:
            raise Exception('Authentication Failed')
            print r.content
            
        if r.status_code == 500:
            raise Exception('Not a match')
            print r.content
            
    def send_yes(self, user):
        #u = 'https://api.gotinder.com/like/%s' % user.get_user_name()
        u = 'https://api.gotinder.com/pass/%s' % user.get_user_name()
        d = requests.get(u, headers=self.headers, timeout=0.7).json()
        return d
        
    def send_no(self, user):
        u = 'https://api.gotinder.com/pass/%s' % user.get_user_name()
        requests.get(u, headers=self.headers, timeout=0.7).json()
        
            
    def get_auth_token(self, fb_user_id, fb_auth_token):
        h = self.headers
        h.update({'content-type': 'application/json'})
        req = requests.post(
            'https://api.gotinder.com/auth',
            headers=h,
            data=json.dumps({'facebook_token': fb_auth_token, 'facebook_id': fb_user_id})
        )
        try:
            return req.json()['token']
        except:
            return None
    

class LocalDataWrapper(imageInterfaceBase):
    
    def __init__(self, directory, labels_location):
        
        self.labelsList = []
        self.directory = directory
        self.labels_location = labels_location
        
        # Reads in the x feature information from a csv file
        with open(labels_location, 'rb') as csvFile:
            reader = csv.reader(csvFile, delimiter=',')
            for row in reader:
                if len(row)>0:
                    self.labelsList.append(row[0])
        
        self.files = [f[:-4] for f in os.listdir(directory) if f[-3:] == "jpg"]
         
    def yes(self, user):
        super(LocalDataWrapper, self).writeResult(self.labels_location, [user.get_user_name(), 10])
        return False
    
    def no(self, user):
        super(LocalDataWrapper, self).writeResult(self.labels_location, [user.get_user_name(), 0])
        return False
    
    def autoPredictionEnabled(self):
        return False
    
    def getMatches(self):
        return []
    
    def getNextUser(self):
        
        while len(self.files) > 0 and self.files[0] in self.labelsList:
            del self.files[0]
        
        if len(self.files) == 0:
            return None
        
        user_name = self.files[0]
        del self.files[0]
        return LocalUser(user_name, Image.open(self.directory + user_name + ".jpg"))
    
    def sendMessage(self, user, message):
        return
    
class AutoDataWrapper(imageInterfaceBase):
    def __init__(self, directory, labels_location):
        
        self.directory = directory
        self.labels_location = labels_location
        self.users = {}
        
        for filename in [f for f in os.listdir(directory) if f[-3:] == "jpg"]:
            username = filename.split('_')[0]
            if self.users.has_key(username):
                self.users[username]['imageFiles'].append(Image.open(directory + filename))
            else:
                self.users[username] = {}
                self.users[username]['imageFiles'] = [Image.open(directory + filename),]
                profileFileLoc = directory + username + "_profile.txt"
                if not os.path.isfile(profileFileLoc):
                    continue
                
                with open(profileFileLoc, 'r') as profileFile:
                    profileText = " ".join(profileFile.readlines()).strip()
            
                self.users[username]['profile'] = profileText
         
    def yes(self, user):
        super(AutoDataWrapper, self).writeResult(self.labels_location, [user.get_user_name(), 10])
        del self.users[user.get_user_name()]
        return False
    
    def no(self, user):
        super(AutoDataWrapper, self).writeResult(self.labels_location, [user.get_user_name(), 0])
        del self.users[user.get_user_name()]
        return False
    
    def autoPredictionEnabled(self):
        return False
    
    def getMatches(self):
        return []
    
    def getNextUser(self):

        if len(self.users.keys()) == 0:
            return None
        
        user_name = self.users.keys()[0]
        user = self.users[self.users.keys()[0]]
        return AutoUser(user_name, user['imageFiles'], user['profile'])
    
    def sendMessage(self, user, message):
        return