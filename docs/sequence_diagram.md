# Sequence diagram

This diagram is made using PlantUML so it can be implemented in Markdown. <br> More information about PlantUML can be found over here: <http://plantuml.com/index>

This diagram can be viewed using multiple different programms, plugins or online tools: <http://plantuml.com/running> <br> We used the online editor from PlantText <https://www.planttext.com>

```
@startuml

title Sequence Diagram of Quality Time.

participant FRONTEND order 10
participant COLLECTOR order 20
participant SOURCES order 30
participant SERVER order 40
participant DATABASE order 50
|||
loop periodically
    COLLECTOR -[#red]> SERVER: Request all metrics
    SERVER -[#red]> DATABASE: Read all metrics
    DATABASE -[#blue]> SERVER: Return all metrics
    SERVER -[#blue]> COLLECTOR: Return all metrics
|||
    loop for every metric
        loop for each metric source 
            COLLECTOR -[#red]> SOURCES: Request source data
            SOURCES -[#blue]> COLLECTOR: Return source data
        end
        COLLECTOR -[#red]> SERVER: Post measurement for the metric
        SERVER -[#red]> DATABASE: Store measurement
    end
end

|||

FRONTEND -[#red]> SERVER: Request report
SERVER -[#red]> DATABASE: Read report
DATABASE -[#blue]> SERVER: Return report
SERVER -[#blue]> FRONTEND: Return report

loop for every metric in the report
    FRONTEND -[#red]> SERVER: Request measurements for metric
    SERVER -[#red]> DATABASE: Read measurements
    DATABASE -[#blue]> SERVER: Return measurements
    SERVER -[#blue]> FRONTEND: Return measurements
end

|||

@enduml
```

# Sequence diagram as of 28 febraury 2019

![Sequence diagram as of 28 february 2019](https://www.plantuml.com/plantuml/img/ZLHDJuD04BtlhvZ4iwP-NJoOrXPFJL50BwQ75QPsauN5OTUaIN-y2owKxHUIa92yzsRcpPimhZGdRNB9c1PQ8iJuRR184MQ2Vn7FGQtWrN0fz0OIaUCLOwLLY5IKlD3m78MB95ZCG5661DSZ3vs6ytamJSB8mJS-78TlqJI87NYx1mRHUz0AxtniDaacJvCuSEZzY6stMoQLAg544YeJAPTomy0-knakFou8i-MZA_q0KUsrqc2vaACcaLQDnBNk-6sxMi6p0tetZHLyIeDU1sseEDF0yRiXZqfgSxMiCRXI1FY3j75mW_WeJzSEX4ePic5sf5CR-KjYjnAdoxZcdhQDxDpenxHOPEnSVxUl5sLxvyWhGvYZJRhsezUux_LqGh5MXFqIh6rVlyqgMNUq9o-2i5IasS0XEDPm_WVb7AqTP9_8ZYODecXsuKYrhs4dlKrKJSNU9WVizQN_FFG3oR1bJxBBQ6m_xM_f5m00)

## Explanation of diagram

When the user opens the dashboard of Quality-Time, the **frontend** gets loaded. After the **frontend** is loaded, the user can open a report. The **frontend** will create a GET request to the **server** requesting the report. The **server** will also make GET request to the **database**. The **database** will in return do a POST request to the **server** with the report data. After this the **server** will do a POST request to the **frontend** with the report data. This shows that the Server is the central point of communication, every component only talks to the **server** and **not with eachother**.  

After you open the report, there will be metrics in this report. For every metric the **frontend** will make a GET request to the **server** asking for the measurements for the metric. The **server** then will make a GET request to read the measurements to the **database**. The **database** will make a POST request back to the **server** containing the measurements. The **server** then will make POST request back to the **frontend** containing themeasurements.  

In the background there is a mechanism that will ensure that the reports are up to date with the latest information available from the **sources**. This mechanism is called the **collector**. The **collector** runs in a loop periodically. When this loop starts the **collector** makes a GET request to the **server** asking for all the metrics. The **server** then makes a GET request to the **database** asking for all the metrics. After this request the **database** returns all the metrics using a POST request to the **server**. The **server** then passes this data containing all the metrics to the **collector**. After this part is finished of the loop the next part starts, which also is a loop. This loop runs on every metric that got returned earlier in the loop. Inside this second loop there is a third loop, this third loop runs for each of the metric its sources. In this third loop the **collector** does a GET request for source data to the **sources** of the metrics. Then the **sources** return source data to the **collector** using a POST request. Now the third loop is finished it can continue the second loop. In the second loop the **collector** will make a POST request to the **server** containing all the measurments for the metric. And the **server** will make a POST request to the **database** for storing the measurements. 

