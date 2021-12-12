months = {
      "January":1, "February":2, "March":3, "April":4, "May":5, "June":6, 
           "July":7, "August":8, "September":9, "October":10, "November":11, "December":12 
}

months_list = [
	{
		"abbreviation": "Jan",
		"name": "January",
        "number":1
	},
	{
		"abbreviation": "Feb",
		"name": "February",
        "number":2
	},
	{
		"abbreviation": "Mar",
		"name": "March",
        "number":3
	},
	{
		"abbreviation": "Apr",
		"name": "April",
        "number":4
	},
	{
		"abbreviation": "May",
		"name": "May",
        "number":5
	},
	{
		"abbreviation": "Jun",
		"name": "June",
        "number":6
	},
	{
		"abbreviation": "Jul",
		"name": "July",
        "number":7
	},
	{
		"abbreviation": "Aug",
		"name": "August",
        "number":8
	},
	{
		"abbreviation": "Sep",
		"name": "September",
        "number":9
	},
	{
		"abbreviation": "Oct",
		"name": "October",
        "number":10
	},
	{
		"abbreviation": "Nov",
		"name": "November",
        "number":11
	},
	{
		"abbreviation": "Dec",
		"name": "December",
        "number":12
	}
]


# import time
# from time import sleep
# from sinchsms import SinchSMS
 
# # function for sending SMS
# def sendSMS():
 
#     # enter all the details
#     # get app_key and app_secret by registering
#     # a app on sinchSMS
#     number = '+353834018842'
#     app_key = 'your_app_key'
#     app_secret = 'your_app_secret'
 
#     # enter the message to be sent
#     message = 'Hello Message!!!'
 
#     client = SinchSMS(app_key, app_secret)
#     print("Sending '%s' to %s" % (message, number))
 
#     response = client.send_message(number, message)
#     message_id = response['messageId']
#     response = client.check_status(message_id)
 
#     # keep trying unless the status returned is Successful
#     while response['status'] != 'Successful':
#         print(response['status'])
#         time.sleep(1)
#         response = client.check_status(message_id)
 
#     print(response['status'])
 
# if __name__ == "__main__":
#     sendSMS()



# import clx.xms
# import requests

# def main():
# 	spid = "b930c1e030b64b15820f5c8e280b4a45"
# 	token = "a681f18c6b45422b8cb766b90976cdac"

# 	client = clx.xms.Client(service_plan_id=f'{spid}', token=f'{token}')

# 	create = clx.xms.api.MtBatchTextSmsCreate()
# 	create.sender = '46123123123'
# 	create.recipients = {'+353834018842'}
# 	create.body = 'Hello, world!'

# 	try:
# 		batch = client.create_batch(create)
# 	except (requests.exceptions.RequestException,
# 		clx.xms.exceptions.ApiException) as ex:
# 		print('Failed to communicate with XMS: %s' % str(ex))
# if __name__ == '__main__':
# 	main()

# from datetime import datetime, timedelta
# import time
# import threading

# while 1:
#     print("check something")
#     dt = datetime.now() + timedelta(hours=1)
#     dt = dt.replace(minute=10)

#     while datetime.now() < dt:
#         time.sleep(1)

