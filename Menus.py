from twilio.rest import Client
from personpill import Person, Pill
# twilio client for reminders (using Katy's login)
account_sid = 'ACb15fe4fe0df5917125a88ad02d6d9b85'
auth_token = 'b0d5c2cdd62b5fb1bc6cc509666df9fe'
client = Client(account_sid, auth_token)
twil_num = '+12562911243'

def __init__():
    pass

def main_menu(person,body):
    body = body.strip()
    if 'ADD PILL' in body:
        person.uistate = 26
        message = client.messages.create(body="What is the name of the pill?", from_=twil_num, to=person.number)
    elif 'REMOVE PILL' in body:
        person.uistate = 20
        message = client.messages.create(body="What prescription would you like to remove?", from_=twil_num,
                                         to=person.number)
    elif 'REFILL' in body:
        person.uistate = 21
        message = client.messages.create(body="What prescription would you like to refill, and how many new pills do you have?",
                                         from_=twil_num, to=person.number)
    elif 'CHANGE NAME' in body:
        person.uistate = 22
        message = client.messages.create(body="Write the new name you would like to use", from_=twil_num, to=person.number)
    elif 'CHANGE REFILL' in body:
        person.uistate = 23
        message = client.messages.create(body="What day would you like to refill on?", from_=twil_num, to=person.number)
    elif 'EDIT PILL' in body:
        person.uistate = 24
        message = client.messages.create(body="Which prescription would you like to edit?", from_=twil_num, to=person.number)
    elif "VIEW PRESCRIPTIONS" in body:
        person.uistate = 0
        view_pills(person, body)
    else:
        message = client.messages.create(body="I don't know what you mean. Please choose from ADD PILL, REMOVE PILL, REFILL, EDIT PILL, CHANGE NAME, VIEW PRESCRIPTIONS or CHANGE REFILL",from_=twil_num, to=person.number)
def change_name(person,body):
    body = body.strip()
    person.name = body
    message = client.messages.create(body=str("Okay "+person.name+"!"),from_=twil_num, to=person.number)
    person.uistate = 0
def change_refill(person,body):
    body = body.strip()
    if 'MENU' in body:
        person.uistate = 0
    if person.set_time(body):
        message = client.messages.create(body=str("Refill reminders will now be sent on "+body), from_=twil_num, to=person.number)
        person.uistate = 0
    else:
        message = client.messages.create(body="Please enter a lowercase day of the week, or send MENU to return to main menu", from_=twil_num, to=person.number)
def refill_pill(person,body):
    body = body.strip()
    if 'MENU' in body:
        person.uistate = 0
        return False
    fields = body.split(',')
    if person.refill(fields[0].strip(),int(fields[1])):
        person.uistate = 0
        message = client.messages.create(body="Refilled and ready to go!", from_=twil_num, to=person.number)
        return True
    else:
        message = client.messages.create(body="I couldn't find that prescription. Check your spelling and try again, or send MENU to return to main menu", from_=twil_num, to=person.number)
        return False
def remove_pill(person,body):
    body = body.strip()
    if 'MENU' in body:
        person.uistate = 0
        return False
    if person.remove_pill(body):
        message = client.messages.create(body=str(body+" was removed from your prescriptions"), from_=twil_num,
                                         to=person.number)
        person.uistate = 0
        Person.to_file(person)
        person.process_set_up()
        return True
    else:
        message = client.messages.create(body="I couldn't find that prescription. Check your spelling and try again, or send MENU to return to main menu", from_=twil_num,
                                         to=person.number)
        return False

def view_pills(person,body):
    m = "Your current prescriptions and settings: \n"    
    for pill in person.pillset:
        print(pill.user_string())
        m+=pill.user_string()
    messaage = client.messages.create(body=m, from_=twil_num, to=person.number)
    person.uistate = 0
    return True

def add_pill(person, body):
    person.add_pill(Pill(name=body))
    # now ask for the the times it should be taken
    person.uistate = 27
    message = "Enter the times you need to be reminded to take " + body
    message = message + ".\nPlease use HH:MM in 24 hour time, separated by commas.\n"
    message = message + "e.g. 08:00, 12:30, 17:00"
    message = client.messages.create(body = message, from_=twil_num, to= person.number)
    Person.to_file(person)
    person.process_set_up()
    return True

def add_pill_times(person,body):
    times = body.split(",")
    person.uistate = 0
    for t in times:
        if person.pillset[-1].add_time(t):
            #success! get the next one!
            pass
        else:
            message = "Please use HH:MM in 24 hour time, separated by commas."
            message = client.messages.create(body = message, from_=twil_num, to= person.number)
            return True
    message = "New pill has been added."
    message = client.messages.create(body = message, from_=twil_num, to= person.number)
    person.pill_count += 1
    Person.to_file(person)
    person.process_set_up()
    return True
        
def edit_premenu(person,body):
    body = body.strip()
    pill_index = person.find_pill(body)
    if 'MENU' in body:
        person.uistate = 0
        return False
    elif pill_index>0:
        person.uistate = 30
        message = client.messages.create(body=str("Here's your prescription information: "+person.pillset[pill_index].user_string),
            from_=twil_num, to=person.number)
        message = client.messages.create(body="What would you like to edit? Send NAME, REMINDER TIMES, FOOD, TEXT FREQUENCY, PILLS REMAINING, or CALL SETTINGS",
                                         from_=twil_num, to=person.number)
        return pill_index
    else:
        message = client.messages.create(body="I couldn't find that prescription. Check your spelling and try again, or send MENU to return to main menu", from_=twil_num,
                                         to=person.number)
        return False
def edit_menu(person,body,pill_index):
    body = body.strip()
    if 'MENU' in body:
        person.uistate = 0
        return False
    elif 'NAME' in body:
        person.uistate = 31
        message = client.messages.create(body="Enter the new name for this prescription",from_=twil_num,to=person.number)
    elif 'FOOD' in body:
        person.uistate = 32
        message = client.messages.create(body="How long before taking this should you eat?",from_=twil_num,to=person.number)
    elif "TEXT FREQUENCY" in body:
        person.uistate = 33
        message = client.messages.create(body="How many minutes would you like between reminders?",from_=twil_num,to=person.number)
    elif 'PILLS REMAINING' in body:
        person.uistate = 34
        message = client.messages.create(body="How many pills would you like to add/subtract? eg. -1, 5",
                                         from_=twil_num, to=person.number)
    elif 'CALL SETTINGS' in body:
        person.uistate = 35
        message = client.messages.create(body="How many reminders would you like before I call you?",
                                         from_=twil_num, to=person.number)
    elif 'TIMES' in body:
        person.uistate = 36
        message = client.messages.create(body='Enter the times you would like reminders, in 24 hour format, separated by commas',
                                         from_=twil_num, to=person.number)
    else:
        return False

    return pill_index

def edit_name(person,body,pill_index):
    body = body.strip()
    person.pillset[pill_index].name = body
    person.uistate = 0
    message = client.messages.create(body="Name changed!",from_=twil_num,to=person.number)  #would be better to have a more specific statement
    return True

def edit_food(person,body,pill_index):
    body = body.strip()
    if body.isdigit():
        person.pillset[pill_index].food = True
        person.pillset[pill_index].food_mins = int(body)
        person.uistate = 0
        message = client.messages.create(body=str("You'll now get reminders to eat food before taking "+person.pillset[pill_index].name),from_=twil_num,to=person.number)
        return True
    else:
        message = client.messages.create(body="I don't know what you mean. Please enter an integer between 0-59",from_=twil_num,to=person.number)
        return False
def edit_freq(person,body,pill_index):
    body = body.strip()
    if body.isdigit():
        person.uistate = 0
        person.pillset[pill_index].freq = int(body)
        message = client.messages.create(body=str("I will now remind you every "+body+" minutes"),from_='twill_num',to=person.number)
        Person.to_file(person)
        person.process_set_up()
        return True
    else:
        message = client.messages.create(body=str("I don't know what you mean. Please send an integer between 0-59"),
                                         from_=twil_num, to=person.number)
        return False
def edit_remaining(person,body,pill_index):
    body = body.strip()
    try:
        body = int(body)
    except ValueError:
        message = client.messages.create(body="I don't know what you mean. Please enter a whole number",
                                         from_=twil_num, to=person.number)
        return False
    person.pillset[pill_index].pills_remaining+=body
    message = client.messages.create(body=str("You now have" + body + " pills left"), from_=twil_num,
                                     to=person.number)
    person.uistate = 0
    return True
def edit_call(person,body,pill_index):
    body = body.strip()
    if body.isdigit():
        person.pillset[pill_index].call_point = int(body)
        message = client.messages.create(body="I will now call you after "+body+" messages",
                                         from_=twil_num, to=person.number)
        person.uistate = 0
        return True
    else:
        message = client.messages.create(body="I don't know what you mean. Please enter an integer",
                                         from_=twil_num, to=person.number)
def edit_times(person,body,pill_index):  #this method kind of sucks
    body = body.strip()
    times = body.split(',')
    person.pillset[pill_index].times = []
    for time in times:
        if person.pillset[pill_index].add_time(time):
            pass
        else:
            message = client.messages.create(body="That value isn't a time. Please try again, and remember to submit times in 24 hour hh:mm format",from_=twil_num, to=person.number)
            return False
    message = client.messages.create(body="Times have been updated", from_=twil_num,to=person.number)
    person.uistate = 0
    Person.to_file(person)
    person.process_set_up()
    return True
