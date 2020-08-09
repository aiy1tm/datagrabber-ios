
import ui
import console
from touchviews import SketchView



rootView = ui.View()
rootView.name = 'DataGrabber'

sv = SketchView()
sv.frame = rootView.bounds
sv.flex = 'WH'

photo_button = ui.ButtonItem()
photo_button.title = 'New Photo'
photo_button.action = sv.take_photo

exist_button = ui.ButtonItem()
exist_button.title = 'Import...'
exist_button.action = sv.get_existing

clear_button = ui.ButtonItem()
clear_button.title = 'Clear'
clear_button.tint_color = 'red'
clear_button.action = sv.clear_action

save_button = ui.ButtonItem()
save_button.title = 'Export...'
save_button.tint_color = 'green'
save_button.action = sv.export_action


rootView.right_button_items = [photo_button, exist_button]
rootView.left_button_items  = [clear_button, save_button]



rootView.add_subview(sv)
rootView.present('fullscreen')

