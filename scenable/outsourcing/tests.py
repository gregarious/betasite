
import logging
logging.disable(logging.CRITICAL)

# import all the test cases from the apitools subpackage
from scenable.outsourcing.apitools.tests import FacebookGraphTest, FactualResolveTest, GoogleGeocodingTest

# import test cases from various subclasses
from scenable.outsourcing.subtests.places import FactualResolutionTest, GoogleResolutionTest
from scenable.outsourcing.subtests.fbpages import PagePullingTest, OrgStorageTest, OrgImportingTest, PlaceStorageTest, PlaceImportingTest
from scenable.outsourcing.subtests.fbevents import EventStorageTest, EventImportingTest
from scenable.outsourcing.subtests.icalevents import ICalEventTest