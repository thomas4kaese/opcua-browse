# opcua-browse

## description
opcua_browse.py is a small script for crawling an OPC-UA server. It returns available NodeIds and and stores them in a CSV file.

The obtained data is suitable for direct adressing certain nodes of interest.

## usage
- edit connection in l. 13
- edit l. 17 in order to change starting point for browsing
- run opcua_browse.py
- check output.csv for desired nodes

## output data
- output.csv with 4 cols: number,  node name, NodeId "ns=<namespaceIndex>;<identifiertype>=<identifier>" with string identifiertype "s=", datatype
