import codecs
import os
import numpy as np 
import tqdm
import os
import nltk
import time
import sys, xmltodict
import os.path
import ktrain
import string, re
import glob
from word_correction.word_correction import WordCorrection
import json

import argparse

def test_valid_word(word, index):
    if index != 0 and word[0].isupper() and word[1:].islower():
        return False, 1
    if word.isupper():
        return False, 2
    test = re.sub(u'[^a-zA-ZáéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ ]', '', word)
    if len(test)==0:
        return False, 3
    return True, 0

def corrigir_sent(sentence, corrector, use_nltk):
    sent_mod = []
    if use_nltk:
        words = nltk.word_tokenize(sentence)
    else:
        words = sentence.split()
    for t, word in enumerate(words):
        #print(t, word)
        valid_word, test = test_valid_word(word, t)
        if valid_word == True:
            sent_mod.append(corrector.classify_input(word))
        else:
            sent_mod.append(word)
    final_sentence = ' '.join(sent_mod)
    return final_sentence 

def corrigir_line(line, corrector, predictor, use_nltk):
    if use_nltk:
        sents = nltk.sent_tokenize(line)
    else:
        sents = line.split(". ")
    sents_new = []
    for sent in sents:
        if predictor.predict(sent) == 'corrige':
            sent_new = corrigir_sent(sent, corrector, use_nltk)
        else:
            sent_new = sent 
        sents_new.append(sent_new)
        pass
    return ' '.join(sents_new)


def read_file(path):
    try:
        with codecs.open(path, 'r', encoding="utf-8") as f:
            resp = f.readlines()
        print('read %s with utf-8'%path)
        return resp 
    except Exception as e:
        if "'utf-8' codec can't" in str(e):
        #try to read with iso-8859-1
            try: 
                with codecs.open(path, 'r', encoding="iso-8859-1") as f:
                    resp = f.readlines()
                print('read %s with iso-8859-1'%path)
                return resp 
            except Exception as e:
                print(e)
                return None
        else:
            print(e)
            return None 

def processar_onefile(pathin, pathout, txtfile, corrector, predictor, use_nltk):
    lines = read_file(os.path.join(pathin, txtfile))
    out = codecs.open(os.path.join(pathout, txtfile), 'w', 'utf-8')
    for line in tqdm.tqdm(lines):
        line = line.strip()
        if len(line)>0:
            line_new = corrigir_line(line, corrector, predictor, use_nltk)
        else:
            line_new = line 
        out.write(line_new+'\n')
    out.close()

def folder_xml(folder, folderout, corrector, predictor, use_nltk):
    files = glob.glob("{}/*.xml".format(folder))
    for f, file in enumerate(files):
        ini_file = time.time()
        filename = file.split('/')[-1].split('\\')[-1].replace("error", "classificador")
        if not os.path.isfile(folderout+"/"+filename):
            print("{} - {} - Iniciado".format(f, filename))
            with open(file, 'r', encoding='utf-8') as temp_f:
                xml_doc = xmltodict.parse(temp_f.read())
                new_xml = {
                        'add':{
                            'doc':[]
                            }
                        }
                doc_erros = 0
                for doc in xml_doc['add']['doc']:
                    print("\t "+doc['field'][0]['#text'])
                    new_doc = {'field':[]}

                    for num_tag in range(len(doc['field'])):
                        if doc['field'][num_tag]['@name'] == 'texto_erros':
                            doc_erros += 1
                            text = doc['field'][num_tag]['#text']
                            #corrigir_line(texto, intancia_Corretor, predictor_bert, use_nltk?)
                            final_sentence = corrigir_line(text, corrector, predictor,use_nltk)
                            new_doc['field'].append({
                                    '@name': "text",
                                    '#text': final_sentence
                                    })
                        else:
                            new_doc['field'].append({
                                '@name': doc['field'][num_tag]['@name'],
                                '#text': doc['field'][num_tag]['#text'] if doc['field'][num_tag]['#text'] else '',
                                })
                    new_xml['add']['doc'].append(new_doc)
            result_xml = xmltodict.unparse(new_xml, pretty=True)
            with open(folderout+"/"+filename, "w", encoding='utf-8') as out_file:
                out_file.write(result_xml)
            end_file = time.time()
            tempo = end_file - ini_file
            print("{} - {} - Concluído em {} sec, {} docs com erros, AVG {}\n".format(f, filename, tempo, doc_erros, (tempo/doc_erros))) 
        else:
            print("{} - {} já processado!\n".format(f, filename))

if __name__ == "__main__":
    parser = argparse.ArgumentParser('sOCRates')
    parser.add_argument('--folderin', 
                        type=str,
                        required=False,
                        help='caminho para a pasta de entrada')
    parser.add_argument('--folderout', 
                        required=False,
                        default='classificador_filtro',
                        type=str,
                        help='caminho para a pasta de saida (sin / al final)')
    parser.add_argument('--xml', 
                        type=int,
                        required=True,
                        help='processar folder xml? (1 - sim, 0 - não)')
    parser.add_argument('--use_nltk', 
                        type=int,
                        required=True,
                        help='use nltk to split sentences and words? (1 - sim, 0 - não)')
    parser.add_argument('--lista_filtro', 
                        type=str,
                        required=False,
                        help='caminho para o json com a lista de documentos a não ser processados')



    # read args
    args = parser.parse_args()
    folderin=args.folderin 
    #it = args.it
    folderout=args.folderout 
    xml = args.xml 
    use_nltk = args.use_nltk
    lista_filtro = args.lista_filtro
    if os.path.exists(folderout):
        pass
    else:#create
        os.mkdir(folderout)
    
    # load resources to correct
    corrector = WordCorrection()
    predictor = ktrain.load_predictor("pred_bert")
   
    # process files of a given folder
    if folderin is not None:
        if xml==1:
            print('corregir xml')
            folder_xml(folderin, folderout, corrector, predictor, use_nltk)
        else:
            print('corregir otros txt')
            print('aqui')
            if os.path.exists(folderin):
                #listar os arquivos de txt
                files = os.listdir(folderin)
                print("files total sem filtro: %i"%len(files))
                #out_lista = codecs.open('all.txt', 'w')
                #for fl in files:
                #    out_lista.write(fl+'\n')
                #print(files)

                if lista_filtro is None:
                    print('processar todos sem filtro')
                    files = [f for f in files if str(f).endswith('.txt') and 'readme' not in str(f)]
                else:
                    print('processar só arquivos que não estão em %s'%lista_filtro)
                    info = []
                    with open(lista_filtro, 'r') as f:
                        info = json.load(f)
                    print('tem %i items in lista_filtro'%len(info))
                    lista_f = [item[2]+'.txt' for item in info]
                    files = [f for f in files if str(f).endswith('.txt') and 'readme' not in str(f) and f not in lista_f]
                    print("files total sem filtro: %i"%len(files))
                    #out_lista = codecs.open('semfiltro.txt', 'w')
                    #for fl in files:
                    #    out_lista.write(fl+'\n')
 
                if os.path.exists(folderout)==False:
                    os.mkdir(folderout)
                #obter arquivos ja processados
                files_ok = os.listdir(folderout)
                #print("processar todos los archivos de una carpeta in folder: %s" %files)
                for fil in tqdm.tqdm(files):
                    try:
                        if fil not in files_ok:
                            processar_onefile(folderin, folderout, fil, corrector, predictor, use_nltk)
                        else:
                            print("arquivo %s ja processado"%fil)
                    except Exception as e:
                        print('error in %s'%fil)
                        print(e)
            else:
                print("folder de entrada no existe")
