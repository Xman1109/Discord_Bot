
import random
import time
import pandas as pd

path = "G:/GitHub-Repos/Stockbot_PY/src/"

old_price = pd.read_csv(path + "data/prices.csv")
while True:
    time.sleep(300)
    for i in old_price:
        new_price = ""
        print(old_price[i][0])
        r = random.randint(-5, 5)
        print(old_price[i][0])
        new_price = old_price[i][0] + r
        print(old_price[i][0])
        old_price[i][0] = new_price
        print(old_price[i][0])
        old_price.to_csv(path + "data/prices.csv",
                         header=True, index=None)
        print(old_price[i][0])
