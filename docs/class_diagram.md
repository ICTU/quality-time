# Class diagram

This diagram is made using PlantUML so it can be implemented in Markdown. <br> More information about PlantUML can be found  here: <http://plantuml.com/index>

This diagram can be viewed using multiple different programms, plugins or online tools: <http://plantuml.com/running> <br> We used the online editor from PlantText <https://www.planttext.com>

```
@startuml

title Class Diagram Quality-time



package "REPORTS" #grey {
    together {
    class REPORT
    class MEASUREMENTS 
    class SUBJECTS
    class METRICS
    class TAGS
    class SOURCE_DEFINITION
    
    
    }
}

package "MEASUREMENTS" #white {
        class MEASUREMENTS
        class SOURCE_DATA
        }


REPORT "1" -- "many" SUBJECTS
SUBJECTS "1" -- "many" METRICS
METRICS "many" -- "many" TAGS
METRICS "1" -- "many" MEASUREMENTS
METRICS "1" -- "many" SOURCE_DEFINITION
SOURCE_DEFINITION "1" -- "many" SOURCE_DATA
SOURCE_DATA "many" -- "1" MEASUREMENTS

@enduml
```

# Class diagram as of March 7, 2019

![Class diagram as of 7 march 2019](https://www.plantuml.com/plantuml/img/TLB1Ze8m4BttAoRTCmV_G1Qx6qo4tRQSDuqsq0XgO8mXnd-t8iY8xXpQpdipdVUQpXiqDHwhaZ5qM5g8IjCqi70chqq5lqTJEcm3T9LbFWvclJMv1Ix5Jogrul2HrxQ5CmCVkCyj5hRkqtLtrRsI02iHgaoAbKYq0eAhx7Cf8gsUIhMC8uhey9kcAira9FuMuYjEOXsdISUDouLTY6WwsIi_5Gvjh_Mzl0arJ0jr-63y_Unk4VYCGn00hyokvQETuJ3X1s_zFi1ZGMVrmKvwYSRt9QylyuByqt5pHyvKs6mocitjRkC_pnK0)

## Explanation of diagram

A **report** has multiple **subjects**, and each **subject** can contain multiple **metrics**. Each metric has one or more **source definitions** that tell Quality-time where the data to measure a metric can be collected.

When the collector runs periodically, it collects **measurements** for each metric. A metric can have multiple sources defined for it, so in order to measure one metric, the collector has to collect **source data** for each source defined for the metric. The **source data** will be put in **measurements**. The measurement value is the sum of the source data values. In the frontend of the system, the report shows the latest measurements for each metric.  

**IMPORTANT NOTE**

The **tags** will be implemented on a later date and are not in use currently. The **tags** will eventually replace the functionality of **subjects** and expand on it. The goal of introducing the **tags** is to make filtering possible. 

*I.E. a user filters on the "security" tag, and in return only the **metrics** containing the "security" tag will be displayed and additionally there will be a graph generated containing a sum off all the "security" **metrics**. The "security" tag is one of the many **tags** that will be available for filtering.*



