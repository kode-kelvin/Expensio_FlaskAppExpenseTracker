#TODO                     
# Create a free account in https://sinch.com/
# pip install requests
# pip install python-decouple
# pip install clx-sdk-xms



from decouple import config
import time
from datetime import datetime, timedelta
import clx.xms
import requests

def main():
	spid = config['SPID'] #Service Plan Id
	token = config['TOKEN'] #Your token
    
    # -- ALL ABOVE CREDENTIALS CAN BE FOUND IN ==> https://dashboard.sinch.com/sms/api/rest
	while 1:
		client = clx.xms.Client(service_plan_id=f'{spid}', token=f'{token}')
		create = clx.xms.api.MtBatchTextSmsCreate()
		create.sender = '46123123123' #this is your assigned SINCH number
		create.recipients = {'+353834113367'}
		create.body = 'Hey You!!, this is the body of your SMS'

		try:
			batch = client.create_batch(create)
		except (requests.exceptions.RequestException,
			clx.xms.exceptions.ApiException) as ex:
			print('Failed to communicate with XMS: %s' % str(ex))

		dt = datetime.now() + timedelta(hours=1)
		dt = dt.replace(minute=10)

		while datetime.now() < dt:
			time.sleep(1)

	
if __name__ == '__main__':
	main()







