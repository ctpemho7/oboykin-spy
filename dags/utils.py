################################### FUNCTIONS ################################### 
import json

from schema import Roll, Asset, Fact


def parse_data(data):
    rolls = []
    assets = []
    facts = []

    for json_data in data["items"]:
        roll = Roll(**json_data)
        rolls.append(roll)

        for i, url in enumerate(json_data['images']):
            asset = Asset(id=i, roll_id=roll.id, url=url) 
            assets.append(asset)


        for i, shop in enumerate(json_data['availability']):
            avaible_count = shop.get('available', 0)
            if avaible_count != 0:        
            # ВАЖНО: фильтруем на этапе чтения данных
                fact = Fact(id=i, roll_id=roll.id, shop_id=shop['shopid'], 
                            price=json_data['price'], available=avaible_count)
                facts.append(fact)

    return rolls, assets, facts


def get_all_vendors_and_ids(data):
    vendors = {}
    for v in data["items"]:
        v = v["vendor"]
        vendors[v["id"]] = v["name"]
    print(vendors)
    print(len(vendors))

def count_rolls(data):
    print(len(data['items']))

def count_facts(data):
    count = 0
    for item in data["items"]:
        for availability in item["availability"]:
            if availability.get("available", 0):
                count += 1
    print(count)

if __name__ == "__main__":
    with open("./dags/file.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    res = parse_data(data)
    count_rolls(data)
    count_facts(data)
    print(len(res[0]))
    print(len(res[1]))
    print(len(res[2]))
    # get_all_vendors_and_ids(data)
