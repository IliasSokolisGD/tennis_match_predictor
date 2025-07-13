from difflib import SequenceMatcher
import unidecode as ud
PROBABILITY_THRESHOLD = 0.85
import re

unwanted_chars_set = {
    '\u0000', '\u0001', '\u0002', '\u0003', '\u0004', '\u0005', '\u0006', '\u0007',
    '\u0008', '\u0009', '\u000a', '\u000b', '\u000c', '\u000d', '\u0010', '\u0011',
    '\u0012', '\u0013', '\u0014', '\u0015', '\u0016', '\u0017', '\u0018', '\u0019',
    '\u001a', '\u001b', '\u001c', '\u001d', '\u001e', '\u001f', '\u007f',
    '\u00a0',  # Non-breaking space
    '\u1680',  # Ogham space mark
    '\u180e',  # Mongolian vowel separator
    '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005',
    '\u2006', '\u2007', '\u2008', '\u2009', '\u200a',
    '\u200b', '\u200c', '\u200d',
    '\u2028', '\u2029', '\u202f',
    '\u205f', '\u2060',
    '\ufeff',
    '\ufff9', '\ufffa', '\ufffb',
}
def keep_only_numbers(number_string: str):
    return ''.join(c for c in number_string if c.isdigit())

def string_not_empty(string: str):
    return len(string) != 0

def keep_only_letters_and_spaces(letter_string: str):
    return "".join(c for c in letter_string if c.isalpha() or c.isspace())

def keep_only_letters(letter_string: str):
    return "".join(c for c in letter_string if c.isalpha())

def strings_sub_sequences(str1: str, str2: str):
    pass



def custom_fuzzy_strategy(name1: str, name2: str):
    try:
        splitted_name1 = name1.upper().split()
        splitted_name2 = name2.upper().split()
        prenom1, nom1 = splitted_name1[0], splitted_name1[-1]
        prenom2, nom2 = splitted_name2[0], splitted_name2[-1]

        nom1_nom2_sequence_matcher = SequenceMatcher(None, nom1, nom2).ratio()
        prenom1_prenom2_sequence_matcher = SequenceMatcher(None, prenom1, prenom2).ratio()
        prenom1_nom2_sequence_matcher = SequenceMatcher(None, prenom1, nom2).ratio()
        prenom2_nom1_sequence_matcher = SequenceMatcher(None, prenom2, nom1).ratio()

        if (nom1_nom2_sequence_matcher == 1 or prenom1_prenom2_sequence_matcher == 1 or
                prenom1_nom2_sequence_matcher == 1 or prenom2_nom1_sequence_matcher == 1):
            return True
        return False
    except:
        return False

def is_subsequence(s1, s2):
    i, j = 0, 0
    while i < len(s1) and j < len(s2):
        if s1[i] == s2[j]:
            i += 1
        j += 1
    return i == len(s1)

def custom_fuzzy_strategy_2(name1: str, name2: str):
    name1_simplified = keep_only_letters(name1).lower()
    name2_simplified = keep_only_letters(name2).lower()

    name1_keep_only_name = name1.split()
    name1_keep_only_name = keep_only_letters("".join(name1_keep_only_name[:len(name1_keep_only_name) -1])).lower()

    name2_keep_only_name = name2.split()
    name2_keep_only_name = keep_only_letters("".join(name2_keep_only_name[:len(name2_keep_only_name) - 1])).lower()



    return (is_subsequence(name1_simplified, name2_simplified) or is_subsequence(name2_simplified, name1_simplified)
            or custom_fuzzy_strategy(keep_only_letters_and_spaces(name1), keep_only_letters_and_spaces(name2))
            or is_subsequence(name1_keep_only_name, name2_simplified) or is_subsequence(name2_keep_only_name, name1_simplified) or custom_fuzzy_strategy(name1_keep_only_name, name2_simplified))




def compare_strings(string1: str, string2: str) -> bool:
    """
        This method's role is to compare two strings and see if they have a high probability of matching
        :param string1: the string1
        :param string2: the string2
        :return: if the two strings have a high probability of matching
        """
    #First of all separate the strings in a list
    simplified1 = ud.unidecode(string1).lower().replace("-", " ")
    simplified2 = ud.unidecode(string2).lower().replace("-", " ")
    simplified1 = re.sub(r'[^a-zA-Z ]', '', simplified1)
    simplified2 = re.sub(r'[^a-zA-Z ]', '', simplified2)

    simplified1_list = simplified1.split()
    simplified1_list.sort()
    simplified2_list = simplified2.split()
    simplified2_list.sort()

    length1 = len(simplified1_list)
    length2 = len(simplified2_list)

    #detect names where there are multiple names
    if (length1 > 2 or length2 > 2) and length1 != length2 and one_sublist_of_another(simplified1_list, simplified2_list):
        return 1

    simplified1 = "".join(simplified1_list)
    simplified2 = "".join(simplified2_list)

    simplified1 = re.sub(r'[^a-zA-Z]', '', simplified1)
    simplified2 = re.sub(r'[^a-zA-Z]', '', simplified2)

    ratio = SequenceMatcher(None, simplified1, simplified2).ratio()

    return ratio


def probability_strings(string1: str, string2: str):
    simplified1 = re.sub(r'[^a-zA-Z]', '', string1)
    simplified2 = re.sub(r'[^a-zA-Z]', '', string2)

    ratio = SequenceMatcher(None, simplified1, simplified2).ratio()
    return ratio


def one_sublist_of_another(list1: list, list2: list) -> float:
    length1 = len(list1)
    length2 = len(list2)

    if length1 > length2:
        for word in list2:
            found = False
            for word1 in list1:
                if probability_strings(word, word1) >= PROBABILITY_THRESHOLD:
                    found = True
                    break
            if found is False:
                return False
            else:
                continue
    else:
        for word in list1:
            found = False
            for word1 in list2:
                if probability_strings(word, word1) >= PROBABILITY_THRESHOLD:
                    found = True
                    break
            if found is False:
                return False
            else:
                continue

    return True
