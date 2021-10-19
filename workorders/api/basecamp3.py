# Initial code. Not Finished/Tested
import requests

create_project_endpoint		= 'projects.json'
create_attachment_endpoint	= 'attachments.json'
create_upload_endpoint		= 'buckets/{0}/vaults/{1}/uploads.json'
update_people_endpoint		= 'projects/{0}/people/users.json'


def authenticate_user():
	pass

def get_account_id_and_token():
	pass

def create_basecamp_project(title, description):
	data = {
		'name'			: title,
		'description'	: description
	}

	endpoint = 'projects.json'
	content_type = 'application/json; charset=utf-8'

	url, headers = prepare_request(endpoint, content_type)
	
	r = requests.post(url, headers=headers, json=data)

	if r.status_code == requests.code.created: # Status code: 201 (Created)		
		# https://github.com/basecamp/bc3-api/blob/master/sections/basecamps.md#get-a-basecamp
		
		# TODO: Might need to move following code
		j = r.json()

		# Get Basecamp id
		basecamp_id = j['id']

		# Get vault id
		# https://github.com/basecamp/bc3-api/blob/master/sections/basecamps.md#get-a-basecamp
		for tool in j['dock']:
			if tool['name'] == 'vault':
				vault_id = tool['id']				
				break

		# TODO: Only if files exists in workorder
		# Create attachment
		for file in files:
			sgid = create_attachment(file)

			if sgid:
				# Associate attachment
				upload_attachment(basecamp_id, vault_id, sgid)
			#TODO: Check for success

def create_attachment(file):

	payload = {'name': file.name}

	# Create attachment in Basecamp
	endpoint = 'attachments.json'
	content_type = get_content_type(file)
	url, headers = prepare_request(endpoint, content_type)
	r = requests.post(url, params=payload, headers=headers, files=file)

	if r.status_code == requests.code.created: # Status code: 201 (Created)
		j = r.json()
		return j['attachable_sgid']

	return False

def upload_attachment(basecamp_id, vault_id, sgid):
	data = {
		'attachable_sgid' : sgid
	}

	endpoint = 'buckets/' + basecamp_id + '/vaults/' + vault_id + '/uploads.json'
	url, headers = prepare_request(endpoint)
	r = requests.post(url, headers=headers, json=data)

	if r.status_code == requests.code.created: # Status code: 201 (Created)
		return True

	return False

def add_people_to_project(basecamp_id, users):
	endpoint = 'projects/' + basecamp_id + '/people/users.json'

	user_list = {
		'grant': [user.id for user in users] # TODO: user.id should be Basecamp People IDs
	} 

	url, headers = prepare_request(endpoint, content_type)

	r = requests.put(url, headers=headers, json=user_list)


def prepare_request(endpoint, content_type=None, content_length=None):
	account_id, token = get_account_id_and_token()

	url		= 'https://3.basecampapi.com/' + account_id + '/' + endpoint
	headers = {
		'Authorization'		: 'Bearer ' + token,
		'User-Agent'		: 'Work Order System (webmaster@asicsulb.org)',
		'Content-Type'		: content_type,
		'Content-Length'	: content_length
	}

	return url, headers

def get_content_type(file):
	pass