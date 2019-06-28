# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.2.2] - [2019-06-28]

### Fixed

- Version number was missing in the footer of the frontend. Fixes #410.

## [0.2.1] - [2019-06-26]

### Fixed

- Work around a limitation of the Travis configuration file. The deploy script doesn't allow sequences, which is surprising since scripts in other parts of the Travis configuration file do allow sequences. See https://github.com/travis-ci/dpl/issues/673.

## [0.2.0] - [2019-06-26]

### Added

- Release Docker containers from Travis CI.

## [0.1.0] - [2019-06-24]

### Added

- Initial release consisting of a metric collector, a webserver, a frontend, and a database component.
