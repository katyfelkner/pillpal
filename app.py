from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

# Flask app for interactive messaging
app = Flask(__name__)

# twilio client for reminders (using Emmma's login)
account_sid = 'AC28009372ebfab0facb6d0171f4feaf5c'
auth_token = '53131dd820f1c5ed4fbb12b0ce24f647'
client = Client(account_sid, auth_token)

@app.route("/sms", methods=['GET','POST'])
def sms_reply():
    body = request.values.get('Body',None)
    resp = MessagingResponse()
    test = str("you sent: "+body)
    resp.message(test)
    return str(resp)

def main():
    message = client.messages.create(body = "practice text", from_='+12029993074', to='+17033029984')
    
if __name__ == "__main__":
    app.run(debug=False)
    main()
