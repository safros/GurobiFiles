import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd
import folium

xls=pd.ExcelFile("baseLine.xlsx")
nodeIds=pd.read_excel(xls,"Node_stochastic_10")
dijRtoM=pd.read_excel(xls,"distanceMatrixRtoM")
dijCtoR=pd.read_excel(xls, "distanceMatrixCtoR")
gijRtoM=pd.read_excel(xls,"emissionsRtoM_adapt")
gijCtoR=pd.read_excel(xls, "emissionsCtoR_adapt")
populationInfo=pd.read_excel(xls,"Population")
SCENARIONUM=10
kmPerKg=0.0003335
MAX_NUM_FACILITIES=4

#collectionNumNodes=[0,1]
tempdf=nodeIds.loc[nodeIds['type'] == "C"]
collectionNumNodes=np.asarray(tempdf['nodeNum'])

#remanufacturingNumNodes=[2,3]
tempdf=nodeIds.loc[nodeIds['type'] == "R"]
remanufacturingNumNodes=np.asarray(tempdf['nodeNum'])
rNodeNumToy_i=remanufacturingNumNodes[0]

#manufacturingNumNodes=[4,5]
tempdf=nodeIds.loc[nodeIds['type'] == "M"]
manufacturingNumNodes=np.asarray(tempdf['nodeNum'])
numManufacturing=manufacturingNumNodes[0]

#landfillNumNodes=[6,7]
tempdf=nodeIds.loc[nodeIds['type'] == "L"]
landfillNumNodes=np.asarray(tempdf['nodeNum'])

#arcs={0:[0,2],1:[0,3],2:[1,3],3:[2,4],4:[2,5],5:[3,4],6:[3,5],7:[2,6],8:[3,7]}
arcs={}
d_ij=[]
c_ij={}
ghg_ij= {}
counter=0
for i in dijCtoR.index:
    for j in range(0, len(dijCtoR.columns)-1):
        arcs[counter]=[int(dijCtoR.iloc[i,0]),int(dijCtoR.columns[j+1])]
        counter+=1
        d_ij.append(dijCtoR.iloc[i, j + 1])
        ghg_ij[i,rNodeNumToy_i+j]=gijCtoR.iloc[i,j+1]
        remanNode=rNodeNumToy_i
        c_ij[i,rNodeNumToy_i+j]=dijCtoR.iloc[i, j + 1]*kmPerKg

for i in dijRtoM.index:
    for j in range(0, len(dijRtoM.columns)-1):
        arcs[counter]=[int(dijRtoM.iloc[i,0]),int(dijRtoM.columns[j+1])]
        counter+=1
        d_ij.append(dijRtoM.iloc[i, j + 1])
        ghg_ij[i+rNodeNumToy_i,numManufacturing+j]=gijRtoM.iloc[i,j+1]
        c_ij[i+rNodeNumToy_i,numManufacturing+j]=dijRtoM.iloc[i, j + 1]*kmPerKg

#LANDFILL
indexer=0
for i in remanufacturingNumNodes:
    arcs[counter] = [i,landfillNumNodes[indexer]]
    c_ij[i, landfillNumNodes[indexer]] = 0
    counter += 1
    indexer+=1
    d_ij.append(0)

#CToR={0:[2,3],1:[3]}
CToR={}
for nodeNumCollection in collectionNumNodes:
    for arc_i in arcs:
        if nodeNumCollection== arcs.get(arc_i)[0]:
            if nodeNumCollection not in CToR.keys():
                CToR[nodeNumCollection]=[int(arcs.get(arc_i)[1])]
            else: CToR[nodeNumCollection].append(arcs.get(arc_i)[1])

#RFromC={2:[0],3:[0,1]}
RFromC={}
for nodeNumCollection in remanufacturingNumNodes:
    for arc_i in arcs:
        if nodeNumCollection== arcs.get(arc_i)[1]:
            if nodeNumCollection not in RFromC.keys():
                RFromC[nodeNumCollection] = [int(arcs.get(arc_i)[0])]
            else: RFromC[nodeNumCollection].append(arcs.get(arc_i)[0])

#RToM={2:[4,5],3:[4,5]}
RToM={}
for nodeNumCollection in remanufacturingNumNodes:
    for arc_i in arcs:
        if nodeNumCollection== arcs.get(arc_i)[0] and arcs.get(arc_i)[1] in manufacturingNumNodes:
            if nodeNumCollection not in RToM.keys():
                RToM[nodeNumCollection] = [int(arcs.get(arc_i)[1])]
            else: RToM[nodeNumCollection].append(arcs.get(arc_i)[1])


#RToL={2:[6],3:[7]}
RToL={}
for nodeNumCollection in remanufacturingNumNodes:
    for arc_i in arcs:
        if nodeNumCollection== arcs.get(arc_i)[0] and arcs.get(arc_i)[1] in landfillNumNodes:
            if nodeNumCollection not in RToL.keys():
                RToL[nodeNumCollection] = [int(arcs.get(arc_i)[1])]
            else: RToL[nodeNumCollection].append(arcs.get(arc_i)[1])

#MFromR={4:[2,3],5:[2,3]}
MFromR={}
for nodeNumCollection in manufacturingNumNodes:
    for arc_i in arcs:
        if nodeNumCollection== arcs.get(arc_i)[1]:
            if nodeNumCollection not in MFromR.keys():
                MFromR[nodeNumCollection] = [int(arcs.get(arc_i)[0])]
            else: MFromR[nodeNumCollection].append(arcs.get(arc_i)[0])


scenarios=[]
#u_it={0:[6,8],1:[4,8],2:[3,5]} #key is the scenario and values are collection center supply
u_is={}
demand_is={}
supplyColNames=[]
demandColNames=[]
probOfScenario=[]
for scene in range(1,SCENARIONUM+1):
    supplyColNames.append("s_"+str(scene))
    demandColNames.append("d_"+str(scene))
    scenarios.append(scene-1)
    probOfScenario.append(1/SCENARIONUM)

for timing in scenarios:
    u_is[timing] = []
    demand_is[timing]=[]
    tempdf = nodeIds[supplyColNames[timing]]
    temporaryDf=nodeIds[demandColNames[timing]]
    u_is[timing]=tempdf.iloc[collectionNumNodes[0]:collectionNumNodes[-1]+1].to_numpy()
    demand_is[timing]=temporaryDf.iloc[manufacturingNumNodes[0]:manufacturingNumNodes[-1]+1].to_numpy()

#o_i=[0.1,0.6]
tempdf=nodeIds.loc[nodeIds['type'] == "R"]
o_i=np.asarray(tempdf['o_i'])
f_i=np.asarray(tempdf['f_i'])

#Cap_i=[100000,100000,100000,100000,100000,100000]
Cap_i=np.asarray(tempdf['capacity'])

#d_ij
dijArr=np.array(d_ij)
alpha=0.2
stochasticModel = gp.Model()

arcsWithScenario={}
counter=0
for t in scenarios:
    for keyArcs in arcs.keys():
        arcsWithScenario[counter]=arcs[keyArcs].copy()
        arcsWithScenario[counter].append(t)
        counter+=1

xArrForVals=np.array([])
numVals=0
for k in arcsWithScenario.keys():
    xArrForVals=np.append(xArrForVals,arcsWithScenario.get(k))
    numVals+=3


arrT2=xArrForVals.reshape((int(numVals/3),3))
lst_tuple = list(map(tuple, arrT2))
x_ijt=stochasticModel.addVars(lst_tuple,lb=0,name="x")

y_i=stochasticModel.addVars(remanufacturingNumNodes,vtype=GRB.BINARY,name="y")

#stochasticModel.setObjective(gp.quicksum(probOfScenario[s]*(gp.quicksum (c_ij[i,j]*x_ijt[i,j,s]
                    #for i in collectionNumNodes for j in remanufacturingNumNodes)+
                    #gp.quicksum(c_ij[i,j]*x_ijt[i,j,s] for i in remanufacturingNumNodes for j in manufacturingNumNodes)+
                    #gp.quicksum(o_i[i-rNodeNumToy_i]*gp.quicksum(x_ijt[j,i,s] for j in collectionNumNodes) for i in remanufacturingNumNodes))
                    #for s in scenarios)+
                    #gp.quicksum(y_i[i]*f_i[i-rNodeNumToy_i] for i in remanufacturingNumNodes),GRB.MINIMIZE)
#stochasticModel.setObjective(gp.quicksum(probOfScenario[s] * (gp.quicksum(ghg_ij[i,j]*x_ijt[i,j,s] for i in collectionNumNodes
                    #for j in remanufacturingNumNodes)+gp.quicksum(ghg_ij[i,j]*x_ijt[i,j,s] for i in remanufacturingNumNodes
                    #for j in manufacturingNumNodes)) for s in scenarios),GRB.MINIMIZE)
stochasticModel.setObjective((0)*(gp.quicksum(probOfScenario[s]*(gp.quicksum (c_ij[i,j]*x_ijt[i,j,s]
                    for i in collectionNumNodes for j in remanufacturingNumNodes)+
                    gp.quicksum(c_ij[i,j]*x_ijt[i,j,s] for i in remanufacturingNumNodes for j in manufacturingNumNodes)+
                    gp.quicksum(o_i[i-rNodeNumToy_i]*gp.quicksum(x_ijt[j,i,s] for j in collectionNumNodes) for i in remanufacturingNumNodes))
                    for s in scenarios)+
                    gp.quicksum(y_i[i]*f_i[i-rNodeNumToy_i] for i in remanufacturingNumNodes))+
                    (1)*(gp.quicksum(probOfScenario[s] * (gp.quicksum(ghg_ij[i, j] * x_ijt[i, j, s] for i in collectionNumNodes
                    for j in remanufacturingNumNodes)+gp.quicksum(ghg_ij[i,j]*x_ijt[i,j,s] for i in remanufacturingNumNodes
                    for j in manufacturingNumNodes)) for s in scenarios)), GRB.MINIMIZE)


for i in collectionNumNodes:
    for t in scenarios:
        stochasticModel.addConstr(gp.quicksum(x_ijt[i,j,t] for j in CToR.get(i))==u_is.get(t)[i]) #supply

for i in manufacturingNumNodes:
    for t in scenarios:
        stochasticModel.addConstr(gp.quicksum(x_ijt[j,i,t] for j in MFromR.get(i))
                                  >=demand_is.get(t)[i-manufacturingNumNodes[0]])

for i in remanufacturingNumNodes:
    for t in scenarios:
        stochasticModel.addConstr(gp.quicksum(x_ijt[j,i,t] for j in RFromC.get(i))
                            -(1-alpha)*gp.quicksum(x_ijt[i,j,t] for j in RToM.get(i))
                            -alpha*gp.quicksum(x_ijt[i,j,t] for j in RToL.get(i))==0)

for i in remanufacturingNumNodes:
    for t in scenarios:
        stochasticModel.addConstr(gp.quicksum(x_ijt[j,i,t] for j in RFromC.get(i))
                            <= Cap_i[i-rNodeNumToy_i]*y_i[i])
        stochasticModel.addConstr(gp.quicksum(x_ijt[i,j,t] for j in RToM.get(i))<=Cap_i[i-rNodeNumToy_i]*y_i[i])

#for i in remanufacturingNumNodes:
    #for t in range(0,len(scenarios)-1):
        #stochasticModel.addConstr(y_i[i-rNodeNumToy_i]<=y_i[i-rNodeNumToy_i])

#max facilities
stochasticModel.addConstr(gp.quicksum(y_i[i] for i in remanufacturingNumNodes)==MAX_NUM_FACILITIES)


stochasticModel.optimize()
#obj = stochasticModel.getObjective()
#print(obj.getValue())
#v= stochasticModel.getVars()
#stochasticModel.write("outSTO.lp")

for i in arcsWithScenario.keys():
    if x_ijt[arcsWithScenario[i][0],arcsWithScenario[i][1],arcsWithScenario[i][2]].X >1:
        print("x_"+str(arcsWithScenario[i][0])+","+str(arcsWithScenario[i][1])+","+str(arcsWithScenario[i][2])
              +str(" value: ")+str(x_ijt[arcsWithScenario[i][0],arcsWithScenario[i][1],arcsWithScenario[i][2]].X))

keepRows=[]
for i in remanufacturingNumNodes:
    if y_i[i].X>0.9:
        print("y_"+str(i)+str(" value: ")+str(y_i[i].X))
        keepRows.append(i)

transportCost=0
emmisionsCost=0
for s in range(0,SCENARIONUM):
    for i in collectionNumNodes:
        for j in remanufacturingNumNodes:
            transportCost+=c_ij[i,j]*x_ijt[i,j,s].X
            emmisionsCost+=ghg_ij[i,j]*x_ijt[i,j,s].X
    for i in remanufacturingNumNodes:
        for j in manufacturingNumNodes:
            transportCost+=c_ij[i,j]*x_ijt[i,j,s].X
            emmisionsCost+=ghg_ij[i,j]*x_ijt[i,j,s].X

print("Transportation cost: "+ str(transportCost/SCENARIONUM))
print("Emissions cost: "+ str(emmisionsCost/SCENARIONUM))
#openedFacilities=tempdf.loc[keepRows]
#newFacilities=pd.merge(openedFacilities, populationInfo, on='nodeNum', how='inner')
'''
m=folium.Map(location=[50.000,-85.000],zoom_start=6)
for i in newFacilities.index:
    lat=newFacilities.iloc[i]['lat']
    lon=newFacilities.iloc[i]['lon']
    name="FACILITY: %s" %i
    folium.Marker(
        location=[lat,lon],
        popup=name,
        icon=folium.Icon(color='black')
    ).add_to(m)

m.save('Facilities.html')'''