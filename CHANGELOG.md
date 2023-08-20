## Version:1.1.2 -- 19 Aug 2023

The gpath_list.real_files method now returns missing files that were in the list.
## Version:1.1.1 -- 31 Jul 2023

* Remove the use of os.path.realpath to resolve symlinks, since it can make DCC asset paths diverge from the paths the uploader sees. (#14)

## Version:1.1.0 -- 19 Jul 2023

* Adds real_files method to gpath_list, which resolves folders and wildcards to real regular files only. Also adds a stat method to gpath which helps gpath_list to resolve real files as mentioned above.

### Version:1.0.3 -- 09 Dec 2022

* Adds the ability to remove entries from a PathList based on unix-style wildcard patterns. [c7db4ae]

### Version:1.0.2 -- 27 Sep 2022

* Faster deduplication. However it no longer removes files if a containing folder is present.

### Version:1.0.0 -- 08 Sep 2022

* Use unicode literals. [53faa83]
* Ignore venvs. [78d6b64]

### Version:0.2.0 -- 14 Jun 2022

* Adds a function to make a path relative to a start path. [bcd624c]

### Version:0.1.8 -- 07 Aug 2021

* Adds cwd normalization. [672da6c]
* Repair next() function for python 2+3 compatibility. [59681cc]

### Version:0.1.7 -- 27 Jun 2021

* Now supports a single dot (cwd) and handles relative normalization. [5e015ff]
* Repair py2+3 next() and removes the need to import builtins. [f3ad5fd]

### Version:0.1.6 -- 20 Jun 2021

* Fixed bug where relative paths that contained ".." would fail if the dots took them higher than
  the initial path component. [e2fca91]

### Version:0.1.5 -- 06 May 2021

* Adds property and tests to detect unc. [366140d]

### Version:0.1.4 -- 25 Mar 2021

* Adds dollar braces to context expansion. This helps for xgen scraping. [a217565]

### Version:0.1.3 -- 11 Mar 2021

* Add .circleci/config.yml. [21ea865]

### Version:0.1.1 -- 09 Mar 2021

* Adds unc path initialization. [20eaeed]

### Version:0.1.0 -- 20 Sep 2020

* Python 2 and 3 compatibility. [361ff3d]
* Gpath allow colons in paths. [320c3ce]
* Fix accidentally commented lines in test. [fa7c7a4]
* Adds remove_missing files method to gpath. [c41fc42]
* Repair some path list issues found while adding remove method. [5e527a1]
* Adds a remove method to pathlist with tests. [9821af4]
* Expander path list enhancements (#5)
* init path list with paths
* expander expands envvars
* test equality with ==
* Initial commit. [b41b155]

 
--