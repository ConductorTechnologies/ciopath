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