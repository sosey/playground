"""hack to make plots for a repo structure, needs cleanup

makes bargraph style plots describing authors and commits for each subdirectory
"""

from glob import glob
import os
import subprocess
import time
import csv

info={}

for dirpath, dnames, files in os.walk("."):
    git="git  log  --pretty=format:'%ad %an'  --date=short"
    gitlog=git.split("  ")
    gitlog.append(dirpath)
    print(dirpath)
    process=subprocess.Popen(gitlog, stdout=subprocess.PIPE)
    out,err = process.communicate()
    results = csv.DictReader(out.decode('utf-8').splitlines(),
                        delimiter=' ', skipinitialspace=True,
                        fieldnames=['date','first','middle','last'])

    counts=dict()
    date = time.strptime("'2009-01-01","'%Y-%m-%d")
    counts['date'] = date
    total_commits=0
    for row in results:
        total_commits+=1
        names=[]
        names.append(row['first'])
        names.append(row['middle'])
        names.append(row['last'])
        name="".join([name for name in names if name is not None])
        if name not in counts.keys():
            counts[name]=1
        else:
            counts[name] +=1
        cdate = time.strptime(row['date'],"'%Y-%m-%d")
        if cdate > counts['date']:
            counts['date']=cdate

    #save information for directory
    counts['date']=time.strftime('%Y-%m-%d',counts['date'])
    counts['total_commits']=total_commits
    info[dirpath]=counts


#make a contribution plot by directory for the authors and oommits
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_pdf import PdfPages

import matplotlib.pyplot as plt
plt.rcdefaults()
import numpy as np
import datetime
pp = PdfPages('gitlog_stats.pdf')
maturity=[]
package=[]

for key in info:
    authors=[]
    commits=[]
    for author in info[key].keys():
        if author is not 'date' and author is not None and author is not 'total_commits':
            authors.append(author)
            commits.append(info[key][author])

    ypos=np.arange(len(authors))
    plt.clf()
    plt.figure(figsize=(10.5, 8), dpi=100)
    plt.barh(ypos, np.asarray(commits), align='center', alpha=0.4)
    plt.yticks(ypos, authors)
    plt.xlabel('Number of Commits')
    #make a rough maturity estimage, this should really include some measure of open issues and time-frame of development
    if len(authors) > 0:
        scaled=(info[key]['total_commits'] / len(authors))/len(info['.'].keys())
        maturity.append(scaled)
        package.append(key)
    else:
        scaled=0
    plt.title('Total commits ({0}):{1}, last:{2} maturity: {3}'.format(key,info[key]['total_commits'],info[key]['date'], scaled))
    plt.tight_layout()
    pp.savefig()
    plt.close(plt.gcf())

#make a plot of the maturity values for the main packages
mat={p:v for p,v in zip(package,maturity) if p.count('/') < 2}
package=[]
maturity=[]
for key in mat:
    package.append(key)
    maturity.append(mat[key])

plt.clf()
plt.figure(figsize=(10.5, 8), dpi=100)
ypos=np.arange(len(mat.keys()))
plt.barh(ypos, np.asarray(maturity), align='center', alpha=0.4)
plt.yticks(ypos, package)
plt.xlabel('Package commits / Number of authors / Total Commits')
plt.title('Rough measure of package maturity')
plt.tight_layout()
pp.savefig()
plt.close(plt.gcf())

d=pp.infodict()
d['CreationDate'] = datetime.datetime.today()
d['Subject']='Github modification history'
pp.close()
