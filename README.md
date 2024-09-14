# Caucasus focused Data Pipeline for Natural Language Processing(NLP)

## Description

This repository contains a data pipeline for monolingual and parallel corpuses used for Neural Machine Translation (NMT) and Speech To Text Tasks (STT). The data, which includes around 100 thousand parallel sentences, 100 thousand parallel words for Abkhazian-Russian pairs, and around 1.4 million sentences monolingual Abkhazian corpus, is sourced from various websites, ebooks, and a dictionary. Our team has obtained permissions from the content owners to open source all the text.

## Data ETL Pipeline

The data pipeline involves the process of extraction, transformation, and loading (ETL) to prepare the data for training neural network models.

### Extraction (This step is done for you, the information is provided in case)

The data acquisition process involves extracting information from various sources, employing diverse techniques to ensure comprehensive coverage. Specifically, the data is obtained through dictionary parsing using the `parse_dictionary.py` script.

For web content, a web scraping methodology is implemented, leveraging Scrapy spiders to simultaneously extract data from parallel web pages. Additionally, [`hunalign`](https://github.com/danielvarga/hunalign) is employed to perform heuristic text alignment across pages, optimizing the alignment process, the scripts can be found in the `scrapy` folder.

Furthermore, the content from ebooks is directly extracted from PDF documents.

### Transformation

The text is cleaned up to remove noise and identify outliers using Python and Shell scripts. This process involves feedback from 3 human evaluators and the implementation of random sampling for inferential statistics to identify outliers and potential sources of noise. Statistics can be found in the `data/stats` folder.

![excert of a stats file](data/stats/p_15_39_94k.astanda.png)

Different hyperparameters such as sentence length are used to filter out sentences. This process is repeated until a 95% accuracy is reached, meaning the sentences contain less than 5% error rate, including syntactical, grammatical, and semantical errors.

### Loading

The cleaned-up data is aggregated into a single file, ready to be passed further down the line for Natural Language Processing(NLP) tasks.

## Transform and load Abkhazian-Russian parallel data

```bash
git clone https://github.com/danielinux7/Abkhaz-NLP-Data-Pipeline.git
cd Abkhaz-NLP-Data-Pipeline
bash getclean_ab_ru.sh
```

## Transform and load Abkhazian Monolingual data

```bash
git clone https://github.com/danielinux7/Abkhaz-NLP-Data-Pipeline.git
cd Abkhaz-NLP-Data-Pipeline
bash getclean_ab.sh
```

The data will be created in the `clean` folder, the scripts will take some time to run(15-30min).

## Optional: Data augmentation

```bash
git clone https://github.com/danielinux7/Abkhaz-NLP-Data-Pipeline.git
cd Abkhaz-NLP-Data-Pipeline/tools
```

We can compose a specific, shuffled training corpus, separate test files, and generate paraphrases among other options with the joined corpus script: `python3 join_corpus.py --help`

```text
usage: join_corpus.py [-h] [--dictionary] [--numerate] [--paraphrase]
                          [--verbose] [--random] [--punctuation]
                          [--only_paraphrase] [--paraphrase_rare_words]
                          ll [ll ...] min_ratio max_ratio min_length max_words
                          paraphrase_scale test_lines valid_lines
                          common_words_threshold corpus_file

Process the corpus with paraphrases and the dictionary

positional arguments:
      ll                    the lengths for dictionary lists
      min_ratio             We only use translation with this minimum ratio
      max_ratio             We only use translation with this maximum ratio
      min_length            We only use translation with this minimum length
      max_words             We only use translation with this maximum words
      paraphrase_scale      Definies how many paraphrases are generated per
                            sentence pair.
      test_lines            We define the number of lines that are filtered for
                            the test set.
      valid_lines           The number of lines that are filtered for the
                            validation set.
      common_words_threshold
                            We define the threshold for the common word
                            classification.
      corpus_file           We define the path to the aligned corpus file.

optional arguments:
      -h, --help            show this help message and exit
      --dictionary          We use the dictionary lists as an additional
                            translation source.
      --numerate            The dictionary list has a numeration
      --paraphrase          We paraphrase the filtered training corpus.
      --verbose             We print the filtered lines to the terminal.
      --random              We randomize the corpus before splitting it into the
                            training, validation and test sets.
      --punctuation         We use the punctuation criteria as filter in such way
                            that each translation have the same order of sentence
                            signs. The sentence signs are ".:!?0-9…()[]«»".
      --only_paraphrase     We simply generate paraphrases and don't store the
                            original translations into the output file.
      --paraphrase_rare_words
                            We only generate paraphrases with rare words.
```

For example `python3 join_corpus.py 10 0.75 1.33 10 50 5 500 500 1 ru_ab_sample.tsv --paraphrase_rare_words --punctuation --random` results in the commited `<date>_corpus` with a minimum range of 10 letters, max 50 words, a min ratio of 0,75 (3/4) and max ratio of 1,33 (~4/3). Maximum 5 paraphrase pairs are generated per sentence pair. The paraphrases are based on the filtered, training copus and are joined with the lists of dictionary entries - if we set the dictionary flag. Other compositions are possible with the described arguments. It is a good practice to firstly figure out the filter and dictionary list parameters, because the praphrase generation will take several minutes.
