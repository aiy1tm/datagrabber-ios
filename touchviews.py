import ui, io, photos, console
import dialogs
import numpy as np
import csv
from time import time

# built by extending the Sketch example provided by the Pythonista app

MAX_DOUBLE_TAP_DELAY = 0.25
MAX_DOUBLE_TAP_PIXEL_DEV = 10

class PathView (ui.View):
	def __init__(self, frame):
		self.frame = frame
		self.flex = 'WH'
		self.path = None
		self.action = None
		self.touched_x = np.array([])
		self.touched_y = np.array([])
		self.lp_corner_x = np.array([])
		self.lp_corner_y = np.array([])
		self.corner_vals_x = np.array([])
		self.corner_vals_y = np.array([])
		self.last_touch_pos_x = 0
		self.last_touch_pos_y = 0
		self.last_touch_up_time = 0
		self.double_tap_start_time = 0
		
		
	def update_graph_bounds(self, **kwargs):
		try:
			title_str = kwargs["message"]
		except KeyError:
			title_str = "Which values are at this point?"
				
		sections = []
		fields = []
		field = {'type':'number','key':'X','title':'X','tint_color':'linen'}
		fields.append(field)
		field = {'type':'number','key':'Y','title':'Y','tint_color':'linen'}
		fields.append(field)
		sections.append(('X-Y Values For Scale at Plot Corner', fields))
		results = dialogs.form_dialog(title=title_str,sections=sections)
		try:
			self.corner_vals_x = np.append(self.corner_vals_x, float(results["X"]))
			self.corner_vals_y = np.append(self.corner_vals_y, float(results["Y"]))
		except ValueError:
			self.update_graph_bounds(message = "Try again, values must be numerical")
		except TypeError:
			pass

	def touch_began(self, touch):
		x, y = touch.location
		self.path = ui.Path()
		self.path.line_width = 8.0
		self.path.line_join_style = ui.LINE_JOIN_ROUND
		self.path.line_cap_style = ui.LINE_CAP_ROUND
		self.path.move_to(x, y)
		#self.touched_x = np.append(self.touched_x,x)
		#self.touched_y = np.append(self.touched_y,y)
		#print('touch began')
		
	def touch_moved(self, touch):
		#super(PathView,self).touch_moved(touch)
		x, y = touch.location
		self.path.line_to(x, y)
		self.set_needs_display()
		self.touched_x = np.append(self.touched_x,x)
		self.touched_y = np.append(self.touched_y,y)
		#print('touch moved')
	
	def touch_ended(self, touch):
		if callable(self.action):
			self.action(self)
			
		x, y = touch.location
		if (time() - self.last_touch_up_time < MAX_DOUBLE_TAP_DELAY) and (abs(self.last_touch_pos_x - x) < MAX_DOUBLE_TAP_PIXEL_DEV) and (abs(self.last_touch_pos_y - y) < MAX_DOUBLE_TAP_PIXEL_DEV):
			#detected double tap
			self.last_touch_up_time = 0
			self.last_touch_pos_x   = 0
			self.last_touch_pos_y   = 0
			self.update_graph_bounds()
			self.lp_corner_y = np.append(self.lp_corner_y, y)
			self.lp_corner_x = np.append(self.lp_corner_x, x)
		else:
			self.last_touch_up_time = time()
			self.last_touch_pos_x = x
			self.last_touch_pos_y = y	
			
		self.path = None
		self.set_needs_display()
	
	def draw(self):
		if self.path:
			self.path.stroke()


class SketchView (ui.View):
	def __init__(self):
		
		self.flex = 'WH'
		self.frame = self.bounds;
		self.pv = PathView(frame=self.bounds)
		
		self.bgview = ui.ImageView()
		self.bgview.frame = self.bounds
		self.bgview.flex = 'WH'
		self.bgview.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
		self.add_subview(self.bgview)
		
		iv = ui.ImageView(frame=self.bounds)
		iv.alpha = 0.75
		iv.flex = 'WH'
		
		self.pv.action = self.path_action
		self.image_view = iv
		self.add_subview(self.image_view)
		self.add_subview(self.pv)

		
	def take_photo(self, sender):
		pil_img =photos.capture_image()
		self.bg_image = self.pil2ui(pil_img)
		self.bgview.image = self.bg_image
		
	def get_existing(self, sender):
		exi_img = photos.pick_asset()
		exi_img = exi_img.get_ui_image()
		self.bg_image = exi_img
		self.bgview.image = self.bg_image
					
	def path_action(self, sender):
		path = sender.path
		old_img = self.image_view.image
		width, height = self.image_view.width, self.image_view.height
		#print(f"{width} and {height}")
		with ui.ImageContext(width, height) as ctx:
			if old_img:
				old_img.draw()
			path.stroke()
			self.image_view.image = ctx.get_image()
	
	def clear_action(self, sender):
		self.image_view.image = None
		self.pv.touched_x = np.array([])
		self.pv.touched_y = np.array([])
		self.pv.corner_vals_y = np.array([])
		self.pv.corner_vals_x = np.array([])
		self.pv.lp_corner_y   = np.array([])
		self.pv.lp_corner_x   = np.array([])
		#print(self.pv.touched_x)
		#print(self.pv.touched_y)
	
	def export_action(self, sender):
		
		if len(self.pv.touched_x):
			self.scale_out_data()
			x = self.pv.touched_x
			with open('export.csv', 'w') as csvfile:
				for indy, out_y in enumerate(self.pv.touched_y):
					writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
					writer.writerow(["%f" % x[indy], "%f" % out_y])
					#writer.writerow([f"{x[indy]}",f"{out_y}"])
			console.open_in('export.csv')
		else:
			console.hud_alert('Nothing to export! Import or take a photo to grab some data.')
		
	def scale_out_data(self):
		# do the scaling for the final export
		max_cx  = max(self.pv.lp_corner_x)
		min_cx  = min(self.pv.lp_corner_x)
		max_cy  = max(self.pv.lp_corner_y)
		min_cy  = min(self.pv.lp_corner_y)
		min_x_i = np.where(self.pv.lp_corner_x == min_cx)
		min_y_i = np.where(self.pv.lp_corner_y == min_cy)
		max_x_i = np.where(self.pv.lp_corner_x == max_cx)
		max_y_i = np.where(self.pv.lp_corner_y == max_cy)
		maxy    = self.pv.corner_vals_y[max_y_i]
		maxx    = self.pv.corner_vals_x[max_x_i]
		miny    = self.pv.corner_vals_y[min_y_i]
		minx    = self.pv.corner_vals_x[min_x_i]
		
		slope_y = (maxy-miny)/(max_cy - min_cy)
		slope_x = (maxx-minx)/(max_cx - min_cx)
		offs_x  =  minx
		offs_y  =  miny
		for ind, pty in enumerate(np.nditer(self.pv.touched_y)):
			pty = (pty - min_cy)*slope_y + offs_y
			self.pv.touched_y[ind] = pty
			self.pv.touched_x[ind] = (self.pv.touched_x[ind] - min_cx)*slope_x + offs_x
			
			
		
	def pil2ui(self, imgIn):
		with io.BytesIO() as bIO:
			imgIn.save(bIO, 'PNG')
			imgOut = ui.Image.from_data(bIO.getvalue())
			del bIO
		return imgOut
		
	def update_bg(self, image_pil):
		imageui = self.pil2ui(image_pil)
		self.bg_image = imageui
		self.bgview.image = self.bg_image
		return
	
	def save_action(self, sender):
		if self.image_view.image:
			with ui.ImageContext(self.width, self.height) as ctx:
				self.image_view.image.draw()
				img = ctx.get_image()
				photos.save_image(img)
				console.hud_alert('Saved')
		else:
			console.hud_alert('No Image', 'error')
	
