## Hybrid Simplification using Deep Semantics and Machine Translation

Sentence simplification maps a sentence to a simpler, more readable
one approximating its content. In practice, simplification is often
modeled using four main operations: splitting a complex sentence into
several simpler sentences; dropping and reordering phrases or
constituents; substituting words/phrases with simpler ones.

This is implementation from our ACL'14 paper. We have modified our
code to let you choose what simplification operations you want to
apply to your complex sentences. Please go through our paper for more
details. Please contact Shashi Narayan
(shashi.narayan(at){ed.ac.uk,gmail.com}) for any query.

If you use our code, please cite the following paper. 

**Hybrid Simplification using Deep Semantics and Machine Translation,
  Shashi Narayan and Claire Gardent, The 52nd Annual meeting of the
  Association for Computational Linguistics (ACL), Baltimore,
  June. https://aclweb.org/anthology/P/P14/P14-1041.pdf.**

> We present a hybrid approach to sentence simplification which
> combines deep semantics and monolingual machine translation to
> derive simple sentences from complex ones. The approach differs from
> previous work in two main ways. First, it is semantic based in that
> it takes as input a deep semantic representation rather than e.g., a
> sentence or a parse tree. Second, it combines a simplification model
> for splitting and deletion with a monolingual translation model for
> phrase substitution and reordering. When compared against current
> state of the art methods, our model yields significantly simpler
> output that is both grammatical and meaning preserving.

### Requirements

* Boxer 1.00:  http://svn.ask.it.usyd.edu.au/trac/candc/wiki/boxer
* Moses: http://www.statmt.org/moses/?n=Development.GetStarted
* Mgiza++:  http://www.statmt.org/moses/?n=Moses.ExternalTools#ntoc3
* NLTK toolkit: http://www.nltk.org/
* Python 2.7
* Stanford Toolkit: http://nlp.stanford.edu/software/tagger.html

### Data preparation


#### Training Data 

* code: ./preprocessing/extract_wikipedia_corpora_boxer_training.py

* This code prepares the training data. It takes as input tokenized
  training (complex, simple) sentences and the boxer output (xml
  format) of the complex sentences.

* I will improve the interface of this script later. But for now you
  have to set following parameters: (C: complex sentence and S: simple
  sentence)

  * ZHUDATA_FILE_ORG = Address to the file with combined
  complex-simple pairs. Format:
  C_1\nS^1_1\nS^2_1\n\nC_2\nS^1_2\nS^2_2\nS^3_2\n\n and so on.

  * ZHUDATA_FILE_MAIN = Address to the file with all tokenized complex
   sentences. Format: C_1\nC_2\n and so on.

   * ZHUDATA_FILE_SIMPLE = Address to the file with all tokenized
   simple sentences. Format: S^1_1\nS^2_1\nS^1_2\nS^2_2\nS^3_2\n and
   so on.

   * BOXER_DATADIR: Directory address which contains the boxer output
   of ZHUDATA_FILE_MAIN.

   * CHUNK_SIZE = Size of the boxer output chunks. The above scripts
   loads boxer xml file before parsing them, it is much faster to use
   chunks (let say of 10000) of ZHUDATA_FILE_MAIN.

   * boxer_main_filename = Boxer output file name pattern. For
   example:
   filename."+str(lower_index)+"-"+str(lower_index+CHUNK_SIZE)
        
#### Test Data
    
* code: ./preprocessing/extract_wikipedia_corpora_boxer_test.py

* This code prepares the test data. It takes as input tokenized test
  (complex) sentences and their boxer outputs in xml format.

* I will improve the interface of this script later. But for now you
  have to set following parameters: 

  * TEST_FILE_MAIN: Address to the file with all tokenized complex
   sentences. Format: C_1\nC_2\n and so on.

  * TEST_FILE_BOXER: Address to the boxer xml output file for
   TEST_FILE_MAIN.

### Training

* Training goes through three states: 1) Building Boxer training
  graphs, 2) EM training and 3) SMT training

python start_learning_training_models.py --help

usage: python learn_training_models.py [-h] [--start-state Start_State]
:                                       [--end-state End_State]
:                                       [--transformation TRANSFORMATION_MODEL]
:                                       [--max-split MAX_SPLIT_SIZE]
:                                       [--restricted-drop-rel RESTRICTED_DROP_REL]
:                                       [--allowed-drop-mod ALLOWED_DROP_MOD]
:                                       [--method-training-graph Method_Training_Graph]
:                                       [--method-feature-extract Method_Feature_Extract]
:                                       [--train-boxer-graph Train_Boxer_Graph]
:                                       [--num-em NUM_EM_ITERATION]
:                                       [--lang-model Lang_Model]
:                                       [--d2s-config D2S_Config] --output-dir
:                                       Output_Directory

Start the training process.

optional arguments:
:  -h, --help            show this help message and exit
:  --start-state Start_State
::                        Start state of the training process
:  --end-state End_State
::                        End state of the training process
:  --transformation TRANSFORMATION_MODEL
::                        Transformation models learned
:  --max-split MAX_SPLIT_SIZE
::                        Maximum split size
:  --restricted-drop-rel RESTRICTED_DROP_REL
::                        Restricted drop relations
:  --allowed-drop-mod ALLOWED_DROP_MOD
::                        Allowed drop modifiers
:  --method-training-graph Method_Training_Graph
::                        Operation set for training graph file
:  --method-feature-extract Method_Feature_Extract
::                        Operation set for extracting features
:  --train-boxer-graph Train_Boxer_Graph
::                        The training corpus file (xml, stanford-tokenized,
::                        boxer-graph)
:  --num-em NUM_EM_ITERATION
::                        The number of EM Algorithm iterations
:  --lang-model Lang_Model
::                        Language model information (in the moses format)
:  --d2s-config D2S_Config
::                        D2S Configuration file
:  --output-dir Output_Directory
::                        The output directory

* Have a look in start_learning_training_models.py for more
information on their definitions and their default values.

* train-boxer-graph: this is the output file from the training data
  preparation·

### Testing

python start_simplifying_complex_sentence.py --help

usage: python simplify_complex_sentence.py [-h]
:                                           [--test-boxer-graph Test_Boxer_Graph]
:                                           [--nbest-distinct N_Best_Distinct]
:                                           [--explore-decoder Explore_Decoder]
:                                           --d2s-config D2S_Config
:                                           --output-dir Output_Directory

Start simplifying complex sentences.

optional arguments:
:  -h, --help            show this help message and exit
:  --test-boxer-graph Test_Boxer_Graph
::                        The test corpus file (xml, stanford-tokenized, boxer-
::                        graph)
:  --nbest-distinct N_Best_Distinct
::                        N Best Distinct produced from Moses
:  --explore-decoder Explore_Decoder
::                        Method for generating the decoder graph
:  --d2s-config D2S_Config
::                        D2S Configuration file
:  --output-dir Output_Directory
::                        The output directory

* test-boxer-graph: this is the output file from the test data
  preparation·

* d2s-config: This is the output configuration file from the training
  stage.

### ToDo

* ToDo: Incorporate improvements from our arXiv
 paper. http://arxiv.org/pdf/1507.08452v1.pdf

      * OOD words at the border should be dropped.
      * Don't split at "TO".
      * Full stop at the end of the sentence. (currently, this was done as a
              post-processing step in the end).
       
* ToDo: Change to online version of sentence simplification.

