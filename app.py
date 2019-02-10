from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import os
import subprocess
from personpill import Person, Pill
import Menus
import personpill

# Flask app for interactive messaging
app = Flask(__name__)

# twilio client for reminders (using Katy's login)
account_sid = 'ACb15fe4fe0df5917125a88ad02d6d9b85'
auth_token = 'b0d5c2cdd62b5fb1bc6cc509666df9fe'
client = Client(account_sid, auth_token)
twil_num = +12562911243

people = {}
@app.route("/sms", methods=['GET','POST'])
def sms_reply():
    # get number
    num = request.values.get('From',None)
    body = request.values.get('Body',None)
    # is it a user we know?
    known = os.listdir("./testfamily")
    if people == {}:
        for k in known:
            # hard-coded - lazy
            people[k.replace(".txt", "")] = Person.from_file("testfamily/" + k)
    print(people)
    found = False
    for key,value in people.items():
        if num == key:
            # we know this user!
            # check their profile to see how to respond to them
            print("known user")
            found = True
            break
    if not found:
        new_user(num)
    else:
        # check the UI state for the known user and respond appropriately
        person = people[num]
        state = person.uistate
        person.menuOut = None
        if state == 0:
            # fully set up user. probably looking for menu?
            Menus.main_menu(person, body)
        elif state == 1:
            # read the name and ask refill day
            get_name_ask_refill_day(person, body)
        elif state == 2:
            # ask how many pills they usually take
            ask_how_many_pills(person,body)
        elif state == 3:
            ask_for_first_pill(person, body)
        elif state == 4:
            parse_pill_name(person,body)
        elif state == 5:
            parse_pill_times(person, body)
        elif state == 20:
            Menus.remove_pill(person, body)
        elif state == 21:
            Menus.refill_pill(person, body)
        elif state == 22:
            Menus.change_name(person, body)
        elif state == 23:
            Menus.change_refill(person, body)
        elif state == 24:
            person.menuOut = Menus.edit_premenu(person,body)
        elif state == 25:
            Menus.view_pills(person, body)
        elif state == 26:
            Menus.add_pill(person, body)
        elif state == 27:
            Menus.add_pill_times(person, body)
        elif state == 30:
            Menus.edit_menu(person,body,person.menuOut)
        elif state == 31:
            Menus.edit_name(person,body,person.menuOut)
        elif state == 32:
            Menus.edit_food(person,body,person.menuOut)
        elif state == 33:
            Menus.edit_freq(person,body,person.menuOut)
        elif state == 34:
            Menus.edit_remaining(person,body,person.menuOut)
        elif state == 35:
            Menus.edit_call(person,body,person.menuOut)
        elif state == 36:
            Menus.edit_times(person,body,person.menuOut)
            
    print("returning ok from sms_reply()")
    return "Everything seems ok"

def new_pill(): #TODO: needs some parameters
    pid = os.fork()
    # n greater than 0  means parent process
    if pid > 0:
        print("Parent process and id is : ", os.getpid())
        print("just return from this call")
        return

    # n equals to 0 means child process
    else:
        print("Child process and id is : ", os.getpid()) 
        print("this is where we start new scheduled reminder")

def new_user(num):
    # make a file with number as the filename
    welcome = "Welcome new user! What's your name?"
    message = client.messages.create(body = welcome, from_=twil_num, to= num)
    #os.system("touch testfamily/" + num + ".txt")
    people[num] = Person(number=num, uistate=1)
    return True

def get_name_ask_refill_day(person, body):
    person.set_name(body)
    person.uistate = 2
    message = "Hello, " + body + "! What day do you usually refill your pillbox (e.g. Monday, Tuesday)?"
    message = client.messages.create(body = message, from_=twil_num, to= person.number)
    return True

def ask_how_many_pills(person, body):
    # parse respone to days
    if person.set_day(body):
        # successfully set the day, so move on to getting number of pills
        person.uistate = 3
        message = "How many pills should I remind you to take? (enter a number)"
        message = client.messages.create(body = message, from_=twil_num, to= person.number)
        return True
    else:
        message = "Please enter a day of the week."
        message = client.messages.create(body = message, from_=twil_num, to= person.number)
        return True

def ask_for_first_pill(person, body):
    # parse respone to number of pills
    if body.strip().isdigit():
        # set the number and ask for the first one
        person.pill_count = int(body.strip())
        person.uistate = 4
        message = "Ok! What is the name of the first medication?"
        message = client.messages.create(body = message, from_=twil_num, to= person.number)
        return True
    else:
        message = "Please enter a whole number."
        message = client.messages.create(body = message, from_=twil_num, to= person.number)
        return True

def parse_pill_name(person, body):
    person.add_pill(Pill(name=body))
    # now ask for the the times it should be taken
    person.uistate = 5
    message = "Enter the times you need to be reminded to take " + body
    message = message + ".\nPlease use HH:MM in 24 hour time, separated by commas.\n"
    message = message + "e.g. 08:00, 12:30, 17:00"
    message = client.messages.create(body = message, from_=twil_num, to= person.number)
    return True

def parse_pill_times(person, body):
    times = body.split(",")
    for t in times:
        if person.pillset[-1].add_time(t):
            #success! get the next one!
            pass
        else:
            message = "Please use HH:MM in 24 hour time, separated by commas."
            message = client.messages.create(body = message, from_=twil_num, to= person.number)
            return True

    # if we made it here, adding times was successful
    # check if we are done
    if len(person.pillset) == person.pill_count:
        # added all pills
        message = "Setup is complete. I will start sending pill reminders!"
        Person.to_file(person)
        person.process_set_up()
        message = client.messages.create(body = message, from_=twil_num, to= person.number)
        person.uistate = 0
        return True
    else:
        # we need to add more pills
        person.uistate = 4
        message = "What is the name of your next medication?"
        message = client.messages.create(body = message, from_=twil_num, to= person.number)
        return True
    
if __name__ == "__main__":
    app.run(debug=True)
