from datetime import datetime
import dateutil.parser
import pickle
import requests
import pandas as pd


class GitHealthModel:
    
    def __init__(self, github_token):
        self._model = pickle.load(open("githeathmodel.p", "rb"))
        self.headers = {
            'Authorization': 'token ' + github_token
        }
    
    def _transform_repo(self, username, repo):
        res = requests.get("https://api.github.com/repos/" + username + "/" + repo, headers=self.headers)
        
        if res.status_code != 200:
            return False
        
        request_key = username + "_" + repo
        
        user_repo = res.json()

        return self._from_json(user_repo)
    
    def _from_json(self, json):
        repo_df = pd.io.json.json_normalize(json)

        repo_num_df = repo_df.select_dtypes(include=['number'])

        repo_num_df = repo_num_df.drop(["organization.id", "id", "open_issues_count", "owner.id", "watchers_count", "network_count", "subscribers_count"], axis=1, errors='ignore')

        commit_url = json['commits_url'][:-6]

        commit_res = requests.get(commit_url, headers=self.headers)

        repo_num_df['commits'] = len(commit_res.json())
        
        return repo_num_df
    
    def team_health(self, org):
        res = requests.get("https://api.github.com/orgs/" + org + "/repos?per_page=10", headers=self.headers)
        
        if res.status_code != 200:
            return False
        
        org_repos = res.json()
        
        healths = []
        
        for repo in org_repos:
            df = self._from_json(repo)
            
            if df is not False:
                prediction = self._predict_health(df)
                
                health = {
                    'name': repo['name'],
                    'health': prediction,
                    'url': "https://github.com/" + repo['full_name']
                }
                
                healths.append(health)
                
        return healths
    
    def _predict_health(self, df):
        prediction = self._model.predict(df)[0]
        
        return min(round((prediction / 250) * 100, 2), 100)
    
    def health(self, username, repo):
        df = self._transform_repo(username, repo)
        
        if(df is False):
            print("Invalid username or repository")
            return False
        
        return self._predict_health(df)
        
    def issue_count(self, username, repo):
        res = requests.get("https://api.github.com/repos/" + username + "/" + repo, headers=self.headers)
        
        if res.status_code != 200:
            return False
    
        user_repo = res.json()
        
        return user_repo['open_issues_count']
    
    def dump(self, username, repo):
        res = requests.get("https://api.github.com/repos/" + username + "/" + repo, headers=self.headers)
        
        if res.status_code != 200:
            return False
        
        user_repo = res.json()
        
        keys = list(filter(lambda k: k[-3:] != 'url' and k != 'owner' and k != 'organization', user_repo))
        
        dump_repo = {}
        
        for key in keys:
            dump_repo[key] = user_repo[key]
        
        return dump_repo
        
  
    def last_updated(self, username, repo):
        res = requests.get("https://api.github.com/repos/" + username + "/" + repo, headers=self.headers)
        
        if res.status_code != 200:
            return False
    
        user_repo = res.json()
        
        updated_at = user_repo['updated_at']
        
        updated_dt = dateutil.parser.parse(updated_at)
        
        return str((datetime.now() - updated_dt.replace(tzinfo=None)).days) + " days ago"
        
    def star_count(self, username, repo):
        res = requests.get("https://api.github.com/repos/" + username + "/" + repo, headers=self.headers)
        
        if res.status_code != 200:
            return False
    
        user_repo = res.json()
        
        return user_repo['stargazers_count']
        
        
        
        