from kivymd.uix.bottomsheet import MDBottomSheet
import inspect, pathlib
print('methods')
print([m for m in dir(MDBottomSheet) if not m.startswith('_')])
print('file', inspect.getsourcefile(MDBottomSheet))
with open(inspect.getsourcefile(MDBottomSheet), 'r', encoding='utf-8') as f:
    text = f.read()
idx = text.find('class MDBottomSheet')
print(text[idx:idx+1200])
