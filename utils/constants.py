grades = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "F": 0,
    "Ab": 0,
}

string_dict = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 4,
    "F": 5,
    "G": 6,
    "H": 7,
    "J": 8,
    "K": 9,
    "L": 10,
    "M": 11,
    "N": 12,
    "P": 13,
}

payloads = [
    "&etype=r17&result=null&grad=null&type=intgrade&htno=",
    "&etype=r17&result=gradercrv&grad=null&type=rcrvintgrade&htno=",
]

headers = {
    "Upgrade-Insecure-Requests": "1",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}

codes = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
