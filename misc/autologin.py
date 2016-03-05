import ldap
import sys
import os
from urllib import urlopen


def check_credentials(usrname, pwd):
    os.environ['LDAPNOINIT']='1'
    ldapmodule_trace_level = 1
    ldapmodule_trace_file = sys.stderr

    ldap._trace_level = ldapmodule_trace_level

    LDAP_SERVER = "ldap://192.168.10.18:389"
    #LDAP_SERVER = ""
    LDAP_USERNAME = "%s@nsrp.com.vn" % usrname
    LDAP_PASSWORD = pwd

    print(LDAP_USERNAME)

    base_dn = "dc=nsrp, dc=com, dc=vn"
    ldap_filter = "sAMAccountName=%s" % usrname
    attrs = ["displayName", "givenName", "email", "sAMAccountName"]

    try:
        # Build a client
        ldap_client = ldap.initialize(LDAP_SERVER) #, trace_level=ldapmodule_trace_level, trace_file=ldapmodule_trace_file)
        # Perform a synchronous bind
        ldap_client.protocol_version = 3
        ldap_client.set_option(ldap.OPT_REFERRALS,0)
        ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
    except ldap.INVALID_CREDENTIALS:
        ldap_client.unbind()
        print( "Wrong username or password")
        #return "Wrong username or password"
    except ldap.SERVER_DOWN:
        print("AD Server is not availabe")
        #return "AD Server is not availabe"

    r = ldap_client.search(base_dn, ldap.SCOPE_SUBTREE, ldap_filter, attrs)
    #cherrypy.session[usrname] = str(r[0][1]['memberOf'])
    #print(str(r[0][1]['memberOf']))
    #ldap_client.unbind()
    return None

check_credentials("ibm.chuong.mh", "Mhc@1092")

#######################################
#
#######################################

#url = "https://hr-qas.nsrp.com.vn:8000/#Hrm_Main_Web/Home/Dashboard#NewTab"
url = "https://hr-qas.nsrp.com.vn:8000/Home/Logout"

try:
    html = urlopen(url)
    print html
except IOError, e:
    print(IOError.strerror)