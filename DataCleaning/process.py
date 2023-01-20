import csv
import re
from dateutil.parser import parse

class ColumnTypeAnalyzer:
  def __init__(self, csv_file):
    self.csv_file = csv_file
    self.column_types = {}
    self.schema = {}
  
  def analyze(self):
    with open(self.csv_file, 'r') as f:
      reader = csv.DictReader(f)
      for row in reader:
        for i, value in enumerate(row.values()):
          if reader.line_num == 2:
            self.column_types[i] = {}
          if value:
            data_type = self.get_data_type(value)
            if data_type in self.column_types[i]:
              self.column_types[i][data_type] += 1
            else:
              self.column_types[i][data_type] = 1
    self.determine_schema()
  
  def get_data_type(self, value):
    if value.isdigit() or value.lstrip("-").isdigit():
      return 'int'
    elif '.' in value and value.replace('.','',1).lstrip("-").isdigit():
      return 'float'
    elif re.match(r'\d{4}-\d{2}-\d{2}', value):
      return 'date'
    elif re.match(r'\d{2}:\d{2}:\d{2}', value):
      return 'time'
    elif value in ["na","Na","nA","NA","Nan","NaN","None",""]:
      return 'None'
    elif value in ["true","True","1","false","False","0"]:
      return "bool"
    else:
      return 'str'
  
  def determine_schema(self):
    for i, types in self.column_types.items():
      most_common_type = max(types, key=types.get)
      self.schema[i] = most_common_type

  def convert_value(self,value, data_type):
    if data_type in ["date","time"]:
        try:
          return parse(value)
        except:
          return value
    try:
      return eval(data_type)(value)
    except:
      return value

  def convert_csv(self):
    with open(self.csv_file, 'r') as f:
      reader = csv.DictReader(f)
      with open("output.csv","w") as o:
        writer = csv.DictWriter(o, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
          converted_row = {key: self.convert_value(value, self.schema[i]) for i, (key, value) in enumerate(row.items())}
          writer.writerow(converted_row)




analyzer = ColumnTypeAnalyzer('data.csv')
analyzer.analyze()
print(analyzer.schema)
analyzer.convert_csv()