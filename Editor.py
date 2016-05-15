import wx
import wx.lib.dialogs
import wx.stc as stc
import os
import re,collections
import yaml


class Node():
    def __init__(self, value):
        self.childs = list()
        self.value = value
        self.terminal = False

class Trie():
    def __init__(self):
        self.root = Node('.')
        self.curr = self.root

    def __insert_letter(self, head, l):
        for c in head.childs:
            if c.value == l:
                return c
        else:
            n = Node(l)
            head.childs.append(n)
            return n

    def insert(self, word):
        self.curr = self.root
        for l in word:
            self.curr = self.__insert_letter(self.curr, l)
        self.curr.terminal = True

    def dump(self, i=0):
        print self.curr.value,
        if self.curr.terminal:
            print
            print " "*i,
        for c in self.curr.childs:
            self.curr = c
            self.dump(i+2)
        self.curr = self.root

    def has_word(self, w):
        self.curr = self.root
        for l in w:
            for x in self.curr.childs:
                if x.value == l:
                    self.curr = x
                    break
            else:
                return False

        if self.curr.terminal:
            return True
        else:
            return False

    def has_prefix(self, w):
        self.curr = self.root
        for l in w:
            for x in self.curr.childs:
                if x.value == l:
                    self.curr = x
                    break
            else:
                return False
        return True

#Class to create main window "To run application"
class MainWindow(wx.Frame):
	def __init__(self,parent,title):
		#title name of application
		self.leftMarginWidth=25
		self.pathname = '' 

		fd=open("word.txt")
		data_text=yaml.load(fd)
		self.NWORDS = self.train(data_text)
		
		self.lineNumberEnabled = True # For preferences menu
#		self.data =wx.FindReplaceData()
		self.pos=0
		self.size=0
		wx.Frame.__init__(self,parent,title=title,size=(800,600))
		#It will create a window of size 800*600
		self.control = stc.StyledTextCtrl(self,style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_RICH2 | wx.TE_CAPITALIZE )
		#It will control the style of text to be multilined and word wrapped
		
		#To assign keys for zooming in and out
		self.control.CmdKeyAssign(ord('='),stc.STC_SCMOD_CTRL,stc.STC_CMD_ZOOMIN)  # Ctrl + is Zoom in
		self.control.CmdKeyAssign(ord('-'),stc.STC_SCMOD_CTRL,stc.STC_CMD_ZOOMOUT)  # Ctrl - is Zoom out
		
		#To set editor to not show white space
		self.control.SetViewWhiteSpace(False)
		#To Set Margins
		self.control.SetMargins(5,0) #Set margins to left inside by 5 pixels
		self.control.SetMarginType(1,stc.STC_MARGIN_NUMBER)  #Create Line Number Column here 1 indicates 1st column
		self.control.SetMarginWidth(1,self.leftMarginWidth) #Here the leftMa--rginWidth declared above comes into invocation


		#Creating the mini bars
		self.CreateStatusBar()   #To create the bottom bar
		self.StatusBar.SetBackgroundColour((220,220,220))

		#Defining attributes of a menu bar 

		#FILE MENU
		filemenu = wx.Menu() 
		menuNew = filemenu.Append(wx.ID_NEW,"&New","Create a new document")  
		"""
		The first attribute gives a special Id already stored in wx , 2nd gives the name in the menu column and the 3rd displays the text in statusbar
		 & is the keyboard representation for alt when in above we press Alt N or Alt n New command will be executed 
		 whereas new is the attribute  of the bar 
		"""
		menuOpen = filemenu.Append(wx.ID_OPEN,"&Open","Open an Existing Document")
		menuSave = filemenu.Append(wx.ID_SAVE,"&Save","Save the Current Document")
		menuSaveAs = filemenu.Append(wx.ID_SAVEAS,"Save &As","Save a New Document")
		filemenu.AppendSeparator()  #To print dotted lines after above keys 
		menuClose = filemenu.Append(wx.ID_EXIT,"&Close","Close the Application")
		

		#EDIT MENU
		editmenu=wx.Menu()
		menuundo=editmenu.Append(wx.ID_UNDO,"&Undo","Undo Last Action")
		menuredo=editmenu.Append(wx.ID_REDO,"&Redo","Redo Last Action")
		editmenu.AppendSeparator()
		menuSelectAll=editmenu.Append(wx.ID_SELECTALL,"&Select All","Select The Entire Document")
		menucopy=editmenu.Append(wx.ID_COPY,"&Copy","Copy Selected Area")
		menucut=editmenu.Append(wx.ID_CUT,"C&ut","Cut Selected Area")
		menupaste=editmenu.Append(wx.ID_PASTE,"&Paste","Paste From Clipboard ")
		menufindreplace=editmenu.Append(wx.ID_REPLACE,"&Find and Replace","Find and replace data to Text")
	
		#PREFERENCE MENU
		prefmenu=wx.Menu()
		menuLineNumbers=prefmenu.Append(wx.ID_ANY,"Toggle &Line Number","Show/Hide Line Numbers Column")
		menuautocorrect=prefmenu.Append(wx.ID_ANY,"&Spell Checker","Auto Spell Check ")

		#HELP MENU
		helpmenu=wx.Menu()
		menuHowTo=helpmenu.Append(wx.ID_ANY,"&How To.....","Get Help Using The Editor ")
		helpmenu.AppendSeparator()
		menuAbout=helpmenu.Append(wx.ID_ABOUT,"&About","Read About the Editor and its Making")



		#Creating a Menu Bar
		menuBar=wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		menuBar.Append(editmenu,"&Edit")
		menuBar.Append(prefmenu,"&Preferences")
		menuBar.Append(helpmenu,"&Help")
		self.SetMenuBar(menuBar)


		#To BInd functions to there variables
		self.Bind(wx.EVT_MENU, self.OnNew,menuNew)
		self.Bind(wx.EVT_MENU, self.OnOpen,menuOpen)
		self.Bind(wx.EVT_MENU, self.OnSave,menuSave)
		self.Bind(wx.EVT_MENU, self.OnSaveAs,menuSaveAs)
		self.Bind(wx.EVT_MENU, self.OnClose,menuClose)


		self.Bind(wx.EVT_MENU, self.OnUndo,menuundo)
		self.Bind(wx.EVT_MENU, self.OnRedo,menuredo)
		self.Bind(wx.EVT_MENU, self.OnSelectAll,menuSelectAll)
		self.Bind(wx.EVT_MENU, self.OnCopy,menucopy)
		self.Bind(wx.EVT_MENU, self.OnCut,menucut)
		self.Bind(wx.EVT_MENU, self.OnPaste,menupaste)
		self.Bind(wx.EVT_MENU, self.OnReplace,menufindreplace)
		self.Bind(wx.EVT_MENU, self.OnSpellCheck,menuautocorrect)

		self.Bind(wx.EVT_MENU, self.OnToggleLineNumbers,menuLineNumbers)

		self.Bind(wx.EVT_MENU, self.OnHowTo,menuHowTo)
		self.Bind(wx.EVT_MENU, self.OnAbout,menuAbout)

		self.control.Bind(wx.EVT_KEY_UP,self.UpdateLineCol)
		self.control.Bind(wx.EVT_CHAR,self.OnCharEvent)

		self.Show()
		self.UpdateLineCol(self)

	# Function for New 	
	def OnNew(self, e) :
		self.pathname=''
		self.control.SetText("")	
	#Function for New 
	def OnOpen(self,e):
		#Dialog box to display open menu
		dlg=wx.FileDialog(self,"Choose a file",self.pathname,"","*.*",wx.FD_OPEN)
		if(dlg.ShowModal() == wx.ID_OK) : #If user presses ok
			#Update filename and directory name
			self.pathname=dlg.GetPath()
			#Open file in read mode())
			f = open(os.path.abspath(self.pathname),'r')
			self.control.SetText(f.read())
			f.close()
		#Destroy dialogue box	dirname,self.filenam
		dlg.Destroy()

	def OnSave(self,e):
		try :
			f=open(os.path.abspath(self.pathname),'w')
			f.write(self.control.GetText())
			f.close()	
		except:
			try :
				dlg=wx.FileDialog(self,"Save File As",self.pathname,"Untitled","*.*",wx.FD_SAVE |wx.FD_OVERWRITE_PROMPT ) 
				#Show save as screen an*d prompt if name already occurs 
				if(dlg.ShowModal() == wx.ID_OK):
					self.pathname=dlg.GetPath()
					f=open(os.path.abspath(self.pathname),'w')
					f.write(self.control.GetText())
					f.close()
				dlg.Destroy()
			except:
				pass		
	def OnSaveAs(self , e ) : 			
		try :
			dlg=wx.FileDialog(self,"Save File As",self.pathname,"Untitled","*.*",wx.FD_SAVE |wx.FD_OVERWRITE_PROMPT ) 
			#Show save as screen an*d prompt if name already occurs 
			if(dlg.ShowModal() == wx.ID_OK):
				self.pathname=dlg.GetPath()
				f=open(os.path.abspath(self.pathname),'w')
				f.write(self.control.GetText())
				f.close()
			dlg.Destroy()
		except :		
			pass
	def OnClose(self,e) :
		self.Close(True)

	def OnUndo(self,e):
		self.control.Undo()

	def OnRedo(self ,e ) :
		self.control.Redo()

	def OnSelectAll(self ,e ) :
		self.control.SelectAll()

	def OnCopy(self ,e ) :
		self.control.Copy()

	def OnCut(self ,e ) :
		self.control.Cut()

	def OnPaste(self ,e ) :
		self.control.Paste()

	def OnReplace(self,e) :
		self.data=self.control.GetText()
		n=len(self.data)
		z=Trie()
		k=''
		i=0
		self.text=self.data
		self.text=self.text.replace(' ','+').replace('\n','+')
		while i<n :
			if(self.text[i]!='+'):
				k=k+self.data[i]
			else :
				z.insert(k)
				del k
				k=''
			i=i+1
		z.insert(k)	
		print("Enter the word to be searched ")
		s=raw_input("Word To Be found - ")

		d=z.has_word(s)
	
		if(d==False) :
			print("No Word Found !!!!")
			return
		r=raw_input("Word To Be Replaced with - ")
		
		self.data=self.data.replace(s,r)

		self.control.SetText(self.data)
		
#		print self.data
		print("Process Complete ")
	

	def words(self,text): 
		return re.findall('[a-z]+', text.lower()) 
	
	def train(self,features):
		model = collections.defaultdict(lambda: 1)
		for f in features:
			model[f] += 1
		return model
	

	def OnSpellCheck(self,e) :


		alphabet = 'abcdefghijklmnopqrstuvwxyz'

		def edits1(word):
			splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
			deletes    = [a + b[1:] for a, b in splits if b]
			transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
			replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
			inserts    = [a + c + b     for a, b in splits for c in alphabet]
			return set(deletes + transposes + replaces + inserts)

		def known_edits2(word):
			return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in self.NWORDS)

		def known(words): return set(w for w in words if w in self.NWORDS)	

		def correct(word):
			candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
			return max(candidates, key=self.NWORDS.get)
		
		self.data=self.control.GetText()
		k=''
		i=0
		self.text=self.data
		self.text=self.data.replace(' ','+').replace('\n','+')
		while i<len(self.text) :
			if(self.text[i]!='+'):
				k=k+self.data[i]
			else :
 
				z=correct(k)
				i=i-len(k)+len(z)
				self.text=self.text.replace(k,z)
				self.data=self.data.replace(k,z)
				del k	

				k=''
			i=i+1
		z=correct(k)
		self.data=self.data.replace(k,z)
		self.control.SetText(self.data)	
	
	def OnToggleLineNumbers(self ,e ) :
		if(self.lineNumberEnabled):
			self.control.SetMarginWidth(1,0)
			self.lineNumberEnabled = False
		else:
			self.control.SetMarginWidth(1,self.leftMarginWidth)
			self.lineNumberEnabled=True	

	def OnHowTo(self,e):
		dlg = wx.lib.dialogs.ScrolledMessageDialog(self,"This is how to",size=(400,400))
		dlg.ShowModal()
		dlg.Destroy()

	def OnAbout(self,e):
		dlg=wx.MessageDialog(self,"My advanced text editor I made with python and wx",wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
		#To Update column number in status bar
	def UpdateLineCol(self,e):
		line=self.control.GetCurrentLine()+1
		col=self.control.GetColumn(self.control.GetCurrentPos())
		stat="Line %s, Column %s" % (line,col)
		self.StatusBar.SetStatusText(stat,0)

	def OnCharEvent(self,e):
		keycode=e.GetKeyCode()
		altDown=e.AltDown()
		if(keycode == 14): #Ctrl + n
			self.OnNew(self)
		elif(keycode==15):  #Ctrl+o	
			self.OnOpen(self)
		elif(keycode==19):  #Ctrl+s	
			self.OnSave(self)
		elif(altDown and  (keycode==115)):  #Alt+s	
			self.OnSaveAs(self)
		elif(keycode==23):  #Ctrl+w	
			self.Close(self)
		elif(keycode==340):  #F1	
			self.OnHowTo(self)
		elif(keycode==341):  #F2	
			self.OnAbout(self)
		elif(keycode==348) :# Ctrl + f9	
			self.OnSpellCheck(self)
		else :
			e.Skip() #Prpgram looks for built in 	


app = wx.App()
#An app to run the module 

frame=MainWindow(None,"My Text Editor")	

app.MainLoop()
