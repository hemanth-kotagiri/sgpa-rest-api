from bs4 import BeautifulSoup
import os

with open("result.html", "r", encoding="utf-16") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

tables = soup.find_all('table')
# print(tables[0].tbody)
data = []

for element in list(tables[0].tbody):
    for row in element:
        for td in row:
            for b in td:
                if type(b) != str:
                    data.append(str(b.string).replace("\n", "").strip())

student = dict(zip([data[i].replace(":", "") for i in range(len(data)) if i % 2 == 0], [data[j] for j in range(1, len(data)) if j % 2 != 0]))

for key, value in student.items():
    print(key, value)
