
# MIO - Feasibility study for a multi-(thread|process) I/O package

## Concepts

The package uses a "Channel" for each thread/process to do the actual writing independently from each other. Each thread
or process writes into it's own channel. Writing can be done in "transactions" on the level of the channel to ensure
consistency in each file, and/or on the whole dataset to ensure consistency across all channels. Ideally the channel
implements all the corresponding file/stream interfaces at API level of the selected language.

A set of channels is "packaged" into a "Dataset" which contains all data written by the various threads/processes.
Some "metadata" is stored in the Dataset, initially the number of channels used in writing. This info can be used
for performance optimisation (e.g. to adjust the number of reading threads accordingly) or otherwise. Other parts
of the metadata may be used to recover transactions, or incomplete writes (e.g. when the writer crashes).

As an initial metaphor (and in this python based implementation) a dataset is mapped to a directory, each channel
to a sub-dir which contains a file (the actual data file) and a buffer (which could also be in memory), and possibly
also a transaction buffer. Writing is done via a buffer which is of a fixed (adjustable) nominal size. Once the buffer
is full it is appended to the actual data file (or the transaction buffer, which itself is appended to the file at
the next "commit"). This way, even if there is a crash of a thread, the content of the main file is not affected and
still consistent. For performance reasons, the buffer may be suppressed, if needed.

Transactions can be used on each channel independently (e.g. to ensure that always only fully processed events are
stored). Alternatively, transactions can be triggered on the dataset as a whole (all channels will get the transaction
in parallel, so it acts also as a synchronization point), this can be useful in the case of multiple threads handling
sub-detector information from the same event to ensure that the information in the dataset is consistent on an event
basis.

When closing the dataset, each channel is closed and a configurable action can be triggered for each channel (e.g. to
compress the datafile for the channel) and the dataset as a whole, e.g. to "package" all files into a tarball for easier
handling in further processing steps (e.g. copying over to other machines or into an archive). Actions like this should
be OK for smaller datasets, for performance reasons it's unlikely that they will be configured for large (>>1GB) datasets.


## Feasibility study

To see how this could work, a small python package ("MIO") has been created containing the Dataset and Channel classes.
Examples are the `testWriter.py` and `testReader.py` files in the `test/` subdir.

## Use cases

- writing events from multi-threaded event processing with full events per thread
- writing collections from multi-threaded event processing, each event uses several threads for sub-detector processing
  (e.g. tracking, calorimeter, trigger, muon reconstruction in four (or more) separate threads).


## C++

An obvious "translation" of this concept to C++ would derive the channels from the fstream classes to allow the most
compatibility. Also for this language implementation the dataset uses directories to separate and manage the channels.
In a further abstraction, the concept could be "translated" to inodes into device drivers running in kernel space, this
way enhancing the performance even further, to the extreme of providing a POSIX compliant multi-threaded storage solution.


## Very preliminary results of testWriter.py:

Using `threading` `Thread`s for the parallel writing (which throttles due to the GIL):

{ "nwords": { nthreads : time to write nwords with nthreads threads, ...}

{  10000.0: {1: 0.0818021297454834,   2: 0.11968088150024414,   4: 0.18979191780090332,  10: 0.15385699272155762},
  100000.0: {1: 0.823232889175415,    2: 1.2277209758758545,    4: 1.5946218967437744,   10: 1.5612168312072754},
 1000000.0: {1: 8.799837827682495,    2: 12.32905101776123,     4: 16.06791114807129,    10: 15.936131000518799}}

and indeed a slowdown about a factor of two.

Using `multiprocessing` `Process`es it is:

{  10000.0: {1: 0.0839390754699707,  2: 0.03995084762573242,  4: 0.0334630012512207,  10: 0.0348360538482666},
  100000.0: {1: 0.7741169929504395,  2: 0.4373040199279785,   4: 0.28017687797546387, 10: 0.19591999053955078},
 1000000.0: {1: 7.910866975784302,   2: 4.279528856277466,    4: 2.8022449016571045,  10: 2.1032071113586426}}

on the same 4-core box (2013 MBPro, 4-core, SSD), so about a factor of 4 speedup in the limit. :)

Reading the last dataset (1M "words" written with 10 threads) in a single-threaded (sequential) manner
takes 0.046 sec (~161MB/s).