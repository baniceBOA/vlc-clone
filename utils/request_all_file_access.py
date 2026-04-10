from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass, cast
    from android import api_version

    def check_and_request_all_files_access():
        # MANAGE_EXTERNAL_STORAGE was introduced in API 30 (Android 11)
        if api_version < 30:
            return True

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Environment = autoclass('android.os.Environment')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        Uri = autoclass('android.net.Uri')
        
        # Check if permission is already granted
        if not Environment.isExternalStorageManager():
            try:
                # Create intent to open the specific settings page for this app
                current_activity = PythonActivity.mActivity
                package_name = current_activity.getPackageName()
                uri = Uri.parse(f"package:{package_name}")
                
                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                current_activity.startActivity(intent)
            except Exception as e:
                # Fallback to the general All Files Access settings page
                intent = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                current_activity.startActivity(intent)