import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd
import folium


xls=pd.ExcelFile("baseLine.xlsx")
dijPtoR=pd.read_excel(xls,"gamecost")
gijPtoR=pd.read_excel(xls,"emissionscost")
facility_costs=[1.009296387, 1.006272109, 1.017934691, 1.017934691, 1.017877583, 1.009827342, 1.017877583, 1.008207507,
                1.012638349, 1.010940059, 1.027307445, 1.017877583, 1.027307445, 1.009157797, 1.003884694, 1.008207507,
                1.010245452, 1.009157797, 1.012638349, 1.013637869, 1.027307445, 1.002612387, 1.009157797, 1.012638349,
                1.002615535, 1.009466279, 1.008230076, 1.009157797, 1.009157797, 1.013637869, 1.017877583, 1.004618288,
                1.004809517, 1.017934691, 1.001602178, 1.007573696, 1.008026812, 1.027307445, 1.017877583, 1.013637869,
                1.003757302, 1.002085485, 1.008026812, 1.017877583, 1.00590316, 1.017877583, 1.013630794, 1.008207507,
                1.003757302, 1.008207507, 1.007759619, 1.008207507, 1.001839727, 1.009466279, 1.010940059, 1.017877583,
                1.008207507, 1.012113833, 1.010940059, 1.013637869, 1.008945437, 1.010940059, 1.013637869, 1.005915726,
                1.004821952, 1.008207507, 1.013637869, 1.008207507, 1.013637869, 1.010940059, 1.010940059, 1.010940059,
                1.005760091, 1.006608054, 1.003101446, 1.010940059, 1.005246738, 1.013637869, 1.013637869, 1.002614191,
                1.008207507, 1.013630794, 1.013637869, 1.005760091, 1.005246738, 1.002914265, 1.006207022, 1.001269682,
                1.00319262, 1.013630794, 1.002614191, 1.005760091, 1.00319262, 1.010245452, 1.001602178, 1.005915726,
                1.008945437, 1.002145191, 1.002614191, 1.008945437, 1.008207507]
supplyDemandlst=[52750,29860,44602,110396,77661,77661,103343,371033,83809,4704,371033,107823,110396,67677,260130,20353,
33399,44602,4704,67302,32585,44602,11263,27641,92461,86459,20353,21088,56665,107823,56665,56665,67302,67302,173223,77661,
4704,44249,173223,103343,77661,20353,260130,110396,29860,20353,11263,77661,37559,15697,110396,27641,43896,70275,110396,
22322,67302,4704,107823,33399,57886,27641,11263,110396,11263,4704,70137,70644,1112635,103343,11263,22322,70267,4704,11263,
53805,56665,286124.5778,286124.5778,286124.5778,286124.5778,286124.5778,286124.5778,286124.5778,286124.5778,286124.5778,
286124.5778,286124.5778,286124.5778,286124.5778,286124.5778,286124.5778,286124.5778,286124.5778,286124.5778]
costPerkm=0.00005696
capacityAll=1000000000
baseFacilityCost=2000000
supplyvar=50
PToR_dict_distance={}
PToR_dict_emissions={}
notOpening={}
c_ij={}
numPlayers=95
numReman=100
weighting=1
MAXFacilities=18
wholesalePrice=37.5
marginalPrice=41

counter=0
for i in dijPtoR.index:
    arrToSave=pd.Series(dijPtoR.iloc[i][1:]).array
    PToR_dict_distance[counter] = arrToSave
    counter+=1

counter=0
for i in gijPtoR.index:
    arrToSave=pd.Series(gijPtoR.iloc[i][1:]).array
    PToR_dict_emissions[counter] = arrToSave
    counter+=1

dimarrayForVars=[]
for i in range (0,numPlayers):
    for j in range(0,numReman):
        a_tuple=(int(i),int(j))
        dimarrayForVars.append(a_tuple)

recording_df=pd.DataFrame(columns=['TransportCost','Facilities','Emissions','Assignment','Runtime'])

for numRuns in range(101,105):#1,101
    #distanceResult=np.array([])
    #facilityCostResult=np.array([])
    if numRuns<=20:
        if numRuns==1 or numRuns==6 or numRuns==11 or numRuns==16:
            weighting=1
        if numRuns == 2 or numRuns == 7 or numRuns == 12 or numRuns == 17:
            weighting=0.75
        if numRuns == 3 or numRuns == 8 or numRuns == 13 or numRuns == 18:
            weighting=0.5
        if numRuns == 4 or numRuns == 9 or numRuns == 14 or numRuns == 19:
            weighting=0.25
        if numRuns == 5 or numRuns == 10 or numRuns == 15 or numRuns == 20:
            weighting=0
        if numRuns<=5:
            MAXFacilities=1
        if numRuns>=6 and numRuns<=10:
            MAXFacilities=2
        if numRuns>=11 and numRuns<=15:
            MAXFacilities=3
        if numRuns>=16 and numRuns<=20:
            MAXFacilities=4
    if numRuns>=21 and numRuns<=40:
        MAXFacilities = 20
        if numRuns==21 or numRuns==26 or numRuns==31 or numRuns==36:
            baseFacilityCost=1000000
        if numRuns==22 or numRuns==27 or numRuns==32 or numRuns==37:
            baseFacilityCost=2000000
        if numRuns==23 or numRuns==28 or numRuns==33 or numRuns==38:
            baseFacilityCost=3000000
        if numRuns==24 or numRuns==29 or numRuns==34 or numRuns==39:
            baseFacilityCost=4000000
        if numRuns==25 or numRuns==30 or numRuns==35 or numRuns==40:
            baseFacilityCost=5000000
        if numRuns>=21 and numRuns<=25:
            weighting=1
        if numRuns>=26 and numRuns<=30:
            weighting=0.75
        if numRuns>=31 and numRuns<=35:
            weighting=0.5
        if numRuns>=36 and numRuns<=40:
            weighting=0.25
    if numRuns>=41 and numRuns<=60:
        baseFacilityCost = 2000000
        if numRuns==41 or numRuns==46 or numRuns==51 or numRuns==56:
            costPerkm=0.00005696*1.5
        if numRuns==42 or numRuns==47 or numRuns==52 or numRuns==57:
            costPerkm=0.00005696*1.25
        if numRuns==43 or numRuns==48 or numRuns==53 or numRuns==58:
            costPerkm=0.00005696*1
        if numRuns==44 or numRuns==49 or numRuns==54 or numRuns==59:
            costPerkm=0.00005696*0.75
        if numRuns==45 or numRuns==50 or numRuns==55 or numRuns==60:
            costPerkm=0.00005696*0.5
        if numRuns>=41 and numRuns<=45:
            weighting=1
        if numRuns>=46 and numRuns<=50:
            weighting=0.75
        if numRuns>=51 and numRuns<=55:
            weighting=0.5
        if numRuns>=56 and numRuns<=60:
            weighting=0.25
    if numRuns>=61 and numRuns<=80:
        costPerkm=0.00005696
        baseFacilityCost = 2000000
        if numRuns==61 or numRuns==66 or numRuns==71 or numRuns==76:
            supplyvar=50*1.5
        if numRuns==62 or numRuns==67 or numRuns==72 or numRuns==77:
            supplyvar=50*1.25
        if numRuns==63 or numRuns==68 or numRuns==73 or numRuns==78:
            supplyvar=50*1
        if numRuns==64 or numRuns==69 or numRuns==74 or numRuns==79:
            supplyvar=50*0.75
        if numRuns==65 or numRuns==70 or numRuns==75 or numRuns==80:
            supplyvar=50*0.5
        if numRuns>=61 and numRuns<=65:
            weighting=1
        if numRuns>=66 and numRuns<=70:
            weighting=0.75
        if numRuns>=71 and numRuns<=75:
            weighting=0.5
        if numRuns>=76 and numRuns<=80:
            weighting=0.25
    if numRuns>=81:
        if numRuns==81 or numRuns==86 or numRuns==91 or numRuns==96:
            wholesalePrice=37.5*1.5
            marginalPrice=41*1.5
        if numRuns==82 or numRuns==87 or numRuns==92 or numRuns==97:
            wholesalePrice=37.5*1.25
            marginalPrice = 41 * 1.25
        if numRuns==83 or numRuns==88 or numRuns==93 or numRuns==98:
            wholesalePrice=37.5*1
            marginalPrice = 41 * 1
        if numRuns==84 or numRuns==89 or numRuns==94 or numRuns==99:
            wholesalePrice=37.5*0.75
            marginalPrice = 41 * 0.75
        if numRuns==85 or numRuns==90 or numRuns==95 or numRuns==100:
            wholesalePrice=37.5*0.5
            marginalPrice = 41 * 0.5
        if numRuns==101 or numRuns==102 or numRuns==103 or numRuns==104:
            wholesalePrice=37.5*0.1
            marginalPrice = 41 * 0.1
        if numRuns>=81 and numRuns<=85:
            weighting=1
        if numRuns>=86 and numRuns<=90:
            weighting=0.75
        if numRuns>=91 and numRuns<=95:
            weighting=0.5
        if numRuns>=96 and numRuns<=100:
            weighting=0.25
        if numRuns>=101 and numRuns<=105:
            weighting=1

    gameModel = gp.Model()
    x_ij=gameModel.addVars(dimarrayForVars,lb=0,name="x")
    y_ij=gameModel.addVars(dimarrayForVars,vtype=GRB.BINARY,name="y")
    wj=gameModel.addVars(range(0,numReman),lb=0,name="w")
    aj=gameModel.addVars(range(0,numReman),vtype=GRB.BINARY,name="a")
    zj=gameModel.addVars(range(0,numReman),lb=0,name="z")
    denomj=gameModel.addVars(range(0,numReman),lb=0,name="denom")
    subj=gameModel.addVars(range(0,numReman),lb=1/numPlayers,ub=1,name="sub")
    Tj=gameModel.addVars(range(0,numReman),vtype=GRB.BINARY,name="T")
    Uj=gameModel.addVars(range(0,numReman),lb=0,ub=numPlayers,name="U")

    gameModel.setObjective((weighting)*(gp.quicksum(PToR_dict_distance[i][j]*costPerkm*x_ij[i,j] for i in range(0,numPlayers) for j in range(0,numReman))
                           +gp.quicksum(zj[j]*facility_costs[j]*baseFacilityCost for j in range(0,numReman)))
                           +(1-weighting)*(gp.quicksum(PToR_dict_emissions[i][j]*x_ij[i,j] for i in range(0,numPlayers) for j in range(0,numReman))),GRB.MINIMIZE)

    #demand supply constraint
    for i in range(0,numPlayers):
        gameModel.addConstr(gp.quicksum(x_ij[i,j] for j in range(0,numReman))==supplyDemandlst[i]*supplyvar)
        gameModel.addConstr(gp.quicksum(y_ij[i,j] for j in range(0,numReman))==1)

    #capacity and open contraint
    for j in range(0,numReman):
        gameModel.addConstr(gp.quicksum(x_ij[i,j] for i in range(0,numPlayers))<=aj[j]*capacityAll)
        gameModel.addConstr(gp.quicksum(y_ij[i,j] for i in range(0,numPlayers))==wj[j])
        gameModel.addConstr(wj[j]<=capacityAll*aj[j])
        gameModel.addConstr(zj[j]<=capacityAll*aj[j])
        #gameModel.addConstr(denomj[j]==wj[j]+1-aj[j])
        gameModel.addConstr(zj[j]>= subj[j]- (1-aj[j])*capacityAll)
        gameModel.addConstr(Uj[j]>=1/numPlayers * wj[j])
        gameModel.addConstr(Uj[j]>=numPlayers*subj[j]+wj[j]-numPlayers)
        gameModel.addConstr(Uj[j]<=numPlayers*subj[j]+1/numPlayers*wj[j]-1)
        gameModel.addConstr(Uj[j]<=wj[j])
        gameModel.addConstr(Tj[j]<=aj[j])
        gameModel.addConstr(Tj[j]<=subj[j])
        gameModel.addConstr(Tj[j]>=2*aj[j]-1)
        #gameModel.addConstr(subj[j]-Tj[j]+Uj[j]==1)

    if numRuns<=20:
        gameModel.addConstr(gp.quicksum(aj[j] for j in range(0,numReman))==MAXFacilities)

    gameModel.optimize()
    #gameModel.write("outSTO.lp")
    #arrResult = np.array([])
    TRANSPORTCOSTSUM=0
    EMISSIONSSUMCOST=0
    #arrResultEmissions = np.array([])
    facility123 = np.array([])
    flow=np.array([])
    notOpeningplayerslst=[]
    for i in range(0,numPlayers):
        for j in range(0, numReman):
            if x_ij[i,j].X > 0:
                TRANSPORTCOSTSUM+=x_ij[i, j].X * PToR_dict_distance[i][j] * costPerkm
                EMISSIONSSUMCOST+=x_ij[i, j].X * PToR_dict_emissions[i][j]
                perPlayertransport=x_ij[i, j].X * PToR_dict_distance[i][j] * costPerkm
                print(f"PLAYER {i} OPENED FACILITY {j}")
                if wj[j].X>0:
                    perPlayerCost=facility_costs[j] * baseFacilityCost / wj[j].X
                #arrResult=np.append(arrResult,x_ij[i,j].X*PToR_dict_distance[i][j]*costPerkm)
                #arrResultEmissions = np.append(arrResultEmissions, x_ij[i, j].X * PToR_dict_emissions[i][j])
                #facilityCostResult=np.append(facilityCostResult,facility_costs[j])
                #print("y_" + str(j) + str(" value: ") + str(y_j[j].X))
        if i<=77:
            if wholesalePrice*supplyDemandlst[i]-perPlayertransport-perPlayerCost<0:
                notOpeningplayerslst.append(i)
        else:
            if marginalPrice*supplyDemandlst[i]-perPlayertransport-perPlayerCost<0:
                notOpeningplayerslst.append(i)

    notOpening[numRuns]=notOpeningplayerslst

    for j in range(0, numReman):
        if aj[j].X>0.1:
            #print(f"the facility {j} is opened")
            facility123=np.append(facility123,j)
            flow=np.append(flow,wj[j].X)
    runtime=gameModel.Runtime
    listingTOADD=list()
    listingTOADD.append(TRANSPORTCOSTSUM)
    listingTOADD.append(facility123)
    listingTOADD.append(EMISSIONSSUMCOST)
    listingTOADD.append(flow)
    listingTOADD.append(runtime)

    recording_df.loc[numRuns-1]=listingTOADD
    print(numRuns)


#recording_df.to_excel("OUTPUTGAMETHEORY.xlsx",sheet_name="gaming")
print(recording_df.to_string())
print(notOpening)
    #print(arrResult)
    #stringy1=""
    #for i in arrResult:
        #stringy1+=str(i)+", "
    #print(stringy1)
