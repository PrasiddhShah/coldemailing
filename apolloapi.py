import requests

url = "https://api.apollo.io/api/v1/mixed_companies/search?q_organization_name=voxel"

headers = {
    "accept": "application/json",
    "Cache-Control": "no-cache",
    "Content-Type": "application/json",
    "x-api-key":"4f6xsxg4Gn0llh_D0Vzgcg"
}
response  = requests.post(url,headers=headers)

print(response.text)