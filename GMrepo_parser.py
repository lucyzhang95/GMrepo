import requests
import json
import pandas as pd

# Get relative species/genus abundances for all phenotypes
query = {"project_id":"PRJNA447983","mesh_id":""}

# Query data
url = 'https://gmrepo.humangut.info/api/getMicrobeAbundancesByPhenotypeMeshIDAndProjectID'
data = requests.post(url, data=json.dumps(query)).json()
# print(data)

# Get project and disease information
project = data.get("project_info")
# print(project)
disease = data.get("disease_info")

# Get abundance and meta data
abundance_and_meta = pd.DataFrame(data.get("abundance_and_meta_data"))
print(abundance_and_meta.iloc[1])

# query = {"run_id":"DRR042265"}
# url = 'https://gmrepo.humangut.info/api/getFullTaxonomicProfileByRunID'
# data = requests.post(url, data=json.dumps(query)).json()
#
# run = data.get("run")
# print(run)
# # species = pd.DataFrame(data.get("species"))
# # genus = pd.DataFrame(data.get("genus"))
#
#
# query = {"run_id":"ERR475468"}
# url = 'https://gmrepo.humangut.info/api/getFullTaxonomicProfileByRunID'
# data = requests.post(url, data=json.dumps(query)).json()
# run = data.get("run")
# print(run)
# # species = pd.DataFrame(data.get("species"))
# # genus = pd.DataFrame(data.get("genus"))