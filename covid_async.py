import asyncio
import requests
import aiohttp
import json
from matplotlib import pyplot as plt
loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)
lst = []
areas = ["Yorkshire and The Humber", "South West", "South East", "North West", "North East", "London", "East of England", "East Midlands", "West Midlands"]

endpoint = 'https://api.coronavirus.data.gov.uk/v1/data'
q = asyncio.Queue()


async def get_response(client, url):
    async with client.get(url) as response:
        try:
            assert response.status == 200
        except Exception as e:
            print(e)
            return 
        return await response.json()



async def task_creator(urls):
    print('Adding a task')
    for url in urls:
        await q.put(url)

def build_url(area):
    url = f'{endpoint}' + f'?filters=areaType=region;areaName={area}' + '&structure={"date":"date","areaName":"areaName","areaCode":"areaCode","newCasesByPublishDate":"newCasesByPublishDate","cumCasesByPublishDate":"cumCasesByPublishDate","newDeathsByDeathDate":"newDeathsByDeathDate","cumDeathsByDeathDate":"cumDeathsByDeathDate"}'
    return url

async def getter():
    count = 1
    print('Getting a task')
    print(f'Queue size is {q.qsize()}')
    region = await q.get()
    url = build_url(region)
    data = await get_response(client, url)
    data = data['data'][:30]
    lst.append(data)
    
    print(f'Retrieved region data: {region}')
    count += 1
    q.task_done()



async def main():
    print('Running main tasks')
    producers = asyncio.create_task(task_creator(areas))
    consumers = [asyncio.create_task(getter()) for x in range(0, len(areas))]
    await asyncio.gather(producers)
    await q.join()
    await client.close()
    for consumer in consumers:
        consumer.cancel()

loop.run_until_complete(main())
last_30_dates = [x['date'] for x in lst[0]] # x axis
last_30_cases = []

for x in lst:
    last_30_cases.append([y['newCasesByPublishDate'] for y in x])

fig, ax = plt.subplots(figsize=(12, 7))
x = last_30_dates
y = last_30_cases
labels = ['YH', 'SW', 'SE', 'NW', 'NE', 'LDN', 'EE', 'EM', 'WM']

ax.stackplot(x, y, labels=labels)
chartBox = ax.get_position()
ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.6, chartBox.height])
ax.legend(loc='upper center', bbox_to_anchor=(1.45, 0.8), shadow=True, ncol=1)
plt.title('Last Thirty Days of Cases in England, by Region')
plt.xticks(x, rotation=45, ha='right')
fig.tight_layout()
plt.show()