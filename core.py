import re


def noun_info_extractor(noun_sect, max_iter=5):
    # Get the Noun info
    noun_table = noun_sect.find('table')  # find table

    de_noun = []
    noun_def = []
    gender = []
    plural = []

    c = 0

    for row in noun_table.tbody.findAll('tr'):

        if c > max_iter:
            break

        first_column = row.findAll('td')[4]
        second_column = row.findAll('td')[7]

        noun_def += [first_column.text]
        de_noun += [second_column.find('mark').text]

        if any(second_column.text[0:3] == g for g in ['der', 'die', 'das']):
            gender += [second_column.text[0:3]]

        if second_column.find_all('small'):
            plural += [second_column.find_all('small')[-1].text.replace('Pl.: ', '')]

        c += 1

    # Parse noun GENDER
    gender = max(set(gender), key=gender.count)

    # Parse noun PLURAL
    plural = max(set(plural), key=plural.count)

    # Merge DEFINITIONS
    noun_def = u' | '.join(noun_def)

    return {'de_noun':  de_noun,
            'noun_def': noun_def,
            'gender':   gender,
            'plural':   plural}


def adjadv_info_extractor(adjadv_sect, max_iter=5):
    # Get the Noun info
    adjadv_table = adjadv_sect.find('table')  # find table

    de_adjadv = []
    adjadv_def = []

    c = 0

    for row in adjadv_table.tbody.findAll('tr'):

        if c > max_iter:
            break

        first_column = row.findAll('td')[4]
        second_column = row.findAll('td')[7]

        adjadv_def += [first_column.text]
        de_adjadv += [second_column.find('mark').text]

        c += 1

    # Merge DEFINITIONS
    adjadv_def = u' | '.join(adjadv_def)

    return {'de_adjadv':  de_adjadv,
            'adjadv_def': adjadv_def}


def verb_info_extractor(verb_sect, max_iter=5):
    # Get the Noun info
    verb_table = verb_sect.find('table')  # find table

    de_verb = []
    verb_def = []
    inf = []
    imp_3 = []
    pii = []

    c = 0

    for row in verb_table.tbody.findAll('tr'):

        if c > max_iter:
            break

        first_column = row.findAll('td')[4]
        second_column = row.findAll('td')[7]

        m = re.match(r'(\w*)[^\w]*(\w*)[^\w]*(\w*)[^\w]*', second_column.text)
        verb_def += [first_column.text]
        de_verb += [second_column.find('mark').text]

        inf += [second_column.find('mark').text]

        tt = [t.text.replace(u'|\xa0', '').replace(u'\xa0|', '')
              for t in second_column.find_all('small') if t.text.startswith('|')]

        if tt:
            tt = tt[0].split(', ')
            imp_3 += [tt[0]]
            pii += [tt[1]]

        c += 1

    # Parse verb TENSES

    inf = max(set(inf), key=inf.count)
    imp_3 = max(set(imp_3), key=imp_3.count)
    pii += max(set(pii), key=pii.count)

    # Merge DEFINITIONS
    verb_def = u' | '.join(verb_def)

    return {'de_verb':      de_verb,
            'verb_def':     verb_def,
            'inf':          inf,
            'imperfekt_3s': imp_3,
            'PII':          pii}


def extra_verb_info_extractor(verb_sect, max_iter=5):
    #TODO MOVE ALL THE TENSES HERE AND LOOK FOR THEM IN THE OTHER TABLE THAT OPENS UP
    # Get the Noun info
    verb_table = verb_sect.find('table')  # find table

    # More verb tenses
    #         if it == 1 and any(
    #                 a.startswith(v_e) for v_e in possible_attributes['verb_extra'] for a in attr_lst):
    #             # go into verb tenses
    #             verb_box = self.driver.find_element_by_xpath(
    #                     '//*[@id="section-verb"]/table/tbody/tr[1]/td[6]/a/i')
    #             verb_box.click()
    #             time.sleep(self.pause)
    #
    #             # Find all sections
    #
    #             v_soup = BeautifulSoup(self.driver.page_source, "lxml")
    #             indikativ_sect = v_soup.find('div', id='mood-1')
    #             konjunktiv_sect = v_soup.find('div', id='mood-2')
    #             imperativ_sect = v_soup.find('div', id='mood-3')
    #             impersonal_sect = v_soup.find('div', id='mood-4')
    #
    #             # Get info
    #             tenses = {
    #                 'imperfekt_3s': '//*[@id="flect"]/div[2]/div/div[3]/table/tbody[2]/tr[4]/td[1]/span[2]',
    #                 'KII_imp_3s':   '//*[@id="flect"]/div[2]/div/div[4]/table/tbody[2]/tr[4]/td[1]/span[2]'}
    #
    #             tenses = {k: self.driver.find_element_by_xpath(v).text for k, v in tenses.iteritems()}
    #
    #             # leave verb tenses
    #             verb_box = self.driver.find_element_by_xpath('/html/body/div[30]/div[1]/button/span[1]')
    #             verb_box.click()
    #             time.sleep(self.pause)


if __name__ == '__main__':
    pass
