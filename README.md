# Excel Sheet baseline.xlsx Explanation
## NodeID
Contains the mapping for all the nodes in the graph. 
Col A contains the node numbering. 
Col B contains the Name of the node. 
Col C indicates the type of node: C for collection center, R for remanufacturing facility, M for manufacturing facility, and L for Landfill. 
Col D is the base facility cost.
Col E is the operational cost.
Col F is the predicted supply number of parts from the collection facility.
Col G is the capacity of a remanufacturing facility
Col H is the kg of supply from each collection center (Col F*25).
Col I is the land cost factor for the facility based on farm land costs.
Col J facility cost (Col D * Col I)
Col K demand of the manufacturing facility
Col L is the kg of supply from each collection center
Col M contains the mutliplier for supply.
Col N - W contains 10 scenarios.

## Node_stochastic_10, Node_stochastic_20, Node_stochastic_30, Node_stochastic_40, Node_stochastic_50
Contain the data for the stoachastic runs. 

## distanceMatrixCtoR
The matrix for the distances for collection nodes to remanufacturing nodes.

## distanceMatrixRtoM
The matrix for the distances for remanufacturing nodes to manufacturing nodes.

## Population
The location latitude and longitude for each node.

## emissionsCtoR
The matrix for the emissions for collection nodes to remanufacturing nodes.

## emissionsRtoM
The matrix for the emissions for remanufacturing nodes to manufacturing nodes.

## emissionsCtoR_adapt and emissionsRtoM_adapt
Unit conversion for emissions.
