# Changelog

All notable changes to this project will be documented in this file.  
Types of changes:
- ```Added``` for new features.
- ```Changed``` for changes in existing functionality.
- ```Deprecated``` for soon-to-be removed features.
- ```Removed``` for now removed features.
- ```Fixed``` for any bug fixes.
- ```Security``` in case of vulnerabilities.

The format is based on [Keep a Changelog](http://keepachangelog.com/)

## 2019-11-11
### Added
- Added `Stream Configurator UI` function and documentation.
### Changed
- Modified configuration of the `Basic Reidentification`.

## 2019-10-19
### Added
- Added new optional parameter of `Multi Graph Runner` miroservice: frame_period_ms.
- Added `Time Synchronization Using NTP` chapter into the documentation.
- Added `UVAP Web Player Access from Client Machine` chapter into the documentation.
- Added `Video Annotation` function and documentation.
### Changed
- Restructured the UVAP documentation.
- Remove all `xhost +` occourrences from the documentation.

### Fixed
- Renamed from 'run_web_player.sh' script to 'run_uvap_web_player.sh' in the documentation.
- Fixed `Invalid input may cause Pass Detection to crash` bug.


## 2019-09-05
### Added
- Added `Basic Reidentification` microservice to the Docker repository (ultinous/uvap). 
- Added `Basic Reidentification` demos into `Quick Start Guide`. 
- Added `Basic Reidentification` microservice documentation into the `Developer's Guide`.
- Added USB webCam (like Brio) usage to the run_mgr.sh. 
- Added 'Required packages' chapter into the `Insall Guide`.
### Changed
- Unified run_*.sh scripts for MS starting in /uvap/scripts directory. 
### Fixed
- Fixed license vs. licence typo in the documentation.
- Fixed: Images of demo (written by MGR) are original not lowres in Kafka.
- Fixed: the javaproperties install is missing from 'Environment for Python Developers' chapter. 

## 2019-08-14
### Added
- Added `Kafka Pass Detection` microservice to the Docker repository (ultinous/uvap). 
- Added `Kafka Pass Detection` demo into `Quick Start Guide`. 
- Added `Kafka Pass Detection` microservice documentation into the `Developer's Guide`.
- Added an 'Update' chapter to the `Install Guide`.
### Changed
- Refactored the structure of `Quick Start Guide`.
- Change configuration file for multi camera usage (Jinja templates).
### Fixed
- Fixed security issue in 'Environment for Python Developers' chapter, 'pip3 install' command is not required the sudo privilage.
- Dropped display related lines from run_demo.sh.
- Fixed: the `Web Player` ignores advertised host and port in index page.
- Fixed: the nvidia-docker-binary-path parameter is not required in demo starter script.

## 2019-07-25
### Added
- Added `Web Player` microservice to the Docker repository (ultinous/uvap).
- Added `Kafka Tracker` microservice to the Docker repository (ultinous/uvap). 
- Added `Kafka Tracker` demo and usage of `Web Player` into `Quick Start Guide`.
- Added `Kafka Tracker` microservice documentation into the `Developer's Guide`.
- Added 'Cross references' and 'Environment for Python Developers' sections into the `Developer's Guide`.
- Added 'Notations of the UVAP Documentation' chapter for the documentation.
- Added 'Example Analysis Results' chapter for the documentation.
- Added 'Example Analysis Results' components (zookeeper-data, kafka-data) to the Docker repository (ultinous/kafka_demo).
### Changed
- Changed `Demo Applications`, now it can write the result images (.jpg) into the Kafka.
- Highlight the 'Overview' in the home page of the documentation.
- Parameterized the retention time setter script (set_retention.sh).
### Fixed
- Completed the `Install Guilde` with some technical details for the better efficiency.
- Fixed some typos in the `Install Guilde`.

## 2019-07-01
### Added
- Added the `Quick Start Guide`, it is a step-by-step description of `Demo Applications` confiration and usage.
- Added `Demo Applications` with the following features:
    - Head detection
    - 3D Head pose
    - Demography
    - List topic (from Kafka stream)
    - List message (from Kafka stream)
    - Show Image (from Kafka stream)
    - Visualise the human skeleton
### Changed
- Added 'Table of contents' to the `Install Guide`.
- In `Install Guide` created the 'Acquiring the private resources' chapter for less required communication between Provider and Customer.  
- Changed `git repository` of UVAP documentation.
- Changed `install.sh` script for easier set up process. 
### Removed
- Reorganized our `Example Scripts` to `Demo applications`

## 2019-06-03
### Added
- Added the `Multi Graph Runner (MGR)` (uvap_mgr) microservice to the Docker repository (ultinous/uvap). 
- Added `Install Guide`, it contains all requirements and set up procss of UVAP.
- Added `Developer's Guide`, it is technical details from Kakfa, Docker and our microservice.
- Added a script which list message from Kafka stream into `Example Scripts`. 
- Added a script which show head or full body bounding boxes on Image into `Example Scripts`.
- Added a script which display image from Kafka into  `Example Scripts`.

