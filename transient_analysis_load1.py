"""
   This file is the main Python file for the "Template8-TargetedAnalysisLoad" template. 
   
   Remark:
   Python programming expects users to respect certain formats.
   e.g. The leading whitespace (spaces and tabs) at the beginning of a line (i.e. the indentation level of the line) is VERY IMPORTANT in Python.
   DO NOT mix spaces and tabs while indenting a line.
"""
import os
import units
import materials
import wbjn
import clr

def createTransientLoad(analysis):
    global Analysis_index, file_path, file_name
    """
       This method is called when the toolbar button "Transient Thermal Load" is clicked.

       Keyword arguments:
       analysis -- the active analysis
    """
    idd=int(Analysis_index)
    # We don't need to add any check here as <canadd> callback will do the check
    analysis.CreateLoadObject("StructuralLLoad", ExtAPI.ExtensionManager.CurrentExtension)
    #scriptcommand = r"""
    DataModel=ExtAPI.DataModel
    model=DataModel.Project.Model
    #model=ExtAPI.DataModel.Project.Model # this works only for verion 2020 above
    geom=model.Geometry
    mesh=model.Mesh
    materials = model.Materials   
    #analysis = model.Analyses[0]
    #as we have two analysis 1. static structural and another Thermal analysis we have used Analyses[1] else we can use Analyses[0]
    analysis = model.Analyses[idd]
    solution = analysis.Solution
    connnections=model.Connections
    conn1=model.Connections
    
    #-----------------------reading Multiple data--------------------
    
    timepath = file_path+'\RTIMES.txt'
    
    with open(timepath,"r") as r:
        data = r.read().strip()
        datalist = data.split('\n')
    times = map(float,datalist)
    
    analysis.AnalysisSettings.NumberOfSteps = len(times)
    with Transaction():
        for index, value in enumerate(reversed(times)):
            n=len(times) - index
            print(n, value)
            analysis.AnalysisSettings.CurrentStepNumber = n
            analysis.AnalysisSettings.StepEndTime=Quantity("{}[sec]".format(value))
    		
    time_vals = [Quantity("{} [sec]".format(t)) for t in times]
    		
    import clr
    data1 =  file_path
    clr.AddReference("Microsoft.Office.Interop.Excel")
    import Microsoft.Office.Interop.Excel as Excel
    import os
    mypath = data1
    myExcel = Excel.ApplicationClass()
    myExcel.Visible = True
    myExcel.DisplayAlerts = False
    excel_file_name = file_name
    workbook = myExcel.Workbooks.Open(os.path.join(mypath,excel_file_name))
    myWorkSheet = workbook.Worksheets[1]
    worsheetrange = myWorkSheet.UsedRange
    
    rowcount= worsheetrange.Rows.Count
    #print(rowcount)
    colCount= worsheetrange.Columns.Count
    #print(colCount)
    
    myWorkSheet2 = workbook.Worksheets[2]
    worsheetrange2 = myWorkSheet2.UsedRange
    rowcount2= worsheetrange2.Rows.Count
    colCount2= worsheetrange2.Columns.Count
    gp=model.NamedSelections.Children
    
    gplist=[]
    gp=model.NamedSelections.Children
    for i in gp:
        gplist.append(i.Name)
        
    namedselection=[]
    for i in range(1,colCount):
        namedselection.append(worsheetrange.Cells[1,i].Value2)
    
    indices_dict = {}
    for i, num in enumerate(namedselection):
        if num in indices_dict:
            indices_dict[num].append(i)
        else:
            indices_dict[num] = [i]
    ids = [indices_dict[num][0] for num in gplist if num in indices_dict]
    
    ##___________________working AS EXPECTED... Removed pair of square bracket because of which we got list of list in the output	
    for i in ids:
        convection1=analysis.AddConvection()
        cv=DataModel.GetObjectsByName(namedselection[i])[0]
        convection1.Location= cv
        convection1.Name=str('Convection_'+cv.Name)
        convection1.FilmCoefficient.Inputs[0].DiscreteValues = time_vals
        convection1.AmbientTemperature.Inputs[0].DiscreteValues = time_vals
        Convection_vals =[]
        for j in range(2,rowcount):
            Convection_vals.append(Quantity("{} [W m^-1 m^-1 C^-1]".format(worsheetrange.Cells[j,i+1].Value2)))
        convection1.FilmCoefficient.Output.DiscreteValues = Convection_vals
        Temperature_vals =[]
        for k in range(2,rowcount):
            Temperature_vals.append(Quantity("{} [C]".format(worsheetrange2.Cells[k,i+1].Value2)))
        convection1.AmbientTemperature.Output.DiscreteValues = Temperature_vals
    myExcel.Quit()
    #    """
    #import wbjn
    #wbjn.ExecuteCommand(ExtAPI,createStaticLoad) 

def createInputLoad(analysis):
    """
       This method is called when the toolbar button "Input Values" is clicked.

       Keyword arguments:
       analysis -- the active analysis
    """

    import clr
    clr.AddReference('System.Windows.Forms')
    clr.AddReference('System.Drawing')
    
    #   get the objects you need from forms and drawing
    from System.Windows.Forms import Form, Label, Button, TextBox
    from System.Drawing import Point, ContentAlignment
    
    #-- The way python works with events, you have to make a class out of your form.  
    #   Then the objects 
    #    you add are available in event functions.
    class TowerForm(Form):
        global Analysis_index, file_path, file_name
        def __init__(self):
    #-- First, make the form (self)
            self.text="Transient Load Tool"
            self.Height=450
            self.Width=450
    
    #-- Create a Simple Text Label describing the tool
    #   it is not self.label because we are not going to access it in event functions
            lbl1 = Label()
            lbl1.Text = "\n     Inputs for Transient Loads \n"
                
            lbl1.Height = 50
            lbl1.Width = 200
            
    
    #-- Create the Text Labels and text boxes to get Dimensions and Pressure
    #   We need to get to the textboxes so we will make them part of the class
    #
    #   some constants to make the positioning easier
            x1 = 10
            y1 = 80
            w1 = 140
            w2 = 240
            x2 = x1 + w1 + 10
    #   Make the labels for the text boxes.  This is done in the Labe() call with 
    #   Name = Value arguments 
    #   instead of object.name = value to save space.  All in one line instead of 
    #   four lines.
    #     The alighment is done so that the labels are all right justified to line 
    #     up with the boxes. Set ContentAlignment.MiddleRight to mr to save space
            mr = ContentAlignment.MiddleCenter
            lb_Length=Label(Text="Analysis Index", Width=w1,TextAlign=mr)
            lb_Width  = Label(Text="Excel Path",   Width = w1, TextAlign=mr)
            lb_Height = Label(Text=".xlsx File name ",  Width = w1, TextAlign=mr)
            #lb_Press  = Label(Text="Pressure",Width = w1, TextAlign=mr)
    
    #   Make the text boxes. Note that these are put in the self. class. 
    #   We do this so that when the OK 
    #   button is pushed, we have access to the text boxes and therefore the values 
    #   typed within
    
            self.An_Index = TextBox(Width = w2)
            self.tb_Width  = TextBox(Width = w2)
            self.tb_Height = TextBox(Width = w2)
            self.tb_Press  = TextBox(Width = w2)
    
    #   Specify the location for the label and the text boxes.  Move down by 
    #   30 after each line
            lb_Length.Location = Point(x1,y1)
            self.An_Index.Location = Point(x2,y1)
            y1 = y1 + 50
            lb_Width.Location = Point(x1,y1)
            self.tb_Width.Location = Point(x2,y1)
            y1 = y1 + 50
            lb_Height.Location = Point(x1,y1)
            self.tb_Height.Location = Point(x2,y1)
            y1 = y1 + 50
            #lb_Press.Location = Point(x1,y1)
            #self.tb_Press.Location = Point(x2,y1)
    
    #   Make an OK and a Cancel Button
            okBut = Button(Text="OK", Width=50)
            okBut.Location = Point(80,350)
    #       This is where you specify the funtion to be called when the button is clicked
    #       note that you call the function self.functionname.
            okBut.Click += self.okButPressed
    
            cancelBut = Button(Text="Cancel", Width=50)
            cancelBut.Location = Point(250,350)
            cancelBut.Click += self.cancelButPressed
    
    #   Put everything on the form (some sort of list and loop would make this easier)
            self.Controls.Add(lbl1)
            self.Controls.Add(lb_Length)
            self.Controls.Add(self.An_Index)
            self.Controls.Add(lb_Width)
            self.Controls.Add(self.tb_Width)
            self.Controls.Add(lb_Height)
            self.Controls.Add(self.tb_Height)
            #self.Controls.Add(lb_Press)
            #self.Controls.Add(self.tb_Press)
            self.Controls.Add(okBut)
            self.Controls.Add(cancelBut)
    
    #-- Now define the button event functions as part of the class
    #
    # Cancel simply closes the form down.  Nothing fancy
        def cancelButPressed(self, sender, args ):
            print 'Closing the Window... Bye...\n'
            self.Close()
    
    # OK prints the values of the text boxes to the console
    #   This will be replaced with calls to workbench for the next step
        def okButPressed(self, sender, args ):
            global Analysis_index, file_path, file_name
            print 'Values Entered:\n'
            Analysis_index = self.An_Index.Text
            print(Analysis_index)
            file_path = self.tb_Width.Text
            file_name = self.tb_Height.Text
            print 'Pressure: %s\n' %self.tb_Press.Text
            self.Close()
    #---------End of class definition
    
    
    # Instantiate the form and make the form visible
    print '=======================================\n'
    print 'Opening the Windows...\n'
    myForm = TowerForm()
    Form.ShowDialog(myForm)
   
    
def canAddStaticLoad(analysis, loadName):
    """
       Method called to check if the "Structural Load" load object can be created in the current analysis.
       Return True or False.

       Keyword arguments:
       analysis -- the analysis on which the load object is added
       loadName -- the added object name
    """

    # Check the Analysis and Physics type.
    if analysis.AnalysisType.ToString() == "Transient" and analysis.PhysicsType.ToString() == "Mechanical":
        return True

    # In case of other analysis/physics type.
    msg = "Selected Analysis is: " + analysis.Name + "\n"
    msg += "Load: " + loadName + " is applicable for Transient Thermal analysis only"
    ExtAPI.Application.LogWarning(msg)
    return False
