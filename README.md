## Hybrid Simplification using Deep Semantics and Machine Translation

Sentence simplification maps a sentence to a simpler, more readable
one approximating its content. In practice, simplification is often
modeled using four main operations: splitting a complex sentence into
several simpler sentences; dropping and reordering phrases or
constituents (); substituting words/phrases with simpler ones.

This is implementation from our ACL'14 paper. Please go through our
paper for more details. Please contact Shashi Narayan
(shashi.narayan(at){ed.ac.uk,gmail.com}) for any query.

If you use our code, please cite the following paper. 

* Hybrid Simplification using Deep Semantics and Machine Translation,
  Shashi Narayan and Claire Gardent, The 52nd Annual meeting of the
  Association for Computational Linguistics (ACL), Baltimore,
  June. https://aclweb.org/anthology/P/P14/P14-1041.pdf

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





### Requirements

* Boxer 1.00: 
* Moses: http://www.statmt.org/moses/?n=Development.GetStarted
* Mgiza++:  http://www.statmt.org/moses/?n=Moses.ExternalTools#ntoc3
* NLTK toolkit 
* Python 2.7
* Stanford Toolkit