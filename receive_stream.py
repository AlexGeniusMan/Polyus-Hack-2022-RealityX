import requests

r = requests.get('http://localhost:8003/api/app/stream', stream=True)

lines = r.iter_lines()
# Save the first line for later or just skip it

first_line = next(lines)

for line in lines:
    print(line)

# for line in r.iter_lines():
#     print(line)
