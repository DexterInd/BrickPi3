import wx
import os
import subprocess

ICON_PATH = os.path.join(os.path.expanduser("~"), "BrickPi3/Software/Python/brickpi3/examples/icons/")


class MainPanel(wx.Panel):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""

        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundColour(wx.WHITE)
        self.frame = parent

        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False,
                        'Helvetica')
        self.SetFont(font)

        vSizer = wx.BoxSizer(wx.VERTICAL)

        # Icon
        icon_sizer = wx.BoxSizer(wx.HORIZONTAL)
        try:
            if os.path.exists(ICON_PATH+"dexter_industries_logo.png"):
                bmp = wx.Bitmap(ICON_PATH+"dexter_industries_logo.png",
                    type=wx.BITMAP_TYPE_PNG)
                bitmap=wx.StaticBitmap(self,bitmap=bmp)
                icon_sizer.Add(bitmap,0,wx.RIGHT|wx.LEFT|wx.EXPAND,50)
        except:
            pass  # Continue without logo if icon path doesn't exist

        # Troubleshoot the BrickPi3
        brickpi3_sizer = wx.BoxSizer(wx.HORIZONTAL)
        troubleshoot_brickpi3 = wx.Button(self, label="Troubleshoot BrickPi3")
        troubleshoot_brickpi3.Bind(wx.EVT_BUTTON, self.brickpi3)
        brickpi3_txt=wx.StaticText(self, -1, "This button runs a series of tests on the BrickPi3 Hardware.")
        brickpi3_txt.Wrap(150)
        brickpi3_sizer.AddSpacer(50)
        brickpi3_sizer.Add(troubleshoot_brickpi3,1,wx.EXPAND)
        brickpi3_sizer.AddSpacer(20)
        brickpi3_sizer.Add(brickpi3_txt,1,wx.ALIGN_CENTER_VERTICAL)
        brickpi3_sizer.AddSpacer(50)

        # Exit
        exit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        exit_button = wx.Button(self, label="Exit")
        exit_button.Bind(wx.EVT_BUTTON, self.onClose)
        exit_sizer.AddSpacer(50)
        exit_sizer.Add(exit_button,1,wx.EXPAND)
        exit_sizer.AddSpacer(50)

        vSizer.Add(icon_sizer,0,wx.SHAPED|wx.FIXED_MINSIZE)
        vSizer.Add(brickpi3_sizer,1,wx.EXPAND)
        vSizer.AddSpacer(20)
        vSizer.Add(exit_sizer,1,wx.EXPAND)
        vSizer.AddSpacer(20)

        self.SetSizerAndFit(vSizer)


    def brickpi3(self, event):
        dlg = wx.MessageDialog(self, 'This program tests the BrickPi3 for potential issues or problems and will make a log report you can send to Dexter Industries.  \n It takes a few moments for the test to start, and once it has begun, it might take a few minutes to run through all the tests.', 'Troubleshoot the BrickPi3', wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
        ran_dialog = False
        if dlg.ShowModal() == wx.ID_OK:
            print("Running BrickPi3 Tests!")
            home_dir = os.path.expanduser("~")
            subprocess.call(['sudo', 'chmod', '+x', f'{home_dir}/BrickPi3/Software/Python/brickpi3/Troubleshooting/all_tests.sh'])
            subprocess.call(['sudo', 'bash', f'{home_dir}/BrickPi3/Software/Python/brickpi3/Troubleshooting/all_tests.sh'])
            ran_dialog = True
        else:
            print("Cancel BrickPi3 Tests!")
        dlg.Destroy()

        # Depending on what the user chose, we either cancel or complete.
        if ran_dialog:
            dlg = wx.MessageDialog(self, 'All tests are complete. The Log has been saved to Desktop. Please copy it and upload it into our Forums.  www.dexterindustries.com/Forum', 'OK', wx.OK|wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self, 'BrickPi3 Test Cancelled', 'Canceled', wx.OK|wx.ICON_HAND)
            dlg.ShowModal()
            dlg.Destroy()

    def onClose(self, event):
        self.frame.Close()


class MainFrame(wx.Frame):
    def __init__(self):
        """Constructor"""
        wx.Log.SetVerbose(False)

        # Set the frame arguments
        wx.Frame.__init__(self, None, title="Test and Troubleshoot BrickPi3")

        # Set the application icon
        try:
            icon = wx.Icon(ICON_PATH+'favicon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
        except:
            pass
        self.panel = MainPanel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel,1,wx.EXPAND)
        self.SetSizerAndFit(sizer)
        self.Center()


if __name__ == "__main__":
    app = wx.App(redirect=False)
    frame = MainFrame()
    frame.Show(True)
    app.MainLoop()