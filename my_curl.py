#!/usr/bin/python
import pdb
import subprocess
import re
import time

#dev_id = 'Developer-Id:Bearer: eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1MDQ4MTY5MDUsInJvbGUiOiJhZG1pbiIsImlkIjoiMTk3YjZlYzFkNzZkYjE4NzI5MjMwOWVlOTAwMDEwMWYiLCJ0ZW5hbnQiOiJ0ZW5hbnRfb3JzeGc1YnIiLCJuYW1lIjoidGVzdDEifQ.NaQpBgOaOhsDujiaY3a_F4LuH_mRQ-hesRUbOeWQzRueUds2cy3ejVshap7h7j4zrEP4OgzotaQKuUJGRMPt_A'
#dev_id = 'Developer-Id:Bearer: eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1MDQ4MTY5MDUsInJvbGUiOiJhZG1pbiIsImlkIjoiMTk3YjZlYzFkNzZkYjE4NzI5MjMwOWVlOTAwMDEyYTQiLCJ0ZW5hbnQiOiJ0ZW5hbnRfb3JzeGc1YnMiLCJuYW1lIjoidGVzdDIifQ.BH_0GxW2yOqVk6T_sjWhQs7icZnKtvAmSAYmanmVsOg3O3LYJZ53vv695sfJrup0ELf_7NSFkf021q5Phc0z_Q'

#dev_id = 'Developer-Id:Bearer: eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1MDQ4MTY5MDUsInJvbGUiOiJhZG1pbiIsImlkIjoiMTk3YjZlYzFkNzZkYjE4NzI5MjMwOWVlOTAwMDIwNjUiLCJ0ZW5hbnQiOiJ0ZW5hbnRfb3JzeGc1YnQiLCJuYW1lIjoidGVzdDMifQ.tTAkowRMi6VimGYmtiljj8S1Cm6g54En6VUxL_JqSlAT62R2Wt4rWZ-zQQ2jJ9AcAZRBw1BVcjo_YVapOF2yXw'

dev_id = 'Developer-Id:Bearer: eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1MDQ4MTY5MDUsInJvbGUiOiJhZG1pbiIsImlkIjoiMTk3YjZlYzFkNzZkYjE4NzI5MjMwOWVlOTAwMDI1ZTQiLCJ0ZW5hbnQiOiJ0ZW5hbnRfb3JzeGc1YnUiLCJuYW1lIjoidGVzdDQifQ.gJzpb7D-N0dmcOZWEUWvfXXUZNdX1Lh98lPk6cgNj6PbqngfvfbCk6CdSa2RkjoSBHURJ1QBRlVur75Fj4dfSw'

client_secret = '5wFTkhC2pSUSgBP5'
client_id     = 'RyhLFSYPtzdWLmbxqngNAzmW7WSHY3bZ'

uname = 'shahramX3'
url   = 'https://sandbox.knurld.io/v1/'

url_shahla     = "https://s3-us-west-2.amazonaws.com/qas3bucket/public/Y-O-P.wav"
url_y_o_p_ver  = "https://s3-us-west-2.amazonaws.com/qas3bucket/public/Y-O-P.wav"



def build_verification(verification_list, asked_phrases):
    range = str(verification_list).replace(" ", "")  # compress the string.
    intervals = ''
    for i, p in enumerate(asked_phrases):
        # find all a specific pharse in the range.
        l_word = re.findall("{\"phrase\":\"" + p + ".*?}", range, re.I)
        intervals = intervals + l_word[i] + ','
    return intervals[0:len(intervals) - 1]

def extract_instruction(astring):
    astring = re.sub('[\n ]', '', str(astring))
    phrases = re.findall('phrases":\[(.*?)]', astring)[0]
    phrases = phrases.replace('"', '')
    return phrases.split(',')

def wait_till_status_complete(enrollment_id='', timeout=15):
    cmd = ['curl', '-X', 'GET',
    '-H', dev_id,
    '-H', 'Authorization:Bearer ' + token,
    url + 'enrollments/' + enrollment_id]
    res =  exec_cmd(cmd)
    seconds = 0
    match = re.search('"status": "completed"', res)
    while (match == None and seconds < timeout):
        time.sleep(.1)
        res =  exec_cmd(cmd)
        match = re.search('"status": "completed"', res)
        seconds = seconds + .1
    assert(seconds < timeout), "\n\nget enrollment to complete timed out!!!\n\n" 
    print "\nenrollment get status took: ", str(seconds), " second(s) to complete.\n"
    return res

def exec_cmd(cmd):
    try:
         p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              stdin=subprocess.PIPE)
         out, err = p.communicate()
         #if len(err) > 0 and \
         #   "% Total    % Received % Xferd  Average Speed   Time" not in err:
         #    print "Got an error: ", err
    except  oSError as e:
           print "Got an exception: ", e
           raise OSError(err)
    return out


def get_user():
    cmd = ['curl', '-X', 'GET', url + 'consumers'+ "?limit=999",
           '-H', dev_id,
           '-H', 'Authorization:Bearer ' + token]
    res = exec_cmd(cmd)
    user_ids = re.findall('"href": ".*consumers/(.*)"', res)
    print "found ", len(user_ids), "user(s)"
    # remove admin from the list of consumers.
    res = res.replace('\n', '')
    res = res.replace(" ", "")
    #admin_user = re.findall('"href": ".*consumers/(.*)".*"admin"', res)
    admin_user = re.findall('consumers/(.*)/phrases","role":"admin"', res)
    if admin_user != []:
        admin_user = str(admin_user).split('/')[0]
        admin_user = admin_user.replace("['", "")
        admin_user = admin_user.split('"')
        user_ids.remove(admin_user[0])
    return user_ids


def delete_user(users):
   for user in users:
       print "deleting: ", user
       cmd = ['curl', '-X', 'DELETE', url + 'consumers/' + user,
              '-H', dev_id,
              '-H', 'Authorization:Bearer ' + token]
       res =  exec_cmd(cmd)
       print "\nconsumer delete results:", res, "\n"


def delete_all_user():
    user_ids = get_user()
    while (user_ids != []):
        delete_user(user_ids)
        user_ids = get_user()

#################################
# get the token
#################################
print "\n=== Get access token starts. ==="
cmd = ['curl', '-X', 'POST', url[0:len(url)-3] +
       'oauth/client_credential/accesstoken?grant_type=client_credentials',
       '--header', 'Content-Type:application/x-www-form-urlencoded',
       '--data-urlencode',
       'client_id=' + client_id, '--data-urlencode',
       'client_secret=' + client_secret]
token = exec_cmd(cmd)
token = re.findall('access_token" : "(.*)"', token)[0]
print "token was ===>", token
print "=== Get access token ends. ===\n"


#################################
# get status
#################################
print "\n=== get status starts ==="
cmd = ['curl', '-X', 'GET', url + 'status', 
       '-H', dev_id, '-H', 'Authorization:Bearer ' + token]
res = exec_cmd(cmd)
print "Get Status result:", res
print "=== get status ends ===\n"
delete_all_user()
users = get_user()
delete_user(users)

#################################
# create app_models/application
#################################
print "\n=== create an app-models starts. ==="
cmd = ['curl', '-X', 'POST', url + 'app-models',
'-H', 'Content-Type:application/json',
'-H', dev_id,
'-H', 'Authorization:Bearer ' + token,
'-H', 'mode: passphrase',
'-d', '{"vocabulary":["Yellow", "Orange", "Purple"\
                     ],\
        "verificationLength":3}']
app_model = exec_cmd(cmd)
print "Created app-model:", app_model, "\n"
app_model_id = re.findall('app-models/(.*)"', app_model)[0]
#app_model_id = re.findall('applications/(.*)"', app_model)[0]
print "app-model_id is:", app_model_id
print "=== create an app-models ends. ===\n"


#################################
# get/find an app_model
#################################
print "\n=== get/find an app-models starts.==="
cmd = ['curl', '-X', 'GET', url + 'app-models/' + app_model_id,
'-H',  dev_id, 
'-H', 'Authorization:Bearer ' + token]
res = exec_cmd(cmd)
print "Get app_model results:", res 
print "=== get/find an app-models ends.===\n"


#################################
# update app model
#################################
print "\n=== update an app-models starts. ==="
cmd = ['curl', '-X', 'POST', url + 'app-models/' + app_model_id,
'-H', 'Content-Type:application/json',
'-H', dev_id,
'-H', 'Authorization:Bearer ' + token,
'-d', '{\"threshold\":\"1.6407\"}']
res = exec_cmd(cmd)
print "update app model results:", res
print "=== update an app-models ends. ===\n"


#################################
# Create a consumer
#################################
users = get_user()
delete_user(users)
print "\n=== create a consumer starts. ==="
cmd = ['curl', '-X', 'POST', url + 'consumers',
'-H', 'Content-Type:application/json',
'-H', dev_id,
'-H', 'Authorization:Bearer ' + token,
'-d', '{\"username\":\"' + uname + '\",\"gender\":\"F\",\"password\":\"password\"}']
res = exec_cmd(cmd)
print "Consumer create results:", res, " ", uname
consumer_id = re.findall('consumers/(.*)"', res)[0]
print "consumer_id is:", consumer_id
print "=== create a consumer ends. ===\n"


#################################
# get consumer bug: kdptl-107
#################################
print "\n=== get consumer starts. ==="
cmd = ['curl', '-X', 'GET', url + 'consumers',
'-H', dev_id,
'-H', 'Authorization:Bearer ' + token]
res = exec_cmd(cmd)
print "Get Consumer results:", res
print "=== get consumer ends. ===\n"


#################################
# login as the user.
#################################
print "\n=== login as the user. ==="
cmd = ['curl', '-X', 'POST', url + 'consumers/token',   #'login',
'-H', 'Content-Type:application/json',
'-H', dev_id,
'-H' ,'Authorization:Bearer ' + token,
'-d', '{\"password\":\"password\",\"username\":\"' + uname + '\"}']
res = exec_cmd(cmd)
udev_id = res.replace('{\n  "token": "', '')
udev_id = str(udev_id.replace('"\n}', ''))
print "user dev_id: " + udev_id
print "=== end of login ===\n"


#################################
# enrollment
#################################
print "\n=== enroll ==="
cmd = ['curl', '-X', 'POST', url + 'enrollments',
'-H', 'Developer-Id: Bearer: ' + udev_id,
'-H', 'Authorization:Bearer ' + token,
'-H', 'Content-Type:application/json',
'-d', '{\"consumer\":\"' + url + 'consumers/' + consumer_id + '\", ' +\
       '\"application\":\"' + url + 'app-models/' + app_model_id + '\"}']
res = exec_cmd(cmd)
enrollment_id = re.findall('enrollments/(.*)"', res)[0]
print "\nCreated enrollment id:", enrollment_id, "\n"
print "\n=== end of enroll ===\n"


#################################
# enrollment update
#################################
print "\n=== update enrollment ==="
cmd = ['curl', '-X', 'POST',
'-H', 'Content-Type:application/json',
'-H', 'Developer-Id: Bearer: ' + udev_id,
'-H', 'Authorization:Bearer ' + token,
url + 'enrollments/' + enrollment_id,
'-d', '{\"enrollment.wav\":\"' + url_shahla + '\", \"intervals\":[' +\
'{"phrase":"Yellow","start": 982   , "stop": 1962},' +\
'{"phrase":"Orange","start": 3012  , "stop": 4102},' +\
'{"phrase":"Purple","start": 5452  , "stop": 6292},' +\
'{"phrase":"Yellow","start": 7802  , "stop": 9022},' +\
'{"phrase":"Orange","start": 10392 , "stop": 11532},'+\
'{"phrase":"Purple","start": 12682 , "stop": 13602},'+\
'{"phrase":"Yellow","start": 15102 , "stop": 16261},'+\
'{"phrase":"Orange","start": 17332 , "stop": 18322},'+\
'{"phrase":"Purple","start": 19572 , "stop": 20502}' +\
' ]}' ]
res =  exec_cmd(cmd)
print "\nenrollment update results:", res, "\n"
print "=== end of update enrollment ===\n"


#################################
# enrollment status or get enrollment
#################################
print "\n=== get enrollment of specific enrollment ==="
cmd = ['curl', '-X', 'GET',
'-H',  'Developer-Id: Bearer: ' + udev_id,
'-H', 'Authorization:Bearer ' + token,
url + 'enrollments/' + enrollment_id]
res =  exec_cmd(cmd)
status  = wait_till_status_complete(enrollment_id)
print "\nenrollment status results:", status, "\n"
print "=== end of get specific enrollment ===\n"


#################################
# get enrollments bug: kdptl-107 now fixed and closed.
#################################
print "\n=== start of get enrollment ==="
cmd = ['curl', '-X', 'GET',
'-H', 'Developer-Id: Bearer: ' + udev_id,
'-H', 'Authorization:Bearer ' + token,
url + 'enrollments/']
res =  exec_cmd(cmd)
status = wait_till_status_complete(enrollment_id)
print "\nget enrollments status results:", status, "\n"
print "=== end of get enrollment ===\n"


#################################
# verification
#################################
print "\n=== start of verification ==="
cmd = ['curl', '-X', 'POST',
'-H', 'Content-Type:application/json',
'-H', 'Developer-Id: Bearer: ' + udev_id,
'-H', 'Authorization:Bearer ' + token,
'-d', '{"consumer": "' + url + 'consumers/' + consumer_id + '",\
        "application": "' + url + 'app-models/' + app_model_id + '"}',
url + 'verifications']
res =  exec_cmd(cmd)
print "\nverification create ressults:", res, "\n"
verification_id = re.findall('/verifications/(.*)"', res)[0]
print "Verification_id is:", verification_id, "\n"
print "=== end of verification ===\n"


#################################
# get verification
#################################
print "\n=== get verification ==="
cmd = ['curl', '-X', 'GET',
'-H', 'Content-Type:application/json',
'-H', 'Developer-Id: Bearer: ' + udev_id,
'-H', 'Authorization:Bearer ' + token,
url + 'verifications/' + verification_id]
res =  exec_cmd(cmd)
asked_phrases = extract_instruction(res)
print "\nget verification ressults:", res, "\n"
print "=== end of get verification ===\n"


#################################
# verification update
#################################
print "\n=== start of update verification ==="
phrase_interval_list = [
'{"phrase":"Yellow","start": 982   , "stop": 1962}' ,
'{"phrase":"Orange","start": 3012  , "stop": 4102}' ,
'{"phrase":"Purple","start": 5452  , "stop": 6292}' ,
'{"phrase":"Yellow","start": 7802  , "stop": 9022}' ,
'{"phrase":"Orange","start": 10392 , "stop": 11532}',
'{"phrase":"Purple","start": 12682 , "stop": 13602}',
'{"phrase":"Yellow","start": 15102 , "stop": 16261}',
'{"phrase":"Orange","start": 17332 , "stop": 18322}',
'{"phrase":"Purple","start": 19572 , "stop": 20502}'
]
ordered_list = build_verification(phrase_interval_list, asked_phrases)
cmd = ['curl', '-X', 'POST',
'-H', 'Content-Type:application/json',
'-H', 'Developer-Id: Bearer: ' + udev_id,
'-H', 'Authorization:Bearer ' + token,
'-d', '{"verification.wav": "' + url_y_o_p_ver + '", "intervals":[' +\
ordered_list +\
'] }', url + 'verifications/' + verification_id]
time.sleep(5)
res =  exec_cmd(cmd)
print "\nupdate verification results", res, "\n"
print "=== end of update verification ===\n"

#################################
# get verification
#################################
print "=== start of get verification results ==="
cmd = ['curl', '-X', 'GET',
'-H', 'Content-Type:application/json',
'-H', 'Developer-Id: Bearer: ' + udev_id,
'-H', 'Authorization:Bearer ' + token,
url + 'verifications/' + verification_id]
time.sleep(5)
res =  exec_cmd(cmd)
print "\nget verification result", res, "\n"
print "=== end of get verification results ===\n"


#################################
# delete verification
#################################
print "\n=== delete verification ==="
cmd = ['curl', '-X', 'DELETE',
'-H', 'Content-Type:application/json',
'-H', 'Developer-Id: Bearer: ' + udev_id,
'-H', 'Authorization:Bearer ' + token,
url + 'verifications/' + verification_id]
res =  exec_cmd(cmd)
print "\nDelete verification result", res, "\n"


#################################
# enrollment delete
#################################
print "\n=== delete enrollment ==="
cmd = ['curl', '-X', 'DELETE',
'-H', 'Content-Type:application/json',
'-H', 'Developer-Id: Bearer: ' + udev_id,
'-H', 'Authorization:Bearer ' + token,
url + 'enrollments/' + enrollment_id]
res =  exec_cmd(cmd)
print "\nenrollment delete ressults:", res, "\n"


#################################
# delete the consumer 
#################################
print "\n=== start of delete consumer ==="
cmd = ['curl', '-X', 'DELETE', url + 'consumers/' + consumer_id,
'-H', dev_id,
'-H', 'Authorization:Bearer ' + token]
res =  exec_cmd(cmd)
print "\nconsumer delete results:", res, "\n"
print "=== end of delete consumer ===\n"


#################################
# delete app_models/application
#################################
print "\n=== delete app_models ==="
cmd = ['curl', '-X', 'DELETE', url + 'app-models/' + app_model_id,
'-H', dev_id,
'-H', 'Authorization:Bearer ' + token]
app_model = exec_cmd(cmd)
print "\nCreated app-model:", app_model, "\n"
