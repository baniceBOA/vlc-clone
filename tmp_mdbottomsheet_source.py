import inspect, pathlib
from kivymd.uix.bottomsheet import MDBottomSheet
path = pathlib.Path(inspect.getsourcefile(MDBottomSheet))
text = path.read_text()
idx = text.find('class MDBottomSheet')
print('file:', path)
print('idx', idx)
print(text[idx:idx+4000])
