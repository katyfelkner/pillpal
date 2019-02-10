from twilio.rest import Client
account_sid = 'AC28009372ebfab0facb6d0171f4feaf5c'
auth_token = '53131dd820f1c5ed4fbb12b0ce24f647'
client = Client(account_sid, auth_token)
message = client.messages.create(body = "practice text", from_='+12029993074', to='+17033029984')
