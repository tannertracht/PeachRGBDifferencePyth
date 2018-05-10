import wx
import cv2
import numpy as np
# The Class WindowClass is inheriting from wx.Frame
class WindowClass(wx.Frame):

    def __init__(self, *args, **kwargs):
        # Super has something to do with inheritance
        super(WindowClass, self).__init__(*args, **kwargs)
        self.SetSize(800, 600)
        self.basicGUI()

    def basicGUI(self):
        global panel
        panel = wx.Panel(self)
        # Define menuBar and set it to a MenuBar type
        menubar = wx.MenuBar()
        # Define fileButton and set it to a Menu type
        filebutton = wx.Menu()
        # Define exitItem and attach it to the fileButton
        exititem = filebutton.Append(wx.ID_EXIT, 'Exit', 'status msg...')
        # Attach fileButton to menuBar
        menubar.Append(filebutton, 'File')
        # Define imageButton
        imageButton = wx.Button(panel, -1, 'Analyze Image')

        # Set the frame's MenuBar to the menuBar we've created
        self.SetMenuBar(menubar)
        # Search for a call originating from exitItem in EVT_MENU and call self.Quit
        self.Bind(wx.EVT_MENU, self.quit, exititem)

        # Bind imageButton to function
        self.Bind(wx.EVT_BUTTON, self.filedialog, imageButton)

        self.SetTitle('Peach Blossom Detection')
        self.Show(True)

    def quit(self, e):
        self.Close()

    def filedialog(self, e):
        with wx.FileDialog(self, "Open File",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Set pathname to the file path of the image
            pathname = fileDialog.GetPath()
            return pathname
            # Load visible image with
            visibleimg = cv2.imread(pathname, 1)

            # Split the image into the 3 bands
            b,g,r = cv2.split(visibleimg)
            # Subtract R image from G image to highlight blossoms
            rminusg = cv2.subtract(r, g)
            # bminusg = cv2.subtract(b, g) not currently using this in calculations
            # Convert image to binary image with thresholding
            th, binaryimg = cv2.threshold(rminusg, 25, 255, cv2.THRESH_BINARY);
            # Kernel used to denoise image, used in morphology functions
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            # Denoise using morphology opening (Eroding then Dilating)
            denoiseimg = cv2.morphologyEx(binaryimg,cv2.MORPH_OPEN, kernel)
            # Label the Pixel Groups. Returns 4 matrixes in labels
            labels = cv2.connectedComponentsWithStats(denoiseimg, 4, cv2.CV_32S)
            # The fourth value of labels is a matrix where each row is a label
            # and each column is that label's x coordinate and y coordinate respectively
            centroids = labels[3]
            for x in range(labels[0]):
                xcoord = int(centroids[x,0])
                ycoord = int(centroids[x,1])
                cv2.circle(visibleimg, (xcoord, ycoord), 30, (255,0,0), 2)
            # Create window to display our images in, set the window size to normal so it can display big images nicely
            cv2.namedWindow('Red', cv2.WINDOW_NORMAL)
            cv2.imshow('Red', visibleimg)

    def AnalyzeImage(self, imagepath):



def main():
    app = wx.App()
    WindowClass(None)

    app.MainLoop()


main()
