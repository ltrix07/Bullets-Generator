from functions import remove_forbidden_words
text = 'Replacement belts for Toro 115-4669 ensure optimal performance and longevity of your lawn equipment, compatible with various Toro models.'
print(remove_forbidden_words(text, '../db/words_black_list.json'))
