from kivy.utils import platform

NOTIFICATION_ID = 1001
CHANNEL_ID = 'audio_playback_channel'
CHANNEL_NAME = 'Audio Playback'


def _android_activity():
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    return PythonActivity.mActivity


def _create_notification_channel(notification_manager):
    from jnius import autoclass
    Build = autoclass('android.os.Build')
    if Build.VERSION.SDK_INT >= 26:
        NotificationChannel = autoclass('android.app.NotificationChannel')
        importance = notification_manager.IMPORTANCE_LOW
        channel = NotificationChannel(CHANNEL_ID, CHANNEL_NAME, importance)
        notification_manager.createNotificationChannel(channel)


def _get_notification_builder(activity):
    from jnius import autoclass
    Build = autoclass('android.os.Build')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    if Build.VERSION.SDK_INT >= 26:
        return NotificationBuilder(activity, CHANNEL_ID)
    return NotificationBuilder(activity)


def _make_intent(action):
    from jnius import autoclass
    Intent = autoclass('android.content.Intent')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = _android_activity()
    intent = Intent(activity, PythonActivity)
    intent.setAction('com.kivyvlc.AUDIO_CONTROL')
    intent.putExtra('audio_action', action)
    intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP)
    return intent


def _make_pending_intent(action, request_code):
    from jnius import autoclass
    PendingIntent = autoclass('android.app.PendingIntent')
    Build = autoclass('android.os.Build')
    intent = _make_intent(action)
    flags = PendingIntent.FLAG_UPDATE_CURRENT
    if Build.VERSION.SDK_INT >= 31:
        flags |= PendingIntent.FLAG_IMMUTABLE
    return PendingIntent.getActivity(_android_activity(), request_code, intent, flags)


def show_audio_notification(title, text, is_playing=True):
    if platform != 'android':
        return
    try:
        from jnius import autoclass
        Context = autoclass('android.content.Context')
        activity = _android_activity()
        nm = activity.getSystemService(Context.NOTIFICATION_SERVICE)
        _create_notification_channel(nm)
        builder = _get_notification_builder(activity)
        app_info = activity.getApplicationInfo()
        icon = app_info.icon
        builder.setSmallIcon(icon)
        builder.setContentTitle(title)
        builder.setContentText(text)
        builder.setOngoing(True)
        builder.setAutoCancel(False)
        builder.setPriority(builder.PRIORITY_LOW)

        main_intent = _make_intent('open')
        main_pending = _make_pending_intent('open', 0)
        builder.setContentIntent(main_pending)

        action_icon = autoclass('android.R$drawable').ic_media_pause if is_playing else autoclass('android.R$drawable').ic_media_play
        action_text = 'Pause' if is_playing else 'Play'
        action_pending = _make_pending_intent('toggle', 1)
        builder.addAction(action_icon, action_text, action_pending)

        stop_icon = autoclass('android.R$drawable').ic_menu_close_clear_cancel
        stop_pending = _make_pending_intent('stop', 2)
        builder.addAction(stop_icon, 'Stop', stop_pending)

        notification = builder.build()
        nm.notify(NOTIFICATION_ID, notification)
    except Exception as e:
        print('Notification failed:', e)


def cancel_audio_notification():
    if platform != 'android':
        return
    try:
        from jnius import autoclass
        Context = autoclass('android.content.Context')
        activity = _android_activity()
        nm = activity.getSystemService(Context.NOTIFICATION_SERVICE)
        nm.cancel(NOTIFICATION_ID)
    except Exception as e:
        print('Cancel notification failed:', e)
