## SETUP

Run python install -r requirements.txt


Paste the following command into "main" in the gg_api.py file:

nltk.download('punkt')


## RUNNING THE CODE

### SENTIMENT CODE

In sentiment.py the sentiment function can be used by passing in the data file, such as gg2013.json, and the output dictionary for the main code.


### MAIN CODE

All codes and files that are necessary for running autograder are in the data_extraction directory. To run the autograder, first, make sure the preprocessed JSON data from IMDB for a specific year is in the data_extraction/data/ directory, and run main() in gg_api.py to compute the answer for a specific year into a JSON file. All function calls in gg_api.py except get_awards() uses the answer JSON file (i.e. 2013_award_extraction_answer.json). The purpose is to save computation.

For example, to run 2013 data, firstly check the preprocessed IMDB data: data_extraction/data/2013_title_data.json and data_extraction/data/2013_name_data.json, which may also be computed through IMDB_Processor.select_from_database() from data_processing.py. Then, make sure data_extraction/2013_award_extraction_answer.json is generated by running main() in gg_api.py. Run autograder.py should work after that.

Library used are included in requirements.txt.
