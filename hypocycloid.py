#Author-Patrick Rainsberry
#Description-Creates a 2 stage Hypocycloid gear
#
#
#import adsk.core, adsk.fusion, traceback
#
#"""Hypocycloid cam generator
#Generate dxfs of hypocycloid cams for cycloid drives
#
#Copyright 	2009, Alex Lait
#Version 	v0.2 (09/13/09)
#License 	GPL
#Homepage 	http://www.zincland.com/hypocycloid
#
#Credit to:
#	Formulas to describe a hypocycloid cam
#	http://gears.ru/transmis/zaprogramata/2.139.pdf
#
#	Insperational thread on CNCzone
#	http://www.cnczone.com/forums/showthread.php?t=72261
#
#	Documenting and updating the sdxf library
#	http://www.kellbot.com/sdxf-python-library-for-dxf/
#
#	Formulas for calculating the pressure angle and finding the limit circles
#	http://imtuoradea.ro/auo.fmte/files-2007/MECATRONICA_files/Anamaria_Dascalescu_1.pdf
#
#Notes:
#	Does not currently do ANY checking for sane input values and it
#	is possible to create un-machinable cams, use at your own risk
#
#	Suggestions:
#	- Eccentricity should not be more than the roller radius
#	- Has not been tested with negative values, may have interesting results :)
#"""

import adsk.core, adsk.fusion, traceback
import os, math

# global set of event handlers to keep them referenced for the duration of the command
handlers = []

app = adsk.core.Application.get()

if app:
    ui = app.userInterface
    product = app.activeProduct
    design = product

def toPolar(x, y):
    return (x**2 + y**2)**0.5, math.atan2(y, x)

def toRect(r, a):
    return r*math.cos(a), r*math.sin(a)

def calcyp(a,e,n,p):
    return math.atan(math.sin(n*a)/(math.cos(n*a)+(n*p)/(e*(n+1))))

def calcX(p,d,e,n,a):
    return (n*p)*math.cos(a)+e*math.cos((n+1)*a)-d/2*math.cos(calcyp(a,e,n,p)+a)

def calcY(p,d,e,n,a):
    return (n*p)*math.sin(a)+e*math.sin((n+1)*a)-d/2*math.sin(calcyp(a,e,n,p)+a)

def calcPressureAngle(p,d,n,a):
    ex = 2**0.5
    r3 = p*n
    rg = r3/ex
    pp = rg * (ex**2 + 1 - 2*ex*math.cos(a))**0.5 - d/2
    return math.asin( (r3*math.cos(a)-rg)/(pp+d/2))*180/math.pi

def calcPressureLimit(p,d,e,n,a):
    ex = 2**0.5
    r3 = p*n
    rg = r3/ex
    q = (r3**2 + rg**2 - 2*r3*rg*math.cos(a))**0.5
    x = rg - e + (q-d/2)*(r3*math.cos(a)-rg)/q
    y = (q-d/2)*r3*math.sin(a)/q
    return (x**2 + y**2)**0.5

def checkLimit(x,y,maxrad,minrad,offset):
    r, a = toPolar(x, y)
    if (r > maxrad) or (r < minrad):
            r = r - offset
            x, y = toRect(r, a)
    return x, y

def createHypoGear(p,d,e,n,b,ang,c,s,plane):
    x = 0.00
    y = 0.00
    i = 0
    q=2*math.pi/float(s)
    
    #if -o was specifed, calculate the tooth pitch for use in cam generation
    if b > 0:
    	p = b/n
    
    #Get root component of Fusion Design
    root = design.rootComponent;

    # Find the pressure angle limit circles
    sketchPressure = root.sketches.add(plane);
    minAngle = -1.0
    maxAngle = -1.0
    for i in range(0, 180):
            x = calcPressureAngle(p,d,n,float(i)*math.pi/180)
            if (x < ang) and (minAngle < 0):
                    minAngle = float(i)
            if (x < -ang) and (maxAngle < 0):
                    maxAngle = float(i-1)
    minRadius = calcPressureLimit(p,d,e,n,minAngle*math.pi/180)
    maxRadius = calcPressureLimit(p,d,e,n,maxAngle*math.pi/180)
    
    # Create Sketch circles 
    sketchPressure.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(-e, 0, 0),minRadius)
    sketchPressure.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(-e, 0, 0),maxRadius)
    
    #generate the cam profile - note: shifted in -x by eccentricicy amount
    sketchCAM = root.sketches.add(plane);   
    i=0
    x1 = calcX(p,d,e,n,q*i)
    y1 = calcY(p,d,e,n,q*i)
    x1, y1 = checkLimit(x1,y1,maxRadius, minRadius, c)
    
    # Collection to hold CAM Profile points
    points = adsk.core.ObjectCollection.create()
    point = adsk.core.Point3D.create(x1, y1, 0)
    points.add(point)
    
    for i in range(0, s):
        x2 = calcX(p,d,e,n,q*(i+1))
        y2 = calcY(p,d,e,n,q*(i+1))
        x2, y2 = checkLimit(x2,y2,maxRadius, minRadius, c)
        point = adsk.core.Point3D.create(x2, y2, 0)
        points.add(point)
    
    # Create Spline through points
    sketchCAM.sketchCurves.sketchFittedSplines.add(points);  
    
    # add a circle in the center of the cam
    sketchCAM.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(-e, 0, 0),d/2)  
    
    # generate the pin locations
    sketchRoller = root.sketches.add(plane);   
    for i in range(0, n+1):
        x = p*n*math.cos(2*math.pi/(n+1)*i)
        y = p*n*math.sin(2*math.pi/(n+1)*i)
        sketchRoller.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0),d/2)   

    #add a circle in the center of the pins
    sketchRoller.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0),d/2)   

class GearCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs
            p_in = 0.00
            d_in = 0.00
            e_in = 0.00
            n_in = 0
            b_in =-1.00
            a_in = 50.0
            c_in = 0.00          
            s_in = 0
            
            # We need access to the inputs within a command during the execute.
            for input in inputs:
                if input.id == 'p':
                    p_in = input
                elif input.id == 'd':
                    d_in = input
                elif input.id == 'e':
                    e_in = input
                elif input.id == 'n':
                    n_in = input
                elif input.id == 'b':
                    b_in = input
                elif input.id == 'a':
                    a_in = input
                elif input.id == 'c':
                    c_in = input
                elif input.id == 's':
                    s_in = input
                elif input.id == 'PlaneSelect':
                    plane = input.selection(0).entity
                    
            p = 0.00
            d = 0.00
            e = 0.00
            n = 0
            b =-1.00
            s = 100
            ang = 50.0
            c = 0.00

            if not p_in or not d_in or not e_in or not n_in or not a_in or not c_in:
                ui.messageBox("One of the inputs don't exist.")
                p = 0.08
                d = 0.15
                e = 0.05
                n = 10
                ang = 50.0
                c = 0.01
                s = 100
            else:
                p = unitsMgr.evaluateExpression(p_in.expression, "in")
                d = unitsMgr.evaluateExpression(d_in.expression, "in")
                e = unitsMgr.evaluateExpression(e_in.expression, "in")
                ang = 180 * unitsMgr.evaluateExpression(a_in.expression, "deg") / math.pi
                b = unitsMgr.evaluateExpression(b_in.expression, "in")
                c = 180 * unitsMgr.evaluateExpression(c_in.expression, "deg") / math.pi

                if n_in.value == '':
                    n = 10
                else:
                    n = int(n_in.value)
                
                if s_in.value == '':
                    s = 100
                else:
                    s = int(s_in.value)
            
            createHypoGear(p,d,e,n,b,ang,c,s,plane)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                
class GearCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class GearCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            cmd = args.command
            onExecute = GearCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onDestroy = GearCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onDestroy)

            # Define the inputs.
            inputs = cmd.commandInputs
            
            # Create the Selection input to have a planar face or construction plane selected.                
            selInput = inputs.addSelectionInput('PlaneSelect', 'Plane', 'Select intersecting plane.')
            selInput.addSelectionFilter('PlanarFaces')
            selInput.addSelectionFilter('ConstructionPlanes')
            selInput.setSelectionLimits(1,1)
            
            initialVal6 = adsk.core.ValueInput.createByReal(0.08)
            inputs.addValueInput('p', 'Tooth Pitch (float)', 'in' , initialVal6)

            #-b over rides p
            # ignored for now
            initialVal7 = adsk.core.ValueInput.createByReal(-1.0)
            inputs.addValueInput('b', 'Pin bolt circle radius', 'in' , initialVal7)
            
            initialVal8 = adsk.core.ValueInput.createByReal(.15)
            inputs.addValueInput('d', 'Roller Diameter', 'in' , initialVal8)
            
            initialVal9 = adsk.core.ValueInput.createByReal(.05)
            inputs.addValueInput('e', 'Eccentricity', 'in' , initialVal9)
            
            initialVal10 = adsk.core.ValueInput.createByReal(50 * (math.pi / 180))
            inputs.addValueInput('a', 'Pressure angle limit', 'deg' , initialVal10)

            initialVal11 = adsk.core.ValueInput.createByReal(.01* (math.pi / 180))
            inputs.addValueInput('c', 'offset in pressure angle', 'deg' , initialVal11)

            inputs.addStringValueInput('n', 'Number of Teeth in Cam', '10')
            inputs.addStringValueInput('s', 'Number of Segments per curve', '100')

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def main():

    try:

        commandId = 'HypoGear'
        commandName = 'Create Hypocycloid Gear'
        commandDescription = 'Create a Hypocycloid Gear'
        cmdDef = ui.commandDefinitions.itemById(commandId)
        if not cmdDef:
            resourceDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources') # absolute resource file path is specified
            cmdDef = ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription, resourceDir)

        onCommandCreated = GearCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)





    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

main()
