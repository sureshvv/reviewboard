
# Requires: python 2.4
#     wx version 2.8

import wx
import time
import wx.lib.hyperlink as hl
import postreview as review
import old_review
import os
import sys
import pickle

VERSION = "alpha"

UPDATE_BUTTON = 5
REFRESH_BUTTON = 6
PUBLISH_BUTTON = 9
EXIT_BUTTON = 4
LOGIN = 7
CL_LIST = 8
REVIEWBOARD_HOST = None

PICKLE_FILE = "pickle"

class ChangeListInfo(object):
  def __init__(self, id, text, full, files, post=None, rbid=None, review_request=None):
    self.id = id
    self.files = files
    self.descrip = text
    self.full = full
    self.info = post
    self.rbid = rbid
    self.review_request = review_request
    self.last_post = None

  def Display(self):
    return "%6s: %s" % (self.id, self.descrip)

  def Url(self):
    return '%s/r/%s/' % (REVIEWBOARD_HOST, self.rbid)

  def beenPosted(self):
    return self.review_request != None

  def afterPost(self, review_request, info):
    self.rbid = review_request['id']
    self.info = info
    self.review_request = review_request
# info in the review_request
    rb_summary = review_request['summary']
    rb_descript  = review_request['description']
    rb_testing_done = review_request['testing_done']
# contains: first_name, fullname, id, last_name, url, username, email
    reviewers = review_request['target_people'] 
# contains: display_name, id, url, name, mailing_list 
    group = review_request['target_groups']
    #import pprint
    #pprint.pprint(review_request)
    self.last_post = time.localtime()

  def p4_info(self):
    r = self.full + self.files
    return r
  def rb_info(self):
    if not self.beenPosted():
      return "No Review Board info"
    people = [a['fullname'] for a in self.review_request['target_people']]
    groups = [a['display_name'] for a in self.review_request['target_groups']]
    r = ""
    r += "Reviewers: %s\n" % ', '.join(people)
    r += "Groups: %s\n" % ', '.join(groups)
    r += "Summary: %s\n" % self.review_request['summary']
    r += "Description:\n %s\n" % self.review_request['description']
    return r

  def postTime(self):
    if not self.last_post:
      return "None"
    return time.strftime("%m/%d/%y %H:%M", self.last_post)

  def postInfo(self):
    if self.beenPosted():
      return "Posted on %s" % self.postTime()
    return "Not Posted"
  def __cmp__(self, other):
    return cmp(int(self.id), int(other.id))

class MyFrame(wx.Frame):

  def makeCLList(self):
    new_list = []
    pending = self.SCM.getPendingCLs(True)
    if self.cls:
      pending_map = {}
      for (id, text, full, files) in pending:
        pending_map[id] = (text, full, files)
      for i in range(len(self.cls)):
        info = self.cls[i]
        if info.id not in pending_map:
          continue
        info.descrip, info.full, info.files = pending_map[info.id]
        new_list.append(info)
        del pending_map[info.id]
      for (id, (text, full, files)) in pending_map.iteritems():
        new_list.append(ChangeListInfo(id, text, full, files))
    else:
      new_list = [ChangeListInfo(id, text, full, files)
          for (id, text, full, files) in pending]
    new_list.sort()
    self.cls = new_list

  def saveList(self):
    try:
      pkl_file = open(PICKLE_FILE, "wb")
      pickle.dump(self.cls, pkl_file)
      pkl_file.close()
    except:
      # skip all the errors
      pass

  def loadList(self):
    try:
      pkl_file = open(PICKLE_FILE, "rb")
      t = pickle.load(pkl_file)
      self.cls = t
      pkl_file.close()
    except:
      # skip all the errors
      pass  

  def makeButtons(self, update, refresh, publish):
    buttons = wx.BoxSizer(wx.HORIZONTAL)
    buttons.AddStretchSpacer(1)
    buttons.Add(update, .4)
    buttons.Add(refresh, .4)
    buttons.Add(publish, .4)
    buttons.AddStretchSpacer(1)
    return buttons

  def layoutStuff(self, items):
    """ the second item is always made growable """
    hbox = wx.BoxSizer(wx.HORIZONTAL)

    fgs = wx.FlexGridSizer(0, 1, 9, 5)
    insert = [(i, 1, wx.EXPAND) for i in items]

    fgs.AddMany(insert)

    fgs.AddGrowableRow(1, 1)
    fgs.AddGrowableCol(0, 1)

    hbox.Add(fgs, 1, wx.ALL | wx.EXPAND, 15)
    return hbox

  def setupRB(self):
    self.Reviewboard = None
    if os.environ.has_key("USERPROFILE"):
      cookiepath = os.path.join(os.environ["USERPROFILE"], "UserData")
    else:
      cookiepath = os.environ["HOME"]

    #cookiefile = os.path.join(cookiepath, ".post-review-cookies.txt")
    cookiefile = os.path.join(cookiepath, ".gui-post-review-cookies.txt")
    self.Reviewboard = review.ReviewBoardServer(REVIEWBOARD_HOST,
      self.SCM.get_repository_info(), cookiefile) 
    review.parse_options(self.SCM,  self.SCM.get_repository_info(), [])

  def __init__(self, parent, id, title):
    self.cls = None
    self.SCM = review.PerforceClient()
    self.setupRB()
    my_size = (300,250)
    wx.Frame.__init__(self, parent, id, title,
          wx.DefaultPosition, my_size)
    _icon = wx.Icon('favicon.ico', wx.BITMAP_TYPE_ICO)
    self.SetIcon(_icon)
    self.panel = wx.Panel(self, -1)
    dropdown_l = wx.StaticText(parent=self.panel)
    dropdown_l.SetLabel("Select a Changelist")
    self.dropdown = wx.ListBox(id=CL_LIST, parent=self.panel)
    self.dropdown.SetSize((350,48))
    publish = wx.Button(self.panel, PUBLISH_BUTTON, "Publish")
    publish.Hide()
    update = wx.Button(self.panel, UPDATE_BUTTON, "Post to Reviewboard")
    refresh = wx.Button(self.panel, REFRESH_BUTTON, "Refresh CLs")
    self.hyper = hl.HyperLinkCtrl(self.panel, -1, "")
    self.hyper.SetURL("http://")
    self.hyper.SetLabel("")
    self.hyper.Enable(False)
    # we don't want the color to change
    c = self.hyper.GetColours()[0]
    self.hyper.SetColours(c, c, c)
    self.lines = wx.StaticText(parent=self.panel)
    self.lines.SetLabel("")

    self.info_win = None

    things = []
    things.append(dropdown_l)
    things.append(self.dropdown)
    things.append(self.makeButtons(update, refresh, publish))
    things.append(self.lines)
    things.append(self.hyper)
    self.panel.SetSizer(self.layoutStuff(things))
    self.panel.Fit()
    self.SetMinSize(my_size)

    menu = wx.Menu()
    menuBar = wx.MenuBar()
    menu.Append(REFRESH_BUTTON, "&Update CL List")
    menu.AppendSeparator()
    menu.Append(EXIT_BUTTON, "Exit")
    menuBar.Append(menu, "&File")
    self.SetMenuBar(menuBar)
    # for some reason removing the menubar messes up the sizers
    # so for now I just add and remove it
    self.SetMenuBar(None)
    self.Bind(wx.EVT_MENU, self.refresh, id=REFRESH_BUTTON)
    self.Bind(wx.EVT_CLOSE, self.exit)
    self.Bind(wx.EVT_BUTTON, self.update, id=UPDATE_BUTTON)
    self.Bind(wx.EVT_BUTTON, self.publish, id=PUBLISH_BUTTON)
    self.Bind(wx.EVT_BUTTON, self.refresh, id=REFRESH_BUTTON)
    self.Bind(wx.EVT_LISTBOX, self.onchange, id=CL_LIST)
    self.Bind(wx.EVT_LISTBOX_DCLICK, self.double_click, id=CL_LIST)
    self.login()
    self.loadList()
    self.refresh(None)
  
  def clearInfo(self):
    self.hyper.SetLabel("")
    self.lines.SetLabel("")
    self.hyper.Enable(False)
    self.Update()

  def showPost(self, info, linktext=None, url=None):
    if linktext and url:
      self.hyper.SetLabel(linktext)
      self.hyper.SetURL(url)
      self.hyper.Enable(True)
    self.lines.SetLabel(info)
    self.Update()

  def showWaiting(self, msg=None):
    self.clearInfo()
    if not msg:
      self.showPost("Posting to Reviewboard")
    else:
      self.showPost(msg)
    self.Update()

  def getSelectedCL(self):
    selected = self.dropdown.GetSelections()
    if len(selected) == 0:
      selected = 0
    else:
      selected = selected[0]
    cl = self.dropdown.GetClientData(selected)
    return cl

  def showItemInfo(self):
    self.clearInfo()
    cl = self.getSelectedCL()
    self.showPost(cl.postInfo())
    if not cl.beenPosted():
      return
    url = cl.Url()
    linktext = "View CL#%s (Review Number %s)" % (cl.id, cl.rbid)
    self.showPost(cl.postInfo(), linktext, url)

  def double_click(self, event):
    cl= self.getSelectedCL()
    if not self.info_win:
      self.info_win = InfoWin(None, -1)
      self.info_win.Show(True)
    self.info_win.SetInfo(cl.p4_info(), cl.rb_info())

  def onchange(self, event):
    self.showItemInfo()

  def try_post(self, changenum):
    try:
      review_request = self.Reviewboard.new_review_request(changenum, None)
    except :
      self.login()
      return None
    return review_request

  def publish(self, event):
    self.showWaiting(msg="This function doesn't work right yet")
    return
    cl= self.getSelectedCL()
    if not cl.beenPosted():
      self.showWaiting(msg="Failed: Post the CL First")
      return
    self.Reviewboard.publish(cl.review_request)
    self.showWaiting(msg="CL Posted")

  def update(self, event):
    self.showWaiting()
    cl = self.getSelectedCL()
    review_request = self.try_post(cl.id)
    self.showWaiting(msg="Generating Diff")
    # TODO: stop using old diff, the new one seems broken though
    try:
      diff = old_review.generate_diff(cl.id)
    except Exception, e:
      print e
      self.showWaiting(msg="Generating Diff FAILED")
      return
    #diff = self.SCM.diff((cl.id,))
    print review_request
    if not review_request:
      return
    #print diff
    self.showWaiting(msg="Uploading Diff")
    print "Uploading Diff"
    self.Reviewboard.upload_diff(review_request, diff)
    url = '%s/r/%s/' % (REVIEWBOARD_HOST, review_request['id'])
    linktext = "View CL#%s (Review Number %s)" % (cl.id, review_request['id'])
    current_time = time.strftime("%H:%M", time.localtime())
    lines_text = "Posted at %s " % current_time
    cl.afterPost(review_request, lines_text)
    self.showItemInfo()
    self.Fit()
  
  def login(self):
    self.clearInfo()
    if REVIEWBOARD_HOST and self.Reviewboard.has_valid_cookie():
      return
    frame = LoginWin(None, -1, "Login", self.Reviewboard)
    frame.Show(True)
    frame.Centre()
    frame.SetFocus()

  def refresh(self, event):
    self.showWaiting("Retrieving Data from P4")
    self.dropdown.Clear()
    self.makeCLList()
    for info in self.cls:
      self.dropdown.Append(info.Display(), info)
    self.panel.Fit()
    self.panel.Layout()
    self.Fit()
    self.clearInfo()

  def exit(self, event):
    if self.info_win:
      self.info_win.Close(force=True)
      self.info_win.Destroy()
    self.saveList()
    self.Destroy()

class LoginWin(wx.Frame):
  def __init__(self, parent, id, title, server):
    wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition,
      wx.Size(200, 150), wx.FRAME_FLOAT_ON_PARENT | wx.CLOSE_BOX)
    panel = wx.Panel(self, -1)
    self.server = server
    self.user = wx.TextCtrl(parent=panel, pos=(30, 10))
    self.password = wx.TextCtrl(parent=panel, pos=(30, 30), style=wx.TE_PASSWORD)
    wx.Button(panel, LOGIN, "Login", (30,60))
    self.Bind(wx.EVT_BUTTON, self.login, id=LOGIN)

  def login(self, event):
    username = self.user.GetValue()
    password = self.password.GetValue()

    self.server.login(username, password)

    self.Close(force=True)
    self.Destroy()

class InfoWin(wx.Frame):
  def __init__(self, parent, id, info=''):
    title = "Info"
    wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, 
      wx.Size(200, 150))
    panel = self#wx.Panel(self, -1)
    self.p4 = wx.StaticText(parent=panel)
    self.p4.SetBackgroundColour("White")
    self.p4.SetLabel(info)
    self.rb = wx.StaticText(parent=panel)
    self.rb.SetBackgroundColour("White")
    self.rb.SetLabel("")
    close = wx.Button(panel, LOGIN, "close", (30,60))
    fgs = wx.FlexGridSizer(1, 2, 9, 5)
    fgs.AddMany([
    (self.p4, 1, wx.EXPAND),
    (self.rb, 1, wx.EXPAND),
    (close, 1, wx.EXPAND)])
    fgs.AddGrowableRow(0)

    panel.SetSizer(fgs)
    panel.Fit()
    panel.SetAutoLayout(True)
    self.Bind(wx.EVT_BUTTON, self.close, id=LOGIN)

  def SetInfo(self, p4, rb):
    self.p4.SetLabel(p4)
    self.p4.Fit()
    self.rb.SetLabel(rb)
    self.rb.Fit()
    self.Fit()
    self.Layout()

  def close(self, event):
    self.Close(force=True)
    self.Destroy()


class MyApp(wx.App):
  def OnInit(self):
    frame = MyFrame(None, -1, "wxPostReview")
    frame.Show(True)
    frame.Centre()
    return True

# need to get cookies
#review.setCookies()
app = MyApp(0)
app.MainLoop()

