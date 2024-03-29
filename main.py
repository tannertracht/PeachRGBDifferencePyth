import wx
import cv2
import numpy as np
# The Class WindowClass is inheriting from wx.Frame
class WindowClass(wx.Frame):
    filepath = None
    redthreshhold = 25
    bluethreshhold = 1
    kernelsize = 10

    def __init__(self, *args, **kwargs):
        # Super has something to do with inheritance
        super(WindowClass, self).__init__(*args, **kwargs)
        self.SetSize(800, 600)
        self.basicGUI()

    def basicGUI(self):
        self.panel = wx.Panel(self)
        # Define menuBar and set it to a MenuBar type
        menubar = wx.MenuBar()
        # Define fileButton and set it to a Menu type
        filebutton = wx.Menu()
        # Define exitItem and attach it to the fileButton
        exititem = filebutton.Append(wx.ID_EXIT, 'Exit', 'status msg...')
        # Attach fileButton to menuBar
        menubar.Append(filebutton, 'File')
        # Define Labels
        redthreshlabel = wx.StaticText(self.panel, -1, 'Red Threshold value (Default 25). '
                                      'Sets the R value that a pixel must exceed to be binarized')
        bluethreshlabel = wx.StaticText(self.panel, -1, 'Blue Threshold value (Default 1). '
                                      'Sets the B value that a pixel must exceed to be binarized')
        kernellabel = wx.StaticText(self.panel, -1, 'Kernel Matrix Size (Default 10). '
                                      'Affects the size a blossom must be to be detected')
        # Define Inputs
        analyzebutton = wx.Button(self.panel, -1, 'Analyze Image')
        imagebutton = wx.Button(self.panel, -1, 'Choose Image')
        self.redthresholdinput = wx.TextCtrl(self.panel, 5, style=wx.TE_PROCESS_ENTER)
        self.bluethresholdinput = wx.TextCtrl(self.panel, 1, style=wx.TE_PROCESS_ENTER)
        self.kernelsizeinput = wx.TextCtrl(self.panel, -1, style=wx.TE_PROCESS_ENTER)
        self.imageselector = wx.Choice(self.panel, -1, name='Image Selector')
        # Create Sizers to hold buttons and labels
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        analyzesizer = wx.BoxSizer(wx.HORIZONTAL)
        analyzesizer.Add(analyzebutton, 0, 0, 0)
        imagesizer = wx.BoxSizer(wx.HORIZONTAL)
        imagesizer.Add(imagebutton, 0, 0, 0)
        redthreshsizer = wx.BoxSizer(wx.HORIZONTAL)
        redthreshsizer.Add(self.redthresholdinput, 0, 0, 0)
        redthreshsizer.Add(redthreshlabel, 0, wx.LEFT | wx.TOP, 5)
        bluethreshsizer = wx.BoxSizer(wx.HORIZONTAL)
        bluethreshsizer.Add(self.bluethresholdinput, 0, 0, 0)
        bluethreshsizer.Add(bluethreshlabel, 0, wx.LEFT | wx.TOP, 5)
        kernelsizer = wx.BoxSizer(wx.HORIZONTAL)
        kernelsizer.Add(self.kernelsizeinput, 0, 0, 0)
        kernelsizer.Add(kernellabel, 0, wx.LEFT | wx.TOP, 5)
        imageselectorsizer = wx.BoxSizer(wx.HORIZONTAL)
        imageselectorsizer.Add(self.imageselector, 0, 0, 0)
        self.sizer.Add(imagesizer, 0, wx.TOP | wx.BOTTOM, 5)
        self.sizer.Add(analyzesizer, 0, wx.TOP | wx.BOTTOM, 5)
        self.sizer.Add(redthreshsizer, 0, wx.TOP | wx.BOTTOM, 5)
        self.sizer.Add(bluethreshsizer, 0, wx.TOP | wx.BOTTOM, 5)
        self.sizer.Add(kernelsizer, 0, wx.TOP | wx.BOTTOM, 5)
        self.sizer.Add(imageselectorsizer, 0, wx.TOP | wx.BOTTOM, 5)
        self.panel.SetSizer(self.sizer)
        # Set the frame's MenuBar to the menuBar we've created
        self.SetMenuBar(menubar)
        # Search for a call originating from exitItem in EVT_MENU and call self.Quit
        self.Bind(wx.EVT_MENU, self.quit, exititem)

        # Bind Buttons and Stuff
        self.Bind(wx.EVT_BUTTON, self.AnalyzeImage, analyzebutton)
        self.Bind(wx.EVT_BUTTON, self.filedialog, imagebutton)
        self.Bind(wx.EVT_TEXT_ENTER, self.updateredthreshold, self.redthresholdinput)
        self.Bind(wx.EVT_TEXT_ENTER, self.updatebluethreshhold, self.bluethresholdinput)
        self.Bind(wx.EVT_TEXT_ENTER, self.updatekernel, self.kernelsizeinput)


        self.SetTitle('Control Panel')
        self.Show(True)

    def quit(self, e):
        self.Close()

    def filedialog(self, e):
        with wx.FileDialog(self, "Open File",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Set pathname to the file path of the image
            self.filepath = fileDialog.GetPath()
            wx.StaticText(self.panel, -1, self.filepath, wx.Point(105, 5))

    def AnalyzeImage(self, e):
        pathname = self.filepath
        # Load visible image with
        visibleimg = cv2.imread(pathname, 1)
        # Split the image into the 3 bands
        b, g, r = cv2.split(visibleimg)
        # Subtract R image from G image to highlight blossoms
        rminusg = cv2.subtract(r, g)
        bminusg = cv2.subtract(b, g)
        rminusgminusb = cv2.subtract(rminusg, b)
        # Convert images to binary image with thresholding
        th, rbinaryimg = cv2.threshold(rminusg, self.redthreshhold, 255, cv2.THRESH_BINARY);
        th, bbinaryimg = cv2.threshold(bminusg, self.bluethreshhold, 255, cv2.THRESH_BINARY);
        # Convert to a final binary image where pixels are white only where both images above had white pixels.
        binaryimg = cv2.bitwise_and(rbinaryimg,bbinaryimg)
        # Kernel used to denoise
        # image, used in morphology functions
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.kernelsize, self.kernelsize))
        # Denoise using morphology opening (Eroding then Dilating)
        denoiseimg = cv2.morphologyEx(binaryimg, cv2.MORPH_OPEN, kernel)
        # Label the Pixel Groups. Returns 4 matrixes inside the 'labels' array
        labels = cv2.connectedComponentsWithStats(denoiseimg, 4, cv2.CV_32S)
        # The fourth value of labels is a matrix where each row is a label
        # and each column is that label's x coordinate and y coordinate respectively
        centroids = labels[3]
        # Labels[0] holds the value of the number of labels in the image
        # Place a number in the top left indicating how many blossoms were detected
        cv2.putText(visibleimg, str(labels[0]), (40,250), 1, 15, (0, 0, 255), 4)
        for x in range(labels[0]):
            # Convert coordinates to INT so they can be used in circle creation
            xcoord = int(centroids[x, 0])
            ycoord = int(centroids[x, 1])
            # Mark each label with a blue circle
            cv2.circle(visibleimg, (xcoord, ycoord), 30, (255, 0, 0), 2)
        # Create window to display our images in, set the window size to normal so it can display big images nicely
        cv2.namedWindow('Blossom Identifier', cv2.WINDOW_NORMAL)
        cv2.imshow('Blossom Identifier', visibleimg)
        # Create array of our images to be used in the wx.Choice dropdown
        imagechoices = ['Red Band', 'Green Band', 'Blue Band', 'Red minus Green', 'Blue minus Green', 'Binary Image', 'Denoised Image', 'Red Minus Everything']
        # Move all our images created into an array to be passed into a function
        imagelist = [r, g, b, rminusg, bminusg, binaryimg, denoiseimg, rminusgminusb]
        # Define the wx.dropdown menu that will contain our created images
        self.imageselector.Clear()
        self.imageselector.Append(imagechoices)

        # When user selects an image from the dropdown it will pass the imagelist array at the index of the selection,
        # Effectively passing in the image from the dropdown we selected to be displayed.
        self.Bind(wx.EVT_CHOICE, lambda event: self.showimage(event, imagelist[self.imageselector.GetSelection()]), self.imageselector)

    def cropimage(self, image):
        pass

    def updateredthreshold(self, e):
        # Updates threshold value from value in the input box
        self.redthreshhold = int(self.redthresholdinput.GetValue())

    def updatebluethreshhold(self, e):
        # Updates threshhold value for blue binary image creation
        self.bluethreshhold = int(self.bluethresholdinput.GetValue())

    def updatekernel(self, e):
        # Updates kernel value from the value in the input box
        self.kernelsize = int(self.kernelsizeinput.GetValue())

    def showimage(self, e, image):
        # Shows the image that was selected in the dropdown
        cv2.namedWindow('Selected Image', cv2.WINDOW_NORMAL)
        cv2.imshow('Selected Image', image)


def main():
    app = wx.App()
    WindowClass(None)
    app.MainLoop()


main()
