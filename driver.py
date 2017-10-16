#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import os
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

import re


# leo_categories = {"section-subst":  ['substantive', 'noun'],
#                   "section-adjadv": ['adjective', 'adverb'],
#                   "section-verb":   ['verb'],
#                   "conj":           ['conjunction']}
#
# def leo_page_xpaths(word_type=None, column=0, num=5):
#     possible_types = [val for sublist in leo_categories.values() for val in sublist]
#
#     word_type = word_type.lower()
#
#     if not any(s.startswith(word_type) for s in possible_types):  # Making sure that word type exists
#         raise Exception("Unknown word type '{0}'".format(word_type))
#
#     matched_val = [s for s in possible_types if s.startswith(word_type)][0]
#
#     # print("The word_type has been set to: '{0}'".format(matched_val))
#
#     matched_key = next(k for k, v in leo_categories.iteritems() if matched_val in v)
#
#     return ['//*[@id="{0}"]/table/tbody/tr[{1}]/td[{2}]/samp'.format(matched_key, i, column) for i in range(1, num + 1)]


class VocabFinder(object):
    # Class variables
    # Names used by leo_dict for the sections that correspond to each type

    num_results = 3

    def _page_attribute_scan(self):
        # Get page HTML
        soup = BeautifulSoup(self.driver.page_source, "lxml")

        # Find all sections
        noun_sect = soup.find('div', id='section-subst')
        verb_sect = soup.find('div', id='section-verb')
        adjadv_sect = soup.find('div', id='section-adjadv')

        results = dict()
        word_type = []

        # NOUNS
        if noun_sect is not None:
            word_type += ['noun']

            # Get the Noun info
            noun_table = noun_sect.find('table')  # find table

            r = []
            d = dict()
            it = 0

            for row in noun_table.tbody.findAll('tr'):
                if it == self.num_results:
                    break
                else:
                    it += 1

                first_column = row.findAll('td')[4]
                third_column = row.findAll('td')[7]

                del d
                d = {
                    'word':                    third_column.find('mark').text,
                    'def':                     first_column.text,
                    'gender': third_column.text[0:3],
                    'plural':                  third_column.find('small').text
                    }

                # Fixing plural format: 'Pl.: ' at the beginning
                if d['plural'].startswith('Pl.: '):
                    d['plural'] = d['plural'][5:]

                r += [d]

            # TODO Keep one row, except in the defs
            # Parse noun GENDER
            lst = [iter_d['gender'] for iter_d in r]
            results['gender'] = max(set(lst), key=lst.count)

            # Parse noun PLURAL
            lst = [iter_d['plural'] for iter_d in r]
            results['plural'] = max(set(lst), key=lst.count)

            # Parse noun DEF
            results['noun_def'] = u' | '.join([iter_d['def'] for iter_d in r])

        # ADJECTIVES & ADVERBS
        if adjadv_sect is not None:
            word_type += ['adjadv']
            for row in noun_table.tbody.findAll('tr'):
                first_column = row.findAll('td')[4]
                third_column = row.findAll('td')[7]

                noun_def = first_column.text

                word_de = third_column.find('mark').text
                word_de_plural = third_column.find('small').text
                word_de_gender = third_column.text[0:3]

                print word_de_gender, word_de, word_de_plural, noun_def

        # VERBS
        if verb_sect is not None:
            word_type += ['verb']

            # Get the Verb info
            verb_table = verb_sect.find('table')  # find table

            r = []
            d = dict()
            it = 0

            for row in verb_table.tbody.findAll('tr'):
                if it == self.num_results:
                    break
                else:
                    it += 1

                first_column = row.findAll('td')[4]
                third_column = row.findAll('td')[7]

                del d

                de_word = third_column.text

                m = re.match(r'(\w*)[^\w]*(\w*)[^\w]*(\w*)[^\w]*', de_word)

                d = {
                    'word':         third_column.find('mark').text,
                    'def':          first_column.text,
                    'inf':          m.group(1),
                    'imperfekt_3s': m.group(2),
                    'PII':          m.group(3)
                    }

                # More verb tenses
                if it == 1:
                    # go into verb tenses
                    verb_box = self.driver.find_element_by_xpath('//*[@id="section-verb"]/table/tbody/tr[1]/td[6]/a/i')
                    verb_box.click()
                    time.sleep(self.pause)

                    # Find all sections

                    v_soup = BeautifulSoup(self.driver.page_source, "lxml")
                    indikativ_sect = v_soup.find('div', id='mood-1')
                    konjunktiv_sect = v_soup.find('div', id='mood-2')
                    imperativ_sect = v_soup.find('div', id='mood-3')
                    impersonal_sect = v_soup.find('div', id='mood-4')

                    # Get info
                    tenses = {
                        'imperfekt_3s': '//*[@id="flect"]/div[2]/div/div[3]/table/tbody[2]/tr[4]/td[1]/span[2]',
                        'KII_imp_3s':   '//*[@id="flect"]/div[2]/div/div[4]/table/tbody[2]/tr[4]/td[1]/span[2]'}

                    tenses = {k: self.driver.find_element_by_xpath(v).text for k, v in tenses.iteritems()}

                    # leave verb tenses
                    verb_box = self.driver.find_element_by_xpath('/html/body/div[30]/div[1]/button/span[1]')
                    verb_box.click()
                    time.sleep(self.pause)

                r += [d]

                # Parse noun GENDER
            lst = [iter_d['gender'] for iter_d in r]
            results['gender'] = max(set(lst), key=lst.count)

            # # Parse noun PLURAL
            # lst = [iter_d['plural'] for iter_d in r]
            # results['plural'] = max(set(lst), key=lst.count)
            #
            # # Parse noun DEF
            # results['noun_def'] = u' | '.join([iter_d['def'] for iter_d in r])
            #
            # # EXTRA
            # results['word_type'] = word_type

        return results

    def _attribute_finder(self, attribute):
        # f = self.possible_attributes.get(attribute, None)

        r_dict = self._page_attribute_scan()

        # if not callable(f):
        #     raise Exception(
        #             "The given attribute '{0}' was not one of the valid attributes:{1}".format(
        #                     attribute, self.possible_attributes.keys()))
        #
        # return f(self, attribute)

    def __init__(self,
                 webdriver,
                 num_of_results=5,
                 word_type=None,
                 driver_timeout=10,
                 driver_pause=0.5):
        # self._word_type = VocabFinder.noun if word_type is None else word_type

        self._num_of_results = num_of_results
        self._pause = float(driver_pause)

        self.driver = webdriver
        url = r'https://dict.leo.org/englisch-deutsch/'
        self.driver.get(url)

        self.wait = WebDriverWait(self.driver, timeout=driver_timeout)

    @classmethod
    def chrome_driver(cls, chrome_driver_path):
        if not os.path.isfile(chrome_driver_path):
            raise Exception("ChromeDriver path:'{0}' did not point to an existing file".format(chrome_driver_path))

        return VocabFinder(webdriver=webdriver.Chrome(chrome_driver_path),
                           )

    @property
    def pause(self):
        return self._pause

    @pause.setter
    def pause(self, pause_val):
        if not pause_val > 0:
            raise Exception('The pause value should be >0. Got {0} instead'.format(pause_val))
        self._pause = pause_val

    def find_defs(self, word, word_type=None, num=None):
        word_type = self.word_type if word_type is None else word_type
        num = self.num_of_results if num is None else num

        # edit the word
        if word_type is VocabFinder.verb:
            word = word.replace("sich", '')

        x_paths = self.definition_xpaths(word_type=word_type, num=num)

        search_box = self.driver.find_element_by_id('search-field')
        search_box.send_keys(word + '\n')
        time.sleep(self.pause)

        # try:
        # 	wait.until(EC.presence_of_element_located((By.ID, 'section-subst')))
        # except TimeoutException:
        # 	return ['_no_def_']

        results = []
        for xpth in x_paths:
            try:
                results.append(self.driver.find_element_by_xpath(xpth).text)
            except NoSuchElementException, AttributeError:
                break

        return results

    # def _find_on_page(self, attr_list):
    #     """
    #     List of attributes to search for in the current page
    #     :param search_term: List
    #     :return:
    #     """
    #
    #     # Ensure that it is a list
    #     if not isinstance(attr_list, list):
    #         attr = [attr_list]
    #
    #     return [self._attribute_finder(a) for a in attr_list]

    # def find_noun_def(self, word, num=None):
    #     return self.find_defs(word, word_type=self.noun, num=num)
    #
    # def find_adjadv_def(self, word, num=None):
    #     return self.find_defs(word, word_type=self.adj_adv, num=num)
    #
    # def find_verb_def(self, word, num=None):
    #     return self.find_defs(word, word_type=self.verb, num=num)
    #
    # def find_conjugation(self, word):
    #     search_box = self.driver.find_element_by_id('search-field')
    #     search_box.send_keys(word + '\n')
    #     time.sleep(self.pause)
    #
    #     v_table = self.driver.find_element_by_xpath('//*[@id="section-verb"]/table/tbody/tr[1]/td[6]/a/i')
    #     v_table.click()
    #     Kii = self.driver.find_element_by_xpath('//*[@id="flect"]/div[2]/div/div[4]/table/tbody[2]/tr[5]/td[1]')
    #     t = Kii.text.replace('er/sie/es ', '')
    #     return t

    # def read_write_files(self):
    #     try:
    #         os.remove(self.output_file)
    #     except OSError:
    #         pass
    #     finally:
    #         my_file = open(self.output_file, 'w+')
    #         my_file.close()
    #
    #         num_lines = sum(1 for line in open(self.input_file))
    #     curr_line = 0
    #
    #     with codecs.open(self.input_file, 'r', 'utf8') as fsource:
    #         with codecs.open(self.output_file, 'w', 'utf8') as fdest:
    #
    #             for line in fsource:
    #                 curr_line += 1
    #                 print(
    #                     "Done {2}%  (Line {0}/{1})".format(curr_line, num_lines,
    #                                                        round(curr_line * 100.00 / num_lines, 2)))
    #
    #                 if len(line.rstrip()) == 0:
    #                     fdest.write('\n')
    #                     continue
    #
    #                 word = line.split()[0]
    #
    #                 definition = leo.find_defs(word)
    #
    #                 dest_line = line.rstrip() + '\t' + ', '.join(definition)
    #
    #                 dest_line = dest_line.replace('\n', ' ') + '\n'
    #
    #                 print(dest_line)
    #                 fdest.write(dest_line)


    def _new_search(self, word):
        search_box = self.driver.find_element_by_id('search-field')
        search_box.send_keys(word + '\n')
        time.sleep(self.pause)

    def lookup_txt_file(self, input_file_path,
                        output_file_path=None,
                        default_attributes=None,
                        csv=False):
        """
        :param input_file_path: path of the input file
        :param output_file_path: OPTIONAL path of the output file
        :param default_attributes: what you want to look up, it has to be one of the possible attributes from the class
                                    variable "possible_attributes". If there are attributes on the line, those will
                                    override the default ones.
        :param csv: If set to True, input is taken as a csv (Comma Separated Value) file, if it is False,
                        the input is taken as a tsv (Tab Separated Value) file.
                    The output file will have the same format as the input file
        :return: None
        """

        try:
            # Does the input exist?
            if not os.path.isfile(input_file_path):
                raise Exception("The input file path:'{0}' does not exist!".format(input_file_path))

            # Output given?
            if output_file_path is None:
                output_file_path = '_RESULTS'.join(os.path.splitext(input_file_path))

            # delimiter to use?
            delim = u',' if csv else u'\t'

            # # Create output file if it did not exist, erase its contents if it did
            # with open(output_file_path, 'w+') as fdest:
            #     pass

            # Count the number of lines in the input file
            line_max = sum(1 for line in open(input_file_path))
            line_iter = 0

            with codecs.open(input_file_path, 'r', 'utf8') as fsource:
                with codecs.open(output_file_path, 'w', 'utf8') as fdest:

                    for line in fsource:
                        line_iter += 1
                        print("Done {2:.2f}%  (Line {0}/{1})".format(
                                line_iter, line_max, line_iter * 100.00 / line_max))

                        # Get the info from the line
                        line_list = line.rstrip().lstrip().split(delim)

                        if len(line_list) < 1:
                            fdest.write('\n')
                            continue  # Empty line, skip it!

                        elif len(line_list) == 1:
                            # No specific attributes, use default values
                            attr_list = default_attributes
                        else:
                            # use specific attributes for that line
                            attr_list = line_list[1:]

                        # Look for the new word
                        search_term = line_list[0]
                        self._new_search(search_term)

                        # Get attributes
                        results = [self._attribute_finder(a) for a in attr_list]

                        # Write to the file
                        fdest.write(delim.join([search_term] + results) + '\n')

        except Exception as e:
            print("General Exception:\n")
            print(e)


if __name__ == "__main__":

    # PyVerb.txt
    #

    # input_file = 'PyNouns.txt'
    # output_file = 'PyNouns_searched.txt'

    # input_file = 'PyAdj.txt'
    # output_file = 'PyAdj_searched.txt'

    chromedriver_path = '/home/ignacio/Code/chromedriver'

    finder = VocabFinder.chrome_driver(chrome_driver_path=chromedriver_path)

    # Relative paths as well?
    finder.lookup_txt_file(input_file_path='/home/ignacio/Code/ger_looker_upper/PyNouns.txt',
                           default_attributes=['gender'])

    # output_file = 'PyVerb_searched.txt'
    # num_of_results = 5
    # 
    # leo = LeoWeb(input_file=input_file,
    #              output_file=output_file,
    #              num_of_results=num_of_results)
    # 
    # leo.word_type = leo.verb
    # 
    # leo.read_write_files()
