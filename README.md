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

### Current Status

* Transformation model is retested for both training and testing.

* ToDo: Test the moses model.  

* ToDo: Test if we successfully incorporated improvements from our
 arXiv paper. http://arxiv.org/pdf/1507.08452v1.pdf

      * OOD words at the border should be dropped and don't split at "TO".

* ToDo: Change to online version of sentence simplification.

* ToDo: Upload small set of training and test sets. 

### Requirements

* Boxer 1.00:  http://svn.ask.it.usyd.edu.au/trac/candc/wiki/boxer
* Moses: http://www.statmt.org/moses/?n=Development.GetStarted
* Mgiza++:  http://www.statmt.org/moses/?n=Moses.ExternalTools#ntoc3
* NLTK toolkit: http://www.nltk.org/
* Python 2.7
* Stanford Toolkit: http://nlp.stanford.edu/software/tagger.html