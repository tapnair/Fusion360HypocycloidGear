# Fusion360HypocycloidGear

Derived from: http://www.zincland.com/hypocycloid/

# ![](./resources/32x32.png) Fusion360HypocycloidGear

This is an [Autodesk Fusion 360](http://fusion360.autodesk.com/) script that's used for simply editing user parameters.

## Installation

Copy the "Fusion360HypocycloidGear" folder into your Fusion 360 "Addins" folder. You may find this folder using the following steps:

1. Start Fusion 360 and then select the File -> Scripts... menu item
2. The Scripts Manager dialog will appear and display the "My Scripts" folder and "Sample Scripts" folders
3. Click on Addins at the top of the dialog box
4. Select one of the "My Addins" files and then click on the "+" Details icon near the bottom of the dialog.
  - If there are no files in the "My Addins" folder then create a default one.
  - Click the Create button, select Python, and then OK.
5. With the user addin selected, click the Full Path "..." button to display a file explorer window that will display the "Addins" folder
6. Copy this addin folder into this location

For example, on my Mac the folder is located in:

/Users/USERNAME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Addins/

7. Next time you start Fusion the addin will be in the list.  Or you can select the green plus sign and browse to hypocycloid.py

    ![Addins Dialog](./resources/AddinsDialog.png)

## Usage

1. Run the "Fusion360HypocycloidGear" script from the Script Manager
2. The settings dialog will be shown.  Adjust to your preferences:

  ![Image of Fusion360HypocycloidGear Dialog](./resources/Fusion360HypocycloidGearDialog.png)

  - Plane : Select the plane on which the sketches will be created
  - Tooth Pitch : TODO
  - Pin Bolt Circle Radius : Radius of pin center, circle
  - Roller Diameter : Diameter of roller
  - Eccentricity : Eccentric offset in shaft 
  - Pressure Angle Limit : TODO
  - Offset in Pressure Angle : TODO
  - Number of Teeth in CAM : Number of lobes on CAM Gear
  - Number of Segments per curve : Determines accuracy. Recomend: 2,000
3. Click OK to begin

Note, after the script has run the design changes may be undone using Edit -> Undo.

### Example Usage

Here is an example of using the script to create a 30:1 reduction Gear set:
