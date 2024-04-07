import pandas as pd
from datetime import datetime
from shape import shape_utils

@shape_utils.shape({
  "folder": {
    "datejoinedcomp": None,
    "salary": [
      {"datestarted": None}
    ]
  },
  "inputs": {
    "current_date": None
  }
})
def validate_salary_records(data):
  """
  This function validates a list of salary records to ensure there's at least
  one entry for each year (starting from April 1st) since the date joined company.
  Note - this is only an example! It isn't the real salary calc.
  The intention is to show how you can ask for related data and how you can do a bit of
  dataframe processing.

  Args:
      folder.salary: List of salaries.
      inputs.current_date: Date object representing the current date.

  Returns:
      outputs.all_present: True if there's at least one entry for each year, False otherwise.
  """
  
  # Convert salary records to a pandas DataFrame (assuming appropriate structure)
  df = pd.DataFrame(data['folder']['salary'])

  # Extract the year for each record (assuming a 'date' column) - If before 1st April we go the year before
  df['year'] = pd.to_datetime(df['datestarted']).dt.year \
             - (pd.to_datetime(df['datestarted']).dt.month < 4)


  # Calculate the starting year (considering April 1st)
  start_date = datetime.fromisoformat(data['folder']['datejoinedcomp'])
  start_year = start_date.year - (start_date.month < 4)
  end_date = datetime.fromisoformat(data['inputs']['current_date'])
  end_year = end_date.year - (end_date.month < 4)

  # Get the range of years to validate (inclusive)
  years_to_validate = range(start_year,  end_year + 1)

  # Check if there's at least one entry for each year
  yearly_entries = df.groupby('year').size()

  # Identify missing years
  missing_years = [year for year in years_to_validate if year not in yearly_entries.index]

  all_present = len(missing_years) == 0 and yearly_entries.all() > 0

  return {
      "outputs": {
          "all_present": str(all_present).lower(),
          "missing_years": missing_years
      }
  }