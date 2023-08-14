import requests

class vng:
    
    my_curl = ""
    my_url = ""
    my_secret = ""
    my_ID = ""
    token = ""
    json_body = ""
    

    
    def __init__(self, curl:str, url:str, client_id:str, client_secret:str, json:dict):
        self.my_curl = curl
        self.my_url = url
        self.my_secret = client_secret
        self.my_ID = client_id
        self.json_body = json
        self.token = self.get_access_token()
        #self.token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJlckVaZFpkNkRsc21pdjhsMDZIaVB3bHZYWnotLVlGYXlZcVJiczlxc09rIn0.eyJleHAiOjE2OTE1NTYxNTQsImlhdCI6MTY5MTU1MjU1NCwianRpIjoiOWYzZTk4NmQtNDRmYy00MDk3LWFmYzUtNDczMzA3ZTFhY2E2IiwiaXNzIjoiaHR0cHM6Ly9zaWduaW4udm5nY2xvdWQudm4vYXV0aC9yZWFsbXMvaWFtIiwic3ViIjoiNmYyNWNlZjgtNDlhMy00OWM5LTk2NTktZDdlYjRiZGI0NzZjIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYzllNzg0MTEtZjJhMi00MWJhLWE5ZTQtM2M1NjI2M2MxODFhIiwic2Vzc2lvbl9zdGF0ZSI6ImNlYTUwZWNmLTE4NjYtNGIyZi04ZjY2LWUwMTlhYTY5ZGY5YiIsImFjciI6IjEiLCJzY29wZSI6IiIsInNpZCI6ImNlYTUwZWNmLTE4NjYtNGIyZi04ZjY2LWUwMTlhYTY5ZGY5YiIsImF1dGhBY2NvdW50SWQiOjgzMjgyLCJhdXRoVXNlclR5cGUiOiJpYW0tdXNlciJ9.cJKnx_9AqqiBvz4neGodv8q_oxGivBk9CotPoxogZ52Sw_f3arYXrQcW7mzSW0rFA8SDSWV378-KaP7tgUz9GXF7HeR8M-HbJsIIDxoZSaPveKuXlX0dnybeicCnlyRVjR6rr5SPKPG_Q1jI0Zkl1EMmK--nAnONVg4lmr9G2txIqDoBz3ClOnnEIa6-k-zdY9sDLuWP1dIYN8d9Z_HS5gbS96Thw5QCh6SqbQWcZpa9fsSu_Gq22qvJdkYGbOim7i2iDnOQkKcBjjoQSA36fNMlgpx4cvlYt53CUERrOQQv06Jl_lafLEVriwjkNJpvxqeCXAs0m5RM2cM49-YXrQ'
        
        
    
    def get_access_token(self):
        response = requests.post(
            self.my_url,
            data={"grant_type": "client_credentials"},
            auth=(self.my_ID, self.my_secret),
        )
        self.token = response.json()["access_token"]
        return response.json()["access_token"]
    
    def get_data(self):
        head = {'Authorization': 'Bearer {}'.format(self.token)}
        response = requests.get(self.my_curl, headers=head)
        return response
    
    def post_data(self):
        head = {'Authorization': 'Bearer {}'.format(self.token)}
        response = requests.post(self.my_curl, headers=head, json = self.json_body)
        return response.json()
    
    
    
