import os
import pygtk
pygtk.require('2.0')
import gtk
import glib

"""
image = (tuple original dimensions w, h)
frame = tuple target dimensions (w, h)
aspect = Maintain aspect ratio?
enlarge -- Allow image to be scaled up?
"""

def resizeToFit(image, frame, aspect=True, enlarge=False):
    if aspect:
        return scaleToFit(image, frame, enlarge)
    else:
        return stretchToFit(image, frame, enlarge)

def scaleToFit(image, frame, enlarge):
    image_width, image_height = image
    frame_width, frame_height = frame
    image_aspect = float(image_width) / image_height
    frame_aspect = float(frame_width) / frame_height

    if not enlarge:
        max_width = min(frame_width, image_width)
        max_height = min(frame_height, image_height)
    else:
        max_width = frame_width
        max_height = frame_height

    if frame_aspect > image_aspect:
        height = max_height
        width = int(height * image_aspect)
    else:
        width = max_width
        height = int(width / image_aspect)
    return (width, height)

def stretchToFit(image, frame, enlarge=False):
    iamge_width, image_height = image
    frame_width, frame_height = frame

    if not enlarge:
        width = min(frame_width, image_width)
        height = min(frame_height, image_height)
    else:
        width = frame_width
        height = frame_height
    return (width, height)

class ResizableImage(gtk.DrawingArea):

    """
    Parameters

    1. aspect (maintain ratio?)
    2. enlarge (allow image to scale?)
    3. interp -- method of interpolation to be used
    4. backcolor -- Tuple (RGB - values range 0 to 1)
    5. max -- Max dimensions for internal image (width, height).
    """
    def __init__(self, aspect=True, enlarge=False, interp=gtk.gdk.INTERP_NEAREST, \
                 backcolor=None, max=(1600, 1200)):
        super(ResizableImage, self).__init__()
        self.pixbuf = None
        self.aspect = aspect
        self.enlarge = enlarge
        self.interp = interp
        self.backcolor = backcolor
        self.max = max
        self.connect ('expose_event', self.expose)
        self.connect('realize', self.on_realize)

    def on_realize(self, widget):
        if self.backcolor is None:
            color = gtk.gdk.Color()
        else:
            color = gtk.gdk.Color(*self.backcolor)
        self.window.set_background(color)       
    
    def expose(self, widget, event):
        #Load Cairo Drawing Context
        self.context = self.window.cairo_create()
        self.context.rectangle(event.area.x, event.area.y, \
                               event.area.width, event.area.height)
        self.context.clip()
        #Render!
        self.draw(self.context)
        return False

    def draw(self, context):
        #Get dimensions
        rect = self.get_allocation()
        x, y = rect.x, rect.y
        #Remove parent offset, if any
        parent= self.get_parent()
        if parent:
            offset = parent.get_allocation()
            x -= offset.x
            y -= offset.y
        #Fill background color
        if self.backcolor:
            context.rectangle(x, y, rect.width, rect.height)
            context.set_source_rgb(*self.backcolor)
            context.fill_preserve()
        if not self.pixbuf:
            return
        width, height = resizeToFit(
            (self.pixbuf.get_width(), self.pixbuf.get_height()),
            (rect.width, rect.height),
            self.aspect,
            self.enlarge)
        x = x + (rect.width - width) / 2
        y = y + (rect.height - height) / 2
        context.set_source_pixbuf(self.pixbuf.scale_simple(width, height, self.interp), x, y)
        context.paint()

    def set_from_pixbuf (self, pixbuf):
        width, height = pixbuf.get_width(), pixbuf.get_height()
        if not self.max or (width < self.max[0] and height < self.max[1]):
            self.pixbuf = pixbuf
        else:
            width, height = resizeToFit((width, height), self.max)
            self.pixbuf = pixbuf.scale_simple(
                width, height, gtk.gdk.INTERP_BILINEAR)
            self.invalidate()

    def set_from_file(self, filename):
        self.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(filename))

    def invalidate(self):
        self.queue_draw()
    

class Base:

    SECONDS_BETWEEN_PICTURES = 3
    FULLSCREEN = True
    WALK_INSTEAD_LISTDIR = True
    
    def destroy(self, widget, data=None):
        gtk.main_quit()

    def myhide(self, widget):
        self.image.hide()

    def load_file_list(self):
            self.files = []
            self.index = 0
            self.files.append("vuevent.png")
            self.files.append("pin_blue.png")

    def display(self):
        if 0 <= self.index < len(self.files):
            self.image.set_from_file(self.files[self.index])
            return True
        else:
            return False

    def on_tick(self):
        self.index += 1
        if self.index >= len(self.files):
            self.index = 0

        return self.display()
         
    def __init__(self):
        self.window = gtk.Window()
        self.window.connect('destroy', gtk.main_quit)
        self.window.set_title("Vuevent")

        self.image = ResizableImage (True, True, gtk.gdk.INTERP_BILINEAR)
        self.image.show()
        self.window.add(self.image)

        self.load_file_list()

        self.window.show_all()

        if self.FULLSCREEN:
            self.window.fullscreen()

        glib.timeout_add_seconds(self.SECONDS_BETWEEN_PICTURES, self.on_tick)
        self.display()

     


        """
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.fullscreen()
        #self.set_size_request(600,100)
        #self.set_position(gtk.WIN_POS_CENTER)
        
        self.image = gtk.Image()
        self.image.set_from_file("vuevent.png")

        self.button1 = gtk.Button("hide")
        self.button1.connect("clicked", self.myhide)
        
        self.box1 = gtk.HBox()
        self.box1.pack_start(self.image)
        self.box1.pack_start(self.button1, 20, 30)

        
        self.window.add(self.box1)
        self.window.show_all()r
        self.window.connect("destroy", self.destroy)
        """

    def main(self):
        gtk.main()

if __name__ == "__main__":
    gui = Base()
    gtk.main()
