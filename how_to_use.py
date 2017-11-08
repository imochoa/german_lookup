import driver

if __name__ == "__main__":

    # Where did you save the chromedriver?
    chromedriver_path = '/home/ignacio/Code/chromedriver'

    # Where is the file you want to translate?
    input_file_path = 'verbs_w_preps_defs_1.txt'
    # Where do you want the results? None = auto-naming
    output_file_path = None

    # What fields do you want to look up?
    fields_to_find = ['word_type', 'blank_column', 'verb_def']

    finder = driver.VocabFinder.chrome_driver(chrome_driver_path=chromedriver_path)

    # Relative paths as well?
    finder.lookup_txt_file(input_file_path=input_file_path,
                           default_attributes=fields_to_find,
                           output_file_path=output_file_path)

    # close the webdriver
    finder.close()
