#!/usr/bin/python

from configparser import ConfigParser
import gi
from gi.repository import Gtk
from gi.repository import Gtk, GLib
import json
import os
import threading
from time import sleep

from Spam import Spam


gi.require_version('Gtk', '3.0')


class MyWindow(Gtk.Window):

    def __init__(self):
        
        Gtk.Window.__init__(self, title="SpamGui")
        self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
        self.activity_mode = False
        self.rdy_and_click = False
        
        #configuration    
        self.cfg = ConfigParser()
        self.cfg.read("spam.cfg")
        self.from_addr = self.cfg.get("spam", "from_addr")
        self.subject = self.cfg.get("spam", "subject")
        self.text_subtype = "html"
        self.attachment_file = ""
        self.message_body = ""
        self.destinations_file = ""
        self.smtpservers_file = ""
        self.messagebody_file = ""
        #self.set_default_size(400, 400)
        self.set_resizable(False)
        self.destinations = []
        self.smtp_servers = ""
        #self.box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        #objects GTK
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)
        
        #label
        '''self.label_spamgui = Gtk.Label()
        self.label_spamgui.set_label("SpamGUI")
        self.box.pack_start(self.label_spamgui, True, True, 0)'''

        self.top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box.pack_start(self.top_box, True, True, 0)
        
        self.top_box_box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.top_box_box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        self.top_box.add(self.top_box_box1)
        self.top_box.add(self.top_box_box2)
                        
        #self.img_icon = Gtk.Image.new_from_file('icon.jpg')
        #self.top_box_box1.pack_start(self.img_icon, True, True, 0)
        
        self.label_fromaddr = Gtk.Label()
        self.label_fromaddr.set_label("From:")
        self.top_box_box2.pack_start(self.label_fromaddr, True, True, 0)

        self.from_addr_entry = Gtk.Entry()
        self.top_box_box2.pack_start(self.from_addr_entry, True, True, 0)
        self.from_addr_entry.set_text(self.from_addr)
       
        self.label_subject = Gtk.Label()
        self.label_subject.set_label("Subject:")
        self.top_box_box2.pack_start(self.label_subject, True, True, 0)
        
        self.subject_entry = Gtk.Entry()
        self.top_box_box2.pack_start(self.subject_entry, True, True, 0)
        self.subject_entry.set_text(self.subject)
        
        self.button_targets = Gtk.Button("Upload target emails file")
        self.button_targets.connect("clicked", self.on_upload_targetmails_clicked)
        self.box.add(self.button_targets)
        
        self.targetmails_file_entry = Gtk.Entry()
        self.box.pack_start(self.targetmails_file_entry, False, False, 0)
        
        #####radio buttons
        self.radio_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box.pack_start(self.radio_button_box, True, True, 0)
        
        self.label_text_subtype = Gtk.Label()
        self.label_text_subtype.set_label("Email text subtype:")
        self.radio_button_box.pack_start(self.label_text_subtype, True, True, 0)
        
        self.radio_button_html = Gtk.RadioButton.new_with_label_from_widget(None, "html")
        self.radio_button_html.connect("toggled", self.on_selected_text_subtype)
        self.radio_button_box.pack_start(self.radio_button_html, False, False, 0)
        
        self.radio_button_text = Gtk.RadioButton.new_with_label_from_widget(self.radio_button_html, "text")
        self.radio_button_text.connect("toggled", self.on_selected_text_subtype)
        self.radio_button_box.pack_start(self.radio_button_text, False, False, 0)
        
        self.radio_button_xml = Gtk.RadioButton.new_with_label_from_widget(self.radio_button_html, "xml")
        self.radio_button_xml.connect("toggled", self.on_selected_text_subtype)
        self.radio_button_box.pack_start(self.radio_button_xml, True, True, 0)
        
        
        ##### body
        self.button_messagebody = Gtk.Button("Upload Email message file")
        self.button_messagebody.connect("clicked", self.on_upload_message_clicked)
        self.box.add(self.button_messagebody)
        
        self.textview_bodymessage = Gtk.TextView()
        #self.textview_bodymessage.set_size_request(200,)
        self.textbuffer_bodymessage = self.textview_bodymessage.get_buffer()
        self.box.pack_start(self.textview_bodymessage, True, True, 0)
        
        self.button_attachment = Gtk.Button("Upload attachment file")
        self.button_attachment.connect("clicked", self.on_upload_attachment_clicked)
        self.box.add(self.button_attachment)
        
        self.attachment_entry = Gtk.Entry()
        self.box.pack_start(self.attachment_entry, True, True, 0)
        self.attachment_entry.set_text(self.attachment_file)
        
        self.button_smtps = Gtk.Button("Upload SMTP servers file")
        self.button_smtps.connect("clicked", self.on_upload_smtpfileservers_clicked)
        self.box.add(self.button_smtps)
        
        self.smtpserververs_file_entry = Gtk.Entry()
        self.box.pack_start(self.smtpserververs_file_entry, True, True, 0)
        
        self.button_start = Gtk.Button("Start SPAM")
        self.button_start.connect("clicked", self.on_startSpam_clicked)
        self.box.add(self.button_start)
        
        self.label_subject = Gtk.Label()
        self.label_subject.set_label("Console")
        self.box.pack_start(self.label_subject, True, True, 0)
        
        self.console_entry = Gtk.Entry()
        self.box.pack_start(self.console_entry, True, True, 0)
        
        self.progressbar = Gtk.ProgressBar()
        self.box.pack_start(self.progressbar, True, True, 0)
    
    
    def on_upload_targetmails_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose the target mails file", self,
           Gtk.FileChooserAction.OPEN,
           (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.add_filters_text(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.destinations_file = dialog.get_filename()
            with open(self.destinations_file) as f:
                self.destinations = f.readlines()
            self.targetmails_file_entry.set_text(os.path.basename(dialog.get_filename()) + 
                " (Targets: " + str(len(self.destinations))+ ")")
        dialog.destroy()     
        
    def on_upload_message_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose the message file", self,
           Gtk.FileChooserAction.OPEN,
           (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.add_filters_text(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            with open (filename ,'r') as mb:
                self.message_body = mb.read()
            self.textbuffer_bodymessage.set_text(self.message_body)
            self.messagebody_file = filename
        dialog.destroy()  
           
    def on_upload_smtpfileservers_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please select the smtp servers file", self,
           Gtk.FileChooserAction.OPEN,
           (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.smtpservers_file = dialog.get_filename()
            with open(self.smtpservers_file) as s:
                servers_smtp_data = json.load(s)
                self.smtp_servers = servers_smtp_data['servers']
            self.smtpserververs_file_entry.set_text(os.path.basename(self.smtpservers_file) +
                " (SMTP servers: " +  str(len(self.smtp_servers)) + ")")
            
        dialog.destroy()     
        
    def on_upload_attachment_clicked(self, widget):
            dialog = Gtk.FileChooserDialog("Please select a file to attach", self,
               Gtk.FileChooserAction.OPEN,
               (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.attachment_file = dialog.get_filename()
                self.attachment_entry.set_text(self.attachment_file)
            dialog.destroy()        
            
    def on_selected_text_subtype(self, widget):
        if (widget.get_active()):
            self.text_subtype = widget.get_label()
        
    def add_filters_text(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)
    
    def do_spam(self):
        for destination in self.destinations:
            for server in self.smtp_servers:
                self.console_entry.set_text("To... " +
                    str(destination).lstrip() + " from " +
                    server["username"] + "@" + server["host"])
                if (self.attachment_file != ""):
                    spam = Spam(self.from_addr, destination, self.subject,
                        server["username"], server["password"],
                        server["host"], server["port"], self.text_subtype,
                        self.messagebody_file, self.attachment_file)
                else:
                    spam = Spam(self.from_addr, destination, self.subject,
                        server["username"], server["password"],
                        server["host"], server["port"], self.text_subtype,
                        self.messagebody_file)
                if (spam.send_email()):
                    break        
        self.activity_mode = False
                
    def on_startSpam_clicked(self, widget):
        if(self.from_addr != "" and self.subject != "" and
            self.destinations_file != "" and self.message_body != ""
            and self.smtpservers_file != ""):
            self.activity_mode = True 
            self.from_addr = self.from_addr_entry.get_text()
            self.subject = self.subject_entry.get_text()
            self.attachment_file = self.attachment_entry.get_text()
            # from_addr, to_addr, subject, username, password, smtp, text_subtype, msg, attachment: 
            spam_thread = threading.Thread(target=self.do_spam, args=())
            spam_thread.start()     
            #self.progressbar.set_fraction(self.progressbar.get_fraction() + fraction)

            sleep(2)
        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Please fill required fields")
            dialog.format_secondary_text(
                "From, subject, target emails file, smtp servers file, and message are required")
            dialog.run()
            dialog.destroy()
    
    
    
    def on_timeout(self, user_data):
        """
        Update value on the progress bar
        """
        fraction = 0
        '''try:
            fraction = 1.0/len(self.destinations)
        except ZeroDivisionError:
            pass'''
     
        if self.activity_mode:
            self.progressbar.pulse()
        else:
            new_value = self.progressbar.get_fraction() + fraction
            if new_value > 1:
                new_value = 0
            self.progressbar.set_fraction(new_value)
        # As this is a timeout function, return True so that it
        # continues to get called
        return True
                    
win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
