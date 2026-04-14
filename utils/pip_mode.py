from kivy.utils import platform

def enter_pip_mode():
    if platform == 'android':
        from jnius import autoclass, cast
        
        # Get the current Android Activity
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
        
        # Build PiP parameters (Required for Android 8.0+)
        # This sets the aspect ratio of the mini-window
        App = autoclass('kivy.app.App')
        ParamsBuilder = autoclass('android.app.PictureInPictureParams$Builder')
        Rational = autoclass('android.util.Rational')
        
        # Example: 16:9 aspect ratio for video
        builder = ParamsBuilder()
        builder.setAspectRatio(Rational(16, 9))
        
        # Trigger the pop-up
        currentActivity.enterPictureInPictureMode(builder.build())