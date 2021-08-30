# cleptr

cgMLST profiling is a useful tool for describing relationships betwen genomic sequences from a range of bacteria. There are many tools which are available to generate these profiles. To date, cgMLST groupings are defined based on a heirarchical clustering approach of cgMLST profiles in order to group sequences, which are within a certain threshold that is meaningful to the user.

For the purpose of genomic epidemiology it is often desirable to maintain a consistent nomenclature of groups between analysis, this is not a straight forward problem when defining groups based on a heirarchical clustering approach. Since these clusters or groups are defined by the relationships between samples in the dataset and are likely to change over time, with clusters joining and splitting apart with the additon/removal of samples to the dataset. But the desire for a common name remains.

cleptr is a tool for maintaining a common nomenclature for cgMLST clusters for the purposes of public health surveillance. It is a tool which defines rules of when a cluster name may be carried through from one analysis to another and when the assignment of a new name is required. 

_Names may be carried through from one analysis to another when_

* no new sequences are added to a cluster following new analysis.
* only NEW (and/or previously unclustered) sequences are added to a cluster following a new analysis.


_New names need to be assigned when_

* A new cluster is formed containing only new (and/or previously unclustered) sequences
* Following a new analysis a new group is formed that contains sequences from two or more previously named clusters ( +/- new sequences added in that analysis).
    * In this case the name of the previous clusters is archived and not re-used to avoid confusion.



