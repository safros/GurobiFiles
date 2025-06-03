import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd
import folium


def dictToArray(dict):
    arrToReturn=np.array([])
    numVals=0
    for x in dict.keys():
        arrToReturn=np.append(arrToReturn,int(dict.get(x)[0]))
        arrToReturn = np.append(arrToReturn, int(dict.get(x)[1]))
        numVals+=2
    arrT2=arrToReturn.reshape((int(numVals/2),2))
    arrT2=arrT2.astype(int)

    lst_tuple = list(map(tuple, arrT2))
    return lst_tuple

xls=pd.ExcelFile("baseLine.xlsx")
nodeIds=pd.read_excel(xls,"nodeId")
dijRtoM=pd.read_excel(xls,"distanceMatrixRtoM")
dijCtoR=pd.read_excel(xls, "distanceMatrixCtoR")
gijRtoM=pd.read_excel(xls,"emissionsRtoM_adapt")
gijCtoR=pd.read_excel(xls, "emissionsCtoR_adapt")
populationInfo=pd.read_excel(xls,"Population")

#c=np.array([0,1,2])
tempdf=nodeIds.loc[nodeIds['type'] == "C"]
c=np.asarray(tempdf['nodeNum'])
#r=np.array([3,4])
tempdf=nodeIds.loc[nodeIds['type'] == "R"]
r=np.asarray(tempdf['nodeNum'])
#reMan=np.array([0,1])
reMan=np.arange(len(r))
rNodeNumToy_i=r[0]
#l=np.array([5,6])
tempdf=nodeIds.loc[nodeIds['type'] == "L"]
l=np.asarray(tempdf['nodeNum'])
#m=np.array([7,8])
tempdf=nodeIds.loc[nodeIds['type'] == "M"]
m=np.asarray(tempdf['nodeNum'])
demand_i=np.asarray(tempdf['di'])
#fi=[1000,2000]
tempdf=nodeIds.loc[nodeIds['type'] == "R"]
fi=np.asarray(tempdf['fi'])
#oi=[1,1]
oi=np.asarray(tempdf['oi'])
#capacity_i=[1000,2000]
capacity_i=np.asarray(tempdf['capacity'])
tempdf=nodeIds.loc[nodeIds['type'] == "C"]
#supply_i=[6,7,8]
supply_i=np.asarray(tempdf['si'])

alpha=0.2
#dij=np.array([1,2,3,4,5,1,2,3,4])
dij=[]
#cij=dij*0.01
ghg_arc=[]

MAX_NUM_FACILITIES=3

#key is the arc and value is the node start and node end
#dictArcNumToArcVals={0:[0,3],1:[1,3],2:[2,4],3:[3,5],4:[3,7],5:[3,8],6:[4,6],7:[4,7],8:[4,8]}
dictArcNumToArcVals={}
counter=0
for i in dijCtoR.index:
    for j in range(0, len(dijCtoR.columns)-1):
        dictArcNumToArcVals[counter]=[int(dijCtoR.iloc[i,0]),int(dijCtoR.columns[j+1])]
        counter+=1
        dij.append(dijCtoR.iloc[i,j+1])
        ghg_arc.append(gijCtoR.iloc[i,j+1])

for i in dijRtoM.index:
    for j in range(0, len(dijRtoM.columns)-1):
        dictArcNumToArcVals[counter]=[int(dijRtoM.iloc[i,0]),int(dijRtoM.columns[j+1])]
        counter+=1
        dij.append(dijRtoM.iloc[i, j + 1])
        ghg_arc.append(gijRtoM.iloc[i, j + 1])

indexer=0
for i in r:
    dictArcNumToArcVals[counter] = [i,l[indexer]]
    counter += 1
    indexer+=1
    dij.append(0)
    ghg_arc.append(0)

dijArr=np.array(dij)
kmPerKg=0.0003335*1
#0.000094 miles/lbs
cij=dijArr*kmPerKg
#NOTE NEED TO MAKE FUNCTIONS TO TURN Arcs into other dictionaries below
#collection hash
cOut={}
for nodeNumCollection in c:
    for arc in dictArcNumToArcVals:
        if nodeNumCollection== dictArcNumToArcVals.get(arc)[0]:
            if nodeNumCollection not in cOut.keys():
                cOut[nodeNumCollection]=[int(dictArcNumToArcVals.get(arc)[1])]
            else: cOut[nodeNumCollection].append(dictArcNumToArcVals.get(arc)[1])
#cOut={0:[3],1:[3],2:[4]}

#remanufacturing in=out c=l+d
rInc={}
rOutl={}
rOutm={}
mInR={}
for rNumCollection in r: #for every remanufacturing node
    for arc in dictArcNumToArcVals: #for every arc in the collection
        if rNumCollection==dictArcNumToArcVals.get(arc)[1]: #check if the arc goes from c to r
            if rNumCollection not in rInc.keys():
                rInc[rNumCollection]=[int(dictArcNumToArcVals.get(arc)[0])]
            else :rInc[rNumCollection].append(dictArcNumToArcVals.get(arc)[0])
        if rNumCollection==dictArcNumToArcVals.get(arc)[0]: #check if the arc goes from r to either l or m
            if dictArcNumToArcVals.get(arc)[1] in l:
                if rNumCollection not in rOutl.keys():
                    rOutl[rNumCollection]=[int(dictArcNumToArcVals.get(arc)[1])]
                else: rOutl[rNumCollection].append(dictArcNumToArcVals.get(arc)[1])
            if dictArcNumToArcVals.get(arc)[1] in m:
                if rNumCollection not in rOutm.keys():
                    rOutm[rNumCollection]=[int(dictArcNumToArcVals.get(arc)[1])]
                else: rOutm[rNumCollection].append(dictArcNumToArcVals.get(arc)[1])
                if dictArcNumToArcVals.get(arc)[1] not in mInR.keys():
                    mInR[int(dictArcNumToArcVals.get(arc)[1])]=[int(rNumCollection)]
                else: mInR[int(dictArcNumToArcVals.get(arc)[1])].append(rNumCollection)


#rInc={3:[0,1],4:[2]}
#rOutd={3:[7,8],4:[7,8]}
#rOutl={3:[5],4:[6]}
#mInr={7:[3,4],8:[3,4]}

#dictArcNumToArcVals={0:[0,3],1:[1,3],2:[2,4],3:[3,5],4:[3,7],5:[3,8],6:[4,6],7:[4,7],8:[4,8]}
#c=np.array([0,1,2])
#r=np.array([3,4])
#reMan=np.array([0,1])
#rNodeNumToy_i=r[0]
#l=np.array([5,6])
#m=np.array([7,8])

testmodel = gp.Model()
arrForArcs=dictToArray(dictArcNumToArcVals)
x_ij=testmodel.addVars(arrForArcs,lb=0,name="x")
y_i=testmodel.addVars(r,vtype=GRB.BINARY,name="y")

#objective of cost
#z_n=testmodel.addVar(name="z_n")
#z_n=gp.quicksum(fi[i-rNodeNumToy_i]*y_i[i] for i in r)+ gp.quicksum(cij[i]*x_ij[dictArcNumToArcVals.get(i)[0],dictArcNumToArcVals.get(i)[1]] for i in dictArcNumToArcVals.keys())+gp.quicksum(oi[i-rNodeNumToy_i] * gp.quicksum(x_ij[i,j] for j in m) for i in r)
#objective of emissions
#z_d=testmodel.addVar(name="z_d")
#z_d=gp.quicksum(ghg_arc[i]*x_ij[dictArcNumToArcVals.get(i)[0],dictArcNumToArcVals.get(i)[1]] for i in dictArcNumToArcVals.keys())

#testmodel.setObjective(gp.quicksum(fi[i-rNodeNumToy_i]*y_i[i] for i in r)
                      # + gp.quicksum(cij[i]*x_ij[dictArcNumToArcVals.get(i)[0],dictArcNumToArcVals.get(i)[1]] for i in dictArcNumToArcVals.keys())
                   # +gp.quicksum(oi[i-rNodeNumToy_i] * gp.quicksum(x_ij[i,j] for j in m) for i in r)
                      # ,GRB.MINIMIZE)
#testmodel.setObjective(gp.quicksum(ghg_arc[i]*x_ij[dictArcNumToArcVals.get(i)[0],dictArcNumToArcVals.get(i)[1]] for i in dictArcNumToArcVals.keys()))

testmodel.setObjective((0.1)*(gp.quicksum(fi[i-rNodeNumToy_i]*y_i[i] for i in r)
                      + gp.quicksum(cij[i]*x_ij[dictArcNumToArcVals.get(i)[0],dictArcNumToArcVals.get(i)[1]] for i in dictArcNumToArcVals.keys())
                    +gp.quicksum(oi[i-rNodeNumToy_i] * gp.quicksum(x_ij[i,j] for j in m) for i in r))+
                       (0.9)*(gp.quicksum(ghg_arc[i]*x_ij[dictArcNumToArcVals.get(i)[0],dictArcNumToArcVals.get(i)[1]] for i in dictArcNumToArcVals.keys())),GRB.MINIMIZE)


for i in r:
    testmodel.addConstr(gp.quicksum(x_ij[j,i] for j in rInc.get(i))
                        -(1-alpha)*gp.quicksum(x_ij[i,j] for j in rOutm.get(i))
                        -alpha*gp.quicksum(x_ij[i,j] for j in rOutl.get(i))==0)
    testmodel.addConstr(gp.quicksum(x_ij[j,i] for j in rInc.get(i))<=capacity_i[i-rNodeNumToy_i]*y_i[i])
    testmodel.addConstr(gp.quicksum(x_ij[i,j] for j in rOutm.get(i))<=capacity_i[i-rNodeNumToy_i]*y_i[i])

#generation
for i in c:
    testmodel.addConstr(gp.quicksum(x_ij[i,j] for j in cOut.get(i))==supply_i[i])

#demand
counter=0
for i in m:
    testmodel.addConstr(gp.quicksum(x_ij[j,i] for j in mInR.get(i))>=demand_i[counter])
    counter+=1

#max facility number
testmodel.addConstr(gp.quicksum(y_i[j] for j in r)<=MAX_NUM_FACILITIES)

testmodel.optimize()
obj = testmodel.getObjective()
print(obj.getValue())
v= testmodel.getVars()
testmodel.write("out.lp")

transportCost=0
emissionsCost=0
for i in dictArcNumToArcVals.keys():
    if x_ij[dictArcNumToArcVals[i][0],dictArcNumToArcVals[i][1]].X >1:
        print("x_"+str(dictArcNumToArcVals[i][0])+","+str(dictArcNumToArcVals[i][1])
              +str(" value: ")+str(x_ij[dictArcNumToArcVals[i][0],dictArcNumToArcVals[i][1]].X))
        transportCost+=x_ij[dictArcNumToArcVals[i][0],dictArcNumToArcVals[i][1]].X*cij[i]
        emissionsCost+=x_ij[dictArcNumToArcVals[i][0],dictArcNumToArcVals[i][1]].X*ghg_arc[i]

tempdf=nodeIds.loc[nodeIds['type'] == "R"]
keepRows=[]

totalFacilitycost=0
for i in r:
    if y_i[i].X==1:
        print("y_"+str(i)+str(" value: ")+str(y_i[i].X))
        keepRows.append(i)
        totalFacilitycost+=fi[i-rNodeNumToy_i]

openedFacilities=tempdf.loc[keepRows]
newFacilities=pd.merge(openedFacilities, populationInfo, on='nodeNum', how='inner')

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

m.save('Facilities.html')

print("Facility cost: "+str(totalFacilitycost))
print("Transportation cost: "+str(transportCost))
print("Emissions cost: "+str(emissionsCost))
print("Total cost: "+ str(totalFacilitycost+transportCost))

#distances for cij= dij * dollar value /km for trucking



