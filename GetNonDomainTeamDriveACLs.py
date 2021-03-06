#!/usr/bin/env python
"""
# Purpose: Delete all drive file ACLs for Team Drives shared outside of a list of specified domains
Note: This script requires advanced GAM with Team Drive support: https://github.com/taers232c/GAMADV-XTD
# Usage:
# 1: Get all Team Drives
#  $ gam redirect csv ./teamdrives.csv print teamdrives
# 1: Get ACLs for all Team Drives
#  $ gam redirect csv ./teamdriveacls.csv multiprocess csv ./teamdrives.csv gam print drivefileacls teamdriveid ~id
# 2: From that list of ACLs, output a CSV file with headers "teamDriveId,permissionId,role,type,emailAddress"
#    that lists the driveFileIds and permissionIds for all ACLs except those from the specified domains.
#    (n.b., role, type, emailAddress and title are not used in the next step, they are included for documentation purposes)
#  $ python GetNonDomainTeamDriveACLs.py ./teamdriveacls.csv deletetdacls.csv
# 3: Inspect deletetdacls.csv, verify that it makes sense and then proceed
# 4: Delete the ACLs
#  $ gam redirect stdout ./deletetdacls.out multiprocess redirect stderr stdout multiprocess csv deletetdacls.csv gam delete drivefileacl teamdriveid "~teamDriveId" "~permissionId"
"""

import csv
import re
import sys

email_n_address = re.compile(r"permissions.(\d+).emailAddress")
# Substitute your domain(s) in the list below, e.g., domainList = ['domain.com',] domainList = ['domain1.com', 'domain2.com',]
domainList = ['domain.com',]

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['teamDriveId', 'permissionId', 'role', 'type', 'emailAddress'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rbU')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for k, v in row.iteritems():
    mg = email_n_address.match(k)
    if mg and v:
      perm_group = mg.group(1)
      if row['permissions.{0}.domain'.format(perm_group)] not in domainList:
        outputCSV.writerow({'teamDriveId': row['id'],
                            'permissionId': 'id:{0}'.format(row['permissions.{0}.id'.format(perm_group)]),
                            'role': row['permissions.{0}.role'.format(perm_group)],
                            'type': row['permissions.{0}.type'.format(perm_group)],
                            'emailAddress': v})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
