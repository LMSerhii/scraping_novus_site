import csv
import json

import requests
import aiohttp
import asyncio
import aiofiles
import datetime

from aiocsv import AsyncWriter
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


async def collect_data_novus(novus_shop=28):
    """ """
    cur_time = datetime.datetime.now().strftime("%m_%d_%Y")
    ua = UserAgent()
    cookies = {
        "novus_shop": f"{novus_shop}"
    }

    headers = {
        "accept": "text/html, */*; q=0.01",
        "user-agent": ua.random
    }

    response = requests.get(url="https://novus.ua/sales.html", headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, "lxml")
    shop_address = soup.select_one('i.icon-location').next_sibling

    all_data = {}
    data = []

    async with aiofiles.open(f"shop_address_{novus_shop}_result_{cur_time}.csv", "w") as file:
        writer = AsyncWriter(file)
        await writer.writerow(
            (
                shop_address,
                ""
            )
        )
    async with aiofiles.open(f"shop_address_{novus_shop}_result_{cur_time}.csv", "a") as file:
        writer = AsyncWriter(file)
        await writer.writerow(
            (
                "Название",
                "Ссылка",
                "Период акции",
                "Старая цена",
                "Скидка",
                "Новая цена "
            )
        )

    async with aiohttp.ClientSession() as session:

        count = 0
        count_cards = 0
        while True:

            url = f"https://novus.ua/sales.html?p={count + 1}"
            response = await session.get(url=url, headers=headers, cookies=cookies)

            # with open("data/les_20/html/index.html", "w") as file:
            #     file.write(await response.text())
            #
            # with open("data/les_20/html/index.html", "r") as file:
            #     res = file.read()
            #
            # soup = BeautifulSoup(res, "lxml")

            soup = BeautifulSoup(await response.text(), "lxml")


            cards = soup.find("ol", class_="products list items product-items").find_all("li")

            for card in cards:

                link = card.find("a", class_="product-item-link").get('href').strip()
                name = card.find("a", class_="product-item-link").text.strip()

                try:
                    sale_date = card.find("div", class_="mb-time-countdown-container").text.strip()
                except Exception as ex:
                    pass

                try:
                    old_price = float(card.find("span", class_="special-price").find("span", class_="old-price"). \
                                      find("span", class_="price-wrapper").get("data-price-amount"))
                except Exception as ex:
                    pass
                try:
                    new_price = float(card.find("span", class_="special-price").find("span", class_="old-price"). \
                                      find_next_sibling().find("span", class_="price-wrapper").get("data-price-amount"))
                except Exception as ex:
                    pass

                try:
                    price_amount = f"{round(((old_price - new_price) / old_price) * 100)}%"

                except Exception as ex:
                    pass

                data.append(
                    {
                        "name": name,
                        "link": link,
                        "sale_date": sale_date,
                        "old_price": old_price,
                        "new_price": new_price,
                        "price_amount": price_amount
                    }
                )

                async with aiofiles.open(f"shop_address_{novus_shop}_result_{cur_time}.csv", "a") as file:
                    writer = AsyncWriter(file)
                    await writer.writerow(
                        (
                            name,
                            link,
                            sale_date,
                            old_price,
                            price_amount,
                            new_price
                        )
                    )

                # print(f" # {name} - {link}\n{sale_date}\n{old_price}\n{new_price}\n{price_amount}")

            print(f"---------------------------- Page # {count + 1} is done------------------------------------------")

            # if len(cards) < 12:
            #     break

            if count == 2:
                break
            count_cards += len(cards)
            count += 1
    all_data['shop_address'] = shop_address
    all_data["shop_data"] = data
    print(count_cards)

    with open(f"shop_address_{novus_shop}_result_{cur_time}.json", "w") as file:
        json.dump(all_data, file, indent=4, ensure_ascii=False)


async def main():
    await collect_data_novus(novus_shop=29)


if __name__ == '__main__':
    asyncio.run(main())
