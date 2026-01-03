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

        asset = [Asset(id=i, roll_id=json_data['id'], url=url) 
                for i, url in enumerate(json_data['images'])]
        assets.append(asset)

        fact = [Fact(id=i, roll_id=json_data['id'], shop_id=shop['shopid'], 
                    price=json_data['price'], available=shop.get('available', 0))
                for i, shop in enumerate(json_data['availability'])]
        facts.append(fact)

    return rolls, assets, facts


if __name__ == "__main__":
    with open("./dags/file.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    res = parse_data(data)
    print(len(res[2]))
