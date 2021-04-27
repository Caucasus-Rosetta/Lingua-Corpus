###### Composition of a training corpus with a local repository
Firstly clone this repo with`git clone https://github.com/danielinux7/Multilingual-Parallel-Corpus.git` and go to the tool folder: `cd tools`

Then we can compose a specific, shuffled training corpus and separate test files with the joined corpus script in the training directory: `python3 join_corpus.py --help`

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

For example `python3 join_corpus.py 10 0.75 1.33 10 50 5 500 500 1 ru-ab-parallel-27-07.bifixed --paraphrase_rare_words --punctuation --random` results in the commited `06-19-2020_corpus` with a minimum range of 10 letters, max 50 words, a min ratio of 0,75 (3/4) and max ratio of 1,33 (~4/3). Maximum 5 paraphrase pairs are generated per sentence pair. The paraphrases are based on the filtered, training copus and are joined with the lists of dictionary entries - if we set the dictionary flag. Other compositions are possible with the described arguments. It is a good practice to firstly figure out the filter and dictionary list parameters, because the praphrase generation will take several minutes.
