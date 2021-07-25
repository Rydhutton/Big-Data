Big-Data WIP

This is a multi-part programming and a systems configuration project leveraging technologies such as VMWare ESXi 6.7 Hypervisor for Systems Hosting with full AD:DS and MySQL running between VMs configured for data duplication storage. The production code only includes the collector at the moment, but is running and storing the users that have triggered the algorithm.

Collector: The collector's job is to find targets that meet a classification criteria to then be further analyzed for possibility of being accepted as future training data for the machine learning algorithm. It does this by storing the username of a Redditor into a SQL database as well as age and gender based information which can then later easily be recontructed back into a class object which includes the Redditor instance.
Analyzer: Not Implemented<br />
Trainer: Not Implemented<br />
Classifier: Not Implemented<br />
