import wx
import cv2
import numpy as np
# The Class WindowClass is inheriting from wx.Frame
class WindowClass(wx.Frame):
    filepath = None
    threshhold = 25
    kernelsize = 15

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
        # Define buttons and stuff
        analyzebutton = wx.Button(self.panel, -1, 'Analyze Image', wx.Point(0, 25))
        imagebutton = wx.Button(self.panel, -1, 'Choose Image')
        thresholdinput = wx.TextCtrl(self.panel, 5, pos=wx.Point(0, 55), style=wx.TE_PROCESS_ENTER)
        kernelsizeinput = wx.TextCtrl(self.panel, -1, pos=wx.Point(0, 85), style=wx.TE_PROCESS_ENTER)

        # Set the frame's MenuBar to the menuBar we've created
        self.SetMenuBar(menubar)
        # Search for a call originating from exitItem in EVT_MENU and call self.Quit
        self.Bind(wx.EVT_MENU, self.quit, exititem)

        # Bind Buttons and Stuff
        self.Bind(wx.EVT_BUTTON, self.AnalyzeImage, analyzebutton)
        self.Bind(wx.EVT_BUTTON, self.filedialog, imagebutton)
        self.Bind(wx.EVT_TEXT_ENTER, self.updatethreshold, thresholdinput)
        self.Bind(wx.EVT_TEXT_ENTER, self.updatekernel, kernelsizeinput)
        wx.StaticText(self.panel, -1, 'Threshold value (Default 25)', wx.Point(115, 60))
        wx.StaticText(self.panel, -1, 'Kernel Matrix Size (Default 15)', wx.Point(115, 90))

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
        bminusg = cv2.subtract(b, g)  # not currently using this in calculations
        # Convert image to binary image with thresholding
        th, binaryimg = cv2.threshold(rminusg, self.threshhold, 255, cv2.THRESH_BINARY);
        # Kernel used to denoise image, used in morphology functions
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
        imagechoices = ['Red Band', 'Green Band', 'Blue Band', 'Red minus Green', 'Blue minus Green', 'Binary Image', 'Denoised Image']
        imagelist = [r, g, b, rminusg, bminusg, binaryimg, denoiseimg]
        imageselector = wx.Choice(self.panel, -1, pos=wx.Point(0, 115), choices=imagechoices, name='Image Selector')
        self.Bind(wx.EVT_CHOICE, lambda event: self.showimage(event, imagelist[imageselector.GetSelection()]), imageselector)

    def updatethreshold(self, e):
        print('thres')
        self.threshhold = int(self.panel.Children[2].GetValue())

    def updatekernel(self, e):
        print('kern')
        self.kernelsize = int(self.panel.Children[3].GetValue())

    def showimage(self, e, image):
        cv2.namedWindow('Selected Image', cv2.WINDOW_NORMAL)
        cv2.imshow('Selected Image', image)

def main():
    app = wx.App()
    WindowClass(None)

    app.MainLoop()


main()
