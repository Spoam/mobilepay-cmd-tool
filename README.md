# mobilepay-cmd-tool
Command line tool for making csv files from mobilepay transactions
## How to use
Apikey will be read from the first line of apikey.txt file. The file in question is not included in this repository for obvious reasons

Use commandline argument -h or -help to see list of available arguments. Not using any arguments will ask all parameters from the user. Leaving a parameter empty will use its default value.

The printed csv file contains the following information: Username, timestamp of transactions (YYYY-MM-DD), transaction amount, message
