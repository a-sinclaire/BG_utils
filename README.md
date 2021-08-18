# BG_utils

col_pick.py</br>
when a shortcut key is pressed col_pick mode is activated</br>
(shortcut is currently set to &lt;f9> key)</br>
(&lt;scroll_lock> terminates the thread)

wherever you click it will give you the hex value of that pixel's color</br>
the hex value will be stored on your clipboard automatically</br>
use the square brackets to change zoom level</br>
(TIP: You could easily use this tool as a magnifier as well!)

pip install pyautogui</br>
pip install pynput</br>
pip install Pillow</br>
pip install opencv-python</br>
pip install pygame</br>

there are currently three bugs (both caused by using pygame):
1. after the first press you will have to hit the hotkey twice to activate again
2. after the first press the whole hotkey needn't be pressed.
  if the hotkey was &lt;alt>+c for example i could get it to trigger
  by just pressing alt, or just pressing c. This leads to annoying misfires.
  Hence why it is currently bound to &lt;f9>. a very uncommon key.
3. The first time the pygame window is not focused or on top. This fixes itself for subsequent uses.
