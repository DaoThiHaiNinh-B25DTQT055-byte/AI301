import json
from agent_core import DataLoader, MinhAnSalesAgent

p, s, pol = DataLoader.load_default_data()
agent = MinhAnSalesAgent(p, s, pol)

with open('data/sample_requests.json', encoding='utf-8') as f:
    samples = json.load(f)

for item in samples:
    print('Testing:', item['id'], '|', item['title'])
    res = agent.process_request(item['raw_text'], custom_opp_id=item['id'])
    print('  Status:', res['status'])
    print('  Step reached:', res['step'])
    if res['sales_rep']:
        print('  Assigned Sales Rep:', res['sales_rep']['FullName'])
    if res['evaluation']:
        print('  Total Net:', f"{res['evaluation']['total_final_amount']:,.0f} VND")
        print('  Decision Badge:', res['evaluation']['decision_badge'])
        print('  Approval Level:', res['evaluation']['approval_level'])
        if res['evaluation']['leadtime_warnings']:
            print('  Leadtime warnings:', res['evaluation']['leadtime_warnings'])
        if res['evaluation']['stock_warnings']:
            print('  Stock warnings:', res['evaluation']['stock_warnings'])
    if res['clarification_draft']:
        print('  Clarification email preview:', res['clarification_draft'][:120] + '...')
    print('-' * 60)
