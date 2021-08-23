import aspell
from symspellpy.symspellpy import SymSpell, Verbosity
from typing import List, Dict
# import string
# import re

import pickle

from PIL import ImageFont
from .distancia_trocas import distancia_troca_caracteres

#word2vec
import gensim

#Levenshtein
import Levenshtein as L

data_dir = "./word_correction/data/"


class WordCorrection:
    def __init__(self):
        self.sym_spell = self.load_symspell()
        self.load_symspell_dict()
        
        self.aspell = self.load_aspell()

        self.model = self.load_sk_model()

        self.w2v = self.load_w2v()
        self.font = ImageFont.truetype(font=data_dir+'arial.ttf', size=12)
        

    #------------------------------
    #----------- ASPELL -----------
    #------------------------------

    def load_aspell(self):
        return aspell.Speller('master', data_dir+'dictionary/pt_BR/pt_BR.rws')

    def print_aspell_ConfigKeys(self):
        for key in self.aspell.ConfigKeys():
            print("{}: {}".format(key, self.aspell.ConfigKeys()[key][1]))
    

    def aspell_check(self, word: str) -> bool:
        return self.aspell.check(word)


    def aspell_suggest(self, word: str):
        # test = re.sub(u'[^a-zA-ZáéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ ]', '', word)

        # if len(test) > 0:
        try:
            suggestions = self.aspell.suggest(word)
            if len(suggestions) != 0:
                return suggestions[0]
        except:
            return ""
        return ""

    #------------------------------
    #---------  SYMSPELL ----------
    #------------------------------

    def load_symspell(self):
        max_edit_distance_dictionary = 2
        prefix_length = 7    
        return SymSpell(max_edit_distance_dictionary, prefix_length)

    def load_symspell_dict(self):
        unigram_path = "unigrams_folha.txt"
        bigram_path = "bigrams_folha_5.txt"
        if not self.sym_spell.load_dictionary(data_dir+unigram_path, term_index=0, separator= "\t",
                                        count_index=1, encoding='utf-8'):
            print("Unigram dictionary file not found")
        if not self.sym_spell.load_bigram_dictionary(data_dir+bigram_path, term_index=0, separator="\t",
                                                count_index=2, encoding='utf-8'):
            print("Bigram dictionary file not found")

    def symspell_suggestion(self, input_term: str): # SymSpell comoFrase
        max_edit_distance_lookup = 2
        suggestions = self.sym_spell.lookup_compound(input_term,
                                            max_edit_distance_lookup, transfer_casing=True, ignore_non_words=False)
        if len(suggestions) != 0:
            return suggestions[0].term
        return ""

    def symspell_word_suggestion(self, input_term: str): # SymSpell default (retornando palavra)
        max_edit_distance_lookup = 2
        suggestion_verbosity = Verbosity.TOP  # TOP, CLOSEST, ALL
        suggestions = self.sym_spell.lookup(input_term, suggestion_verbosity,
                                           max_edit_distance_lookup, transfer_casing=True)
        if len(suggestions) != 0:
            return suggestions[0].term
        return ""

  
    #------------------------------
    #---------- SKLEARN -----------
    #------------------------------

    def load_sk_model(self):
        return pickle.load(open(data_dir+'rfmodel_2s_1a_9f_lwr_3lab', 'rb'))

    def classify_input(self, input):
        cands = [self.symspell_suggestion(input), self.symspell_word_suggestion(input), self.aspell_suggest(input)]
        inst = self.create_values(input, cands)

        predicted_label = self.model.predict([inst])
        index_pred = self.get_index_pred(predicted_label)

        return cands[index_pred]


    def get_index_pred(self, predicted_label):
        if predicted_label == "label0":
            return 0
        elif predicted_label == 'label1':
            return 1
        elif predicted_label == 'label2':
            return 2


    #------------------------------
    #---------- FEATURES ----------
    #------------------------------

    def load_w2v(self):
        return gensim.models.KeyedVectors.load_word2vec_format(data_dir+"modelo.bin", binary=True, unicode_errors='ignore')

    def simil_semantica(self, word, word_esp):
        resp = -2
        try:
            resp = self.w2v.similarity(word, word_esp)
        except Exception as e:
            pass
        return resp

    def create_values(self, input, candidatos):
        values_cand = []
        width_inserida, height_inserida = self.font.getsize(input)
        for cand_atual in candidatos:
            if cand_atual != '':
                sim_semantica = self.simil_semantica(input, cand_atual)       
                isupper_char = str.isupper(cand_atual[0])
                isupper_word = str.isupper(cand_atual)
                distance = L.distance(input, cand_atual)
                jaro = L.jaro(input, cand_atual)
                ratio = L.ratio(input, cand_atual)

                dist_trocas = distancia_troca_caracteres(input, cand_atual)

                width_cand, height_cand = self.font.getsize(cand_atual)
                diff_tam = abs(width_inserida-width_cand)
                diff_alt = abs(height_inserida-height_cand)

                # -------------------------------------------------------
                values_cand.append(sim_semantica)
                values_cand.append(isupper_char)
                values_cand.append(isupper_word)
                values_cand.append(distance)
                values_cand.append(jaro)
                values_cand.append(ratio)
                values_cand.append(dist_trocas)
                values_cand.append(diff_tam)
                values_cand.append(diff_alt)
            else:
                values_cand.append(-2)
                values_cand.append(False)
                values_cand.append(False)
                values_cand.append(-1)
                values_cand.append(-1)
                values_cand.append(-1)
                values_cand.append(-1)
                values_cand.append(width_inserida)
                values_cand.append(height_inserida)
        
        return values_cand
