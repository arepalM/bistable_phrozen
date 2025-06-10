from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os


#ODB
case     = 'h0p001_r2'
FB_ELSET = "PART-1-1.EB2"
FB_NSET  = "PART-1-1.NS6"
stepname = 'cooldown'
dir      = os.path.join(r'C:\Users\mlapera1\OneDrive - Johns Hopkins\Documents\JHU\Research\morphing wing\Abaqus\bistable_phrozen\for paper',case)
ODBFILE  = os.path.join(dir,'main_phrozen1j.odb')
fname1   = 'RF2vsU1_cooldown'
fname2   = 'U1vstime_cooldown'
fname3   = 'NT11vstime_N5252_cooldown'
fname4   = 'NT11vstime_N3548_cooldown'
fname5   = 'deltaT_vs_time_cooldown'
fname6   = 'NT11vstime_N4403_cooldown'


# Remove white space and format XY data from Abaqus report
def toCSV(fname,fpath):
    U1_FILEPATH = os.path.join(fpath,fname + '.txt')
    U1_CSVOUT   = os.path.join(fpath,fname + '.csv')
    with open(U1_FILEPATH) as infile:
        U1_df = pd.read_csv(U1_FILEPATH, sep='\s+',header=1)
        U1_df.set_index('X', inplace=True)
        U1_df = U1_df.dropna(axis = 'columns')
        U1_df.to_csv(U1_CSVOUT,header='none')
        #data = re.sub('[ ]+',',',infile.read())
    infile.close()
    return U2_df

# Outfiles
OUTFILE1 = os.path.join(dir,case + '_' + fname1 + '.txt')
OUTFILE2 = os.path.join(dir,case + '_' + fname2 + '.txt')
OUTFILE3 = os.path.join(dir,case + '_' + fname3 + '.txt')
OUTFILE4 = os.path.join(dir,case + '_' + fname4 + '.txt')
OUTFILE5 = os.path.join(dir,case + '_' + fname5 + '.txt')
OUTFILE6 = os.path.join(dir,case + '_' + fname6 + '.txt')

# Set ODB file 
o1 = session.openOdb(
    name=ODBFILE)
session.viewports['Viewport: 1'].setValues(displayedObject=o1)
odb = session.odbs[ODBFILE]
session.odbData[ODBFILE].setValues(activeFrames=((stepname, ('0:-1', )), ))



# Extract N5252 U1 displacement
odb = session.openOdb(name=ODBFILE)
session.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=(('U', 
    NODAL, ((COMPONENT, 'U1'), )), ), nodeLabels=(('PART-1-1', ('5252', )), ))
xy11 = session.xyDataObjects['U:U1 PI: PART-1-1 N: 5252']
tmpName = xy11.name
session.xyDataObjects.changeKey(tmpName, case + '_U1_vs_t')
xy11 = session.xyDataObjects[case + '_U1_vs_t']
# Write out data to files
session.writeXYReport(fileName=OUTFILE2, xyData=(xy11, ))


# Sets that define the freebody cut
eLeaf = dgo.LeafFromElementSets(elementSets=(FB_ELSET, ))
nLeaf = dgo.LeafFromNodeSets(nodeSets=(FB_NSET, ))
# Make freebody cut
session.FreeBodyFromNodesElements(name='FreeBody-1', elements=eLeaf, 
    nodes=nLeaf, summationLoc=CENTROID, componentResolution=NORMAL_TANGENTIAL)

# Extract 1-component (not global 1-direction, rather normal to section)
xyList = xyPlot.XYDataFromFreeBody(odb=odb, force=ON, moment=OFF, 
    heatFlowRate=OFF, resultant=OFF, comp1=ON, comp2=OFF, comp3=OFF)
xy2 = session.xyDataObjects['_FreeBody-1 force component 1']

# Concatenate RF2 vs. U1
xy3 = combine(xy11, xy2)
xy3.setValues(sourceDescription='combine("U:U1 PI: PART-1-1 N: 5252","_FreeBody-1 force component 1")')
tmpName = xy3.name
session.xyDataObjects.changeKey(tmpName, case + '_RF2_vs_U1')

xy3 = session.xyDataObjects[case + '_RF2_vs_U1']
session.writeXYReport(fileName=OUTFILE1, xyData=(xy3, ))

# Get N5252 node temperature
xyList = xyPlot.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=((
    'NT11', NODAL), ), nodeLabels=(('PART-1-1', ('5252', )), ))
xy4 = session.xyDataObjects['_NT11 PI: PART-1-1 N: 5252']
tmpName = xy4.name
session.xyDataObjects.changeKey(tmpName, case + '_NT11_N5252')
session.writeXYReport(fileName=OUTFILE3, xyData=(xy4, ))

# Get N3548 node temperature
xyList = xyPlot.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=((
    'NT11', NODAL), ), nodeLabels=(('PART-1-1', ('3548', )), ))
xy5 = session.xyDataObjects['_NT11 PI: PART-1-1 N: 3548']
tmpName = xy5.name
session.xyDataObjects.changeKey(tmpName, case + '_NT11_N3548')
session.writeXYReport(fileName=OUTFILE4, xyData=(xy5, ))

# Get N4403 node temperature
xyList = xyPlot.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=((
    'NT11', NODAL), ), nodeLabels=(('PART-1-1', ('4403', )), ))
xy6 = session.xyDataObjects['_NT11 PI: PART-1-1 N: 4403']
tmpName = xy6.name
session.xyDataObjects.changeKey(tmpName, case + '_NT11_N4403')
session.writeXYReport(fileName=OUTFILE6, xyData=(xy6, ))

# Calculate deltaT as f(t)
xy7 = session.xyDataObjects[case + '_NT11_N4403']
xy8 = session.xyDataObjects[case + '_NT11_N5252']
xy9 = xy7-xy8
tmpName = xy9.name
session.xyDataObjects.changeKey(tmpName, case + '_deltaT_vs_t')
session.writeXYReport(fileName=OUTFILE5, xyData=(xy9, ))

# Read in txt/rpt file and convert to csv
#toCSV(str(case + '_' + fname1),dir)
#toCSV(str(case + '_' + fname2),dir)