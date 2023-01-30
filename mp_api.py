import requests
from sys import argv
from datetime import date,timedelta
import csv
import json

keyfile = open('apikey.txt', "r")

API_KEY = keyfile.readline()

keyfile.close()

url = "https://api.mobilepay.dk/v3/reporting/transactions"
headers = {'Authorization' : 'Bearer ' + API_KEY,
            'Content-Type' : 'application/json'}
load_count = 1000

params = {'pagesize' : load_count,
            'pagenumber' : 1}

legal_args = {"-s" : "start date(YYYY-MM-DD)",
             "-e" : "end date(YYYY-MM-DD)", 
             "-o" : "operator for transaction amount filtering(\'>\', \'<\' or \'=\')",
             "-a" : "amount for transactions amount filtering",
             "-d" : "use default values"}

def tomorrow():
    tomorrow = date.today() + timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d")

start_date_def = "1970-1-1"
end_date_def = tomorrow()
operator_def = '>'
amount_def = '0'

legal_args = {"-s" : "start date(YYYY-MM-DD) | Default: %s" % start_date_def,
              "-e" : "end date(YYYY-MM-DD) | Default: %s" % end_date_def, 
              "-o" : "operator for transaction amount filtering(\'>\', \'<\' or \'=\') | Default: \'%c\'" % (operator_def),
              "-a" : "amount for transaction amount filtering | Default: %s" % amount_def,
              "-d" : "use default values"}


def verify_date(date_string, accept_empty) -> bool:

    if not date_string:
        return accept_empty

    date_list = date_string.split("-")
    if len(date_list) != 3:
        return False
    elif len(date_list[0]) != 4:
        return False
    elif int(date_list[1]) < 1 or int(date_list[1]) > 12:
        return False
    elif int(date_list[2]) < 1 or int(date_list[2]) > 31:
        return False
    else:
        return True
    

def amount_limit_test(value, operator, test_value):
    if operator == '>':
        return value >= test_value
    elif operator == '=':
        return value == test_value
    elif operator == '<':
        return value <= test_value
    else:
        return True

def print_dict(dict):
    for key, val in dict.items():
        print(" %s %s" % (key, val))

def parse_args():
    arg_count = len(argv)
    args = {}
    error = False
    i = 1
    while i < arg_count:
        if argv[i] in legal_args:
            if i + 1 < arg_count and not argv[i + 1] in legal_args:
                args[argv[i]] = argv[i + 1]
                i = i + 2
            else:
               if(argv[i] != '-d'): 
                    print("missing argument after %s" % argv[i]) 
                    error = True
               i = i + 1
        else:
            if argv[i] in ["-h", "-help"]:
                print("Available arguments:")
                print_dict(legal_args)
                print("Using no arguments will ask them from the user one by one")
            else:
                print("invalid argument %s" % argv[i])
                print("use -h or -help to see valid arguments")
            error = True
            i = i + 1 
    if error:
        exit(-1)
    return args

def extract_param(args, key):
    if key in args:
        return args[key]
    else:
        return ""


def main():

    args = parse_args()

    if len(argv) == 1:
        startdate = input(legal_args["-s"] + ": ")
        enddate = input(legal_args["-e"] + ": ")
        amount_operator = input(legal_args["-o"] + ": ")
        amount_string = input(legal_args["-a"] + ": ")
    else:
        startdate = extract_param(args, "-s")
          #tomorrow instead of today because api is dumb
        enddate = extract_param(args, "-e")
        amount_operator = extract_param(args, "-o")
        amount_string = extract_param(args, "-a")
    
    #replace empty with default
    startdate = startdate if startdate else start_date_def
    enddate = enddate if enddate else end_date_def
    amount_operator = amount_operator if amount_operator else operator_def
    amount_string = amount_string if amount_string else amount_def

    amount_value = float(amount_string)
    

    if not (verify_date(startdate, True) and verify_date(enddate, True)):
        print("invalid date")
        exit(-1)

    
    params['startdate'] = startdate
    params['enddate'] = enddate
    
    print("requesting transactions between %s and %s where amount %c %d€" % (startdate, enddate, amount_operator, amount_value))
    req = requests.get(url=url, headers=headers, params=params)

    if not req.ok:
        print("request failed with %s %s. \nMessage: %s" % (req.status_code, req.reason, req.json()["message"]))
        with open("error-%s-request.json" % date.today().strftime("%Y-%m-%d"), "w") as errorlog:
            errorlog.write(req.text)  
        exit(-2)
    else:
        print("request success")


    with open("transactions-%s-%s-%de.csv" % (startdate, enddate, amount_value), 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        transactions = req.json()["transactions"]
        total = 0
        for i in range(0, len(transactions)):
            if amount_limit_test(float(transactions[i]["amount"]), amount_operator, amount_value):
                print(transactions[i]["userName"])
                print(transactions[i]["timestamp"].split("T")[0])
                print("---")
                csvwriter.writerow([transactions[i]["userName"], transactions[i]["timestamp"].split("T")[0], transactions[i]["amount"],transactions[i]["message"]])
                total = total + 1
    print("Printed %d out of %d lines" % (total, len(transactions)))          

main()
