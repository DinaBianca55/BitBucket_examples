import requests, dateutil.parser
import os
import os.path
import shutil

# parameters to pass in
tmpDownloadDir = "c:\\tempfolder"
baseUrl = "<YOUR-GIT-REPOSITORY>"       
username = "<USERNAME>"
password = "PASSWORD>"


baseUrlv1 = baseUrl + "/rest/api/1.0"


def init():
  try:
    shutil.rmtree(tmpDownloadDir)
  except OSError:
    pass


def downloadFile(projName, repoName, file):
  serviceURL= "{base}/projects/{projName}/repos/{repoName}/browse/{file}?raw".format(projName=projName,repoName=repoName,base=baseUrl,file=file)
  response = requests.get(serviceURL, auth=(username, password), allow_redirects=True)
  outfile = tmpDownloadDir + "\\" + file.replace("/", "\\")
  outdir = os.path.dirname(outfile)
  try:
    os.makedirs(outdir)
  except OSError:
    pass
  open(outfile, 'wb').write(response.content)

def getProjectContents(projName, repoName,prefix):
  baseURL= "{base}/projects/{projName}/repos/{repoName}/browse/{prefix}".format(projName=projName,repoName=repoName,base=baseUrlv1,prefix=prefix)
  serviceURL= baseURL
  response = requests.get(serviceURL, auth=(username, password))
  paths = response.json()
  fileList = []
  while 1:
    for path in paths['children']["values"]:
      name = path["path"]["name"]
      fullname = prefix + name
      if (path["type"] == "DIRECTORY"):
        childFileList = getProjectContents(projName, repoName, fullname + "/")
        fileList.extend(childFileList)
      else:
        fileList.append(fullname);
    if paths['children']['isLastPage']:
      break;
    nextStart = paths['nextPageStart']
    serviceURL = (baseURL +"?start={nextStart}").format(start=start)
    response = requests.get(serviceURL, auth=(username, password))
    paths = response.json()
  return fileList

def getRepos(projectname):
  repoNames=[]
  repoNameProjectNameMap={}
  start = 0
  baseURL = "{base}/repos/".format(base=baseUrlv1)
  urlExtender = "?"
  if (projectname):
    baseURL = (baseURL + "?projectname={projectname}").format(projectname = projectname);
    urlExtender = "&"
  serviceURL = baseURL
  response = requests.get(serviceURL, auth=(username, password))
  repos = response.json()
  while 1:
    for repo in repos['values']:
      repoName = repo['name'];
      projName = repo['project']['name']
      repoNames.append(repoName)
      repoNameProjectNameMap[repoName] = projName
    if repos['isLastPage']:
      break;
    start = repos['nextPageStart']
    serviceURL = (baseURL + urlExtender + "start={startValue}").format(startValue=start)
    response = requests.get(serviceURL, auth=(username, password))
    repos = response.json()
  return repoNameProjectNameMap

def testGetProjectContents(project, repo):
  files = getProjectContents(project, repo, "")
  for file in files:
    print "#### Project ", project, " contains ", file

def testDownload(project, repo):
  files = getProjectContents(project, repo, "")
  for file in files:
    downloadFile(project, repo, file)
  
def testGetRepos(project):
  repoProjectMap = getRepos(project);
  for repo,project in repoProjectMap.iteritems():
    print "Project ", project, " found in repo ", repo
  print len(repoProjectMap)



init()
#testGetRepos("YOURPROJECT")
#testGetProjectContents("YOURPROJECT", "YOURREPO")
testDownload("YOURPROJECT", "YOURREPO")
