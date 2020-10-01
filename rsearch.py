import re

# pattern for school name in subject
executive_summary = r'(:\s(.+)\sE)'
# executive_summary.group(2) is school name
# pattern for date in subject
date_of_report = r'(([A-Z][a-z]{2})\s\d,\s(\d{4}))'
# date_of_report.group(2) # is month
# date_of_report.group(3) # is Year
# pattern for Printer groups summary in subject
printer_groups = r'(P[a-z].+- (s[a-z]{6}[A-Z]{3}?|s[a-z]{6}))'

string1 = 'Automated report: Sylvan Hills North Executive summary (Monthly, Jul 1, 2020 to Jul 31, 2020, PDF)'
string2 = 'Automated report: Printer groups - summaryCVS (Monthly, Jul 1, 2020 to Jul 31, 2020, CSV)'
string3 = 'Automated report: Printer groups - summary (Monthly, Jul 1, 2020 to Jul 31, 2020, PDF)'
string4 = 'Automated report: Bates Executive summary (Monthly, Jul 1, 2020 to Jul 31, 2020, PDF)'

strings = [string1, string2, string3, string4]
patterns = [executive_summary, date_of_report, printer_groups]

#for string in strings:
#    for pattern in patterns:
#        result = re.search(pattern, string)
#        if result != None:
#            if string == string1 and pattern ==executive_summary:
#                print(pattern + result.group(2))
#            elif string == string2:
#                print(pattern + result.group(1))
#                print(pattern + result.group(2))
#            elif string == string3:
#                print(pattern + result.group(2))
#            else:
#                print(pattern + result.group(1))


for pattern in patterns:
    result = re.search(pattern, string4)
    if result != None:
        sch = result.group(1)
        print(sch)