#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import os
import time
from bs4 import BeautifulSoup

import traceback

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

import re

possible_attributes = {
    'general':    ['word_type'],
    'noun':       ['gender', 'plural', 'noun_def'],
    'verb':       ['verb_def', 'PII', 'inf', 'imperfekt_3s'],
    'verb_extra': ['KII_imperfekt'],
    'adjadv':     ['adjadv_def']
    }


class VocabFinder(object):
    # Class variables
    # Names used by leo_dict for the sections that correspond to each type

    num_results = 3

    def __init__(self,
                 webdriver,
                 driver_timeout=10,
                 driver_pause=0.5):
        # self._word_type = VocabFinder.noun if word_type is None else word_type

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

    def _new_search(self, word):
        search_box = self.driver.find_element_by_id('search-field')
        search_box.send_keys(word + '\n')
        time.sleep(self.pause)

    def _attribute_finder(self, attr_lst):

        if not isinstance(attr_lst, list):
            attr_lst = [attr_lst]

        # Get page HTML
        soup = BeautifulSoup(self.driver.page_source, "lxml")

        # Find all sections
        noun_sect = soup.find('div', id='section-subst')
        verb_sect = soup.find('div', id='section-verb')
        adjadv_sect = soup.find('div', id='section-adjadv')

        results = {'word_type': []}

        # NOUNS
        if noun_sect is not None:
            results['word_type'] += ['noun']  # Add to that word's type

            if any(a in possible_attributes['noun'] for a in attr_lst):
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
        # TODO Finish adjectives and adverbs
        if adjadv_sect is not None:
            results['word_type'] += ['adjadv']  # Add to that word's type

            if any(a in possible_attributes['adjadv'] for a in attr_lst):
                for row in noun_table.tbody.findAll('tr'):
                    first_column = row.findAll('td')[4]
                    third_column = row.findAll('td')[7]

                    noun_def = first_column.text

                    word_de = third_column.find('mark').text
                    word_de_plural = third_column.find('small').text
                    word_de_gender = third_column.text[0:3]

                    print word_de_gender, word_de, word_de_plural, noun_def

        # VERBS
        # TODO Finish verbs
        if verb_sect is not None:
            results['word_type'] += ['verb']

            if any(a in possible_attributes['verb'] for a in attr_lst):
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
                    if it == 1 and any(
                            a.startswith(v_e) for v_e in possible_attributes['verb_extra'] for a in attr_lst):
                        # go into verb tenses
                        verb_box = self.driver.find_element_by_xpath(
                                '//*[@id="section-verb"]/table/tbody/tr[1]/td[6]/a/i')
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

                # Parse verb results
                lst = [iter_d['gender'] for iter_d in r]
                results['gender'] = max(set(lst), key=lst.count)

                # Parse verb DEF
                results['verb_def'] = u' | '.join([iter_d['def'] for iter_d in r])

        # FINISHED

        results['word_type'] = u' | '.join([t for t in results['word_type']])

        return {a: results.get(a, '') for a in attr_lst}

    def lookup_txt_file(self, input_file_path,
                        output_file_path=None,
                        default_attributes=None,
                        csv=False,
                        headers=True):
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

            if not isinstance(default_attributes, list):
                default_attributes = [default_attributes]

            # # Create output file if it did not exist, erase its contents if it did
            # with open(output_file_path, 'w+') as fdest:
            #     pass

            # Count the number of lines in the input file
            line_max = sum(1 for line in open(input_file_path))
            line_iter = 0

            with codecs.open(input_file_path, 'r', 'utf8') as fsource:
                with codecs.open(output_file_path, 'w', 'utf8') as fdest:

                    if headers:
                        # Add the column headers
                        fdest.write(delim.join(['Words'] + default_attributes) + '\n')

                    for line in fsource:

                        line_iter += 1

                        # Get the info from the line
                        line_list = line.rstrip().lstrip().split(delim)

                        if len(line_list) < 1:
                            fdest.write('\n')
                            continue  # Empty line, skip it!

                        elif len(line_list) == 1:
                            # No specific attributes, use default values
                            attr_lst = default_attributes
                        else:
                            # use specific attributes for that line
                            attr_lst = line_list[1:]

                        # Look for the new word
                        search_term = line_list[0]
                        self._new_search(search_term)
                        print("{2:.2f}% [{0:4d}/{1}] Word: ".format(
                                line_iter,
                                line_max,
                                line_iter * 100.00 / line_max) + search_term)

                        # Get attributes
                        results = self._attribute_finder(attr_lst=attr_lst)

                        # Write to the file
                        fdest.write(search_term + delim + delim.join([results.get(a, '') for a in attr_lst]) + '\n')

        except Exception as e:
            # print("General Exception:\n")
            print(e)
            traceback.print_exc()


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
