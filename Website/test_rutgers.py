import requests

p = {'prompt': 'Im planning to go to Rutgers New Brunswick for a Masters, what do the costs look like?'}
r = requests.post('http://127.0.0.1:5055/api/advisor', json=p, timeout=60)
d = r.json()

print('Status:', r.status_code)
uni_used = d.get('mcp', {}).get('universityCost', {}).get('used')
print('University MCP used:', uni_used)
mode = d.get('mcp', {}).get('universityCost', {}).get('mode')
print('Mode:', mode)

if d.get('universityData'):
    print('University name:', d['universityData'].get('university_name'))
    costs = d['universityData'].get('costs', {})
    print('Tuition:', costs.get('tuition'))
    print('Total annual cost:', d['universityData'].get('estimated_total_annual_cost'))
else:
    print('No university data returned')
    if d.get('universityData') is not None:
        print('Payload:', d.get('universityData'))
