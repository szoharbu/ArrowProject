
def upload_statistics(duration, run_status):
    '''
    Entry fields:
    - Name: ??
    - Template:
    - Command Line
    - Status : Pass / Fail
    - Start time
    - Duration
    '''
    import os
    from Arrow.Externals.cloud.Airtable import upload_run_statistics
    from Arrow.Utils.configuration_management import get_config_manager

    config_manager = get_config_manager()
    upload_stats = config_manager.get_value('Upload_statistics')
    if not upload_stats:
        return

    template_path = config_manager.get_value('template_path')
    template_name = os.path.basename(template_path)
    command_line = config_manager.get_value('command_line_string')
    architecture = config_manager.get_value("Architecture")
    cloud_mode = config_manager.get_value('Cloud_mode')

    '''
    The bellow collects basic system metadata (OS, architecture, Python version) and an anonymous user identifier (hashed username or random ID)
     to help improve compatibility and understand usage trends. 
     No personal or sensitive data is collected, ensuring full privacy and anonymity.
    '''
    # Get system metadata as a summarized string
    system_summary = get_system_metadata()


    if config_manager.is_exist('Identifier'):
        user_id = config_manager.get_value('Identifier')
    else:
        # Get anonymized user identifier
        user_id = get_anonymized_user()


    upload_run_statistics(template=template_name,
                          command_line=command_line,
                          duration=duration,
                          run_status=run_status,
                          architecture=architecture,
                          cloud_mode=cloud_mode,
                          system_metadata=system_summary,
                          user_id=user_id,
                          )




def get_system_metadata():
    import platform

    """Summarizes system metadata into a single short text string."""
    metadata = {
        "os": platform.system(),
        "version": platform.release(),  # Shorter than full version
        "arch": platform.architecture()[0],
        "python": platform.python_version()
    }
    return f"{metadata['os']} {metadata['version']} ({metadata['arch']}, Py{metadata['python']})"


def get_anonymized_user():
    import os
    import hashlib
    import uuid
    """Returns a hashed username if available, otherwise generates a random user ID."""
    username = os.getenv("USER") or os.getenv("USERNAME") or None

    if username:  # If a username exists, anonymize it
        return hashlib.sha256(username.encode()).hexdigest()
    else:  # If no username is found, generate a random UUID
        return str(uuid.uuid4())

