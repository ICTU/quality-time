"""Base classes for JMeter CSV collectors."""

from ..source_collector_test_case import SourceCollectorTestCase


class JMeterCSVTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for JMeter CSV collector unit tests."""

    SOURCE_TYPE = "jmeter_csv"
    JMETER_CSV = """timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,\
    bytes,sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect
1638325618779,57,/home,500,Internal Server Error,Thread Group 1-1,text,false,,\
    389,717,1,1,https://app.example.org/home,54,0,38
1638325618967,360,/api/search,200,OK,Thread Group 1-1,text,true,,\
    60221,726,1,1,https://app.example.org/api/search,359,0,0
1638325618694,544,Test,,"Number of samples in transaction : 2, number of failing samples : 1",Thread Group 1-1,,\
    false,,61338,6131,1,1,null,540,96,38
1638325624692,10,/home,404,Not Found,Thread Group 1-2,text,true,,\
    389,717,1,1,https://app.example.org/home,10,0,4
1638325734752,1214,/api/search,200,OK,Thread Group 1-2,text,true,,\
    274377,721,1,1,https://app.example.org/api/search,1207,0,0
1638325624689,1272,Test,,"Number of samples in transaction : 2, number of failing samples : 1",Thread Group 1-2,,\
    false,,275531,6114,1,1,null,1265,11,4
"""
