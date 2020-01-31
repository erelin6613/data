import pandas as pd
from tqdm import tqdm

results = pd.read_csv('task_companies_results.csv')
name_col = 'Company name'


def clean_sm_links(frame):

	social_media_cols = ['facebook', 'instagram', 'linkedin', 
						'pinterest', 'twitter', 'youtube']
	for ind in tqdm(frame.index):
		for col in social_media_cols:
			if str(frame.loc[ind, col]) != 'nan':
				if frame.loc[ind, col].startswith('https://'+col):
					frame.loc[ind, col] = frame.loc[ind, col].replace('https://', 'https://www.')
				if frame.loc[ind, col].startswith('http://'+col):
					frame.loc[ind, col] = frame.loc[ind, col].replace('http://', 'https://www.')
				if frame.loc[ind, col].startswith('https://'+col) == False:
					try:
						frame.loc[ind, col] = 'https://www.'+col+ \
						frame.loc[ind, col].split(col)[1]
					except Exception:
						frame.loc[ind, col] = None
						continue
				try:
					assert len(frame.loc[ind, col].split('www.')) > 2
					#print(frame.loc[ind, col].split('www.'))
					frame.loc[ind, col] = 'https://www.'+frame.loc[ind, col].split('www.')[-1]
				except Exception:
					pass

				if str(frame.loc[ind, col]) == 'https://www.'+col+'.com' or\
				str(frame.loc[ind, col]) == 'https://www.'+col+'.com/' or \
				str(frame.loc[ind, col]) == 'http://www.'+col+'.com' or \
				str(frame.loc[ind, col]) == 'http://www.'+col+'.com/':
					frame.loc[ind, col] = None
				try:
					assert 'post' not in frame.loc[ind, name_col].lower()
					if 'post' in frame.loc[ind, col]:
						frame.loc[ind, col] = None
				except Exception:
					pass



	return frame

def clean_meta(frame, link_cols):

	for ind in tqdm(frame.index):
		for col in link_cols:
			if str(frame.loc[ind, col]) != 'nan':
				try:
					if 'google' in frame.loc[ind, col] or \
					'%' in frame.loc[ind, col]:
						frame.loc[ind, col] = None
						continue
					try:
						assert len(frame.loc[ind, col].split('?')) > 1
						frame.loc[ind, col] = frame.loc[ind, col].split('?')[0]
					except Exception:
						pass

					try:
						assert len(frame.loc[ind, col].split('#')) > 1
						frame.loc[ind, col] = frame.loc[ind, col].split('#')[0]
					except Exception:
						pass
				except Exception:
					frame.loc[ind, col] = None

				if len(str(frame.loc[ind, col])) > 75:
					frame.loc[ind, col] = None
	return frame


def clean_delivery_links(frame):


	for ind in tqdm(frame.index):
		if 'membership' in str(frame.loc[ind, 'shipping_url']).lower() or \
		'leadership' in str(frame.loc[ind, 'shipping_url']).lower():
			frame.loc[ind, 'shipping_url'] = None

	return frame


def remove_login_required(frame, cols):

	for ind in tqdm(frame.index):
		for col in cols:
			if str(frame.loc[ind, col]) != 'nan':
				if 'login' in str(frame.loc[ind, col]).lower():
					frame.loc[ind, col] = None

	return frame




results = clean_sm_links(results)
results = clean_meta(results, ['facebook', 'instagram', 'linkedin', 
							'pinterest', 'twitter', 'youtube',
							'contact_link', 'return_policy_url',
							'shipping_url', 'faq_url', 
							'privacy_policy_url',
							'terms and conditions_url', 'warranty_url'])

results = remove_login_required(results, ['contact_link', 'return_policy_url',
							'shipping_url', 'faq_url', 
							'privacy_policy_url',
							'terms and conditions_url', 'warranty_url'])

results = clean_delivery_links(results)

#results.to_csv('check.csv')
results.to_csv('task_companies_results.csv')