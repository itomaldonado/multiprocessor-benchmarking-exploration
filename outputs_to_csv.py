import os, re, csv

# Variables for the program, al dirs need to end with a '/'
benchmark_dir = './'
outputs_dir = 'outputs/'
csv_output_dir =  'csv/'
csv_output_file = 'npb-benchmark-all-output.csv'
csv_total_output_file = 'npb-benchmark-total-output.csv'
fieldnames = ['program', 'class', 'threads', 'run', 'section', 'section time', 'section percentage', 'total time']
total_fieldnames = ['program', 'class', 'threads', 'run', 'time']
filename_regex = '^([a-z]{2})\.([A-Z])\.x.T([1-9]+)\.run([0-9]+)\.out$'

# Different regex to capture total time, one is more accurate but depends on the "timerflag" to be on.
total_acc_time_regex = '^ *Time in seconds *= *([0-9]+\.[0-9]+) *$'
total_acc_time_group = 1
total_no_acc_time_regex = '^.*(total|benchmk|Total execution|Total time) *\)? *\: *([0-9]+\.[0-9]{3}).*$'
total_no_acc_time_group = 2

# Regex to extract all sections
section_time_regex = {
  'bt': '^(?! +total) +([A-Za-z0-9]+) *\)? *\: *([0-9]+\.[0-9]{3}) *\( *([0-9]+\.[0-9]+)\%\).*$',
  'cg': '^(?! +benchmk|!? +init) +([A-Za-z0-9]+) *\)? *\: *([0-9]+\.[0-9]{3}) *\( *([0-9]+\.[0-9]+)\%\).*$',
  'ep': '^(?! +Total time) +([A-Za-z0-9 ]+) *\)? *\: *([0-9]+\.[0-9]{3}) *\( *([0-9]+\.[0-9]+)\%\).*$',
  'ft': '^ * timer *[0-9]+\( *(?!total)([A-Za-z0-9]+) *\) *\: *([0-9]+\.[0-9]{4}) *\( *([0-9]+\.[0-9]+)\%\).*$',
  'is': '^(?! +Total execution) +([A-Za-z0-9 ]+) *\)? *\: *([0-9]+\.[0-9]{3}) *\( *([0-9]+\.[0-9]+)\%\).*$',
  'lu': '^(?! +total) +([A-Za-z0-9]+) *\)? *\: *([0-9]+\.[0-9]{3}) *\( *([0-9]+\.[0-9]+)\%\).*$',
  'mg': '^(?! +benchmk) +([A-Za-z0-9]+) *\)? *\: *([0-9]+\.[0-9]{3}) *\( *([0-9]+\.[0-9]+)\%\).*$',
  'sp': '^(?! +total) +([A-Za-z0-9]+) *\)? *\: *([0-9]+\.[0-9]{3}) *\( *([0-9]+\.[0-9]+)\%\).*$'
}


# Crete the csv output folder if needed...
if not os.path.exists(benchmark_dir + csv_output_dir):
  os.makedirs(benchmark_dir + csv_output_dir)

with open(benchmark_dir + csv_output_dir + csv_output_file, 'wb') as csv_out, open(benchmark_dir + csv_output_dir + csv_total_output_file, 'wb') as csv_total_out: # Open the output csvs
  # Open dictionary writer and add the header labels
  writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
  writer.writeheader()
  total_writer = csv.DictWriter(csv_total_out, fieldnames=total_fieldnames)
  total_writer.writeheader()

  # Go through all .out files, parse them and add them to the csv file.
  for out_filename in os.listdir(outputs_dir):
    if out_filename.endswith(".out"):
      # if the file size is > 0 we check the contents, if not we skip it
      print out_filename +' --> Size: ' + str(os.stat(benchmark_dir + outputs_dir + out_filename).st_size)
      if os.stat(benchmark_dir + outputs_dir + out_filename).st_size > 0:
        with open(benchmark_dir + outputs_dir + out_filename, 'rb') as out_file:
          # create template row, we'll fill it below
          row_to_write = {
          'program': None,
          'class': None,
          'threads': None,
          'run': None,
          'section': None,
          'section time': None,
          'section percentage': None,
          'total time': None,
          }

          total_row_to_write = {
          'program': None, 
          'class': None, 
          'threads': None, 
          'run': None, 
          'time': None
          }

          # First get the information from the file name
          m = re.search(filename_regex, out_filename)
          row_to_write['program'] = m.group(1).upper()
          row_to_write['class'] = m.group(2)
          row_to_write['threads'] = m.group(3)
          row_to_write['run'] = m.group(4)
          total_row_to_write['program'] = m.group(1).upper()
          total_row_to_write['class'] = m.group(2)
          total_row_to_write['threads'] = m.group(3)
          total_row_to_write['run'] = m.group(4)

          # Read in the file
          data = out_file.read()

          # Extract the total time of the run, use high-accuracy first
          # if it fails, fall back to low accuracy (should always be there)
          m = re.search(total_acc_time_regex, data, re.MULTILINE)
          group_index = total_acc_time_group
          if m is None:
            m = re.search(total_no_acc_time_regex, data, re.MULTILINE)
            group_index = total_no_acc_time_group

          row_to_write['total time'] = m.group(group_index)
          total_row_to_write['time'] = m.group(group_index)

          # write to total csv since we got everything for it
          total_writer.writerow(total_row_to_write)

          # extract section time for each type
          iterator = None
          for k in section_time_regex:
            if out_filename.startswith(k):
              iterator = re.finditer(section_time_regex[k], data, re.MULTILINE)
              break

          for m in iterator:
            row_to_write['section'] = m.group(1).strip()
            row_to_write['section time'] = m.group(2)
            row_to_write['section percentage'] = m.group(3)
            writer.writerow(row_to_write) # Write the row
print 'Done.'

