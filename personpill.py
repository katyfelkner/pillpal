import datetime
import multiprocessing as mp
from twilio.rest import Client
import schedule
import time

account_sid = 'ACb15fe4fe0df5917125a88ad02d6d9b85'
auth_token = 'b0d5c2cdd62b5fb1bc6cc509666df9fe'
client = Client(account_sid, auth_token)
twil_num = +12562911243

def __init__():
    pass

class Pill:
        def __init__(self,name='pill1',times = [],food = False, food_mins = 0, freq = 10, pills_remaining = 0,call_point = 3):
            self.name = name
            self.times = times
            self.food = food
            self.food_mins = food_mins
            self.freq = freq
            self.pills_remaining = pills_remaining
            self.call_point = call_point

        def set_freq(self,body):
            body = body.strip()
                
            if body.isdigit():
                self.freq = int(body)
                return True
            else:
                return False

        def refill(self,body):
            body = body.strip()
            if body.isdigit():
                self.pills_remaining+=int(body)
                return True
            else:
                return False

        def set_call(self,body):
            body = body.strip()
            if body.isdigit():
                self.call_point = body
                return True
            else:
                return False

        def add_time(self,body):
            if ':' in body:
                body = body.strip()
                b = body.split(':')
                hour = b[0]
                min = b[1]
                if not (hour.isdigit() and min.isdigit()):  #checks that it's the correct format.
                    return False
                elif int(min)>59:
                    return False
                else:
                    pill_time = body
                    self.times.append(pill_time)
                    return True
            else:
                return False
        
        def refill(self,body):
            body = body.strip()
            if body.isdigit():
                self.pills_remaining+=int(body)
                return True
            else:
                return False

        def set_food(self,body):
            body = body.strip()
            if 'yes' in body or 'Yes' in body or 'YES' in body:  #check food value in main method before asking next question
                self.food = True
                return True
            elif 'no' in body or 'NO' in body or 'No' in body:
                self.food = False
                return True
            else:
                return False

        def set_food_time(self,body):
            body = body.strip()
            if body.isdigit():
                min = int(body)
                if min > 59:
                    return False
                self.food_mins = min
                return True
            else:
                return False

        def user_string(self):
            str_out = self.name + "\n"
            if self.food:
                str_out = str_out + "Eat "+str(self.food_mins)+" minutes before taking\n"
            else:
                str_out+="No food with pills\n"

            str_out = str_out + "I will text you every " + str(self.freq) + ' minutes, and call after I have texted you ' + str(self.call_point) + ' times\n'
            str_out = str_out + "You have "+str(self.pills_remaining) + " pills left\n"
            str_out+="You have set the times to take this pill at: "
            for time in self.times:
                str_out += time
                str_out += ','
            str_out = str_out[:int(len(str_out)-1)]
            str_out+='\n'
            return str_out
        def __str__(self):
            str_out = self.name+","+str(self.food)+','+str(self.food_mins)+","+str(self.freq)+','+str(self.pills_remaining)+','+str(self.call_point)+"\n"
            for time in self.times:
                str_out+=str(time)
                str_out+=','
            str_out+='\n'
            return str_out                        
        
class Person:
    def __init__(self,uistate,name="user1",pillset=[],number = 0,refill_day=6,refill_time=14,pill_count=0):
        self.name = name
        self.pill_count = pill_count
        self.uistate = uistate
        self.pillset = pillset
        self.processes = []
        self.number = number
        self.refill_day = refill_day
        #self.refill_time = refill_time
        self.days = {
                'monday': 0,
                'tuesday': 1,
                'wednesday': 2,
                'thursday': 3,
                'friday': 4,
                'saturday': 5,
                'sunday': 6,
        }
            
    def add_pill(self,pill):
        self.pillset.append(pill)

    def set_name(self,body):
        body = body.strip()
        self.name = body
        return True

    def set_number(self,num):
        self.number = num
 
    def set_day(self,body):
        body = body.strip()
        if body.lower() in self.days:
                self.refill_day = self.days[body.lower()]
                return True
        else:
                return False

    def remove_pill(self,pill_name):
        for pill in self.pillset:
            if pill.name == pill_name:
                self.pillset.remove(pill)
                return True
        return False

    def refill(self,pill_name,number):
        for pill in self.pillset:
            if pill.name == pill_name:
                pill.pills_remaining+=number
                return True
        return False

    def find_pill(self,pill_name):
        for i in range(len(self.pillset)):
            if self.pillset[1].name == pill_name:
                return i
        return -1

    def __str__(self):
        str_out = str(self.number)+","+self.name+','+str(self.refill_day)+'\n'
        for pill in self.pillset:
            str_out+=str(pill)
        str_out+='END'
        return str_out

    @staticmethod
    def from_file(filename):
        user = Person(0)
        file = open(filename,mode='r')
        first_line = file.readline()
        fields = first_line.split(',')
        user.set_number(fields[0])
        user.set_name(fields[1])
        user.refill_day = fields[2].strip()
        line = ""
        while True:
            line = file.readline().strip()
            if 'END' in line:
                    break
            fields = line.split(',')
            pill = Pill()
            pill.name = fields[0]
            pill.food = bool(fields[1])
            pill.food_mins = int(fields[2])
            pill.freq = int(fields[3])
            pill.pills_remaining = int(fields[4])
            pill.call_point = int(fields[5])
            line = file.readline().strip()
            times = line.split(',')
            for time in times:
                pill.add_time(time)
            user.pill_count = len(user.pillset)
            file.close()
            return user

    @staticmethod
    def to_file(user):
        # hardcoded - lazy
        filename = "testfamily/" + str(user.number)+".txt"
        new_file = open(filename,'w')
        new_file.write(str(user))
        new_file.close()

    def process_set_up(self):
        if self.processes is not []:
            # kill the processes
            for p in self.processes:
                p.terminate()
                self.processes.remove(p)
            
        # now make a new process
        self.processes.append(mp.Process(target=self.run_process))
        self.processes[-1].start()
        
        
    def run_process(self):

        # schedule box refill reminder
        print("trying to schedule refill reminder") 
        if self.refill_day == 0:
            schedule.every().monday.at("18:00").do(self.refill_remind)
        elif self.refill_day == 1:
            schedule.every().tuesday.at("18:00").do(self.refill_remind)
        elif self.refill_day == 2:
            schedule.every().wednesday.at("18:00").do(self.refill_remind)
        elif self.refill_day == 3:
            schedule.every().thursday.at("18:00").do(self.refill_remind)
        elif self.refill_day == 4:
            schedule.every().friday.at("18:00").do(self.refill_remind)
        elif self.refill_day == 5:
            schedule.every().saturday.at("18:00").do(self.refill_remind)
        elif self.refill_day == 6:
            schedule.every().sunday.at("18:00").do(self.refill_remind)
        print("scheduled refill reminder")
        
        # schedule pill reminders
        for p in self.pillset:
            print("scheduling for "+ p.name)
            for t in p.times:
                print("scheduling for time: " + t)
                # testing purposes only
                schedule.every(10).seconds.do(self.pill_remind, pill=p)   
                #schedule.every().day.at(t).do(pill_remind, pill=p, client=client)
                
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def pill_remind(self, pill):
        print("inside the pill_remind function")
        def pill_text(pillName):
                print("inside the pill_text function")
                if (False): #sensor check here
                        return schedule.CancelJob
                message = "It's time to take " + pillName + "!"
                message = client.messages.create(body = message, from_=twil_num, to= self.number)
                return schedule.CancelJob

        print("scheduling pill texts")
        schedule.every(10).seconds.do(pill_text, pillName=pill.name)
        return None

    def refill_remind(self):
            message = "It's time to refill your pillbox!"
            message = client.messages.create(body = message, from_=twil_num, to= self.number)
            return None
