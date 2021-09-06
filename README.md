# sOCRates
## _A post-OCR text correction method_

sOCRates is a post-OCR text correction method that relies on contextual word embeddings and on a classifier that uses format, semantic, and syntactic similarity features.

## Edit distance adapted to OCR error detection
Similarity function based on the Levenshtein distance, changing the way the weights are assigned to the substitutions.
![stack Overflow](https://github.com/dannysv/sOCRates/blob/master/Edit_distance_adapted_for_OCR.png)

## Configuration

- Download the repository
- Create a virtual enviroment 
- Install the requirements by using the reqs.txt file
- Install and configure Aspell for portuguese
- Download data (unigrams, bigrams and word-embeddings model) and place it in word_correction folder
```
	https://mega.nz/file/a2xwlDaT#x3wjns6doZaqs6Q2wcTC3-JxUr0UeU26eoPdHJho-84
```
- Download the fine-tuned Bert model
```
	https://mega.nz/file/enIVFSCQ#tJtk4_1OpkMNX-ga_HZYdi7GKL4VQun4iNWYaZOTPjg
	https://mega.nz/file/r2ZB1QZL#LC7jjKSB361gGzS0Jfj6QBcBcKc5W5ny4dUpkJXY_ms
```	

## Example usage
```
- python corrigir.py --folderin ./arquivosxml --folderout ../saida --xml 1 --use_nltk 0 --lista_filtro ../filtro.json 
```
### Arguments
- folderin .- The folder with the data to be processed. This folder could contain xml and txt files
- folderout .- The folder where the output will be placed.
- xml .- Argument to know if sOCRates should process xml or not
- use_nltk .- Argument to know if sOCRates should use the NLTK toolkit or not
- lista_filtro .- Path to the json file with a list of files to be skipped.
