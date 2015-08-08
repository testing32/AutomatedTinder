from Tkinter import Frame, Button, LEFT, BOTTOM, END, Label, Tk, StringVar, OptionMenu, DISABLED, NORMAL, Toplevel, Entry
from PIL import Image, ImageTk
from imageInterface import LocalDataWrapper, TinderWrapper, AutoDataWrapper
import csv
import os
from Models import modelBuilder, userPredictor
from FaceDetect import face_detect

class App:

    #https://www.facebook.com/dialog/oauth?client_id=464891386855067&redirect_uri=https://www.facebook.com/connect/login_success.html&scope=basic_info,email,public_profile,user_about_me,user_activities,user_birthday,user_education_history,user_friends,user_interests,user_likes,user_location,user_photos,user_relationship_details&response_type=token
    #fb_id = '535036946'
    fb_id = '10152761571561947'
    fb_auth_token = 'CAAGm0PX4ZCpsBAHlIZCk3NRtXKSWo2Fa8Ph6BkOWEz26l6CURjZCFlADxpRnLtJUXYZBaRsyWupGsR6UCjlE0tCSbkyLwDCoFhtRdDe6DHDC3TdiQoMGoUQFeqifm2eU2dpRiBBE8goucOrdDsaKyEDya7bPZByjEu67SKAZBt00ySGrUpZCAhNLgJkd6c8TTfeu93ibYPbN5nAH0XXfkKj3FSh6Qyi6FTnxuAgzV0VSAZDZD'
    
    def __init__(self, master):

        # sets the image repository and the user labeled data
        self.dictionaryLocation = "PreLabeledTrainingData/women/"
        
        self.autoLabels = "AutoLabeledData/labels.csv"
        self.autoImageLocation = "AutoLabeledData/"
        self.autoFaceLocation = "AutoLabeledData/Faces/"
        
        self.newImageLocation = "UserTrainingData/"
        self.labelLocation = "UserTrainingData/womenlabels.csv"
        #self.newImageLocation = "AutoLabeledData/"
        #self.labelLocation = "AutoLabeledData/labels.csv"
        
        self.userPredictor = userPredictor.UserPredictor("Models/", '/home/testing32/Downloads/word2vec/trunk/vectors.bin', "user_")

        self.images = None
        self.currentImage = None
        self.currentUser = None
        self.matches = []
        self.master = master

        # set the title
        master.wm_title("Automatic Tinder")

        # binds the frame and the key events
        button_frame = Frame(master)
        button_frame.bind_all("<Key>", self.key_press)
        button_frame.pack()

        # default menu value
        variable = StringVar(button_frame)
        variable.set("Local") 
        
        # set up the drop down menu for switching between Local images and Tinder images
        w = OptionMenu(button_frame, variable, "Local", "Tinder", command=self.menu_change)
        w.pack(side=LEFT)
        
        # create the "No" button
        self.no_btn = Button(button_frame, text="NO (1)", fg="red", command=self.no)
        self.no_btn.pack(side=LEFT)

        # create the "Yes" button
        self.yes_btn = Button(button_frame, text="YES (2)", fg="blue", command=self.yes)
        self.yes_btn.pack(side=LEFT)
        
        # create the "Automate" button
        self.auto_btn = Button(button_frame, text="Automate", fg="brown", command=self.auto)
        self.auto_btn.pack(side=LEFT)
        
        # create the "Previous Image" button
        self.prev_img_btn = Button(button_frame, text="Previous Image", fg="black", command=self.showPreviousImage)
        self.prev_img_btn.pack(side=LEFT)
        
        # create the "Next Image" button
        self.next_img_btn = Button(button_frame, text="Next Image", fg="black", command=self.showNextImage)
        self.next_img_btn.pack(side=LEFT)
        
        # create the "Matches" button
        self.matches_text = StringVar(value="Matches (0)")
        self.matches_btn = Button(button_frame, textvariable=self.matches_text, command=self.openMatches)
        self.matches_btn.pack(side=BOTTOM)
        
        # Setting up the profile text area
        profile_frame = Frame(master)
        profile_frame.pack()
        
        self.profile_text = StringVar(value="")
        self.profile_lbl = Label(profile_frame, textvariable=self.profile_text, width=60,wraplength=475)
        self.profile_lbl.pack(side=BOTTOM)
        
        # Setting up the image area
        image_frame = Frame(master)
        image_frame.pack()
        
        # load the image
        self.pic = Label()
        self.pic.pack(side=BOTTOM)
        
        # create the interface to our data
        """
        self.imgInterface = AutoDataWrapper(
            self.dictionaryLocation, 
            self.labelLocation)
        """
        self.imgInterface = LocalDataWrapper(
            self.dictionaryLocation, 
            self.labelLocation)
        
        # Load the next user from the image interface
        self.loadUser(self.imgInterface.getNextUser())

    def key_press(self, event):
        # handles the key events
        if event.char == "1": #we say no
            self.no()
        elif event.char == "2" and self.yes(): # we say yes and hope for match
            self.startConversation()
        
    def menu_change(self, event):
        # handles the menu change events by switching
        # the image interface
        if event == "Local":
            self.imgInterface = LocalDataWrapper(
                self.dictionaryLocation, 
                self.labelLocation)
        elif event == "Tinder":
            self.imgInterface = TinderWrapper(
                self.fb_id, 
                self.fb_auth_token, 
                self.newImageLocation, 
                self.labelLocation)
        
        # load the next user from the image interface
        self.loadUser(self.imgInterface.getNextUser())
         
    # the current user is a yes   
    def yes(self):
        self.imgInterface.yes(self.currentUser)
        self.loadUser(self.imgInterface.getNextUser())
        print "Yes"
    
    # the current user is a no
    def no(self):
        self.imgInterface.no(self.currentUser)
        self.loadUser(self.imgInterface.getNextUser())
        print "No"
        
    # Start auto-labeling users
    def auto(self):
        # if the image interface doesn't 
        # allow auto-prediction then return
        if not self.imgInterface.autoPredictionEnabled():
            return
        
        # start by saving the images and profile
        self.currentUser.save_data(self.autoImageLocation)
        
        # find and save the faces
        for imageName in self.currentUser.get_image_names():
            face_detect.loadImageSaveFace(self.autoImageLocation, imageName, self.autoFaceLocation)
            
        userFileNames = [s for s in os.listdir(self.autoFaceLocation) if s.endswith(".jpg") and s.startswith(self.currentUser.get_user_name())]
        
        if len(userFileNames) == 0:
            print "No Faces Detected"
            return
        
        if self.userPredictor.predict(self.autoFaceLocation, userFileNames, profile=self.currentUser.get_profile()):
            self.imgInterface.send_yes(self.currentUser)
            self.writeToLabelCVSFile(self.autoLabels, [self.currentUser.get_user_name(),10])
            print "Yes"
        else:
            self.imgInterface.send_no(self.currentUser)
            self.writeToLabelCVSFile(self.autoLabels, [self.currentUser.get_user_name(),0])
            print "No"
        
        self.loadUser(self.imgInterface.getNextUser())
        
    def loadUser(self, user):
        self.currentUser = user
        self.loadImages(user)
        
        if user is None:
            self.profile_text.set("")
        
        self.profile_text.set(user.get_profile())
        self.updateMatches(self.imgInterface.getMatches())
        
    def updateMatches(self, matches):
        self.matches = matches
        self.matches_text.set("Matches (" + str(len(matches)) + ")")
        if len(matches) == 0:
            self.matches_btn.config(state=DISABLED)
        else:
            self.matches_btn.config(state=NORMAL)
        
    # loads the user's images
    def loadImages(self, user):
            
        if user is None:
            self.images = None
            self.pic.configure(image=None)
            self.pic.image = None
            self.currentImage = None
            return
        
        images = user.get_images()
        
        if len(images) == 0:
            self.images = None
            self.pic.configure(image=None)
            self.pic.image = None
            self.currentImage = None
            return
        
        self.images = images
        self.setImage(images[0])
        
    # sets the display image
    def setImage(self, image):
        
        # load the image
        photo = ImageTk.PhotoImage(image)
        self.pic.configure(image=photo)
        self.pic.image = photo # keep a reference!
        self.currentImage = image
        
        if self.hasPreviousImage():
            self.prev_img_btn.config(state=NORMAL)
        else:
            self.prev_img_btn.config(state=DISABLED)
            
        if self.hasNextImage():
            self.next_img_btn.config(state=NORMAL)
        else:
            self.next_img_btn.config(state=DISABLED)
             
    def getCurrentImgIndex(self):
        if len(self.images) == 0:
            return 0
        
        return self.images.index(self.currentImage)
    
    def hasPreviousImage(self):
        return self.getCurrentImgIndex() > 0
    
    def hasNextImage(self):
        return self.getCurrentImgIndex() + 1 < len(self.images)
    
    def showPreviousImage(self):
        if self.hasPreviousImage():
            self.setImage(self.images[self.getCurrentImgIndex() - 1])
        
    def showNextImage(self):
        if self.hasNextImage():
            self.setImage(self.images[self.getCurrentImgIndex() + 1])

    def writeToLabelCVSFile(self, fileLoc, row):
        fp = open(fileLoc, 'a') 
        writer = csv.writer(fp) 
        writer.writerow((row))
       
       
    ###############
    # MATCH METHODS
    ###############
    
    def openMatches(self):
        t = Toplevel(self.master)
        t.wm_title("Current Matches")
        
        self.current_match_index = 0
        self.current_match = None
        
        button_frame = Frame(t)
        button_frame.pack()
        
        # create the "Previous Match" button
        self.prev_match_btn = Button(button_frame, text="Previous Match", fg="black", command=self.showPreviousMatch)
        self.prev_match_btn.pack(side=LEFT)
        
        # create the "Next Match" button
        self.next_match_btn = Button(button_frame, text="Next Match", fg="black", command=self.showNextMatch)
        self.next_match_btn.pack(side=LEFT)
        
        # create the "Send Message" button
        self.send_msg_btn = Button(button_frame, text="Send Message", fg="black", command=self.sendMessage)
        self.send_msg_btn.pack(side=LEFT)
        
        img_frame = Frame(t)
        img_frame.pack()
        
        # show the match
        self.match_pic = Label(img_frame)
        self.match_pic.pack(side=BOTTOM)
        
        msg_frame = Frame(t)
        msg_frame.pack()
        
        # show the previous messages
        self.match_pic = Label(img_frame)
        self.match_pic.pack(side=BOTTOM)
        
        self.msg_text = StringVar(value="")
        self.msg_lbl = Label(msg_frame, textvariable=self.msg_text)
        self.msg_lbl.pack(side=BOTTOM)
        
        text_frame = Frame(t)
        text_frame.pack()
        
        # text entry
        self.message_entry = Entry(text_frame)
        self.message_entry.pack()
        
        self.refreshMatch()
        
    def refreshMatch(self):
        self.current_match = self.matches[self.current_match_index]
        self.setMatchImage()
        self.displayMessages()
        
    def setMatchImage(self):
                   
        images = self.current_match.get_images()
        
        if len(images) == 0:
            return
        
        # load the image
        photo = ImageTk.PhotoImage(images[0])
        self.match_pic.configure(image=photo)
        self.match_pic.image = photo # keep a reference!
        self.updateMatchButtons()

    def showPreviousMatch(self):
        self.current_match_index -= 1
        self.refreshMatch()
    
    def showNextMatch(self):
        self.current_match_index += 1
        self.refreshMatch()
    
    def sendMessage(self):
        messageText = self.message_entry.get()
        
        if messageText in (None, ""):
            return
        
        self.message_entry.delete(0, END)
        self.imgInterface.sendMessage(self.currentUser, messageText)
    
    def updateMatchButtons(self):
        if self.current_match_index == 0:
            self.prev_match_btn.config(state=DISABLED)
        else:
            self.prev_match_btn.config(state=NORMAL)
            
        if self.current_match_index + 1 < len(self.matches):
            self.next_match_btn.config(state=NORMAL)
        else:
            self.next_match_btn.config(state=DISABLED)

    def displayMessages(self):
        
        all_msgs = ""
        for msg in self.current_match.get_messages():
            if msg.get_from() == self.current_match.get_user_name():
                all_msgs = all_msgs + self.current_match.get_name() + ": "
            else:
                all_msgs = all_msgs + "Me: "
            all_msgs = all_msgs + msg.get_message() + "\n"
            
        self.msg_text.set(all_msgs)

root = Tk()

app = App(root)

root.mainloop()