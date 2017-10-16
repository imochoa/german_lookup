
import driver

if __name__ == "__main__":

    # PyVerb.txt
    #

    # input_file = 'PyNouns.txt'
    # output_file = 'PyNouns_searched.txt'

    # input_file = 'PyAdj.txt'
    # output_file = 'PyAdj_searched.txt'

    chromedriver_path = '/home/ignacio/Code/chromedriver'

    finder = driver.VocabFinder.chrome_driver(chrome_driver_path=chromedriver_path)

    # Relative paths as well?
    finder.lookup_txt_file(input_file_path='/home/ignacio/Code/ger_looker_upper/PyNouns.txt',
                           default_attributes=['word_type'])