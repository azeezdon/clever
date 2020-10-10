import collections, string, re
from django.utils.html import strip_tags
from io import StringIO

# Counts words in template files and insert keywords into page
word_count_min = 2
word_length_min = 4

nogo_list = []  # Optional list of words you may not want as meta tags.


# meta_keywords ( html string ) =>
#   returns non html keyword list, as a comma seperated string,
#   for words fitting qualifications as chosen above.
def meta_keywords(str_file):
    c = collections.Counter()
    strIO_Obj = StringIO.StringIO(str_file)
    for line in strIO_Obj.readlines():
        c.update(re.findall(r"[\w']+", strip_tags(line).lower()))
    wordlist = []
    for word, count in c.most_common():
        if len(word) > (word_length_min - 1) and count > (
                word_count_min - 1) and word not in nogo_list: wordlist.append(word)
    return string.join(wordlist, ',')
